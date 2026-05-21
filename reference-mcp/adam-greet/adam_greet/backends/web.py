"""Web backend — would call real APIs. In v0.1 it stays unavailable. Implements §2.6."""

from __future__ import annotations
from ..types import WeatherSnapshot, CalendarEvent, MusicTrack


class WebBackend:
    mode_tag = "[WEB]"
    available = False  # Demonstrates mode_tag pattern; real impl deferred.

    def call(self, payload: dict) -> dict:
        return {"web_echo": payload}

    def get_weather(self) -> WeatherSnapshot:
        raise NotImplementedError("WebBackend stub — see ROADMAP")

    def get_next_event(self) -> CalendarEvent | None:
        raise NotImplementedError

    def get_recent_music(self) -> list[MusicTrack]:
        raise NotImplementedError

    def calendar_authenticated(self) -> bool:
        return False
