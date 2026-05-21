"""Workflow base class — implements §2.8 of HOUSE_STYLE.md."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from .result import Result


class Workflow(ABC):
    """A higher-order tool that orchestrates atomic ops. Implements §2.8.

    Subclasses must define `name` and implement `run(...)`.
    """

    name: str = ""

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Result: ...
