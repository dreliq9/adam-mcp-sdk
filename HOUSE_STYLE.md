# House Style — Adam's MCPs

**Version:** 2026.05 (CalVer; spec is the slow-moving source of truth)

This is the source of truth for how MCPs are built in Adam's stack. Every library symbol, template, audit rule, and skill embeds rules from this document. Cross-links are mandatory: every rule names its corresponding library symbol; every library symbol names its rule.

---

## Principle Zero — AI-shaped, not API-shaped

The unit of a tool is "a coherent thing an AI can do," not "an API endpoint."

If clumping multiple API calls into one workflow-shaped tool makes the AI parse it better, do that. If splitting one API call into multiple specialized tools makes the AI parse it better, do that. The API surface is irrelevant to the tool surface.

Every other rule in this document descends from this one.

**You will be tempted to write one tool per API endpoint. Don't.** That's the shallow-wrapper default. The unit of work is what an AI does, not what an API exposes.

**Auditability ceiling.** Principle Zero is the SDK's most important rule and its least mechanically auditable — "is this tool AI-shaped?" is a judgment, not a regex. The canonical check is human review at LLM_GUIDE time: when you write the LLM_GUIDE per §3.14, the act of describing the tool's purpose and parameter gotchas exposes API-shapedness. An optional heuristic (`tool_count / underlying_api_endpoint_count > 0.7` → warn) can be added to the audit, but it is advisory, not authoritative.

## Principle One — Escape hatches always available

Tools shaped for AI consumption are the happy path. They are not a cage.

When an agent's task doesn't fit any tool's shape, it must be able to drop down to the underlying API/library/protocol directly. The MCP adds value by lifting common cases; it must never block the uncommon case.

Canonical example: `caid-mcp`'s `run_cadquery_script`. Full validated tool surface for common operations, plus an unconstrained script-runner for everything else.

---

## §1 Tool contract

### §1.1 Result type

Every tool returns a typed `Result(status, value, raw, metrics, diagnostics, hint, mode_tag)`. Never raw output. Never raw exceptions.

| Field | Type | Purpose |
|-------|------|---------|
| `status` | `OK` / `WARN` / `FAIL` | Outcome category |
| `value` | `T \| None` | Synthesized/typed output for AI consumption |
| `raw` | `Any \| None` | Underlying API response when applicable (Principle One support) |
| `metrics` | `dict[str, Any]` | Numeric/scalar measurements (`elapsed_ms`, `bytes_read`, etc.) |
| `diagnostics` | `list[str]` | What happened, in human terms |
| `hint` | `str \| None` | What to try next on FAIL/WARN |
| `mode_tag` | `str \| None` | Which backend/path was used (e.g., `[IPC]`, `[FILE]`, `[LOCAL]`) |

**If you can't write a useful `hint` on FAIL, the tool's shape is wrong.**

→ Library: `adam_mcp_py.Result`

### §1.2 Validation layer

The MCP validates inputs before delegating to the underlying API. It catches silent failures (e.g., OCCT booleans returning empty shapes), surfaces actionable diagnostics. Underlying API rawness must not bleed through unless the agent opts in via `Result.raw` or an escape-hatch tool.

→ Library: `adam_mcp_py.validates`

### §1.3 Process guardrails

Preconditions are enforced (ERC gates `sync_to_pcb`; DRC gates Gerber export; schema valid before write).

Default severity is **WARN**. **FAIL** only when the consequence is genuinely destructive. Override via explicit `force=True` parameter, with required justification in the call.

→ Library: `adam_mcp_py.requires`

### §1.4 Mode/path transparency

When the server has multiple backends, the result tells the agent which one was used (`[IPC]` vs `[FILE]`, `[LOCAL]` vs `[WEB]`). Set `Result.mode_tag`.

→ Library: `adam_mcp_py.BackendProtocol.mode_tag`

### §1.5 Validates parameter naming convention

Every `@validates(Model)`-decorated tool function must name its first parameter **`input`** (e.g. `def my_tool(input: MyInput) -> Result[...]`). The `validates` wrapper accepts `input` as its kwarg, matching the JSONSchema field name FastMCP generates from the original signature via `@wraps`. Using any other name (`data`, `args`, `req`, etc.) publishes a mismatched schema field, and every runtime call FAILs with `unexpected keyword argument 'input'`. The `§1.5` audit rule enforces this; the `--self-check` extends it to the wrapper in `validation.py` itself.

