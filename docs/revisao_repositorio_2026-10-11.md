# Revisão do repositório e integração da aula 1

Revisão da `main` publicada em `jplavos7/robotica-grupoNN`, commit
`4f7277809efe70dfceb8db7b78553be42ae48f05`, confirmada com o GitHub em
11/10/2026. As observações abaixo distinguem resultados já registados pelo
colega de testes executados nesta cópia de trabalho.

## Revisão ficheiro a ficheiro

| Ficheiro publicado | O que contém | Verificação e observação |
|---|---|---|
| `.gitignore` | Exclui caches e alguns registos. | Foi acrescentada a exclusão dos novos CSV e PNG de aquisição. |
| `README.md` | Instalação no Windows/Linux, simulador e três comandos de execução. | A receita pressupõe o pacote instalado com `pip install -e .`; foi acrescentada a aula 1 e o comando de aquisição. A instalação de raiz não foi repetida nesta revisão. |
| `requirements.txt` | Versões fixas do SDK, NumPy, SciPy, PyYAML, pytest e matplotlib. | O ambiente virtual existente tem Python 3.12.10 e conseguiu executar os testes. Não foi criada uma instalação limpa. |
| `pyproject.toml` | Declara o pacote `lite6`, dependências principais e configuração do pytest. | Estrutura coerente com o README. |
| `config/robot.yaml` | Alvos `sim`/`lab`, home, velocidades, ROS e testes. | `ros.domain_id=0` continua provisório porque o número do grupo não foi atribuído. Foram acrescentados o IP, home e offset da garra observados na aula 1, separados do simulador. A fronteira TCP continua sem valores. |
| `lite6/__init__.py` | Marca o pacote. | Apenas documentação. |
| `lite6/config.py` | Carrega o YAML e escolhe o alvo. | Passa a aplicar home e offset específicos do alvo real; verificado nos testes locais. |
| `lite6/session.py` | Sessão, registo, paragem por exceção e movimento para home. | A versão publicada não configurava modo reduzido nem fronteira no código. A integração da aula 1 aplica-os ao alvo real antes de ativar movimento e recusa ligação sem fronteira. Também passa a verificar os códigos de `go_home`. Não foi executada no robô real. |
| `lite6/kinematics.py` | Interface anunciada para LW1. | Só tem uma docstring; cinemática direta por implementar. |
| `lite6/ik.py` | Interface anunciada para LW2. | Só tem uma docstring. |
| `lite6/velocity.py` | Interface anunciada para LW3. | Só tem uma docstring. |
| `lite6/trajectory.py` | Interface anunciada para LW4. | Só tem uma docstring. |
| `lite6/game.py` | Interface anunciada para o Desafio Final. | Só tem uma docstring. |
| `scripts/b5_connect.py` | Lê juntas e pose; com `--move`, move no simulador e regressa a home. | Foram acrescentadas verificações dos códigos das leituras. O movimento não foi repetido nesta revisão. |
| `scripts/test8_fk_compare.py` | Obtém FK do SDK, constrói matriz 4×4 e compara translações com `tf2`. | Foi acrescentada verificação do código do SDK. A comparação numérica cobre a posição, não a diferença angular; requer simulador ativo para repetir. |
| `scripts/lifecycle_tests.py` | Oito ensaios de sessão, home, tempos e falhas induzidas; escreve CSV. | O script existe e os CSV publicados mostram a repetição de 3/8 para 8/8; esses ensaios históricos não foram repetidos agora. Inclui comandos de movimento, pelo que depende do simulador ou do robô. |
| `tests/test_config.py` | Cinco testes sem robô. | Resultado atual: 4 passam; falha o teste que exige o número do grupo (valor atual 0). |
| `docs/relatorio_LW0_parte2.md` | Rascunho de ambiente, Testes 1–8, exercício de ciclo de vida e rastreabilidade. | Os valores remetem para evidências e registos do colega. Ainda tem nomes/número do grupo provisórios e relata `ROS_DOMAIN_ID=99` na VM, diferente do `0` do YAML. Os resultados da VM não foram repetidos nesta máquina. |
| `docs/modelo_V.svg` | Esquema do modelo em V. | O relatório aponta para o ficheiro; o SVG contém níveis LW1–LW4 e testes. |
| `docs/evidencias/frames_2026-10-04_17.58.04.gv` | Grafo `world → link_base → … → link_eef`. | Contém seis transformações de juntas a cerca de 19 Hz e duas estáticas. |
| `docs/evidencias/frames_2026-10-04_17.58.04.pdf` | Versão visual do grafo. | PDF de uma página; não é prova de movimento por si só. |
| `docs/evidencias/poseA_juntas.txt` | Ângulos da pose A. | Seis juntas a zero. |
| `docs/evidencias/poseA_tf2.txt` | Matriz e translação da pose A. | Translação impressa `0.087, 0.000, 0.154` m. |
| `docs/evidencias/poseB_juntas.txt` | Ângulos da pose B. | Seis valores em radianos, coerentes com os graus arredondados no YAML. |
| `docs/evidencias/poseB_tf2.txt` | Matriz e translação da pose B. | Translação impressa `0.087, 0.269, 0.154` m. |
| `logs/.gitkeep` | Mantém a pasta no Git. | Sem efeito funcional. |
| `logs/lifecycle_sim_20261004_002655.csv` | Primeira campanha de ciclo de vida. | 3/8; quatro casos mostram `motion_enable` com código 3 e um falha por `KeyError`. |
| `logs/lifecycle_sim_20261004_003138.csv` | Segunda campanha. | 8/8 registados no simulador; são resultados históricos, não uma execução desta revisão. |

