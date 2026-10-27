"""Tests for `adam-mcp new`."""

from pathlib import Path
import json
import tomllib

import pytest

from adam_mcp_cli.cmd_new import scaffold_new_mcp


def test_scaffold_creates_full_layout(tmp_target: Path):
    scaffold_new_mcp(name="my-thing", description="testing scaffold", target_dir=tmp_target)
    # Layout files
    assert (tmp_target / "pyproject.toml").exists()
    assert (tmp_target / "SPEC.md").exists()
    assert (tmp_target / "LLM_GUIDE.md").exists()
    assert (tmp_target / "CLAUDE.md").exists()
    assert (tmp_target / "README.md").exists()
    assert (tmp_target / "CHANGELOG.md").exists()
    assert (tmp_target / "ROADMAP.md").exists()
    assert (tmp_target / "DECISIONS.md").exists()
    assert (tmp_target / "AUDIT.md").exists()
    assert (tmp_target / "server.json").exists()
    # Code layout
    assert (tmp_target / "my_thing" / "__init__.py").exists()
    assert (tmp_target / "my_thing" / "types.py").exists()
    assert (tmp_target / "my_thing" / "schema.py").exists()
    assert (tmp_target / "my_thing" / "cli.py").exists()
    assert (tmp_target / "my_thing" / "backends" / "__init__.py").exists()
    assert (tmp_target / "my_thing" / "backends" / "default.py").exists()
    assert (tmp_target / "my_thing" / "mcp" / "__init__.py").exists()
    assert (tmp_target / "my_thing" / "mcp" / "core_tools.py").exists()
    assert (tmp_target / "my_thing" / "mcp" / "escape_tools.py").exists()
    assert (tmp_target / "my_thing" / "mcp" / "server.py").exists()
    assert (tmp_target / "tests" / "conftest.py").exists()
    assert (tmp_target / "tests" / "test_core_tools.py").exists()


def test_scaffold_substitutes_name(tmp_target: Path):
    scaffold_new_mcp(name="my-thing", description="x", target_dir=tmp_target)
    pyproject = (tmp_target / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "my-thing"' in pyproject
    assert "my_thing" in pyproject  # snake_case package name
    init = (tmp_target / "my_thing" / "__init__.py").read_text(encoding="utf-8")
    assert "my-thing" in init


def test_scaffold_pins_current_adam_and_mcp_v2(tmp_target: Path):
    scaffold_new_mcp(name="my-thing", description="x", target_dir=tmp_target)
    pyproject = (tmp_target / "pyproject.toml").read_text(encoding="utf-8")
    assert '"adam-mcp-py==0.3.3"' in pyproject
    assert '"mcp==2.0.0"' in pyproject
    assert '"pydantic~=2.5"' in pyproject
    assert "mcp==1." not in pyproject


def test_scaffold_includes_passthrough_tool(tmp_target: Path):
    scaffold_new_mcp(name="my-thing", description="x", target_dir=tmp_target)
    escape = (tmp_target / "my_thing" / "mcp" / "escape_tools.py").read_text(encoding="utf-8")
    assert "@passthrough" in escape
    assert "my_thing_passthrough" in escape


def test_scaffold_escapes_metadata_and_python_docstring_values(tmp_target: Path):
    description = 'A "quoted" line\\with a slash\nand emoji 🚀\x7f'
    scaffold_new_mcp(name="my-thing", description=description, target_dir=tmp_target)

    pyproject = tomllib.loads((tmp_target / "pyproject.toml").read_text(encoding="utf-8"))
    server = json.loads((tmp_target / "server.json").read_text(encoding="utf-8"))
    assert pyproject["project"]["description"] == description
    assert server["description"] == description

    package_init = tmp_target / "my_thing" / "__init__.py"
    namespace = {}
    source = package_init.read_text(encoding="utf-8")
    exec(compile(source, str(package_init), "exec"), namespace)
    assert namespace["__doc__"] == f"my-thing — {description}"


@pytest.mark.parametrize("name", ["../escape", "has space", "bad/name", "class", "async"])
def test_scaffold_rejects_unsafe_project_names(name: str, tmp_target: Path):
    with pytest.raises(ValueError, match="project name"):
        scaffold_new_mcp(name=name, description="x", target_dir=tmp_target)
    assert not tmp_target.exists()


@pytest.mark.parametrize(
    ("name", "package_name"),
    [("two--hyphens", "two_hyphens"), ("9project", "_9project"), ("my.project", "my_project")],
)
def test_scaffold_allows_pep508_names_and_generated_python_compiles(
    name: str, package_name: str, tmp_target: Path
):
    scaffold_new_mcp(name=name, description="x", target_dir=tmp_target)

    package = tmp_target / package_name
    python_files = list(tmp_target.rglob("*.py"))
    assert python_files
    for path in python_files:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    assert (package / "mcp" / "server.py").is_file()
    metadata = tomllib.loads((tmp_target / "pyproject.toml").read_text(encoding="utf-8"))
    assert metadata["project"]["scripts"] == {
        name: f"{package_name}.cli:main",
        f"{name}-mcp": f"{package_name}.mcp.server:main",
    }
