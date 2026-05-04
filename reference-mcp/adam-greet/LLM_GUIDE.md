# adam-greet — LLM Guide

## Overview

Compose context-aware morning greetings that pull from weather, calendar, and recent music. AI-shaped tools cover the common cases; an escape hatch covers everything else.

## Critical workflow

1. For a one-shot greeting, call `compose_greeting(name, formality)`. Atomic, no state.
2. For a context-rich briefing, call `morning_briefing(name)`. Workflow that composes weather + calendar + greeting in one call.
3. To recall history, call `recent_greetings(n)`.
4. To bypass synthesis entirely (custom template, unusual phrasing), call `compose_raw_greeting(template)`.

## Tool categories

- **`greeting_tools`** — atomic greeting composition. `compose_greeting`, `compose_personalized_greeting`.
- **`context_tools`** — multi-source synthesis. `get_morning_context` returns weather + calendar + music as one structured value.
- **`history_tools`** — stateful. `record_greeting`, `recent_greetings`.
- **`workflow_tools`** — higher-order compositions. `morning_briefing`.
- **`escape_tools`** — Principle One. `compose_raw_greeting`.

## Parameter gotchas

- `formality` is 0–10, not a string. Map: 0–2 = "yo", 3–6 = "hello", 7–10 = "good morning".
- `morning_briefing` requires the calendar to be authenticated. If unauthenticated, default response is `WARN` with a `force=True` override.
- `recent_greetings(n)` clamps n to [1, 100].

## Failure → fix

| Failure | Hint | Fix |
|---------|------|-----|
| `formality` validation error | "Fix the following input fields: formality" | Pass an int 0–10 |
| `morning_briefing` WARN — calendar unauthed | "Calendar not authenticated. Use force=True to proceed with a placeholder." | Either auth the calendar or pass `force=True` |
| Tool returned non-Result | "Tool '<name>' did not return a Result..." | Tool author bug — file an issue against adam-greet |

## Mode/path transparency

Every result carries a `mode_tag`:
- `[LOCAL]` — in-process backend, deterministic, no network. Default in v0.1.
- `[WEB]` — would call real APIs. Stub in v0.1; raises `NotImplementedError`.

## Escape hatches

When the AI-shaped tools don't fit your task, drop down:

- `compose_raw_greeting(template)` — `@passthrough`. Returns `template` verbatim. `Result.raw = {"template": ...}`. Use for custom phrasing, unusual languages, anything where the formality scale or briefing format doesn't match what you need.

The underlying `LocalBackend` is also publicly importable (`from adam_greet.backends import LocalBackend`) if you need to compose your own logic in adjacent code.
