"""Type definitions for adam-greet. Implements §2.9."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class WeatherSnapshot:
    temperature_c: float
    condition: str  # "sunny", "rainy", etc.


@dataclass
class CalendarEvent:
    title: str
    starts_at: str  # ISO 8601


@dataclass
class MusicTrack:
    title: str
    artist: str


@dataclass
class MorningContext:
    weather: WeatherSnapshot
    next_event: CalendarEvent | None
    recent_music: list[MusicTrack] = field(default_factory=list)


@dataclass
class GreetingHistory:
    greetings: list[str] = field(default_factory=list)
