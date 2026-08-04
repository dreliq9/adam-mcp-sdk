# Roadmap

## v0.1 (current)
- HOUSE_STYLE.md complete (Principles + §1–§6)
- HOUSE_STYLE_RATIONALE.md
- adam_mcp_py library — full module set
- CLI: `adam-mcp new` + `adam-mcp audit`
- Plugin pack: `mcp-author` skill + `/mcp-spec`, `/mcp-scaffold`, `/mcp-audit`
- Reference MCP `adam-greet` complete in Python, passes audit

## v0.2

### Done (Spec 1 — upgrade system)
- AuditRule registry + rule_id stability rules
- `adam-mcp upgrade` CLI subcommand
- `/mcp-upgrade` slash command
- `--self-check` extended for CHANGELOG ↔ rule_id cross-links

### Pending (Spec 2 — incremental authoring)
- `adam-mcp tool add <name> --category <cat>`
- `adam-mcp workflow add <name>`
- `/mcp-tool` slash command

### Pending (Spec 3 — Zig pack)
- Zig library + templates (corpus already indexed in corpus-retrieval)

## Later
- TS / Kotlin / Rust language packs
- Backport adam_mcp_py into existing MCPs (kipilot, caid-mcp, declip, etc.)
- **Async / long-running tool Result shape.** The current `Result` envelope is value-shaped, not stream-shaped. Tools whose work exceeds ~5–10s (LLM-in-tool, large batch ops) need either: (a) progress-bearing Workflow with intermediate diagnostics emission, or (b) a streaming Result variant (`AsyncIterator[Result[Partial[T]]]` or equivalent). Pick a direction once MCP protocol-level streaming stabilizes. Until then, long tools should emit a single Result with `metrics.elapsed_ms` and a hint pointing at a follow-up tool, rather than blocking the agent.

### Possible future development: stateful domain workspace profile

Explore an optional Jupyter-informed workspace pattern for domain MCPs whose underlying backends have meaningful live state. This should be a reusable SDK profile rather than a requirement for ordinary stateless MCP servers.

Potential SDK concepts:

- `SessionRef` and monotonic `SessionRevision` contracts;
- explicit `create_session`, `inspect_session`, `checkpoint_session`, `restore_session`, `interrupt_operation`, and `close_session` conventions;
- execution journals that record operation order, input hashes, dependencies, changed objects, invalidated objects, outputs, diagnostics, and backend mode;
- optimistic concurrency through `expected_session_revision` on state-mutating calls;
- discoverable backend capabilities and introspection tools;
- typed rich-artifact handles for waveforms, schematics, geometry, build reports, graph views, matrices, measurements, and other domain outputs;
- separation between session-local exploratory artifacts, persisted exploratory artifacts, and promotion candidates;
- promotion workflows that convert successful exploration into reproducible workflows, tests, scripts, pipelines, or governed project deltas;
- clean-session replay or dependency replay before promotion when reproducibility matters;
- backend adapters that retain domain-specific state while still returning the Adam `Result` envelope.

Likely use cases include SPICE and simulation MCPs, CAD/KiCad workspaces, firmware build/debug MCPs, theorem-prover sessions, SCPI laboratory sessions, numerical graph analysis, and other tools where a sequence of operations builds meaningful context.

Design principle:

> The Adam MCP SDK should standardize session discipline, observability, and promotion boundaries while leaving live execution state and domain behavior inside the domain-specific backend.
