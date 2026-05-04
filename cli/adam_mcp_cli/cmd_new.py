"""`adam-mcp new` — scaffold a new MCP project."""
from __future__ import annotations
import re
from pathlib import Path
from .templates_loader import render_tree


def _to_snake(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _to_pascal(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(p.capitalize() for p in parts if p)


def scaffold_new_mcp(name: str, description: str, target_dir: Path) -> None:
    """Render the _base template tree for a new MCP. Implements `adam-mcp new`."""
    context = {
        "name": name,
        "name_snake": _to_snake(name),
        "name_pascal": _to_pascal(name),
        "description": description,
    }
    render_tree(target_dir, context)
