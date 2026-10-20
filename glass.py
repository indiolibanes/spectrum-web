"""
Superfícies e cores de botão do SPECTRUM-LAB PRO.

Estilo: minimalista e inspirado no iOS. Os **gráficos** têm cor (uma por banda); os **botões**
são neutros, translúcidos e sem fio de luz. Os painéis são translúcidos sobre um fundo com brilhos
roxos (noturno) ou verdes (claro), para que a profundidade venha da transparência e não de ornamento.
Ouro (noturno) e verde (claro) aparecem como foco e identidade, nunca como preenchimento de botão.

Módulo sem Qt, para poder ser testado em qualquer lugar (tests/test_glass.py).
"""
from animation_math import mix_hex

# Tons por função (usados só nas barras dos indicadores e nos testes). Os botões são neutros.
TONES = ("accent", "secondary", "sky", "indigo", "rose", "green", "slate", "sand")
_TONE_KEYS = {"accent": "accent", "secondary": "secondary", "sky": "sky", "indigo": "violet",
              "rose": "rose", "green": "positive", "slate": "slate", "sand": "sand"}

# Opacidade dos painéis: quanto menor, mais o fundo aparece (translucidez).
PANEL_ALPHA_DARK = 0.32
PANEL_ALPHA_LIGHT = 0.52


def _channels(color):
    return tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))


def luminance(color):
    """Luminância relativa (WCAG, 0 a 1) de '#RRGGBB'."""
    r, g, b = ((c / 255.0) / 12.92 if c / 255.0 <= 0.04045 else (((c / 255.0) + 0.055) / 1.055) ** 2.4
               for c in _channels(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def is_dark(p):
    return luminance(p["canvas"]) < 0.18


def rgba(color, alpha):
    """'#RRGGBB' + opacidade de 0 a 1 -> 'rgba(r, g, b, N%)' para o QSS."""
    r, g, b = _channels(color)
    return f"rgba({r}, {g}, {b}, {round(max(0.0, min(1.0, alpha)) * 100)}%)"


def rim(p, strength=1.0):
    """Fio fino e neutro das bordas (tinta do tema, translúcida). strength aumenta ou reduz."""
    return rgba(p["text"], 0.16 * strength)


def panel_fill(p):
    """Painel translúcido: a superfície com opacidade, deixando o fundo aparecer."""
    return rgba(p["surface"], PANEL_ALPHA_DARK if is_dark(p) else PANEL_ALPHA_LIGHT)


def result_fill(p):
    """Cartão do resultado e rodapé: um pouco mais opaco, com um sopro de destaque."""
    base = mix_hex(p["surface"], p["accent"], 0.08)
    return rgba(base, (PANEL_ALPHA_DARK if is_dark(p) else PANEL_ALPHA_LIGHT) + 0.10)


def button_fill(p, state="rest"):
    """Botão neutro e translúcido (estilo iOS): um véu da cor de texto; ao passar o mouse, um pouco mais."""
    if is_dark(p):
        alpha = {"rest": 0.10, "hover": 0.17, "disabled": 0.04}[state]
    else:
        alpha = {"rest": 0.07, "hover": 0.12, "disabled": 0.04}[state]
    return rgba(p["text"], alpha)


def primary_fill(p, state="rest"):
    """Botão principal: preenchimento sólido neutro (cor de texto), que escurece ou clareia pouco."""
    if state == "hot":
        return mix_hex(p["text"], p["accent"], 0.25)
    if state == "hover":
        return mix_hex(p["text"], p["accent"], 0.12)
    return p["text"]


def field_fill(p):
    """Campos de texto: um poço translúcido, mais fundo que o painel."""
    return rgba(p["canvas"], 0.55) if is_dark(p) else rgba("#FFFFFF", 0.85)


def glow_spec(p):
    """Brilhos suaves do fundo (x e y em fração da janela): dão profundidade aos painéis translúcidos."""
    if is_dark(p):
        return [(0.08, 0.00, 0.85, p["secondary"], 0.26), (0.98, 1.00, 0.75, p["accent"], 0.14)]
    return [(0.10, 0.00, 0.80, "#7DBE6A", 0.22), (0.95, 1.00, 0.70, "#B8DDA0", 0.28)]


def edge_highlight(p):
    """Sem fio de luz no topo dos botões (alfa 0)."""
    return ("#FFFFFF", 0.0)


def tone_color(p, tone):
    """Cor de um tom (ver TONES) na paleta do tema: usada nas barras e indicadores, não nos botões."""
    return p[_TONE_KEYS[tone]]


def tone_text(p, tone):
    """Texto de botão: sempre a cor de texto do tema (botões neutros)."""
    return p["text"]


def tone_fill(p, tone, state="rest"):
    """Preenchimento de botão: neutro, igual para todas as funções."""
    return button_fill(p, state)


def tone_border(p, tone, state="rest"):
    """Borda de botão: fio neutro em repouso; destaque dourado/verde ao passar o mouse."""
    return rgba(p["accent"], 0.85) if state == "hover" else rim(p, 1.5)


def tone_hot(p, tone):
    """Botão pressionado: o mesmo preenchimento principal."""
    return primary_fill(p, "hot")


def on_tone(p):
    """Texto sobre o preenchimento principal (pressionado)."""
    return p["on_strong"]
