"""Pluggable backend protocol — implements §2.6 of HOUSE_STYLE.md."""
from __future__ import annotations
from typing import Protocol, runtime_checkable, Sequence


@runtime_checkable
class BackendProtocol(Protocol):
    """Backend Protocol. Implements §2.6.

    Attributes:
        mode_tag: short tag identifying this backend (e.g., "[LOCAL]", "[IPC]").
        available: True if this backend can currently serve requests.
    """
    mode_tag: str
    available: bool

    def call(self, payload: dict) -> dict:
        ...


def detect_backend(backends: Sequence[BackendProtocol]) -> BackendProtocol | None:
    """Return the first backend with .available = True, or None. Helper for §2.6."""
    for b in backends:
        if b.available:
            return b
    return None
