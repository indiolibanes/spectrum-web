# Auditoria GUI / UX / UI — SpectrumLabPro 4.16.1

Branch: `feat/gui-ux-audit`
Base: `main` @ `cb72553`
Data: 19/10/2026

## 1. Escopo e método

- **Escopo:** todo o código de interface (PyQt5), fluxos de operação, mensagens ao operador, tema, acessibilidade, intertravamentos de segurança e pontos de contato com autenticação e persistência que afetam a experiência.
- **Método:** leitura estática do código, com verificação de referências por busca (`grep`) e checagem das chamadas críticas (emergência, comunicação, fechamento). **Não houve execução visual nem teste com hardware.** Os achados de aparência são inferências de código e precisam ser confirmados com capturas de tela.
- **Severidade:**
  - **Crítica:** pode levar a operação física insegura ou a informação falsa sobre estado do equipamento.
  - **Alta:** causa erro operacional provável, falha de segurança ou de integridade de dados.
  - **Média:** dificulta uso, manutenção ou acessibilidade.
  - **Baixa:** acabamento e consistência.

### Cobertura

| Área | Situação |
|---|---|
| `main.py` — diálogos, janela principal, status, emergência, comunicação, autenticação, fechamento | Lida em detalhe |
| `scada_ui.py`, `appearance.py`, `popup_design.py`, `responsive_layout.py`, `brand_assets.py` | Lidos integralmente |
| `manual_control_dialog.py`, `auth_dialogs.py`, `diagnostics.py`, `modern_splash.py` | Lidos (auth por padrões de busca) |
| `main.py` — ciclo automático, repetibilidade, calibração (trechos 3209–3523, 3600–4060) | **Parcial**: lidos por busca de mensagens e chamadas. Não linha a linha. |
| `main.py` — processamento e exportação (4205–4436, 4600–4715, 4727–4862) | **Parcial** |
| `animated_chart.py`, `database_manager.py` (corpo), `pdf_generator.py` | **Não lidos em detalhe** |
| `chemometrics.py`, `equipment_interlocks.py`, `connection_worker.py` | Lógica lida por trechos; não auditada a fundo |

A cobertura parcial está indicada para não passar a impressão de revisão completa. Os itens da seção 8 fecham essa lacuna.

---

## 2. Resumo executivo

O projeto tem uma base de segurança bem pensada: confirmação do operador antes de fechar a gaveta, desacoplamento atômico dos comandos manuais, diálogos modais com botão de emergência e cancelamento que preserva a calibração anterior. Esses pontos são bons e devem ser mantidos.

O risco principal está na **parada de emergência**: a interface informa que a bancada está em repouso sem garantir que o comando chegou ao ESP32. Também há **feedback crítico escondido** (o console está oculto por padrão), **Kappa apresentado como medição** em destaque e **três classificações de Kappa que não concordam entre si**.

Em termos de manutenção, a interface é construída duas vezes (a versão antiga é descartada depois), há mais de 430 cores fixas em `main.py` e o tema depende de substituições por expressão regular. Isso torna qualquer mudança visual arriscada sem testes de tela.

**Contagem por severidade:** 6 críticos · 10 altos · 12 médios · 8 baixos.

---

## 3. Achados críticos

### C1. Parada de emergência sem confirmação de envio
- **Onde:** `main.py:4112` (`stop_cycle_action`), `connection_worker.py:262` (`send_emergency`), `connection_worker.py:244` (`enviar`).
- **Problema:** `enviar()` retorna `False` quando não há conexão, mas `send_emergency()` descarta esse retorno. Em seguida, `stop_cycle_action` trava a UI e escreve **"EMERGÊNCIA ACIONADA - BANCADA EM REPOUSO"**, sem saber se o comando saiu. Sem conexão (ou com o enlace caído), o operador vê uma confirmação que não existe.
- **Agravante:** o texto "em repouso" aparece antes da confirmação do hardware. Após 1,5 s, se o ESP32 não tiver confirmado, a mensagem muda para "Aguardando confirmação", mas o texto anterior já foi lido.
- **Recomendação:** propagar o resultado de `send_emergency`. Se não for enviado, mostrar alerta vermelho persistente: "PARADA NÃO ENVIADA — use o botão físico / verifique a conexão". Só exibir "em repouso" após `STATUS:EMERGENCIA_ACIONADA`.

