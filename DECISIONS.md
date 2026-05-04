# Decisions

Architectural and process decisions for the SDK. Each entry: date, decision, rationale, alternatives considered.

## 2026-05-03 — Bootstrap-from-reference build order

**Decision:** Build `reference-mcp/adam-greet` BEFORE the scaffold templates. Templates are extracted from the working reference, not invented.

**Rationale:** Templates extracted from working code don't drift from the spec the way invented templates do. The reference MCP also doubles as the integration test for the library.

**Alternative considered:** Templates first, reference MCP second. Rejected — leads to template/reality drift.

## 2026-05-03 — Python first, Zig second, others deferred

**Decision:** v0.1 ships Python only. Zig in v0.2. TS/Kotlin/Rust deferred indefinitely.

**Rationale:** Zig is in flight and maximally different from Python (no async runtime, manual memory). If the spec survives both, it'll survive the rest. Building all 5 from day one would take a year.

## 2026-05-03 — Cross-link contract

**Decision:** Every spec rule names its library symbol; every library symbol names its rule. `adam-mcp audit --self-check` validates this in CI.

**Rationale:** Drift between spec and library is the #1 risk. Mechanical enforcement beats discipline.
