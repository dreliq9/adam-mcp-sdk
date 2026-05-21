"""Escape-hatch decorator — implements §6.30 of HOUSE_STYLE.md."""

from __future__ import annotations
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)

_PASSTHROUGH_MARKER = "__adam_mcp_passthrough__"


def passthrough(fn: F) -> F:
    """Mark this tool as the MCP's documented escape hatch. Implements §6.30.

    Every MCP must have exactly one @passthrough-decorated tool. The audit
    CLI enforces this. The decorated tool's behavior is unchanged.
    """
    setattr(fn, _PASSTHROUGH_MARKER, True)
    return fn


def is_passthrough(fn: object) -> bool:
    """Return True if fn was decorated with @passthrough. Helper for §6.30."""
    return bool(getattr(fn, _PASSTHROUGH_MARKER, False))