### C2. Estado físico desconhecido após emergência não é sinalizado
- **Onde:** `main.py:4175` (`_handle_emergency_confirmed`), `_on_emergency_lock_timeout`.
- **Problema:** após a confirmação, a UI volta a `IDLE` e reabilita os controles. A posição da gaveta e do sensor, que pode ter ficado no meio do curso, não é marcada como incerta. Os indicadores "Carcaça / Porta / Carrinho" mantêm o último valor conhecido.
- **Recomendação:** marcar as posições como "desconhecidas" após emergência, bloquear movimentos até uma consulta de estado (`CMD:ESTADO_PORTA` ou equivalente) e mostrar essa pendência de forma visível.

### C3. Fechar o aplicativo durante operação não é bloqueado nem avisa
- **Onde:** `main.py:4715` (`closeEvent`).
- **Problema:** `closeEvent` para timers, desconecta e aceita o fechamento. Se a gaveta ou o sensor estiverem em movimento, o aplicativo fecha no meio do movimento e a bancada fica sem controle.
- **Recomendação:** se `fsm_state != IDLE` ou houver movimento pendente, exigir confirmação explícita com aviso de risco. Antes de fechar, enviar parada segura.

### C4. Exceção não tratada mantém a aplicação rodando com máquina de estados inconsistente
- **Onde:** `main.py:4887` (`global_exception_handler`).
- **Problema:** o handler grava em `crash.log`, mostra um diálogo e **continua em execução**. Se a exceção ocorrer no meio de uma sequência de hardware, o FSM pode ficar em um estado que não corresponde à bancada, sem parada.
- **Recomendação:** em exceção durante operação ativa, acionar parada segura automaticamente e mudar o estado para `FALHA`, bloqueando novas ações até reconexão e verificação.

### C5. Feedback crítico escondido no console oculto
- **Onde:** `scada_ui.py:99` (`w.txt_console.hide()`), `main.py:2722` (recusa de mudança de método, só em log), `main.py:2906` (`_execute_atomic_manual_button`, retornos silenciosos quando há rotina em andamento).
- **Problema:** o console de telemetria, que é o único lugar onde várias mensagens aparecem, começa **oculto**. Recusas e bloqueios são registrados apenas ali. Exemplo: o operador troca o método de análise durante um ciclo, o combo volta sozinho e nada é explicado. Clicar em "Abrir gaveta" com outro comando pendente não faz nada visível.
- **Recomendação:** toda recusa ou bloqueio deve gerar feedback na barra de status ou em toast visível, com o motivo em linguagem simples.

### C6. Ação motorizada ativada pela tecla Enter
- **Onde:** `main.py:1525` (`DialogDecisaoConclusao`, `btn_finish.setDefault(True)` + `setFocus()`).
- **Problema:** o diálogo diz que a gaveta está aberta para manipulação da lâmina, e o botão em foco é **"Finalizar e Fechar Gaveta"**. Um Enter involuntário fecha a gaveta com a mão na amostra.
- **Recomendação:** o foco padrão deve ser "Nova Análise" (que não move nada) ou o fechamento deve exigir confirmação adicional. Nenhuma ação que movimenta hardware deve ser padrão de teclado.

---

## 4. Achados altos

