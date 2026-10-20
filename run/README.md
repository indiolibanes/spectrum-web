# Executar o SPECTRUM-LAB PRO no Codespace (branch `run`)

Roteiro para rodar o supervisório num navegador, com display virtual e uma bancada simulada (ESP32 falso).
**Limitações:** não há hardware real e a escala de DPI do Windows não é reproduzida fielmente. As fontes (IBM Plex) vão embutidas no programa, então a tipografia é a mesma do Windows. Serve para validar layout, fluxo e comunicação, não para medir a bancada.

> Para testar a interface nova (temas, botões, indicador de análise e teclado na tela), use o roteiro completo em [docs/TUTORIAL_CODESPACE.md](../docs/TUTORIAL_CODESPACE.md). Este arquivo cobre só a parte de execução e responsividade.

## 1. Criar o Codespace

1. No GitHub, abra o repositório `indiolibanes/spectrum-web`.
2. Troque a branch para `feat/ui-ouro-arauco` (interface nova, já com os scripts de `run/`) ou `run` (interface anterior).
3. Clique em **Code → Codespaces → Create codespace on** a branch escolhida.
4. Aguarde o VS Code (web) abrir.

## 2. Instalar dependências (uma vez por Codespace)

No terminal do Codespace:

```bash
bash run/setup.sh
```

Ao final deve aparecer `PyQt5 OK`. Se houver erro de pacote, copie a mensagem e envie.

## 3. Subir o display virtual

```bash
bash run/start_display.sh
```

O padrão é **1920x1080**. Para testar outra resolução:

```bash
RESOLUTION=1366x768 bash run/start_display.sh
```

Depois, na aba **PORTS** do VS Code, localize a porta **6080**, clique com o botão direito e escolha **Port Visibility → Public** (ou mantenha Private e acesse pelo próprio navegador logado no GitHub). Abra o link e acrescente `/vnc.html` ao endereço, depois clique em **Connect**. Você verá uma área de trabalho vazia.

## 4. Iniciar o programa

Em um terminal (pode ser o mesmo, o display continua rodando em segundo plano):

```bash
bash run/start_app.sh
```

Isso sobe o ESP32 simulado na porta 8080 e abre o supervisório na área de trabalho do noVNC. O log da bancada simulada fica em `run-data/esp32_simulado.log`.

## 5. Conectar ao ESP32 simulado

No supervisório:

| Campo | Valor |
|---|---|
| Conexão | **Wi-Fi** |
| IP | **127.0.0.1** |
| Porta | **8080** |

Clique em **Conectar ESP32**. A aplicação deve mostrar a bancada conectada (`STATUS:PROTOCOLO_2`).

## 6. Primeiro acesso

Como `run-data/` começa vazio, o login mostra **CRIAR ADMINISTRADOR INICIAL**. Preencha usuário, senha (mínimo 8 caracteres) e confirmação. Esse usuário é só para teste.

## 7. Testes de responsividade

Reinicie o programa a cada troca de resolução ou escala (`Ctrl+C` no terminal do `start_app.sh` e rode de novo).

| Teste | Comando | Equivale a |
|---|---|---|
| A. Resolução de referência | `RESOLUTION=1920x1080 bash run/start_display.sh` + `bash run/start_app.sh` | 1920x1080 em 100% |
| B. Escala 125% | `QT_SCALE_FACTOR=1.25 bash run/start_app.sh` (display 1920x1080) | 1536x864 lógicos |
| C. Notebook comum | `RESOLUTION=1366x768 bash run/start_display.sh` + `bash run/start_app.sh` | 1366x768 em 100% |

Para o teste B, use `QT_SCALE_FACTOR=1.25 bash run/start_app.sh`. Os demais, sem essa variável.

### Checklist por tela

Anote **OK** ou o problema em cada item:

- [ ] Nenhum texto cortado nem sobreposto.
- [ ] Textos com pelo menos 11 px.
- [ ] Os KPIs ficam na mesma linha (não quebram em duas).
- [ ] Botões de ação visíveis sem rolar a janela.
- [ ] Diálogos (login, calibração, configurações) cabem na tela.
- [ ] Logo do cabeçalho visível e alinhado ao título.
- [ ] Barras de rolagem aparecem onde devem, não em toda parte.
- [ ] Fundo texturizado não atrapalha a leitura do texto.
- [ ] Campos de IP e porta cabem no cabeçalho sem cortar os botões ao lado.

Tire um print da tela (botão **Print Screen** ou ferramenta de captura do navegador) de cada resolução com problema e envie junto com o número do item.

## 8. Encerrar

```bash
pkill -f fake_esp32.py; pkill -f Xvfb; pkill -f x11vnc; pkill -f websockify
```

## Solução de problemas

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `could not connect to display :99` | display não subiu | rode `bash run/start_display.sh` de novo |
| Tela preta no noVNC | `start_app.sh` ainda não foi executado | execute `bash run/start_app.sh` |
| `qt.qpa.plugin: could not load xcb` | biblioteca faltando | rode `bash run/setup.sh` de novo |
| "Falha ao conectar" no supervisório | simulador não está ativo ou porta errada | confira IP `127.0.0.1` e porta `8080` |
| Porta 8080 já em uso | simulador antigo ainda rodando | `pkill -f fake_esp32.py` e repita o passo 4 |

## O que o simulador responde

`run/fake_esp32.py` atende os comandos do firmware real: `CMD:PING`, `CMD:ESTADO_PORTA`, movimentos de gaveta, porta e sensor, `CMD:LER_ESPECTRO` (6 canais, 610 a 860 nm), `CMD:LER_ESCURO`, `CMD:EMERGENCIA` e `CMD:MANUAL:<cmd>`. Ele não simula ruído, falhas nem tempos reais de motor.
