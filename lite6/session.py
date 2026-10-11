"""Ligação, segurança e movimentos de juntas do Lite 6.

Uso: ``with safe_session() as (arm, cfg, log): ...``. Os parâmetros vêm do
YAML; os limites da bancada da aula 1 só são aplicados ao alvo ``lab``.
"""
from __future__ import annotations

import contextlib
import logging
import math
import time
from datetime import datetime

from xarm.wrapper import XArmAPI

from .config import ROOT, load_config


def get_logger(cfg: dict) -> logging.Logger:
    """Regista no terminal e num ficheiro por processo em logs/."""
    logger = logging.getLogger("lite6")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_dir = ROOT / cfg["logging"]["dir"]
    log_dir.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    fh = logging.FileHandler(log_dir / f"session_{datetime.now():%Y%m%d_%H%M%S}.log", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def check(code: int, what: str, log: logging.Logger) -> int:
    """Regista o retorno do SDK e interrompe a sessão se o comando falhou."""
    log.info("%-28s -> code=%s", what, code)
    if code != 0:
        raise RuntimeError(f"{what} falhou (code={code})")
    return code


def _number(value, name: str, *, allow_zero: bool = False) -> float:
    """Aceita apenas números finitos e não negativos (ou estritamente positivos)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} deve ser um número finito")
    if value < 0 or (value == 0 and not allow_zero):
        limit = "não negativo" if allow_zero else "positivo"
        raise ValueError(f"{name} deve ser {limit}")
    return float(value)


def _validate_motion_settings(cfg: dict) -> None:
    """Valida os valores do YAML antes de abrir a ligação ou comandar movimento."""
    motion, safety = cfg["motion"], cfg["safety"]
    speed = _number(motion["joint_speed"], "motion.joint_speed")
    cap = _number(safety["max_joint_speed"], "safety.max_joint_speed")
    _number(motion["joint_acc"], "motion.joint_acc")
    _number(motion["home_timeout_s"], "motion.home_timeout_s")
    _number(motion["home_tolerance_deg"], "motion.home_tolerance_deg", allow_zero=True)
    if speed > cap:
        raise ValueError(f"joint_speed={speed:g} excede o teto max_joint_speed={cap:g} (S2)")


def _joint_angles(joints, name: str) -> list[float]:
    """As trajetórias deste projeto usam sempre seis ângulos em graus."""
    if not isinstance(joints, (list, tuple)) or len(joints) != 6:
        raise ValueError(f"{name} precisa de 6 ângulos em graus")
    return [_signed_angle(angle, f"{name}[{i}]") for i, angle in enumerate(joints)]


def _signed_angle(value, name: str) -> float:
    """Aceita ângulos positivos ou negativos, mas nunca booleanos/NaN/infinitos."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} deve ser um número finito")
    return float(value)


def _tcp_offset(values) -> list[float]:
    """Confirma os seis valores do TCP: posição em mm e orientação em graus."""
    if not isinstance(values, (list, tuple)) or len(values) != 6:
        raise ValueError("tool.tcp_offset precisa de 6 valores (mm e graus)")
    return [_signed_angle(value, f"tool.tcp_offset[{i}]")
            for i, value in enumerate(values)]


def validate_tcp_boundary(boundary) -> list[float]:
    """Valida a fronteira em mm e na ordem exigida pelo SDK."""
    if not isinstance(boundary, (list, tuple)) or len(boundary) != 6:
        raise ValueError("safety.tcp_boundary_mm precisa de 6 valores em mm")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
           for v in boundary):
        raise ValueError("safety.tcp_boundary_mm contém valores inválidos")
    if any(boundary[i] <= boundary[i + 1] for i in (0, 2, 4)):
        raise ValueError("cada máximo da fronteira do TCP deve exceder o mínimo")
    return [float(v) for v in boundary]


