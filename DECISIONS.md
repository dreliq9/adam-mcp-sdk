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

## 2026-05-04 — Library pin style: compatible-release for adam-mcp-py runtime deps

**Decision:** `adam-mcp-py`'s own `pyproject.toml` uses minimum/compatible-release pins (`mcp>=1.0`, `pydantic>=2.5`), not exact pins.

**Rationale:** §2.11 explicitly carves out `adam-mcp-py` from the exact-pin rule ("Compatible-release allowed only for `adam-mcp-py` itself"). Libraries that other projects depend on should not force exact dep versions on consumers — that locks every downstream MCP to the same dependency tree. Exact pins remain mandatory for MCP **projects** (kipilot, caid-mcp, adam-greet, etc.), per §2.11.

**Resolves design-doc §13 Q5** (the previously deferred question about adam-mcp-py's pin style): defer to §2.11's carveout. Reconsider only if compat issues arise.

## 2026-05-04 — Reference MCP is a workspace member (deviation from Task 1)

**Decision:** `reference-mcp/adam-greet` is included in the root `pyproject.toml` workspace `members` list, alongside `python` and `cli`.

**Context:** The plan originally listed only `["python", "cli"]`. Adam-greet's `pyproject.toml` declares `[tool.uv.sources] adam-mcp-py = { workspace = true }` so it can use the local in-development library. That source resolver only works when both packages are workspace members.

**Rationale:** The "isolation" benefit of keeping reference MCPs out of the workspace is theoretical for development — in production each MCP installs adam-mcp-py from PyPI. Workspace membership during dev keeps a single shared venv simple. Reference MCPs (just adam-greet for now) are explicitly tied to the SDK; coupling is honest.

**Alternative considered:** Use `[tool.uv.sources] adam-mcp-py = { path = "../../python", editable = true }`. Rejected — same coupling, more brittle path string, breaks if directory structure changes.

## 2026-05-04 — End-to-end smoke test passed

`adam-mcp new smoke-test` produced a project that passed `adam-mcp audit` (status OK, strict mode, 0 findings) and whose 2 templated tests passed. v0.1 is shippable.
