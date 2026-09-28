"""Teste 8: FK do SDK para a Pose A (ou B) vs a matriz tf2 do Teste 5.

    python scripts/test8_fk_compare.py --pose A --tf2-xyz 0.087 0.000 0.154

--tf2-xyz é a "Translation" que o tf2_echo imprimiu, em METROS.
O SDK devolve milímetros e graus; o ROS 2 usa metros e radianos (requisito de interface!).
"""
import argparse

import numpy as np
from scipy.spatial.transform import Rotation

from lite6.session import safe_session


def pose_to_T(pose_mm_deg) -> np.ndarray:
    """[x,y,z (mm), roll,pitch,yaw (graus)] do SDK -> matriz 4x4 em metros.

    Convenção do SDK: ângulos fixos X-Y-Z, R = Rz(yaw) Ry(pitch) Rx(roll).
    (No LW1 esta função passa para lite6/kinematics.py.)
    """
    x, y, z, roll, pitch, yaw = pose_mm_deg[:6]
    T = np.eye(4)
    T[:3, :3] = Rotation.from_euler("xyz", [roll, pitch, yaw], degrees=True).as_matrix()
    T[:3, 3] = np.array([x, y, z]) / 1000.0
    return T


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pose", choices=["A", "B"], default="A")
    ap.add_argument("--tf2-xyz", type=float, nargs=3, metavar=("X", "Y", "Z"))
    args = ap.parse_args()

    with safe_session() as (arm, cfg, log):
        q = cfg["test_poses"][f"pose_{args.pose}_joints"]
        code, pose = arm.get_forward_kinematics(q, input_is_radian=False, return_is_radian=False)
        log.info("get_forward_kinematics(%s) -> code=%s pose=%s", q, code, pose)

    np.set_printoptions(precision=5, suppress=True)
    T = pose_to_T(pose)
    print(f"Pose {args.pose}: juntas = {q} graus")
    print(f"SDK pose  = {[round(p, 3) for p in pose]} (mm, graus)")
    print("SDK T (m) =\n", T)
    if args.tf2_xyz:
        d_mm = (np.array(args.tf2_xyz) - T[:3, 3]) * 1000.0
        print(f"tf2 - SDK = {np.round(d_mm, 4)} mm   |d| = {np.linalg.norm(d_mm):.4f} mm")


if __name__ == "__main__":
    main()