def configure_reduced_safety(arm, cfg: dict, log: logging.Logger) -> None:
    """Aplica o modo reduzido e a fronteira antes de ativar o robô real."""
    safety = cfg["safety"]
    boundary = validate_tcp_boundary(safety["tcp_boundary_mm"])
    joint_speed = _number(safety["reduced_max_joint_speed"], "safety.reduced_max_joint_speed")
    tcp_speed = _number(safety["reduced_max_tcp_speed"], "safety.reduced_max_tcp_speed")
    check(arm.set_reduced_max_joint_speed(joint_speed, is_radian=False),
          "set_reduced_max_joint_speed", log)
    check(arm.set_reduced_max_tcp_speed(tcp_speed), "set_reduced_max_tcp_speed", log)
    check(arm.set_reduced_tcp_boundary(boundary), "set_reduced_tcp_boundary", log)
    check(arm.set_reduced_mode(True), "set_reduced_mode", log)
    check(arm.set_fence_mode(True), "set_fence_mode", log)


def _request_stop(arm, log: logging.Logger) -> bool:
    """Pede a paragem; devolve se o controlador aceitou o comando."""
    try:
        code = arm.set_state(4)
        log.info("%-28s -> code=%s", "set_state(4)", code)
        if code != 0:
            log.error("paragem comandada falhou (code=%s)", code)
        return code == 0
    except Exception:
        log.exception("set_state(4) falhou")
        return False


@contextlib.contextmanager
def safe_session(cfg: dict | None = None):
    """Prepara a sessão e liberta a ligação mesmo quando há uma exceção.

    Numa saída normal, pede paragem se o movimento estiver ativo, pausado ou
    não for possível ler o estado. Uma exceção também desencadeia a paragem.
    O código de paragem confirma apenas a aceitação do comando pelo SDK.
    """
    cfg = load_config() if cfg is None else cfg
    if cfg["target"] not in ("sim", "lab"):
        raise ValueError("target deve ser 'sim' ou 'lab' para usar safe_session")
    _validate_motion_settings(cfg)
    tcp_offset = _tcp_offset(cfg["tool"]["tcp_offset"])
    settle = _number(cfg.get("session", {}).get("settle_after_disconnect_s", 0.0),
                     "session.settle_after_disconnect_s", allow_zero=True)
    # Uma sessão na bancada só pode começar depois de o docente validar a fronteira.
    if cfg["target"] == "lab":
        validate_tcp_boundary(cfg["safety"]["tcp_boundary_mm"])
        reduced_speed = _number(cfg["safety"]["reduced_max_joint_speed"],
                                "safety.reduced_max_joint_speed")
        _number(cfg["safety"]["reduced_max_tcp_speed"], "safety.reduced_max_tcp_speed")
        if cfg["motion"]["joint_speed"] > reduced_speed:
            raise ValueError("motion.joint_speed excede safety.reduced_max_joint_speed")
    log = get_logger(cfg)
    rc = cfg["robot"]
    log.info("alvo=%s ip=%s", cfg["target"], rc["ip"])
    arm = XArmAPI(rc["ip"], is_radian=False, check_joint_limit=rc.get("check_joint_limit", True))
    failed = False
    try:
        if not arm.connected:
            raise ConnectionError(f"sem ligação ao controlador em {rc['ip']}")
        arm.register_error_warn_changed_callback(
            lambda d: log.warning("erro/aviso: error_code=%s warn_code=%s",
                                  d.get("error_code"), d.get("warn_code")))
        if arm.error_code != 0:
            # Limpar um erro pode causar movimento inesperado (§A.4): só se faz aqui,
            # antes de qualquer comando, com alguém na paragem de emergência.
            log.warning("erro pendente %s ao ligar — a limpar", arm.error_code)
        check(arm.clean_warn(), "clean_warn", log)
        check(arm.clean_error(), "clean_error", log)
        if cfg["target"] == "lab":
            configure_reduced_safety(arm, cfg, log)
        check(arm.motion_enable(enable=True), "motion_enable", log)
        check(arm.set_tcp_offset(tcp_offset, wait=True), "set_tcp_offset", log)
        check(arm.set_mode(0), "set_mode(0)", log)
        check(arm.set_state(0), "set_state(0)", log)
        time.sleep(0.5)
        log.info("pronto: mode=%s state=%s error=%s", arm.mode, arm.state, arm.error_code)
        if not arm.connected or arm.mode != 0 or arm.state not in (0, 2) or arm.error_code != 0:
            raise RuntimeError("o controlador não ficou pronto após a configuração")
        yield arm, cfg, log
    except BaseException as exc:
        failed = True
        log.error("exceção na sessão (%s: %s) — paragem comandada", type(exc).__name__, exc)
        _request_stop(arm, log)
        raise
    finally:
        stop_failed = False
        if not failed and arm.connected:
            try:
                code, state = arm.get_state()
                if code != 0:
                    log.error("get_state falhou (code=%s) — paragem preventiva", code)
                # 0 = pronto, 2 = sem movimento, 4 = já parado. Um movimento
                # pausado (3) pode ter comandos pendentes e também deve parar.
                if code != 0 or state not in (0, 2, 4):
                    stop_failed = not _request_stop(arm, log)
            except Exception:
                log.exception("não foi possível confirmar o estado — paragem preventiva")
                stop_failed = not _request_stop(arm, log)
        disconnect_error = None
        try:
            arm.disconnect()
            log.info("desligado")
        except Exception as exc:
            disconnect_error = exc
            log.exception("não foi possível desligar a ligação ao controlador")
        finally:
            # O controlador precisa de tempo para libertar a ligação antes de aceitar outra.
            time.sleep(settle)
        # Numa exceção do corpo, preservamos a causa original; as falhas de
        # limpeza ficam no registo. Numa saída normal, comunicamo-las ao chamador.
        if not failed:
            if stop_failed:
                raise RuntimeError("o controlador não aceitou o comando de paragem")
            if disconnect_error is not None:
                raise RuntimeError("não foi possível desligar a ligação ao controlador") from disconnect_error


