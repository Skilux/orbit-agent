"""
bloomreach-engagement-mcp

FastMCP server wrapping four Bloomreach Engagement API endpoints as MCP tools.
Runs over Streamable HTTP transport.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.responses import PlainTextResponse

# ---------------------------------------------------------------------------
# Load .env if present (optional — Docker/CI use env vars directly)
# ---------------------------------------------------------------------------

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# ---------------------------------------------------------------------------
# Env validation at startup
# ---------------------------------------------------------------------------

REQUIRED_ENV_VARS = ["BR_PROJECT_TOKEN", "BR_API_KEY", "BR_API_SECRET"]
missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing:
    msg = (
        f"Missing required environment variables: {', '.join(missing)}. "
        f"Please set them in your .env file or environment before starting the server."
    )
    raise RuntimeError(msg)


def _auth() -> tuple[str, str]:
    """Return (api_key, api_secret) from environment."""
    key = os.environ["BR_API_KEY"]
    secret = os.environ["BR_API_SECRET"]
    return (key, secret)


# ---------------------------------------------------------------------------
# Application lifespan – shared httpx.AsyncClient
# ---------------------------------------------------------------------------

_request_context: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(server: FastMCP) -> None:
    """Startup / shutdown hook for the MCP server."""
    global _request_context
    key, secret = _auth()
    _request_context = httpx.AsyncClient(
        auth=httpx.BasicAuth(key, secret),
        timeout=30.0,
    )
    try:
        yield
    finally:
        await _request_context.aclose()
        _request_context = None


def _client() -> httpx.AsyncClient:
    """Return the shared async HTTP client.  Raises if called outside lifespan."""
    if _request_context is None:
        raise RuntimeError("HTTP client not initialised – server not running?")
    return _request_context


# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="bloomreach-engagement",
    instructions="""
MCP server wrapping the Bloomreach Engagement API.

Tools:
- set_customer_property: Write/update attributes on a customer profile
- trigger_scenario: Fire an event that activates a Bloomreach scenario (e.g. send email)
- read_customer_events: Read stored events for a customer (monitoring/verification)
- read_customer_attributes: Read stored attributes for a customer (write verification)

