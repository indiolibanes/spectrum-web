"""
Indicador de análise: mostra, abaixo do gráfico espectral, o que o equipamento está fazendo.

  [rosto]  Título da fase                                  espectro em movimento
           Frase amigável que se alterna                    etapa 3 de 5  ▮▮▮▯▯

O rosto é desenhado (sem emoji, que o gerenciador de temas remove): sorri quando tudo vai bem,
pisca de tempos em tempos e dá um pulinho quando uma análise termina. Em emergência ou falha
fica sério. O texto vem de analysis_messages.py (testado sem Qt).
"""
import time

from PyQt5.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

import analysis_messages as messages
from animation_math import blink_amount, bounce, mouth_params, pulse, spectrum_points
from typography import make_font

HEIGHT = 92
MESSAGE_SECONDS = 4.5      # tempo de cada frase
CELEBRATE_SECONDS = 7.0    # quanto tempo o "análise concluída" fica na tela
FAST_MS = 40               # animação enquanto algo se move
SLOW_MS = 120              # em repouso (só o piscar)
POLL_MS = 250              # com que frequência lê o estado da máquina


class AnalysisIndicator(QWidget):
    busyChanged = pyqtSignal(bool)

    def __init__(self, state_provider, parent=None):
        super().__init__(parent)
        self._provider = state_provider
        self._state = "IDLE"
        self._phase = messages.phase_for("IDLE")
        self._phase_started = time.monotonic()
        self._celebrate_until = 0.0
        self._busy = False
        self._born = time.monotonic()
        self.setFixedHeight(HEIGHT)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setAccessibleName("Estado da análise")
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

        self._poll = QTimer(self)
        self._poll.setInterval(POLL_MS)
        self._poll.timeout.connect(self.refresh)
        self._anim = QTimer(self)
        self._anim.setInterval(SLOW_MS)
        self._anim.timeout.connect(self.update)

    # -- ciclo de vida --------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        self._poll.start()
        self._anim.start()
        self.refresh()

    def hideEvent(self, event):
        super().hideEvent(event)
        self._poll.stop()
        self._anim.stop()

    # -- estado ---------------------------------------------------------------------------
    @property
    def celebrating(self):
        return time.monotonic() < self._celebrate_until

    @property
    def busy(self):
        return self._busy

    def refresh(self):
        """Lê o estado atual, atualiza a fase e ajusta a velocidade da animação."""
        try:
            state = self._provider() or "IDLE"
        except Exception:
            state = self._state
        now = time.monotonic()
        if state != self._state:
            if messages.finished(self._state, state):
                self._celebrate_until = now + CELEBRATE_SECONDS
            elif state != "IDLE":
                self._celebrate_until = 0.0
            self._state = state
            self._phase = messages.phase_for(state)
            self._phase_started = now
        busy = self._phase.busy
        if busy != self._busy:
            self._busy = busy
            self.busyChanged.emit(busy)
        self._anim.setInterval(FAST_MS if (busy or self.celebrating) else SLOW_MS)
        self.update()

    def current_text(self):
        """(título, frase) exibidos agora. Útil para testes e para o log."""
        if self.celebrating:
            phase = messages.Phase("done", "Análise concluída", 0, 0, "smile", False)
            tick = int((time.monotonic() - self._celebrate_until + CELEBRATE_SECONDS) / MESSAGE_SECONDS)
            return phase.title, messages.message_for(phase, tick)
        tick = int((time.monotonic() - self._phase_started) / MESSAGE_SECONDS)
        return self._phase.title, messages.message_for(self._phase, tick)

    # -- pintura --------------------------------------------------------------------------
    def paintEvent(self, event):
        from appearance import palette_for
        pal = palette_for()
        now = time.monotonic()
        t = now - self._born
        celebrate = self.celebrating
        phase = self._phase
        mood = "smile" if celebrate else phase.mood
        tone_key = "danger" if mood == "alert" else "positive" if celebrate else "accent"
        tone = QColor(pal[tone_key])
        title, message = self.current_text()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Cartão tonal com uma barra de cor à esquerda
        card = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        fill = QColor(pal["soft"])
        fill.setAlphaF(0.92)
        painter.setPen(QPen(QColor(pal["border"]), 1))
        painter.setBrush(fill)
        painter.drawRoundedRect(card, 12, 12)
        bar = QPainterPath()
        bar.addRoundedRect(QRectF(0.5, 0.5, 6, h - 1.0), 3, 3)
        painter.setPen(Qt.NoPen)
        painter.setBrush(tone)
        painter.drawPath(bar)

        # Rosto
        self._draw_face(painter, QPointF(46, h / 2.0), 22.0, mood, t, celebrate, tone)

        # Bloco da direita: espectro e etapas (só quando há espaço)
        right_width = 0
        if w >= 560:
            right_width = 230
            self._draw_spectrum(painter, QRectF(w - right_width - 6, 14, right_width - 10, 34), t, phase, tone, pal)
            self._draw_steps(painter, QRectF(w - right_width - 6, 58, right_width - 10, 22), t, phase, celebrate, tone, pal)

        # Textos
        text_left = 86
        text_width = max(60, w - text_left - right_width - 18)
        painter.setPen(QColor(pal["text"]))
        painter.setFont(make_font("ui", 15, 600))
        title_text = QFontMetrics(painter.font()).elidedText(title, Qt.ElideRight, int(text_width))
        painter.drawText(QRectF(text_left, 12, text_width, 22), Qt.AlignLeft | Qt.AlignVCenter, title_text)
        painter.setPen(QColor(pal["muted"]))
        painter.setFont(make_font("ui", 13, 400))
        painter.drawText(QRectF(text_left, 38, text_width, 44), Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, message)
        painter.end()

    def _draw_face(self, painter, center, radius, mood, t, celebrate, tone):
        painter.save()
        if celebrate:
            painter.translate(0, -bounce(t, 0.8, 4.0))
        face_fill = QColor(tone)
        face_fill.setAlphaF(0.16)
        painter.setPen(QPen(tone, 2))
        painter.setBrush(face_fill)
        painter.drawEllipse(center, radius, radius)

        eye_dx, eye_y, eye_r = radius * 0.38, center.y() - radius * 0.18, radius * 0.10
        eye_open = 1.0 - blink_amount(t)
        painter.setPen(Qt.NoPen)
        painter.setBrush(tone)
        for sign in (-1, 1):
            painter.drawEllipse(QPointF(center.x() + sign * eye_dx, eye_y), eye_r, max(0.9, eye_r * eye_open))

        curve, width_rel = mouth_params("smile" if celebrate else mood)
        half = radius * width_rel
        mouth_y = center.y() + radius * 0.26
        mouth = QPainterPath(QPointF(center.x() - half, mouth_y))
        mouth.quadTo(QPointF(center.x(), mouth_y + curve * radius * 0.78), QPointF(center.x() + half, mouth_y))
        pen = QPen(tone, 2.2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(mouth)

        if celebrate:   # três faíscas piscando ao redor
            painter.setPen(Qt.NoPen)
            for i, (dx, dy) in enumerate(((-30, -14), (30, -18), (34, 10))):
                spark = QColor(tone)
                spark.setAlphaF(pulse(t + i * 0.3, 0.9, 0.2, 0.9))
                painter.setBrush(spark)
                painter.drawEllipse(QPointF(center.x() + dx, center.y() + dy), 2.4, 2.4)
        painter.restore()

    def _draw_spectrum(self, painter, rect, t, phase, tone, pal):
        amplitude = 1.0 if phase.kind == "reading" else 0.35 if phase.busy else 0.0
        baseline = QColor(pal["border"])
        painter.setPen(QPen(baseline, 1))
        painter.drawLine(QPointF(rect.left(), rect.bottom()), QPointF(rect.right(), rect.bottom()))
        points = spectrum_points(48, t, amplitude)
        path = QPainterPath()
        for i, value in enumerate(points):
            x = rect.left() + rect.width() * i / (len(points) - 1)
            y = rect.bottom() - 2 - value * (rect.height() - 6)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        line = QColor(tone)
        line.setAlphaF(0.95 if amplitude else 0.35)
        pen = QPen(line, 2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def _draw_steps(self, painter, rect, t, phase, celebrate, tone, pal):
        total = messages.TOTAL_STEPS
        if phase.step <= 0 and not celebrate:
            painter.setPen(QColor(pal["muted"]))
            painter.setFont(make_font("ui", 11, 500))
            label = "Em repouso" if phase.kind == "idle" else "Aguarde"
            painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, label)
            return
        gap, bar_h = 6.0, 6.0
        bar_w = (rect.width() - gap * (total - 1)) / total
        painter.setPen(Qt.NoPen)
        for i in range(1, total + 1):
            x = rect.left() + (i - 1) * (bar_w + gap)
            color = QColor(tone if (celebrate or i <= phase.step) else pal["border"])
            if not celebrate and i == phase.step:
                color.setAlphaF(pulse(t))
            painter.setBrush(color)
            painter.drawRoundedRect(QRectF(x, rect.top(), bar_w, bar_h), 3, 3)
        painter.setPen(QColor(pal["muted"]))
        painter.setFont(make_font("ui", 11, 500))
        caption = "Concluída" if celebrate else f"Etapa {phase.step} de {total}"
        painter.drawText(QRectF(rect.left(), rect.top() + bar_h + 3, rect.width(), 14), Qt.AlignRight | Qt.AlignVCenter, caption)
