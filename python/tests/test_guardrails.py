"""Tests for adam_mcp_py.requires — implements §1.3, §6.31."""

import pytest

from adam_mcp_py import Result, Status, requires


def auth_ok() -> bool:
    return True


def auth_missing() -> bool:
    return False


def test_requires_passes_when_precondition_holds():
    @requires(auth_ok, fail_hint="run /auth first")
    def protected_op() -> Result[int]:
        return Result.ok(value=42)

    r = protected_op()
    assert r.status == Status.OK
    assert r.value == 42


def test_requires_warns_when_precondition_fails_default():
    @requires(auth_missing, fail_hint="run /auth first")
    def protected_op() -> Result[int]:
        return Result.ok(value=42)

    r = protected_op()
    # Default severity is WARN per §6.31
    assert r.status == Status.WARN
    assert "auth" in r.hint.lower()


def test_requires_fails_when_severity_is_fail():
    @requires(auth_missing, fail_hint="run /auth first", severity="FAIL")
    def destructive_op() -> Result[int]:
        return Result.ok(value=99)

    r = destructive_op()
    assert r.status == Status.FAIL


def test_requires_force_overrides_failed_precondition():
    @requires(auth_missing, fail_hint="run /auth first")
    def protected_op(force: bool = False) -> Result[int]:
        return Result.ok(value=42)

    r = protected_op(force=True)
    # With force=True the guardrail is bypassed
    assert r.status == Status.OK
    assert r.value == 42


@pytest.mark.asyncio
async def test_requires_supports_async_tools():
    @requires(auth_ok, fail_hint="run /auth first")
    async def protected_op() -> Result[int]:
        return Result.ok(value=42)

    result = await protected_op()
    assert result.status == Status.OK
    assert result.value == 42
