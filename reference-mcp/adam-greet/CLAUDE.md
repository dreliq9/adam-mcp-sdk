# adam-greet — CLAUDE.md

## When to use this MCP

The user wants a context-aware greeting, morning briefing, or anything pulling weather + calendar + music together.

Trigger phrases: "good morning", "give me a briefing", "what's my morning look like", "say hi to X".

## When NOT to use this MCP

- The user wants real-time weather data — adam-greet's `[WEB]` backend is a v0.1 stub.
- The user wants to schedule things on the calendar — read-only.
- The user wants production-quality content — adam-greet is a reference MCP, not a polished tool.

## When to drop down to underlying APIs

Principle One. If the user wants:

- A greeting in a language other than English → use `compose_raw_greeting(template)`. Don't try to coerce `compose_greeting`'s formality scale into language switching.
- A briefing in a non-default format → use `compose_raw_greeting`.
- Direct backend access → `from adam_greet.backends import LocalBackend`.

## Co-tools

Pairs well with: time-of-day tools, scheduling MCPs (read-only), TTS for spoken briefings.
