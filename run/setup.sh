#!/usr/bin/env bash
# Instala dependências do sistema e do Python para rodar o supervisório no Codespace.
# Executar uma vez, a partir da raiz do repositório: bash run/setup.sh
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
cd "$REPO_DIR"
if (( EUID == 0 )); then
  SUDO=()
else
  SUDO=(sudo)
fi

echo "==> Pacotes do sistema (display virtual, acesso pelo navegador e bibliotecas do Qt)"
# Uma fonte extra (por exemplo Yarn) pode falhar por assinatura ausente.
# Isso não deve impedir a instalação das dependências do projeto presentes
# nos repositórios Debian autenticados. Não ignorar verificação GPG nem usar
# --allow-unauthenticated; apt-get install permanece estrito.
if ! "${SUDO[@]}" apt-get update -y; then
  echo "AVISO: apt-get update não terminou (possível repositório externo, como Yarn)."
  echo "Tentando instalar dependências apenas a partir das fontes autenticadas já disponíveis."
fi
"${SUDO[@]}" apt-get install -y \
  python3-venv xvfb x11-utils x11vnc novnc websockify fluxbox xdg-utils \
  libgl1 libegl1 libxkbcommon0 libxkbcommon-x11-0 libdbus-1-3 \
  libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-xinerama0 libxcb-xkb1 libxcb-shape0 libxcb-cursor0 \
  fontconfig fonts-dejavu-core fonts-liberation file procps

echo "==> Dependências Python (sem PyInstaller, que só serve para gerar o .exe)"
if [[ -z "${SPECTRUM_PYTHON:-}" ]]; then
  python3 -m venv "$REPO_DIR/.venv"
  PYTHON="$REPO_DIR/.venv/bin/python"
fi
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r "$REPO_DIR/requirements.txt"

echo "==> Verificação"
"$PYTHON" -c "import PyQt5.QtCore as c, numpy, matplotlib, serial, reportlab; print('Qt', c.QT_VERSION_STR, '| PyQt5 OK')"
echo "Pronto. Próximo passo: bash run/start_app.sh"
