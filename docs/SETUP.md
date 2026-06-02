# Orbit — Setup

Install, configure, and run Orbit. For *how to drive the agent loop* once it's
up, see **[USAGE.md](USAGE.md)**.

## Prerequisites

- **Docker + Docker Compose** (the one-command path), **or** **Python 3.12+** for local mode.
- An **OpenAI-compatible LLM endpoint + key** — OpenAI, OpenRouter, a LiteLLM
  proxy, or a local server (vLLM / Ollama with an OpenAI shim).
- A **Bloomreach Engagement sandbox** project with a **Project Token**, **API Key**,
  and **API Secret**:
  - *Engagement → Project settings* → the **Project Token**.
  - *Data & Assets → Access Management → API* → the **API Key + Secret** (HTTP Basic).
  - The sandbox is invite / CSM-gated — you must already have access. Orbit uses
    **sandbox / synthetic data only**.
- A **Loomi Connect** login (read-only). Authenticated in-app via browser OAuth —
  see [Connecting Loomi](#connecting-loomi-read-only). No env var, no secret in the repo.

## Clone & configure

```bash
git clone https://github.com/Skilux/orbit-agent.git
cd orbit-agent
cp .env.example .env          # then fill it in — see Environment variables below
```

## Run mode A — Docker (recommended)

```bash
# macOS/Linux: set your real uid/gid so the named volume stays writable
echo "UID=$(id -u)"  >> .env
echo "GID=$(id -g)"  >> .env   # macOS is often 501 / 20, not 1000

docker compose up --build
open http://localhost:8787
```

Two containers come up on a shared network:

| Service | Port | What it is |
| --- | --- | --- |
| `hermes-webui` | 8787 | Hermes agent runtime **+** web UI (the agent runs in-process) |
| `bloomreach-mcp` | 8000 | the custom Bloomreach Engagement **write**-MCP |

Compose loads `.env` into both services and overrides `BLOOMREACH_MCP_URL` to the
in-network service name (`http://bloomreach-mcp:8000/mcp`) automatically — don't
set that one yourself for Docker.

## Run mode B — Local, no Docker

Runs the agent directly on the host so it operates on **this repo's real files**
as its workspace (useful for editing `agent/`, scenarios, templates live):

```bash
cp .env.example .env          # fill in credentials
./run-local.sh                # starts bloomreach-mcp (:8000) + Hermes WebUI (:8787)
open http://localhost:8787
```

`run-local.sh` sources `.env`, creates a Python venv for the MCP, installs
`requirements.txt`, runs the MCP on `127.0.0.1:8000`, and launches Hermes with
`HERMES_HOME=./hermes/.hermes` and the workspace set to the repo root. Ctrl-C
stops both. (Docker and local differ only in `BLOOMREACH_MCP_URL`, which each
mode sets automatically.)

## Configuring the LLM model

Orbit's Hermes profile reads three env vars from the root `.env`:

```bash
OPENAI_API_KEY=...                          # your key
OPENAI_BASE_URL=https://api.openai.com/v1   # any OpenAI-compatible endpoint
OPENAI_MODEL=gpt-4o                          # model name
```

These map straight to the `model` block in
`hermes/.hermes/profiles/orbit/config.yaml` (`provider: custom`, `base_url`,
`api_key`, `default`). **Any OpenAI-compatible endpoint works** — just point
`OPENAI_BASE_URL` at it and set a matching `OPENAI_MODEL`.

Prefer interactive setup? Run `hermes model` to pick/configure a provider; it
writes back to the same profile config. (Commented-out fallback providers —
OpenRouter, Bedrock, etc. — live at the bottom of `config.yaml`.)

## Connecting Loomi (read-only)

Loomi Connect is a **remote** MCP authenticated with **browser OAuth** — there is
no Loomi key in this repo. On first use, the Hermes UI walks you through a browser
authorization for the `loomi` MCP; the resulting token is cached under
`hermes/.hermes/profiles/orbit/mcp-tokens/` (gitignored, never committed).

- A fresh clone has **no token** — you must authorize once before discovery works.
- Tokens are **short-lived** (≈1 hour observed). If discovery suddenly stops
  returning data, re-authorize.
- The endpoint comes from `LOOMI_MCP_URL` in `.env`
  (`https://loomi-mcp-alpha.bloomreach.com/mcp`, **no trailing slash**).

## Running the custom MCP server standalone

The write-path MCP (`mcp/bloomreach-engagement-mcp/`, Python / FastMCP, Streamable
HTTP) can run on its own:

```bash
cd mcp/bloomreach-engagement-mcp
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env           # fill BR_PROJECT_TOKEN, BR_API_KEY, BR_API_SECRET
python server.py               # serves on http://0.0.0.0:8000
```

- **MCP endpoint:** `http://localhost:8000/mcp`
- **Health check:** `curl http://localhost:8000/health` → `OK`
- **stdio transport** (e.g. Claude Desktop): `MCP_TRANSPORT=stdio python server.py`

**Tools exposed (4):**

| Tool | Mode | Purpose |
| --- | --- | --- |
| `set_customer_property` | async (queued) | write/update attributes on a customer profile |
| `trigger_scenario` | async (queued) | fire an event that activates a **pre-built** Bloomreach scenario |
| `read_customer_events` | sync | read stored events (monitoring / verification) |
| `read_customer_attributes` | sync | read stored attributes (write verification) |

> Writes are **asynchronous**: HTTP 200 means *queued*, not committed. Wait 1–2 s
> before verifying with a read tool. `trigger_scenario` only does something if a
> scenario with a matching event-trigger node already exists in the Bloomreach UI.

## Environment variables

Copy `.env.example` → `.env` (gitignored) and fill it in. Three groups: **LLM**
(agent), **Bloomreach sandbox** (write-MCP), and **MCP wiring**. Loomi needs **no**
env var beyond its URL — it authenticates via browser OAuth (above).

| Var | Required? | Used by | Purpose | Example |
| --- | --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes¹ | Hermes agent | LLM auth | `sk-…` |
| `OPENAI_BASE_URL` | Yes | Hermes agent | LLM endpoint (OpenAI-compatible) | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | Yes | Hermes agent | model name | `gpt-4o` |
| `BR_PROJECT_TOKEN` | Yes | bloomreach-mcp | Engagement project token (in every REST URL) | *Project settings* |
| `BR_API_KEY` | Yes | bloomreach-mcp | HTTP Basic Auth user | *Access Mgmt → API* |
| `BR_API_SECRET` | Yes | bloomreach-mcp | HTTP Basic Auth password | *Access Mgmt → API* |
| `BR_BASE_TRACK` | No (default) | bloomreach-mcp | Track API base | `https://api.exponea.com/track/v2` |
| `BR_BASE_DATA` | No (default) | bloomreach-mcp | Data API base | `https://api.exponea.com/data/v2` |
| `MCP_HOST` | No (default `0.0.0.0`) | bloomreach-mcp | bind host | `0.0.0.0` |
| `MCP_PORT` | No (default `8000`) | bloomreach-mcp | listen port | `8000` |
| `MCP_TRANSPORT` | No (default `http`) | bloomreach-mcp | `http` or `stdio` | `http` |
| `BLOOMREACH_MCP_URL` | Yes (auto) | Hermes agent | where the agent reaches the write-MCP | local `http://localhost:8000/mcp` · docker `http://bloomreach-mcp:8000/mcp` |
| `LOOMI_MCP_URL` | Yes | Hermes agent | Loomi endpoint (no trailing slash) | `https://loomi-mcp-alpha.bloomreach.com/mcp` |
| `UID` / `GID` | Docker only | docker-compose | named-volume file ownership | macOS: `id -u` / `id -g` |

¹ Required unless you configure a different provider via `hermes model`.

---

Stuck? See the **[Troubleshooting / FAQ in USAGE.md](USAGE.md#faq--troubleshooting)**.
