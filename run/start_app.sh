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

export DISPLAY=:99
# Dados de teste isolados: não tocam nos arquivos reais de usuários e calibração.
export SPECTRUM_LAB_DATA_DIR="$REPO_DIR/run-data"
mkdir -p run-data

if ! python3 -c "import PyQt5.QtCore" 2>/dev/null; then
  c_err "PyQt5 não está instalado. Rode: bash run/setup.sh"; exit 1
fi

pkill -f "run/fake_esp32.py" 2>/dev/null || true
python3 run/fake_esp32.py --port 8080 >run-data/esp32_simulado.log 2>&1 &
SIM_PID=$!
trap 'kill $SIM_PID 2>/dev/null || true' EXIT
if wait_port 8080 8; then c_ok "ESP32 simulado em 0.0.0.0:8080"; else c_warn "O simulador não respondeu na porta 8080"; tail_log run-data/esp32_simulado.log; fi

echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null) @ $(git rev-parse --short HEAD 2>/dev/null)"
echo "Abra no navegador: $(novnc_url)"
echo "No supervisório: Conexão = Wi-Fi, IP = 127.0.0.1, Porta = 8080, depois 'Conectar ESP32'."
echo "(Log do programa: run-data/app.log)"
python3 main.py 2>&1 | tee run-data/app.log
