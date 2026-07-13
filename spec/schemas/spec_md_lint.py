"""Required-section checks for SPEC.md files in MCP projects.

Implements parts of §3.13 (SPEC.md is law). Used by `adam-mcp audit`.
"""

from __future__ import annotations
from pathlib import Path

REQUIRED_SECTIONS: list[str] = [
    "# ",  # title (any H1 starting with "# ")
    "## What this is",
    "## Repository layout",
    "## Dependencies",
]


def check_spec_md(path: Path) -> list[str]:
    """Return a list of missing required sections (empty list = pass)."""
    if not path.exists():
        return [f"SPEC.md not found at {path}"]
    text = path.read_text(encoding="utf-8")
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            missing.append(f"Missing section in SPEC.md: '{section}'")
    return missing
