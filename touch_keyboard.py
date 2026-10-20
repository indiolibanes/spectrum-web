"""
Teclado na tela para uso com touchscreen (e com mouse, se preferir).

Como funciona
  - Abre sob demanda: um DUPLO CLIQUE (ou toque duplo) em um campo de texto mostra o teclado. Um
    clique simples só posiciona o cursor, como em qualquer campo.
  - Um clique fora do teclado e fora do campo em edição o recolhe. Concluir ou Fechar também o recolhem.
  - Pode ser arrastado pela faixa do título. Ao abrir de novo, volta para perto do campo.
  - É uma janela própria que NÃO rouba o foco, então o cursor continua no campo e as teclas
    chegam a ele como se fossem as do teclado físico (QKeyEvent). Funciona com QLineEdit,
    QSpinBox, QTextEdit e QPlainTextEdit, inclusive dentro de diálogos modais.
  - Campos com a propriedade touchKeyboard = "numeric" (dígitos e ponto), "digits" (só dígitos)
    ou "off" escolhem o teclado. Sem a propriedade, usa o teclado completo (ou numérico em
    caixas de número).

As regras de teclas e de posicionamento ficam em keyboard_layouts.py (testado sem Qt).
"""
from functools import partial

from PyQt5 import sip
from PyQt5.QtCore import QEvent, QObject, QPoint, QPointF, Qt, QTimer
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (QAbstractSpinBox, QApplication, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
                             QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget)

import glass
import keyboard_layouts as kl
import typography as ty
from animation_math import mix_hex as _mix

INPUT_TYPES = (QLineEdit, QTextEdit, QPlainTextEdit)
KEYBOARD_FLAGS = Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
HEADER_GRAB_PX = 44   # faixa do título onde um arraste move o teclado


def is_input(widget):
    """Campo em que faz sentido abrir o teclado: editável, habilitado e sem touchKeyboard = off."""
    if widget is None or not isinstance(widget, INPUT_TYPES) or sip.isdeleted(widget):
        return False
    if not widget.isEnabled() or widget.isReadOnly() or widget.property("touchKeyboard") == "off":
        return False
    parent = widget.parentWidget()
    return not (parent is not None and parent.property("touchKeyboard") == "off")


def field_screen_rect(widget):
    """(x, y, largura, altura) do campo na tela, mesmo dentro de um QGraphicsView escalado."""
    size = widget.size()
    top = widget.window()
    try:
        proxy = top.graphicsProxyWidget()
        if proxy is not None and proxy.scene() is not None and proxy.scene().views():
            view = proxy.scene().views()[0]
            corner = widget.mapTo(top, QPoint(0, 0))
            far = widget.mapTo(top, QPoint(size.width(), size.height()))

            def to_screen(point):
                scene_point = proxy.mapToScene(QPointF(point))
                return view.viewport().mapToGlobal(view.mapFromScene(scene_point))

            first, second = to_screen(corner), to_screen(far)
            return first.x(), first.y(), max(1, second.x() - first.x()), max(1, second.y() - first.y())
    except RuntimeError:
        pass
    origin = widget.mapToGlobal(QPoint(0, 0))
    return origin.x(), origin.y(), size.width(), size.height()


