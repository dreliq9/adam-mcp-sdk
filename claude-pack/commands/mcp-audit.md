---
name: mcp-audit
description: Two-pass audit of an MCP. First mechanical (adam-mcp audit), then semantic (Principle Zero application, tool shape, hint quality).
---

Run a two-pass audit of an MCP. The CLI catches mechanical issues; you catch design issues.

## Pass 1: Mechanical

```bash
adam-mcp audit <path>
```

Capture the report. If `status` is FAIL, list every finding and propose fixes. Do not start fixing yet — let the user decide.

## Pass 2: Semantic (this is your job)

For each `_tools.py` file:

### Principle Zero check
- Does each tool represent "a coherent thing an AI can do" or "an API endpoint"?
- Look for tools whose names mirror API endpoint names — that's a smell.
- Look for tools that take many flags to serve different purposes — split them.
- Look for tools that always need to be called in the same sequence — consider a workflow.

### Tool shape check
- Does each tool return `Result`? (mechanical caught this; verify nothing got past it.)
- Is `Result.hint` actually useful on FAIL? Or generic ("an error occurred")?
- Are diagnostics meaningful (state of inputs, what was attempted), or just exception strings?
- Is `mode_tag` set when there are multiple backends?

### Workflow check
- Are workflows in `workflows/`?
- Does each workflow's `Result` have `metrics` describing the steps performed?

### Escape hatch check
- Is the escape hatch real (raw-call into underlying API/engine), or still a stub?
- Is it documented in `LLM_GUIDE.md`'s "Escape hatches" section?
- Is `Result.raw` populated?

### Guardrail check
- Are guardrails using `@requires`?
- Default severity WARN, only FAIL when destructive — verify each FAIL is justified.

## Pass 3: Report

Output a markdown report with:
- Mechanical pass result
- Semantic findings, grouped by severity
- Recommended fix order

Do not auto-fix. Hand back to the user.
