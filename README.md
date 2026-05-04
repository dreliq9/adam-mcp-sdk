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
cd ~/Projects/adam-mcp-sdk
uv sync
```

## Usage

```bash
# Scaffold a new MCP
adam-mcp new my-thing

# Audit it against the spec
adam-mcp audit ~/Projects/my-thing
```

See `HOUSE_STYLE.md` for the rules. See `reference-mcp/adam-greet/` for a worked example.
