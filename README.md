# robotica-grupoNN — Robotics 2026/2027 (Lite 6)

Grupo NN: <nome 1> (<nº>), <nome 2> (<nº>) · `ROS_DOMAIN_ID` = NN

## 1. Recriar o ambiente a partir do zero (Python ≥ 3.10)

```bash
python3 -m venv ~/venvs/robotica
source ~/venvs/robotica/bin/activate        # Windows: %USERPROFILE%\venvs\robotica\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .                             # instala o pacote lite6 (imports funcionam em scripts/ e no IDE)
```

No IDE (VS Code/PyCharm), escolher explicitamente o interpretador `~/venvs/robotica/bin/python`.

## 2. Verificar (sem robô)

```bash
pytest -q          # deve passar tudo
```

## 3. Simulador de firmware UFACTORY (§C.4)

```bash
docker run -it --name uf_software -p 18333:18333 -p 502:502 -p 503:503 -p 504:504 \
  -p 30000:30000 -p 30001:30001 -p 30002:30002 -p 30003:30003 danielwang123321/uf-ubuntu-docker
# dentro do contentor: arrancar o firmware com o perfil Lite 6 (argumentos "6 9")
# Studio: http://127.0.0.1:18333
```
Nas vezes seguintes: `docker start -ai uf_software`.

## 4. Correr

```bash
python scripts/b5_connect.py --move                        # §B.5 / Teste 8
python scripts/test8_fk_compare.py --pose A --tf2-xyz X Y Z  # Teste 8 (tf2 em metros)
python scripts/lifecycle_tests.py                          # exercício de ciclo de vida
```

Alvo: `target:` em `config/robot.yaml` (`sim` ou `lab`), ou `LITE6_TARGET=lab python ...`.
Contra o robô real: só com autorização do docente e um membro na paragem de emergência.

## 5. Nível avançado (ROS 2 Jazzy + MoveIt 2 + Gazebo Harmonic)

Via escolhida: <Docker / de raiz (VM / nativo)> — ver relatório.
<colar aqui os comandos exatos que usaram>

## Etiquetas entregues
`delivery-1` (LW0 + LW1 + LW2), `delivery-2`, `delivery-3`.
