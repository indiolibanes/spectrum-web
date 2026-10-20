#!/usr/bin/env bash
# Instala dependências do sistema e do Python para rodar o supervisório no Codespace.
# Executar uma vez, a partir da raiz do repositório: bash run/setup.sh
set -euo pipefail

echo "==> Pacotes do sistema (display virtual, acesso pelo navegador e bibliotecas do Qt)"
sudo apt-get update -y
sudo apt-get install -y \
  xvfb x11vnc novnc websockify fluxbox \
  libgl1 libegl1 libxkbcommon0 libxkbcommon-x11-0 libdbus-1-3 \
  libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-xinerama0 libxcb-xkb1 libxcb-shape0 libxcb-cursor0 \
  fontconfig fonts-dejavu-core fonts-liberation file procps

echo "==> Dependências Python (sem PyInstaller, que só serve para gerar o .exe)"
python3 -m pip install --upgrade pip
grep -v -i '^pyinstaller' requirements.txt > /tmp/requirements-run.txt
python3 -m pip install -r /tmp/requirements-run.txt

echo "==> Verificação"
python3 -c "import PyQt5.QtCore as c, numpy, matplotlib, serial, reportlab; print('Qt', c.QT_VERSION_STR, '| PyQt5 OK')"
echo "Pronto. Próximo passo: bash run/start_display.sh"
