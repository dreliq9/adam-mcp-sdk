"""Template loader. Walks the _base template tree and renders each .j2 file with substitutions."""
from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, BaseLoader, StrictUndefined

# Templates ship inside the python/ workspace member.
_TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "python" / "templates" / "_base"


def template_root() -> Path:
    return _TEMPLATES_ROOT


def render_tree(target_dir: Path, context: dict[str, str]) -> None:
    """Render the _base template tree into target_dir.

    File and directory names containing {{name_snake}} are substituted at copy time.
    File contents ending in .j2 are rendered as Jinja2 templates; .j2 suffix is stripped.
    """
    env = Environment(loader=BaseLoader(), undefined=StrictUndefined)
    target_dir.mkdir(parents=True, exist_ok=True)
    for src in _TEMPLATES_ROOT.rglob("*"):
        rel = src.relative_to(_TEMPLATES_ROOT)
        # Substitute path components
        rel_str = str(rel)
        for key, val in context.items():
            rel_str = rel_str.replace("{{" + key + "}}", val)
        dest = target_dir / rel_str
        if src.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        if src.suffix == ".j2":
            dest = dest.with_suffix("")  # strip .j2
            tmpl = env.from_string(src.read_text())
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(tmpl.render(**context))
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
