"""Exercício de ciclo de vida (§D.3b): testes dos requisitos de safe_session e home.

Corre contra o alvo de config/robot.yaml (simulador por omissão).
Resultado: tabela no ecrã + logs/lifecycle_<alvo>_<data>.csv (evidência para o relatório).
"""
import copy
import csv
import statistics
import subprocess
import sys
import time
from datetime import datetime

from lite6.config import ROOT, load_config
from lite6.session import go_home, move_joints, safe_session

# Limiar / alvo dos requisitos de desempenho (fazem parte da especificação, não da configuração)
P1_LIMIAR, P1_ALVO = 5.0, 2.0     # s, pior abertura de sessão
P2_LIMIAR, P2_ALVO = 15.0, 8.0    # s, pior home a partir de start_joints
IMOVEL_DEG = 0.05                 # graus em 1 s

RESULTS: list[dict] = []


class InducedFault(Exception):
    """Falha induzida de propósito pelos testes; distinta de qualquer falha real."""


def record(test_id, req, passed, measured, criterion):
    res = "PASSA" if passed else "FALHA"
    RESULTS.append({"teste": test_id, "requisito": req, "resultado": res,
                    "medido": measured, "criterio": criterion})
    print(f"[{res}] {test_id} ({req}): {measured}   | critério: {criterion}")


def max_diff(a, b):
    return max(abs(float(x) - float(y)) for x, y in zip(a[:6], b[:6]))


def t_f1(cfg):
    with safe_session(cfg) as (arm, _, _):
        ok = arm.connected and arm.mode == 0 and arm.state != 4 and arm.error_code == 0
        med = f"connected={arm.connected} mode={arm.mode} state={arm.state} error={arm.error_code}"
    record("T-F1", "R1", ok, med, "ligado, mode=0, state≠4, error_code=0")


def t_f2(cfg):
    ref = {}
    try:
        with safe_session(cfg) as (arm, _, _):
            ref["arm"] = arm
            raise InducedFault("falha induzida (T-F2)")
    except InducedFault:
        pass
    ok = not ref["arm"].connected
    record("T-F2", "R2", ok, f"connected após exceção={ref['arm'].connected}", "connected=False")


def t_f3(cfg):
    tol = cfg["motion"]["home_tolerance_deg"]
    with safe_session(cfg) as (arm, _, log):
        move_joints(arm, cfg["test_poses"]["start_joints"], cfg, log)
        r = go_home(arm, cfg, log)
    ok = r["code"] == 0 and r["max_err_deg"] <= tol
    record("T-F3", "R3", ok, f"code={r['code']} erro_max={r['max_err_deg']:.3f}°",
           f"code=0 e erro_max ≤ {tol}°")


def t_p1(cfg):
    n, times = cfg["tests"]["n_connect"], []
    for _ in range(n):
        t0 = time.monotonic()
        with safe_session(cfg):
            times.append(time.monotonic() - t0)
    worst = max(times)
    alvo = "alvo cumprido" if worst < P1_ALVO else "alvo NÃO cumprido"
    record("T-P1", "P1", worst < P1_LIMIAR,
           f"pior={worst:.2f}s média={statistics.mean(times):.2f}s n={n} ({alvo})",
           f"pior < {P1_LIMIAR}s (alvo < {P1_ALVO}s)")


def t_p2(cfg):
    n, times = cfg["tests"]["n_home"], []
    with safe_session(cfg) as (arm, _, log):
        for _ in range(n):
            move_joints(arm, cfg["test_poses"]["start_joints"], cfg, log)
            times.append(go_home(arm, cfg, log)["time_s"])
    worst = max(times)
    alvo = "alvo cumprido" if worst < P2_ALVO else "alvo NÃO cumprido"
    record("T-P2", "P2", worst < P2_LIMIAR,
           f"pior={worst:.2f}s média={statistics.mean(times):.2f}s n={n} ({alvo})",
           f"pior < {P2_LIMIAR}s (alvo < {P2_ALVO}s)")


def t_s1(cfg):
    far = cfg["test_poses"]["far_joints"]
    try:
        with safe_session(cfg) as (arm, _, log):
            move_joints(arm, cfg["test_poses"]["start_joints"], cfg, log)
            move_joints(arm, far, cfg, log, wait=False)
            time.sleep(0.8)
            raise InducedFault("falha induzida a meio do movimento (T-S1)")
    except InducedFault:
        pass
    time.sleep(1.0)
    with safe_session(cfg) as (arm, _, _):
        _, a1 = arm.get_servo_angle(is_radian=False)
        time.sleep(1.0)
        _, a2 = arm.get_servo_angle(is_radian=False)
    drift, dist = max_diff(a1, a2), max_diff(a2, far)
    ok = drift < IMOVEL_DEG and dist > 1.0
    record("T-S1", "S1", ok, f"deriva em 1s={drift:.3f}° distância ao alvo={dist:.1f}°",
           f"deriva < {IMOVEL_DEG}° e alvo não atingido")


def t_s2(cfg):
    bad = copy.deepcopy(cfg)
    bad["motion"]["joint_speed"] = cfg["safety"]["max_joint_speed"] * 2
    with safe_session(cfg) as (arm, _, log):
        move_joints(arm, cfg["test_poses"]["start_joints"], cfg, log)
        _, before = arm.get_servo_angle(is_radian=False)
        try:
            go_home(arm, bad, log)
            refused = False
        except ValueError:
            refused = True
        time.sleep(0.5)
        _, after = arm.get_servo_angle(is_radian=False)
    moved = max_diff(before, after)
    record("T-S2", "S2", refused and moved < IMOVEL_DEG,
           f"recusou={refused} movimento={moved:.3f}°", "recusa (ValueError) e sem movimento")


def t_i1(cfg):
    p = subprocess.run([sys.executable, "-m", "pytest", "-q",
                        "tests/test_config.py::test_no_hardcoded_ip"],
                       cwd=ROOT, capture_output=True, text=True)
    last = (p.stdout.strip().splitlines() or ["(sem saída)"])[-1]
    record("T-I1", "I1", p.returncode == 0, last, "pytest test_no_hardcoded_ip passa")


TESTS = [("T-F1", "R1", t_f1), ("T-F2", "R2", t_f2), ("T-F3", "R3", t_f3),
         ("T-P1", "P1", t_p1), ("T-P2", "P2", t_p2), ("T-I1", "I1", t_i1),
         ("T-S1", "S1", t_s1), ("T-S2", "S2", t_s2)]


def main() -> None:
    cfg = load_config()
    print(f"alvo: {cfg['target']} ({cfg['robot']['ip']})\n")
    if cfg["target"] != "sim":
        ans = input("ATENÇÃO: robô real. O docente autorizou e há alguém na paragem de emergência? [s/N] ")
        if ans.strip().lower() != "s":
            sys.exit("abortado")
    for tid, req, fn in TESTS:
        try:
            fn(cfg)
        except Exception as e:  # a PRIMEIRA mensagem de erro fica registada, como pede a ficha
            record(tid, req, False, f"exceção: {type(e).__name__}: {e}", "—")

    out = ROOT / cfg["logging"]["dir"] / f"lifecycle_{cfg['target']}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(RESULTS[0]))
        w.writeheader()
        w.writerows(RESULTS)
    n_ok = sum(r["resultado"] == "PASSA" for r in RESULTS)
    print(f"\n{n_ok}/{len(RESULTS)} passam. Resultados em {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()