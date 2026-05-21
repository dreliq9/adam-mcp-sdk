"""Workflow tools — exposes higher-order workflows as MCP tools. Implements §2.8, §1.3."""

from __future__ import annotations
from adam_mcp_py import Result, validates, requires
from ..backends import LocalBackend
from ..schema import MorningBriefingInput
from ..workflows import MorningBriefingWorkflow

_backend = LocalBackend()
_workflow = MorningBriefingWorkflow()


def _calendar_authed() -> bool:
    return _backend.calendar_authenticated()


@validates(MorningBriefingInput)
@requires(
    _calendar_authed,
    fail_hint="Calendar not authenticated. Use force=True to proceed with a placeholder.",
)
def morning_briefing(input: MorningBriefingInput) -> Result[str]:
    """Compose a context-aware morning briefing. Implements §2.8, §4.20.

    Guardrail: calendar must be authenticated. WARN by default; pass force=True to override.
    """
    return _workflow.run(name=input.name)
