"""Carrega config/robot.yaml e escolhe os parâmetros do alvo selecionado."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "robot.yaml"

REQUIRED_FIELDS = {
    "session": ("settle_after_disconnect_s",),
    "ros": ("domain_id",),
    "motion": ("home_joints", "joint_speed", "joint_acc", "home_tolerance_deg", "home_timeout_s"),
    "safety": ("max_joint_speed", "reduced_max_joint_speed", "reduced_max_tcp_speed",
               "tcp_boundary_mm"),
    "tool": ("tcp_offset",),
    "test_poses": ("start_joints", "far_joints", "pose_A_joints", "pose_B_joints"),
    "tests": ("n_connect", "n_home"),
    "logging": ("dir",),
}


def _required_map(parent: dict, key: str, path: Path, prefix: str = "") -> dict:
    field = f"{prefix}.{key}" if prefix else key
    if key not in parent:
        raise ValueError(f"Falta '{field}' em {path}")
    value = parent[key]
    if not isinstance(value, dict):
        raise ValueError(f"'{field}' em {path} deve ser um mapa YAML")
    return value


def load_config(path: str | Path | None = None, target: str | None = None) -> dict:
    """Lê o YAML e resolve o alvo (sim/lab).

    Prioridade do alvo: argumento > variável de ambiente LITE6_TARGET > campo 'target'.
    O dicionário devolvido tem cfg["robot"] = parâmetros do alvo escolhido.
    """
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"A configuração em {path} deve ser um mapa YAML")
    if "target" not in cfg:
        raise ValueError(f"Falta 'target' em {path}")
    if not isinstance(cfg["target"], str) or not cfg["target"].strip():
        raise ValueError(f"'target' em {path} deve ser o nome de um alvo não vazio")
    targets = _required_map(cfg, "targets", path)
    for section, fields in REQUIRED_FIELDS.items():
        values = _required_map(cfg, section, path)
        for field in fields:
            if field not in values:
                raise ValueError(f"Falta '{section}.{field}' em {path}")
    name = target or os.environ.get("LITE6_TARGET") or cfg["target"]
    if name not in targets:
        raise ValueError(f"Alvo '{name}' não existe em {path} (opções: {list(targets)})")
    cfg["target"] = name
    cfg["robot"] = _required_map(targets, name, path, "targets")
    if "ip" not in cfg["robot"]:
        raise ValueError(f"Falta 'targets.{name}.ip' em {path}")
    if "home_joints" in cfg["robot"]:
        cfg["motion"]["home_joints"] = cfg["robot"]["home_joints"]
    if "tcp_offset" in cfg["robot"]:
        cfg["tool"]["tcp_offset"] = cfg["robot"]["tcp_offset"]
    return cfg
