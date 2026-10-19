"""Marcas institucionais em SVG (assets/brands), com fundo transparente e proporção preservada."""
import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QWidget,QHBoxLayout,QLabel

def resource_path(name):
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'assets'/'brands'/name

def program_logo_path():
    """Marca do próprio programa (SPECTRUM-LAB PRO), em assets/logo."""
    return Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))/'assets'/'logo'/'spectrumlab-mark.svg'

def program_logo_pixmap(size=48):
    """Marca do programa em tamanho lógico 'size', nítida em telas de alta densidade."""
    renderer=QSvgRenderer(str(program_logo_path()))
    if not renderer.isValid():return QPixmap()
    dpr=2
    pix=QPixmap(int(size*dpr),int(size*dpr));pix.fill(Qt.transparent)
    painter=QPainter(pix);renderer.render(painter,QRectF(0,0,size*dpr,size*dpr));painter.end()
    pix.setDevicePixelRatio(dpr)
    return pix

def program_icon():
    """Ícone da janela e da barra de tarefas."""
    return QIcon(str(program_logo_path()))

def logo_pixmap(name,width=100,height=28):
    """Logo da marca 'name' ajustado dentro de width x height (lógicos), sem fundo."""
    renderer=QSvgRenderer(str(resource_path(name+'.svg')))
    if not renderer.isValid():return QPixmap()
    view=renderer.defaultSize()
    scale=min(width/view.width(),height/view.height())
    w,h=view.width()*scale,view.height()*scale
    dpr=2
    pix=QPixmap(int(round(w*dpr)),int(round(h*dpr)));pix.fill(Qt.transparent)
    painter=QPainter(pix);renderer.render(painter,QRectF(0,0,w*dpr,h*dpr));painter.end()
    pix.setDevicePixelRatio(dpr)
    return pix

def institutional_signature(parent=None):
    box=QWidget(parent);layout=QHBoxLayout(box);layout.setContentsMargins(0,0,0,0);layout.setSpacing(18)
    for name,tip in (('senai','SENAI'),('arauco-sucuriu','ARAUCO · Projeto Sucuriú')):
        label=QLabel();label.setObjectName('institution_'+name);label.setPixmap(logo_pixmap(name,168,28));label.setToolTip(tip)
        layout.addWidget(label)
    return box
