"""BaseServer — house-style FastMCP wrapper.

Enforces:
- Every tool returns Result. Non-Result returns are coerced to FAIL with hint pointing to §1.1.
- Exceptions in tools become FAIL Results with hints, never propagate raw.
- Stderr-only logging (so stdio transport stays clean).
"""
from __future__ import annotations
import logging
import sys
import traceback
from functools import wraps
from typing import Any, Callable

from .result import Result, Status

logger = logging.getLogger("adam_mcp_py")


def _configure_stderr_logging() -> None:
    """Configure logging to use stderr only — never corrupt stdio JSON-RPC."""
    if logger.handlers:
        return
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)


def _wrap_tool(fn: Callable) -> Callable:
    """Wrap a tool so:
    - Non-Result returns become Result.fail with hint pointing to §1.1.
    - Exceptions become Result.fail with the traceback in diagnostics.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except Exception as e:
            tb = traceback.format_exc()
            return Result.fail(
                hint=f"Tool '{fn.__name__}' raised: {e}. Check inputs or try the escape hatch.",
                diagnostics=[tb],
            )
        if not isinstance(result, Result):
            return Result.fail(
                hint=(
                    f"Tool '{fn.__name__}' did not return a Result. "
                    f"All tools must return adam_mcp_py.Result (§1.1)."
                ),
                diagnostics=[f"actual return type: {type(result).__name__}"],
            )
        return result
    return wrapper


class BaseServer:
    """Wraps FastMCP with house-style enforcement.

    Implements parts of §1.1 (Result enforcement), §1.4 (mode/path), §2.5 (three-layer).

    Usage:
        server = BaseServer(name="my-mcp")

        @server.tool()
        def my_tool(x: int) -> Result[int]:
            return Result.ok(value=x * 2)
    """

    def __init__(self, name: str):
        _configure_stderr_logging()
        # Lazy import to avoid hard-failing when mcp isn't installed
        try:
            from mcp.server.fastmcp import FastMCP
            self._fastmcp: Any = FastMCP(name)
        except ImportError:
            logger.warning("mcp package not available; BaseServer running in offline mode")
            self._fastmcp = None
        self.name = name

    def tool(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator that registers a Result-returning tool with the underlying FastMCP."""
        def decorator(fn: Callable) -> Callable:
            wrapped = _wrap_tool(fn)
            # Preserve passthrough markers
            if getattr(fn, "__adam_mcp_passthrough__", False):
                setattr(wrapped, "__adam_mcp_passthrough__", True)
            if self._fastmcp is not None:
                self._fastmcp.tool(*args, **kwargs)(wrapped)
            return wrapped
        return decorator

    def run(self) -> None:
        """Run the underlying FastMCP server."""
        if self._fastmcp is None:
            raise RuntimeError("mcp package not installed; cannot run server")
        self._fastmcp.run()
