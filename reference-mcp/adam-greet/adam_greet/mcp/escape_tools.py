"""Escape-hatch tool — Principle One. Implements §6.30."""
from __future__ import annotations
from adam_mcp_py import Result, validates, passthrough
from ..schema import RawGreetingInput


@passthrough
@validates(RawGreetingInput)
def compose_raw_greeting(input: RawGreetingInput) -> Result[str]:
    """Bypass all synthesis logic — render the template as-is. Implements §6.30.

    When the agent's task doesn't fit the AI-shaped tools (compose_greeting, morning_briefing),
    drop down to this. Returns the template verbatim, no formality adjustment, no context blend.
    """
    return Result.ok(
        value=input.template,
        raw={"template": input.template},
        mode_tag="[LOCAL]",
        diagnostics=["passthrough — synthesis logic bypassed"],
    )
