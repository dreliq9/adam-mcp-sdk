"""Backends for adam-greet. Implements §2.6."""
from .local import LocalBackend
from .web import WebBackend

__all__ = ["LocalBackend", "WebBackend"]
