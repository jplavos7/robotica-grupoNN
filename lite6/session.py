"""safe_session() e home — LW0, com parâmetros da aula 1 para o robô real.

Interface:
    with safe_session() as (arm, cfg, log): ...
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
    """Um ficheiro de registo por execução em logs/ (§A.5: registos desde o primeiro dia)."""
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
    """Regista cada comando com o código de retorno e falha alto se não for 0."""
    log.info("%-28s -> code=%s", what, code)
    if code != 0:
        raise RuntimeError(f"{what} falhou (code={code})")
    return code


def _check_speed_cap(cfg: dict) -> None:
    """S2: nunca comandar acima do teto configurado."""
    v, cap = cfg["motion"]["joint_speed"], cfg["safety"]["max_joint_speed"]
    if v > cap:
        raise ValueError(f"joint_speed={v} excede o teto max_joint_speed={cap} (S2)")


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
    """Aplica os limites da aula 1 antes de ativar o movimento no robô real."""
    safety = cfg["safety"]
    boundary = validate_tcp_boundary(safety["tcp_boundary_mm"])
    joint_speed = safety["reduced_max_joint_speed"]
    tcp_speed = safety["reduced_max_tcp_speed"]
    if joint_speed <= 0 or tcp_speed <= 0:
        raise ValueError("as velocidades do modo reduzido têm de ser positivas")
    check(arm.set_reduced_max_joint_speed(joint_speed, is_radian=False),
          "set_reduced_max_joint_speed", log)
    check(arm.set_reduced_max_tcp_speed(tcp_speed), "set_reduced_max_tcp_speed", log)
    check(arm.set_reduced_tcp_boundary(boundary), "set_reduced_tcp_boundary", log)
    check(arm.set_reduced_mode(True), "set_reduced_mode", log)
    check(arm.set_fence_mode(True), "set_fence_mode", log)


@contextlib.contextmanager
def safe_session(cfg: dict | None = None):
    """Liga-se, deixa o braço pronto, e garante paragem + desligar em qualquer saída."""
    cfg = cfg or load_config()
    _check_speed_cap(cfg)
    # Uma sessão na bancada só pode começar depois de o docente validar a fronteira.
    if cfg["target"] == "lab":
        validate_tcp_boundary(cfg["safety"]["tcp_boundary_mm"])
    log = get_logger(cfg)
    rc = cfg["robot"]
    log.info("alvo=%s ip=%s", cfg["target"], rc["ip"])
    arm = XArmAPI(rc["ip"], is_radian=False, check_joint_limit=rc.get("check_joint_limit", True))
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
        check(arm.set_tcp_offset(cfg["tool"]["tcp_offset"], wait=True), "set_tcp_offset", log)
        check(arm.set_mode(0), "set_mode(0)", log)
        check(arm.set_state(0), "set_state(0)", log)
        time.sleep(0.5)
        log.info("pronto: mode=%s state=%s error=%s", arm.mode, arm.state, arm.error_code)
        yield arm, cfg, log
    except BaseException as exc:
        log.error("exceção na sessão (%s: %s) — paragem comandada", type(exc).__name__, exc)
        try:
            arm.set_state(4)
        except Exception:
            log.exception("set_state(4) falhou")
        raise
    finally:
        arm.disconnect()
        log.info("desligado")
        # O controlador precisa de tempo para libertar a ligação antes de aceitar outra.
        time.sleep(cfg.get("session", {}).get("settle_after_disconnect_s", 0.0))


def move_joints(arm, joints, cfg: dict, log: logging.Logger, wait: bool = True) -> int:
    """Movimento em espaço de juntas (graus), com teto de velocidade e registo."""
    _check_speed_cap(cfg)
    m = cfg["motion"]
    code = arm.set_servo_angle(angle=list(joints), speed=m["joint_speed"], mvacc=m["joint_acc"],
                               wait=wait, timeout=m["home_timeout_s"])
    return check(code, f"set_servo_angle{list(joints)}", log)


def go_home(arm, cfg: dict, log: logging.Logger) -> dict:
    """Leva o braço a home_joints. Devolve código, tempo, erro máximo e ângulos finais."""
    _check_speed_cap(cfg)
    m = cfg["motion"]
    t0 = time.monotonic()
    code = arm.set_servo_angle(angle=m["home_joints"], speed=m["joint_speed"], mvacc=m["joint_acc"],
                               wait=True, timeout=m["home_timeout_s"])
    dt = time.monotonic() - t0
    log.info("%-28s -> code=%s t=%.2fs", "set_servo_angle(home)", code, dt)
    check(code, "set_servo_angle(home)", log)
    read_code, angles = arm.get_servo_angle(is_radian=False)
    check(read_code, "get_servo_angle(home)", log)
    if len(angles) < 6:
        raise RuntimeError("get_servo_angle(home) devolveu menos de 6 juntas")
    angles = [float(a) for a in angles[:6]]
    err = max(abs(a - h) for a, h in zip(angles, m["home_joints"]))
    log.info("home: ângulos=%s erro_max=%.3f°", [round(a, 3) for a in angles], err)
    return {"code": code, "time_s": dt, "max_err_deg": err, "angles": angles}
