"""Required-section checks for LLM_GUIDE.md files in MCP projects.

Implements §3.14 + §6.32. Used by `adam-mcp audit`.
"""

from __future__ import annotations
from pathlib import Path

REQUIRED_SECTIONS: list[str] = [
    "## Overview",
    "## Critical workflow",
    "## Tool categories",
    "## Parameter gotchas",
    "## Failure",  # matches "## Failure → fix" or "## Failure / fix"
    "## Mode",  # matches "## Mode/path transparency" etc.
    "## Escape hatches",  # §6.32 — required
]


def check_llm_guide(path: Path) -> list[str]:
    """Return a list of missing required sections (empty list = pass)."""
    if not path.exists():
        return [f"LLM_GUIDE.md not found at {path}"]
    text = path.read_text(encoding="utf-8")
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in text:
            missing.append(f"Missing section in LLM_GUIDE.md: '{section}'")
    return missing