def move_joints(arm, joints, cfg: dict, log: logging.Logger, wait: bool = True) -> int:
    """Comanda seis juntas em graus; com ``wait=False`` não espera pelo fim."""
    _validate_motion_settings(cfg)
    angles = _joint_angles(joints, "joints")
    m = cfg["motion"]
    code = arm.set_servo_angle(angle=angles, speed=m["joint_speed"], mvacc=m["joint_acc"],
                               wait=wait, timeout=m["home_timeout_s"])
    return check(code, f"set_servo_angle{angles}", log)


def go_home(arm, cfg: dict, log: logging.Logger) -> dict:
    """Vai a home e confirma que as seis juntas ficaram dentro da tolerância."""
    _validate_motion_settings(cfg)
    m = cfg["motion"]
    home = _joint_angles(m["home_joints"], "motion.home_joints")
    t0 = time.monotonic()
    code = arm.set_servo_angle(angle=home, speed=m["joint_speed"], mvacc=m["joint_acc"],
                               wait=True, timeout=m["home_timeout_s"])
    dt = time.monotonic() - t0
    log.info("%-28s -> code=%s t=%.2fs", "set_servo_angle(home)", code, dt)
    check(code, "set_servo_angle(home)", log)
    # code=0 confirma o comando; só a leitura das juntas confirma a pose final.
    read_code, angles = arm.get_servo_angle(is_radian=False)
    check(read_code, "get_servo_angle(home)", log)
    if not isinstance(angles, (list, tuple)) or len(angles) < 6:
        raise RuntimeError("get_servo_angle(home) não devolveu seis juntas válidas")
    angles = [_signed_angle(a, f"get_servo_angle(home)[{i}]") for i, a in enumerate(angles[:6])]
    err = max(abs(a - h) for a, h in zip(angles, home))
    log.info("home: ângulos=%s erro_max=%.3f°", [round(a, 3) for a in angles], err)
    if err > m["home_tolerance_deg"]:
        raise RuntimeError(f"home fora da tolerância: erro máximo {err:.3f}° > "
                           f"{m['home_tolerance_deg']}°")
    return {"code": code, "time_s": dt, "max_err_deg": err, "angles": angles}
