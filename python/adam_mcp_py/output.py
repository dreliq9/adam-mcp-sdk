"""Output directory helper — implements §2.10 of HOUSE_STYLE.md."""
from __future__ import annotations
from pathlib import Path


def output_dir(name: str) -> Path:
    """Return ~/<name>-output/, creating it if missing. Implements §2.10."""
    p = Path.home() / f"{name}-output"
    p.mkdir(parents=True, exist_ok=True)
    return p
