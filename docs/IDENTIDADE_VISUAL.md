# Identidade visual — SPECTRUM-LAB PRO

Este documento define os logos e a tipografia do programa, da documentação e do README. Ele vale para novas telas e para ajustes futuros.

## Logos

| Marca | Arquivo | Onde aparece |
|---|---|---|
| SPECTRUM-LAB PRO | `assets/logo/spectrumlab-mark.svg` | Ícone da janela, cabeçalho e abertura |
| SENAI | `assets/brands/senai.svg` | Rodapé da janela e abertura |
| ARAUCO \| Projeto Sucuriú | `assets/brands/arauco-sucuriu.svg` | Rodapé da janela e abertura |
| ARAUCO (wordmark isolado) | `assets/brands/arauco.svg` | Reserva, para uso sem o projeto |

Regras de uso:

- Os SVGs não têm fundo. Use sobre fundo claro ou escuro, sem recolorir a marca.
- Tamanho mínimo: 24 px de altura na tela. Abaixo disso, a marca do programa substitui a composta.
- Deixe, em volta de cada logo, um espaço livre igual à altura da letra "a" do wordmark ARAUCO.
- Os logos SENAI e ARAUCO são de terceiros. O uso no executável e na documentação depende de autorização (auditoria, item B8).

## Cores e fundo

O tema padrão é **Ouro (preto e dourado)**. Ele pode ser trocado em *Configurações → Aparência* por Claro ou Escuro, e a escolha fica salva.

| Token | Hex | Uso |
|---|---|---|
| canvas | `#0B0A08` | Fundo da janela (preto quente) |
| surface | `#131108` | Cartões e painéis |
| soft | `#1C1810` | Áreas alternadas e botões |
| border | `#4A3D22` | Bordas e divisores |
| text | `#F4EAD2` | Texto principal (marfim) |
| muted | `#BFAE86` | Texto secundário e legendas |
| disabled | `#6F6548` | Controles desabilitados |
| accent | `#D4AF37` | Títulos, destaques e detalhes dourados |
| positive | `#B9D98A` | Estado OK |
| warning | `#E8C25A` | Atenção |
| danger | `#E97462` | Erro e parada |

Contraste: texto principal sobre o fundo fica acima de 15:1, e o dourado de destaque acima de 8:1. Texto secundário acima de 7:1.

**Textura de celulose.** O fundo da janela principal leva `assets/textures/celulose-madeira.png`, uma textura de fibras e veios de madeira em âmbar com opacidade entre 3% e 18%. Ela se repete sem emendas e não reduz a leitura. Cartões e diálogos mantêm cor sólida.

**Marca.** O ícone do programa usa o mesmo preto e dourado.

## Tipografia

Famílias, todas instaladas no Windows 10 e 11 (sem instalação extra):

| Família | Função |
|---|---|
| **Bahnschrift** | Marca e títulos de destaque. Traços industriais, adequados ao contexto de bancada. |
| **Segoe UI** | Texto de interface, rótulos, corpo e legendas. |
| **Consolas** | Valores de medição (ADC, Kappa, CV %). Largura fixa mantém as colunas alinhadas. |

Ordem de substituição, quando a família não existir: Segoe UI → Arial → sans-serif.

### Escala

Tamanhos em pixels, para escala de 100%.

| Nível | Tamanho | Família e peso | Uso |
|---|---|---|---|
| Display | 44 | Bahnschrift 600 | Título da tela de abertura |
| Marca | 28 | Bahnschrift 700 | Nome curto do programa na abertura |
| Título | 18 | Bahnschrift 700 (cabeçalho) · Segoe UI 600 (diálogos) | Cabeçalho e título de diálogo |
| Seção | 14 | Segoe UI 600 | Cartões e painéis |
| Corpo | 13 | Segoe UI 400 | Texto corrido e descrições |
| Legenda | 11 | Segoe UI 600, caixa-alta, espaçamento 0,6 | Rótulos, metadados e subtítulos |
| Dado | 14 | Consolas 400 | Valores de medição e tabelas |
| KPI | 28 | Bahnschrift 700 | Valor de destaque de um indicador |

Regras de hierarquia:

1. O tamanho mínimo de texto é 11 px. Nada fica menor que isso.
2. Cada painel usa no máximo quatro tamanhos.
3. Cada tela tem um único destaque: um título ou um KPI, nunca os dois no mesmo nível.
4. Valores numéricos sempre em Consolas, para que as colunas alinhem.

### Estado da aplicação

Aplicado nesta revisão: tela de abertura (display, marca, legendas) e cabeçalho da janela principal (título e subtítulo).

Pendente: demais painéis e diálogos. A aplicação completa da escala depende de revisão visual com o programa em execução, que não foi feita nesta etapa. Ver a auditoria, itens M5 (tamanho mínimo de fonte) e M6 (contraste).
