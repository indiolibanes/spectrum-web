"""
Emojis e ícones coloridos desenhados à mão (vetor), iguais em qualquer sistema.

O gerenciador de temas remove emojis de texto (as fontes de emoji variam entre Windows, Linux e o
noVNC, e em vários casos saem como caixas ou em preto e branco). Por isso os "emojis" do programa
são desenhados aqui com QPainter: rosto de feedback do indicador de análise e ícones dos
indicadores (raio, tendência, folha, gota). As cores são as de um emoji, nos dois temas.
"""
import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QLinearGradient, QPainterPath, QPen, QRadialGradient
from PyQt5.QtWidgets import QSizePolicy, QWidget

from animation_math import blink_amount, mouth_params, pulse

OUTLINE = QColor(140, 80, 0, 190)
EYE = QColor("#4A2B00")
FACE_HAPPY = ("#FFF0A0", "#FFD23F", "#F2A20C")
FACE_ALERT = ("#FFD9A0", "#FFA040", "#E0590C")
SPARKS = ("#FFD23F", "#FF7A9C", "#52B6FF", "#6BD38A")


def _q(color, alpha=None):
    out = QColor(color)
    if alpha is not None:
        out.setAlphaF(alpha)
    return out


def _star(painter, center, size):
    path = QPainterPath()
    for i in range(8):
        angle = math.pi / 4 * i - math.pi / 2
        radius = size if i % 2 == 0 else size * 0.28
        point = QPointF(center.x() + math.cos(angle) * radius, center.y() + math.sin(angle) * radius)
        path.moveTo(point) if i == 0 else path.lineTo(point)
    path.closeSubpath()
    painter.drawPath(path)


