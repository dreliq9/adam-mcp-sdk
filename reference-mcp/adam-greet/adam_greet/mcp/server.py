"""MCP server entrypoint for adam-greet. Wires every tool category into BaseServer."""

from __future__ import annotations
from adam_mcp_py import BaseServer

from . import greeting_tools, context_tools, history_tools, workflow_tools, escape_tools

_server = BaseServer(name="adam-greet")

_server.tool()(greeting_tools.compose_greeting)
_server.tool()(greeting_tools.compose_personalized_greeting)
_server.tool()(context_tools.get_morning_context)
_server.tool()(history_tools.record_greeting)
_server.tool()(history_tools.recent_greetings)
_server.tool()(workflow_tools.morning_briefing)
_server.tool()(escape_tools.compose_raw_greeting)


def main() -> None:
    _server.run()


if __name__ == "__main__":
    main()
