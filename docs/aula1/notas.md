**1. Ligação**

O computador foi ligado à rede Wi-Fi **wifi-robot-3** e configurado com o endereço IP estático **192.168.1.50** e a máscara de sub-rede **255.255.255.0**. O robô tinha o endereço IP **192.168.1.176**. A ligação foi verificada através do comando ping, tendo sido recebidas **quatro respostas em quatro pedidos, com 0% de perdas**. Após esta verificação, acedeu-se ao UFACTORY Studio através do endereço [**http://192.168.1.176:18333**](http://192.168.1.176:18333).

**2. Exploração no Live Control**

As seis juntas foram mexidas individualmente através do Live Control do UFACTORY Studio. Os extremos observados foram registados e comparados com as gamas indicadas no enunciado.

| **Junta** | **Gama observada** | **Gama do enunciado** |
| --------- | ------------------ | --------------------- |
| J1        | −360° a +360°      | −360° a +360°         |
| J2        | −139,9° a +148,8°  | −150° a +150°         |
| J3        | −1,8° a +299,9°    | −3,5° a +300°         |
| J4        | −360° a +360°      | −360° a +360°         |
| J5        | −121,6° a +122,4°  | −124° a +124°         |
| J6        | −359,9° a +360°    | −360° a +360°         |

Todos os valores observados ficaram dentro das gamas especificadas. Em J1 e J4, os extremos registados coincidiram com os do enunciado. Nas restantes juntas, a exploração não atingiu exatamente todos os limites especificados; estes resultados representam os extremos observados durante o ensaio.

**Movimentação cartesiana**

Foram aplicados sucessivamente os comandos X+, Y+ e Z+ no Live Control do UFACTORY Studio. Cada comando produziu um aumento de **1,0 mm na respetiva coordenada do TCP**. A orientação manteve-se constante à precisão apresentada no Studio. A tabela seguinte regista a posição, a orientação e os ângulos das juntas em cada etapa.

**Tabela 1 — Leituras durante os comandos de translação**

| **Leitura** | **X (mm)** | **Y (mm)** | **Z (mm)** | **Roll (°)** | **Pitch (°)** | **Yaw (°)** | **J1 (°)** | **J2 (°)** | **J3 (°)** | **J4 (°)** | **J5 (°)** | **J6 (°)** |
| ----------- | ---------- | ---------- | ---------- | ------------ | ------------- | ----------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Inicial     | 15,9       | −62,6      | 676,9      | 84,7         | −27,5         | 99,6        | −300,0     | −0,9       | 176,9      | −52,9      | 84,3       | 300,0      |
| Após X+     | 16,9       | −62,6      | 676,9      | 84,7         | −27,5         | 99,6        | −300,0     | −0,9       | 176,9      | −52,9      | 84,3       | 300,0      |
| Após Y+     | 16,9       | −61,6      | 676,9      | 84,7         | −27,5         | 99,6        | −299,7     | −0,5       | 177,3      | −53,2      | 84,3       | 300,0      |
| Após Z+     | 16,9       | −61,6      | 677,9      | 84,7         | −27,5         | 99,6        | −299,7     | −1,4       | 175,6      | −53,2      | 83,8       | 300,6      |

De seguida, foram aplicados sucessivamente os comandos RX+, RY+ e RZ+, partindo da configuração obtida após Z+. Observaram-se alterações na orientação do TCP e nos ângulos de várias juntas, conforme a Tabela 2.

**Tabela 2 — Leituras durante os comandos de rotação**

| **Leitura**       | **Roll (°)** | **Pitch (°)** | **Yaw (°)** | **J1 (°)** | **J2 (°)** | **J3 (°)** | **J4 (°)** | **J5 (°)** | **J6 (°)** |
| ----------------- | ------------ | ------------- | ----------- | ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| Inicial — após Z+ | 84,7         | −27,5         | 99,6        | −299,7     | −1,4       | 175,6      | −53,2      | 83,8       | 300,6      |
| Após RX+          | 84,5         | −28,5         | 99,7        | −299,8     | −1,3       | 175,9      | −53,3      | 83,8       | 301,5      |
| Após RY+          | 85,6         | −28,7         | 99,2        | −299,8     | −2,4       | 173,8      | −53,3      | 84,2       | 302,4      |
| Após RZ+          | 85,6         | −28,7         | 100,2       | −299,3     | −2,6       | 173,5      | −52,8      | 84,2       | 302,4      |

Os resultados mostram que um comando cartesiano pode envolver alterações em várias juntas. Nos ensaios de rotação, também se verificou que um comando num eixo de rotação pode alterar mais do que um dos valores apresentados como roll, pitch e yaw. Todas as leituras foram registadas com uma casa decimal, conforme apresentado no Studio.







**Modo manual e deteção de colisão**

Após configurar a carga da garra, foi ativado o modo manual e o braço foi guiado à mão. **Ao ser largado, o braço manteve a posição**, sustentando-se contra a gravidade. No final, o Studio apresentava o estado Normal, uma carga de aproximadamente 0,28 kg e os seguintes ângulos:

| **J1 (°)** | **J2 (°)** | **J3 (°)** | **J4 (°)** | **J5 (°)** | **J6 (°)** |
| ---------- | ---------- | ---------- | ---------- | ---------- | ---------- |
| −299,3     | 43,3       | 173,4      | −119,5     | −81,0      | 325,9      |

Quando o braço bateu num obstáculo, o Studio apresentou uma mensagem e bloqueou o movimento. Foi necessário carregar em Reset para voltar a movimentá-lo. Não ficou registado o texto nem o código dessa mensagem.

A abertura e o fecho da garra foram testados através dos botões Open e Close do UFACTORY Studio, tendo sido observada a execução de ambas as operações.





**Configuração da garra**

Foi utilizada a predefinição **Gripper** do UFACTORY Studio, com os seguintes parâmetros:

| **Parâmetro**                | **Valor configurado** |
| ---------------------------- | --------------------- |
| Massa                        | 0,277 kg              |
| Centro de massa [Cx, Cy, Cz] | [0; 0; 30] mm         |
| Offset do   TCP [X, Y, Z]    | [0; 0; 83,6] mm       |
| Rotação do offset            | [0°; 0°; 0°]          |

Estes valores correspondem à configuração utilizada, não a medições realizadas pelo grupo. A abertura da garra nos estados aberto e fechado e a distância entre a face da flange e a ponta dos dedos não foram medidas, devido à ausência de um instrumento de medição.

**3. Exercícios em Python**

**3.1. Leitura dos ângulos das juntas e da pose do TCP**

Utilizaram-se as funções get_servo_angle() e get_position() para ler os ângulos das juntas e a pose do TCP antes e depois de movimentar o braço em modo manual. Ambas as leituras devolveram código 0.

| **Grandeza** | **Antes** | **Depois** | **Unidade** |
| ------------ | --------- | ---------- | ----------- |
| J1           | −299,3    | −299,3     | °           |
| J2           | 43,3      | 3,9        | °           |
| J3           | 173,4     | 173,5      | °           |
| J4           | −119,5    | −90,5      | °           |
| J5           | −81,0     | −70,6      | °           |
| J6           | 325,9     | 322,4      | °           |
| X            | 41,1      | −136,2     | mm          |
| Y            | 337,3     | 47,9       | mm          |
| Z            | 562,1     | 727,0      | mm          |
| Roll         | 148,6     | −53,1      | °           |
| Pitch        | 71,7      | 57,9       | °           |
| Yaw          | −88,2     | 89,7       | °           |

A movimentação manual alterou a configuração das juntas e, consequentemente, a posição e a orientação do TCP. J1 manteve o valor apresentado, enquanto as restantes juntas variaram. Os valores da tabela estão arredondados a uma casa decimal.

**3.2. Leitura das gamas das juntas**

Utilizou-se a função get_reduced_states() para consultar os limites angulares configurados no controlador. A chamada devolveu código 0.

| **Junta** | **Limite inferior** | **Limite superior** | **Comparação com o §1.2** |
| --------- | ------------------- | ------------------- | ------------------------- |
| J1        | −360°               | +360°               | Coincide                  |
| J2        | −150°               | +150°               | Coincide                  |
| J3        | −3,5°               | +300°               | Coincide                  |
| J4        | −360°               | +360°               | Coincide                  |
| J5        | −124°               | +124°               | Coincide                  |
| J6        | −360°               | +360°               | Coincide                  |

As gamas reportadas pelo controlador coincidiram com as especificadas no §1.2 do enunciado. Os extremos observados na exploração pelo Live Control ficaram dentro destes limites, embora alguns não tenham sido atingidos exatamente. A consulta dos limites configurados não confirma, por si só, que o modo reduzido esteja ativo.

**3.3. Regresso à configuração home**

Definiu-se a configuração **HOME = [−299,3; 3,9; 173,5; −90,5; −70,6; 322,4]°**. Utilizou-se set_servo_angle() com velocidade de **20°/s** e wait=True para regressar a esta configuração a partir de três posições iniciais distintas, obtidas alterando J2.

| **Ensaio** | **J2 inicial (°)** | **J2 final (°)** | **Código devolvido** |
| ---------- | ------------------ | ---------------- | -------------------- |
| 1          | 5,9                | 3,9              | 0                    |
| 2          | 1,9                | 3,9              | 0                    |
| 3          | 7,9                | 3,9              | 0                    |

Os três movimentos terminaram com código 0. As seis juntas regressaram aos mesmos valores finais à precisão de **0,1°** apresentada. A dispersão observada, calculada como a diferença entre o máximo e o mínimo das três leituras finais de cada junta, foi de **0,0° à resolução apresentada**.

**3.4. Deslocamento do TCP em +Z e regresso**

Utilizou-se set_position() para aumentar a coordenada Z do TCP em **50 mm** e regressar à posição inicial, com velocidade de **50 mm/s** e wait=True.

A primeira tentativa falhou, tendo o Studio apresentado o erro **C21 — “Kinematic Error — Please re-plan the path”**. Após reposicionar o braço, repetiu-se o ensaio com sucesso. A subida e o regresso devolveram código 0.

| **Leitura**     | **X (mm)** | **Y (mm)** | **Z (mm)** |
| --------------- | ---------- | ---------- | ---------- |
| Antes da subida | 61,939781  | 398,083405 | 408,828644 |
| Após a subida   | 61,939777  | 398,083405 | 458,828583 |
| Após o regresso | 61,939781  | 398,083405 | 408,828705 |

A diferença entre as leituras de Z antes e depois da subida foi de **49,999939 mm**. Após o regresso, a leitura de Z diferiu da inicial em **0,000061 mm**. Estas diferenças resultam das leituras numéricas do controlador e não constituem uma medição externa da precisão física do robô.

Enquanto o exercício anterior comandou diretamente os ângulos das juntas, este exercício comandou a posição cartesiana do TCP, cabendo ao controlador determinar os movimentos das juntas necessários.

**3.5. Controlo da garra**

A garra foi comandada através das funções open_lite6_gripper(), close_lite6_gripper() e stop_lite6_gripper(), com uma pausa de dois segundos entre as operações.

| **Operação** | **Função utilizada**  | **Código devolvido** |
| ------------ | --------------------- | -------------------- |
| Abrir        | open_lite6_gripper()  | 0                    |
| Fechar       | close_lite6_gripper() | 0                    |
| Parar        | stop_lite6_gripper()  | 0                    |

Todas as chamadas devolveram código 0 e o programa terminou com código de saída 0. A abertura e o fecho foram observados, mas as dimensões da garra não foram medidas devido à ausência de um instrumento de medição.

**5. Registo dos ângulos das juntas**

Foi desenvolvido o programa log_joints.py para registar os ângulos das seis juntas durante 30 segundos. As leituras foram realizadas através de get_servo_angle(), guardando apenas as respostas com código de retorno igual a zero. Os instantes de aquisição foram obtidos com time.perf_counter(). Não foram introduzidas pausas no ciclo, procurando atingir a maior frequência de leitura sustentada pela comunicação.

Na primeira aquisição, com o robô parado, foram registadas **1396 amostras**, com uma **frequência média de 46,5 Hz**. A frequência foi calculada pela divisão do número de intervalos entre amostras pelo tempo decorrido entre a primeira e a última leitura. Os ângulos das seis juntas mantiveram-se visualmente constantes durante o registo.

*[Inserir Figure_1.png — Figura: Evolução dos ângulos das seis juntas durante 30 segundos com o robô parado.]*

Na segunda aquisição, durante a movimentação manual, observaram-se variações mais acentuadas nas juntas J4 e J6. A junta J2 apresentou também alterações, enquanto J5 variou de forma menos pronunciada. J1 e J3 mantiveram-se aproximadamente constantes. Na parte final da aquisição, as curvas estabilizaram, correspondendo à manutenção da posição atingida.

*[Inserir Figure_2.png — Figura: Evolução dos ângulos das seis juntas durante 30 segundos com movimentação manual.]*

O número de amostras e a frequência média da segunda aquisição não ficaram registados nas evidências disponíveis. Assim, os valores de 1396 amostras e 46,5 Hz referem-se exclusivamente à primeira aquisição.

**6. Função de preparação da sessão**

Foi implementada a função safe_session(boundary) para preparar uma sessão de comunicação com o robô no endereço 192.168.1.176, utilizando graus como unidade angular. A função recebe os limites espaciais do TCP pela ordem [x_max, x_min, y_max, y_min, z_max, z_min] e verifica se foram fornecidos seis elementos.

O código inclui a limpeza de avisos e erros, a definição dos limites do modo reduzido para **54°/s nas juntas** e **150 mm/s no TCP**, a configuração da fronteira recebida e a ativação do modo reduzido e da delimitação espacial. Inclui também a ativação do movimento e a definição do modo e do estado como zero. O código de retorno de cada operação é verificado, sendo lançada uma exceção se for diferente de zero. No final, a função devolve o objeto XArmAPI.

A sintaxe do ficheiro foi verificada através do comando python -m py_compile safe_session.py, sem erros apresentados. **A função não foi executada no robô**, pelo que não foi verificada a aplicação das configurações ao controlador. Também não foram definidos nem validados experimentalmente os seis limites espaciais da bancada.