"""`adam-mcp upgrade` — bump the adam-mcp-py pin and run audit-as-migration.

See HOUSE_STYLE.md §7 (Upgrade system) and the design doc at
docs/superpowers/specs/2026-05-04-mcp-sdk-upgrade-system-design.md.
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path
from typing import Optional

import tomlkit


def parse_pin(pyproject_path: Path) -> Optional[str]:
    """Read the adam-mcp-py version pin from pyproject.toml.

    Returns:
        - exact version string for `adam-mcp-py==X.Y.Z`
        - lower bound for `adam-mcp-py>=X.Y,<A.B` (per spec §2.11, MCP projects pin
          exact, but range pins are tolerated and the lower bound is used)
        - None if adam-mcp-py is not in dependencies

    Raises tomlkit's parse errors on malformed TOML.
    """
    doc = tomlkit.parse(pyproject_path.read_text())
    deps = doc.get("project", {}).get("dependencies", [])
    for dep in deps:
        dep_str = str(dep)
        if dep_str.startswith("adam-mcp-py"):
            # Match ==X.Y.Z, >=X.Y(.Z), etc.
            m = re.match(r"adam-mcp-py\s*(==|>=)\s*([\d.]+)", dep_str)
            if m:
                return m.group(2)
    return None


def _version_tuple(v: str) -> tuple:
    """Convert '0.2.10' to (0, 2, 10) for numeric comparison.

    Padded with zeros so '0.2' and '0.2.0' compare equal.
    """
    parts = v.split(".")
    return tuple(int(p) for p in parts) + (0,) * (3 - len(parts))


def version_lt(a: str, b: str) -> bool:
    """True if version a is less than version b. Numeric, not lexicographic."""
    return _version_tuple(a) < _version_tuple(b)


def update_pin(pyproject_path: Path, new_version: str) -> None:
    """Rewrite pyproject.toml to pin adam-mcp-py exactly at new_version.

    Replaces any existing adam-mcp-py pin (==, >=, range) with `==new_version`.
    Preserves order, comments, and other dependencies via tomlkit.
    """
    doc = tomlkit.parse(pyproject_path.read_text())
    deps = doc["project"]["dependencies"]
    for i, dep in enumerate(deps):
        if str(dep).startswith("adam-mcp-py"):
            deps[i] = f"adam-mcp-py=={new_version}"
            break
    pyproject_path.write_text(tomlkit.dumps(doc))


def _pypi_latest() -> Optional[str]:
    """Query PyPI for the latest released adam-mcp-py version. Returns None on any error.

    Note: as of v0.2 launch, adam-mcp-py is not published on PyPI; this returns None.
    Kept as the preferred source for when publishing happens.
    """
    try:
        import urllib.request, json
        with urllib.request.urlopen("https://pypi.org/pypi/adam-mcp-py/json", timeout=3) as r:
            data = json.load(r)
        return data["info"]["version"]
    except Exception:
        return None


def fetch_latest_version() -> str:
    """Resolve the latest adam-mcp-py version. PyPI first; fall back to installed __version__."""
    pypi = _pypi_latest()
    if pypi is not None:
        return pypi
    import adam_mcp_py
    return adam_mcp_py.__version__
