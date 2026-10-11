"""Verificações locais das condições antes de abrir uma sessão no robô real."""
from unittest.mock import Mock, patch

import pytest

from lite6.config import load_config
from lite6.session import configure_reduced_safety, safe_session, validate_tcp_boundary


@pytest.mark.parametrize("boundary", [None, [1, 2], [0, 1, 2, 1, 3, 2],
                                      [float("nan"), 0, 2, 1, 3, 2]])
def test_invalid_boundary_is_rejected(boundary):
    with pytest.raises(ValueError):
        validate_tcp_boundary(boundary)


def test_lab_session_rejects_missing_boundary_before_connecting():
    cfg = load_config(target="lab")
    with patch("lite6.session.XArmAPI") as api:
        with pytest.raises(ValueError, match="tcp_boundary_mm"):
            with safe_session(cfg):
                pass
        api.assert_not_called()


def test_reduced_limits_and_boundary_are_applied_in_order():
    cfg = load_config(target="lab")
    cfg["safety"]["tcp_boundary_mm"] = [400, -400, 300, -300, 600, 100]
    calls = []
    arm = Mock()
    for name in ("set_reduced_max_joint_speed", "set_reduced_max_tcp_speed",
                 "set_reduced_tcp_boundary", "set_reduced_mode", "set_fence_mode"):
        getattr(arm, name).side_effect = lambda *args, _name=name, **kwargs: calls.append(_name) or 0
    configure_reduced_safety(arm, cfg, Mock())
    assert calls == ["set_reduced_max_joint_speed", "set_reduced_max_tcp_speed",
                     "set_reduced_tcp_boundary", "set_reduced_mode", "set_fence_mode"]
    arm.set_reduced_max_joint_speed.assert_called_once_with(54.0, is_radian=False)
    arm.set_reduced_max_tcp_speed.assert_called_once_with(150.0)
    arm.set_reduced_tcp_boundary.assert_called_once_with(
        [400.0, -400.0, 300.0, -300.0, 600.0, 100.0])