### A1. Kappa apresentado como medição, sem o aviso demonstrativo onde ele importa
- **Onde:** `main.py:2555` ("NÚMERO KAPPA ESTIMADO (NIR)", 30px), `main.py:2559`, `main.py:4261` (aviso "Kappa demonstrativo, sem validação analítica" só no rótulo de 10px).
- **Problema:** o README declara que o Kappa é "estimativa demonstrativa por equações fixas, sem treinamento ou validação". A tela principal destaca o número em 30px com a palavra "NIR", e o aviso aparece só numa linha pequena que, na inicialização, nem está preenchida (o texto inicial é "Método: Amostra Seca", sem aviso). O texto `Método: Amostra Seca (Reflectância Difusa)` também é fixo e pode não bater com o método ativo na inicialização.
- **Recomendação:** rotular o valor como "Kappa demonstrativo (não validado)" e mostrar o aviso junto ao número, não em rodapé. Garantir que o rótulo de método leia do estado real. Isso também alinha a UI com o texto do TCC.

### A2. Três classificações de Kappa que não concordam
- **Onde:** `main.py:4863` (`_classify_kappa`: limites 2 / 6 / 12 / 22 / 55); `main.py:520–526` (histórico: limites 1,5 / 12 / 25 / 35 e rótulos "Alta Alvura", "Padrão", "Semi", "Kraft"); `main.py:467` (tabela de histórico: limite 15).
- **Problema:** o mesmo valor de Kappa pode aparecer com uma classificação na tela principal e outra cor e texto no histórico. Os rótulos "Alta Alvura", "Padrão" e "Semi" **nunca são produzidos** por `_classify_kappa`, então o ramo de cor do histórico cai nos limiares numéricos, que são diferentes.
- **Recomendação:** uma única função de classificação, usada em todos os lugares, com limites definidos em um só módulo.

### A3. Credencial padrão `admin/admin` e armazenamento fraco de senha
- **Onde:** `auth_manager.py:35–62` e `database.py:115` (criação de `admin/admin`); `auth_manager.py:35` (SHA-256 sem sal, segundo o próprio docstring em `database.py:31`).
- **Problema:** o usuário administrador padrão é criado automaticamente, sem exigir troca no primeiro acesso. A senha é gravada com SHA-256 sem sal. O repositório é **público**, então a senha padrão é conhecida.
- **Recomendação:** forçar troca da senha padrão no primeiro login; usar `bcrypt`, `scrypt` ou `argon2`; remover o padrão de versões distribuídas.

### A4. Política de senha ausente e `strip()` altera a senha
- **Onde:** `auth_dialogs.py:130` (login) e `auth_dialogs.py:319` (cadastro): `password = self.txt_new_password.text().strip()`.
- **Problema:** não há tamanho mínimo, não há campo de confirmação e o `strip()` remove espaços do início e do fim da senha **sem avisar**. O usuário que criou a senha com espaço não consegue entrar depois se o login não remover os mesmos espaços. (No código atual o login também faz `strip()`, então o efeito é consistente, mas a senha efetiva é diferente da digitada.)
- **Recomendação:** mínimo de caracteres com feedback, confirmação de senha, nenhum `strip()` em senha, e botão para mostrar/ocultar.

### A5. Sessão manual sem tempo limite e com regras diferentes por caminho de acesso
- **Onde:** `main.py:4436` (`_on_control_tab_changed`, rebloqueia ao sair da aba) e `main.py:4558` (`open_manual_control_dialog`, pelo botão da barra superior, **não** rebloqueia).
- **Problema:** pelo botão "Modo manual", a autenticação fica liberada até logout, sem tempo limite. Pela aba, sair da aba bloqueia de novo. Dois caminhos, duas regras, e nenhuma delas expira por inatividade em uma bancada de atuadores.
- **Recomendação:** uma única regra de sessão, com bloqueio por inatividade e rebloqueio ao fechar o painel.

