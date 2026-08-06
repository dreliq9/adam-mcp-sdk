"""adam_mcp_py — primitives for the Adam MCP house style.

Public API. See HOUSE_STYLE.md for the rules each symbol implements.
"""

from .backend import BackendProtocol, detect_backend
from .base_server import BaseServer
from .escape import is_bounded_passthrough, is_passthrough, passthrough
from .guardrails import requires
from .output import output_dir
from .result import ENVELOPE_VERSION, Raw, Result, Status
from .validation import validates
from .workflows import Workflow

__all__ = [
    "ENVELOPE_VERSION",
    "Raw",
    "Result",
    "Status",
    "validates",
    "requires",
    "BackendProtocol",
    "detect_backend",
    "Workflow",
    "output_dir",
    "passthrough",
    "is_passthrough",
    "is_bounded_passthrough",
    "BaseServer",
]
__version__ = "0.3.3"
