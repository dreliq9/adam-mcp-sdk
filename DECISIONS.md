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

## 2026-07-13 — Bound the official MCP SDK compatibility line

**Decision:** Superseding the unbounded `mcp>=1.0` minimum above, `adam-mcp-py` supports `mcp>=1.28.1,<2`. MCP applications, including the reference MCP and scaffold template, pin `mcp==1.28.1` exactly.

**Rationale:** The library should compose with downstream dependency graphs while excluding the upcoming MCP 2.x API break. Applications need an exact, reproducible protocol implementation. Version 1.28.1 is the stable API verified by this release.

## 2026-07-13 — Bounded passthrough for safety-critical backends

**Decision:** `@passthrough(bounded=True)` marks the required escape hatch when authorization or hardware safety requires a constrained capability surface. An unbounded passthrough remains the default house-style mechanism for ordinary MCPs.

**Rationale:** Hardware and host-command MCPs need an escape hatch without silently expanding the server's authority. Explicit metadata lets audits and documentation distinguish intentional bounds from an accidentally incomplete passthrough.

## 2026-05-04 — Reference MCP is a workspace member (deviation from Task 1)

**Decision:** `reference-mcp/adam-greet` is included in the root `pyproject.toml` workspace `members` list, alongside `python` and `cli`.

**Context:** The plan originally listed only `["python", "cli"]`. Adam-greet's `pyproject.toml` declares `[tool.uv.sources] adam-mcp-py = { workspace = true }` so it can use the local in-development library. That source resolver only works when both packages are workspace members.

**Rationale:** The "isolation" benefit of keeping reference MCPs out of the workspace is theoretical for development — in production each MCP installs adam-mcp-py from PyPI. Workspace membership during dev keeps a single shared venv simple. Reference MCPs (just adam-greet for now) are explicitly tied to the SDK; coupling is honest.

**Alternative considered:** Use `[tool.uv.sources] adam-mcp-py = { path = "../../python", editable = true }`. Rejected — same coupling, more brittle path string, breaks if directory structure changes.

## 2026-05-04 — End-to-end smoke test passed

`adam-mcp new smoke-test` produced a project that passed `adam-mcp audit` (status OK, strict mode, 0 findings) and whose 2 templated tests passed. v0.1 is shippable.

## 2026-05-04 — v0.2 Spec 1: audit-as-migration

**Decision:** Migrations are audit rules. No parallel transform engine, no codemod runner.

**Rationale:** Reuses v0.1 audit infrastructure. Forces every breaking change to ship with a self-explaining hint. Keeps v0.2 small enough to ship.

**Alternatives considered:** pure docs (too loose), codemods (too much engineering for current scale), hybrid (defer to v0.3 if needed).

## 2026-05-04 — CHANGELOG cross-link discipline

**Decision:** Every `### Breaking` bullet starts with `**§X.Y**` referencing a real `rule_id`; bullet body contains a `Migration:` line. `adam-mcp audit --self-check` enforces against the most recent CHANGELOG version block.

**Rationale:** Discipline for B (audit-as-migration) — without it, the system silently degrades into "release notes + good luck."

## 2026-05-04 — rule_id format = `§N.NN`, stable forever

**Decision:** rule_ids match HOUSE_STYLE.md anchors. Stable forever once published. Reassignment forbidden. Deprecations recorded here.

**Rationale:** rule_ids are the cross-link substrate for the upgrade system. Renames break downstream MCPs.

## 2026-05-04 — Single-version-jump for upgrades

**Decision:** `adam-mcp upgrade` does not walk through intermediate versions. Bumping 0.2 → 0.5 surfaces all of 0.5's findings at once.

**Rationale:** Audit is current-state. Walking is more ceremony for the same outcome.

## 2026-05-04 — No downgrade support in CLI

**Decision:** `adam-mcp upgrade` returns FAIL on downgrade attempts.

**Rationale:** Downgrades are rare and risky; manual `pyproject.toml` edit + `uv sync` is the explicit path. Don't tempt people with an automated downgrade.

## 2026-05-04 — No git operations in CLI

**Decision:** `adam-mcp upgrade` does not commit, branch, or stash. Slash command suggests commits but never runs them.

**Rationale:** Per `~/CLAUDE.md` safety boundary, git operations need explicit user approval.

## 2026-05-04 — Batch-fix strategy in `/mcp-upgrade`

**Decision:** Slash command works through all findings, then re-audits. Not per-finding interactive.

**Rationale:** Adam's "just do the thing" preference. Diff review is the gate, not finding-by-finding approval.

## 2026-05-04 — Max 3 audit iterations in `/mcp-upgrade`

**Decision:** Hard cap on re-audit loops to prevent oscillation from buggy rules.

**Rationale:** Belt for the case where fixing finding A introduces finding B.

## 2026-05-04 — No bulk-MCP upgrade in v0.2

**Decision:** `adam-mcp upgrade` operates on one project at a time.

**Rationale:** Single-project primitive is the right abstraction first. Bulk upgrade is v0.3+ if the manual loop becomes painful.

## 2026-05-04 — No rollback support in v0.2

**Decision:** Git is the rollback story. `adam-mcp upgrade` does not maintain a "previous state" snapshot.

**Rationale:** Out of scope for current design. Revisit in v0.3 if painful in practice.

## 2026-05-19 — CLOSED: `Result.raw` typing strategy

