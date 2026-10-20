# Tutorial de teste no Codespace

Roteiro para validar a interface nova: tema Escuro (preto quase AMOLED, umber e ouro, sobre madeira), tema Claro, vidro translúcido, títulos em EB Garamond, botões refinados, cursor de fibra de celulose, indicador de análise, teclado na tela e assinatura. Tempo estimado: 40 minutos, sendo 10 de preparação.

> **Importante.** A interface foi escrita sem poder abrir o PyQt5 no ambiente do assistente. A lógica pura tem testes automáticos que passam, mas **a aparência e o toque ainda não foram vistos em execução**. É isso que este roteiro verifica.

## 1. Criar o Codespace

1. No GitHub, abra o repositório `indiolibanes/spectrum-web`.
2. Troque a branch para **`feat/ui-vidro-umber`** (esta é a branch da interface nova e já traz os scripts de `run/`). A branch anterior, `feat/ui-ouro-arauco`, tem a versão sem vidro.
3. **Code → Codespaces → Create codespace on feat/ui-vidro-umber**.
4. Aguarde o VS Code (web) abrir. Confira, no canto inferior esquerdo, que a branch é a certa.

Já tem um Codespace antigo? Abra o terminal e rode `git fetch && git checkout feat/ui-vidro-umber && git pull`.

## 2. Instalar dependências (uma vez por Codespace)

```bash
bash run/setup.sh
```

No fim deve aparecer `PyQt5 OK`. As fontes (EB Garamond e IBM Plex), as texturas e os cursores já vêm no repositório; não há nada a instalar para eles.

## 3. Conferir o ambiente (novo)

```bash
bash run/check.sh
```

O script lista com ✔ e ✘ o que está pronto: branch, arquivos novos, ferramentas, bibliotecas Python, display e portas. **Se algo falhar daqui em diante, copie a saída inteira dele.** Neste ponto é normal aparecer "display parado" e "portas sem serviço": eles sobem no passo 5.

## 4. Rodar os testes automáticos (sem janela)

Na raiz do repositório:

```bash
python3 -I tests/test_typography.py
python3 -I tests/test_glass.py
python3 -I tests/test_analysis_messages.py
python3 -I tests/test_animation_math.py
python3 -I tests/test_keyboard_layouts.py
QT_QPA_PLATFORM=offscreen python3 -m unittest tests.test_gui_smoke -v
```

Esperado: os cinco primeiros terminam com `OK`. O último abre widgets de verdade em modo invisível e confere: fontes registradas (e só nos estilos Regular/Bold), os cursores de fibra, só dois temas, textura pintada em ambos, painéis de vidro realmente translúcidos, indicador desenhado em todos os estados, efeito nos botões, brilho em botão desabilitado e o teclado numérico digitando `192.168.4.1`.

| Se falhar… | Significa |
|---|---|
| `test_embedded_fonts_are_registered` | as fontes não carregaram: confira a pasta `assets/fonts/` |
| `test_font_styles_are_regular_and_bold_only` | o Qt registrou um estilo inesperado de fonte; copie a mensagem (ela lista qual) |
| `test_cursor_images_load` ou `test_buttons_and_windows_get_the_cellulose_cursor` | os PNG de `assets/cursors/` não carregaram ou o cursor não foi instalado |
| `test_glass_panels_show_the_texture_through` | o painel está opaco: o QSS de vidro não foi aplicado |
| `test_canvas_root_paints_the_cellulose_texture` | a textura não está sendo pintada no fundo |
| `test_numeric_keyboard_types_an_ip_address` | o teclado não está entregando as teclas ao campo |
| Qualquer outro | copie a saída completa e envie |

## 5. Subir o display e abrir no navegador

```bash
bash run/start_display.sh
```

O script confere as ferramentas, espera as portas subirem e **imprime o endereço pronto** (algo como `https://<seu-codespace>-6080.app.github.dev/vnc.html?autoconnect=1&resize=scale`). Abra-o **no navegador em que você está logado no GitHub**. Você verá uma área de trabalho vazia.

Não torne a porta 6080 *Public*: a área de trabalho virtual não tem senha. Mantenha *Private*.

Depois, em outro terminal (ou no mesmo):

```bash
bash run/start_app.sh
```

Isso sobe o ESP32 simulado (porta 8080) e abre o supervisório. Se o display não estiver de pé, ele sobe sozinho. Na primeira execução, o login pede **CRIAR ADMINISTRADOR INICIAL**: use um usuário de teste e senha com 8 ou mais caracteres. Para encerrar tudo: `bash run/stop.sh`.

