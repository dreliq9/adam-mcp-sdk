"""Validation decorator — implements §1.2 of HOUSE_STYLE.md."""

from __future__ import annotations
from functools import wraps
import inspect
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
        def parse(input) -> M | Result:
            if isinstance(input, model):
                return input
            try:
                return model(**input)
            except (ValidationError, TypeError) as error:
                if isinstance(error, ValidationError):
                    diagnostics = [
                        f"{'.'.join(str(x) for x in item['loc'])}: {item['msg']}"
                        for item in error.errors()
                    ]
                else:
                    diagnostics = [f"input: {error}"]
                fields = ", ".join(item.split(":")[0] for item in diagnostics)
                return Result.fail(
                    hint=f"Fix the following input fields: {fields}",
                    diagnostics=diagnostics,
                )

        if inspect.iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapper(input) -> Result:
                parsed = parse(input)
                if isinstance(parsed, Result):
                    return parsed
                return await fn(parsed)

            return async_wrapper

        @wraps(fn)
        def wrapper(input) -> Result:
            parsed = parse(input)
            if isinstance(parsed, Result):
                return parsed
            return fn(parsed)

        return wrapper

    return decorator
