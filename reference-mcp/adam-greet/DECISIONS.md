# Decisions

## 2026-05-03 — Mundane domain on purpose
**Decision:** adam-greet's domain is "compose a morning greeting." Not anything Adam actually needs.
**Rationale:** The reference MCP's job is to exemplify every house-style rule clearly. A boring domain makes the rules visible.

## 2026-05-03 — WebBackend stays a stub in v0.1
**Decision:** WebBackend's methods raise NotImplementedError. Only LocalBackend works.
**Rationale:** v0.1 is about exemplifying the architecture, not building a production morning-briefing service. WebBackend exists to demonstrate the mode_tag pattern.
