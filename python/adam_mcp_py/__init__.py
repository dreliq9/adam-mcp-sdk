"""adam_mcp_py — primitives for the Adam MCP house style.

Public API. See HOUSE_STYLE.md for the rules each symbol implements.
"""
from .result import ENVELOPE_VERSION, Raw, Result, Status
from .validation import validates
from .guardrails import requires
from .backend import BackendProtocol, detect_backend
from .workflows import Workflow
from .output import output_dir
from .escape import passthrough, is_passthrough
from .base_server import BaseServer

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
    "BaseServer",
]
__version__ = "0.3.1"
