# Identidade visual — SPECTRUM-LAB PRO

Este documento define logos, cores, tipografia, vidro, cursor e comportamento visual do programa, da documentação e do README. Vale para novas telas e ajustes futuros.

![Tema Escuro](img/especime-umber.png)
![Tema Claro](img/especime-claro.png)

> As duas imagens são um **espécime em HTML** gerado por `tools/especime.py` a partir das **mesmas paletas e receitas de vidro** do programa (`appearance.py` e `glass.py`). Servem para conferir hierarquia, contraste e proporção. **Não são capturas da tela real**: o desfoque de fundo e a renderização exata das fontes no Qt só se confirmam com o programa aberto (`docs/TUTORIAL_CODESPACE.md`).

## Linguagem de design

Três referências, todas usadas como inspiração de linguagem, nunca como cópia de código ou de imagem:

- **Vidro translúcido** (superfícies que deixam o fundo aparecer, com um fio de luz na borda). Ponto de partida: o visual do app BitChord, que é licenciado em GPL-3.0; por isso **nenhum código nem recurso dele** foi copiado, só a ideia (cartões flutuantes, translucidez, realce de borda).
- **Clareza da interface da Apple**: poucos elementos por tela, hierarquia tipográfica curta, cantos generosos (10 px nos botões e campos, 16 px nos painéis), um único tom de destaque usado com contenção, estados de toque discretos. Só a *linguagem*: as fontes e o kit visual da Apple são proprietários e não são usados.
- **Material 3** para os estados de toque (realce ao passar, cor viva ao pressionar, ondulação no ponto tocado) e alvos de toque grandes.

**O que o Qt não faz.** O QSS não desfoca o que está atrás do widget. O vidro é construído com preenchimento translúcido em degradê, fio de luz na borda, a textura do fundo aparecendo por baixo dos painéis e um brilho ambiente pintado no fundo. Resultado: a mesma sensação de profundidade, sem desfoque real.

**Por que não Jetpack Compose neste programa.** O Compose é uma biblioteca em Kotlin (Android e JVM) e não pode ser embutido em um aplicativo PyQt5. O caminho para Android é um cliente separado, que fale o mesmo protocolo TCP do ESP32 (comandos em `run/fake_esp32.py`), e fica para a última fase do roteiro: primeiro UX/UI, depois animações, por fim Android e talvez web.

## Logos

| Marca | Arquivo | Onde aparece |
|---|---|---|
| SPECTRUM-LAB PRO | `assets/logo/spectrumlab-mark.svg` | Ícone da janela e abertura |
| SENAI | `assets/brands/senai.svg` | Rodapé da janela e abertura |
| ARAUCO \| Projeto Sucuriú | `assets/brands/arauco-sucuriu.svg` | Rodapé da janela e abertura |
| ARAUCO (wordmark isolado) | `assets/brands/arauco.svg` | Reserva, para uso sem o projeto |

Regras de uso:

- Os SVGs não têm fundo. Use sobre fundo claro ou escuro, sem recolorir a marca.
- Tamanho mínimo: 24 px de altura na tela. Abaixo disso, a marca do programa substitui a composta.
- Deixe, em volta de cada logo, um espaço livre igual à altura da letra "a" do wordmark ARAUCO.
- Os logos SENAI e ARAUCO são de terceiros. O uso no executável e na documentação depende de autorização (auditoria, item B8).

## Assinatura

> Protótipo desenvolvido por Davi Baracat, Kauê Carvalho e Mateus Ferreira

Aparece na abertura (canto inferior direito) e no rodapé da janela principal. O texto está em `version.py` (`__credits__` e `__authors__`), em um só lugar.

## Temas

Há dois temas, escolhidos em *Configurações → Aparência*; a escolha fica salva. Preferências antigas (`dark`, `gold`) migram sozinhas para o tema Escuro.

### Escuro · umber e ouro (padrão)

Preto quase AMOLED (`#050504`: os pixels ficam praticamente apagados em telas OLED) com os tons de papel, umber e ouro da identidade do autor.

| Token | Hex | Uso |
|---|---|---|
| canvas | `#050504` | Fundo da janela |
| surface | `#14120D` | Diálogos e base dos painéis de vidro |
| soft | `#1F1C14` | Áreas alternadas |
| border | `#4C4638` | Bordas sólidas e divisores |
| text | `#F0EADB` | Texto principal (papel) |
| heading | `#FFF1B4` | Títulos (ouro pálido) |
| muted | `#C7BFA9` | Texto secundário |
| disabled | `#6F6853` | Controles desabilitados |
| accent | `#E2C35C` | Destaque: botão principal, números, curva |
| positive / warning / danger | `#8FBF86` / `#E79A5C` / `#EC7F73` | Estado OK / atenção / erro |
| on_strong | `#3B2F00` | Texto sobre botão dourado |

