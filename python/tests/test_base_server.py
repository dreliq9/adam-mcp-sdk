"""Tests for adam_mcp_py.BaseServer — wraps FastMCP with house-style defaults."""

import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from adam_mcp_py import BaseServer, Result, Status


def test_base_server_registers_a_tool_returning_result():
    server = BaseServer(name="test-mcp")

    @server.tool()
    def hello(name: str) -> Result[str]:
        return Result.ok(value=f"hi {name}")

    # The tool callable still works directly
    r = hello("Adam")
    assert r.status == Status.OK
    assert r.value == "hi Adam"


def test_base_server_wraps_non_result_returns_as_fail():
    server = BaseServer(name="test-mcp")

    @server.tool()
    def bad_tool(x: int) -> int:
        return x * 2  # WRONG — should return Result

    r = bad_tool(5)
    # The wrapper coerces non-Result returns to FAIL with hint pointing to §1.1
    assert r.status == Status.FAIL
    assert "§1.1" in (r.hint or "")


def test_base_server_wraps_exception_as_fail_with_hint():
    server = BaseServer(name="test-mcp")

    @server.tool()
    def crashing_tool() -> Result:
        raise RuntimeError("boom")

    r = crashing_tool()
    assert r.status == Status.FAIL
    assert "boom" in " ".join(r.diagnostics)
    assert r.hint is not None


def test_base_server_passthrough_decorator_marks_tool():
    from adam_mcp_py import passthrough, is_passthrough

    server = BaseServer(name="test-mcp")

    @server.tool()
    @passthrough
    def run_raw_script(script: str) -> Result[str]:
        return Result.ok(value=script)

    assert is_passthrough(run_raw_script)


@pytest.mark.asyncio
async def test_base_server_awaits_async_result_tool():
    server = BaseServer(name="test-mcp")

    @server.tool()
    async def async_tool(value: int) -> Result[int]:
        return Result.ok(value=value * 2)

    result = await async_tool(4)
    assert result.status == Status.OK
    assert result.value == 8


@pytest.mark.asyncio
async def test_base_server_wraps_async_exception_without_traceback_in_result():
    server = BaseServer(name="test-mcp")

    @server.tool()
    async def async_crash() -> Result:
        raise RuntimeError("async boom")

    result = await async_crash()
    assert result.status == Status.FAIL
    assert result.diagnostics == ["RuntimeError: async boom"]
    assert "Traceback" not in " ".join(result.diagnostics)


@pytest.mark.asyncio
async def test_base_server_wraps_async_non_result_as_fail():
    server = BaseServer(name="test-mcp")

    @server.tool()
    async def bad_async_tool() -> int:
        return 7

    result = await bad_async_tool()
    assert result.status == Status.FAIL
    assert "actual return type: int" in result.diagnostics


@pytest.mark.asyncio
async def test_base_server_async_tool_over_stdio_protocol():
    fixture = Path(__file__).with_name("async_server_fixture.py")
    parameters = StdioServerParameters(command=sys.executable, args=[str(fixture)])

    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("async_double", {"value": 6})

    assert response.isError is False
    payload = json.loads(response.content[0].text)
    assert payload["status"] == "OK"
    assert payload["value"] == 12
