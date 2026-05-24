"""
Natural-language chat interface for bluesky-queueserver using a local LLM.

Works with any OpenAI-compatible local LLM server:
  - LM Studio   (http://localhost:1234/v1)
  - Ollama      (http://localhost:11434/v1)
  - llama.cpp   (http://localhost:8080/v1)
  - vLLM        (http://localhost:8000/v1)

Usage::

    # With LM Studio (start LM Studio first and load a model):
    pixi run python -m bluesky_queueserver_mcp.chat

    # With Ollama:
    CHAT_BASE_URL=http://localhost:11434/v1 CHAT_MODEL=llama3.2 \\
        pixi run python -m bluesky_queueserver_mcp.chat

    # Override RE Manager user group:
    QSERVER_USER_GROUP=primary pixi run python -m bluesky_queueserver_mcp.chat

Environment variables
---------------------
CHAT_BASE_URL     Base URL of the OpenAI-compatible API  (default: http://localhost:1234/v1)
CHAT_MODEL        Model name to use                      (default: local-model)
CHAT_API_KEY      API key (most local servers accept any value, default: lm-studio)
QSERVER_USER_GROUP  User group for RE Manager            (default: primary_users)
QSERVER_ZMQ_CONTROL_ADDRESS  ZMQ address                (default: tcp://localhost:60615)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

import openai

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("CHAT_BASE_URL", "http://localhost:1234/v1")
MODEL = os.environ.get("CHAT_MODEL", "local-model")
API_KEY = os.environ.get("CHAT_API_KEY", "lm-studio")
USER_GROUP = os.environ.get("QSERVER_USER_GROUP", "primary_users")
ZMQ_ADDR = os.environ.get("QSERVER_ZMQ_CONTROL_ADDRESS", "tcp://localhost:60615")

# ---------------------------------------------------------------------------
# Build the MCP tool list (as OpenAI function-calling schemas)
# ---------------------------------------------------------------------------

def _build_tools_from_mcp(mcp_tools) -> list[dict]:
    """Convert FastMCP tool objects to OpenAI function-calling format."""
    tools = []
    for t in mcp_tools:
        # Build parameter schema from the tool's input schema
        schema = t.parameters if hasattr(t, "parameters") else {}
        if not schema:
            schema = {"type": "object", "properties": {}}
        tools.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": (t.description or "").strip(),
                "parameters": schema,
            },
        })
    return tools


async def _get_mcp_tools(mcp):
    """Return list of MCP tool objects."""
    import fastmcp
    async with fastmcp.Client(mcp) as client:
        return await client.list_tools()


async def _call_mcp_tool(mcp, name: str, arguments: dict) -> str:
    """Call an MCP tool and return the result as a JSON string."""
    import fastmcp
    async with fastmcp.Client(mcp) as client:
        result = await client.call_tool(name, arguments)
        if result.content:
            return result.content[0].text
        return json.dumps({"success": True})


# ---------------------------------------------------------------------------
# Chat loop
# ---------------------------------------------------------------------------

async def chat_loop(mcp):
    # Set up OpenAI client pointing at the local server
    client = openai.AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

    # Discover tools
    print("Discovering MCP tools...", flush=True)
    mcp_tools = await _get_mcp_tools(mcp)
    openai_tools = _build_tools_from_mcp(mcp_tools)
    print(f"Loaded {len(openai_tools)} tools from bluesky-queueserver MCP server.")
    print(f"LLM: {MODEL} @ {BASE_URL}")
    print(f"RE Manager: {ZMQ_ADDR}  user_group={USER_GROUP}")
    print("\nType your question (Ctrl-C or 'exit' to quit).\n")

    system_prompt = (
        "You are a helpful assistant for controlling the Bluesky Run Engine (RE) Manager "
        "at a scientific synchrotron beamline. "
        "You have access to tools that let you inspect and control the RE Manager: "
        "checking status, managing the plan queue, opening/closing the worker environment, "
        "pausing/resuming/aborting runs, and more. "
        "When the user asks you to do something, use the available tools to do it. "
        "Always confirm what you did and report the result in plain language."
    )

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input or user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        # Agentic loop: keep calling LLM until it stops requesting tool calls
        while True:
            try:
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )
            except openai.APIConnectionError:
                print(f"\nERROR: Cannot connect to LLM at {BASE_URL}")
                print("Make sure LM Studio (or Ollama) is running with a model loaded.")
                break

            msg = response.choices[0].message
            messages.append(msg.model_dump(exclude_unset=True))

            # If no tool calls, print the final answer
            if not msg.tool_calls:
                print(f"\nAssistant: {msg.content}\n")
                break

            # Execute each tool call
            for tc in msg.tool_calls:
                fn = tc.function
                try:
                    args = json.loads(fn.arguments) if fn.arguments else {}
                except json.JSONDecodeError:
                    args = {}

                print(f"  [tool] {fn.name}({json.dumps(args, separators=(',', ':'))})")
                tool_result = await _call_mcp_tool(mcp, fn.name, args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_result,
                })


def main():
    # Build the MCP server
    from bluesky_queueserver_api.zmq import REManagerAPI
    from bluesky_queueserver_mcp.server import create_server

    api = REManagerAPI(zmq_control_addr=ZMQ_ADDR)
    api.user_group = USER_GROUP
    mcp = create_server(lambda: api)

    asyncio.run(chat_loop(mcp))


if __name__ == "__main__":
    main()
