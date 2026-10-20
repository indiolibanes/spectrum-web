<p align="center">
  <img src="assets/logo/spectrumlab-mark.svg" width="112" alt="Logo SPECTRUM-LAB PRO">
</p>

<h1 align="center">SPECTRUM-LAB PRO</h1>

<p align="center">
  <strong>Supervisório espectrométrico NIR para caracterização de celulose</strong><br>
  Versão 4.16.2 · Build 1263 · 20/10/2026
</p>

---

O SPECTRUM-LAB PRO controla uma bancada de medição NIR de baixo custo: aquisição de seis canais espectrais (610 a 860 nm, sensor GY-AS7263), referenciamento de branco e escuro, reflectância relativa, estimativa demonstrativa do número Kappa, ensaios de repetibilidade, histórico em banco SQLite e laudo em PDF.

> **Aviso de uso.** O número Kappa é uma **estimativa demonstrativa** por equações fixas, sem treinamento nem validação analítica. Não use os valores como medição certificada. A parada de emergência do programa e do firmware **não é um corte elétrico certificado**: mantenha o botão de emergência físico da bancada como proteção principal.

## Funcionalidades

- **Ensaios automáticos:** ciclo guiado com intertravamentos humanos (carregamento da amostra e confirmação do operador antes de fechar a gaveta).
- **Modo manual:** acionamento individual de gaveta, porta, carrinho e LED, protegido por autenticação.
- **Calibração:** referência de branco e escuro, com validade metrológica configurável e bloqueio de medições quando expirada.
- **Repetibilidade:** cinco aquisições consecutivas no mesmo posicionamento, com estatísticas e histórico individual.
- **Histórico:** ensaios salvos em `usuarios.db`, com consulta, exportação em CSV e laudo em PDF.
- **Gerenciamento de usuários:** perfis *administrador* e *operador*.
- **Dois temas, no estilo da ISA-101:** Noturno (quase preto com roxo e turquesa, padrão) e Claro (branco e verde, na linha da Arauco). Superfícies planas, sem vidro, brilho nem textura; a cor é informação (alarmes reservados), cada função de botão tem sempre a mesma cor e os gráficos usam uma cor por banda. Veja [docs/ISA-101.md](docs/ISA-101.md).
- **Indicador de análise:** abaixo do gráfico, um rosto colorido e mensagens em português acompanham cada etapa do ensaio.
- **Responsivo:** a janela se adapta a qualquer tela (cabeçalho em duas linhas, indicadores em grade, painéis empilhados) sem comprimir o texto.
- **Animações** inspiradas no movimento da Apple (molas, entrada escalonada, fusão na troca de tema), com opção de reduzi-las.
- **Configurações** em duas seções: *Aparência* (tema noturno ou claro) e *Acessibilidade* (teclado na tela em modo automático, sempre ou nunca; numérico no campo de IP e completo nos demais; e redução de animações). O teclado só abre em aparelhos de toque, é compacto e fica no canto superior esquerdo.

## Estrutura do repositório

| Arquivo | Função |
|---|---|
| `main.py` | Janela principal, máquina de estados e fluxos de ensaio |
| `scada_ui.py` · `appearance.py` · `popup_design.py` | Interface, temas e diálogos de alerta |
| `typography.py` · `button_fx.py` · `animation_math.py` | Escala tipográfica, efeitos de botão e funções de animação (molas, entradas) |
| `analysis_indicator.py` · `analysis_messages.py` | Indicador de análise (rosto, etapas, frases) |
| `touch_keyboard.py` · `keyboard_layouts.py` | Teclado na tela |
| `connection_worker.py` · `serial_worker.py` | Comunicação com o ESP32 (USB, Bluetooth SPP e Wi-Fi TCP) |
| `chemometrics.py` | Calibração, reflectância relativa, SNV e estimativa de Kappa |
| `equipment_interlocks.py` · `manual_control_dialog.py` | Intertravamentos e painel de atuadores |
| `database.py` · `auth_dialogs.py` · `password_hashing.py` | Usuários, senhas e histórico |
| `pdf_generator.py` · `database_manager.py` | Laudos e gerenciador de registros |
| `runtime_data.py` · `version.py` | Criação de dados locais e versionamento |
| `assets/logo/` | Marca do programa |
| `assets/brands/` | Logos SENAI e ARAUCO (SVG, fundo transparente) |
| `assets/fonts/` | Fontes Arena e Dropline (marca e títulos) e IBM Plex (licença OFL) |
| `assets/textures/` · `assets/cursors/` | Textura do fundo do tema claro (celulose) e cursores de fibra de celulose |
| `glass.py` · `cursors.py` | Receitas do vidro (cores e QSS) e instalação dos cursores |
| `tools/` | Geradores reproduzíveis das texturas, dos cursores e dos espécimes de tema |
| `tests/` | Testes das regras puras e teste gráfico de fumaça |
| `banco_materiais.json` | Base inicial de materiais (cópia editável criada na primeira execução) |
| `docs/IDENTIDADE_VISUAL.md` | Logos, temas, tipografia, animações e teclado |
| `docs/TUTORIAL_CODESPACE.md` | Roteiro de teste da interface no Codespace |
| `docs/AUDITORIA_GUI_UX.md` | Auditoria de interface, segurança e pendências |

