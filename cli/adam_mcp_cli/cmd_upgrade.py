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


def upgrade(path: Path, target: Optional[str], dry_run: bool) -> dict:
    """Bump the adam-mcp-py pin in `path` and run audit. Returns Result-shaped dict.

    Returns dict with keys: status, mode_tag, value, raw, hint, metrics, diagnostics.
    Behavior matches HOUSE_STYLE.md §1 (Result envelope) and design spec §7.
    """
    pyproject_path = path / "pyproject.toml"
    if not pyproject_path.exists():
        return _result_fail(
            hint=f"pyproject.toml not found at {pyproject_path}. "
                 "Is this an MCP project root?",
        )

    try:
        current = parse_pin(pyproject_path)
    except Exception as e:
        return _result_fail(raw=str(e), hint=f"Cannot parse {pyproject_path}: {e}")

    if current is None:
        return _result_fail(
            hint="pyproject.toml has no adam-mcp-py dependency. "
                 "Run `adam-mcp new` for a fresh project, or add the dep manually.",
        )

    target = target or fetch_latest_version()

    if target == current:
        return _result_ok(value={"current": current, "target": target},
                          hint=f"Already on {current}.")

    if version_lt(target, current):
        return _result_fail(
            hint=f"Cannot downgrade ({current} → {target}). "
                 "adam-mcp does not support downgrades. Edit pyproject.toml manually if needed.",
        )

    if dry_run:
        return _result_ok(
            value={"current": current, "target": target,
                   "would_edit": [str(pyproject_path)]},
            hint=f"Dry run: would upgrade {current} → {target}.",
        )

    update_pin(pyproject_path, target)

    sync = subprocess.run(["uv", "sync"], cwd=str(path), capture_output=True, text=True)
    if sync.returncode != 0:
        return _result_fail(
            raw=sync.stderr,
            hint="`uv sync` failed — likely a transitive dep conflict. "
                 "Read the error above, fix pyproject.toml, then retry.",
        )

    # Run audit
    from .cmd_audit import audit_project
    audit_report = audit_project(path)
    findings = audit_report.get("findings", [])

    status = "WARN" if findings else "OK"
    return {
        "status": status,
        "mode_tag": f"upgrade:{current}→{target}",
        "value": {"current": current, "target": target, "findings": findings},
        "raw": None,
        "metrics": {"findings_count": len(findings)},
        "diagnostics": [f["message"] for f in findings],
        "hint": (
            f"Upgraded {current} → {target}. {len(findings)} finding(s) — work through them."
            if findings else f"Upgraded {current} → {target}. No findings."
        ),
    }


def _result_ok(value=None, hint=None) -> dict:
    return {"status": "OK", "mode_tag": None, "value": value, "raw": None,
            "metrics": {}, "diagnostics": [], "hint": hint}


def _result_fail(raw=None, hint=None) -> dict:
    return {"status": "FAIL", "mode_tag": None, "value": None, "raw": raw,
            "metrics": {}, "diagnostics": [], "hint": hint}
