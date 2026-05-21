"""Greeting tools — atomic ops. Implements §2.7."""

from __future__ import annotations
from adam_mcp_py import Result, validates
from ..backends import LocalBackend
from ..schema import GreetingInput, PersonalizedGreetingInput

_backend = LocalBackend()


def _formality_phrasing(formality: int) -> str:
    if formality <= 2:
        return "yo"
    if formality <= 6:
        return "hello"
    return "good morning"


@validates(GreetingInput)
def compose_greeting(input: GreetingInput) -> Result[str]:
    """Compose a single greeting line. AI-shaped: takes name + formality, returns prose.

    Implements §1.1, §1.2, §1.4.
    """
    phrase = _formality_phrasing(input.formality)
    return Result.ok(value=f"{phrase}, {input.name}", mode_tag=_backend.mode_tag)


@validates(PersonalizedGreetingInput)
def compose_personalized_greeting(input: PersonalizedGreetingInput) -> Result[str]:
    """Compose a greeting using whatever the server remembers. Implements §1.1, §4.19."""
    return Result.ok(value=f"hello again, {input.name}", mode_tag=_backend.mode_tag)
