"""Tests for adam_mcp_py.output_dir — implements §2.10."""

from pathlib import Path
from adam_mcp_py import output_dir


def test_output_dir_default_location():
    p = output_dir("adam-greet")
    assert p == Path.home() / "adam-greet-output"


def test_output_dir_creates_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    p = output_dir("test-mcp")
    assert p.exists()
    assert p.is_dir()
    assert p == tmp_path / "test-mcp-output"


def test_output_dir_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    p1 = output_dir("test-mcp")
    p2 = output_dir("test-mcp")
    assert p1 == p2
    assert p1.exists()
