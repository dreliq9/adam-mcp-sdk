"""Stdio fixture proving BaseServer preserves async tools over MCP."""

import asyncio

from adam_mcp_py import BaseServer, Result


server = BaseServer(name="async-test-server")


@server.tool()
async def async_double(value: int) -> Result[int]:
    await asyncio.sleep(0)
    return Result.ok(value=value * 2)


if __name__ == "__main__":
    # MCP Python SDK v2 defaults to stdio for direct run().
    server.run()