## Como foi desenvolvido

Este projeto foi feito com assistentes de IA, e isso está declarado aqui de forma explícita:

- **Em parceria com o Antigravity**, como assistente de IA durante o desenvolvimento.
- **Desenvolvimento principal no Codex e no Claude Code**: código, refatorações, testes e documentação.
- **Testes**: a maior parte é feita no **GitHub Codespaces**, com um display virtual e uma bancada simulada (ESP32 falso). Também há testes com **amostras reais** na bancada.
- **Autoria**: a interface foi inspirada em projetos de terceiros (por exemplo, o BitChord, usado só como referência de linguagem visual, sem código copiado) e também em ideias autorais. Ela recebeu dezenas de implementações e melhorias após feedbacks de usuários reais.

Revisão técnica, decisões de segurança e a validade dos resultados são responsabilidade dos autores.

## Identidade visual

<p align="center">
  <img src="assets/logo/spectrumlab-mark.svg" height="64" alt="SPECTRUM-LAB PRO">
  &nbsp;&nbsp;&nbsp;
  <img src="assets/brands/senai.svg" height="40" alt="SENAI">
  &nbsp;&nbsp;&nbsp;
  <img src="assets/brands/arauco-sucuriu.svg" height="48" alt="ARAUCO | Projeto Sucuriú">
</p>

Os logos SENAI e ARAUCO são de terceiros e seu uso depende de autorização. O detalhe das regras está em [docs/IDENTIDADE_VISUAL.md](docs/IDENTIDADE_VISUAL.md).

**Cores.** Dois temas, em *Configurações → Aparência*: **Noturno · roxo e turquesa** (fundo `#0D0B14`, painéis `#181426`, roxo `#B79CFF` como destaque, turquesa `#4FD1C1` como cor secundária) e **Claro** (fundo `#F4F6F1`, cartões brancos, verde `#436722`). Os dois são lisos, sem textura. O verde deriva do logo Projeto Sucuriú; se houver o manual oficial da Arauco, ajuste em `appearance.py`. Paleta completa em [docs/IDENTIDADE_VISUAL.md](docs/IDENTIDADE_VISUAL.md).

**Tipografia.** Quatro famílias embutidas em `assets/fonts/`, iguais em Windows, Linux e no executável. As IBM Plex têm licença OFL. **Arena e Dropline foram enviadas sem licença legível: confirme os direitos de uso antes de distribuir** (detalhes em [docs/IDENTIDADE_VISUAL.md](docs/IDENTIDADE_VISUAL.md)):

| Família | Uso |
|---|---|
| Arena | Marca (nome ao lado do logo) |
| Dropline | Títulos e cabeçalhos |
| IBM Plex Sans | Interface, rótulos e texto corrido |
| IBM Plex Mono | Valores de medição e tabelas |

A escala vai de 12 px (mínimo) a 40 px (número Kappa), mais 44 px só na abertura. O cursor do mouse é uma seta de fibra de celulose (desligue com `SPECTRUM_SYSTEM_CURSOR=1`). A tabela completa está no documento de identidade visual.

