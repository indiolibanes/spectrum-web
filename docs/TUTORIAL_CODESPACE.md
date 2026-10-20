# Tutorial de teste no Codespace

Roteiro para validar a nova interface (temas Ouro e Claro, tipografia IBM Plex, botões animados, indicador de análise com mensagens, teclado na tela e assinatura). Tempo estimado: 40 minutos, sendo 10 de preparação.

> **Importante.** A interface nova foi escrita sem poder abrir o PyQt5 no ambiente do assistente. A lógica pura tem testes automáticos que passam, mas **a aparência e o toque ainda não foram vistos em execução**. É isso que este roteiro verifica. Se algo estiver errado, o passo 3 (testes) e o passo 6 (roteiro) dizem onde olhar.

## 1. Criar o Codespace

1. No GitHub, abra o repositório `indiolibanes/spectrum-web`.
2. Troque a branch para `feat/ui-ouro-arauco` (esta branch já contém os scripts de `run/`).
3. **Code → Codespaces → Create codespace on feat/ui-ouro-arauco**.
4. Aguarde o VS Code (web) abrir.

## 2. Instalar dependências (uma vez por Codespace)

```bash
bash run/setup.sh
```

No fim deve aparecer `PyQt5 OK`. As fontes IBM Plex já vêm no repositório (`assets/fonts/`); não há nada a instalar para elas.

## 3. Rodar os testes automáticos (sem janela)

Na raiz do repositório:

```bash
python3 -I tests/test_typography.py
python3 -I tests/test_analysis_messages.py
python3 -I tests/test_animation_math.py
python3 -I tests/test_keyboard_layouts.py
QT_QPA_PLATFORM=offscreen python3 -m unittest tests.test_gui_smoke -v
```

Esperado: os quatro primeiros terminam com `OK`. O último abre widgets de verdade em modo invisível e confere: fontes registradas, só dois temas, textura pintada em ambos, indicador desenhado em todos os estados, efeito nos botões, brilho em botão desabilitado e o teclado numérico digitando `192.168.4.1`.

| Se falhar… | Significa |
|---|---|
| `test_embedded_fonts_are_registered` | as fontes Plex não carregaram: confira a pasta `assets/fonts/` |
| `test_canvas_root_paints_the_cellulose_texture` | a textura não está sendo pintada no fundo |
| `test_numeric_keyboard_types_an_ip_address` | o teclado não está entregando as teclas ao campo |
| Qualquer outro | copie a saída completa e envie |

## 4. Subir o display virtual e abrir o noVNC

```bash
bash run/start_display.sh
```

Na aba **PORTS**, abra a porta **6080** (Private, pelo navegador logado no GitHub). Acrescente `/vnc.html` ao endereço e clique em **Connect**.

## 5. Iniciar o programa

```bash
bash run/start_app.sh
```

Isso sobe o ESP32 simulado (porta 8080) e abre o supervisório. Na primeira execução, o login pede **CRIAR ADMINISTRADOR INICIAL**: use um usuário de teste e senha com 8 ou mais caracteres.

## 6. Roteiro de teste

Marque **OK** ou descreva o problema. Prints ajudam muito.

### A. Aparência

| # | Passo | Esperado | |
|---|---|---|---|
| A1 | Observe a abertura | Marca "SpectrumLab Pro" em serifa dourada; "Da luz" em marfim e "à análise." em dourado; logos SENAI e ARAUCO; assinatura no canto inferior direito | ☐ |
| A2 | Janela principal | Fundo preto quente, texto marfim, detalhes dourados; margens com fibras de celulose quase invisíveis | ☐ |
| A3 | Títulos e números | "SpectrumLab Pro" em serifa; valores dos indicadores e o número Kappa em fonte de largura fixa (Mono) | ☐ |
| A4 | **Configurações** → tema **Claro** | Troca na hora para branco e verde; nenhum trecho azul ou preto "esquecido" | ☐ |
| A5 | Volte para **Escuro · preto e dourado** | Preto e dourado. A lista tem só dois temas | ☐ |
| A6 | Feche e abra o programa | Lembra o último tema escolhido | ☐ |
| A7 | Rodapé | À direita: "Protótipo desenvolvido por Davi Baracat, Kauê Carvalho e Mateus Ferreira" | ☐ |
| A8 | Abra qualquer diálogo (login, calibração) | Mesmas cores e fontes do painel principal; botões com gradiente | ☐ |

### B. Botões

| # | Passo | Esperado | |
|---|---|---|---|
| B1 | Passe o mouse sobre **Leitura com repetibilidade** | Borda dourada/verde e leve realce que surge, sem piscar | ☐ |
| B2 | Mantenha o botão pressionado | Cor viva (mais clara) e uma ondulação que nasce no ponto do clique e some | ☐ |
| B3 | Olhe **Realizar leitura** | Gradiente sutil (dourado no tema escuro, verde no claro) | ☐ |
| B4 | Com a bancada desconectada | Botões de ensaio cinza, sem efeito ao passar o mouse | ☐ |

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

1. A saída do passo 3 (texto).
2. A tabela do passo 6 com OK/problema em cada linha.
3. Prints dos itens com problema (use a captura do navegador).
4. Se o programa fechar com erro: o final do terminal do `start_app.sh`.

## 8. Encerrar

```bash
pkill -f fake_esp32.py; pkill -f Xvfb; pkill -f x11vnc; pkill -f websockify
```

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| Fonte parecendo a padrão do sistema | Rode o teste de fontes do passo 3. Se passar, o problema é só visual do noVNC |
| O teclado não abre | Confira Configurações → Teclado na tela **Ligado**; o campo não pode ser somente leitura |
| O teclado abre mas o cursor some do campo | Anote o gerenciador de janelas em uso (`start_display.sh` usa o fluxbox) e envie |
| O teclado cobre o campo | Envie um print com a resolução usada |
| Brilho do botão "Analisando…" não aparece | Pode ser limite de desempenho do display virtual; compare no Windows |
| Tela preta no noVNC | `bash run/start_app.sh` ainda não foi executado |
| `could not load xcb` | `bash run/setup.sh` de novo |
