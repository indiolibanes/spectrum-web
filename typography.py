"""
Tipografia do SPECTRUM-LAB PRO: famílias, escala e normalização de folhas de estilo.

Hierarquia (embutida no programa para que Windows, Linux e o executável tenham a mesma aparência):

    Arena           marca: só o nome "SpectrumLab Pro" no cabeçalho (não tem dígitos nem acentos)
    Dropline        títulos e cabeçalhos de seção (tem acentos e dígitos; só existe em peso regular)
    Inter           interface: rótulos, botões e texto corrido        (SIL OFL)
    IBM Plex Mono   valores de medição, tabelas e console             (SIL OFL)

Arena e Dropline foram enviadas pelo autor do projeto; a licença de uso delas não está documentada
nos arquivos (ver docs/IDENTIDADE_VISUAL.md). A Inter e a IBM Plex Mono têm licença SIL OFL (LICENSE-Inter-OFL.txt).
EB Garamond, usada antes nos títulos, deixou de ser carregada.

Nas famílias Inter e Plex Mono só existem os pesos 400 (regular) e 700 (negrito). É de propósito: os arquivos Medium e
SemiBold dessas famílias declaram nomes de família próprios, e o Windows os registraria como
famílias separadas, quebrando o peso pedido no QSS. Regular e Bold formam par normal.

A parte de regras deste módulo não depende do Qt, para poder ser testada sem interface.
"""
import re
import sys
from pathlib import Path

FAMILY_UI = "Inter"
FAMILY_DISPLAY = "Dropline"
FAMILY_BRAND = "Arena"
FAMILY_DATA = "IBM Plex Mono"

# Pilhas com alternativas, caso a fonte embutida não carregue.
STACK_UI = f"'{FAMILY_UI}', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
# A Dropline não tem alguns sinais ("·", "…", "–"): o Qt os busca na Inter, que vem em seguida.
STACK_DISPLAY = f"'{FAMILY_DISPLAY}', '{FAMILY_UI}', 'Segoe UI', Arial, sans-serif"
STACK_BRAND = f"'{FAMILY_BRAND}', '{FAMILY_DISPLAY}', '{FAMILY_UI}', Arial, sans-serif"
STACK_DATA = f"'{FAMILY_DATA}', 'Consolas', 'Courier New', monospace"

# Escala em pixels (tamanho lógico, a 100%). Nada fica abaixo de 12: abaixo disso o texto claro
# sobre fundo escuro perde nitidez (revisão de legibilidade).
SCALE = (12, 14, 16, 20, 24, 28, 40)
(SIZE_CAPTION, SIZE_BODY, SIZE_BUTTON, SIZE_SECTION, SIZE_TITLE, SIZE_KPI, SIZE_HERO) = SCALE
SIZE_DISPLAY = 44  # só para a abertura, desenhada à mão
REGULAR, BOLD = 400, 700
# Famílias que só têm o peso regular: pedir negrito faria o Qt "engrossar" o desenho (falso negrito).
REGULAR_ONLY = ("display", "brand")

# Papéis: (tamanho, família, peso)
ROLES = {
    "display": (SIZE_DISPLAY, "display", REGULAR),
    "brand": (SIZE_TITLE, "brand", REGULAR),
    "hero": (SIZE_HERO, "data", REGULAR),
    "kpi": (SIZE_KPI, "data", REGULAR),
    "title": (SIZE_TITLE, "display", REGULAR),
    "section": (SIZE_SECTION, "display", REGULAR),
    "button": (SIZE_BUTTON, "ui", BOLD),
    "body": (SIZE_BODY, "ui", REGULAR),
    "card": (SIZE_BODY, "ui", REGULAR),
    "label": (SIZE_CAPTION, "ui", REGULAR),
    "caption": (SIZE_CAPTION, "ui", REGULAR),
    "data": (SIZE_BODY, "data", REGULAR),
}
_STACKS = {"ui": STACK_UI, "display": STACK_DISPLAY, "data": STACK_DATA, "brand": STACK_BRAND}

FONT_FILES = (
    "Inter-Regular.ttf", "Inter-Bold.ttf",
    "IBMPlexMono-Regular.ttf",
    "DroplineRegular.otf", "Arena.ttf",
)


def snap_size(px):
    """Leva qualquer tamanho em pixels ao degrau mais próximo da escala (sem passar de 40)."""
    px = float(px)
    for limit, step in ((12, 12), (14, 14), (17, 16), (22, 20), (26, 24), (34, 28)):
        if px <= limit:
            return step
    return 40


def snap_weight(value):
    """Só 400 e 700 existem nas fontes embutidas: de 600 para cima é negrito, o resto é regular."""
    text = str(value).strip().lower()
    if text in ("bold", "bolder"):
        return BOLD
    if text in ("normal", "lighter"):
        return REGULAR
    try:
        number = int(float(text))
    except ValueError:
        return value
    return BOLD if number >= 600 else REGULAR


