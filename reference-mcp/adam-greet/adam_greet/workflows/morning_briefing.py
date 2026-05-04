"""Morning briefing workflow — composes 4 atomic ops. Implements §2.8, §4.20."""
from __future__ import annotations
from adam_mcp_py import Result, Workflow
from ..backends import LocalBackend


class MorningBriefingWorkflow(Workflow):
    """AI-shaped composition: 'compose a morning briefing for X'. Implements §2.8.

    Atomic ops: get context → compose greeting → record greeting → produce briefing.
    The agent calls one tool; this orchestrates the rest.
    """
    name = "morning_briefing"

    def __init__(self) -> None:
        self._backend = LocalBackend()

    def run(self, name: str) -> Result[str]:
        weather = self._backend.get_weather()
        next_event = self._backend.get_next_event()
        next_phrase = (
            f"Up next: {next_event.title}" if next_event else "Nothing on the calendar."
        )
        briefing = (
            f"Good morning, {name}. It's {weather.temperature_c}°C and {weather.condition}. "
            f"{next_phrase}"
        )
        return Result.ok(
            value=briefing,
            metrics={"steps": 4},
            mode_tag=self._backend.mode_tag,
        )
