"""Validation decorator — implements §1.2 of HOUSE_STYLE.md."""
from __future__ import annotations
from functools import wraps
from typing import Callable, TypeVar
from pydantic import BaseModel, ValidationError

from .result import Result

M = TypeVar("M", bound=BaseModel)


def validates(model: type[M]) -> Callable:
    """Decorator: validate the input dict against a Pydantic model. Implements §1.2.

    The wrapped function receives a parsed model instance instead of a raw dict.
    On validation failure, returns a Result.fail with actionable diagnostics.
    """
    def decorator(fn: Callable[[M], Result]) -> Callable[[dict], Result]:
        @wraps(fn)
        def wrapper(input) -> Result:
            if isinstance(input, model):
                return fn(input)
            try:
                parsed = model(**input)
            except ValidationError as e:
                diagnostics = [
                    f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}"
                    for err in e.errors()
                ]
                fields = ", ".join(d.split(":")[0] for d in diagnostics)
                return Result.fail(
                    hint=f"Fix the following input fields: {fields}",
                    diagnostics=diagnostics,
                )
            return fn(parsed)
        return wrapper
    return decorator
