#!/usr/bin/env bash
# Funções compartilhadas pelos scripts de run/. Não é para executar diretamente.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${LOG_DIR:-/tmp/spectrum-run}"
mkdir -p "$LOG_DIR"

c_ok()   { printf '\033[32m✔\033[0m %s\n' "$*"; }
c_warn() { printf '\033[33m!\033[0m %s\n' "$*"; }
c_err()  { printf '\033[31m✘\033[0m %s\n' "$*" >&2; }

# port_open PORTA -> 0 se algo está escutando em 127.0.0.1:PORTA
port_open() { (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }

# wait_port PORTA SEGUNDOS
wait_port() {
  local port="$1" limit="${2:-20}" i
  for ((i = 0; i < limit * 2; i++)); do
    port_open "$port" && return 0
    sleep 0.5
  done
  return 1
}

# novnc_dir -> imprime a pasta do noVNC que contém vnc.html
novnc_dir() {
  local d
  for d in /usr/share/novnc /opt/novnc; do
    [[ -f "$d/vnc.html" ]] && { echo "$d"; return 0; }
  done
  return 1
}

# novnc_url -> endereço para abrir no navegador (Codespaces ou local)
novnc_url() {
  local path="vnc.html?autoconnect=1&resize=remote&path=websockify"
  if [[ -n "${CODESPACE_NAME:-}" ]]; then
    echo "https://${CODESPACE_NAME}-6080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}/${path}"
  else
    echo "http://localhost:6080/${path}"
  fi
}

# tail_log ARQUIVO
tail_log() { [[ -s "$1" ]] && { echo "--- $1 (últimas linhas) ---"; tail -n 12 "$1"; echo "---"; }; }

# need COMANDO PACOTE
need() {
  command -v "$1" >/dev/null 2>&1 || { c_err "Falta o comando '$1' (pacote $2). Rode: bash run/setup.sh"; return 1; }
}

# Use o mesmo interpretador na instalação, no diagnóstico e na aplicação.
if [[ -n "${SPECTRUM_PYTHON:-}" ]]; then
  PYTHON="$SPECTRUM_PYTHON"
elif [[ -x "$REPO_DIR/.venv/bin/python" ]]; then
  PYTHON="$REPO_DIR/.venv/bin/python"
else
  PYTHON=python3
fi
