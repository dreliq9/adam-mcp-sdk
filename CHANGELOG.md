# Changelog

All notable changes to adam-mcp-sdk.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project uses SemVer for the library and CalVer for the spec.

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
