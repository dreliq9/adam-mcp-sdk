"""Result type — implements §1.1 and §6.29 of HOUSE_STYLE.md.

Every tool returns a Result. Never raw output, never raw exceptions.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Status(str, Enum):
    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass
class Result(Generic[T]):
    """The unified tool result type. Implements §1.1.

    Fields:
        status:      OK / WARN / FAIL.
        value:       Synthesized/typed output for AI consumption.
        raw:         Underlying API response (Principle One support, §6.29).
        metrics:     Numeric measurements (elapsed_ms, bytes_read, etc.).
        diagnostics: Human-readable description of what happened.
        hint:        What to try next on FAIL/WARN. REQUIRED for non-OK.
        mode_tag:    Which backend/path was used (e.g., "[IPC]", "[LOCAL]").
    """
    status: Status
    value: T | None = None
    raw: Any | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    hint: str | None = None
    mode_tag: str | None = None

    @classmethod
    def ok(
        cls,
        value: T | None = None,
        *,
        raw: Any | None = None,
        metrics: dict[str, Any] | None = None,
        diagnostics: list[str] | None = None,
        mode_tag: str | None = None,
    ) -> "Result[T]":
        return cls(
            status=Status.OK,
            value=value,
            raw=raw,
            metrics=metrics or {},
            diagnostics=diagnostics or [],
            mode_tag=mode_tag,
        )

    @classmethod
    def warn(
        cls,
        value: T | None = None,
        *,
        hint: str | None,
        raw: Any | None = None,
        metrics: dict[str, Any] | None = None,
        diagnostics: list[str] | None = None,
        mode_tag: str | None = None,
    ) -> "Result[T]":
        if not hint:
            raise ValueError("Result.warn: hint is required (§1.1: every WARN has a hint).")
        return cls(
            status=Status.WARN,
            value=value,
            raw=raw,
            metrics=metrics or {},
            diagnostics=diagnostics or [],
            hint=hint,
            mode_tag=mode_tag,
        )

    @classmethod
    def fail(
        cls,
        *,
        hint: str | None,
        raw: Any | None = None,
        metrics: dict[str, Any] | None = None,
        diagnostics: list[str] | None = None,
        mode_tag: str | None = None,
    ) -> "Result[T]":
        if not hint:
            raise ValueError("Result.fail: hint is required (§1.1: every FAIL has a hint).")
        return cls(
            status=Status.FAIL,
            value=None,
            raw=raw,
            metrics=metrics or {},
            diagnostics=diagnostics or [],
            hint=hint,
            mode_tag=mode_tag,
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d
