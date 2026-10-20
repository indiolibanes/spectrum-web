"""
Teclas e posicionamento do teclado na tela (sem Qt, para poder testar sem interface).

Rótulos em português e sem emoji nem símbolos fora das fontes embutidas: o gerenciador de
temas remove emoji dos botões, então "Apagar" é texto mesmo.
"""
from dataclasses import dataclass, replace

KINDS = ("numeric", "digits", "full")
LAYERS = ("letters", "symbols", "accents")
KEY_KINDS = ("char", "backspace", "clear", "enter", "shift", "layer", "space", "left", "right", "spacer")


@dataclass(frozen=True)
class Key:
    label: str
    value: str = ""        # texto inserido (kind == "char") ou camada de destino (kind == "layer")
    kind: str = "char"
    weight: float = 1.0    # largura relativa na linha


def _chars(text, weight=1.0):
    return [Key(c, c, "char", weight) for c in text]


BACKSPACE = Key("Apagar", "", "backspace", 1.7)
CLEAR = Key("Limpar", "", "clear", 1.7)
ENTER = Key("Concluir", "", "enter", 1.9)
LEFT = Key("‹", "", "left", 1.0)     # ‹
RIGHT = Key("›", "", "right", 1.0)   # ›
SPACE = Key("Espaço", " ", "space", 5.0)


def numeric_rows(allow_dot=True):
    dot = Key(".", ".", "char", 1.0) if allow_dot else Key("", "", "spacer", 1.0)
    return [
        _chars("123") + [BACKSPACE],
        _chars("456") + [CLEAR],
        _chars("789") + [dot],
        [LEFT, Key("0", "0"), RIGHT, ENTER],
    ]


def _digits_row():
    return _chars("1234567890") + [BACKSPACE]


def _letters_rows(shift):
    def cased(text):
        return _chars(text.upper() if shift else text)
    return [
        _digits_row(),
        cased("qwertyuiop"),
        cased("asdfghjklç"),
        [Key("Maiús.", "", "shift", 1.6)] + cased("zxcvbnm") + _chars(",.") + [],
        [Key("123", "symbols", "layer", 1.5), Key("Acentos", "accents", "layer", 1.5), LEFT, SPACE, RIGHT, ENTER],
    ]


def _symbols_rows():
    return [
        _digits_row(),
        _chars("!?@#$%&*()"),
        _chars("-_+=/\\:;\"'"),
        _chars("<>[]{}~^|`") ,
        [Key("ABC", "letters", "layer", 1.5), Key("Acentos", "accents", "layer", 1.5), LEFT, SPACE, RIGHT, ENTER],
    ]


def _accents_rows(shift):
    def cased(text):
        return _chars(text.upper() if shift else text)
    return [
        _digits_row(),
        cased("áàâãäéèêë"),
        cased("íìîóòôõöú"),
        [Key("Maiús.", "", "shift", 1.6)] + cased("ùûüçñ") + [],
        [Key("ABC", "letters", "layer", 1.5), Key("123", "symbols", "layer", 1.5), LEFT, SPACE, RIGHT, ENTER],
    ]


def layout_for(kind="full", layer="letters", shift=False):
    """Linhas de teclas. kind: numeric (dígitos e ponto), digits (só dígitos) ou full."""
    if kind == "numeric":
        return numeric_rows(True)
    if kind == "digits":
        return numeric_rows(False)
    if layer == "symbols":
        return _symbols_rows()
    if layer == "accents":
        return _accents_rows(shift)
    return _letters_rows(shift)


def resolve_kind(property_value, inside_spin_box=False):
    """Tipo de teclado para um campo: a propriedade touchKeyboard do campo, ou numérico se for caixa de número."""
    if property_value in KINDS:
        return property_value
    return "numeric" if inside_spin_box else "full"


def keyboard_size(kind, screen_width, screen_height):
    """(largura, altura) do teclado em pixels, limitado à tela."""
    if kind in ("numeric", "digits"):
        width, height = 440, 372
    else:
        width, height = 1000, 396
    return min(width, max(300, screen_width - 32)), min(height, max(240, screen_height // 2))


def compute_position(field, screen, size, margin=14):
    """
    Onde colocar o teclado sem cobrir o campo em edição.
    field, screen: (x, y, largura, altura). size: (largura, altura). Retorna (x, y).
    Prefere a parte de baixo e centralizado na tela; sobe para o topo se cobrir o campo.
    """
    fx, fy, fw, fh = field
    sx, sy, sw, sh = screen
    kw, kh = size
    x = sx + (sw - kw) // 2
    bottom_y = sy + sh - kh - margin
    top_y = sy + margin
    if fy + fh + margin <= bottom_y:           # o campo cabe acima do teclado embaixo
        return x, bottom_y
    if top_y + kh + margin <= fy:              # o campo está abaixo do teclado no topo
        return x, top_y
    # Sem espaço vertical livre: alinha ao lado oposto do campo na horizontal
    field_center = fx + fw / 2
    side_x = sx + margin if field_center > sx + sw / 2 else sx + sw - kw - margin
    return max(sx, side_x), bottom_y if fy < sy + sh / 2 else top_y


def with_shift_applied(key, shift):
    """Aplica a maiúscula a uma tecla de caractere (usado por quem monta teclas fora de layout_for)."""
    if key.kind == "char" and shift and key.value.isalpha():
        return replace(key, label=key.label.upper(), value=key.value.upper())
    return key
