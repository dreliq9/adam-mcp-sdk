"""Render the packaged scaffold resource tree."""

from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from jinja2 import BaseLoader, Environment, StrictUndefined


def template_root() -> Traversable:
    """Return the canonical packaged scaffold tree."""
    return resources.files("adam_mcp_cli.templates").joinpath("_base")


def _render_name(name: str, context: dict[str, str]) -> str:
    for key, value in context.items():
        name = name.replace("{{" + key + "}}", value)
    return name


def _render_resource(
    source: Traversable,
    destination: Path,
    context: dict[str, str],
    environment: Environment,
) -> None:
    for child in source.iterdir():
        rendered_name = _render_name(child.name, context)
        target = destination / rendered_name
        if child.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            _render_resource(child, target, context, environment)
        elif child.name.endswith(".j2"):
            target = destination / rendered_name.removesuffix(".j2")
            target.parent.mkdir(parents=True, exist_ok=True)
            template = environment.from_string(child.read_text(encoding="utf-8"))
            target.write_text(template.render(**context), encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(child.read_bytes())


def render_tree(target_dir: Path, context: dict[str, str]) -> None:
    """Render the packaged scaffold into ``target_dir``."""
    source = template_root()
    if not source.is_dir():
        raise RuntimeError("adam-mcp-cli package is missing templates/_base")
    environment = Environment(loader=BaseLoader(), undefined=StrictUndefined)
    target_dir.mkdir(parents=True, exist_ok=True)
    _render_resource(source, target_dir, context, environment)
