"""Testes unitários que NÃO precisam de robô (§A.3, degrau 1). Correm a cada alteração."""
import re

import pytest
import yaml

from lite6.config import DEFAULT_CONFIG, ROOT, load_config

IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")


def test_config_loads():
    """Confirma que o YAML carrega e contém os dados básicos do alvo."""
    cfg = load_config()
    assert cfg["target"] in cfg["targets"]
    assert "ip" in cfg["robot"]
    assert len(cfg["motion"]["home_joints"]) == 6


def test_target_switch_is_one_parameter():
    """Confirma que sim e lab podem ser escolhidos sem editar o código."""
    for name in load_config()["targets"]:
        assert load_config(target=name)["robot"]["ip"]


def test_no_hardcoded_ip():
    """Procura endereços IP escritos diretamente nos scripts Python (T-I1)."""
    offenders = []
    for folder in ("lite6", "scripts"):
        for py in (ROOT / folder).rglob("*.py"):
            for n, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
                if IP_RE.search(line):
                    offenders.append(f"{py.relative_to(ROOT)}:{n}: {line.strip()}")
    assert not offenders, "IP no código:\n" + "\n".join(offenders)


def test_speed_within_cap():
    """Confirma que a velocidade pedida não excede o teto definido no YAML."""
    cfg = load_config()
    assert cfg["motion"]["joint_speed"] <= cfg["safety"]["max_joint_speed"]


def test_domain_id_is_group_number():
    """Exige o número do grupo em ros.domain_id; falha até ser atribuído."""
    assert 1 <= load_config()["ros"]["domain_id"] <= 16


@pytest.mark.parametrize("missing, field", [
    (("motion", "joint_acc"), "motion.joint_acc"),
    (("targets", "sim", "ip"), "targets.sim.ip"),
    (("safety",), "safety"),
])
def test_missing_config_field_is_named(tmp_path, missing, field):
    """Confirma que um campo em falta aparece pelo nome na mensagem de erro."""
    cfg = yaml.safe_load(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    section = cfg
    for key in missing[:-1]:
        section = section[key]
    del section[missing[-1]]
    path = tmp_path / "robot.yaml"
    path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match=re.escape(f"Falta '{field}'")):
        load_config(path=path, target="sim")
