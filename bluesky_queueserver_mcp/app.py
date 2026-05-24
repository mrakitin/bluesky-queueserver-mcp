"""
Module-level FastMCP app for use with `fastmcp dev inspector` and similar tools.

Reads connection settings from environment variables (all optional):
  QSERVER_PROTOCOL     zmq (default) or http
  QSERVER_ZMQ_CONTROL_ADDRESS   default: tcp://localhost:60615
  QSERVER_ZMQ_INFO_ADDRESS      default: tcp://localhost:60625
  QSERVER_HTTP_SERVER_URI       required when QSERVER_PROTOCOL=http
  QSERVER_USER_GROUP            default: primary_users
  QSERVER_USER                  default: not set

Usage with the inspector::

    fastmcp dev inspector bluesky_queueserver/mcp_server/app.py

Or with environment overrides::

    QSERVER_USER_GROUP=primary fastmcp dev inspector bluesky_queueserver/mcp_server/app.py
"""

from __future__ import annotations

import os

from bluesky_queueserver_mcp.server import create_server

_protocol = os.environ.get("QSERVER_PROTOCOL", "zmq").lower()
_user_group = os.environ.get("QSERVER_USER_GROUP", "primary_users")
_user = os.environ.get("QSERVER_USER", None)

_api_cache: list = []


def _get_api():
    if _api_cache:
        return _api_cache[0]

    if _protocol == "zmq":
        from bluesky_queueserver_api.zmq import REManagerAPI

        api = REManagerAPI(
            zmq_control_addr=os.environ.get(
                "QSERVER_ZMQ_CONTROL_ADDRESS", "tcp://localhost:60615"
            ),
            zmq_info_addr=os.environ.get(
                "QSERVER_ZMQ_INFO_ADDRESS", "tcp://localhost:60625"
            ),
        )
    else:
        from bluesky_queueserver_api.http import REManagerAPI

        api = REManagerAPI(
            http_server_uri=os.environ.get("QSERVER_HTTP_SERVER_URI", "http://localhost:60610"),
        )

    if _user is not None:
        api.user = _user
    api.user_group = _user_group

    _api_cache.append(api)
    return api


# Module-level FastMCP instance — discovered automatically by fastmcp tools
mcp = create_server(_get_api)
