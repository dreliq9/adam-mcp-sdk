"""Tests for adam_mcp_py.BaseServer — wraps FastMCP with house-style defaults."""

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