## Material da aula 1 adicionado

`docs/aula1/` conserva o relatório de três páginas, fonte Word, notas, dois
gráficos e os dois scripts originais. Os gráficos foram abertos: o primeiro
mostra as juntas estáveis; o segundo mostra variações durante movimento manual.
O relatório distingue as leituras do controlador de medições físicas externas.

O script `scripts/log_joints.py` adapta a aquisição da aula: lê sem comandar
movimento, grava CSV, pode guardar PNG e fecha a ligação mesmo se houver erro.
`lite6/session.py` incorpora a configuração de 54°/s, 150 mm/s e fronteira TCP
para o alvo real. A fronteira não foi inventada: terá de ser definida com o
docente e verificada na bancada. A configuração observada no Studio não prova
que as chamadas Python tenham sido executadas com sucesso.

## Testes desta revisão

| Verificação | Resultado |
|---|---|
| Coincidência com a `main` no GitHub antes das alterações | SHA completo igual a `4f7277809efe70dfceb8db7b78553be42ae48f05` |
| `pytest` no ambiente virtual existente após a integração | 10 passam, 1 falha: número do grupo ainda desconhecido |
| Testes novos da fronteira e ordem da configuração | 6 passam; usam objeto simulado, sem comandar robô |
| Análise sintática dos módulos e scripts Python | 12 ficheiros analisados sem erro |
| Ajuda de `python -m scripts.log_joints --help` | Abre sem ligar ao robô |
| Simulador de firmware | Não testado agora: Docker Desktop não tinha o motor ativo |
| Robô físico, ROS/Gazebo e ensaios com movimento | Não testados nesta revisão |

## Pendências antes de declarar a entrega concluída

1. Receber o número do grupo e definir o mesmo `ROS_DOMAIN_ID` no YAML e na VM.
2. Definir os seis limites da fronteira TCP com o docente e confirmar IP, home e offset na bancada.
3. Repetir no simulador os scripts com movimento e o teste 8; registar novos resultados.
4. Atualizar o relatório da parte 2 com nomes e resultados próprios, mantendo a primeira campanha identificada como 3/8.
5. Executar a configuração de segurança no robô real apenas na sessão autorizada e registar códigos de retorno.
