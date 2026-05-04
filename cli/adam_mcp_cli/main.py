"""`adam-mcp` CLI — Typer entrypoint."""
from __future__ import annotations
import json
import re
from pathlib import Path
import typer

# Module-level repo root, monkeypatchable for tests
_SELF_CHECK_REPO_ROOT: Path = Path(__file__).resolve().parents[2]

from .cmd_new import scaffold_new_mcp
from .cmd_audit import audit_project

app = typer.Typer(help="Adam MCP CLI.", no_args_is_help=True)


@app.callback()
def _root() -> None:
    """Adam MCP CLI."""


@app.command("new")
def cmd_new(
    name: str = typer.Argument(..., help="Project name (kebab-case recommended)"),
    description: str = typer.Option("New MCP", help="One-line description"),
    target: Path = typer.Option(None, help="Target directory; defaults to ~/Projects/<name>"),
):
    """Scaffold a new MCP project."""
    target_dir = target or (Path.home() / "Projects" / name)
    if target_dir.exists() and any(target_dir.iterdir()):
        typer.echo(f"FAIL: {target_dir} exists and is non-empty.")
        raise typer.Exit(code=1)
    scaffold_new_mcp(name=name, description=description, target_dir=target_dir)
    typer.echo(f"OK: scaffolded {name} at {target_dir}")
    typer.echo(f"hint: cd {target_dir} && uv sync && pytest tests/ -v")


@app.command("audit")
def cmd_audit(
    path: Path = typer.Argument(Path.cwd(), help="Path to MCP project; defaults to cwd"),
    self_check: bool = typer.Option(False, "--self-check", help="Run cross-link integrity self-check on the SDK repo itself"),
):
    """Run mechanical conformance check against HOUSE_STYLE.md."""
    if self_check:
        report = _self_check()
    else:
        report = audit_project(path)
    typer.echo(json.dumps(report, indent=2))
    if report["status"] == "FAIL":
        raise typer.Exit(code=1)


def _self_check() -> dict:
    """Cross-link integrity check for the SDK repo. Implements §5.27."""
    from importlib import import_module
    spec_path = Path(__file__).resolve().parents[2] / "HOUSE_STYLE.md"
    if not spec_path.exists():
        return {"status": "FAIL", "value": None, "hint": "HOUSE_STYLE.md missing", "diagnostics": [], "findings": []}
    text = spec_path.read_text()
    findings: list[dict] = []
    import re
    for m in re.finditer(r"→ Library: `?adam_mcp_py\.([\w_]+)(?:\.[\w_.]+)?`?", text):
        symbol = m.group(1)  # top-level symbol only; ignore attribute paths after the first dot
        try:
            mod = import_module("adam_mcp_py")
            if not hasattr(mod, symbol):
                findings.append({"rule": "§5.25", "severity": "FAIL",
                                 "message": f"Spec references adam_mcp_py.{symbol} but symbol is not exported",
                                 "hint": "Add to adam_mcp_py/__init__.py or update spec"})
        except ImportError as e:
            findings.append({"rule": "§5.25", "severity": "FAIL",
                             "message": f"Cannot import adam_mcp_py: {e}",
                             "hint": "Install adam-mcp-py first"})
            break
    fails = sum(1 for f in findings if f["severity"] == "FAIL")
    return {
        "status": "FAIL" if fails else "OK",
        "mode": "self-check",
        "value": None,
        "metrics": {"findings": len(findings), "fails": fails},
        "diagnostics": [f["message"] for f in findings],
        "findings": findings,
        "hint": "Update spec or library exports" if fails else None,
    }


def _self_check_v2() -> dict:
    """Extended self-check (v0.2). Verifies:
      1. Spec ↔ library cross-links (existing v0.1 behavior, preserved below)
      2. Every REGISTRY rule_id appears in HOUSE_STYLE.md
      3. Every CHANGELOG ### Breaking bullet's §X.Y resolves to a REGISTRY rule_id

    Implements §5.27 (existing) + §5.28 + §5.29 (new in v0.2).
    """
    from .audit_rules import REGISTRY

    findings: list[dict] = []
    repo = _SELF_CHECK_REPO_ROOT

    # === Check 1: spec ↔ library cross-links (preserved from v0.1) ===
    spec_path = repo / "HOUSE_STYLE.md"
    if not spec_path.exists():
        return {"status": "FAIL", "value": None,
                "hint": f"HOUSE_STYLE.md missing at {spec_path}",
                "diagnostics": [], "findings": []}
    spec_text = spec_path.read_text()

    from importlib import import_module
    for m in re.finditer(r"→ Library: `?adam_mcp_py\.([\w_]+)(?:\.[\w_.]+)?`?", spec_text):
        symbol = m.group(1)
        try:
            mod = import_module("adam_mcp_py")
            if not hasattr(mod, symbol):
                findings.append({"rule": "§5.27", "severity": "FAIL",
                                 "message": f"Spec references adam_mcp_py.{symbol} but symbol is not exported",
                                 "hint": "Add to adam_mcp_py/__init__.py or update spec"})
        except ImportError as e:
            findings.append({"rule": "§5.27", "severity": "FAIL",
                             "message": f"Cannot import adam_mcp_py: {e}",
                             "hint": "Install adam-mcp-py first"})
            break

    # === Check 3: CHANGELOG ### Breaking entries cross-link to REGISTRY ===
    changelog_path = repo / "CHANGELOG.md"
    if changelog_path.exists():
        changelog_text = changelog_path.read_text()
        registry_ids = {r.rule_id for r in REGISTRY}
        # Find the most recent version block. Format: `## [X.Y.Z]`
        version_blocks = re.split(r"^## \[", changelog_text, flags=re.MULTILINE)
        if len(version_blocks) >= 2:
            most_recent = "## [" + version_blocks[1]
            # Extract ### Breaking section
            breaking_match = re.search(
                r"^### Breaking\s*$(.*?)(?=^### |^## |\Z)",
                most_recent, flags=re.MULTILINE | re.DOTALL,
            )
            if breaking_match:
                breaking_body = breaking_match.group(1)
                for bullet in re.finditer(r"^- \*\*(§\d+\.\d+)\*\*", breaking_body, flags=re.MULTILINE):
                    cited = bullet.group(1)
                    if cited not in registry_ids:
                        findings.append({"rule": "§5.29", "severity": "FAIL",
                                         "message": f"CHANGELOG ### Breaking cites {cited} but it's not in REGISTRY",
                                         "hint": "Add the rule to audit_rules.py REGISTRY, or fix the CHANGELOG citation."})

    fails = sum(1 for f in findings if f["severity"] == "FAIL")
    return {
        "status": "FAIL" if fails else "OK",
        "mode": "self-check",
        "value": None,
        "metrics": {"findings": len(findings), "fails": fails},
        "diagnostics": [f["message"] for f in findings],
        "findings": findings,
        "hint": "Fix self-check failures before tagging a release" if fails else None,
    }


if __name__ == "__main__":
    app()