def qss(role, extra=""):
    """Declarações QSS de um papel tipográfico (tamanho, família e peso)."""
    size, family, weight = ROLES[role]
    return f"font-family: {_STACKS[family]}; font-size: {size}px; font-weight: {weight};{(' ' + extra) if extra else ''}"


def font_stack(family_key):
    return _STACKS[family_key]


_RE_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)\s*px", re.I)
_RE_FAMILY = re.compile(r"font-family\s*:\s*([^;{}]+)(;|(?=\}))?", re.I)
_RE_WEIGHT = re.compile(r"font-weight\s*:\s*([A-Za-z0-9]+)", re.I)
_RE_LINEHEIGHT = re.compile(r"\bline-height\s*:\s*[^;{}]+;?\s*", re.I)
_RE_LETTERSPACING = re.compile(r"\bletter-spacing\s*:\s*[^;{}]+;?\s*", re.I)


def _map_family(value):
    low = value.lower()
    if "ibm plex" in low or "inter" in low or "dropline" in low or "arena" in low:
        return value.strip()
    if "garamond" in low:
        return STACK_DISPLAY
    if any(token in low for token in ("consolas", "courier", "mono", "menlo")):
        return STACK_DATA
    if any(token in low for token in ("bahnschrift", "georgia", "times", "serif")) and "sans" not in low:
        return STACK_DISPLAY
    return STACK_UI


def normalize_body(body):
    """
    Normaliza o corpo de uma regra QSS (o que fica entre chaves, ou uma lista solta de declarações):
    tamanhos na escala, pesos disponíveis, famílias da superfamília e sem propriedades que o Qt ignora.
    É idempotente: aplicar duas vezes dá o mesmo resultado.
    """
    if not body or not re.search(r"font|line-height|letter-spacing", body, re.I):
        return body

    body = _RE_LINEHEIGHT.sub("", body)      # o Qt não suporta line-height em QSS
    body = _RE_LETTERSPACING.sub("", body)   # nem letter-spacing

    snapped = []

    def size(match):
        value = snap_size(match.group(1))
        snapped.append(value)
        return f"font-size: {value}px"

    body = _RE_SIZE.sub(size, body)
    body = _RE_WEIGHT.sub(lambda m: f"font-weight: {snap_weight(m.group(1))}", body)

    has_family = bool(_RE_FAMILY.search(body))
    if has_family:
        body = _RE_FAMILY.sub(lambda m: f"font-family: {_map_family(m.group(1))}{m.group(2) or ''}", body)
    elif snapped:
        # Sem família declarada: títulos em serifa, números grandes em mono.
        biggest = max(snapped)
        if SIZE_SECTION <= biggest < SIZE_KPI:
            family = STACK_DISPLAY
        elif biggest >= SIZE_KPI:
            family = STACK_DATA
        else:
            family = None
        if family:
            glue = "" if body.rstrip().endswith(";") or not body.strip() else ";"
            body = f"{body.rstrip()}{glue} font-family: {family};"
    if FAMILY_DISPLAY in body or FAMILY_BRAND in body:
        # Dropline e Arena só têm o peso regular
        body = _RE_WEIGHT.sub("font-weight: 400", body)
    return body


def normalize_qss(source):
    """Normaliza uma folha de estilo completa (com regras entre chaves) ou uma lista de declarações."""
    if not source:
        return source
    if "{" not in source:
        return normalize_body(source)
    return re.sub(r"\{([^{}]*)\}", lambda m: "{" + normalize_body(m.group(1)) + "}", source)


def fonts_directory():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "assets" / "fonts"


def load_fonts():
    """Registra as fontes embutidas no Qt. Retorna as famílias carregadas (vazio se falhar)."""
    from PyQt5.QtGui import QFontDatabase
    loaded = []
    for name in FONT_FILES:
        path = fonts_directory() / name
        if not path.exists():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id >= 0:
            loaded.extend(QFontDatabase.applicationFontFamilies(font_id))
    return sorted(set(loaded))


def install(app):
    """Carrega as fontes e define a fonte padrão da aplicação (corpo, 13 px)."""
    from PyQt5.QtGui import QFont
    families = load_fonts()
    font = QFont(FAMILY_UI if FAMILY_UI in families else "Segoe UI")
    font.setPixelSize(SIZE_BODY)
    app.setFont(font)
    return families


def make_font(kind="ui", pixel_size=SIZE_BODY, weight=400):
    """QFont para pinturas manuais (gráficos, abertura). kind: 'ui', 'display' ou 'data'."""
    from PyQt5.QtGui import QFont
    family = {"ui": FAMILY_UI, "display": FAMILY_DISPLAY, "data": FAMILY_DATA, "brand": FAMILY_BRAND}[kind]
    font = QFont(family)
    if kind in ("display", "brand") and hasattr(font, "setFamilies"):
        font.setFamilies([family, FAMILY_UI])   # sinais que faltam na Dropline/Arena vêm da Inter
    font.setPixelSize(int(pixel_size))
    bold = snap_weight(weight) == BOLD and kind not in REGULAR_ONLY
    font.setWeight(QFont.Bold if bold else QFont.Normal)
    return font
