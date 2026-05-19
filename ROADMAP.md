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
