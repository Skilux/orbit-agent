# Bloomreach Engagement MCP Server

A minimal, production-ready MCP server wrapping the Bloomreach Engagement API. Exposes four endpoints (set customer properties, trigger scenarios, read events, read attributes) as LLM-callable tools over Streamable HTTP transport.

Built with **FastMCP** and **httpx**. Fully containerized with Docker.

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended for local dev)
- Docker + Docker Compose (for containerized deploy)
- A Bloomreach Engagement project with **Project Token**, **API Key**, and **API Secret**

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/Skilux/bloomreach-engagement-mcp.git
cd bloomreach-engagement-mcp

# Create virtual environment and install deps
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure credentials
cp .env.example .env
# Edit .env — fill in BR_PROJECT_TOKEN, BR_API_KEY, BR_API_SECRET

# Start the server
python server.py
```

Server starts on **`http://0.0.0.0:8000`**. The MCP endpoint is at **`http://localhost:8000/mcp`**.

### Test with MCP Inspector

```bash
fastmcp dev server.py
```

This launches the web inspector at `http://localhost:5173` — you can test each tool interactively.

### Test with the example client

In another terminal:

```bash
source .venv/bin/activate
python client_example.py
```

---

## Docker Deploy

```bash
cp .env.example .env   # fill in credentials
docker compose up -d
```

Health check: `curl http://localhost:8000/health` → `OK`

---

## Connect from Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "bloomreach": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

---

## Tool Reference

| Tool | HTTP Endpoint | Sync/Async | Purpose |
|------|---------------|------------|---------|
| `set_customer_property` | `POST /track/v2/{token}/customers` | **Async** (queued) | Write/update customer profile attributes |
| `trigger_scenario` | `POST /track/v2/{token}/customers/events` | **Async** (queued) | Fire event to trigger a Bloomreach scenario |
| `read_customer_events` | `POST /data/v2/{token}/customers/events` | **Sync** | Read stored events for a customer |
| `read_customer_attributes` | `POST /data/v2/{token}/customers/attributes` | **Sync** | Read stored attributes for a customer |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BR_PROJECT_TOKEN` | **Yes** | — | Bloomreach project token |
| `BR_API_KEY` | **Yes** | — | Private API key (HTTP Basic Auth) |
| `BR_API_SECRET` | **Yes** | — | Private API secret (HTTP Basic Auth) |
| `BR_BASE_TRACK` | No | `https://api.exponea.com/track/v2` | Tracking API base URL |
| `BR_BASE_DATA` | No | `https://api.exponea.com/data/v2` | Data API base URL |
| `MCP_HOST` | No | `0.0.0.0` | Server bind host |
| `MCP_PORT` | No | `8000` | Server listen port |

---

## Rate Limits & Gotchas

- **Tracking API rate limit:** 6,000 requests/minute per IP. HTTP 429 if exceeded — excess data is silently dropped by Bloomreach.
- **Writes are async!** `set_customer_property` and `trigger_scenario` return HTTP 200 when the request is *queued*, not committed. Always add a **1–2 second delay** before verifying with `read_customer_events` / `read_customer_attributes`.
- **`trigger_scenario`** only works if a matching scenario with an event-based trigger node already exists in the Bloomreach UI. This tool fires the event; Bloomreach handles audience filtering and channel dispatch.
- **Max request body:** 800 KB. **Max single property value:** 16 KB.
- **Consent & audience rules** are enforced by Bloomreach server-side — the API accepts the event, but Bloomreach decides whether to dispatch based on customer consent, suppression lists, and scenario audience filters.

---

## License

MIT