## 6. Roteiro de teste

Marque **OK** ou descreva o problema. Prints ajudam muito.

### A. Aparência

| # | Passo | Esperado | |
|---|---|---|---|
| A1 | Observe a abertura | Marca "SpectrumLab Pro" em Garamond cor de ouro pálido; "Da luz" em ouro pálido e "à análise." em dourado; madeira escura ao fundo, logos SENAI e ARAUCO; assinatura no canto inferior direito | ☐ |
| A2 | Janela principal | Fundo quase preto (confira em tela OLED, se tiver), veios de madeira discretos nas margens **e por trás dos painéis**, painéis de vidro com fio de luz na borda, destaques dourados | ☐ |
| A3 | Títulos e números | "SpectrumLab Pro", "Ensaios automáticos" e o título do indicador em **Garamond** (serifa fina); rótulos e botões em Plex Sans; valores dos indicadores e o número Kappa em Mono | ☐ |
| A4 | **Configurações** → tema **Claro** | Troca na hora para branco e verde; nenhum trecho azul ou preto "esquecido" | ☐ |
| A5 | Volte para **Escuro · umber e ouro** | Preto, madeira e ouro. A lista tem só dois temas | ☐ |
| A6 | Feche e abra o programa | Lembra o último tema escolhido | ☐ |
| A7 | Rodapé | À direita: "Protótipo desenvolvido por Davi Baracat, Kauê Carvalho e Mateus Ferreira" | ☐ |
| A8 | Abra qualquer diálogo (login, calibração) | Mesmas cores e fontes do painel principal; botões de vidro com cantos de 10 px | ☐ |
| A9 | Compare com `docs/img/especime-umber.png` e `especime-claro.png` | Proporções, cores e hierarquia parecidas (o espécime não tem desfoque nem a renderização do Qt) | ☐ |

### B. Botões

| # | Passo | Esperado | |
|---|---|---|---|
| B1 | Passe o mouse sobre **Leitura com repetibilidade** | Borda dourada/verde, o vidro ganha luz e o realce surge sem piscar | ☐ |
| B1b | Olhe qualquer botão de perto | Um fio de luz fino no topo, cantos de 10 px, sem texto cortado | ☐ |
| B2 | Mantenha o botão pressionado | Cor viva (mais clara) e uma ondulação que nasce no ponto do clique e some | ☐ |
| B3 | Olhe **Realizar leitura** | Destaque cheio com luz no topo (dourado no escuro, verde no claro), texto em Plex Sans negrito | ☐ |
| B4 | Com a bancada desconectada | Botões de ensaio cinza, sem efeito ao passar o mouse | ☐ |

### B2. Cursor de fibra de celulose

| # | Passo | Esperado | |
|---|---|---|---|
| K1 | Mova o mouse sobre o fundo e os painéis | Seta cor de papel com fibras soltas na cauda, legível sobre o preto | ☐ |
| K2 | Passe sobre um botão | A seta fica dourada | ☐ |
| K3 | Passe sobre o campo de IP | Cursor "I" comum, para digitar | ☐ |
| K4 | Abra um diálogo | O cursor de fibra continua | ☐ |

No noVNC, se aparecer só um ponto em vez da seta, abra o painel lateral do noVNC → *Settings* e desligue *Show Dot when No Cursor*; se ainda assim vier a seta do sistema, anote: é limite da transmissão do cursor pelo VNC, não do programa. Para comparar, rode `SPECTRUM_SYSTEM_CURSOR=1 bash run/start_app.sh`.

### C. Teclado na tela (touch)

Escolha **Conexão → Wi-Fi** no cabeçalho para mostrar os campos de IP e porta.

| # | Passo | Esperado | |
|---|---|---|---|
| C1 | Clique no campo **IP ESP32** | Abre o teclado numérico (dígitos, ponto, Apagar, Limpar, ‹ ›, Concluir) sem cobrir o campo; o cursor continua piscando no campo | ☐ |
| C2 | Digite `127.0.0.1` | Aparece no campo; a tecla pressionada fica em destaque | ☐ |
| C3 | Teste **Apagar** (segure), **‹ ›** e **Limpar** | Apaga repetindo, move o cursor e esvazia o campo | ☐ |
| C4 | Toque em **Concluir** | O teclado fecha e o valor fica | ☐ |
| C5 | Clique em **Porta** | Teclado só de dígitos (sem ponto). Digite `8080` | ☐ |
| C6 | Abra o login e clique em usuário e senha | Teclado completo; teste **Maiús.**, **123** (símbolos) e **Acentos** (á, ã, ç) | ☐ |
| C7 | **Configurações** → Teclado na tela **Desligado** | Ao clicar num campo, não abre teclado. Volte para **Ligado** | ☐ |
| C8 | Com o teclado aberto, clique em **Fechar** | Fecha; clicar de novo no campo reabre | ☐ |

