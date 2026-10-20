"""
Superfícies e cores de botão do SPECTRUM-LAB PRO, no estilo plano pedido pela ISA-101.

O nome do módulo vem da versão anterior ("vidro"); hoje tudo aqui é opaco e plano:
sem degradê, sem translucidez, sem brilho ambiente e sem textura. A ISA-101 pede telas
sóbrias, em que a cor é informação (estado, alarme) e não enfeite. As receitas continuam
com os mesmos nomes (panel_fill, button_fill, tone_fill...) para o resto do código.

Módulo sem Qt, para poder ser testado em qualquer lugar (tests/test_glass.py).
"""
from animation_math import mix_hex

# Tons de botão por função: matizes que NÃO são cores de alarme (vermelho, laranja e amarelo
# ficam reservados a alarmes e avisos). Ver docs/ISA-101.md.
TONES = ("accent", "secondary", "sky", "indigo", "rose", "green", "slate", "sand")
_TONE_KEYS = {"accent": "accent", "secondary": "secondary", "sky": "sky", "indigo": "violet",
              "rose": "rose", "green": "positive", "slate": "slate", "sand": "sand"}
DARK_BORDER_STRENGTH = 1.0


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
    """'#RRGGBB' + opacidade de 0 a 1 -> 'rgba(r, g, b, N%)' para o QSS (seleções e barras de rolagem)."""
    r, g, b = _channels(color)
    return f"rgba({r}, {g}, {b}, {round(max(0.0, min(1.0, alpha)) * 100)}%)"


def rim(p, strength=1.0):
    """Cor sólida da borda de painéis e botões. strength < 1 suaviza em direção à superfície."""
    if strength >= 1.0:
        return mix_hex(p["border"], p["text"], min(0.25, (strength - 1.0) * 0.5)) if strength > 1.0 else p["border"]
    return mix_hex(p["surface"], p["border"], max(0.0, strength))


def panel_fill(p):
    """Painel: a cor de superfície, lisa."""
    return p["surface"]


def result_fill(p):
    """Cartão do resultado e rodapé: superfície com um traço do tom de destaque (4%)."""
    return mix_hex(p["surface"], p["accent"], 0.05 if is_dark(p) else 0.04)


def button_fill(p, state="rest"):
    """Botão secundário (cinza): sólido; ao passar o mouse clareia, sem mudar de cor."""
    if is_dark(p):
        amount = {"rest": 0.11, "hover": 0.18, "disabled": 0.04}[state]
        return mix_hex(p["surface"], "#FFFFFF", amount)
    return {"rest": p["soft"], "hover": mix_hex(p["soft"], p["accent"], 0.12), "disabled": p["canvas"]}[state]


def primary_fill(p, state="rest"):
    """Botão principal: cor de destaque cheia e lisa."""
    accent = p["accent_strong"]
    if state == "hot":
        return mix_hex(accent, "#FFFFFF", 0.28)
    if state == "hover":
        return mix_hex(accent, "#FFFFFF", 0.14)
    return accent


def field_fill(p):
    """Campos de texto: um poço mais fundo que o painel."""
    if is_dark(p):
        return mix_hex(p["canvas"], p["surface"], 0.45)
    return "#FFFFFF"


def glow_spec(p):
    """Sem brilho ambiente (ISA-101: fundo neutro e sem decoração)."""
    return []


def edge_highlight(p):
    """(cor, alfa) do fio de luz no topo dos botões: desligado (alfa 0)."""
    return ("#FFFFFF", 0.0)


def tone_color(p, tone):
    """Cor de um tom de botão (ver TONES) na paleta do tema."""
    return p[_TONE_KEYS[tone]]


def tone_text(p, tone):
    """Texto do botão em tom: a cor do tom clareada (escuro) ou escurecida (claro), para manter o contraste."""
    base = tone_color(p, tone)
    return mix_hex(base, "#FFFFFF", 0.55) if is_dark(p) else mix_hex(base, "#000000", 0.30)


def tone_fill(p, tone, state="rest"):
    """Botão em tom: superfície tingida com a cor do tom, sólida; mais forte ao passar o mouse."""
    base = tone_color(p, tone)
    if is_dark(p):
        amount = {"rest": 0.24, "hover": 0.36}[state]
        return mix_hex(p["surface"], base, amount)
    amount = {"rest": 0.14, "hover": 0.24}[state]
    return mix_hex("#FFFFFF", base, amount)


def tone_border(p, tone, state="rest"):
    base = tone_color(p, tone)
    return mix_hex(p["surface"], base, 0.70) if state == "rest" else base


def tone_hot(p, tone):
    """Botão em tom pressionado: a cor cheia do tom."""
    return tone_color(p, tone)


def on_tone(p):
    """Texto sobre um tom cheio (pressionado)."""
    return p["on_strong"]
