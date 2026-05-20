# adam-mcp-sdk

Personal MCP SDK encoding the Adam house style. One repo, multiple deliverables.

## What's here

| Path | What it is |
|------|-----------|
| `HOUSE_STYLE.md` | The spec. Source of truth for everything. |
| `HOUSE_STYLE_RATIONALE.md` | Why each rule exists, with links to the MCP that taught us. |
| `python/` | `adam-mcp-py` library — the primitives (Result, BaseServer, etc.). |
| `cli/` | `adam-mcp` CLI — `new`, `audit`. |
| `claude-pack/` | Claude Code plugin: `mcp-author` skill + `/mcp-spec`, `/mcp-scaffold`, `/mcp-audit`. |
| `reference-mcp/adam-greet/` | Canonical reference MCP. Embodies every rule. Templates are extracted from this. |

## Install (development)

```bash
# macOS / Linux
cd ~/Projects/adam-mcp-sdk
uv sync
```

```powershell
# Windows (PowerShell)
cd $HOME\Projects\adam-mcp-sdk
uv sync
```

## Usage

```bash
# Scaffold a new MCP
adam-mcp new my-thing

# Audit it against the spec
adam-mcp audit ~/Projects/my-thing

# Self-check (verifies cross-link integrity)
adam-mcp audit --self-check
```

On Windows, the same commands work in PowerShell or cmd. Paths follow Windows conventions: `adam-mcp audit $HOME\Projects\my-thing`.

## Platform support

The Python SDK targets POSIX (macOS + Linux) and Windows as first-class platforms. The codebase uses `pathlib.Path` and `Path.home()` throughout; no POSIX-specific syscalls. FastMCP (the underlying MCP transport) handles stdio JSON-RPC on both platforms.

| | macOS / Linux | Windows |
|---|---|---|
| Install | `uv sync --all-extras` | `uv sync --all-extras` |
| Run tests | `uv run python -m pytest python/tests/` (each test dir separately) | same |
| Reference MCP | `uv run --directory reference-mcp/adam-greet python -m adam_greet.mcp.server` | same |
| `Path.home()` source | `$HOME` | `%USERPROFILE%` (or `$HOME` if set) |
| Output dir | `~/<name>-output/` | `%USERPROFILE%\<name>-output\` |

Use `uv run python -m pytest` rather than `uv run pytest`. The `python -m` form invokes the venv's pytest directly; `uv run pytest` resolves the script through `$PATH` and can pick up a system pytest from Homebrew/Scoop/etc. if it's earlier in the PATH.

See `HOUSE_STYLE.md` for the rules. See `reference-mcp/adam-greet/` for a worked example.
