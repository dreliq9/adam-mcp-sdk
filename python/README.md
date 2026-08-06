# adam-mcp-py

Methodology-first primitives for building Model Context Protocol servers in Python:
a typed `Result` envelope, validation and guardrail decorators, predictable output
locations, and explicit escape hatches.

```bash
pip install adam-mcp-py
```

Version 0.3.3 supports Python 3.11+ and pins the stable MCP Python SDK 2.0.0,
including the 2026-07-28 protocol line with backward compatibility for older MCP
clients. `BaseServer` now wraps `MCPServer` while preserving the existing Adam
house-style decorator and Result-enforcement surface.

The package is pre-1.0; pin exact versions in downstream applications. See the
[repository](https://github.com/dreliq9/adam-mcp-sdk) for documentation, examples,
the specification, changelog, and contribution guide.