**Textura de madeira.** `assets/textures/madeira-escura.png`: tábuas de fibra âmbar quase transparentes, geradas por `tools/gerar_assets.py` (semente fixa, sem imagem de terceiros). Aparece no fundo e por trás dos painéis de vidro.

### Claro: branco e verde

| Token | Hex | Uso |
|---|---|---|
| canvas | `#F6F9F3` | Fundo da janela (branco com um fio de verde) |
| surface | `#FFFFFF` | Cartões e diálogos |
| soft | `#EAF1E4` | Áreas alternadas |
| border | `#CBD6C2` | Bordas e divisores |
| text | `#1B2612` | Texto principal |
| heading | `#243818` | Títulos |
| muted | `#56634B` | Texto secundário |
| disabled | `#7E8873` | Controles desabilitados |
| accent | `#436722` | Verde de destaque e botão primário |
| positive / warning / danger | `#266435` / `#8A5A00` / `#B3261E` | Estado OK / atenção / erro |
| on_strong | `#FFFFFF` | Texto sobre botão verde |

**Textura de celulose.** `assets/textures/celulose-claro.png`: fibras verde-musgo quase transparentes.

**Origem do verde.** Não há manual de marca da Arauco no repositório. O verde foi derivado do logo *ARAUCO | Projeto Sucuriú* (matiz das colinas, cerca de 92°) e escurecido para dar contraste. **Se houver o manual oficial, troque `accent` e `accent_strong` em `appearance.py`** e o resto do tema acompanha.

**Contrastes (WCAG, conferidos em `tests/test_glass.py`).** Texto sobre fundo acima de 14:1; texto secundário sobre cartão acima de 6:1; destaque sobre fundo acima de 6:1; texto do botão principal e do botão de perigo acima de 4,5:1. Controles desabilitados ficam perto de 3,5:1 de propósito.

## Vidro

Receitas em `glass.py` (sem Qt, testadas):

| Elemento | Receita |
|---|---|
| Painel | Degradê vertical translúcido (74% em cima, 56% embaixo no escuro), borda de 1 px com fio de luz (16% de `heading` no escuro, 22% de `accent` no claro), raio 16 px |
| Cartão de resultado | O mesmo vidro com um sopro do tom de destaque e borda de destaque a 38% |
| Botão secundário | Vidro leve; ao passar o mouse ganha luz e a borda vira destaque |
| Botão principal | Cor de destaque cheia, com luz no topo (desenhada por `button_fx.py`) |
| Campos | Poço levemente mais escuro que o painel, borda de destaque no foco |
| Fundo | Cor do tema + textura + dois brilhos ambientes (dourado no escuro, verde no claro) |

Diálogos usam cor sólida (são janelas separadas e não há o que enxergar através delas).

## Tipografia

Duas famílias com licença SIL OFL, embutidas em `assets/fonts/`; o programa as carrega na abertura, então a aparência é igual no Windows, no Linux e no executável. Licenças em `assets/fonts/LICENSE-*.txt`.

| Família | Função |
|---|---|
| **EB Garamond** | Títulos e marca: serifa humanista de traço fino, que dá o tom editorial |
| **IBM Plex Sans** | Interface: rótulos, botões, texto corrido |
| **IBM Plex Mono** | Valores de medição (KPIs, número kappa, eixos do gráfico, console), com largura fixa para alinhar |

Só os pesos **400 e 700** são usados: são os que Windows, macOS e Linux agrupam na mesma família sem ambiguidade. Os pesos intermediários (Medium, SemiBold) foram removidos de propósito.

Se uma fonte não carregar, o programa usa Georgia / Segoe UI / Consolas (nessa ordem de preferência por papel).

### Escala (pixels, a 100%)

| Papel | Tamanho | Família · peso | Uso |
|---|---|---|---|
| display | 44 | Garamond 700 | Só na abertura |
| hero | 40 | Mono 400 | Número kappa |
| kpi | 28 | Mono 400 | Valor dos indicadores |
| title | 24 | Garamond 700 | Marca no cabeçalho, títulos de diálogo |
| section | 19 | Garamond 700 | Títulos de painel e do indicador de análise |
| button | 15 | Sans 700 | Botão principal e Concluir do teclado |
| card | 13 | Sans 400 | Título de cartão, botões |
| body | 13 | Sans 400 | Texto corrido, campos |
| label | 11 | Sans 400 | Rótulos pequenos |
| caption | 11 | Sans 400 | Legendas e apoio |
| data | 13 | Mono 400 | Tabelas e console |

