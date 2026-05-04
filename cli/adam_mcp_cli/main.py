"""`adam-mcp` CLI — Typer entrypoint."""
from __future__ import annotations
import sys
from pathlib import Path
import typer

from .cmd_new import scaffold_new_mcp

app = typer.Typer(help="Adam MCP CLI.", no_args_is_help=True)


@app.callback()
def _root() -> None:
    """Adam MCP CLI."""


@app.command("new")
def cmd_new(
    name: str = typer.Argument(..., help="Project name (kebab-case recommended)"),
    description: str = typer.Option("New MCP", help="One-line description"),
    target: Path = typer.Option(
        None, help="Target directory; defaults to ~/Projects/<name>"
    ),
):
    """Scaffold a new MCP project."""
    target_dir = target or (Path.home() / "Projects" / name)
    if target_dir.exists() and any(target_dir.iterdir()):
        typer.echo(f"FAIL: {target_dir} exists and is non-empty.")
        raise typer.Exit(code=1)
    scaffold_new_mcp(name=name, description=description, target_dir=target_dir)
    typer.echo(f"OK: scaffolded {name} at {target_dir}")
    typer.echo(f"hint: cd {target_dir} && uv sync && pytest tests/ -v")


if __name__ == "__main__":
    app()
