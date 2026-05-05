# DIRECTION

Where this project is, where it's going, and why. Distinct from `ROADMAP.md` (versioned plans) and `DECISIONS.md` (architectural log). This file is the strategic snapshot — update it when direction changes, not when releases ship.

**Last updated:** 2026-05-04

## What this project is

A house-style framework + audit + agentic plugin pack layered on top of the official MCP Python SDK. Encodes Principle Zero (AI-shaped tools, not API-shaped) and Principle One (escape hatches always available) as enforceable rules — not just documentation.

**Niche:** sits between Tier 2 (opinionated frameworks like FastMCP) and Tier 4 (audit tools like mcp-scan). The combination — Principle Zero enforcement + mandatory `Result` envelope + audit-as-migration upgrade system + Claude Code plugin pack — is empty in the surveyed landscape.

## Current state — 2026-05-04

| Layer | Status |
|---|---|
| `HOUSE_STYLE.md` spec | v2026.05, includes §3.18 (rule_id stability) |
| `adam-mcp-py` library | v0.2.0 shipped; **v0.2.1 patch uncommitted in working tree** (validates param-name fix + §1.5 audit rule) |
| `adam-mcp` CLI | v0.2.0 shipped; subcommands: `new`, `audit`, `audit --self-check`, `upgrade` |
| Plugin pack (Claude Code) | `mcp-author` skill + `/mcp-spec`, `/mcp-scaffold`, `/mcp-audit`, `/mcp-upgrade` |
| Reference MCP `adam-greet` | passes audit strict mode, 0 findings |
| First real backport (polyglot) | Phase 1 done — audit clean strict mode. Phase 2 (Principle Zero refactor) pending. |
| PyPI publishing | Not done. Path-install only across Adam's two machines. |

**78 tests** across 4 suites. `--self-check` catches: spec↔library cross-link drift, REGISTRY rule_ids missing from HOUSE_STYLE.md, CHANGELOG `### Breaking` entries citing nonexistent rule_ids.

## In flight (uncommitted)

A v0.2.1 patch is sitting in the working tree, not yet committed. It contains:
- Bug fix: `validates` wrapper parameter renamed `input_dict` → `input` (FastMCP JSONSchema-field-name mismatch was causing every `@validates`-decorated tool to FAIL at first call).
- New audit rule §1.5 — AST-walks user code, FAILs any `@validates`-decorated function whose first parameter isn't named `input`.
- `--self-check` extension catching wrapper drift in `validation.py` itself.
- HOUSE_STYLE.md §1.5 documenting the convention.
- Test coverage in `python/tests/test_validation.py`.

**This patch demonstrates the audit-as-migration design working as intended:** real-world bug found → ships with both a fix AND a permanent regression-blocker audit rule, with the spec cross-link enforced by `--self-check`. Ready to tag as v0.2.1 once Adam reviews.

## Strategic direction

### Validation done
- **v0.2 audit-as-migration mechanism works.** Polyglot Phase 1 took an MCP from 12 advisory-mode WARNs to 0 findings strict mode by following the audit hints. The first-pass LLM_GUIDE.md draft had wrong section headers; audit caught it; second pass clean. Exactly the loop the spec promised.
- **Principle Zero is real.** Even before Phase 2 refactor, the SPEC.md exercise (writing the target 13-tool shape for polyglot) revealed how API-shaped the original 21 tools were. The spec writing process itself surfaces the design issues.

### Open strategic questions

1. **PyPI publishing.** Currently blocking real `adam-mcp upgrade` against external MCPs (Phase 1 of polyglot needed `tool.uv.sources` path install workaround). One hour of manual `uv build` + `uv publish` resolves it. Trusted-publishing via GitHub Actions is the polished version. **Pending Adam's decision.**

2. **Polyglot Phase 2 timing.** Half-day refactor (21 → 13 tools per SPEC.md, BaseServer, Result envelope, test port). Could happen next, or be deferred while Spec 2 / Spec 3 of the SDK happen first. **Pending Adam's decision.**

3. **Spec 2 vs Spec 3 priority.** Spec 2 = `tool add` / `workflow add` / `/mcp-tool` (incremental authoring, supports Phase 2 of polyglot). Spec 3 = Zig pack (independent, validates SDK abstractions against a maximally-different language). Spec 2 has stronger near-term coupling to active backport work; Spec 3 is the more interesting design test. **Pending Adam's decision.**

4. **Public positioning.** Honest competitive read: this is "Black for MCP tool design" — opinionated, niche, valuable to people maintaining many MCPs or feeling pain from agent-confusing shallow wrappers. A `MANIFESTO.md` (or sharp README opening) + one polished worked example (polyglot post-Phase-2 would qualify) + one short blog post would do most of the marketing work. **Not blocking; revisit when polyglot Phase 2 ships.**

### Not pursuing

- Multi-language packs beyond Python + Zig (TS / Kotlin / Rust deferred indefinitely; the audience that wants this much opinion enforced is small enough that breadth doesn't pay).
- Bulk-MCP upgrade (deferred to v0.3+ if the manual loop becomes painful in practice).
- Rollback support in CLI (git is the rollback story; revisit only if painful).
- Codemod-style migrations (audit-as-migration is sufficient; reconsider in v0.3 only if specific transforms become repetitive).

## Recent learnings

- **The validates param-name bug** (the in-flight v0.2.1 patch) is the kind of issue that only surfaces under real use. v0.1 + v0.2 both shipped with this latent bug because adam-greet's tools happened to not exercise the pattern that breaks. This is the strongest argument yet for backporting: every additional consumer of the SDK is also an additional probe of its design.
- **The audit can't catch semantic issues.** Polyglot Phase 1 went to "0 findings strict mode" while still having 21 API-shaped tools returning `str`. Mechanical conformance ≠ Principle Zero conformance. The SPEC.md authoring step is where Principle Zero gets enforced; the audit just enforces the *contract*.
- **Cross-link discipline pays compound interest.** When the v0.2.1 patch was prepared, the author followed the same pattern: new audit rule + CHANGELOG cross-link + HOUSE_STYLE.md section + test. The discipline is becoming load-bearing — it's what makes "audit-as-migration" actually work.
