"""Escape-hatch decorator — implements §6.30 of HOUSE_STYLE.md."""

from __future__ import annotations
from typing import Callable, overload, TypeVar

F = TypeVar("F", bound=Callable)

_PASSTHROUGH_MARKER = "__adam_mcp_passthrough__"
_BOUNDED_PASSTHROUGH_MARKER = "__adam_mcp_passthrough_bounded__"


@overload
def passthrough(fn: F) -> F: ...


@overload
def passthrough(*, bounded: bool = False) -> Callable[[F], F]: ...


def passthrough(fn: F | None = None, *, bounded: bool = False):
    """Mark this tool as the MCP's documented escape hatch. Implements §6.30.

    Use ``@passthrough(bounded=True)`` when unrestricted underlying access
    would enable destructive or out-of-scope operations. The decorated tool's
    behavior is unchanged.
    """

    def mark(target: F) -> F:
        setattr(target, _PASSTHROUGH_MARKER, True)
        setattr(target, _BOUNDED_PASSTHROUGH_MARKER, bounded)
        return target

    return mark(fn) if fn is not None else mark


def is_passthrough(fn: object) -> bool:
    """Return True if fn was decorated with @passthrough. Helper for §6.30."""
    return bool(getattr(fn, _PASSTHROUGH_MARKER, False))


def is_bounded_passthrough(fn: object) -> bool:
    """Return True for a safety-bounded passthrough tool. Implements §6.30."""
    return bool(getattr(fn, _BOUNDED_PASSTHROUGH_MARKER, False))
