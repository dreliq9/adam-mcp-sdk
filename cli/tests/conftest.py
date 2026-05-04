"""Shared fixtures for adam-mcp-cli tests."""
import pytest
from pathlib import Path


@pytest.fixture
def tmp_target(tmp_path: Path) -> Path:
    return tmp_path / "generated"