Start with set_customer_property to enrich a profile, then trigger_scenario to activate a campaign.
""",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BR_BASE_TRACK = os.getenv("BR_BASE_TRACK", "https://api.exponea.com/track/v2")
BR_BASE_DATA = os.getenv("BR_BASE_DATA", "https://api.exponea.com/data/v2")
BR_PROJECT_TOKEN = os.environ["BR_PROJECT_TOKEN"]


async def _post(url: str, body: dict[str, Any]) -> dict[str, Any]:
    """POST JSON to *url*, raise on non-2xx."""
    client = _client()
    resp = await client.post(url, json=body)
    if not resp.is_success:
        raise RuntimeError(
            f"Bloomreach API error (HTTP {resp.status_code}): {resp.text}"
        )
    return resp.json()


# ---------------------------------------------------------------------------
# Tool 1 – set_customer_property
# ---------------------------------------------------------------------------


@mcp.tool
async def set_customer_property(
    customer_id: str,
    properties: dict[str, Any],
    id_type: str = "registered",
) -> dict[str, Any]:
    """
    Create or update properties on a Bloomreach customer profile.

    **Important:** This is an **async** write. A HTTP 200 response means the
    write has been *queued*, not yet committed. Wait 1-2 seconds before
    verifying with ``read_customer_attributes``.

    Args:
        customer_id: The customer identifier value (e.g. email or internal ID).
        properties: Dict of attribute key-value pairs to write
            (e.g. ``{"email": "x@y.com", "plan": "pro"}``).
        id_type: The customer ID type.  Defaults to ``"registered"``.
            Other common values: ``"cookie"``, ``"email"``.

    Returns:
        Bloomreach API response dict.  HTTP 200 means the write was QUEUED.
    """
    url = f"{BR_BASE_TRACK}/projects/{BR_PROJECT_TOKEN}/customers"
    body: dict[str, Any] = {
        "customer_ids": {id_type: customer_id},
        "properties": properties,
    }
    return await _post(url, body)


# ---------------------------------------------------------------------------
# Tool 2 – trigger_scenario
# ---------------------------------------------------------------------------


@mcp.tool
async def trigger_scenario(
    customer_id: str,
    event_type: str,
    properties: dict[str, Any] | None = None,
    id_type: str = "registered",
) -> dict[str, Any]:
    """
    Fire a Bloomreach event that triggers a pre-configured scenario
    (e.g. campaign email).

    **Important:** A scenario with a matching event-based trigger node must
    already exist in the Bloomreach UI before this tool will activate it.
    This tool fires the event; Bloomreach handles audience filtering, consent
    checks, and channel dispatch.

    This is an **async** write.  A HTTP 200 response means the event has been
    *queued*, not yet processed.  Wait 1-2 seconds before verifying with
    ``read_customer_events``.

    Args:
        customer_id: The customer identifier value.
        event_type: The event name to fire (must match the trigger node in the
            scenario).
        properties: Optional dict of event properties
            (e.g. ``{"voucher_code": "X10", "source": "agent"}``).
        id_type: Customer ID type.  Defaults to ``"registered"``.

    Returns:
        Bloomreach API response dict.  HTTP 200 means event was QUEUED.
    """
    url = f"{BR_BASE_TRACK}/projects/{BR_PROJECT_TOKEN}/customers/events"
    body: dict[str, Any] = {
        "customer_ids": {id_type: customer_id},
        "event_type": event_type,
        "properties": properties or {},
    }
    return await _post(url, body)


# ---------------------------------------------------------------------------
# Tool 3 – read_customer_events
# ---------------------------------------------------------------------------


@mcp.tool
async def read_customer_events(
    customer_id: str,
    event_types: list[str],
    id_type: str = "registered",
    limit: int = 20,
    order: str = "desc",
) -> dict[str, Any]:
    """
    Read stored events for a customer profile from Bloomreach.

    Use this to monitor what happened after ``trigger_scenario`` — check for
    system events like ``email_delivered``, ``email_opened``, or your custom
    event type.

    This is a **synchronous** read (immediate result).

    Args:
        customer_id: The customer identifier value.
        event_types: List of event type names to filter by
            (e.g. ``["email_delivered", "my_custom_event"]``).
        id_type: Customer ID type.  Defaults to ``"registered"``.
        limit: Max number of events to return.  Defaults to 20.
        order: Sort order by timestamp — ``"desc"`` (newest first) or
            ``"asc"``.  Defaults to ``"desc"``.

    Returns:
        Dict with ``"data"`` list of matching events.
    """
    url = f"{BR_BASE_DATA}/projects/{BR_PROJECT_TOKEN}/customers/events"
    body: dict[str, Any] = {
        "customer_ids": {id_type: customer_id},
        "event_types": event_types,
        "limit": limit,
        "order": order,
    }
    return await _post(url, body)


# ---------------------------------------------------------------------------
# Tool 4 – read_customer_attributes
# ---------------------------------------------------------------------------


@mcp.tool
async def read_customer_attributes(
    customer_id: str,
    attributes: list[str],
    id_type: str = "registered",
) -> dict[str, Any]:
    """
    Read stored attribute values for a customer profile from Bloomreach.

    Use this to verify that ``set_customer_property`` was committed — note
    that writes are async, so add a 1-2 second delay before calling this.

    This is a **synchronous** read (immediate result).

    Args:
        customer_id: The customer identifier value.
        attributes: List of property names to read
            (e.g. ``["email", "plan", "first_name"]``).
        id_type: Customer ID type.  Defaults to ``"registered"``.

    Returns:
        Dict with attribute values keyed by property name.
    """
    url = f"{BR_BASE_DATA}/projects/{BR_PROJECT_TOKEN}/customers/attributes"
    body: dict[str, Any] = {
        "customer_ids": {id_type: customer_id},
        "attributes": [{"type": "property", "property": a} for a in attributes],
    }
    return await _post(url, body)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Any) -> PlainTextResponse:
    """Simple liveness probe for Docker healthcheck et al."""
    _ = request  # unused but required by FastMCP route signature
    return PlainTextResponse("OK")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "http")
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        mcp.run(transport="http", host=host, port=port)
