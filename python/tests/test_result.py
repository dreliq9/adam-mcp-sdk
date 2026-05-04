"""Tests for adam_mcp_py.Result — implements §1.1, §6.29."""
from adam_mcp_py import Result, Status


def test_result_ok_basic():
    r = Result.ok(value=42)
    assert r.status == Status.OK
    assert r.value == 42
    assert r.hint is None
    assert r.raw is None


def test_result_ok_with_metrics_and_mode_tag():
    r = Result.ok(value="hello", metrics={"elapsed_ms": 5.0}, mode_tag="[LOCAL]")
    assert r.metrics == {"elapsed_ms": 5.0}
    assert r.mode_tag == "[LOCAL]"


def test_result_warn_requires_hint():
    r = Result.warn(value=None, hint="retry with smaller radius", diagnostics=["edge too short"])
    assert r.status == Status.WARN
    assert r.hint == "retry with smaller radius"
    assert r.diagnostics == ["edge too short"]


def test_result_fail_requires_hint():
    r = Result.fail(hint="check API key", diagnostics=["401 Unauthorized"])
    assert r.status == Status.FAIL
    assert r.value is None
    assert r.hint == "check API key"


def test_result_raw_holds_underlying_response():
    raw_response = {"id": 7, "data": [1, 2, 3]}
    r = Result.ok(value=[1, 2, 3], raw=raw_response)
    assert r.raw == raw_response
    assert r.value == [1, 2, 3]


def test_result_to_dict_preserves_all_fields():
    r = Result.ok(value=1, metrics={"n": 1}, mode_tag="[T]", diagnostics=["did it"])
    d = r.to_dict()
    assert d["status"] == "OK"
    assert d["value"] == 1
    assert d["metrics"] == {"n": 1}
    assert d["mode_tag"] == "[T]"
    assert d["diagnostics"] == ["did it"]
    assert d["hint"] is None
    assert d["raw"] is None


def test_result_warn_without_hint_raises():
    import pytest
    with pytest.raises(ValueError, match="hint is required"):
        Result.warn(value=None, hint=None)


def test_result_fail_without_hint_raises():
    import pytest
    with pytest.raises(ValueError, match="hint is required"):
        Result.fail(hint=None)
