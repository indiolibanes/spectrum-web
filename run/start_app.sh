#!/usr/bin/env bash
# Inicia a bancada simulada (ESP32 falso na porta 8080) e o supervisório no display virtual.
# Uso: bash run/start_app.sh
#      QT_SCALE_FACTOR=1.25 bash run/start_app.sh   (simula escala 125% do Windows)
set -euo pipefail
cd "$(dirname "$0")/.."

export DISPLAY=:99
# Dados de teste isolados: não tocam nos arquivos reais de usuários e calibração.
export SPECTRUM_LAB_DATA_DIR="$PWD/run-data"
mkdir -p run-data

pkill -f "run/fake_esp32.py" 2>/dev/null || true
python3 run/fake_esp32.py --port 8080 >run-data/esp32_simulado.log 2>&1 &
SIM_PID=$!
trap 'kill $SIM_PID 2>/dev/null || true' EXIT
sleep 1

echo "ESP32 simulado: 0.0.0.0:8080 (log em run-data/esp32_simulado.log)"
echo "No supervisório: Conexão = Wi-Fi, IP = 127.0.0.1, Porta = 8080, depois 'Conectar ESP32'."
python3 main.py
