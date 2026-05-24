"""Command-line entry point for the bluesky-queueserver MCP server.

Run with::

    bluesky-mcp-server [options]

The server communicates with AI clients (Copilot, Claude Desktop, etc.) via
stdio using the Model Context Protocol (MCP).
"""

from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bluesky-mcp-server",
        description=(
            "MCP server for bluesky-queueserver. "
            "Exposes the full REManagerAPI as MCP tools and resources over stdio."
        ),
    )
    parser.add_argument(
        "--protocol",
        choices=["zmq", "http"],
        default="zmq",
        help="Protocol to use when connecting to RE Manager (default: zmq).",
    )
    # ZMQ options
    zmq_group = parser.add_argument_group("ZMQ options (--protocol zmq)")
    zmq_group.add_argument(
        "--zmq-control-addr",
        default="tcp://localhost:60615",
        metavar="ADDR",
        help="ZMQ control socket address (default: tcp://localhost:60615).",
    )
    zmq_group.add_argument(
        "--zmq-info-addr",
        default="tcp://localhost:60625",
        metavar="ADDR",
        help="ZMQ info/publish socket address (default: tcp://localhost:60625).",
    )
    # HTTP options
    http_group = parser.add_argument_group("HTTP options (--protocol http)")
    http_group.add_argument(
        "--http-server-uri",
        default=None,
        metavar="URI",
        help="Base URI of the bluesky-httpserver REST API, e.g. http://localhost:60610.",
    )
    http_group.add_argument(
        "--http-server-keyfile",
        default=None,
        metavar="PATH",
        help="Path to a TLS private-key file for the HTTP server.",
    )
    # Common options
    parser.add_argument(
        "--user",
        default=None,
        metavar="NAME",
        help="Default user name for API calls.",
    )
    parser.add_argument(
        "--user-group",
        default="primary_users",
        metavar="GROUP",
        help="Default user group for API calls (default: primary_users).",
    )
    return parser


def _make_get_api(args: argparse.Namespace):
    """Return a factory function that creates and caches an REManagerAPI."""
    _api_cache: list = []

    def get_api():
        if _api_cache:
            return _api_cache[0]

        if args.protocol == "zmq":
            from bluesky_queueserver_api.zmq import REManagerAPI

            api = REManagerAPI(
                zmq_control_addr=args.zmq_control_addr,
                zmq_info_addr=args.zmq_info_addr,
            )
        else:
            from bluesky_queueserver_api.http import REManagerAPI

            http_kwargs: dict = {}
            if args.http_server_uri is not None:
                http_kwargs["http_server_uri"] = args.http_server_uri
            if args.http_server_keyfile is not None:
                http_kwargs["http_server_keyfile"] = args.http_server_keyfile
            api = REManagerAPI(**http_kwargs)

        if args.user is not None:
            api.user = args.user
        api.user_group = args.user_group

        _api_cache.append(api)
        return api

    return get_api


def main(argv=None) -> None:
    """Entry point for the ``bluesky-mcp-server`` command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Validate HTTP-specific requirement
    if args.protocol == "http" and args.http_server_uri is None:
        parser.error("--http-server-uri is required when --protocol http is selected.")

    try:
        from bluesky_queueserver_mcp.server import create_server
    except ImportError as exc:
        print(
            f"ERROR: Could not import MCP server dependencies: {exc}\n"
            "Make sure fastmcp and bluesky-queueserver-api are installed.",
            file=sys.stderr,
        )
        sys.exit(1)

    get_api = _make_get_api(args)
    mcp = create_server(get_api)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