**Status:** CLOSED 2026-05-20 — Option 1 with opt-in narrowing via `Raw` type alias.

**Context:** `Result.raw` is typed `Any` (Python) / equivalent in Zig. This is the spec's own escape-hatch-escape-hatch — it directly contradicts the strict-typing rule that holds everywhere else in the codebase. Pragmatic because the backing API's response shape may not be known at tool-author time, but it reads like an oversight rather than an intentional carveout.

**Options considered:**

1. **Keep `Any`, name the exception.** Add a paragraph to §1.1 explicitly stating that `Result.raw` is the documented exception to strict typing because it represents an unknown-shaped foreign payload. No code change; just promote the implicit decision to an explicit one.
2. **Parameterize as `Raw[T]`.** Make `Result.raw` typed by the backend's response schema. Stricter but pushes per-backend type definitions onto every MCP author.
3. **Split into `raw_json: JsonValue` + `raw_typed: T | None`.** Belt-and-suspenders. Grows the envelope.

**Decision:** Option 1, with a forward-compat tweak. `Result.raw` stays `Any` in the canonical contract — this is the documented exception to strict typing, because `raw` exists *to* carry unknown-shape payloads from foreign APIs. Trying to type the untyped fights the design's purpose.

To allow MCPs that *can* type their backend's response to opt in without breaking the envelope, `adam_mcp_py` exports a public type alias `Raw = Any`. An MCP can annotate locally (e.g. `raw: Raw` becomes equivalent to `raw: Any`, but in v0.3+ may be parameterized as `Raw[T]` once a project narrows it). This is purely an annotation convenience; no envelope change, no audit-rule change, no byte-equivalence impact.

**Tradeoffs accepted:**
- Doesn't improve type safety at the contract level (intentional — `raw` is by definition unstructured).
- Doesn't force per-MCP discipline (intentional — would raise authoring burden for marginal gain).

**Tradeoffs rejected:**
- Option 2 raises per-MCP burden; in practice most authors would write `Raw[Any]` and gain nothing.
- Option 3 grows the envelope to 8 fields, which collides with the byte-equivalence contract and intersects with the envelope-versioning decision below.

**Spec impact:** §1.1 to be updated with one sentence naming `raw` as the documented exception to §1.x strict typing. `adam_mcp_py.Raw` to be added as a public re-export. No `rule_id` changes.

## 2026-05-19 — CLOSED: Envelope versioning strategy

**Status:** CLOSED 2026-05-20 — Option 1, reserve `envelope_version: int = 1` as the **first** field.

**Context:** `Result` field order is frozen (`status → value → raw → metrics → diagnostics → hint → mode_tag`) per `tools/byte_equivalence_check.sh`. Cross-language byte-equivalence depends on it. There is no explicit forward-compatibility story for the case when the envelope needs an 8th field — and the async/streaming roadmap item makes this concrete: progress payloads, partial results, citations, and trace IDs are all plausible future additions.

**Options considered:**

1. **Reserve `envelope_version: int` field now.** Adds the version field at envelope creation time, before any tagged release commits us to the current shape. Consumers that don't care ignore it; future code can branch on version.
2. **Commit to "additions go in `metrics` / `diagnostics`, never new top-level fields."** Locks the envelope at 7 fields forever. New axes squeeze into existing dicts/lists.
3. **Plan a `Result_v2` shape and bump byte-equivalence to versioned checksums.** Defer the choice; commit to handling it the day it's needed via a major-version migration.

**Decision:** Option 1, reserved as the **first** field of the envelope (before `status`). The new canonical order is `envelope_version → status → value → raw → metrics → diagnostics → hint → mode_tag`, initial value `envelope_version = 1`.

**Reasoning:**

- **Byte-equivalence makes `Result` a wire format.** Once cross-language byte-equivalence is contractual (Zig/TS/Rust packs upcoming), `Result` is no longer an in-process Python dataclass — it is a serialization format. Every wire format has a version field (PNG magic, ELF header, MCP protocol version, HTTP version). The need does not go away by refusing to add it; refusal only delays the addition to a more expensive moment.
- **Option 2 collides with the async/streaming roadmap entry.** Progress payloads, partial results, and trace IDs are not metrics and not diagnostics. Squeezing them into either dict bloats those fields' semantics and undermines their existing purpose. Trading one principled cost (an extra field) for a worse semantic mess later is the wrong direction.
- **Option 3 causes the v2 break it claims to manage.** Without a version field, shipping `Result_v2` requires every MCP to migrate *and* the byte-equiv tooling to support versioned checksums after the fact. With a version field already in place, `v2` is a bump from `envelope_version=1` to `envelope_version=2` — strictly cheaper migration.
- **First-position placement** lets a parser short-circuit on version mismatch before attempting to read the rest. Standard wire-format convention.

**Cost accepted:** one field of structural metadata in every Result forever. This is the cheapest insurance the design will ever buy.

**Spec impact (separate commit):**
- §1.1 Result type table: add `envelope_version: int` as the first row.
- `tools/byte_equivalence_check.sh`: update canonical field order; refresh golden checksum.
- `adam_mcp_py.Result` constructor: add `envelope_version` field with default `1`.
- Library docstring update naming §1.1.
- CHANGELOG `### Breaking` entry for the field order change (still pre-v1.0, but worth noting).
- No `rule_id` changes per §3.18.
