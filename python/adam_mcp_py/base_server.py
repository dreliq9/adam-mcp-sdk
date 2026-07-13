"""BaseServer — house-style FastMCP wrapper.

Enforces:
- Every tool returns Result. Non-Result returns are coerced to FAIL with hint pointing to §1.1.
- Exceptions in tools become FAIL Results with hints, never propagate raw.
- Stderr-only logging (so stdio transport stays clean).
"""

from __future__ import annotations
import inspect
import logging
import sys
from functools import wraps
from typing import Any, Callable

from .result import Result

logger = logging.getLogger("adam_mcp_py")


def _configure_stderr_logging() -> None:
    """Configure logging to use stderr only — never corrupt stdio JSON-RPC."""
    if logger.handlers:
        return
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)


def _exception_result(fn: Callable, error: Exception) -> Result:
    """Turn a tool exception into a safe Result while logging details to stderr."""
    logger.exception("Tool '%s' raised", fn.__name__, exc_info=error)
    return Result.fail(
        hint=f"Tool '{fn.__name__}' raised. Check inputs or try the escape hatch.",
        diagnostics=[f"{type(error).__name__}: {error}"],
    )


def _validated_result(fn: Callable, result: object) -> Result:
    """Enforce the Result contract after a sync or async tool completes."""
    if isinstance(result, Result):
        return result
    return Result.fail(
        hint=(
            f"Tool '{fn.__name__}' did not return a Result. "
            f"All tools must return adam_mcp_py.Result (§1.1)."
        ),
        diagnostics=[f"actual return type: {type(result).__name__}"],
    )


def _wrap_tool(fn: Callable) -> Callable:
    """Wrap a sync or async tool with Result and exception enforcement."""

    if inspect.iscoroutinefunction(fn):

        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await fn(*args, **kwargs)
            except Exception as error:
                return _exception_result(fn, error)
            return _validated_result(fn, result)

        return async_wrapper

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
        except Exception as error:
            return _exception_result(fn, error)
        return _validated_result(fn, result)

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

    def __init__(self, name: str, **fastmcp_kwargs: Any):
        _configure_stderr_logging()
        # Lazy import to avoid hard-failing when mcp isn't installed
        try:
            from mcp.server.fastmcp import FastMCP

            self._fastmcp: Any = FastMCP(name, **fastmcp_kwargs)
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
            if getattr(fn, "__adam_mcp_passthrough_bounded__", False):
                setattr(wrapped, "__adam_mcp_passthrough_bounded__", True)
            if self._fastmcp is not None:
                self._fastmcp.tool(*args, **kwargs)(wrapped)
            return wrapped

        return decorator

    def run(self, **kwargs: Any) -> None:
        """Run the underlying FastMCP server."""
        if self._fastmcp is None:
            raise RuntimeError("mcp package not installed; cannot run server")
        self._fastmcp.run(**kwargs)