class TouchKeyboard(QWidget):
    def __init__(self, controller):
        super().__init__(None, KEYBOARD_FLAGS)
        self.controller = controller
        self.target = None
        self.kind = "full"
        self.layer = "letters"
        self.shift = False
        self.setObjectName("touchKeyboard")
        self.setProperty("touchKeyboardWindow", True)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAccessibleName("Teclado na tela")
        self._scada_style_factory = self.style_for

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 6, 10, 10)
        root.setSpacing(6)
        header = QHBoxLayout()
        self.caption = QLabel("Teclado")
        self.caption.setObjectName("kbCaption")
        header.addWidget(self.caption, 1)
        self.close_button = QPushButton("Fechar")
        self.close_button.setObjectName("kbClose")
        self.close_button.setFocusPolicy(Qt.NoFocus)
        self.close_button.setMinimumSize(72, 28)
        self.close_button.clicked.connect(self.controller.hide_keyboard)
        header.addWidget(self.close_button)
        root.addLayout(header)
        self.rows = QVBoxLayout()
        self.rows.setSpacing(6)
        root.addLayout(self.rows, 1)

    # -- arrastar pelo título --------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() <= HEADER_GRAB_PX:
            self._drag_offset = event.globalPos() - self.pos()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        offset = getattr(self, "_drag_offset", None)
        if offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    # -- aparência ------------------------------------------------------------------------
    def style_for(self, p):
        accent = p["accent_strong"]
        hot = glass.primary_fill(p, "hot")
        rim = glass.rim(p, 1.2)
        base = p["surface"]
        return f"""QWidget#touchKeyboard {{background:{base};border:1px solid {rim};}}
QLabel#kbCaption {{color:{p['muted']};{ty.qss('label')}}}
QPushButton {{background:{glass.button_fill(p)};color:{p['text']};border:1px solid {rim};border-radius:8px;padding:0;font-family:{ty.STACK_UI};font-size:16px;font-weight:400;}}
QPushButton:pressed {{background:{hot};color:{p['on_strong']};border:1px solid {accent};}}
QPushButton#kbNum {{font-family:{ty.STACK_DATA};font-size:16px;font-weight:400;}}
QPushButton#kbAction,QPushButton#kbClose {{color:{p['muted']};{ty.qss('body')}}}
QPushButton#kbShiftOn {{color:{p['accent']};border:1px solid {p['accent']};{ty.qss('body')}}}
QPushButton#kbEnter {{background:{glass.primary_fill(p)};color:{p['on_strong']};border:1px solid {accent};{ty.qss('button')}}}
QPushButton#kbEnter:pressed {{background:{hot};}}"""

    # -- montagem das teclas ----------------------------------------------------------------
    def _clear_rows(self):
        while self.rows.count():
            item = self.rows.takeAt(0)
            layout = item.layout()
            if layout is None:
                continue
            while layout.count():
                child = layout.takeAt(0).widget()
                if child is not None:
                    child.setParent(None)
                    child.deleteLater()
            layout.deleteLater()

    def rebuild(self):
        self._clear_rows()
        numeric = self.kind in ("numeric", "digits")
        for key_row in kl.layout_for(self.kind, self.layer, self.shift):
            row = QHBoxLayout()
            row.setSpacing(6)
            for key in key_row:
                weight = int(key.weight * 10)
                if key.kind == "spacer":
                    row.addStretch(weight)
                    continue
                button = QPushButton(key.label)
                button.setFocusPolicy(Qt.NoFocus)
                button.setMinimumHeight(34)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                if key.kind == "enter":
                    button.setObjectName("kbEnter")
                elif key.kind == "shift":
                    button.setObjectName("kbShiftOn" if self.shift else "kbAction")
                elif key.kind in ("backspace", "clear", "layer", "left", "right"):
                    button.setObjectName("kbAction")
                elif numeric and key.kind == "char":
                    button.setObjectName("kbNum")
                if key.kind in ("backspace", "left", "right"):
                    button.setAutoRepeat(True)
                    button.setAutoRepeatDelay(380)
                    button.setAutoRepeatInterval(60)
                button.clicked.connect(partial(self._press, key))
                row.addWidget(button, weight)
            self.rows.addLayout(row, 1)
        self.controller.manager.apply_widget(self)
        for child in self.findChildren(QPushButton):
            self.controller.manager.apply_widget(child)

    # -- abrir / posicionar -----------------------------------------------------------------
    def open_for(self, widget):
        if sip.isdeleted(widget):
            return
        inside_spin = isinstance(widget.parentWidget(), QAbstractSpinBox)
        self.target = widget
        self.kind = kl.resolve_kind(widget.property("touchKeyboard"), inside_spin)
        self.layer, self.shift = "letters", False
        self.caption.setText(self._caption_for(widget))

        owner = widget.window()
        if self.parentWidget() is not owner:
            was_visible = self.isVisible()
            self.hide()
            self.setParent(owner, KEYBOARD_FLAGS)
            self.setAttribute(Qt.WA_ShowWithoutActivating)
            self.setAttribute(Qt.WA_StyledBackground)
            if was_visible:
                self.show()

        field = field_screen_rect(widget)
        center = QPoint(field[0] + field[2] // 2, field[1] + field[3] // 2)
        area = QApplication.desktop().availableGeometry(center)
        size = kl.keyboard_size(self.kind, area.width(), area.height())
        self.setFixedSize(*size)
        x, y = kl.compute_position(field, (area.x(), area.y(), area.width(), area.height()), size)
        self.move(x, y)
        self.rebuild()
        self.show()
        self.raise_()

    @staticmethod
    def _caption_for(widget):
        text = widget.accessibleName() or ""
        if not text and hasattr(widget, "placeholderText"):
            text = widget.placeholderText()
        if not text:
            text = (widget.toolTip() or "").split("\n")[0].split("(")[0].strip()
        return text or "Teclado"

    # -- teclas ---------------------------------------------------------------------------
    def _send(self, key_code, text=""):
        target = self.target
        if target is None or sip.isdeleted(target):
            return
        for kind in (QEvent.KeyPress, QEvent.KeyRelease):
            QApplication.sendEvent(target, QKeyEvent(kind, key_code, Qt.NoModifier, text))

    def _press(self, key, *_):
        target = self.target
        if target is None or sip.isdeleted(target):
            self.controller.hide_keyboard()
            return
        if key.kind in ("char", "space"):
            self._send(0, key.value)
            if self.shift and key.kind == "char" and key.value.isalpha():
                self.shift = False
                self.rebuild()
        elif key.kind == "backspace":
            self._send(Qt.Key_Backspace)
        elif key.kind == "clear":
            if hasattr(target, "selectAll"):
                target.selectAll()
            self._send(Qt.Key_Backspace)
        elif key.kind == "left":
            self._send(Qt.Key_Left)
        elif key.kind == "right":
            self._send(Qt.Key_Right)
        elif key.kind == "shift":
            self.shift = not self.shift
            self.rebuild()
        elif key.kind == "layer":
            self.layer, self.shift = key.value, False
            self.rebuild()
        elif key.kind == "enter":
            if isinstance(target, QLineEdit):
                self._send(Qt.Key_Return)
            self.controller.hide_keyboard()


class TouchKeyboardController(QObject):
    """Abre o teclado com duplo clique em um campo de texto e o recolhe com um clique fora dele."""
    def __init__(self, app, manager):
        super().__init__(app)
        self.app = app
        self.manager = manager
        self.keyboard = None
        app.installEventFilter(self)

    # -- janela ---------------------------------------------------------------------------
    def _window(self):
        if self.keyboard is None or sip.isdeleted(self.keyboard):
            self.keyboard = TouchKeyboard(self)
        return self.keyboard

    def _visible(self):
        return self.keyboard is not None and not sip.isdeleted(self.keyboard) and self.keyboard.isVisible()

    def _is_keyboard(self, obj):
        keyboard = self.keyboard
        if keyboard is None or sip.isdeleted(keyboard):
            return False
        return obj is keyboard or keyboard.isAncestorOf(obj)

    def hide_keyboard(self, *_):
        if self.keyboard is not None and not sip.isdeleted(self.keyboard):
            self.keyboard.target = None
            self.keyboard.hide()

    def show_for(self, widget):
        if not is_input(widget) or not widget.isVisible():
            return
        window = self._window()
        if window.isVisible() and window.target is widget:
            return
        window.open_for(widget)

    # -- observação dos eventos -------------------------------------------------------------
    def eventFilter(self, obj, event):
        if not isinstance(obj, QWidget):
            return False
        kind = event.type()
        if kind == QEvent.MouseButtonDblClick:
            if is_input(obj):
                # Adiado: o duplo clique ainda seleciona a palavra; o teclado abre logo depois.
                QTimer.singleShot(0, partial(self.show_for, obj))
        elif kind == QEvent.MouseButtonPress:
            if self._visible() and not self._is_keyboard(obj) and obj is not self.keyboard.target:
                self.hide_keyboard()
        return False
