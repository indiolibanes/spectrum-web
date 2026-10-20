"""
Efeitos de botão do SPECTRUM-LAB PRO (dinâmica inspirada nos toques da Apple).

O QSS não anima. O preenchimento, a borda e o tom por função ficam nas folhas de estilo (scada_ui,
popup_design, glass.py); este módulo acrescenta, numa camada transparente por cima de cada botão:

  - realce suave ao passar o mouse (sem reflexos nem brilho: estilo plano da ISA-101);
  - pressão com mola: ao apertar, as bordas escurecem (como um botão que afunda) e, ao soltar, o
    botão "volta" com um leve vai e volta (física de mola, animation_math.spring);
  - onda de toque (ripple) a partir do ponto tocado e um anel de luz no instante do clique;
  - brilho que percorre o botão enquanto ele estiver "em andamento" (propriedade fxBusy = True).

Não se altera o tamanho do botão ao apertar: mexer na geometria de um widget que o layout controla
pode fazer o toque na borda cair fora do botão e perder o clique. O efeito é todo de pintura.

Para desligar o efeito em um botão: button.setProperty("fx", False) antes de mostrá-lo.
Botão de fundo forte (texto escuro/claro sobre cor cheia): setProperty("fxTone", "strong").
Tom do botão (accent, secondary, sky, indigo, rose, green, slate, sand): setProperty("tone", ...), ver glass.TONES.
"""
import time

from PyQt5 import sip
from PyQt5.QtCore import QEvent, QEasingCurve, QObject, QPointF, QRectF, Qt, QTimer, QVariantAnimation
from PyQt5.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt5.QtWidgets import QPushButton, QWidget

import glass
import motion
from animation_math import busy_sweep_x, ripple_alpha, ripple_radius, spring

RADIUS = 10.0   # igual ao border-radius dos botões em glass.py / scada_ui.py
HOVER_MS = 180
RIPPLE_MS = 620
PRESS_MS = 320       # mola ao apertar: rápida, quase sem vai e volta
RELEASE_MS = 900     # mola ao soltar: com ultrapassagem visível
BUSY_PERIOD_S = 1.6