**Framework dependency:** §1.5 exists because of FastMCP's `@wraps`-driven schema generation. It is a framework-integration rule that sits in §1 for proximity to its enforcement mechanism, not because it's a property of the Result contract. If the underlying MCP framework changes its schema-generation behavior, the canonical mitigation is to deprecate §1.5 (keeping the `rule_id` reserved per §3.18) and add a replacement rule in Appendix A. See Appendix A — Framework integration notes.

→ Library: `adam_mcp_py.validates`

---

## §2 Architecture

### §2.5 Three-layer

Core lib → MCP layer → CLI. The MCP is a thin wrapper over a usable library; the CLI is too. Tools never reach into framework internals.

→ Template: `python/templates/_base/`

### §2.6 Pluggable backends

When there's an underlying engine, abstract over it via a Protocol. `backends/` directory; each backend implements `BackendProtocol`.

→ Library: `adam_mcp_py.BackendProtocol`

### §2.7 Tool file organization

Tools live in `<package>/mcp/<area>_tools.py`, grouped by concern. Suffix is `_tools.py`. Never one giant `server.py`.

Examples: `greeting_tools.py`, `context_tools.py`, `analysis_tools.py`, `edit_tools.py`.

### §2.8 Workflows directory

Higher-order compositions distinct from atomic tools live in `<package>/workflows/`. A workflow orchestrates many atomic ops.

→ Library: `adam_mcp_py.Workflow`

### §2.9 Schema and types separated

`<package>/schema.py` and `<package>/types.py` exist as separate modules. They contain only type/schema definitions, no logic.

### §2.10 Predictable output location

Side effects go to `~/<domain>-output/`. Use `output_dir(name)` from the library.

→ Library: `adam_mcp_py.output_dir`

### §2.11 Pinned exact dependencies

Every MCP project's `pyproject.toml` pins exact versions for runtime deps. Compatible-release allowed only for `adam-mcp-py` itself.

### §2.12 Underlying clients publicly importable

The lib layer must expose its dependencies. `from my_mcp.backends import client` must work. No hiding, no proxying. (Principle One.)

---

## §3 Documentation

### §3.13 SPEC.md is law

Versioned. Written before tools.

The spec is the contract — but mid-build discoveries do happen. When a real necessity surfaces that the spec doesn't cover:

1. Add a `DECISIONS.md` entry capturing the discovery, the necessity, and the chosen direction. This is the audit trail.
2. Update SPEC.md to incorporate the addition. The spec now describes the new state.
3. Then build.

What's forbidden is *silent* scope creep — adding features that aren't in the spec without leaving a record. The rule isn't "never add what isn't listed"; it's "never quietly violate the spec." If the rule felt like "violate when needed" in practice, that meant the spec lacked a documented path for honest scope expansion. Now it has one.

### §3.14 LLM_GUIDE.md

Agent-facing usage guide. Lives next to README. Required sections:
- **Overview** — what this MCP is and what it does
- **Critical workflow** — order of operations that matters
- **Tool categories** — one paragraph per `_tools.py`
- **Parameter gotchas** — non-obvious input details
- **Failure → fix** — what each FAIL means and how to recover
- **Mode/path transparency** — what each `mode_tag` means
- **Escape hatches** — when to drop down, how, what `Result.raw` contains for each tool

### §3.15 CLAUDE.md

Routing/usage discipline. Required sections:
- **When to use this MCP** — the trigger phrases
- **When NOT to use this MCP** — boundaries
- **When to drop down to underlying APIs** — Principle One in practice
- **Co-tools** — what other MCPs/skills pair well

### §3.16 AUDIT.md

Periodic research-driven SOTA survey. Compiled from parallel research agents. Compares "current" vs "best-in-class" with explicit upgrade plan. Re-run quarterly.

### §3.17 Working artifacts

- `CHANGELOG.md` — Keep a Changelog format
- `ROADMAP.md` — what's coming, what's deferred
- `DECISIONS.md` — architectural decision log
- `DEVLOG.md` — running notes during implementation
- `task_plan.md`, `progress.md`, `findings.md` — planning-with-files artifacts inside the project

### §3.18 — Audit rule_id stability

`rule_id` strings (`§N.NN`) in `cli/adam_mcp_cli/audit_rules.py::REGISTRY` are stable forever once published. They are the cross-link substrate for the upgrade system (audit-as-migration); a rename or reassignment would silently break downstream MCPs' upgrade paths.

