"""Context tools — multi-source synthesis. Implements §4.18."""
from __future__ import annotations
from dataclasses import asdict
from adam_mcp_py import Result
from ..backends import LocalBackend
from ..types import MorningContext

_backend = LocalBackend()


def get_morning_context() -> Result[dict]:
    """Bundle weather + calendar + music into one AI-parseable result. Implements §4.18.

    AI-shaped: the agent gets one synthesized object, not three separate API calls.
    """
    ctx = MorningContext(
        weather=_backend.get_weather(),
        next_event=_backend.get_next_event(),
        recent_music=_backend.get_recent_music(),
    )
    return Result.ok(
        value={
            "weather": asdict(ctx.weather),
            "next_event": asdict(ctx.next_event) if ctx.next_event else None,
            "recent_music": [asdict(t) for t in ctx.recent_music],
        },
        raw=None,  # No single underlying API; this is composed.
        mode_tag=_backend.mode_tag,
    )
