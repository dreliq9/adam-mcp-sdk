"""Tests for `adam-mcp new`."""

from pathlib import Path

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
    assert "mcp==1." not in pyproject


def test_scaffold_includes_passthrough_tool(tmp_target: Path):
    scaffold_new_mcp(name="my-thing", description="x", target_dir=tmp_target)
    escape = (tmp_target / "my_thing" / "mcp" / "escape_tools.py").read_text(encoding="utf-8")
    assert "@passthrough" in escape
    assert "my_thing_passthrough" in escape
