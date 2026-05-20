# Changelog

All notable changes to adam-mcp-sdk.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project uses SemVer for the library and CalVer for the spec.

## [0.3.1] — 2026-05-20

### Added
- **Windows is now a documented first-class platform.** No code changes — the codebase was already cross-platform (`pathlib`, `Path.home()`, no POSIX syscalls). This release codifies that: README has a "Platform support" matrix, Install instructions cover both shells, and the audit + test suites are verified to pass via the same `uv run` invocations on Windows. Sibling SDK `adam-mcp-zig` 0.2.0 ships the same parity on the Zig side.

### Notes
- The MCP protocol (stdio JSON-RPC) is handled by FastMCP, which sets binary mode on stdio when needed; no Windows-specific newline handling is required at the SDK layer.
- `Path.home()` on Windows reads `USERPROFILE` (or `HOME` if explicitly set). The `test_output_dir_*` tests monkeypatch `HOME`, which `Path.home()` honors first on every platform.

## [0.3.0] — 2026-05-20

### Breaking
- **§1.1** — `Result` envelope shape changed. `envelope_version: int` added as the **first** field, before `status`. Canonical order is now `(envelope_version, status, value, raw, metrics, diagnostics, hint, mode_tag)`. Field order is contractual — cross-language byte-equivalence depends on it. Future top-level fields require an `envelope_version` bump and another `### Breaking` entry. Migration: existing keyword-only callers (`Result.ok(...)`, `Result.warn(...)`, `Result.fail(...)`) are unaffected — `envelope_version` defaults to `1`. Positional `Result(Status.OK, ...)` construction is now a `TypeError` (kw_only). Replace any positional construction with `Result.ok/.warn/.fail(...)`.

### Added
- `adam_mcp_py.Raw`: `TypeAlias = Any`. Self-documenting alias for `Result.raw`. Lets an MCP narrow to a project-specific type without changing the contract. Documented in §1.1 as the strict-typing exception.
- `adam_mcp_py.ENVELOPE_VERSION`: integer constant for parsers verifying wire-format compatibility.
- §1.1 "Envelope is a wire format" note: codifies that `Result` is a serialization format whenever byte-equivalence is in play.

### Changed
- `@dataclass(kw_only=True)` on `Result` enforces that the envelope's canonical field order is a wire-format contract, not an argument-passing convention. See `tests/test_result.py::test_result_construction_is_keyword_only`.

### Convention going forward
Adding a new top-level field to `Result` is a Breaking change. The path is: bump `ENVELOPE_VERSION`, add a `### Breaking` entry citing `**§1.1**`, update the canonical-order test in `test_result.py`, refresh any byte-equivalence golden checksums.

## [0.2.1] — 2026-05-04

### Fixed
- `adam_mcp_py.validates`: wrapper parameter renamed `input_dict` → `input` so it matches the JSONSchema field name FastMCP generates from the original `(input: SomeModel)` signature. Previous name caused every `@validates`-decorated tool in every downstream MCP to FAIL at first call with `unexpected keyword argument 'input'`. Wrapper now also accepts a pre-parsed model instance (FastMCP validates from JSONSchema before dispatch), avoiding double-validation crashes.

### Added
- §1.5 in HOUSE_STYLE.md: validates parameter naming convention.
- Audit rule **§1.5**: AST-walks user code and FAILs any `@validates`-decorated function whose first parameter is not named `input`.
- `--self-check` extended: parses `validation.py` and FAILs if its wrapper's first parameter drifts from `input`. Catches future regressions of the bug above.

## [0.2.0] — 2026-05-04

### Added
- `adam-mcp upgrade [path] [--to VERSION] [--dry-run]` subcommand: bumps `adam-mcp-py` pin in target MCP, runs `uv sync`, runs audit, returns Result with findings.
- `/mcp-upgrade` slash command in claude-pack: agentic wrapper over `adam-mcp upgrade` that works through audit findings as edits.
- `AuditRule` dataclass and `REGISTRY` in `cli/adam_mcp_cli/audit_rules.py`: first-class registry for audit rules (refactor; no behavior change).
- `--self-check` extended: now verifies (a) every REGISTRY rule_id appears in HOUSE_STYLE.md (§5.28), and (b) every CHANGELOG `### Breaking` bullet's `**§X.Y**` resolves to a REGISTRY rule_id (§5.29).
- §3.18 in HOUSE_STYLE.md: rule_id stability rules.

### Changed
- `_self_check()` superseded by `_self_check_v2()`. The CLI `--self-check` flag now invokes the v2 implementation. Old function removed.

### Convention going forward
Every release that introduces a breaking change MUST have a `### Breaking` section. Each bullet starts with `**§X.Y**` referencing a real `rule_id` in REGISTRY, and the bullet body MUST contain a `Migration:` line. Enforced by `adam-mcp audit --self-check` against the most recent CHANGELOG version block.

## [0.1.0] — 2026-05-04

### Added
- `HOUSE_STYLE.md` v2026.05 — Principles + §1–§6
- `HOUSE_STYLE_RATIONALE.md`
- `adam_mcp_py` library: Result, validates, requires, BackendProtocol, Workflow, output_dir, passthrough, BaseServer
- `adam-mcp` CLI: `new`, `audit`, `audit --self-check`
- `claude-pack`: `mcp-author` skill, `/mcp-spec`, `/mcp-scaffold`, `/mcp-audit` commands, sync tests
- Reference MCP `adam-greet`: full implementation passing audit

### Deferred to v0.2
- Zig language pack
- `/mcp-tool`, `/mcp-upgrade` slash commands
- `adam-mcp tool add` / `workflow add` / `upgrade`
- Migration system
