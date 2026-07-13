"""Tests for adam_mcp_py.passthrough — implements §6.30."""

from adam_mcp_py import is_bounded_passthrough, is_passthrough, passthrough


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


def test_bounded_passthrough_records_safety_policy():
    @passthrough(bounded=True)
    def run_safe_raw_query(query: str) -> str:
        return query

    assert is_passthrough(run_safe_raw_query)
    assert is_bounded_passthrough(run_safe_raw_query)


def test_unbounded_passthrough_is_not_marked_bounded():
    @passthrough
    def run_raw_script(script: str) -> str:
        return script

    assert not is_bounded_passthrough(run_raw_script)
