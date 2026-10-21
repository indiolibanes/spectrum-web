#!/usr/bin/env bash
# Inicia a bancada simulada (ESP32 falso na porta 8080) e o supervisório no display virtual.
# Uso: bash run/start_app.sh
#      QT_SCALE_FACTOR=1.25 bash run/start_app.sh   (simula escala 125% do Windows)
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
cd "$REPO_DIR"

# O display precisa estar de pé; se não estiver, sobe sozinho.
if [[ ! -S /tmp/.X11-unix/X99 ]] || ! port_open 6080; then
  c_warn "Display virtual não está ativo. Subindo agora..."
  bash "$REPO_DIR/run/start_display.sh" || exit 1
fi

source "$REPO_DIR/run/common.sh"
export DISPLAY=:99
# NoVNC usa X11; não herdar um backend Wayland/offscreen do ambiente.
export QT_QPA_PLATFORM=xcb
export QT_X11_NO_MITSHM=1
# Dados de teste isolados: não tocam nos arquivos reais de usuários e calibração.
export SPECTRUM_LAB_DATA_DIR="$REPO_DIR/run-data"
mkdir -p run-data

if ! "$PYTHON" -c "import PyQt5.QtWidgets, matplotlib, reportlab, numpy, serial" 2>/dev/null; then
  c_warn "Dependências Python ausentes; executando configuração do Codespace..."
  bash "$REPO_DIR/run/setup.sh" || { c_err "Falha ao instalar as dependências Python."; exit 1; }
  source "$REPO_DIR/run/common.sh"
  "$PYTHON" -c "import PyQt5.QtWidgets, matplotlib, reportlab, numpy, serial" || exit 1
fi

# Verifique o plugin xcb num processo separado: falhas nativas do Qt abortam o processo.
if ! "$PYTHON" run/probe_qt.py >run-data/qt.log 2>&1; then
  c_err "Qt não conseguiu abrir o display :99. Detalhes:"
  cat run-data/qt.log
  c_err "Rode bash run/setup.sh e bash run/start_display.sh."
  exit 1
fi

pkill -f "run/fake_esp32.py" 2>/dev/null || true
"$PYTHON" run/fake_esp32.py --host 127.0.0.1 --port 8080 >run-data/esp32_simulado.log 2>&1 &
SIM_PID=$!
trap 'kill $SIM_PID 2>/dev/null || true' EXIT
if wait_port 8080 8; then c_ok "ESP32 simulado em 127.0.0.1:8080"; else c_err "O simulador não respondeu na porta 8080"; tail_log run-data/esp32_simulado.log; exit 1; fi

echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null) @ $(git rev-parse --short HEAD 2>/dev/null)"
echo "Abra no navegador: $(novnc_url)"
echo "No supervisório: Conexão = Wi-Fi, IP = 127.0.0.1, Porta = 8080, depois 'Conectar ESP32'."
echo "(Log do programa: run-data/app.log)"
"$PYTHON" -u main.py 2>&1 | tee run-data/app.log
