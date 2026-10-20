#!/usr/bin/env bash
# Sobe o display virtual e o acesso pelo navegador (noVNC na porta 6080).
# Uso: bash run/start_display.sh               (1920x1080)
#      RESOLUTION=1366x768 bash run/start_display.sh
set -euo pipefail
RES="${RESOLUTION:-1920x1080}"

pkill -f "Xvfb :99" 2>/dev/null || true
pkill -f "x11vnc.*5900" 2>/dev/null || true
pkill -f "websockify.*6080" 2>/dev/null || true
sleep 1

Xvfb :99 -screen 0 "${RES}x24" -ac +extension GLX +render -noreset >/tmp/xvfb.log 2>&1 &
sleep 2
export DISPLAY=:99
fluxbox >/tmp/fluxbox.log 2>&1 &
x11vnc -display :99 -forever -shared -nopw -quiet -rfbport 5900 >/tmp/x11vnc.log 2>&1 &
websockify --web /usr/share/novnc 6080 localhost:5900 >/tmp/websockify.log 2>&1 &
sleep 2

echo "Display virtual: ${RES} (DISPLAY=:99)"
echo "Abra a porta 6080 na aba PORTS do Codespace e acesse /vnc.html."