### A6. Código de teste dentro do caminho de produção
- **Onde:** `main.py` — ramos `QT_QPA_PLATFORM == "offscreen"` em `_on_control_tab_changed`, `open_manual_control_dialog`, `_handle_interlock_popup` (`_auto_confirm_dialog`), `_check_calibration_validity`, `_calib_transition_choice`, `_calib_confirm_empty`.
- **Problema:** variáveis como `_auto_login_success` e `_auto_confirm_dialog` alteram fluxos de **autenticação e de intertravamento humano** quando a variável de ambiente está definida. Hoje o padrão é seguro, mas o mecanismo é uma porta de entrada desnecessária.
- **Recomendação:** mover a infraestrutura de teste para um módulo separado, fora do fluxo de produção, ou injetar as respostas de diálogo por interface de teste.

### A7. Persistência acoplada à exibição do relatório
- **Onde:** `main.py:3571–3573` (`_display_repeatability_report` chama `process_raw_spectral_data(scan, persist=True)` para cada leitura).
- **Problema:** mostrar um relatório grava registros no histórico. Se o relatório for reaberto ou o fluxo for repetido, pode haver duplicação. O efeito colateral não aparece no nome da função.
- **Recomendação:** separar cálculo, persistência e apresentação. A gravação deve ocorrer uma única vez, na conclusão do ensaio.

### A8. Histórico de leituras e usuários no mesmo arquivo SQLite
- **Onde:** `main.py:1894` (`self.auth_manager = DatabaseManager(self.auth_db_path)`), `main.py:4304–4305` (gravação de leituras pelo `auth_manager`), arquivo `usuarios.db`.
- **Problema:** o nome `auth_manager` esconde que ele também guarda o histórico metrológico. Restaurar ou apagar a base de usuários apaga os ensaios, e vice-versa. Também é o arquivo versionado no repositório público.
- **Recomendação:** separar em dois bancos com nomes claros.

### A9. Protocolo cru exposto ao operador
- **Onde:** `main.py:2922` ("Aguardando STATUS:GAVETA_ABERTA"), `manual_control_dialog.py` (botões "Abrir Gaveta (CMD:ABRIR_GAVETA)"), `manual_control_dialog.py:` log "[RX STATUS]".
- **Problema:** o operador lê nomes de comandos de firmware. Isso aumenta a carga cognitiva e torna a tela pouco legível para quem não programa.
- **Recomendação:** rótulos em linguagem de operação ("Abrir gaveta"), com o código do comando somente no log técnico.

### A10. Emoji tratado por substituição em tempo de execução
- **Onde:** `appearance.py` (`apply_widget`: regex remove emoji de `QLabel`/`QPushButton` fora de popups; esconde `QLabel` que ficar vazio). Textos definidos no código com emoji (ex.: `main.py:2922`, `main.py:3029`, `main.py:3112`) só são limpos quando o widget recebe novo estilo.
- **Problema:** a aparência depende de **quando** o widget foi repintado. O mesmo texto pode aparecer com ou sem ícone. O ícone de `PowerBiKpiCard` (ex.: "⚡") é apagado na janela principal, mas aparece nos diálogos. Como efeito colateral, o `QLabel` com só ícone fica oculto.
- **Recomendação:** remover emoji do texto de estado e usar ícones gráficos (SVG) ou nenhum ícone. Remover a substituição automática.

---

## 5. Achados médios

