"""Pydantic schemas for tool inputs. Implements §1.2 + §2.9."""

from __future__ import annotations
from pydantic import BaseModel, Field


class GreetingInput(BaseModel):
    name: str = Field(min_length=1)
    formality: int = Field(ge=0, le=10, default=5)


class PersonalizedGreetingInput(BaseModel):
    name: str = Field(min_length=1)


class RecordGreetingInput(BaseModel):
    greeting: str = Field(min_length=1)


class RecentGreetingsInput(BaseModel):
    n: int = Field(ge=1, le=100, default=5)


class MorningBriefingInput(BaseModel):
    name: str = Field(min_length=1)
    force: bool = Field(default=False)


class RawGreetingInput(BaseModel):
    template: str = Field(min_length=1)
