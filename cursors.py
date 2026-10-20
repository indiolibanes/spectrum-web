"""
Cursores de fibra de celulose.

A seta é um recorte de papel com fibras soltas na cauda; no botão (e em tudo que se clica) ela ganha
o tom dourado/verde do destaque. Os desenhos são gerados por tools/gerar_assets.py, sem imagens de
terceiros, em duas resoluções (32 px e 64 px para telas HiDPI).

Para desligar: variável de ambiente SPECTRUM_SYSTEM_CURSOR=1 (usa o cursor do sistema).
Campos de texto mantêm o cursor "I" do sistema, que é o que indica onde se digita.
"""
import os
import sys
from pathlib import Path

from PyQt5.QtCore import QEvent, QObject, Qt
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import (QAbstractButton, QApplication, QComboBox, QGraphicsView, QTabBar, QWidget)

HOTSPOT = (1, 1)           # a ponta da seta, em pixels lógicos (arquivo de 32 px)
ARROW, HAND = "fibra-seta", "fibra-mao"
_CACHE = {}


def cursor_dir():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "assets" / "cursors"


def enabled():
    return os.environ.get("SPECTRUM_SYSTEM_CURSOR", "") not in ("1", "true", "yes")


def load_cursor(name):
    """QCursor a partir de assets/cursors; None se a imagem não existir."""
    if name in _CACHE:
        return _CACHE[name]
    cursor = None
    app = QApplication.instance()
    scale = 2 if app is not None and app.devicePixelRatio() > 1.25 else 1
    path = cursor_dir() / (f"{name}@2x.png" if scale == 2 else f"{name}.png")
    if not path.exists():
        path = cursor_dir() / f"{name}.png"
        scale = 1
    pixmap = QPixmap(str(path))
    if not pixmap.isNull():
        pixmap.setDevicePixelRatio(float(scale))
        cursor = QCursor(pixmap, HOTSPOT[0] * scale, HOTSPOT[1] * scale)
    _CACHE[name] = cursor
    return cursor


def apply_arrow(widget):
    cursor = load_cursor(ARROW)
    if cursor is not None:
        widget.setCursor(cursor)


def apply_hand(widget):
    cursor = load_cursor(HAND)
    if cursor is not None:
        widget.setCursor(cursor)


class CursorController(QObject):
    """Troca o cursor das janelas (seta de fibra) e dos controles clicáveis (seta dourada)."""

    def __init__(self, app):
        super().__init__(app)
        self.active = enabled()
        if self.active:
            app.installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.active and event.type() == QEvent.Show and isinstance(obj, QWidget):
            self._apply(obj)
        return False

    def _apply(self, widget):
        if widget.property("cursorManaged"):
            return
        if isinstance(widget, (QAbstractButton, QComboBox, QTabBar)):
            if widget.isEnabled() or isinstance(widget, QAbstractButton):
                apply_hand(widget)
        elif isinstance(widget, QGraphicsView):
            apply_arrow(widget.viewport())
            apply_arrow(widget)
        elif widget.isWindow() and widget.cursor().shape() == Qt.ArrowCursor:
            apply_arrow(widget)
        else:
            return
        widget.setProperty("cursorManaged", True)
