"""`adam-mcp` CLI — Typer entrypoint."""

from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional
import typer

from .cmd_new import scaffold_new_mcp  # noqa: E402
from .cmd_audit import audit_project  # noqa: E402

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
    self_check: bool = typer.Option(
        False, "--self-check", help="Run cross-link integrity self-check on the SDK repo itself"
    ),
):
    """Run mechanical conformance check against HOUSE_STYLE.md."""
    if self_check:
        report = _self_check_v2(path.resolve())
    else:
        report = audit_project(path)
    typer.echo(json.dumps(report, indent=2))
    if report["status"] == "FAIL":
        raise typer.Exit(code=1)


@app.command("upgrade")
def cmd_upgrade(
    path: Path = typer.Argument(Path.cwd(), help="MCP project root; defaults to cwd"),
    to: Optional[str] = typer.Option(
        None, "--to", help="Target adam-mcp-py version (default: latest)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print what would happen, don't edit files"
    ),
):
    """Bump adam-mcp-py pin and run audit. See HOUSE_STYLE.md §7."""
    from .cmd_upgrade import upgrade

    report = upgrade(path, target=to, dry_run=dry_run)
    typer.echo(json.dumps(report, indent=2))
    if report["status"] == "FAIL":
        raise typer.Exit(code=1)


_SELF_CHECK_SENTINELS = (
    "HOUSE_STYLE.md",
    "CHANGELOG.md",
    "cli/adam_mcp_cli/audit_rules.py",
    "python/adam_mcp_py/validation.py",
)


def _self_check_v2(repo_root: Path | None = None) -> dict:
    """Run SDK repository cross-link checks from an explicit checkout root."""
    from .audit_rules import REGISTRY

    repo = (repo_root or Path.cwd()).resolve()
    missing = [relative for relative in _SELF_CHECK_SENTINELS if not (repo / relative).is_file()]
    if missing:
        return {
            "status": "FAIL",
            "mode": "self-check",
            "value": None,
            "metrics": {"findings": 0, "fails": 1},
            "diagnostics": missing,
            "findings": [],
            "hint": "Run audit --self-check from the adam-mcp-sdk checkout root.",
        }

    findings: list[dict] = []

    # === Check 1: spec ↔ library cross-links (preserved from v0.1) ===
    spec_path = repo / "HOUSE_STYLE.md"
    spec_text = spec_path.read_text(encoding="utf-8")

    from importlib import import_module

    for m in re.finditer(r"→ Library: `?adam_mcp_py\.([\w_]+)(?:\.[\w_.]+)?`?", spec_text):
        symbol = m.group(1)
        try:
            mod = import_module("adam_mcp_py")
            if not hasattr(mod, symbol):
                findings.append(
                    {
                        "rule": "§5.27",
                        "severity": "FAIL",
                        "message": f"Spec references adam_mcp_py.{symbol} but symbol is not exported",
                        "hint": "Add to adam_mcp_py/__init__.py or update spec",
                    }
                )
        except ImportError as e:
            findings.append(
                {
                    "rule": "§5.27",
                    "severity": "FAIL",
                    "message": f"Cannot import adam_mcp_py: {e}",
                    "hint": "Install adam-mcp-py first",
                }
            )
            break

    # === Check 2: every REGISTRY rule_id appears in HOUSE_STYLE.md ===
    for rule in REGISTRY:
        # Match either `## §X.Y` headers or `**§X.Y**` references
        pattern = re.escape(rule.rule_id)
        if not re.search(rf"(?:^##+ {pattern}\b|\*\*{pattern}\*\*)", spec_text, flags=re.MULTILINE):
            findings.append(
                {
                    "rule": "§5.28",
                    "severity": "FAIL",
                    "message": f"REGISTRY contains {rule.rule_id} but HOUSE_STYLE.md does not document it",
                    "hint": f"Add a section for {rule.rule_id} to HOUSE_STYLE.md, or remove the rule from REGISTRY.",
                }
            )

    # === Check 3: CHANGELOG ### Breaking entries cross-link to REGISTRY ===
    changelog_path = repo / "CHANGELOG.md"
    if changelog_path.exists():
        changelog_text = changelog_path.read_text(encoding="utf-8")
        registry_ids = {r.rule_id for r in REGISTRY}
        # Find the most recent version block. Format: `## [X.Y.Z]`
        version_blocks = re.split(r"^## \[", changelog_text, flags=re.MULTILINE)
        if len(version_blocks) >= 2:
            most_recent = "## [" + version_blocks[1]
            # Extract ### Breaking section
            breaking_match = re.search(
                r"^### Breaking\s*$(.*?)(?=^### |^## |\Z)",
                most_recent,
                flags=re.MULTILINE | re.DOTALL,
            )
            if breaking_match:
                breaking_body = breaking_match.group(1)
                for bullet in re.finditer(
                    r"^- \*\*(§\d+\.\d+)\*\*", breaking_body, flags=re.MULTILINE
                ):
                    cited = bullet.group(1)
                    if cited not in registry_ids:
                        findings.append(
                            {
                                "rule": "§5.29",
                                "severity": "FAIL",
                                "message": f"CHANGELOG ### Breaking cites {cited} but it's not in REGISTRY",
                                "hint": "Add the rule to audit_rules.py REGISTRY, or fix the CHANGELOG citation.",
                            }
                        )

    # === Check 4: validates() wrapper accepts `input` as its parameter name ===
    # Guards the contract every @validates-decorated tool depends on. If this drifts,
    # every MCP using the SDK breaks at runtime with 'unexpected keyword argument'.
    import ast

    validation_path = repo / "python" / "adam_mcp_py" / "validation.py"
    if validation_path.exists():
        try:
            tree = ast.parse(validation_path.read_text(encoding="utf-8"))
            wrapper_param = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == "wrapper":
                    args = node.args.args
                    wrapper_param = args[0].arg if args else None
                    break
            if wrapper_param != "input":
                findings.append(
                    {
                        "rule": "§1.5",
                        "severity": "FAIL",
                        "message": (
                            f"validation.py wrapper first param is {wrapper_param!r}, must be 'input' — "
                            f"will break every @validates-decorated tool at runtime."
                        ),
                        "hint": "Rename the wrapper parameter (and its uses) back to `input`.",
                    }
                )
        except (SyntaxError, OSError) as e:
            findings.append(
                {
                    "rule": "§1.5",
                    "severity": "FAIL",
                    "message": f"Cannot parse validation.py: {e}",
                    "hint": "Restore validation.py from git.",
                }
            )

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
