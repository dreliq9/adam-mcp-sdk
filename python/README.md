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

## MCP 2 response and migration boundary

MCP 2 exposes the dataclass envelope as `response.structured_content["result"]`.
The text-content JSON is the envelope itself. The Adam `Result` fields, canonical
order and envelope version remain unchanged. Missing or incorrect tool return
annotations cannot override BaseServer's Result enforcement.

This package requires MCP 2; it does not adapt MCP 1-only applications or removed
FastMCP internals automatically. See [migration qualification](../docs/MCP2-QUALIFICATION.md)
for the tested matrix and downstream adoption limits.
