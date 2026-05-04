"""Pytest helpers for testing adam-mcp-py-based MCPs."""
from __future__ import annotations
import pytest

from .base_server import BaseServer


@pytest.fixture
def in_process_server() -> BaseServer:
    """Returns a BaseServer suitable for in-process tool invocation in tests."""
    return BaseServer(name="test-server")
