"""adam_mcp_py — primitives for the Adam MCP house style.

Public API. See HOUSE_STYLE.md for the rules each symbol implements.
"""
from .result import Result, Status
from .validation import validates
from .output import output_dir
from .escape import passthrough, is_passthrough

__all__ = [
    "Result",
    "Status",
    "validates",
    "output_dir",
    "passthrough",
    "is_passthrough",
]
__version__ = "0.1.0"
