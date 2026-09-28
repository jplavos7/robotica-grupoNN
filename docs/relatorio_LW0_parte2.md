# LW0 — Parte 2: Ambiente e Ciclo de Vida — Grupo NN

## 1. Ambiente (máx. 4 páginas)

| Item | Valor |
|---|---|
| Nível(eis) instalado(s) | intermédio + avançado |
| Via | Docker / de raiz |
| Variante | VM (VMware ...) / nativo / WSL2 |
| SO anfitrião | ... |
| ROS_DOMAIN_ID | NN |
| Versão `gz sim --version` | 8.x |

### Testes 1–8 (§C.5)

| Teste | Descrição | Passa/Falha | Primeira mensagem de erro (texto) / notas |
|---|---|---|---|
| 1 | talker/listener | | |
| 2 | pacotes UFACTORY visíveis | | |
| 3 | lite6_moveit_fake (RViz) | | |
| 4 | view_frames — nº de referenciais: __ ; primeiro: `____` ; último: `____` | | |
| 5 | tf2_echo link_base → link_eef | | |
| 6 | gz sim shapes.sdf | | |
| 7 | lite6_moveit_gazebo | | |
| 8 | SDK vs simulador de firmware | | |

### Teste 5 — matrizes 4×4 (tf2, metros)

Pose A (home), juntas [rad] = [ , , , , , ] = [graus] [ , , , , , ]
```
T_A =
```
Pose B, juntas [rad] = [ , , , , , ] = [graus] [ , , , , , ]
```
T_B =
```

### Teste 7 — Gazebo vs RViz (uma frase)
> ...

### Teste 8 — FK do SDK vs tf2 (Pose A)
| | x | y | z |
|---|---|---|---|
| tf2 (mm) | | | |
| SDK (mm) | | | |
| diferença (mm) | | | |
Norma da diferença: ___ mm. Comentário (unidades mm/graus vs m/rad; offset do TCP): ...

## 2. Exercício de ciclo de vida (máx. 2 páginas)

### (a) Requisitos de `safe_session` e `home`

| ID | Tipo | Requisito ("deve") | Teste |
|---|---|---|---|
| R1 | Funcional | `safe_session` deve ligar-se ao controlador cujo IP está em `config/robot.yaml` e deixar o braço pronto (mode = 0, state ≠ 4, error_code = 0). | T-F1 |
| R2 | Funcional | `safe_session` deve fechar a ligação ao sair, também quando é levantada uma exceção dentro da sessão. | T-F2 |
| R3 | Funcional | `home` deve levar as 6 juntas a `home_joints` com código de retorno 0 e erro máximo ≤ 0.5°. | T-F3 |
| P1 | Desempenho | Tempo de abertura de `safe_session` (construção até pronto), pior de 10: limiar < 5 s, alvo < 2 s. | T-P1 |
| P2 | Desempenho | Duração de `home` a partir de `start_joints`, pior de 5: limiar < 15 s, alvo < 8 s. | T-P2 |
| I1 | Interface | Todos os parâmetros (IP, home, velocidades, offset) devem vir de `config/robot.yaml`; nenhum endereço IP aparece no código Python. Unidades no SDK: mm e graus (`is_radian=False`). | T-I1 |
| S1 | Segurança | Se ocorrer uma exceção durante um movimento, `safe_session` deve comandar paragem (state 4) e o braço deve ficar imóvel (< 0.05° em 1 s) sem atingir o alvo; verificado por falha induzida. | T-S1 |
| S2 | Segurança | `home` deve recusar executar, sem qualquer movimento, se a velocidade configurada exceder `max_joint_speed`; verificado com configuração induzida. | T-S2 |

### (b) Resultados (de `logs/lifecycle_*.csv`)

| Teste | Alvo (sim/braço) | Passa/Falha | Valor medido |
|---|---|---|---|
| T-F1 | sim | | |
| T-F2 | sim | | |
| T-F3 | sim | | |
| T-P1 | sim | | pior = __ s (alvo cumprido? ) |
| T-P2 | sim | | pior = __ s (alvo cumprido? ) |
| T-I1 | — | | |
| T-S1 | sim | | deriva = __°, distância = __° |
| T-S2 | sim | | |

Requisitos não cumpridos: valor medido + análise do porquê (vale mais do que um "cumprido" sem evidência).

### (c) Matriz de rastreabilidade

| Requisito | Módulo / função | Teste | Script | Resultado |
|---|---|---|---|---|
| R1 | `lite6/session.py::safe_session` | T-F1 | `scripts/lifecycle_tests.py` | |
| R2 | `lite6/session.py::safe_session` (finally) | T-F2 | `scripts/lifecycle_tests.py` | |
| R3 | `lite6/session.py::go_home` | T-F3 | `scripts/lifecycle_tests.py` | |
| P1 | `lite6/session.py::safe_session` | T-P1 | `scripts/lifecycle_tests.py` | |
| P2 | `lite6/session.py::go_home` | T-P2 | `scripts/lifecycle_tests.py` | |
| I1 | `lite6/config.py::load_config`, `config/robot.yaml` | T-I1 | `tests/test_config.py` | |
| S1 | `lite6/session.py::safe_session` (except → set_state(4)) | T-S1 | `scripts/lifecycle_tests.py` | |
| S2 | `lite6/session.py::_check_speed_cap` | T-S2 | `scripts/lifecycle_tests.py` | |

Matriz de cobertura: cada requisito tem ≥ 1 teste; cada teste rastreia para ≥ 1 requisito.

### (d) Modelo em V
![Modelo em V](modelo_V.svg)
