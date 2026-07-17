# Adam MCP CLI

`adam-mcp-cli` scaffolds and audits MCP servers that follow the Adam MCP house style.

## Install

```bash
uv tool install adam-mcp-cli
```

The installed command is `adam-mcp`.

## Commands

```bash
adam-mcp --help
adam-mcp new example-mcp --target ./example-mcp
adam-mcp audit ./example-mcp
adam-mcp upgrade ./example-mcp --dry-run
```

`adam-mcp audit --self-check` is an SDK-maintainer command and must run from the
root of an `adam-mcp-sdk` checkout.
