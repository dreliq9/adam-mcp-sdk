"""Shared fixtures for adam-greet tests."""

import pytest


@pytest.fixture(autouse=True)
def _isolated_output(tmp_path, monkeypatch):
    """Keep output isolated on Windows and POSIX without changing home variables."""
    monkeypatch.setenv("ADAM_MCP_OUTPUT_ROOT", str(tmp_path))
    yield
