#!/usr/bin/env bash
# Encerra tudo que os scripts de run/ iniciaram.
pkill -f "run/fake_esp32.py" 2>/dev/null
pkill -f "python3 main.py" 2>/dev/null
pkill -x fluxbox 2>/dev/null
pkill -x websockify 2>/dev/null
pkill -x x11vnc 2>/dev/null
pkill -x Xvfb 2>/dev/null
echo "Encerrado."
