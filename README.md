## Obter o projeto

Com acesso ao repositório privado do grupo, clonar uma vez e entrar na pasta:

```
git clone https://github.com/jplavos7/robotica-grupoNN.git
cd robotica-grupoNN
```

Se a pasta já existir, entrar nela; não é necessário clonar novamente.

## 1. Recriar o ambiente a partir do zero (Python ≥ 3.10)

Linux / macOS:

```bash
python3 -m venv ~/venvs/robotica
source ~/venvs/robotica/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Windows (Linha de comandos, `cmd`):

```bat
python -m venv %USERPROFILE%\venvs\robotica
%USERPROFILE%\venvs\robotica\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

PowerShell (ex.: terminal do VS Code), sem depender da permissão para executar
`Activate.ps1`:

```powershell
python -m venv "$env:USERPROFILE\venvs\robotica"
$roboticaPython = "$env:USERPROFILE\venvs\robotica\Scripts\python.exe"
& $roboticaPython -m pip install --upgrade pip
& $roboticaPython -m pip install -r requirements.txt
& $roboticaPython -m pip install -e .
```

Se o ambiente já existir, saltar a primeira linha. Na mesma janela PowerShell,
usar `& $roboticaPython` no lugar de `python` nos comandos seguintes e
`& $roboticaPython -m pytest` no lugar de `pytest`.

O `pip install -e .` instala o pacote `lite6`, para os imports funcionarem em `scripts/` e no IDE.
No IDE, escolher o interpretador de `venvs/robotica`.

## 2. Verificar (sem robô)

```
pytest -q
```

No PowerShell sem ativação: `& $roboticaPython -m pytest -q`.

Enquanto o número do grupo não for atribuído, espera-se uma falha:
`test_domain_id_is_group_number`, porque `config/robot.yaml` ainda tem
`ros.domain_id: 0`. Na versão publicada eram 4 testes passados e 1 falhado;
esta cópia acrescenta testes de segurança sem robô. Depois de atribuído,
colocar esse número no YAML e na VM e repetir todos os testes.

## 3. ROS 2 na VM: repetir os Testes 1 e 3 (§C.5)

Na VM Ubuntu onde ROS 2 Jazzy e `xarm_ros2` já estão instalados, abrir dois
terminais. Em **cada um**, preparar o ambiente:

```bash
source /opt/ros/jazzy/setup.bash
source ~/dev_ws/install/setup.bash
export ROS_DOMAIN_ID=NUMERO_DO_GRUPO
echo "$ROS_DOMAIN_ID"
```

Substituir `NUMERO_DO_GRUPO` pelo número atribuído antes de executar. Os dois
terminais devem mostrar o mesmo número. Enquanto não existir número atribuído,
estes testes na rede do laboratório ficam pendentes.

**Teste 1:** no primeiro terminal executar `ros2 run demo_nodes_cpp talker`;
no segundo, `ros2 run demo_nodes_py listener`. Confirmar mensagens
`I heard: [Hello World: ...]` sucessivas. Parar ambos com Ctrl+C.

**Teste 3:** num terminal preparado da mesma forma, executar
`ros2 launch xarm_moveit_config lite6_moveit_fake.launch.py`. Confirmar que o
RViz abre com o Lite 6 e o painel MotionPlanning. Registar o primeiro erro se
falhar.

## 4. Simulador de firmware UFACTORY (§C.4)

No Windows, abrir o Docker Desktop e esperar que o motor esteja pronto. Antes
de criar ou iniciar o contentor, confirmar que o motor Linux responde e ver se
o contentor já existe:

```powershell
docker info --format '{{.OSType}}'
docker ps -a --filter name=uf_software
```

O primeiro comando deve imprimir `linux`. Se falhar por falta de ligação à API
do Docker, esperar pelo arranque do Docker Desktop e repetir. Se o segundo
comando listar `uf_software`, usar «Vezes seguintes»; caso contrário, usar
«Primeira vez».

Primeira vez (uma só linha):

```
docker run -it --name uf_software -p 18333:18333 -p 502:502 -p 503:503 -p 504:504 -p 30000:30000 -p 30001:30001 -p 30002:30002 -p 30003:30003 danielwang123321/uf-ubuntu-docker
```

Vezes seguintes:

```
docker start -ai uf_software
```

