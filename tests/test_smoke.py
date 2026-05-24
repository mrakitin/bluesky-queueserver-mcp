"""Smoke tests for bluesky-queueserver-mcp.

Unit tests verify tool registration without any external services.
Integration tests start the real ``bluesky-mcp-server`` binary via stdio
and talk to it using ``fastmcp.Client``.

Integration tests require a running RE Manager and are skipped when it is
not available (the ``integration`` pytest mark).
"""

from __future__ import annotations

import asyncio
import os

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_TOOLS = {
    "status",
    "ping",
    "config_get",
    "queue_get",
    "queue_start",
    "queue_stop",
    "queue_clear",
    "item_add",
    "item_get",
    "item_remove",
    "environment_open",
    "environment_close",
    "re_pause",
    "re_resume",
    "re_stop",
    "history_get",
    "history_clear",
    "lock",
    "unlock",
}


def _re_manager_available() -> bool:
    """Return True if a local RE Manager is responding on the default ZMQ port."""
    try:
        from bluesky_queueserver_api.zmq import REManagerAPI

        api = REManagerAPI(timeout_recv=1.0, timeout_send=1.0)
        r = api.ping()
        return bool(r.get("msg"))
    except Exception:
        return False


skip_no_re_manager = pytest.mark.skipif(
    not _re_manager_available(),
    reason="RE Manager not running on tcp://localhost:60615",
)


# ---------------------------------------------------------------------------
# Unit tests (no external services needed)
# ---------------------------------------------------------------------------


def test_server_creates():
    """Server can be instantiated with a dummy API factory."""
    from bluesky_queueserver_mcp.server import create_server

    mcp = create_server(lambda: None)
    assert mcp is not None


def test_expected_tools_registered():
    """All expected tool names are registered on the server."""
    from bluesky_queueserver_mcp.server import create_server

    mcp = create_server(lambda: None)
    tools = asyncio.run(mcp.list_tools())
    registered = {t.name for t in tools}
    missing = EXPECTED_TOOLS - registered
    assert not missing, f"Missing tools: {missing}"


# ---------------------------------------------------------------------------
# Integration tests (require a running RE Manager)
# ---------------------------------------------------------------------------


@skip_no_re_manager
async def test_list_tools_via_stdio():
    """MCP server starts and lists the expected tools over stdio."""
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    transport = StdioTransport(command="bluesky-mcp-server", args=[])
    async with Client(transport) as client:
        tools = await client.list_tools()
        names = {t.name for t in tools}
        assert EXPECTED_TOOLS.issubset(names)


@skip_no_re_manager
async def test_ping_via_stdio():
    """Calling the ``ping`` tool returns a dict with a ``msg`` key."""
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    transport = StdioTransport(command="bluesky-mcp-server", args=[])
    async with Client(transport) as client:
        result = await client.call_tool("ping")
        assert not result.is_error
        data = result.data or result.structured_content or {}
        assert "msg" in data


@skip_no_re_manager
async def test_status_via_stdio():
    """Calling the ``status`` tool returns RE Manager state information."""
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    transport = StdioTransport(command="bluesky-mcp-server", args=[])
    async with Client(transport) as client:
        result = await client.call_tool("status")
        assert not result.is_error
        data = result.data or result.structured_content or {}
        assert "manager_state" in data
