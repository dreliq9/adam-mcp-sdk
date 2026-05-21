"""Guardrail decorator — implements §1.3 and §6.31 of HOUSE_STYLE.md."""

from __future__ import annotations
from functools import wraps
from typing import Callable, Literal

from .result import Result

Severity = Literal["WARN", "FAIL"]


def requires(
    precondition: Callable[[], bool],
    *,
    fail_hint: str,
    severity: Severity = "WARN",
) -> Callable:
    """Guard a tool with a precondition. Implements §1.3, §6.31.

    Default severity is WARN. Use FAIL only when the consequence is destructive.

    Pass `force=True` to the decorated tool to bypass the guardrail.
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, force: bool = False, **kwargs):
            if force or precondition():
                return fn(*args, **kwargs)
            if severity == "FAIL":
                return Result.fail(
                    hint=fail_hint, diagnostics=[f"precondition failed: {precondition.__name__}"]
                )
            return Result.warn(
                value=None,
                hint=fail_hint,
                diagnostics=[f"precondition failed: {precondition.__name__}"],
            )

        return wrapper

    return decorator
