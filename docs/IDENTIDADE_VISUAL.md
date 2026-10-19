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
