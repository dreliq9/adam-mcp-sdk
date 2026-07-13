# DIRECTION

Where this project is, where it's going, and why. Distinct from `ROADMAP.md` (versioned plans) and `DECISIONS.md` (architectural log). This file is the strategic snapshot — update it when direction changes, not when releases ship.

**Last updated:** 2026-07-13

## What this project is

A house-style framework + audit + agentic plugin pack layered on top of the official MCP Python SDK. Encodes Principle Zero (AI-shaped tools, not API-shaped) and Principle One (escape hatches always available) as enforceable rules — not just documentation.

**Niche:** sits between Tier 2 (opinionated frameworks like FastMCP) and Tier 4 (audit tools like mcp-scan). The combination — Principle Zero enforcement + mandatory `Result` envelope + audit-as-migration upgrade system + Claude Code plugin pack — is empty in the surveyed landscape.

## Current state — 2026-07-13

| Layer | Status |
|---|---|
| `HOUSE_STYLE.md` spec | v2026.05, includes §1.1 (envelope_version + Raw), §3.18 (rule_id stability) |
| `adam-mcp-py` library | v0.3.2 prepared — async-safe wrappers, bounded passthrough metadata, Windows UTF-8/output fixes |
| `adam-mcp` CLI | v0.2.2 prepared; subcommands: `new`, `audit`, `audit --self-check`, `upgrade` |
| Plugin pack (Claude Code) | `mcp-author` skill + `/mcp-spec`, `/mcp-scaffold`, `/mcp-audit`, `/mcp-upgrade` |
| Reference MCP `adam-greet` | passes audit strict mode, 0 findings |
| Cross-language sibling | `adam-mcp-zig` v0.2.0 shipped, public on GitHub, byte-equivalent wire format |
| Platform support | macOS / Linux / Windows all first-class |
| PyPI publishing | Not done yet. Path-install across local machines and the Zig sibling. |

Four suites cover the library, CLI, Claude pack, and reference MCP. `--self-check` catches: spec↔library cross-link drift, REGISTRY rule_ids missing from HOUSE_STYLE.md, CHANGELOG `### Breaking` entries citing nonexistent rule_ids.

## Strategic direction

### Validation done

- **v0.2 audit-as-migration mechanism works.** First downstream consumer went from N advisory-mode WARNs to 0 findings strict mode by following the audit hints. The first-pass LLM_GUIDE.md draft had wrong section headers; audit caught it; second pass clean. Exactly the loop the spec promised.
- **Principle Zero is real.** Even before semantic refactors, the SPEC.md exercise (writing the target tool shape) revealed how API-shaped original tool surfaces were. The spec writing process itself surfaces the design issues.
- **Cross-language byte-equivalence works.** Zig sibling (`adam-mcp-zig`) ships the same `Result` envelope; the wire format is byte-identical. The envelope_version field added in 0.3.0 was the structural change that made future cross-language wire-format evolution possible without coordinated breaks.
- **Windows is a real platform, not a footnote.** 0.3.1 documents and verifies the Python SDK on Windows; the Zig sibling cross-compiles cleanly to x86_64-windows-gnu and ships PowerShell verification scripts.

### Open strategic questions

1. **PyPI publishing.** Blocking real `adam-mcp upgrade` against external MCPs without `tool.uv.sources` path workarounds. One hour of manual `uv build` + `uv publish` resolves it; trusted-publishing via GitHub Actions is the polished version. Likely happens alongside the public-launch pass for this repo.

2. **Spec 2 (incremental authoring).** `tool add` / `workflow add` / `/mcp-tool` for adding tools to existing MCPs without re-scaffolding. Decoupled from cross-language pack work; takes ~half a day. **Not blocking; lower priority than landing more real consumers.**

3. **Public positioning.** Honest competitive read: this is "Black for MCP tool design" — opinionated, niche, valuable to people maintaining many MCPs or feeling pain from agent-confusing shallow wrappers. A polished worked example (the reference MCP qualifies post-0.3.1) + one short blog post would do most of the marketing work. **The Zig sibling's first-public-MCP-SDK-on-Zigistry positioning may carry more weight than the Python framework's "yet another methodology" framing — worth coordinating the announcement.**

### Not pursuing

- Multi-language packs beyond Python + Zig (TS / Kotlin / Rust deferred indefinitely; the audience that wants this much opinion enforced is small enough that breadth doesn't pay).
- Bulk-MCP upgrade (deferred to v0.3+ if the manual loop becomes painful in practice).
- Rollback support in CLI (git is the rollback story; revisit only if painful).
- Codemod-style migrations (audit-as-migration is sufficient; reconsider in v0.4 only if specific transforms become repetitive).

## Recent learnings

- **Windows needed executable tests, not documentation-only confidence.** The prior `HOME` and default-codepage assumptions failed on Windows despite the implementation appearing portable. Output roots are now injectable and all repository text I/O is explicitly UTF-8.
- **FastMCP accepts async tools, so the contract wrapper must preserve async semantics.** A synchronous wrapper around an async tool validates the coroutine object instead of its result. `BaseServer`, `@validates`, and `@requires` now dispatch sync and async callables separately.
- **The `validates` param-name bug** (v0.2.1) is the kind of issue that only surfaces under real use. v0.1 + v0.2 both shipped with this latent bug because the reference MCP's tools happened to not exercise the pattern that breaks. This is the strongest argument yet for getting external consumers: every additional consumer of the SDK is also an additional probe of its design.
- **The audit can't catch semantic issues.** A consumer can hit "0 findings strict mode" while still having API-shaped tools returning `str`. Mechanical conformance ≠ Principle Zero conformance. The SPEC.md authoring step is where Principle Zero gets enforced; the audit just enforces the *contract*.
- **Cross-link discipline pays compound interest.** When v0.3.0 added envelope_version + Raw, the author followed the same pattern: new audit rule + CHANGELOG cross-link + HOUSE_STYLE.md section + test. The discipline is load-bearing — it's what makes "audit-as-migration" actually work across breaking changes.
- **Wire-format thinking flipped the SDK from "in-process library" to "serialization contract."** Once cross-language byte-equivalence with Zig became a constraint, `Result` stopped being a Python convenience and became a wire spec. envelope_version exists because of this realization; it's the cheapest forward-compat insurance possible.
