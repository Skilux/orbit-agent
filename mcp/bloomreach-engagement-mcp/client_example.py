"""
Example async client to test the bloomreach-engagement-mcp server locally.

Usage:
    python client_example.py

Requires the server to be running at http://localhost:8000/mcp
"""

from __future__ import annotations

import asyncio

from fastmcp import Client


async def main() -> None:
    """Run all four MCP tools against a local server."""
    client = Client("http://localhost:8000/mcp")
    async with client:
        # 1. Set a property
        print("--- set_customer_property ---")
        r1 = await client.call_tool(
            "set_customer_property",
            {
                "customer_id": "test@example.com",
                "properties": {"first_name": "Test", "plan": "pro"},
            },
        )
        print(r1)

        # 2. Trigger a scenario
        print("\n--- trigger_scenario ---")
        r2 = await client.call_tool(
            "trigger_scenario",
            {
                "customer_id": "test@example.com",
                "event_type": "agent_test_event",
                "properties": {"source": "mcp_agent"},
            },
        )
        print(r2)

        # 3. Read events (after short delay for async commit)
        print("\n--- read_customer_events ---")
        await asyncio.sleep(2)
        r3 = await client.call_tool(
            "read_customer_events",
            {
                "customer_id": "test@example.com",
                "event_types": ["agent_test_event"],
            },
        )
        print(r3)

        # 4. Read attributes
        print("\n--- read_customer_attributes ---")
        r4 = await client.call_tool(
            "read_customer_attributes",
            {
                "customer_id": "test@example.com",
                "attributes": ["first_name", "plan"],
            },
        )
        print(r4)


if __name__ == "__main__":
    asyncio.run(main())