**Assinatura.** Protótipo desenvolvido por [Davi Baracat](https://github.com/DaviBaracat), [Kauê Carvalho](https://github.com/indiolibanes) e [Mateus Ferreira](https://github.com/yosemate). No programa, o rodapé repete a assinatura com os mesmos links.

## Testes

```bash
python3 -I tests/test_typography.py
python3 -I tests/test_glass.py
python3 -I tests/test_analysis_messages.py
python3 -I tests/test_animation_math.py
python3 -I tests/test_keyboard_layouts.py
QT_QPA_PLATFORM=offscreen python3 -m unittest tests.test_gui_smoke -v   # precisa de PyQt5
```

O roteiro de teste visual no Codespace está em [docs/TUTORIAL_CODESPACE.md](docs/TUTORIAL_CODESPACE.md).

## Requisitos

- **Executável:** Windows 10 ou 11.
- **Código-fonte:** Python 3 com as dependências de `requirements.txt` (PyQt5 5.15.11, numpy, matplotlib, pyserial, reportlab e PyInstaller para gerar o executável).
- **Firmware:** ESP32 com o sketch correspondente à versão do supervisório. Para placas de 4 MB, use o esquema de partição *No OTA (2 MB APP / 2 MB SPIFFS)*. Verifique a compatibilidade na documentação da versão antes de gravar.

```bash
pip install -r requirements.txt
python main.py
```

## Primeiro acesso

Na primeira execução não há usuário cadastrado. O programa pede a criação do **administrador** (nome, senha com pelo menos 8 caracteres e confirmação). Não existe usuário ou senha padrão.

Para liberar o modo manual, o gerenciamento de usuários ou o histórico restrito, use o login. Operadores acessam o modo manual; apenas administradores gerenciam usuários.

## Dados locais

Os arquivos de dados são criados automaticamente na primeira execução, sem substituir os existentes:

| Execução | Pasta dos dados |
|---|---|
| Código-fonte | pasta do projeto |
| Executável | ao lado do `.exe` (banco de usuários e histórico) e `%LOCALAPPDATA%\SpectrumLabPro` (calibração, preferências e materiais) |
| Testes | pasta indicada em `SPECTRUM_LAB_DATA_DIR` |

Os arquivos `*.db`, `calibracao.json` e `crash.log` **não são versionados** (ver `.gitignore`). Eles contêm credenciais, calibrações da bancada e registros locais.

## Gerar o executável

```bat
python -m PyInstaller --noconfirm SpectrumLabPro_4_16_2.spec
```

O resultado fica em `dist/SpectrumLabPro_4_16_2.exe`. O `.spec` inclui `banco_materiais.json` e a pasta `assets/`.

Para gerar a documentação técnica em PDF, use `build_technical_doc_pdf.py`, a partir de `DOCUMENTACAO_TECNICA_SUPERVISORIO.md`.

## Segurança

Alterações desta versão:

- **Senhas** armazenadas com PBKDF2-HMAC-SHA256 (600 000 iterações e sal aleatório). Hashes antigos (SHA-256 sem sal) continuam válidos e são migrados no próximo login correto.
- **Sem credencial padrão:** o `admin/admin` foi removido. O primeiro administrador é criado no primeiro acesso.
- **Política de senha:** mínimo de 8 caracteres e confirmação na criação do administrador. A senha é usada exatamente como digitada, sem remover espaços.
- **Código de teste removido** dos fluxos de autenticação e de intertravamento. Não há mais variáveis de ambiente que alterem essas decisões.
- **Parada de emergência honesta:** a interface informa se o comando foi enviado. Sem conexão, aparece um aviso vermelho persistente para usar o botão físico. A mensagem "em repouso" só aparece depois da confirmação do ESP32.
- **Fechamento seguro:** fechar o aplicativo durante um movimento ou ensaio pede confirmação e envia parada antes de encerrar.
- **Ação padrão removida** do diálogo de fim de ensaio. Enter não aciona movimento motorizado.
- **Dados sensíveis fora do repositório:** bancos de usuários, calibração, log de falhas e caminhos pessoais de desenvolvimento foram retirados.

Pendências de segurança e operação estão listadas na [auditoria](docs/AUDITORIA_GUI_UX.md), na seção 9. Entre elas: estado físico desconhecido após emergência, tratamento de exceções durante operação, separação do banco de usuários e do histórico, e sessão manual com tempo limite.

## Limitações conhecidas

- O Kappa é demonstrativo e não foi validado analiticamente.
- Os servos não têm confirmação física de posição. Os intertravamentos usam posições estimadas pelos comandos.
- Os valores de referência dependem da geometria e da iluminação. Trocar qualquer um deles exige nova calibração.
- Alterações de segurança desta versão ainda precisam de ensaio na bancada: parada com e sem conexão, queda de cabo durante movimento e fechamento durante operação.

## Documentação e histórico de versões

| Versão | Documento |
|---|---|
| 4.16.2 | [Interface ISA-101, tema noturno e correções](INTERFACE_ISA101_4_16_2.md) |
| 4.16.1 | [Inicialização automática dos dados](INICIALIZACAO_AUTOMATICA_4_16_1.md) |
| 4.16.0 | [Carrinho com servo contínuo](CARRINHO_CONTINUO_4_16_0.md) |
| 4.15.0 | [Manual livre](MANUAL_LIVRE_4_15_0.md) |
| 4.14.3 | [Porta sem limite](PORTA_SEM_LIMITE_4_14_3.md) |
| 4.14.2 | [Correção do modo manual](CORRECAO_MANUAL_4_14_2.md) |
| 4.14.1 | [Correção de conexão](CORRECAO_CONEXAO_4_14_1.md) |
| 4.14.0 | [Porta e carcaça](PORTA_SUPERVISORIO_4_14_0.md) |
| Técnica | [Documentação técnica do supervisório](DOCUMENTACAO_TECNICA_SUPERVISORIO.md) · [PDF](SPECTRUM-LAB_PRO_Documentacao_Tecnica.pdf) |
| Identidade | [Logos, tipografia e escala de texto](docs/IDENTIDADE_VISUAL.md) |
| Auditoria | [Auditoria GUI / UX / UI e segurança](docs/AUDITORIA_GUI_UX.md) |

Os documentos de versões anteriores descrevem o comportamento daquela versão. Quando houver conflito, a versão mais recente prevalece.

---

Projeto acadêmico do curso técnico em Automação Industrial.
