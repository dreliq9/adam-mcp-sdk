"""`adam-mcp` CLI — Typer entrypoint."""
from __future__ import annotations
import json
from pathlib import Path
import typer

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


if __name__ == "__main__":
    app()
