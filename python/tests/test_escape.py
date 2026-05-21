"""Tests for adam_mcp_py.passthrough — implements §6.30."""

from adam_mcp_py import passthrough, is_passthrough


def test_passthrough_marks_function():
    @passthrough
    def run_raw_script(script: str) -> str:
        return script

    assert is_passthrough(run_raw_script)


def test_non_passthrough_function_is_not_marked():
    def normal_fn():
        pass

    assert not is_passthrough(normal_fn)


def test_passthrough_does_not_alter_function_behavior():
    @passthrough
    def echo(x: int) -> int:
        return x * 2

    assert echo(5) == 10
