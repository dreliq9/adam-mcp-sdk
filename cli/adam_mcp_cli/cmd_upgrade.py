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
