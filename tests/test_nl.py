"""Natural-language tool-selection tests for bluesky-queueserver-mcp.

Each test sends a natural-language prompt to an Ollama-hosted LLM with the
MCP server tools available (via the OpenAI tool-use API) and asserts that the
LLM chose the correct tool.  The LLM's prose reply is not evaluated.

Requirements
------------
- Ollama running with ``llama3.2:1b`` (or the model set via ``OLLAMA_MODEL``)
- ``bluesky-mcp-server`` on PATH
- Tests are automatically skipped when Ollama is unreachable
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

import pytest

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")


def _ollama_available() -> bool:
    try:
        import httpx

        r = httpx.get(OLLAMA_BASE_URL.replace("/v1", ""), timeout=3.0)
        return r.status_code < 500
    except Exception:
        return False


skip_no_ollama = pytest.mark.skipif(
    not _ollama_available(),
    reason=f"Ollama not running at {OLLAMA_BASE_URL}",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _get_mcp_tools_as_openai_schema() -> list[dict]:
    """Start the MCP server and return its tools in OpenAI function-call format."""
    from fastmcp import Client
    from fastmcp.client.transports import StdioTransport

    transport = StdioTransport(command="bluesky-mcp-server", args=[])
    async with Client(transport) as client:
        tools = await client.list_tools()

    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema or {"type": "object", "properties": {}},
            },
        }
        for t in tools
    ]


_SYSTEM_PROMPT = (
    "You are a helpful assistant with access to tools. "
    "You MUST always call one of the available tools to fulfill the user's request. "
    "Never respond in plain text — always invoke a tool."
)


async def _ask_llm(prompt: str, tools: list[dict]) -> Optional[str]:
    """Send *prompt* to Ollama with *tools* and return the first tool name called."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama", timeout=120.0)
    response = await client.chat.completions.create(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        tools=tools,
        tool_choice="required",
    )
    choice = response.choices[0]
    tool_calls = getattr(choice.message, "tool_calls", None)
    if tool_calls:
        return tool_calls[0].function.name
    return None


# ---------------------------------------------------------------------------
# NL tests
# ---------------------------------------------------------------------------

_TOOLS: list[dict] = []  # populated once per session


def _tools_named(*names: str) -> list[dict]:
    """Return the subset of tools whose names are in *names*."""
    return [t for t in _TOOLS if t["function"]["name"] in names]


@pytest.fixture(scope="session", autouse=True)
def _load_tools():
    global _TOOLS
    loop = asyncio.new_event_loop()
    try:
        _TOOLS = loop.run_until_complete(_get_mcp_tools_as_openai_schema())
    finally:
        loop.close()


@skip_no_ollama
async def test_nl_status():
    """'What is the current state of the RE Manager?' → status or ping."""
    tools = _tools_named("status", "ping", "environment_open")
    tool = await _ask_llm(
        "What is the current state of the RE Manager?", tools
    )
    assert tool in ("status", "ping"), f"Unexpected tool: {tool!r}"


@skip_no_ollama
async def test_nl_queue_get():
    """'Show me what's in the queue' → queue_get."""
    tools = _tools_named("queue_get", "item_add", "history_get")
    tool = await _ask_llm("Show me what's in the plan queue.", tools)
    assert tool == "queue_get", f"Unexpected tool: {tool!r}"


@skip_no_ollama
async def test_nl_environment_open():
    """'Open the worker environment' → environment_open."""
    tools = _tools_named("environment_open", "environment_close", "status")
    tool = await _ask_llm("Open the worker environment.", tools)
    assert tool == "environment_open", f"Unexpected tool: {tool!r}"


@skip_no_ollama
async def test_nl_item_add():
    """'Add a count plan to the queue' → item_add."""
    tools = _tools_named("item_add", "queue_get", "item_remove")
    tool = await _ask_llm(
        "Add a count plan with detector det for 5 points to the queue.", tools
    )
    assert tool == "item_add", f"Unexpected tool: {tool!r}"


@skip_no_ollama
async def test_nl_history_get():
    """'Show me the run history' → history_get."""
    tools = _tools_named("history_get", "queue_get", "history_clear")
    tool = await _ask_llm("Show me the plan execution history.", tools)
    assert tool == "history_get", f"Unexpected tool: {tool!r}"
