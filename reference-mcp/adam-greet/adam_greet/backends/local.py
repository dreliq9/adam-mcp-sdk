"""Local backend — in-process fakes, no network. The default. Implements §2.6."""

from __future__ import annotations
from ..types import WeatherSnapshot, CalendarEvent, MusicTrack


class LocalBackend:
    mode_tag = "[LOCAL]"
    available = True

    def call(self, payload: dict) -> dict:
        return {"echo": payload}

    def get_weather(self) -> WeatherSnapshot:
        return WeatherSnapshot(temperature_c=18.0, condition="sunny")

    def get_next_event(self) -> CalendarEvent | None:
        return CalendarEvent(title="Standup", starts_at="2026-05-03T09:00:00Z")

    def get_recent_music(self) -> list[MusicTrack]:
        return [MusicTrack(title="Sample Track", artist="Test Artist")]

    def calendar_authenticated(self) -> bool:
        return True
