"""
Indicador de análise (ISA-101): uma faixa discreta abaixo do gráfico com o que o equipamento está fazendo.

  Título da fase · frase que se alterna                          Etapa 3 de 5  ▮▮▮▯▯

Sem rosto e sem animação decorativa. A cor só aparece quando importa: vermelha em alerta,
verde quando a análise termina e a cor de destaque do tema enquanto uma etapa está em curso.
O texto vem de analysis_messages.py (testado sem Qt).
"""
import time

from PyQt5.QtCore import QRectF, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFontMetrics, QPainter, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

import analysis_messages as messages
import glass
from typography import make_font

HEIGHT = 56
MESSAGE_SECONDS = 4.5      # tempo de cada frase
CELEBRATE_SECONDS = 7.0    # quanto tempo o "análise concluída" fica na tela
FAST_MS = 120              # atualização enquanto algo se move
SLOW_MS = 500              # em repouso
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
        celebrate = self.celebrating
        phase = self._phase
        alert = phase.mood == "alert"
        tone = QColor(pal["danger"] if alert else pal["positive"] if celebrate else pal["accent"])
        title, message = self.current_text()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Superfície plana; filete de cor apenas em alerta ou conclusão
        card = QRectF(0.5, 0.5, w - 1.0, h - 1.0)
        painter.setPen(QPen(QColor(tone if alert else glass.rim(pal)), 1))
        painter.setBrush(QColor(pal["soft"]))
        painter.drawRoundedRect(card, 8, 8)
        if alert or celebrate:
            painter.setPen(Qt.NoPen)
            painter.setBrush(tone)
            painter.drawRoundedRect(QRectF(0.5, 6, 4, h - 12), 2, 2)

        # Etapas à direita (só quando há espaço)
        right_width = 0
        if w >= 520:
            right_width = 190
            self._draw_steps(painter, QRectF(w - right_width - 12, 10, right_width, h - 20), phase, celebrate, tone, pal)

        left, text_width = 16, max(60, w - 16 - right_width - 28)
        painter.setPen(QColor(pal["heading"]))
        painter.setFont(make_font("ui", 13, 700))
        title_text = QFontMetrics(painter.font()).elidedText(title, Qt.ElideRight, int(text_width))
        painter.drawText(QRectF(left, 6, text_width, 22), Qt.AlignLeft | Qt.AlignVCenter, title_text)
        painter.setPen(QColor(pal["muted"]))
        painter.setFont(make_font("ui", 11, 400))
        message_text = QFontMetrics(painter.font()).elidedText(message, Qt.ElideRight, int(text_width))
        painter.drawText(QRectF(left, 28, text_width, 20), Qt.AlignLeft | Qt.AlignVCenter, message_text)
        painter.end()

    def _draw_steps(self, painter, rect, phase, celebrate, tone, pal):
        total = messages.TOTAL_STEPS
        painter.setFont(make_font("ui", 11, 400))
        if phase.step <= 0 and not celebrate:
            painter.setPen(QColor(pal["muted"]))
            painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, "Em repouso" if phase.kind == "idle" else "Aguarde")
            return
        gap, bar_h = 5.0, 6.0
        bar_w = (rect.width() - gap * (total - 1)) / total
        painter.setPen(Qt.NoPen)
        top = rect.top() + 4
        for i in range(1, total + 1):
            x = rect.left() + (i - 1) * (bar_w + gap)
            done = celebrate or i <= phase.step
            painter.setBrush(QColor(tone if done else pal["border"]))
            painter.drawRoundedRect(QRectF(x, top, bar_w, bar_h), 3, 3)
        painter.setPen(QColor(pal["muted"]))
        caption = "Concluída" if celebrate else f"Etapa {phase.step} de {total}"
        painter.drawText(QRectF(rect.left(), top + bar_h + 2, rect.width(), 16), Qt.AlignRight | Qt.AlignVCenter, caption)
