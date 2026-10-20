# Tutorial de teste no Codespace

Roteiro para validar a interface nova: tema Escuro (preto AMOLED sóbrio, com dourado em destaque), tema Claro, Configurações em duas seções (Aparência e Acessibilidade), legibilidade e responsividade, botões em tons com animação de mola, gráficos coloridos, indicador de análise com rosto colorido, teclado na tela, rodapé com links e cursor de fibra de celulose. Tempo estimado: 50 minutos, sendo 10 de preparação.

> **Importante.** A interface foi escrita sem poder abrir o PyQt5 no ambiente do assistente. A lógica pura tem testes automáticos que passam, mas **a aparência e o toque ainda não foram vistos em execução**. É isso que este roteiro verifica.

## 1. Criar o Codespace

1. No GitHub, abra o repositório **`indiolibanes/spectrum-web`** (onde a branch desta fase está publicada; depois do merge no `yosemate/spectrum`, use ele).
2. Troque a branch para **`feat/ux-acessibilidade-animacoes`** (a interface desta fase: Configurações separadas, contraste maior no escuro, layout responsivo, botões e animações novos).
3. **Code → Codespaces → Create codespace on feat/ux-acessibilidade-animacoes**.
4. Aguarde o VS Code (web) abrir. Confira, no canto inferior esquerdo, que a branch é a certa.

