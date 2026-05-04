"""Tests for `adam-mcp upgrade`."""
from pathlib import Path
import pytest


def test_parse_pin_returns_exact_version(tmp_path: Path):
    from adam_mcp_cli.cmd_upgrade import parse_pin
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\nversion = "0.1.0"\n'
        'dependencies = ["adam-mcp-py==0.1.0", "typer>=0.12"]\n'
    )
    assert parse_pin(tmp_path / "pyproject.toml") == "0.1.0"


def test_parse_pin_returns_lower_bound_for_range(tmp_path: Path):
    from adam_mcp_cli.cmd_upgrade import parse_pin
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["adam-mcp-py>=0.2,<0.3"]\n'
    )
    assert parse_pin(tmp_path / "pyproject.toml") == "0.2"


def test_parse_pin_returns_none_when_no_dep(tmp_path: Path):
    from adam_mcp_cli.cmd_upgrade import parse_pin
    (tmp_path / "pyproject.toml").write_text('[project]\ndependencies = ["typer"]\n')
    assert parse_pin(tmp_path / "pyproject.toml") is None


def test_parse_pin_raises_on_malformed_toml(tmp_path: Path):
    from adam_mcp_cli.cmd_upgrade import parse_pin
    (tmp_path / "pyproject.toml").write_text("this is not toml [[[")
    with pytest.raises(Exception):
        parse_pin(tmp_path / "pyproject.toml")


def test_version_lt_basic():
    from adam_mcp_cli.cmd_upgrade import version_lt
    assert version_lt("0.1.0", "0.2.0") is True
    assert version_lt("0.2.0", "0.1.0") is False
    assert version_lt("0.1.0", "0.1.0") is False
    assert version_lt("0.1.10", "0.1.2") is False  # numeric compare, not lex
    assert version_lt("0.2", "0.2.0") is False     # equal-after-normalization


def test_update_pin_writes_exact_version(tmp_path: Path):
    from adam_mcp_cli.cmd_upgrade import update_pin
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        '[project]\nname = "x"\n'
        'dependencies = ["adam-mcp-py==0.1.0", "typer>=0.12"]\n'
    )
    update_pin(pyproj, "0.2.0")
    text = pyproj.read_text()
    assert "adam-mcp-py==0.2.0" in text
    assert "adam-mcp-py==0.1.0" not in text
    assert "typer>=0.12" in text  # unrelated dep preserved


def test_update_pin_replaces_range_with_exact(tmp_path: Path):
    from adam_mcp_cli.cmd_upgrade import update_pin
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        '[project]\ndependencies = ["adam-mcp-py>=0.1,<0.2"]\n'
    )
    update_pin(pyproj, "0.2.0")
    text = pyproj.read_text()
    assert "adam-mcp-py==0.2.0" in text
    assert ">=0.1" not in text