| ID | Achado | Onde |
|---|---|---|
| M1 | **Interface construída duas vezes.** `build_dashboard` cria os `_create_*` (topbar, KPIs, painel esquerdo, gráfico, rodapé) e depois reparenta parte deles e apaga o resto (`deleteLater`). Cerca de 800 linhas são construídas e descartadas. | `scada_ui.py:17–135`, `main.py:2149–2640` |
| M2 | **`switch_mode` duplicado** na mesma classe. A primeira versão referencia `btn_mode_auto` e `btn_mode_manual`, que não existem. A segunda sobrescreve a primeira, então é código morto que aguarda um erro. | `main.py:2672`, `main.py:4474` |
| M3 | **434 cores fixas em `main.py`**, além de cores em `manual_control_dialog.py` (41), `auth_dialogs.py` (49), `database_manager.py` (37), `animated_chart.py` (41). Pelo menos cinco paletas QSS distintas convivem. | vários |
| M4 | **`line-height` em QSS** (8 ocorrências em `main.py`). Qt não suporta essa propriedade em folhas de estilo e a ignora sem aviso. | `main.py` |
| M5 | **Fontes de 9 px** em 14 pontos de `main.py`. Em telas de notebook com escala 125–150%, o texto fica pequeno demais para leitura de bancada. | `main.py` |
| M6 | **Contraste baixo** em textos auxiliares (`#6B7280`, `#71717A` sobre fundos `#18181B`–`#202020`), inferior a 4,5:1 para texto pequeno. Confirmar com medição. | `main.py` (histórico, cards) |
| M7 | **Cor como único canal** em LEDs do painel manual (verde/âmbar sem legenda) e em badges de calibração (verde/vermelho com texto curto). | `manual_control_dialog.py`, `main.py:814–840` (`CardKpiCalibracao`) |
| M8 | **Ícones e rótulos sem nome acessível.** Apenas 2 `setAccessibleName`, 7 `setToolTip`, 0 atalhos de teclado em toda a aplicação. Não há atalho para emergência. | global |
| M9 | **Diálogos de segurança duplicados.** `DialogAlertaRadiacao` e `DialogAlertaGaveta` têm quase o mesmo código (estilo, barra, botão de emergência). Diálogos de intertravamento repetem ~60 linhas de QSS. | `main.py:1562`, `main.py:1687` |
| M10 | **Texto de risco impreciso.** "Radiação invisível de alta densidade" é alarmista e não é uma especificação. Revisar com a ficha técnica do emissor (50 mA, configuração informada no README). | `main.py:1629` |
| M11 | **Splash com atraso fixo de 4,5 s** em todo início, mesmo com o sistema pronto. | `modern_splash.py` (`minimum_duration_ms=4500`) |
| M12 | **Campos Wi-Fi sem validação** de IP e faixa de porta (0–65535) e sem estado "conectando" no botão. Duplo clique pode disparar conexões. | `main.py:2745–2768` |

---

## 6. Achados baixos

| ID | Achado | Onde |
|---|---|---|
| B1 | "Total: 1 ensaios registrados" — concordância no singular. | `main.py:472` |
| B2 | Botão desabilitado com texto de ação. "Escuro medido automaticamente" é definido após o botão já estar desabilitado, e o caminho "Zero Físico" é código morto. | `main.py:1099–1101` |
| B3 | CSV com separador `;` (padrão pt-BR) e decimais com ponto. O Excel em pt-BR pode importar os valores como texto. | `main.py:675` (`_on_exportar_csv`) |
| B4 | Rótulo "Velocidade USB" mostra 115.200 baud também em Bluetooth. | `diagnostics.py` (`refresh`) |
| B5 | Docstring de `CardKpiCalibracao` descreve R² e RMSE, mas os rótulos mostram "CV branco máximo" e "Ruído escuro máximo". | `main.py:814–840` |
| B6 | Comentário diz que o console é "retrátil", mas tem altura fixa (`setFixedHeight(75)`). | `main.py:2664` |
| B7 | `stop_cycle_action` tem a docstring depois de uma chamada, então ela não é docstring. | `main.py:4112–4113` |
| B8 | Logotipo "SENAI" e "ARAUCO" com fundo branco fixo, que aparece como caixa clara no tema escuro. Uso de logos de terceiros precisa de confirmação de autorização e atribuição para o TCC. | `brand_assets.py`, `modern_splash.py` ("Projeto ARAUCO") |

---

## 7. Pontos positivos (manter)

