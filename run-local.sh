#!/usr/bin/env bash
# Orbit — run locally (no Docker).
#
# Runs the Hermes agent + UI directly on the host so the agent operates on
# THIS repo's real files (agent/, docs/, scenarios, …) as its workspace,
# instead of an isolated container workspace. Starts two local processes:
#   1. bloomreach-mcp   (Python, :8000)
#   2. Hermes WebUI     (agent in-process + UI, :8787)
#
# Usage:
#   cp .env.example .env   # fill in credentials
#   ./run-local.sh
#   open http://localhost:8787
#
# Ctrl-C stops both. Requires python3.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

[ -f .env ] || { echo "[!] No .env — copy .env.example to .env and fill it in."; exit 1; }
set -a; . ./.env; set +a

# Local run talks to the MCP on localhost, not the docker service name.
export BLOOMREACH_MCP_URL="${BLOOMREACH_MCP_URL:-http://localhost:8000/mcp}"
case "$BLOOMREACH_MCP_URL" in
  *bloomreach-mcp*) export BLOOMREACH_MCP_URL="http://localhost:${MCP_PORT:-8000}/mcp" ;;
esac

PIDS=()
cleanup() { echo; echo "[*] Stopping…"; for p in "${PIDS[@]:-}"; do kill "$p" 2>/dev/null || true; done; }
trap cleanup EXIT INT TERM

# ── 1. bloomreach MCP ───────────────────────────────────────────────
echo "[*] Starting bloomreach-mcp on 127.0.0.1:${MCP_PORT:-8000} …"
pushd mcp/bloomreach-engagement-mcp >/dev/null
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q -r requirements.txt
MCP_HOST=127.0.0.1 MCP_PORT="${MCP_PORT:-8000}" ./.venv/bin/python server.py &
PIDS+=($!)
popd >/dev/null

# ── 2. Hermes WebUI (agent + UI), workspace = this repo ─────────────
echo "[*] Starting Hermes WebUI on :8787 (workspace: $ROOT) …"
export HERMES_HOME="$ROOT/hermes/.hermes"
export HERMES_WEBUI_DEFAULT_WORKSPACE="${HERMES_WEBUI_DEFAULT_WORKSPACE:-$ROOT}"
cd hermes/ui
./start.sh &
PIDS+=($!)

echo "[*] Up. Open http://localhost:8787  (Ctrl-C to stop both)"
wait
