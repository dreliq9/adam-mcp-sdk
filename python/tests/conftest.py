"""Shared pytest fixtures for the adam_mcp_py library tests."""

import pytest


@pytest.fixture
def example_metric() -> dict[str, float]:
    return {"elapsed_ms": 12.3, "bytes_read": 1024.0}