- **Intertravamento humano:** a gaveta só fecha depois de `OK` do operador. O cancelamento não envia `CMD:FECHAR_GAVETA` (`main.py:3166`).
- **Desacoplamento atômico:** cada botão manual fica desabilitado até o `STATUS` correspondente, com watchdog de 30 s.
- **Cancelamento preserva a referência anterior:** calibração incompleta é descartada, e a anterior é mantida (`main.py:4010`).
- **Confirmação antes de excluir** registros, com botão "Não" como padrão (`main.py:661`).
- **Irradiância marcada como "Não validada"** em vez de um valor inventado (`diagnostics.py`). Telemetria ausente aparece como "—" ou "Não enviados".
- **Diálogos de alerta não fecham com Esc** durante a operação (`popup_design.py`).
- **Redimensionamento proporcional** (`responsive_layout.py`) evita rolagem e mantém a disposição.
- **Rótulos de status com texto**, não só cor, na maior parte da tela.

---

## 8. Pendências de cobertura

Para fechar a auditoria completa, falta:

1. Ler integralmente `main.py` 3209–3523 (ciclo automático e repetibilidade) e 3600–4060 (relatório e calibração).
2. Ler `main.py` 4205–4436 (processamento e gráficos) e 4600–4715 (exportação PDF/CSV).
3. Ler `animated_chart.py` (gráfico e paleta de séries) e o corpo de `database_manager.py`.
4. Revisar `pdf_generator.py` como superfície de leitura do laudo (linguagem, unidades, avisos).
5. Validar visualmente os temas claro e escuro com capturas de tela (`QWidget.grab()` com `QT_QPA_PLATFORM=offscreen`).
6. Testar com hardware: parada de emergência com e sem conexão, queda de cabo durante movimento, fechamento durante operação.

---

## 9. Plano proposto

**Fase 0 — Segurança operacional (antes de qualquer mudança visual)**
- C1: confirmar envio da emergência; alerta persistente se não enviada; "em repouso" só após confirmação.
- C2: estado físico "desconhecido" após emergência, bloqueio até consulta de estado.
- C3: bloqueio ou confirmação ao fechar durante operação.
- C4: parada segura em exceção durante operação.
- C6: remover foco padrão de ação motorizada.

**Fase 1 — Verdade da informação**
- C5 e A9: feedback visível para recusas e bloqueios; rótulos de operação sem jargão de firmware.
- A1 e A2: aviso de Kappa demonstrativo junto ao valor; classificação única.
- A7 e A8: separar persistência da apresentação; separar bancos.

**Fase 2 — Manutenibilidade do tema**
- M1, M2, M3, M4, M9: uma só fonte de paleta, diálogos base comuns, remoção de código morto e de `line-height`.
- A10: remover substituição de emoji em tempo de execução.

**Fase 3 — Acessibilidade e legibilidade**
- M5 a M8: tamanhos mínimos de fonte, contraste medido, nomes acessíveis, atalhos (incluindo emergência), legenda para LEDs.

**Fase 4 — Segurança de acesso**
- A3, A4, A5, A6: troca de senha padrão, hash moderno, política de senha, sessão com inatividade, remoção de hooks de teste.

**Fase 5 — Decisão de plataforma**
- O port para Android não é uma adaptação. O código é PyQt5 com cerca de 5.000 linhas de interface acopladas a estado de hardware. Recomendo decidir a stack depois da Fase 0–2, porque a estrutura de estado (FSM) é reaproveitável e a camada de UI não.

---

## 10. Decisões pendentes para o time

1. A Fase 0 pode ser feita já, antes da reestruturação visual? (Recomendado.)
2. Os logos "ARAUCO" e "SENAI" podem ficar no executável do TCC? Precisa de autorização ou devem ser removidos?
3. Remover `usuarios.db`, `test_usuarios.db`, `crash.log` e arquivos `.spec` antigos do repositório público? Isso exige reescrever o histórico se houver senhas reais.
4. O texto do TCC deve ser alinhado ao aviso de Kappa demonstrativo do README?
