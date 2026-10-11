"""Verificações locais da ligação e dos movimentos, sem ligar ao robô."""
from unittest.mock import Mock, patch

import pytest

from lite6.config import load_config
from lite6.session import (configure_reduced_safety, go_home, move_joints,
                           safe_session, validate_tcp_boundary)


@pytest.mark.parametrize("boundary", [None, [1, 2], [0, 1, 2, 1, 3, 2],
                                      [float("nan"), 0, 2, 1, 3, 2]])
def test_invalid_boundary_is_rejected(boundary):
    """Recusa fronteiras incompletas, invertidas ou com números inválidos."""
    with pytest.raises(ValueError):
        validate_tcp_boundary(boundary)


def test_lab_session_rejects_missing_boundary_before_connecting():
    """Impede a ligação ao robô real enquanto faltar a fronteira da bancada."""
    cfg = load_config(target="lab")
    with patch("lite6.session.XArmAPI") as api:
        with pytest.raises(ValueError, match="tcp_boundary_mm"):
            with safe_session(cfg):
                pass
        api.assert_not_called()


def test_reduced_limits_and_boundary_are_applied_in_order():
    """Confirma a ordem dos comandos usando uma fronteira fictícia de teste."""
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
    arm.set_reduced_max_joint_speed.assert_called_once_with(
        cfg["safety"]["reduced_max_joint_speed"], is_radian=False)
    arm.set_reduced_max_tcp_speed.assert_called_once_with(
        cfg["safety"]["reduced_max_tcp_speed"])
    arm.set_reduced_tcp_boundary.assert_called_once_with(
        [400.0, -400.0, 300.0, -300.0, 600.0, 100.0])


@pytest.mark.parametrize("state_code, state, should_stop", [
    (0, 1, True), (0, 2, False), (0, 3, True), (3, 2, True),
])
def test_safe_session_stop_on_normal_exit(state_code, state, should_stop):
    """Pede paragem ao sair se houver movimento, pausa ou estado incerto."""
    cfg = load_config(target="sim")
    # A sessão começa pronta; get_state representa o estado ao sair do bloco.
    arm = Mock(connected=True, error_code=0, mode=0, state=2)
    arm.get_state.return_value = (state_code, state)
    for name in ("clean_warn", "clean_error", "motion_enable", "set_tcp_offset", "set_mode",
                 "set_state"):
        getattr(arm, name).return_value = 0
    with patch("lite6.session.XArmAPI", return_value=arm), \
         patch("lite6.session.get_logger"), \
         patch("lite6.session.time.sleep"):
        with safe_session(cfg):
            pass
    if should_stop:
        arm.set_state.assert_any_call(4)
    else:
        arm.set_state.assert_called_once_with(0)
    arm.disconnect.assert_called_once_with()


def test_safe_session_reports_failed_stop_after_disconnect():
    """Comunica que o comando de paragem falhou e ainda tenta desligar."""
    cfg = load_config(target="sim")
    arm = Mock(connected=True, error_code=0, mode=0, state=2)
    arm.get_state.return_value = (0, 1)
    for name in ("clean_warn", "clean_error", "motion_enable", "set_tcp_offset", "set_mode"):
        getattr(arm, name).return_value = 0
    arm.set_state.side_effect = lambda state: 3 if state == 4 else 0
    with patch("lite6.session.XArmAPI", return_value=arm), \
         patch("lite6.session.get_logger"), \
         patch("lite6.session.time.sleep"):
        with pytest.raises(RuntimeError, match="comando de paragem"):
            with safe_session(cfg):
                pass
    arm.disconnect.assert_called_once_with()


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf"), True])
def test_invalid_joint_speed_is_rejected_before_connecting(value):
    """Recusa velocidades inválidas antes de abrir a ligação ao controlador."""
    cfg = load_config(target="sim")
    cfg["motion"]["joint_speed"] = value
    with patch("lite6.session.XArmAPI") as api:
        with pytest.raises(ValueError, match="motion.joint_speed"):
            with safe_session(cfg):
                pass
        api.assert_not_called()


def test_invalid_tcp_offset_is_rejected_before_connecting():
    """Recusa um offset TCP inválido antes de abrir a ligação."""
    cfg = load_config(target="sim")
    cfg["tool"]["tcp_offset"] = [0, 0, float("inf"), 0, 0, 0]
    with patch("lite6.session.XArmAPI") as api:
        with pytest.raises(ValueError, match="tool.tcp_offset"):
            with safe_session(cfg):
                pass
        api.assert_not_called()


@pytest.mark.parametrize("joints", [[0] * 5, [0, 0, 0, 0, 0, float("nan")]])
def test_invalid_joint_target_is_rejected_without_movement(joints):
    """Não envia movimento se faltarem juntas ou algum ângulo for inválido."""
    arm = Mock()
    with pytest.raises(ValueError, match="joints"):
        move_joints(arm, joints, load_config(target="sim"), Mock())
    arm.set_servo_angle.assert_not_called()


def test_go_home_rejects_position_outside_tolerance():
    """Deteta quando a posição final excede a tolerância do home."""
    cfg = load_config(target="sim")
    arm = Mock()
    arm.set_servo_angle.return_value = 0
    arm.get_servo_angle.return_value = (0, [1, 0, 0, 0, 0, 0])
    with pytest.raises(RuntimeError, match="fora da tolerância"):
        go_home(arm, cfg, Mock())


def test_session_keeps_original_error_if_disconnect_fails():
    """Preserva a primeira exceção se também falhar o desligar."""
    cfg = load_config(target="sim")
    arm = Mock(connected=True, error_code=0, mode=0, state=2)
    for name in ("clean_warn", "clean_error", "motion_enable", "set_tcp_offset", "set_mode",
                 "set_state"):
        getattr(arm, name).return_value = 0
    arm.disconnect.side_effect = OSError("ligação perdida")
    with patch("lite6.session.XArmAPI", return_value=arm), \
         patch("lite6.session.get_logger"), \
         patch("lite6.session.time.sleep"):
        with pytest.raises(ValueError, match="falha original"):
            with safe_session(cfg):
                raise ValueError("falha original")
    arm.set_state.assert_any_call(4)