def draw_face(painter, center, radius, mood, t, celebrate=False):
    """Rosto de emoji: 'calm' (🙂), 'smile' (😊), celebrando (😄 com faíscas) e 'alert' (😟 com gota de suor)."""
    painter.save()
    cx, cy = center.x(), center.y()
    alert = mood == "alert" and not celebrate
    light, mid, deep = FACE_ALERT if alert else FACE_HAPPY

    gradient = QRadialGradient(QPointF(cx - radius * 0.30, cy - radius * 0.38), radius * 1.45)
    gradient.setColorAt(0.0, QColor(light))
    gradient.setColorAt(0.55, QColor(mid))
    gradient.setColorAt(1.0, QColor(deep))
    painter.setPen(QPen(OUTLINE, max(1.2, radius * 0.07)))
    painter.setBrush(gradient)
    painter.drawEllipse(center, radius, radius)

    # brilho no alto da testa
    shine = QLinearGradient(cx, cy - radius, cx, cy - radius * 0.2)
    shine.setColorAt(0.0, _q("#FFFFFF", 0.50))
    shine.setColorAt(1.0, _q("#FFFFFF", 0.0))
    painter.setPen(Qt.NoPen)
    painter.setBrush(shine)
    painter.drawEllipse(QRectF(cx - radius * 0.62, cy - radius * 0.94, radius * 1.24, radius * 0.80))

    eye_dx, eye_y = radius * 0.38, cy - radius * 0.14
    if celebrate or mood == "smile":
        # bochechas
        painter.setBrush(_q("#FF5C7A", 0.38))
        for sign in (-1, 1):
            painter.drawEllipse(QPointF(cx + sign * radius * 0.60, cy + radius * 0.22), radius * 0.17, radius * 0.11)

    if celebrate:   # olhos felizes "^ ^"
        pen = QPen(EYE, max(1.6, radius * 0.10))
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        for sign in (-1, 1):
            path = QPainterPath(QPointF(cx + sign * eye_dx - radius * 0.13, eye_y + radius * 0.06))
            path.quadTo(QPointF(cx + sign * eye_dx, eye_y - radius * 0.22), QPointF(cx + sign * eye_dx + radius * 0.13, eye_y + radius * 0.06))
            painter.drawPath(path)
    else:
        open_ratio = 1.0 - blink_amount(t)
        for sign in (-1, 1):
            ex = cx + sign * eye_dx
            painter.setPen(Qt.NoPen)
            painter.setBrush(EYE)
            painter.drawEllipse(QPointF(ex, eye_y), radius * 0.075, max(0.9, radius * 0.115 * open_ratio))
            if open_ratio > 0.5:
                painter.setBrush(_q("#FFFFFF", 0.9))
                painter.drawEllipse(QPointF(ex - radius * 0.025, eye_y - radius * 0.04), radius * 0.025, radius * 0.025)
        if alert:       # sobrancelhas preocupadas
            pen = QPen(EYE, max(1.4, radius * 0.07))
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            for sign in (-1, 1):
                painter.drawLine(QPointF(cx + sign * eye_dx - sign * radius * 0.16, eye_y - radius * 0.30),
                                 QPointF(cx + sign * eye_dx + sign * radius * 0.14, eye_y - radius * 0.40))

    curve, width_rel = mouth_params("smile" if celebrate else mood)
    half = radius * width_rel
    mouth_y = cy + radius * 0.34
    if celebrate:   # boca aberta com língua
        mouth = QPainterPath(QPointF(cx - half, mouth_y - radius * 0.06))
        mouth.quadTo(QPointF(cx, mouth_y + radius * 0.80), QPointF(cx + half, mouth_y - radius * 0.06))
        mouth.closeSubpath()
        painter.setPen(QPen(OUTLINE, max(1.0, radius * 0.05)))
        painter.setBrush(QColor("#7A2A12"))
        painter.drawPath(mouth)
        painter.save()
        painter.setClipPath(mouth)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#FF7B8A"))
        painter.drawEllipse(QPointF(cx, mouth_y + radius * 0.50), half * 0.55, radius * 0.22)
        painter.restore()
    else:
        pen = QPen(EYE, max(1.6, radius * 0.09))
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        mouth = QPainterPath(QPointF(cx - half, mouth_y))
        mouth.quadTo(QPointF(cx, mouth_y + curve * radius * 0.62), QPointF(cx + half, mouth_y))
        painter.drawPath(mouth)

    if alert:       # gota de suor
        drop = QPainterPath(QPointF(cx + radius * 0.70, cy - radius * 0.62))
        drop.quadTo(QPointF(cx + radius * 0.92, cy - radius * 0.28), QPointF(cx + radius * 0.70, cy - radius * 0.14))
        drop.quadTo(QPointF(cx + radius * 0.48, cy - radius * 0.28), QPointF(cx + radius * 0.70, cy - radius * 0.62))
        painter.setPen(QPen(_q("#1F78C8", 0.8), 1))
        painter.setBrush(QColor("#7CCBFF"))
        painter.drawPath(drop)

    if celebrate:   # faíscas coloridas
        painter.setPen(Qt.NoPen)
        spots = ((-1.55, -0.55, 0.20), (1.55, -0.70, 0.24), (1.62, 0.45, 0.17), (-1.35, 0.62, 0.15))
        for i, (dx, dy, size) in enumerate(spots):
            spark = _q(SPARKS[i % len(SPARKS)], pulse(t + i * 0.27, 0.9, 0.35, 1.0))
            painter.setBrush(spark)
            _star(painter, QPointF(cx + dx * radius, cy + dy * radius), size * radius * 1.6)
    painter.restore()


# ---- ícones dos indicadores --------------------------------------------------------------
def _gradient(rect, top, bottom):
    g = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
    g.setColorAt(0.0, QColor(top))
    g.setColorAt(1.0, QColor(bottom))
    return g


