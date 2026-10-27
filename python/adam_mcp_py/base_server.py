"""BaseServer — house-style wrapper around MCP Python SDK v2's MCPServer.

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
from typing import Any, Callable, get_origin

from .result import Result

logger = logging.getLogger("adam_mcp_py")


def _configure_stderr_logging() -> None:
    """Configure logging to use stderr only — never corrupt stdio protocol traffic."""
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


def _registration_signature(fn: Callable, wrapped: Callable) -> None:
    """Advertise the envelope that enforcement actually returns, including FAIL."""
    signature = inspect.signature(fn, eval_str=False)
    namespace = getattr(inspect.unwrap(fn), "__globals__", {})

    def resolve(annotation: Any) -> Any:
        # These are trusted Python function annotations, as evaluated by MCP.
        return eval(annotation, namespace) if isinstance(annotation, str) else annotation

    parameters = [
        parameter.replace(annotation=resolve(parameter.annotation))
        for parameter in signature.parameters.values()
    ]
    try:
        annotation = resolve(signature.return_annotation)
    except NameError:
        # A bad return hint must not prevent the actual Result envelope from
        # being registered. Unresolved input annotations still fail explicitly.
        annotation = Result[Any]
    if annotation is not Result and get_origin(annotation) is not Result:
        annotation = Result[Any]
    wrapped.__signature__ = signature.replace(parameters=parameters, return_annotation=annotation)


class BaseServer:
    """Wrap MCPServer with Adam house-style enforcement.

    Implements parts of §1.1 (Result enforcement), §1.4 (mode/path), and
    §2.5 (three-layer architecture). MCP Python SDK v2 renamed the high-level
    server from FastMCP to MCPServer; the decorator surface remains compatible.

    Usage:
        server = BaseServer(name="my-mcp")

        @server.tool()
        def my_tool(x: int) -> Result[int]:
            return Result.ok(value=x * 2)
    """

    def __init__(self, name: str, **mcp_server_kwargs: Any):
        _configure_stderr_logging()
        # Lazy import keeps the module importable in tooling contexts where
        # runtime dependencies have intentionally not been installed yet.
        try:
            from mcp.server import MCPServer

            self._mcp_server: Any = MCPServer(name, **mcp_server_kwargs)
        except ImportError:
            logger.warning("mcp package not available; BaseServer running in offline mode")
            self._mcp_server = None
        self.name = name

    @property
    def mcp_server(self) -> Any:
        """Expose the underlying MCPServer for in-memory clients and advanced integration."""
        if self._mcp_server is None:
            raise RuntimeError("mcp package not installed; MCPServer is unavailable")
        return self._mcp_server

    def tool(self, *args: Any, **kwargs: Any) -> Callable:
        """Decorator that registers a Result-returning tool with the underlying MCPServer."""

        def decorator(fn: Callable) -> Callable:
            wrapped = _wrap_tool(fn)
            _registration_signature(fn, wrapped)
            # Preserve passthrough markers
            if getattr(fn, "__adam_mcp_passthrough__", False):
                setattr(wrapped, "__adam_mcp_passthrough__", True)
            if getattr(fn, "__adam_mcp_passthrough_bounded__", False):
                setattr(wrapped, "__adam_mcp_passthrough_bounded__", True)
            if self._mcp_server is not None:
                self._mcp_server.tool(*args, **kwargs)(wrapped)
            return wrapped

        return decorator

    def run(self, **kwargs: Any) -> None:
        """Run the underlying MCPServer. With no arguments, v2 defaults to stdio."""
        if self._mcp_server is None:
            raise RuntimeError("mcp package not installed; cannot run server")
        self._mcp_server.run(**kwargs)
