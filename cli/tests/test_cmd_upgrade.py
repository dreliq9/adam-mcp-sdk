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
