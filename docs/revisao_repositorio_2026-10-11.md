# Revisão do repositório e integração da aula 1

Esta nota descreve a cópia de trabalho de `robotica-grupoNN` em 11/10/2026.
A revisão começou a partir da `main` publicada por `jplavos7`, no commit
`4f7277809efe70dfceb8db7b78553be42ae48f05`. As alterações descritas
abaixo estão nesta cópia; não foram enviadas por nós para o GitHub nem
aplicadas à pasta original do projeto.

## O que foi revisto e alterado

- O `README.md` passou a explicar melhor os passos para Windows e PowerShell,
  incluindo o ambiente virtual, o simulador, os testes e o registo das juntas.
- `config/robot.yaml` distingue os valores do simulador dos observados na aula 1
  para o robô real. Os comentários indicam o que ainda precisa de confirmação.
  `ros.domain_id` continua em `0`, pois o número do grupo ainda não foi atribuído.
- `lite6/config.py` passou a indicar qual o campo em falta quando a configuração
  YAML está incompleta, em vez de apresentar apenas um `KeyError`.
- `lite6/session.py` passou a validar os valores antes de ligar ou mover, a
  verificar os códigos de retorno e a confirmar a posição final de `home`.
  Também procura parar o braço quando a sessão falha e fecha a ligação ao sair.
  No alvo `lab`, prepara o modo reduzido e a fronteira TCP; sem os seis limites
  da fronteira, recusa ligar-se. Esta parte ainda não foi testada no robô real.
- `scripts/b5_connect.py` e `scripts/test8_fk_compare.py` verificam os códigos
  devolvidos pelas leituras do SDK. `scripts/lifecycle_tests.py` foi revisto e
  mantido como estava.
- A aula 1 foi integrada em `docs/aula1/`, com relatório, notas, gráficos e
  scripts originais. `scripts/log_joints.py` é a versão adaptada para este
  projeto: lê as juntas sem comandar movimento, grava CSV e pode criar PNG.
  O argumento `--seconds` recusa agora valores não positivos ou infinitos.
- `tests/test_config.py` e `tests/test_safety.py` cobrem a configuração e o
  comportamento de segurança sem precisar de ligar ao robô.
- `docs/relatorio_LW0_parte2.md` já contém os nomes Bernardo Pereira
  (2022219048) e João Lavos (número por confirmar). Distingue a instalação
  inicial com Python 3.14.7 da revisão feita com Python 3.12.10 e regista os
  resultados de testes apresentados nesta revisão.

Os módulos `lite6/kinematics.py`, `ik.py`, `velocity.py`, `trajectory.py` e
`game.py` continuam como estruturas para trabalhos futuros.

## O que foi testado nesta revisão

| Verificação | Resultado observado |
|---|---|
| Ambiente Python | Ambiente virtual existente com Python 3.12.10; dependências e pacote `lite6` instalados. Não foi recriado do zero nesta revisão. |
| Suite completa de `pytest`, na última execução apresentada | 17 testes passaram e 1 falhou: `test_domain_id_is_group_number`, porque o número do grupo ainda não foi atribuído. |
| `tests/test_safety.py`, executado em separado | 21 testes passaram. |
| Simulador de firmware UFACTORY | Contentor iniciado; Studio abriu; `b5_connect.py` ligou-se e `--move` moveu o braço e regressou a home. |
| Comparação de cinemática direta, Teste 8 | Diferença de 0,20 mm na pose A e cerca de 0,30 mm na pose B, usando os valores `tf2` registados pelo colega. |
| Oito testes de ciclo de vida no simulador | 8/8 passaram; registo mais recente em `logs/lifecycle_sim_20261011_101616.csv`. |
| Aquisição de juntas durante 30 s | `scripts/log_joints.py` criou CSV e PNG em `logs/`. O ensaio foi no simulador. |
| Valor inválido para `--seconds` | `inf` foi recusado antes da ligação. |

Os Testes 1–7 de ROS/Gazebo no relatório são resultados registados pelo
colega; não foram repetidos nesta revisão. Não houve testes no robô físico.

## Perguntas para o professor antes de usar o robô real

1. Qual é o número atribuído ao grupo? Deve ser usado tanto em
   `config/robot.yaml` (`ros.domain_id`) como em `ROS_DOMAIN_ID` na VM.
2. O IP `192.168.1.176`, a pose `home` e o offset TCP da garra registados na
   aula 1 são os corretos para a próxima sessão na bancada?
3. Quais são os seis limites numéricos da fronteira TCP da bancada, em mm, e
   qual é o referencial em que devem ser definidos? O programa espera a ordem
   `[x_max, x_min, y_max, y_min, z_max, z_min]`.
4. Confirmam-se os limites do modo reduzido observados na aula 1 (54°/s nas
   juntas e 150 mm/s no TCP) e o teto de 30°/s escolhido para os movimentos
   deste programa? Há outros limites que devemos aplicar?
5. Podemos usar no robô real as poses e os critérios definidos no YAML para
   os testes de `home`, paragem e desempenho? Em particular, confirmar as
   poses `start_joints` e `far_joints`, a tolerância de 0,5° e os tempos limite.
6. Quando e em que condições podemos executar os ensaios no robô físico,
   incluindo a paragem induzida? Até lá, os resultados são apenas do simulador.

## Pequenas pendências no relatório

- O número de estudante de João Lavos ainda está por preencher.
- A tabela de ciclo de vida no relatório ainda cita o CSV de 04/10; os valores
  mais recentes estão no CSV de 11/10 indicado acima.
- Na matriz de rastreabilidade do relatório, `_check_speed_cap` é um nome
  antigo; a validação atual está em `_validate_motion_settings`.

