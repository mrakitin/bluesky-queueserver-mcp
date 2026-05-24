"""FastMCP application for bluesky-queueserver.

Usage
-----
Instantiate the server by calling :func:`create_server`, passing a callable
``get_api`` that returns a configured ``REManagerAPI`` instance.  The callable
is invoked on every tool/resource access so the API object can be recreated if
the connection is lost.
"""

from __future__ import annotations

from typing import Callable

import fastmcp

from bluesky_queueserver_mcp._tools import (
    environment,
    history,
    items,
    locks,
    misc,
    permissions,
    plans_devices,
    queue,
    re_control,
    scripting,
    status,
    tasks,
)


def create_server(get_api: Callable) -> fastmcp.FastMCP:
    """Create and return the configured FastMCP application.

    Parameters
    ----------
    get_api:
        Zero-argument callable that returns a ready-to-use ``REManagerAPI``
        instance.  It is called each time a tool or resource handler is invoked.
    """
    mcp = fastmcp.FastMCP(
        name="bluesky-queueserver",
        instructions=(
            "Control the Bluesky Run Engine Manager (RE Manager). "
            "Use the available tools to manage the plan queue, control the "
            "Run Engine, open/close the worker environment, and inspect "
            "allowed plans and devices."
        ),
    )

    # --- Resources -----------------------------------------------------------

    @mcp.resource("re-manager://status")
    def resource_status() -> dict:
        """Current RE Manager status."""
        return get_api().status(reload=True)

    @mcp.resource("re-manager://queue")
    def resource_queue() -> dict:
        """Current plan queue contents and running plan."""
        return get_api().queue_get(reload=True)

    @mcp.resource("re-manager://plans")
    def resource_plans() -> dict:
        """Plans allowed for the current user group."""
        return get_api().plans_allowed(reload=True)

    @mcp.resource("re-manager://devices")
    def resource_devices() -> dict:
        """Devices allowed for the current user group."""
        return get_api().devices_allowed(reload=True)

    @mcp.resource("re-manager://history")
    def resource_history() -> dict:
        """Plan execution history."""
        return get_api().history_get(reload=True)

    # --- Tools ---------------------------------------------------------------

    status.register(mcp, get_api)
    queue.register(mcp, get_api)
    items.register(mcp, get_api)
    environment.register(mcp, get_api)
    re_control.register(mcp, get_api)
    plans_devices.register(mcp, get_api)
    history.register(mcp, get_api)
    permissions.register(mcp, get_api)
    scripting.register(mcp, get_api)
    tasks.register(mcp, get_api)
    locks.register(mcp, get_api)
    misc.register(mcp, get_api)

    return mcp