class _Overlay(QWidget):
    def __init__(self, button):
        super().__init__(button)
        self.button = button
        self.hover = 0.0
        self.depth = 0.0                 # 0 em repouso, 1 apertado; fica negativo na ultrapassagem da mola
        self.ripple_progress = 1.0
        self.ripple_center = QPointF()
        self.spot = QPointF(-1000, -1000)
        self._spring_from = 0.0
        self._spring_to = 0.0
        self._spring_params = (0.2, 0.75, PRESS_MS)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setFocusPolicy(Qt.NoFocus)

        self.hover_anim = QVariantAnimation(self)
        self.hover_anim.setDuration(HOVER_MS)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.hover_anim.valueChanged.connect(self._set_hover)

        self.ripple_anim = QVariantAnimation(self)
        self.ripple_anim.setDuration(RIPPLE_MS)
        self.ripple_anim.setStartValue(0.0)
        self.ripple_anim.setEndValue(1.0)
        self.ripple_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.ripple_anim.valueChanged.connect(self._set_ripple)

        self.spring_anim = QVariantAnimation(self)
        self.spring_anim.setStartValue(0.0)
        self.spring_anim.setEndValue(1.0)
        self.spring_anim.setEasingCurve(QEasingCurve.Linear)
        self.spring_anim.valueChanged.connect(self._set_spring)

        self.busy_timer = QTimer(self)
        self.busy_timer.setInterval(33)
        self.busy_timer.timeout.connect(self.update)
        self.busy_started = time.monotonic()

        button.setMouseTracking(True)    # o holofote acompanha o ponteiro sem precisar apertar
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

    def _set_spring(self, value):
        response, damping, duration_ms = self._spring_params
        elapsed = float(value) * duration_ms / 1000.0
        progress = spring(elapsed, response, damping)
        self.depth = self._spring_from + (self._spring_to - self._spring_from) * progress
        self.update()

    def _run_spring(self, target, response, damping, duration_ms):
        self.spring_anim.stop()
        if motion.reduced():          # "Reduzir animações": o estado muda direto, sem mola
            self.depth = float(target)
            self.update()
            return
        self._spring_from = self.depth
        self._spring_to = float(target)
        self._spring_params = (response, damping, duration_ms)
        self.spring_anim.setDuration(duration_ms)
        self.spring_anim.start()

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
            if self.depth > 0.01:
                self._run_spring(0.0, 0.55, 0.45, RELEASE_MS)
        elif kind == QEvent.MouseMove:
            self.spot = QPointF(event.pos())
            self.update()
        elif kind == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton and self.button.isEnabled():
                self.ripple_center = QPointF(event.pos())
                self.spot = QPointF(event.pos())
                self.ripple_anim.stop()
                self.ripple_anim.start()
                self._run_spring(1.0, 0.20, 0.80, PRESS_MS)
        elif kind == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton and (self.depth > 0.01 or self.spring_anim.state() == QVariantAnimation.Running):
                self._run_spring(0.0, 0.55, 0.40, RELEASE_MS)   # volta com um leve "pop"
        elif kind == QEvent.EnabledChange:
            if not self.button.isEnabled():
                self._animate_hover(0.0)
            self._sync_busy()
        elif kind == QEvent.DynamicPropertyChange:
            self._sync_busy()
        return False

    # -- pintura --------------------------------------------------------------------------
    def _tone(self, pal):
        tone = self.button.property("tone")
        if tone in glass.TONES:
            return QColor(glass.tone_color(pal, tone))
        return QColor(pal["accent"])

    def paintEvent(self, event):
        enabled = self.button.isEnabled()
        if not enabled and not self._is_busy():
            return
        from appearance import palette_for
        width, height = self.width(), self.height()
        if width < 8 or height < 8:
            return
        pal = palette_for()
        strong = self.button.property("fxTone") == "strong" or self.button.objectName() in ("scadaPrimary", "kbEnter")
        accent = self._tone(pal)
        white = QColor(255, 255, 255)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0.5, 0.5, width - 1.0, height - 1.0), RADIUS, RADIUS)
        painter.setClipPath(clip)

        edge_color, edge_alpha = glass.edge_highlight(pal)
        if enabled and edge_alpha > 0:   # fio de luz no topo (desligado no estilo plano da ISA-101)
            top = QColor(edge_color)
            top.setAlphaF(edge_alpha * (0.55 if strong else 1.0))
            fade = QColor(edge_color)
            fade.setAlpha(0)
            band = min(height * 0.5, 18.0)
            sheen = QLinearGradient(0, 0, 0, band)
            sheen.setColorAt(0.0, top)
            sheen.setColorAt(1.0, fade)
            painter.fillRect(QRectF(0, 0, width, band), sheen)

        if enabled and self.hover > 0.001:
            tint = QColor(white if strong else accent)
            tint.setAlphaF((0.14 if strong else 0.16) * self.hover)
            painter.fillRect(self.rect(), tint)

        if enabled and self.depth > 0.001:   # afundando: as bordas escurecem em direção ao centro
            shade = QColor(0, 0, 0)
            inner = QColor(shade)
            inner.setAlpha(0)
            edge = QColor(shade)
            edge.setAlphaF(min(0.40, 0.34 * self.depth))
            vignette = QRadialGradient(QPointF(width / 2.0, height / 2.0), max(width, height) * 0.62)
            vignette.setColorAt(0.55, inner)
            vignette.setColorAt(1.0, edge)
            painter.fillRect(self.rect(), vignette)
        elif enabled and self.depth < -0.001:   # ultrapassagem da mola: um anel de luz percorre a borda
            ring = QColor(white if strong else accent)
            ring.setAlphaF(min(0.85, -self.depth * 3.2))
            painter.setPen(QPen(ring, 2.0))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(QRectF(1.0, 1.0, width - 2.0, height - 2.0), RADIUS - 1, RADIUS - 1)
            glow = QColor(ring)
            glow.setAlphaF(ring.alphaF() * 0.30)
            painter.fillPath(clip, glow)

        if self._is_busy():
            phase = ((time.monotonic() - self.busy_started) / BUSY_PERIOD_S) % 1.0
            band = max(40.0, width * 0.35)
            x = busy_sweep_x(phase, width, band)
            gradient = QLinearGradient(x - band, 0, x + band, 0)
            glow = QColor(white if strong else accent)
            clear = QColor(glow)
            clear.setAlpha(0)
            peak = QColor(glow)
            peak.setAlphaF(0.36 if strong else 0.30)
            gradient.setColorAt(0.0, clear)
            gradient.setColorAt(0.5, peak)
            gradient.setColorAt(1.0, clear)
            painter.fillRect(self.rect(), gradient)

        if enabled and self.ripple_progress < 1.0:
            center = self.ripple_center
            radius = ripple_radius(center.x(), center.y(), width, height, self.ripple_progress)
            if radius > 1.0:
                color = QColor(white if strong else accent)
                color.setAlphaF(ripple_alpha(self.ripple_progress, 0.42))
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