Regras:

1. O mínimo é 11 px. Nada fica menor.
2. Cada painel usa no máximo quatro tamanhos.
3. Cada tela tem um único destaque.
4. Números de medição sempre em Mono.
5. O QSS do Qt **ignora** `line-height` e `letter-spacing`; por isso o programa não os usa.

**Como é aplicado.** `typography.py` define a escala. Toda folha de estilo que passa pelo gerenciador de temas é normalizada: tamanhos vão ao degrau mais próximo, pesos aos disponíveis (400 ou 700), famílias antigas (Segoe UI, Bahnschrift, Consolas) à família do mesmo papel, e `line-height`/`letter-spacing` são removidos. Assim, telas antigas seguem a escala sem reescrita. Novos widgets devem usar `typography.qss("papel")`.

## Cursor

O cursor do mouse é uma **seta de fibra de celulose**: corpo cor de papel, contorno escuro, um fio de luz claro para ler sobre o fundo preto e fibras soltas na cauda. Sobre botões, listas e abas vira uma seta dourada com o mesmo desenho (`assets/cursors/fibra-seta*.png` e `fibra-mao*.png`, em 32 px e 64 px para telas HiDPI). Campos de texto mantêm o cursor "I" do sistema, que indica onde se digita.

Os desenhos são gerados por `tools/gerar_assets.py`. A instalação está em `cursors.py` (um filtro de eventos da aplicação). Para voltar ao cursor do sistema: variável de ambiente `SPECTRUM_SYSTEM_CURSOR=1`.

## Botões e animações

| Estado | Efeito |
|---|---|
| Repouso | Vidro leve com fio de luz no topo (botão principal: destaque cheio) |
| Passar o mouse/dedo | Borda de destaque e realce que surge suavemente (140 ms) |
| Pressionado | Degradê vivo do tema, com ondulação (520 ms) a partir do ponto tocado |
| Em andamento | O botão que iniciou o ciclo vira "Analisando…" com um brilho que percorre o botão |
| Desabilitado | Vidro apagado, texto cinza do tema, sem efeito |

Implementação: o preenchimento e a cor de pressionado ficam no QSS; `button_fx.py` acrescenta o que o QSS não anima (realce, fio de luz, ondulação e brilho) com uma camada transparente por cima de cada botão.

**Fase seguinte.** Esta revisão fecha UX/UI. As animações (transições entre telas, entrada dos painéis, curva do gráfico) ficam para a próxima fase, como combinado.

## Indicador de análise

Abaixo do gráfico, o `AnalysisIndicator` mostra o que o equipamento faz, em linguagem simples:

- **Rosto** desenhado (sem emoji): sorri em repouso e ao concluir, pisca de tempos em tempos, dá um pulinho com faíscas quando a análise termina e fica sério em falha ou emergência.
- **Título e frase** que se alternam a cada 4,5 s (`analysis_messages.py`, textos em português do Brasil).
- **Espectro animado** durante a leitura e **etapas 1 a 5** (fechar gaveta, avançar sensor, ler, recuar sensor, abrir gaveta).
- **Mensagem final** "Análise concluída. Boa amostra!" por 7 s.

## Teclado na tela

Para touchscreen, ao tocar em um campo de texto abre um teclado próprio (`touch_keyboard.py`), com teclas de vidro e o mesmo destaque dos botões:

- **Numérico** (dígitos e ponto) no campo de IP; **só dígitos** na porta.
- **Completo** (letras, símbolos e acentos do português) nos demais campos, como login e nomes de amostra.
- Não rouba o foco: o cursor continua no campo e as teclas chegam como as do teclado físico.
- Posiciona-se onde não cubra o campo em edição e funciona dentro de diálogos modais.
- Liga e desliga em *Configurações → Aparência* (padrão: ligado).

Para um campo novo escolher o teclado: `campo.setProperty("touchKeyboard", "numeric")` (ou `"digits"` / `"off"`).

## Estado da aplicação

Aplicado: abertura, painel principal, cartões KPI, gráficos, diálogos (via normalização), campos de IP, teclado, indicador, cursor.

**Não verificado com o programa em execução.** Esta revisão foi escrita sem PyQt5 disponível no ambiente de desenvolvimento do assistente: a lógica pura tem testes (`tests/`), e há um teste gráfico (`tests/test_gui_smoke.py`) para rodar no Codespace, mas o resultado visual real precisa ser conferido pelo roteiro de `docs/TUTORIAL_CODESPACE.md`.
