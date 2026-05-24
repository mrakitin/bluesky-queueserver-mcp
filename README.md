# bluesky-queueserver-mcp

MCP server for [bluesky-queueserver](https://github.com/bluesky/bluesky-queueserver).

Exposes the full `REManagerAPI` as [Model Context Protocol](https://modelcontextprotocol.io/) tools and resources over stdio, so AI agents (LM Studio, Claude Desktop, etc.) can control the Bluesky Run Engine queue.

## Installation

```bash
pip install bluesky-queueserver-mcp
```

## Usage

```bash
# Connect to a local RE Manager via ZMQ (default)
bluesky-mcp-server

# Connect via HTTP
bluesky-mcp-server --protocol http --http-server-uri http://localhost:60610
```

## LM Studio configuration (`~/.lmstudio/mcp.json`)

```json
{
  "mcpServers": {
    "bluesky-queueserver": {
      "command": "bluesky-mcp-server",
      "args": ["--user-group", "primary"]
    }
  }
}
```

## Available tools

| Tool | Description |
|------|-------------|
| `status` | RE Manager status |
| `queue_add_item` | Add a plan to the queue |
| `queue_start` / `queue_stop` | Start/stop queue execution |
| `environment_open` / `environment_close` | Manage the worker environment |
| `re_pause` / `re_resume` / `re_stop` | Control the running plan |
| … and many more |

## Environment variables (for `fastmcp dev inspector`)

| Variable | Default | Description |
|----------|---------|-------------|
| `QSERVER_PROTOCOL` | `zmq` | `zmq` or `http` |
| `QSERVER_ZMQ_CONTROL_ADDRESS` | `tcp://localhost:60615` | ZMQ control address |
| `QSERVER_ZMQ_INFO_ADDRESS` | `tcp://localhost:60625` | ZMQ info address |
| `QSERVER_HTTP_SERVER_URI` | — | Required for HTTP protocol |
| `QSERVER_USER_GROUP` | `primary_users` | User group |
