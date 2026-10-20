"""
Efeitos de botão do SPECTRUM-LAB PRO.

O QSS não anima. Por isso o gradiente e a cor de "pressionado" ficam nas folhas de estilo
(appearance / scada_ui / popup_design) e este módulo acrescenta só o que o QSS não faz:

  - realce que surge e some suavemente ao passar o mouse (ou o dedo);
  - ondulação (ripple) que nasce no ponto tocado ao pressionar;
  - brilho que percorre o botão enquanto ele estiver "em andamento"
    (propriedade dinâmica fxBusy = True, usada no botão Realizar leitura durante a análise).

Cada QPushButton recebe uma camada transparente por cima, que não captura o mouse.
Para desligar o efeito em um botão: button.setProperty("fx", False) antes de mostrá-lo.
Para um botão de fundo forte (texto escuro/claro sobre cor cheia): setProperty("fxTone", "strong").
"""
import time

from PyQt5 import sip
from PyQt5.QtCore import QEvent, QEasingCurve, QObject, QPointF, QRectF, Qt, QTimer, QVariantAnimation
from PyQt5.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QRadialGradient
from PyQt5.QtWidgets import QPushButton, QWidget

from animation_math import busy_sweep_x, ripple_alpha, ripple_radius

RADIUS = 7.0
HOVER_MS = 140
RIPPLE_MS = 520
BUSY_PERIOD_S = 1.6


class _Overlay(QWidget):
    def __init__(self, button):
        super().__init__(button)
        self.button = button
        self.hover = 0.0
        self.ripple_progress = 1.0
        self.ripple_center = QPointF()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setFocusPolicy(Qt.NoFocus)

        self.hover_anim = QVariantAnimation(self)
        self.hover_anim.setDuration(HOVER_MS)
        self.hover_anim.setEasingCurve(QEasingCurve.OutQuad)
        self.hover_anim.valueChanged.connect(self._set_hover)

        self.ripple_anim = QVariantAnimation(self)
        self.ripple_anim.setDuration(RIPPLE_MS)
        self.ripple_anim.setStartValue(0.0)
        self.ripple_anim.setEndValue(1.0)
        self.ripple_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.ripple_anim.valueChanged.connect(self._set_ripple)

        self.busy_timer = QTimer(self)
        self.busy_timer.setInterval(33)
        self.busy_timer.timeout.connect(self.update)
        self.busy_started = time.monotonic()

        button.installEventFilter(self)
        self.setGeometry(button.rect())
        self.show()
        self.raise_()
        self._sync_busy()

    # -- estado -------------------------------------------------------------------------
    def _set_hover(self, value):
        self.hover = float(value)
        self.update()

    def _set_ripple(self, value):
        self.ripple_progress = float(value)
        self.update()

    def _is_busy(self):
        # O botão fica desabilitado enquanto o ciclo roda; mesmo assim ele mostra que está trabalhando.
        return bool(self.button.property("fxBusy"))

    def _sync_busy(self):
        if self._is_busy():
            if not self.busy_timer.isActive():
                self.busy_started = time.monotonic()
                self.busy_timer.start()
        else:
            self.busy_timer.stop()
            self.update()

    def _animate_hover(self, target):
        self.hover_anim.stop()
        self.hover_anim.setStartValue(self.hover)
        self.hover_anim.setEndValue(float(target))
        self.hover_anim.start()

    # -- eventos do botão -----------------------------------------------------------------
    def eventFilter(self, obj, event):
        if obj is not self.button or sip.isdeleted(self):
            return False
        kind = event.type()
        if kind in (QEvent.Resize, QEvent.Move, QEvent.Show):
            self.setGeometry(self.button.rect())
            self.raise_()
        elif kind == QEvent.Enter:
            if self.button.isEnabled():
                self._animate_hover(1.0)
        elif kind == QEvent.Leave:
            self._animate_hover(0.0)
        elif kind == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and self.button.isEnabled():
                self.ripple_center = QPointF(event.pos())
                self.ripple_anim.stop()
                self.ripple_anim.start()
        elif kind == QEvent.EnabledChange:
            if not self.button.isEnabled():
                self._animate_hover(0.0)
            self._sync_busy()
        elif kind == QEvent.DynamicPropertyChange:
            self._sync_busy()
        return False

    # -- pintura --------------------------------------------------------------------------
    def paintEvent(self, event):
        enabled = self.button.isEnabled()
        if not enabled and not self._is_busy():
            return
        from appearance import palette_for
        width, height = self.width(), self.height()
        if width < 8 or height < 8:
            return
        strong = self.button.property("fxTone") == "strong" or self.button.objectName() == "scadaPrimary"
        accent = QColor(palette_for()["accent"])

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0.5, 0.5, width - 1.0, height - 1.0), RADIUS, RADIUS)
        painter.setClipPath(clip)

        if enabled and self.hover > 0.001:
            tint = QColor(255, 255, 255) if strong else QColor(accent)
            tint.setAlphaF((0.16 if strong else 0.12) * self.hover)
            painter.fillRect(self.rect(), tint)

        if self._is_busy():
            phase = ((time.monotonic() - self.busy_started) / BUSY_PERIOD_S) % 1.0
            band = max(40.0, width * 0.35)
            x = busy_sweep_x(phase, width, band)
            gradient = QLinearGradient(x - band, 0, x + band, 0)
            glow = QColor(255, 255, 255) if strong else QColor(accent)
            clear = QColor(glow)
            clear.setAlpha(0)
            peak = QColor(glow)
            peak.setAlphaF(0.34 if strong else 0.26)
            gradient.setColorAt(0.0, clear)
            gradient.setColorAt(0.5, peak)
            gradient.setColorAt(1.0, clear)
            painter.fillRect(self.rect(), gradient)

        if enabled and self.ripple_progress < 1.0:
            center = self.ripple_center
            radius = ripple_radius(center.x(), center.y(), width, height, self.ripple_progress)
            if radius > 1.0:
                color = QColor(255, 255, 255) if strong else QColor(accent)
                color.setAlphaF(ripple_alpha(self.ripple_progress))
                edge = QColor(color)
                edge.setAlpha(0)
                gradient = QRadialGradient(center, radius)
                gradient.setColorAt(0.0, color)
                gradient.setColorAt(0.75, color)
                gradient.setColorAt(1.0, edge)
                painter.setBrush(gradient)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(center, radius, radius)
        painter.end()


class ButtonFx(QObject):
    """Anexa o efeito a todo QPushButton quando ele é mostrado pela primeira vez."""

    def __init__(self, app):
        super().__init__(app)
        app.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Show and isinstance(obj, QPushButton):
            if getattr(obj, "_fx_overlay", None) is None and obj.property("fx") is not False and not obj.isFlat():
                obj._fx_overlay = _Overlay(obj)
        return False
