"""House Result envelopes must survive actual MCP 2 serialization."""

import json

import pytest
from mcp import Client

from adam_mcp_py import BaseServer, Result


@pytest.mark.asyncio
async def test_protocol_preserves_result_for_misannotated_and_unannotated_tools():
    server = BaseServer("envelope-regression")

    @server.tool()
    def wrong_return() -> int:
        return 7

    @server.tool()
    def unannotated_return():
        return Result.ok(value=9)

    @server.tool()
    async def raises() -> int:
        raise RuntimeError("fixture failure")

    async with Client(server.mcp_server) as client:
        for name, status, value in [
            ("wrong_return", "FAIL", None),
            ("unannotated_return", "OK", 9),
            ("raises", "FAIL", None),
        ]:
            response = await client.call_tool(name, {})
            assert not response.is_error
            payload = response.structured_content["result"]
            assert payload["status"] == status
            assert payload["value"] == value
            assert payload["envelope_version"] == 1
            assert json.loads(response.content[0].text) == payload


@pytest.mark.asyncio
async def test_protocol_does_not_evaluate_an_invalid_return_forward_reference():
    namespace = {"Result": Result}
    exec(
        "from __future__ import annotations\n"
        "def postponed(value: int) -> UnknownReturn:\n"
        "    return Result.ok(value=value)\n",
        namespace,
    )
    server = BaseServer("postponed-return-regression")
    server.tool()(namespace["postponed"])
    async with Client(server.mcp_server) as client:
        response = await client.call_tool("postponed", {"value": 15})
        assert not response.is_error
        assert response.structured_content["result"]["value"] == 15
