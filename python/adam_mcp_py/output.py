"""Output directory helper — implements §2.10 of HOUSE_STYLE.md."""

from __future__ import annotations
import os
from pathlib import Path


def output_dir(name: str, *, root: str | Path | None = None) -> Path:
    """Return a predictable output directory, creating it if missing. Implements §2.10.

    Resolution order is an explicit ``root``, ``ADAM_MCP_OUTPUT_ROOT``, then
    the platform-native home directory.
    """
    configured_root = root or os.environ.get("ADAM_MCP_OUTPUT_ROOT")
    base = Path(configured_root).expanduser() if configured_root else Path.home()
    p = base / f"{name}-output"
    p.mkdir(parents=True, exist_ok=True)
    return p