Dentro do contentor, arrancar o firmware com o perfil Lite 6:

```
/xarm_scripts/xarm_start.sh 6 9
```

Studio: http://127.0.0.1:18333

## 5. SDK no simulador: repetir o Teste 8 (§C.5)

Com o firmware ativo e o alvo `target: sim` em `config/robot.yaml`, abrir outro
terminal na pasta do projeto. No PowerShell, confirmar com `Get-Location` que a
pasta termina em `robotica-grupoNN`; se não terminar, entrar nessa pasta antes
de executar `scripts/b5_connect.py`. Sem ativação, definir novamente
`$roboticaPython = "$env:USERPROFILE\venvs\robotica\Scripts\python.exe"` nesse
novo terminal.
Começar por preparar a sessão e ler juntas/pose sem comandar uma trajetória;
só depois confirmar movimento no Studio:

```powershell
& $roboticaPython scripts/b5_connect.py
& $roboticaPython scripts/b5_connect.py --move
& $roboticaPython scripts/test8_fk_compare.py --pose A --tf2-xyz 0.087 0.000 0.154
& $roboticaPython scripts/test8_fk_compare.py --pose B --tf2-xyz 0.087 0.269 0.154
```

Em Linux/macOS, com o ambiente virtual ativado, substituir `& $roboticaPython`
por `python`.

O primeiro comando ativa o controlador e configura a sessão, embora não envie
uma trajetória de movimento. Confirmar no Studio que o braço responde a um
pequeno movimento manual (*jog*) em `Sim` antes de executar `--move`.

Os valores `--tf2-xyz` estão em metros e vêm das leituras das Poses A e B no
Teste 5; para outra pose, usar os valores medidos nessa pose. Registar os ângulos, a
pose, a matriz e a diferença apresentada. É o comando `--move` que move o braço
virtual no Studio; `test8_fk_compare.py` calcula a cinemática direta sem
comandar movimento. Os valores usados estão em `docs/evidencias/poseA_tf2.txt`
e `docs/evidencias/poseB_tf2.txt`. Depois de `--move`, o Studio fica na posição
`home` (Pose A); a matriz calculada para a Pose B não tem de coincidir com os
valores atuais apresentados no Studio, porque o braço não se desloca para B.

Para repetir separadamente os oito testes do exercício de ciclo de vida:

```powershell
& $roboticaPython scripts/lifecycle_tests.py
```

Alvo: `target:` em `config/robot.yaml` (`sim` ou `lab`). Contra o robô real:
só com autorização do docente e um membro na paragem de emergência.

## 6. Material da aula 1

Em `docs/aula1/` estão o relatório de três páginas e os gráficos da aula 1.
As notas mais detalhadas estão em `docs/aula1/notas.md`. O script
`scripts/log_joints.py` adapta o programa usado nessa aula para registar os
ângulos das juntas:

```powershell
& $roboticaPython -m scripts.log_joints --seconds 30 --plot
```

Em Linux/macOS ou `cmd`, com o ambiente ativado, usar
`python -m scripts.log_joints --seconds 30 --plot`.

O script lê as seis juntas e guarda CSV e PNG em `logs/`. Para trabalho em modo
manual no robô real, selecionar `target: lab` em `config/robot.yaml` e confirmar
o IP na bancada. Este script não comanda movimento.
Se não houver movimento durante os 30 segundos, o gráfico mostrará linhas
horizontais; algumas podem sobrepor-se quando duas juntas têm o mesmo ângulo.
No simulador, a frequência apresentada é a taxa de consultas ao SDK, não a
frequência de novas medições físicas do robô.

A sessão em `lite6/session.py` tem registados os valores da aula 1 (54°/s nas
juntas e 150 mm/s no TCP) para o alvo `lab`. **Antes de usar o robô real, confirmar
com o docente** estes valores, o IP, o home, o offset da garra e os limites e
critérios de teste em `config/robot.yaml`. Definir também, com o docente, os seis
limites da bancada em `safety.tcp_boundary_mm`; sem eles a sessão recusa ligar-se.
O modo reduzido foi observado no Studio, mas a aplicação da fronteira pelo
script ainda não foi testada no robô.

O `home` do alvo `lab` e o offset da garra vêm do relatório da aula 1; os
valores do simulador continuam separados. O número do grupo em `ros.domain_id`
também está por definir.
