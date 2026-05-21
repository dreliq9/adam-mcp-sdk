"""Shared fixtures for adam-greet tests."""

import pytest


@pytest.fixture(autouse=True)
def _isolated_output(tmp_path, monkeypatch):
    """Redirect ~/adam-greet-output/ into a tmp_path for tests."""
    monkeypatch.setenv("HOME", str(tmp_path))
    yield