**Rules:**
- Once a rule_id appears in a tagged release, its meaning is frozen.
- A rule may be deprecated (removed from REGISTRY) but its `rule_id` is reserved permanently — never reassigned to a different rule. Removals recorded in `DECISIONS.md`.
- New rules use the next free number in their chapter.
- A rule's `severity_default` may change across versions. That is a breaking change and requires a CHANGELOG `### Breaking` entry referencing the rule_id, but the rule_id itself stays put.
- A rule's `check` function may be tightened (stricter behavior under the same rule_id). That is also a breaking change.

→ CLI: `adam_mcp_cli.audit_rules.AuditRule` (the dataclass that carries the rule_id).

**Cross-link enforcement:** `adam-mcp audit --self-check` verifies that every REGISTRY rule_id appears in this spec, and that every CHANGELOG `### Breaking` bullet's `**§X.Y**` resolves to a real REGISTRY rule_id.

---

## §4 Authoring patterns (apply when relevant)

Not every MCP needs all of these.

### §4.18 Multi-source synthesis
Pull from N sources, return composite. Example: `vulnerability-intelligence` synthesizes NVD + CISA KEV + EPSS into composite risk.

### §4.19 Stateful server context
Server remembers profile/watchlist/history; every response is enriched.

### §4.20 Tool composition / pipelines
Tools designed to be chained by an agent. Example: `qa-hard` is `build_evaluator_prompts → dispatch → build_weigher_prompts → dispatch → finalize`.

### §4.21 Bundled subagents
Companion agents shipped with the MCP. Example: `local-llm-gateway` ships `batch-processor`, `draft-refine`, `tiered-reviewer`.

### §4.22 Domain logic baked in
Server has its own engine/rules/kernel. Example: `archi` has its own kernel + rules; tools call that, not an external API.

### §4.23 Parallel fan-out
Tools that orchestrate batched/parallel work across subagents/models. Example: `corpus-retrieval` summarize-pending fans out parallel Haiku 4.5 subagents.

### §4.24 Agent-aware result formatting
Outputs shaped for an agent: structured value + summary diagnostics + next-step hint, not raw API JSON.

---

## §5 Cross-link contract

### §5.25 Spec rules name library symbols

Every rule above with a `→ Library:` pointer must name an exact symbol that exists in `adam_mcp_py`.

### §5.26 Library symbols name rules

Every public symbol in `adam_mcp_py` has a docstring naming the rule it implements (e.g., `"Implements §1.1."`).

### §5.27 Audit self-check

`adam-mcp audit --self-check` validates cross-link integrity:
- Every spec `→ Library:` pointer resolves to an importable symbol.
- Every public `adam_mcp_py` symbol's docstring names a spec rule.
- Drift fails CI.

---

## §6 Escape hatch contract

### §6.28 Underlying clients publicly importable
(Restates §2.12.)

### §6.29 Result.raw

Synthesized output goes in `Result.value`. Raw API response goes in `Result.raw`. Agent can use either.

### §6.30 Every MCP ships a passthrough tool

For MCPs wrapping an external API: a tool that makes raw API calls. For MCPs over an own-kernel/own-engine (archi-style): a tool that runs raw scripts/queries against the engine.

Decorated with `@passthrough`. One per server, enforced. Generic name: `<domain>_passthrough` or `run_<domain>_script`. Canonical example: `caid-mcp`'s `run_cadquery_script`.

→ Library: `adam_mcp_py.passthrough`

### §6.31 Guardrails default WARN

Restates §1.3 default severity. Hard-block (FAIL) only when consequence is destructive.

### §6.32 LLM_GUIDE has Escape hatches section
(Restates §3.14 required section.)

### §6.33 CLAUDE.md has "when to drop down" guidance
(Restates §3.15 required section.)

---

## Appendix A — Framework integration notes

Rules in this appendix encode constraints that come from the underlying MCP framework (currently FastMCP for Python; equivalents in other language packs), not from the agent-tool contract itself. They are listed here so that:

- The §1–§6 core stays portable across frameworks and protocol versions.
- When a framework's behavior changes, the affected rule can be deprecated (its `rule_id` reserved per §3.18) and a replacement added here without disturbing the core contract.

Currently routed into this appendix:

- **§1.5** — `validates` parameter naming. Lives in §1 for proximity to enforcement, but conceptually belongs here. If FastMCP changes its `@wraps`-driven schema generation, §1.5 will be deprecated and a replacement rule (`§A.N`) added here.

This appendix is intentionally short. New rules land here only when they encode a framework-specific behavior that the §1–§6 contract does not require.
