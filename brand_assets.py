"""Marcas institucionais obtidas nos sites oficiais, incluídas no executável."""
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
    pix=QPixmap(width*2,height*2);pix.fill(Qt.white)
    renderer=QSvgRenderer(str(resource_path(name+'.svg')))
    if not renderer.isValid():return QPixmap()
    size=renderer.defaultSize();size.scale(width*2-12,height*2-12,Qt.KeepAspectRatio)
    painter=QPainter(pix)
    from PyQt5.QtCore import QRectF
    renderer.render(painter,QRectF((pix.width()-size.width())/2,(pix.height()-size.height())/2,size.width(),size.height()))
    painter.end();pix.setDevicePixelRatio(2)
    return pix

def institutional_signature(parent=None):
    box=QWidget(parent);layout=QHBoxLayout(box);layout.setContentsMargins(0,0,0,0);layout.setSpacing(18)
    for name in ('senai','arauco'):
        label=QLabel();label.setObjectName('institution_'+name);label.setPixmap(logo_pixmap(name));label.setToolTip(name.upper())
        layout.addWidget(label)
    return box
