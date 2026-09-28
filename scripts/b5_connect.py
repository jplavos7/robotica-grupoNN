"""§B.5 ponto 2 e Teste 8: liga-se via safe_session, imprime ângulos e pose.

    python scripts/b5_connect.py          # só lê
    python scripts/b5_connect.py --move   # vai a start_joints e volta a home (vê-se no Studio)
"""
import argparse

from lite6.session import go_home, move_joints, safe_session


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--move", action="store_true", help="mover para start_joints e voltar a home")
    args = ap.parse_args()

    with safe_session() as (arm, cfg, log):
        code, angles = arm.get_servo_angle(is_radian=False)
        code2, pose = arm.get_position(is_radian=False)
        print(f"alvo     : {cfg['target']} ({cfg['robot']['ip']})  firmware {arm.version}")
        print(f"ângulos  : {[round(a, 3) for a in angles[:6]]} graus (code={code})")
        print(f"pose TCP : {[round(p, 3) for p in pose]} mm/graus (code={code2})")
        if args.move:
            move_joints(arm, cfg["test_poses"]["start_joints"], cfg, log)
            r = go_home(arm, cfg, log)
            print(f"home     : code={r['code']} t={r['time_s']:.2f}s erro_max={r['max_err_deg']:.3f}°")


if __name__ == "__main__":
    main()
