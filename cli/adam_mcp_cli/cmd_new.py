"""`adam-mcp new` — scaffold a new MCP project."""

from __future__ import annotations
import json
import keyword
import re
from pathlib import Path
from .templates_loader import render_tree

_SAFE_PROJECT_NAME = re.compile(r"[A-Za-z0-9]+(?:[-_.]+[A-Za-z0-9]+)*\Z")


def _quoted_string(value: str) -> str:
    """Return JSON/TOML-compatible quoted string syntax for metadata values."""
    # TOML forbids a literal DEL character even though JSON permits it.
    return json.dumps(value, ensure_ascii=False).replace("\x7f", r"\u007f")


def _to_snake(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _to_pascal(name: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", name)
    return "".join(p.capitalize() for p in parts if p)


def scaffold_new_mcp(name: str, description: str, target_dir: Path) -> None:
    """Render the _base template tree for a new MCP. Implements `adam-mcp new`."""
    if not _SAFE_PROJECT_NAME.fullmatch(name):
        raise ValueError(
            "project name must contain ASCII letters or numbers separated by hyphens, "
            "underscores, or dots"
        )
    package_name = _to_snake(name)
    if not package_name.isidentifier():
        package_name = f"_{package_name}"
    if keyword.iskeyword(package_name):
        raise ValueError(f"project name produces Python keyword package name {package_name!r}")
    try:
        description.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("description must be valid UTF-8 text") from error

    context = {
        "name": name,
        "name_snake": package_name,
        "name_pascal": _to_pascal(name),
        "description": description,
        # JSON string syntax is also valid for TOML basic strings. Keeping the
        # quotes in the context prevents user text from escaping metadata values.
        "name_literal": _quoted_string(name),
        "cli_script_literal": _quoted_string(name),
        "mcp_script_literal": _quoted_string(f"{name}-mcp"),
        "description_literal": _quoted_string(description),
        "description_python_literal": repr(description),
    }
    render_tree(target_dir, context)
