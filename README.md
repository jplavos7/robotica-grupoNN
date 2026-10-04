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

Via escolhida: **de raiz, em máquina virtual** — VMware Workstation Pro 17,
Ubuntu 24.04.5 LTS, 8 GB RAM, 4 núcleos, 60 GB de disco, *Accelerate 3D graphics* ativo.

Nota: instalar o Ubuntu **sem rede** (o servidor pt.archive.ubuntu.com devolveu 403
ao descarregar o kernel); ligar a rede depois do primeiro arranque.

```bash
# servidor principal do Ubuntu
sudo sed -i 's|http://pt.archive.ubuntu.com|http://archive.ubuntu.com|g' /etc/apt/sources.list.d/ubuntu.sources
sudo apt update && sudo apt upgrade -y

# locale e repositórios
sudo apt install -y locales software-properties-common curl
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
sudo add-apt-repository universe

# fonte apt do ROS 2 (ver https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update

# ROS 2, ferramentas, MoveIt, Gazebo
sudo apt install -y ros-jazzy-desktop ros-dev-tools ros-jazzy-moveit ros-jazzy-ros-gz ros-jazzy-gz-ros2-control
sudo rosdep init && rosdep update

# shell (ROS_DOMAIN_ID provisório = 99, a trocar pelo número do grupo)
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "export ROS_DOMAIN_ID=99" >> ~/.bashrc
echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc   # sem isto o Gazebo treme/fica cinzento na VM
source ~/.bashrc
gz sim --version   # Gazebo Sim 8.x (Harmonic)

# pacotes do Lite 6
mkdir -p ~/dev_ws/src && cd ~/dev_ws/src
git clone https://github.com/xArm-Developer/xarm_ros2.git --recursive -b jazzy
rosdep install --from-paths . --ignore-src --rosdistro jazzy -y
cd ~/dev_ws && colcon build --parallel-workers 2
echo "source ~/dev_ws/install/setup.bash" >> ~/.bashrc && source ~/.bashrc
```

Testes: `ros2 run demo_nodes_cpp talker` / `ros2 run demo_nodes_py listener` (Teste 1),
`ros2 launch xarm_moveit_config lite6_moveit_fake.launch.py` (Teste 3),
`ros2 launch xarm_moveit_config lite6_moveit_gazebo.launch.py` (Teste 7).