#!/usr/bin/env bash
# Sobe o display virtual e o acesso pelo navegador (noVNC na porta 6080) e mostra o endereço para abrir.
# Uso: bash run/start_display.sh                       (1920x1080)
#      RESOLUTION=1366x768 bash run/start_display.sh
set -uo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
RES="${RESOLUTION:-1920x1080}"

echo "==> Conferindo ferramentas"
missing=0
need Xvfb xvfb || missing=1
need x11vnc x11vnc || missing=1
need websockify websockify || missing=1
need fluxbox fluxbox || missing=1
NOVNC="$(novnc_dir)" || { c_err "noVNC não encontrado (pacote novnc). Rode: bash run/setup.sh"; missing=1; }
[[ "$missing" == 1 ]] && exit 1
c_ok "Xvfb, x11vnc, websockify, fluxbox e noVNC (${NOVNC})"

echo "==> Encerrando uma execução anterior"
pkill -x Xvfb 2>/dev/null || true
pkill -x x11vnc 2>/dev/null || true
pkill -x websockify 2>/dev/null || true
pkill -x fluxbox 2>/dev/null || true
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
sleep 1

echo "==> Iniciando o display ${RES}"
setsid nohup Xvfb :99 -screen 0 "${RES}x24" -ac +extension GLX +render -noreset >"$LOG_DIR/xvfb.log" 2>&1 &
for _ in $(seq 1 20); do [[ -S /tmp/.X11-unix/X99 ]] && break; sleep 0.5; done
if [[ ! -S /tmp/.X11-unix/X99 ]]; then c_err "O display :99 não subiu."; tail_log "$LOG_DIR/xvfb.log"; exit 1; fi
c_ok "Display :99 pronto"

export DISPLAY=:99
setsid nohup fluxbox >"$LOG_DIR/fluxbox.log" 2>&1 &
# -localhost: só o noVNC (nesta máquina) fala com o x11vnc. Nada de VNC aberto sem senha na rede.
setsid nohup x11vnc -display :99 -forever -shared -nopw -localhost -cursor most -quiet -rfbport 5900 >"$LOG_DIR/x11vnc.log" 2>&1 &
if ! wait_port 5900 15; then c_err "O x11vnc não abriu a porta 5900."; tail_log "$LOG_DIR/x11vnc.log"; exit 1; fi
c_ok "x11vnc na porta 5900 (somente local)"

setsid nohup websockify --web "$NOVNC" 6080 localhost:5900 >"$LOG_DIR/websockify.log" 2>&1 &
if ! wait_port 6080 15; then c_err "O noVNC não abriu a porta 6080."; tail_log "$LOG_DIR/websockify.log"; exit 1; fi
c_ok "noVNC na porta 6080"

echo
echo "Pronto. Abra este endereço no navegador em que você está logado no GitHub:"
echo
echo "    $(novnc_url)"
echo
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  echo "Se aparecer erro 502 ou 404: aguarde 10 s e atualize a página; confira a aba PORTS (porta 6080 deve"
  echo "estar listada, visibilidade Private). Não é preciso torná-la Public: a área de trabalho não tem senha."
else
  echo "Fora do Codespaces o endereço acima só funciona nesta própria máquina."
fi
echo "Próximo passo: bash run/start_app.sh      (diagnóstico: bash run/check.sh)"