def draw_glyph(painter, rect, kind):
    """Desenha um ícone colorido dentro de rect. kind: bolt, trend, leaf ou drop."""
    painter.save()
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

    def pt(u, v):
        return QPointF(x + u * w, y + v * h)

    painter.setPen(QPen(_q("#7A4A00", 0.65), max(1.0, w * 0.045)))
    if kind == "bolt":
        path = QPainterPath(pt(0.58, 0.04))
        for u, v in ((0.20, 0.54), (0.46, 0.54), (0.38, 0.96), (0.80, 0.40), (0.54, 0.40), (0.58, 0.04)):
            path.lineTo(pt(u, v))
        painter.setBrush(_gradient(rect, "#FFE867", "#FF9A1F"))
        painter.drawPath(path)
    elif kind == "trend":
        body = QRectF(x + w * 0.04, y + h * 0.04, w * 0.92, h * 0.92)
        painter.setPen(QPen(_q("#4B2FA8", 0.7), max(1.0, w * 0.045)))
        painter.setBrush(_gradient(body, "#C3B2FF", "#7557E6"))
        painter.drawRoundedRect(body, w * 0.24, w * 0.24)
        line = QPen(QColor("#FFFFFF"), max(1.6, w * 0.10))
        line.setCapStyle(Qt.RoundCap)
        line.setJoinStyle(Qt.RoundJoin)
        painter.setPen(line)
        painter.setBrush(Qt.NoBrush)
        path = QPainterPath(pt(0.20, 0.68))
        for u, v in ((0.40, 0.46), (0.54, 0.58), (0.78, 0.28)):
            path.lineTo(pt(u, v))
        painter.drawPath(path)
        painter.drawLine(pt(0.78, 0.28), pt(0.78, 0.46))
        painter.drawLine(pt(0.78, 0.28), pt(0.60, 0.28))
    elif kind == "leaf":
        path = QPainterPath(pt(0.12, 0.88))
        path.cubicTo(pt(0.02, 0.40), pt(0.36, 0.06), pt(0.92, 0.08))
        path.cubicTo(pt(0.94, 0.62), pt(0.60, 0.96), pt(0.12, 0.88))
        painter.setPen(QPen(_q("#1D6B33", 0.8), max(1.0, w * 0.045)))
        painter.setBrush(_gradient(rect, "#9BEA6B", "#2FA84F"))
        painter.drawPath(path)
        vein = QPen(_q("#1D6B33", 0.8), max(1.0, w * 0.06))
        vein.setCapStyle(Qt.RoundCap)
        painter.setPen(vein)
        painter.drawLine(pt(0.16, 0.84), pt(0.68, 0.34))
    elif kind == "drop":
        path = QPainterPath(pt(0.50, 0.04))
        path.cubicTo(pt(0.50, 0.04), pt(0.90, 0.46), pt(0.90, 0.64))
        path.cubicTo(pt(0.90, 0.86), pt(0.72, 0.96), pt(0.50, 0.96))
        path.cubicTo(pt(0.28, 0.96), pt(0.10, 0.86), pt(0.10, 0.64))
        path.cubicTo(pt(0.10, 0.46), pt(0.50, 0.04), pt(0.50, 0.04))
        painter.setPen(QPen(_q("#14609F", 0.8), max(1.0, w * 0.045)))
        painter.setBrush(_gradient(rect, "#A6E6FF", "#2B8DE8"))
        painter.drawPath(path)
        painter.setPen(Qt.NoPen)
        painter.setBrush(_q("#FFFFFF", 0.65))
        painter.drawEllipse(QRectF(x + w * 0.27, y + h * 0.52, w * 0.12, h * 0.20))
    painter.restore()


class GlyphIcon(QWidget):
    """Ícone colorido de tamanho fixo (ver draw_glyph)."""
    KINDS = ("bolt", "trend", "leaf", "drop")

    def __init__(self, kind, size=24, parent=None):
        super().__init__(parent)
        self.kind = kind if kind in self.KINDS else "bolt"
        self.setFixedSize(size, size)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAccessibleName("Ícone")

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        draw_glyph(painter, QRectF(1, 1, self.width() - 2, self.height() - 2), self.kind)
        painter.end()
