"""
Vidro: receitas de cor e QSS compartilhadas pelos painéis, botões, diálogos e teclado.

O Qt não desfoca o que está atrás de um widget, então o "vidro" aqui é construído com o que o QSS
sabe fazer: preenchimento translúcido em degradê, fio de luz na borda (rim), a textura de madeira
aparecendo por baixo dos painéis e um brilho ambiente no fundo (pintado em scada_ui.CanvasRoot).

Módulo sem Qt, para poder ser testado em qualquer lugar (tests/test_glass.py).
"""
from animation_math import mix_hex

DARK_RIM_ALPHA = 0.16
LIGHT_RIM_ALPHA = 0.22


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


def vgrad(top, bottom):
    return f"qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {top},stop:1 {bottom})"


def rim(p, strength=1.0):
    """Cor do fio de luz da borda: dourado pálido no escuro, verde no claro."""
    if is_dark(p):
        return rgba(p["heading"], DARK_RIM_ALPHA * strength)
    return rgba(p["accent"], LIGHT_RIM_ALPHA * strength)


def panel_fill(p):
    """Painel de vidro: mais claro no alto, mais fundo embaixo; deixa a madeira aparecer."""
    if is_dark(p):
        return vgrad(rgba(mix_hex(p["surface"], "#FFFFFF", 0.07), 0.74), rgba(p["surface"], 0.56))
    return vgrad(rgba("#FFFFFF", 0.88), rgba("#FFFFFF", 0.66))


def result_fill(p):
    """Cartão do resultado: o mesmo vidro com um sopro do tom de destaque."""
    if is_dark(p):
        return vgrad(rgba(mix_hex(p["soft"], p["accent"], 0.10), 0.80), rgba(mix_hex(p["surface"], p["accent"], 0.05), 0.62))
    return vgrad(rgba(mix_hex("#FFFFFF", p["accent"], 0.07), 0.94), rgba(mix_hex("#FFFFFF", p["accent"], 0.04), 0.78))


def button_fill(p, state="rest"):
    """Botão secundário: vidro leve; ao passar o mouse ganha luz, sem mudar de cor."""
    if is_dark(p):
        a = {"rest": (0.090, 0.040), "hover": (0.150, 0.075), "disabled": (0.030, 0.015)}[state]
        return vgrad(rgba("#FFFFFF", a[0]), rgba("#FFFFFF", a[1]))
    tops = {"rest": ("#FFFFFF", p["soft"]), "hover": ("#FFFFFF", mix_hex(p["soft"], p["accent"], 0.10)),
            "disabled": (p["soft"], p["soft"])}[state]
    return vgrad(*tops)


def primary_fill(p, state="rest"):
    """Botão principal: cor de destaque cheia, com luz em cima (estilo "tinted" da Apple)."""
    accent = p["accent_strong"]
    if state == "hot":
        return vgrad(mix_hex(accent, "#FFFFFF", 0.38), accent)
    if state == "hover":
        return vgrad(mix_hex(accent, "#FFFFFF", 0.22), mix_hex(accent, "#000000", 0.05))
    return vgrad(mix_hex(accent, "#FFFFFF", 0.12), mix_hex(accent, "#000000", 0.14))


def field_fill(p):
    """Campos de texto: um poço levemente mais escuro que o painel."""
    if is_dark(p):
        return rgba("#000000", 0.42)
    return rgba(p["soft"], 0.70)


def glow_spec(p):
    """Brilho ambiente do fundo: lista de (x, y, raio, cor, alfa), com x e y em fração da janela."""
    if is_dark(p):
        return [(0.12, 0.00, 0.80, p["accent"], 0.085), (0.95, 1.00, 0.70, mix_hex(p["accent"], p["warning"], 0.5), 0.055)]
    return [(0.10, 0.00, 0.75, p["accent"], 0.07), (0.95, 1.00, 0.65, p["positive"], 0.05)]


def edge_highlight(p):
    """(cor, alfa) do fio de luz desenhado pelo efeito dos botões no topo de cada botão."""
    return ("#FFFFFF", 0.30) if is_dark(p) else ("#FFFFFF", 0.80)
