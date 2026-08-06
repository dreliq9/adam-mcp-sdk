# adam-mcp-sdk

A methodology-first MCP (Model Context Protocol) SDK for **Python 3.11+**. Typed `Result` envelope, validation wrappers, escape hatches by default. One repo, multiple deliverables — library, CLI, Claude Code plugin, reference MCP.

**Status:** v0.3.3 (2026-08-06). Migrated to the stable MCP Python SDK v2 / 2026-07-28 protocol line while retaining the Adam house-style API. Async tools and Windows UTF-8/output handling are verified across library/CLI/plugin/reference-mcp. Windows is a first-class platform. Cross-language byte-equivalent envelope with the Zig sibling, [adam-mcp-zig](https://github.com/dreliq9/adam-mcp-zig).

> **Pre-1.0.** The public API of `adam_mcp_py` may break between minor versions. SemVer guarantees kick in at v1.0. Pin exact versions in your dependencies until then.

---

## Why this exists

Most MCP servers in the wild are shallow wrappers — one tool per API endpoint, no validation contract, no designated escape hatch, no `Result` envelope to enforce against. `adam-mcp-sdk` is the contract layer the shallow wrappers skip:

- **`Result(envelope_version, status, value, raw, metrics, diagnostics, hint, mode_tag)`** — typed envelope. Never raw output, never raw exceptions. Cross-language byte-identical with the Zig sibling.
- **`@validates(Model)`** — decorator that parses MCP-side JSON into a typed Pydantic model; parse failures become `Result.fail` with diagnostics.
- **`@requires(precondition, hint, severity)`** — runtime guard. WARN by default, FAIL only when destructive, bypass with `force=True`.
- **`@passthrough`** — marks a tool as the documented escape hatch. Every MCP ships one.
- **`BackendProtocol` + `detect_backend`** — interface for IPC/local/web backends; `mode_tag` surfaces which path was used on every `Result`.
- **`Workflow`** — class for higher-order compositions distinct from atomic tools.
- **`BaseServer`** — MCP Python SDK v2 `MCPServer` wrapper that enforces every tool returns `Result`, coerces non-`Result` returns to `Result.fail`, and traps exceptions.

The single load-bearing principle: **AI-shaped, not API-shaped.** One tool per *coherent thing an AI can do*, not one tool per API endpoint. House style and rationale live in [HOUSE_STYLE.md](./HOUSE_STYLE.md).

---

## What's here

| Path | What it is |
|------|-----------|
| `HOUSE_STYLE.md` | The spec. Cross-language source of truth (same spec governs `adam-mcp-zig`). |
| `HOUSE_STYLE_RATIONALE.md` | Why each rule exists, with links to the MCP that taught us. |
| `python/` | `adam-mcp-py` library — the primitives (Result, BaseServer, validates, etc.). |
| `cli/` | `adam-mcp` CLI — `new` (scaffold), `audit`, `upgrade`. |
| `claude-pack/` | Claude Code plugin: `mcp-author` skill + `/mcp-spec`, `/mcp-scaffold`, `/mcp-audit`, `/mcp-upgrade` commands. |
| `reference-mcp/adam-greet/` | Canonical reference MCP. Embodies every rule. Templates are extracted from this. |

---

## Install (development)

```bash
# macOS / Linux
git clone https://github.com/dreliq9/adam-mcp-sdk ~/Projects/adam-mcp-sdk
cd ~/Projects/adam-mcp-sdk
uv sync --all-extras
```

```powershell
# Windows (PowerShell)
git clone https://github.com/dreliq9/adam-mcp-sdk $HOME\Projects\adam-mcp-sdk
cd $HOME\Projects\adam-mcp-sdk
uv sync --all-extras
```

The library distribution (`adam-mcp-py`) is publicly available from PyPI:

```bash
uv add adam-mcp-py
```

### CLI

`adam-mcp-cli` 0.2.2 is published on PyPI:

```bash
uv tool install adam-mcp-cli
adam-mcp --help
```

The PyPI distribution is `adam-mcp-cli`; the installed command is `adam-mcp`.

## Usage

```bash
# Scaffold a new MCP project
adam-mcp new my-thing

# Audit a project against the spec
adam-mcp audit ~/Projects/my-thing

# Bump the adam-mcp-py pin in a downstream MCP + run audit
adam-mcp upgrade ~/Projects/my-thing --to 0.3.3

# Self-check (verifies cross-link integrity in this repo)
adam-mcp audit --self-check
```

On Windows, the same commands work in PowerShell or cmd. Paths follow Windows conventions: `adam-mcp audit $HOME\Projects\my-thing`.

---

## Authoring a tool, end-to-end

```python
from pydantic import BaseModel
from adam_mcp_py import BaseServer, Result, validates, requires, passthrough

server = BaseServer(name="my-mcp")

class GreetingInput(BaseModel):
    name: str
    formality: int = 5

@server.tool()
@validates(GreetingInput)
def compose_greeting(input: GreetingInput) -> Result[str]:
    phrase = "good morning" if input.formality > 6 else "hello"
    return Result.ok(value=f"{phrase}, {input.name}", mode_tag="[LOCAL]")

@server.tool()
@passthrough
def run_raw_query(query: str) -> Result[str]:
    # Documented escape hatch — agent can drop down to raw underlying API.
    return Result.ok(value=query, mode_tag="[LOCAL]")

if __name__ == "__main__":
    server.run()
```

The decorators enforce:
- Every tool returns a `Result` (non-`Result` returns become `Result.fail` with hint pointing to §1.1).
- Every WARN/FAIL has a hint (required by `Result.warn` / `Result.fail` factory methods).
- Every passthrough is detectable for audit purposes via the `__adam_mcp_passthrough__` marker.

`BaseServer.mcp_server` exposes the underlying v2 `MCPServer` for advanced integration and in-memory protocol tests. MCP SDK v2 serves the 2026-07-28 revision while retaining compatibility with older MCP clients.

---

## Platform support

The Python SDK targets POSIX (macOS + Linux) and Windows as first-class platforms. The codebase uses `pathlib.Path` and `Path.home()` throughout; no POSIX-specific syscalls. MCP Python SDK v2 handles stdio transport on both platforms.

| | macOS / Linux | Windows |
|---|---|---|
| Install | `uv sync --all-extras` | `uv sync --all-extras` |
| Run tests | `uv run python -m pytest python/tests/` (each test dir separately) | same |
| Reference MCP | `uv run --directory reference-mcp/adam-greet python -m adam_greet.mcp.server` | same |
| `Path.home()` source | `$HOME` | `%USERPROFILE%` (or `$HOME` if set) |
| Output dir | `~/<name>-output/` | `%USERPROFILE%\<name>-output\` |

Use `uv run python -m pytest` rather than `uv run pytest`. The `python -m` form invokes the venv's pytest directly; `uv run pytest` resolves the script through `$PATH` and can pick up a system pytest from Homebrew/Scoop/etc. if it's earlier in the PATH.

## Cross-language parity

The `Result` wire format is byte-identical between this Python SDK and [adam-mcp-zig](https://github.com/dreliq9/adam-mcp-zig). Same canonical field order, same `envelope_version`, same default values. Tools written against either SDK speak the same wire. See [adam-mcp-zig's `tools/byte_equivalence_check.sh`](https://github.com/dreliq9/adam-mcp-zig/blob/main/tools/byte_equivalence_check.sh) for the cross-language verification harness.

## Roadmap

See [ROADMAP.md](./ROADMAP.md). Phase B follow-ups include broader audit rule coverage, additional language packs (TS / Rust / Kotlin), and migration tooling for downstream MCPs as the spec evolves pre-1.0.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Short version: PRs welcome, file an issue first for non-trivial changes, run the test suites before submitting, respect `audit rule_id` stability.

## License

[MIT](./LICENSE).
