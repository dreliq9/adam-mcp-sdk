# adam-mcp-py

Methodology-first primitives for building Model Context Protocol servers in Python:
a typed `Result` envelope, validation and guardrail decorators, predictable output
locations, and explicit escape hatches.

```bash
pip install adam-mcp-py
```

Version 0.3.2 supports Python 3.11+ and MCP Python SDK releases from 1.28.1 up to,
but not including, 2.0. It adds async-safe server/decorator behavior and portable
Windows output and UTF-8 handling.

The package is pre-1.0; pin exact versions in downstream applications. See the
[repository](https://github.com/dreliq9/adam-mcp-sdk) for documentation, examples,
the specification, changelog, and contribution guide.
