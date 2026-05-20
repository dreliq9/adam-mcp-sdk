"""Result type — implements §1.1 and §6.29 of HOUSE_STYLE.md.

Every tool returns a Result. Never raw output, never raw exceptions.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Generic, TypeAlias, TypeVar

T = TypeVar("T")

# Raw — documented exception to strict typing (§1.1). Result.raw carries
# unknown-shape payloads from foreign APIs; typing it as Any is intentional.
# Use this alias for self-documenting annotations; an individual MCP may
# narrow to a project-specific type if its backend response is fully known.
Raw: TypeAlias = Any

# Wire-format version of the Result envelope. Bumped only on breaking
# top-level field changes; see §1.1 "Envelope is a wire format" and
# DECISIONS 2026-05-19 (envelope versioning).
ENVELOPE_VERSION: int = 1


class Status(str, Enum):
    OK = "OK"
    WARN = "WARN"
    FAIL = "FAIL"


@dataclass(kw_only=True)
class Result(Generic[T]):
    """The unified tool result type. Implements §1.1.

    Fields (in canonical envelope order — byte-equivalence depends on this):
        envelope_version: Wire-format version. First field by design.
        status:           OK / WARN / FAIL.
        value:            Synthesized/typed output for AI consumption.
        raw:              Underlying API response (Principle One, §6.29).
                          Typed Any by contract — the documented exception
                          to strict typing.
        metrics:          Numeric measurements (elapsed_ms, bytes_read, etc.).
        diagnostics:      Human-readable description of what happened.
        hint:             What to try next on FAIL/WARN. REQUIRED for non-OK.
        mode_tag:         Which backend/path was used (e.g., "[IPC]", "[LOCAL]").

    kw_only=True keeps positional construction unavailable so the canonical
    field order stays an envelope-shape contract, not an argument convention.
    """
    envelope_version: int = ENVELOPE_VERSION
    status: Status
    value: T | None = None
    raw: Raw | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)
    hint: str | None = None
    mode_tag: str | None = None

    @classmethod
    def ok(
        cls,
        value: T | None = None,
        *,
        raw: Raw | None = None,
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
        raw: Raw | None = None,
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
        raw: Raw | None = None,
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
