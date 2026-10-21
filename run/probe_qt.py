"""Confirma que QtWidgets e o plugin gráfico funcionam antes de abrir o SCADA."""
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv[:1])
window = QLabel("SPECTRUM: display OK")
window.show()
QTimer.singleShot(100, app.quit)
app.exec_()
print("Qt OK:", app.platformName())
