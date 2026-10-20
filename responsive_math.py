"""
Regras de responsividade, sem Qt (testadas em tests/test_responsive_math.py).

Antes o programa era desenhado num canvas fixo de 1600 x 1000 e reduzido por inteiro para caber na
janela: em telas menores o texto encolhia junto (um corpo de 14 px virava 9 px). Agora o canvas
acompanha a janela e a escala fica perto de 1:

    escala = limitada entre MIN_SCALE e MAX_SCALE, e nunca maior que a necessária para o
             conteúdo caber (tamanho mínimo do layout);
    tamanho lógico do canvas = janela / escala.

Em janelas estreitas ou em retrato, o layout muda de disposição (pontos de quebra em layout_mode)
em vez de simplesmente encolher.
"""
import math

REFERENCE_WIDTH = 1600     # largura em que a escala é 1:1
MIN_SCALE = 0.90           # abaixo disso o texto de 14 px passa de 12,6 px: só se o layout exigir
MAX_SCALE = 1.35           # em telas muito grandes o texto cresce até aqui

TOPBAR_TWO_ROWS_BELOW = 1590    # largura lógica abaixo da qual o cabeçalho passa a ter duas linhas
KPI_TWO_COLUMNS_BELOW = 1180    # abaixo disso os indicadores ficam em grade 2 x 2
STACK_BELOW = 1040              # abaixo disso (ou em retrato) controles e gráfico ficam empilhados


def clamp(value, low, high):
    return max(low, min(high, value))


def fit(viewport_w, viewport_h, min_w, min_h, reference=REFERENCE_WIDTH, lo=MIN_SCALE, hi=MAX_SCALE):
    """
    Devolve (escala, largura_lógica, altura_lógica) para a janela dada.

    min_w e min_h são o menor tamanho que o layout aceita (em pixels lógicos). Se a janela, na
    escala preferida, ficar menor que isso, a escala diminui o mínimo necessário: nunca há corte
    nem rolagem do conjunto.
    """
    viewport_w = max(1.0, float(viewport_w))
    viewport_h = max(1.0, float(viewport_h))
    preferred = clamp(viewport_w / float(reference), lo, hi)
    limit_w = viewport_w / max(1.0, float(min_w))
    limit_h = viewport_h / max(1.0, float(min_h))
    scale = min(preferred, limit_w, limit_h)
    return scale, int(math.ceil(viewport_w / scale)), int(math.ceil(viewport_h / scale))


def layout_mode(logical_w, logical_h):
    """Disposição para um canvas lógico de logical_w x logical_h."""
    portrait = logical_h > logical_w * 1.05
    return {
        "topbar_two_rows": logical_w < TOPBAR_TWO_ROWS_BELOW,
        "kpi_columns": 2 if logical_w < KPI_TWO_COLUMNS_BELOW else 4,
        "stack_main": portrait or logical_w < STACK_BELOW,
    }
