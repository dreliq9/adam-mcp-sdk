"""Tests for adam_mcp_py.BaseServer — wraps MCPServer with house-style defaults."""

import pytest
from mcp import Client

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
    from adam_mcp_py import is_passthrough, passthrough

    server = BaseServer(name="test-mcp")

    @server.tool()
    @passthrough
    def run_raw_script(script: str) -> Result[str]:
        return Result.ok(value=script)

    assert is_passthrough(run_raw_script)


def test_base_server_exposes_underlying_mcp_server():
    server = BaseServer(name="test-mcp")
    assert server.mcp_server.name == "test-mcp"


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
async def test_base_server_async_tool_over_v2_in_memory_protocol():
    """Exercise the 2026-era v2 protocol without a subprocess transport."""
    server = BaseServer(name="async-test-server")

    @server.tool()
    async def async_double(value: int) -> Result[int]:
        return Result.ok(value=value * 2)

    async with Client(server.mcp_server) as client:
        response = await client.call_tool("async_double", {"value": 6})

    payload = response.structured_content
    assert payload is not None
    assert payload["status"] == "OK"
    assert payload["value"] == 12
