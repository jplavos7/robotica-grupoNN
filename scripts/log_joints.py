"""Regista as seis juntas durante a aula, sem comandar movimento.

Adaptação do log_joints.py da aula 1: IP na configuração, CSV preservado e
ligação fechada antes de abrir qualquer gráfico.
"""
from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime

from xarm.wrapper import XArmAPI

from lite6.config import ROOT, load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--plot", action="store_true", help="guardar também um gráfico PNG")
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("--seconds deve ser positivo")

    cfg = load_config()
    arm = XArmAPI(cfg["robot"]["ip"], is_radian=False,
                  check_joint_limit=cfg["robot"].get("check_joint_limit", True))
    samples: list[tuple[float, list[float]]] = []
    try:
        if not arm.connected:
            raise ConnectionError(f"sem ligação ao controlador em {cfg['robot']['ip']}")
        start = time.perf_counter()
        while time.perf_counter() - start < args.seconds:
            code, values = arm.get_servo_angle(is_radian=False)
            if code == 0 and len(values) >= 6:
                samples.append((time.perf_counter() - start, [float(v) for v in values[:6]]))
    finally:
        arm.disconnect()

    if not samples:
        raise RuntimeError("nenhuma leitura válida das seis juntas")
    output_dir = ROOT / cfg["logging"]["dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"joints_{cfg['target']}_{datetime.now():%Y%m%d_%H%M%S}"
    csv_path = output_dir / f"{stem}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["time_s", "j1_deg", "j2_deg", "j3_deg", "j4_deg", "j5_deg", "j6_deg"])
        writer.writerows((t, *angles) for t, angles in samples)

    duration = samples[-1][0] - samples[0][0]
    frequency = (len(samples) - 1) / duration if len(samples) > 1 and duration > 0 else 0.0
    print(f"{len(samples)} amostras; frequência média {frequency:.1f} Hz; {csv_path}")

    if args.plot:
        import matplotlib.pyplot as plt

        for joint in range(6):
            plt.plot([t for t, _ in samples], [a[joint] for _, a in samples], label=f"J{joint + 1}")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Ângulo (graus)")
        plt.legend()
        plt.tight_layout()
        png_path = output_dir / f"{stem}.png"
        plt.savefig(png_path, dpi=180)
        plt.close()
        print(png_path)


if __name__ == "__main__":
    main()