Observação: no noVNC o toque do navegador chega ao programa como clique de mouse, e é por isso que o teclado abre ao clicar. Em um touchscreen de verdade o comportamento é o mesmo.

### D. Análise da amostra (com o simulador)

Conecte: Wi-Fi, IP `127.0.0.1`, porta `8080`, **Conectar ESP32**.

| # | Passo | Esperado | |
|---|---|---|---|
| D1 | Antes de iniciar | Abaixo do gráfico, rosto sorrindo e "Pronto para a próxima amostra." (pisca de vez em quando) | ☐ |
| D2 | Calibrar · Branco e escuro (confirme os pop-ups) | Título "Calibração · padrão branco" e depois "referência escura"; etapas 1 a 5 avançando | ☐ |
| D3 | **Realizar leitura** | O botão vira **Analisando…** com um brilho percorrendo; o indicador mostra etapas e frases que trocam a cada ~4,5 s | ☐ |
| D4 | Durante a leitura do espectro | Curva animada no indicador (etapa 3 de 5) | ☐ |
| D5 | Fim do ciclo | "Análise concluída. Boa amostra!", rosto com pulinho e faíscas por ~7 s; o botão volta a **Realizar leitura** | ☐ |
| D6 | Ensaio de repetibilidade | Título "Leitura com repetibilidade"; entre as leituras, "Aguardando a próxima leitura…" | ☐ |
| D7 | Parada de emergência durante um ciclo | Rosto sério e mensagem de emergência, sem sorriso | ☐ |

### E. Responsividade

Repita A2, C1 e D3 em cada configuração (veja `run/README.md`, seção 7):

| Teste | Como | Esperado |
|---|---|---|
| 1920×1080 | `RESOLUTION=1920x1080 bash run/start_display.sh` + `bash run/start_app.sh` | Sem cortes; cabeçalho cabe com os campos de IP maiores (confira se nenhum botão do cabeçalho fica cortado) |
| 125% | `QT_SCALE_FACTOR=1.25 bash run/start_app.sh` | Idem |
| 1366×768 | `RESOLUTION=1366x768 bash run/start_display.sh` + `bash run/start_app.sh` | Idem; teclado cabe na tela |

## 7. O que enviar de volta

1. A saída do passo 3 (`bash run/check.sh`) e do passo 4 (testes), em texto.
2. A tabela do passo 6 com OK/problema em cada linha.
3. Prints dos itens com problema (use a captura do navegador).
4. Se o programa fechar com erro: o final do terminal do `start_app.sh`.

## 8. Encerrar

```bash
bash run/stop.sh
```

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Fonte parecendo a padrão do sistema | Rode os testes de fontes do passo 4. Se passarem, o problema é só visual do noVNC |
| O teclado não abre | Confira Configurações → Teclado na tela **Ligado**; o campo não pode ser somente leitura |
| O teclado abre mas o cursor some do campo | Anote o gerenciador de janelas em uso (`start_display.sh` usa o fluxbox) e envie |
| O teclado cobre o campo | Envie um print com a resolução usada |
| Brilho do botão "Analisando…" não aparece | Pode ser limite de desempenho do display virtual; compare no Windows |
| Tela preta no noVNC | `bash run/start_app.sh` ainda não foi executado |
| Página do noVNC não abre (erro 502, 404 ou "não foi possível acessar") | Rode `bash run/check.sh`: ele mostra se a porta 6080 está de pé. Espere 10 s e atualize; abra o endereço impresso por `start_display.sh` **no navegador logado no GitHub**; na aba **PORTS**, a 6080 deve aparecer (Private) |
| `bash: run/start_display.sh: cannot execute` ou `\r: command not found` | Fim de linha do Windows: `sed -i 's/\r$//' run/*.sh` |
| O Codespace mostra a interface antiga (sem vidro, sem Garamond) | Está na branch errada: `git fetch && git checkout feat/ui-vidro-umber && git pull` |
| `could not load xcb` | `bash run/setup.sh` de novo |