Já tem um Codespace antigo? Abra o terminal e rode `git fetch && git checkout feat/ux-acessibilidade-animacoes && git pull`.

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
python3 -I tests/test_responsive_math.py
QT_QPA_PLATFORM=offscreen python3 -m unittest tests.test_gui_smoke -v
```

Esperado: os seis primeiros terminam com `OK`. O último abre widgets de verdade em modo invisível e confere: fontes registradas (e só nos estilos Regular/Bold), os cursores de fibra, só dois temas, textura pintada em ambos, painéis de vidro realmente translúcidos, indicador desenhado em todos os estados, efeito nos botões (e que ele respeita *Reduzir animações*), brilho em botão desabilitado, o teclado numérico digitando `192.168.4.1`, as **duas seções separadas das Configurações** (tema em uma; teclado e animações na outra), ícones e rostos coloridos, uma cor por barra do gráfico, os links do rodapé, o cartão de calibração sem texto comprimido e o canvas adaptativo sem cortar o layout.

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
| A1 | Observe a abertura | Marca "SpectrumLab Pro" em Garamond cor de ouro pálido; "Da luz" em ouro pálido e "à análise." em dourado; fundo preto liso, sem textura no Escuro, logos SENAI e ARAUCO; assinatura no canto inferior direito | ☐ |
| A2 | Janela principal | Fundo preto liso (confira em tela OLED, se tiver), **sem** veios ou textura no Escuro; painéis de vidro com fio de luz na borda; destaques dourados | ☐ |
| A3 | Títulos e números | "SpectrumLab Pro", "Ensaios automáticos" e o título do indicador em **Garamond** (serifa fina); rótulos e botões em Plex Sans; valores dos indicadores e o número Kappa em Mono | ☐ |
| A4 | **Configurações** → seção **Aparência** → tema **Claro** | Troca na hora, com uma fusão suave, para branco e verde; nenhum trecho azul ou preto "esquecido". O tema fica **só** nessa seção | ☐ |
| A5 | Volte para **Escuro · preto e dourado** | Preto e dourado, sem textura. A lista tem só dois temas | ☐ |
| A6 | Feche e abra o programa | Lembra o último tema escolhido | ☐ |
| A7 | Rodapé | Cartão com borda de destaque, bem visível nos dois temas. À direita: "Protótipo desenvolvido por Davi Baracat, **Kauê Carvalho** e **Mateus Ferreira**", com os dois nomes em destaque como links | ☐ |
| A7b | Clique em **Kauê Carvalho** e em **Mateus Ferreira** | Abrem `github.com/indiolibanes` e `github.com/yosemate` no navegador | ☐ |
| A8 | Abra qualquer diálogo (login, calibração) | Mesmas cores e fontes do painel principal; botões de vidro com cantos de 10 px | ☐ |
| A9 | Compare com `docs/img/especime-umber.png`, `especime-claro.png` e `especime-config-*.png` | Proporções, cores e hierarquia parecidas (o espécime não tem desfoque nem a renderização do Qt) | ☐ |

### A2. Configurações, legibilidade e cores

| # | Passo | Esperado | |
|---|---|---|---|
| S1 | Abra **Configurações** | Duas seções em cartões: **Aparência** (dois botões, Escuro e Claro) e **Acessibilidade** (Teclado na tela e Animações). O tema claro/escuro **não** aparece junto do teclado | ☐ |
| S2 | Em **Animações**, escolha **Reduzidas** | Daqui em diante: sem entrada escalonada, sem fusão na troca de tema, botões só trocam de estado. Volte para **Completas** | ☐ |
| L1 | No tema Escuro, leia rótulos, valores, legendas do gráfico e o cartão **Calibração** | Texto claro e nítido, nada comprimido; R², RMSE e N em linhas (rótulo à esquerda, valor à direita); nenhum texto menor que 12 px | ☐ |
| L2 | Role a **coluna da esquerda** (método, ensaios, calibração, resultado) | Rola inteira; os cartões não encolhem para caber | ☐ |
| L3 | Olhe os botões no tema Escuro | Todos são visíveis sobre o preto: vidro claro com borda, cada função com seu tom (azul-céu, violeta, rosa, verde, âmbar), o principal em dourado cheio | ☐ |
| L4 | Olhe o gráfico de barras | Uma cor por banda (azul, laranja, verde, âmbar, rosa, violeta), rótulos em cor de texto com uma tarja da cor da banda; curva clara com um ponto colorido por banda | ☐ |
| L5 | Olhe os quatro indicadores | Ícones coloridos (raio, tendência, folha, gota) e uma barra de cor à esquerda de cada um | ☐ |
| L6 | Confira simetria | Margens iguais entre cartões (cerca de 16 px), cartões alinhados nas bordas, rodapé na largura total | ☐ |

### B. Botões

| # | Passo | Esperado | |
|---|---|---|---|
| B1 | Passe o mouse sobre **Leitura com repetibilidade** | Borda dourada/verde, o vidro ganha luz e o realce surge sem piscar | ☐ |
| B1b | Olhe qualquer botão de perto | Um fio de luz fino no topo, cantos de 10 px, sem texto cortado | ☐ |
| B1c | Mova o mouse sobre um botão | Um foco de luz suave acompanha o ponteiro | ☐ |
| B2 | Mantenha o botão pressionado | Ele "cede" (bordas escurecem, profundidade) e uma ondulação nasce no ponto do clique | ☐ |
| B2b | Solte o botão | Volta com leve ultrapassagem (efeito de mola) e um anel que se dissipa; o tamanho do botão **não** muda | ☐ |
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
| D5 | Fim do ciclo | "Análise concluída. Boa amostra!", rosto **amarelo** com pulinho e faíscas coloridas por ~7 s; o botão volta a **Realizar leitura** | ☐ |
| D6 | Ensaio de repetibilidade | Título "Leitura com repetibilidade"; entre as leituras, "Aguardando a próxima leitura…" | ☐ |
| D7 | Parada de emergência durante um ciclo | Rosto laranja preocupado (com gota) e mensagem de emergência, sem sorriso | ☐ |
| D8 | Ao iniciar o programa e ao rodar a leitura | Painéis entram em sequência com subida suave; as barras do gráfico sobem com mola | ☐ |

### E. Responsividade

Repita A2, C1 e D3 em cada configuração (veja `run/README.md`, seção 7):

| Teste | Como | Esperado |
|---|---|---|
| 1920×1080 | `RESOLUTION=1920x1080 bash run/start_display.sh` + `bash run/start_app.sh` | Cabeçalho em **uma** linha, indicadores em **4 colunas**, painéis lado a lado; sem cortes |
| 125% | `QT_SCALE_FACTOR=1.25 bash run/start_app.sh` | Idem |
| 1366×768 | `RESOLUTION=1366x768 bash run/start_display.sh` + `bash run/start_app.sh` | Cabeçalho em **duas** linhas (campos na primeira, ações na segunda); texto do mesmo tamanho, sem compressão; teclado cabe na tela |
| 1024×768 e 800×1280 (vertical) | `RESOLUTION=1024x768 ...` e `RESOLUTION=800x1280 ...` | Indicadores em grade 2×2; painel do gráfico **embaixo** do painel de ensaios (empilhados); a janela inteira rola se preciso, o texto continua legível |
| Arrastar a borda da janela | Redimensione com o mouse | O layout se reorganiza nos pontos de quebra, sem saltos nem texto cortado |

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
| O Codespace mostra a interface antiga (sem vidro, sem Garamond) | Está na branch errada: `git fetch && git checkout feat/ux-acessibilidade-animacoes && git pull` |
| `could not load xcb` | `bash run/setup.sh` de novo |
