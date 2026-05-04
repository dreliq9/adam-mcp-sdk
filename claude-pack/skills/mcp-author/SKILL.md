---
name: mcp-author
description: Use when building, modifying, or reviewing MCPs in the Adam house style. Activates on phrases like "build an MCP", "new MCP", "add a tool to my MCP", "audit this MCP", or any reference to adam_mcp_py, adam-mcp CLI, HOUSE_STYLE.md.
---

<!-- mirrors HOUSE_STYLE.md Principle Zero + Principle One + §1 + §6 -->

# mcp-author

You are about to author or review an MCP in the Adam house style. **Before writing any tool code, read this in full.**

## Principle Zero — AI-shaped, not API-shaped

The unit of a tool is "a coherent thing an AI can do," not "an API endpoint." If clumping multiple API calls into one workflow-shaped tool makes the AI parse it better, do that. If splitting one API call into multiple specialized tools makes the AI parse it better, do that. The API surface is irrelevant to the tool surface.

**You will be tempted to write one tool per API endpoint. Don't. That's the shallow-wrapper default. The unit of work is what an AI does, not what an API exposes.**

## Principle One — Escape hatches always available

Tools shaped for AI consumption are the happy path. They are not a cage. When the agent's task doesn't fit any tool's shape, it must be able to drop down to the underlying API/library/protocol directly. Every MCP ships an `@passthrough`-decorated tool.

Canonical example: `caid-mcp`'s `run_cadquery_script`.

## §1 Tool contract (load-bearing — verbatim from HOUSE_STYLE.md)

### §1.1 Result type

Every tool returns a typed `Result(status, value, raw, metrics, diagnostics, hint, mode_tag)`. Never raw output, never raw exceptions.

**If you can't write a useful `hint` on FAIL, the tool's shape is wrong.**

### §1.2 Validation layer

The MCP validates inputs before delegating to the underlying API. Use `@validates(<PydanticModel>)`.

### §1.3 Process guardrails

Default severity WARN; FAIL only when destructive. Use `@requires(precondition, fail_hint=..., severity="WARN" | "FAIL")`. Allow `force=True` to override.

### §1.4 Mode/path transparency

Result tells the agent which backend was used. Set `Result.mode_tag`.

## Pre-flight checklist (run before writing any tool)

1. **What's the AI's coherent unit of work here?** Not "what API endpoint am I wrapping" — "what's the smallest thing an AI agent naturally wants to do in this domain?" If the answer is "wrap this endpoint," reread Principle Zero.
2. **Compose or atomic?** If you'd describe it with the word "and" — *fetch the data **and** transform it **and** post the result* — it's probably a workflow.
3. **Result hint on FAIL?** What's the next thing the agent should try if this fails? **If you can't write a useful hint, the tool's shape is wrong.**
4. **Precondition guardrail?** Is there state that must be valid before this runs? Encode it as `@requires(...)`. Default WARN; FAIL only if destructive.
5. **Backend mode tag?** If multiple backends could serve this, what `mode_tag` belongs on the result?
6. **Escape path?** If this tool's shape doesn't fit some legitimate task in this domain, what does the agent fall back to? If "the agent is stuck," the MCP needs an escape hatch (or one it has needs to be more visible).

## Workflow

For new MCPs:
1. `/mcp-spec <name>` — write SPEC.md by walking through Principle Zero questions.
2. `/mcp-scaffold` — run `adam-mcp new`, then customize per spec.
3. Build tools, running the pre-flight checklist for each.
4. `/mcp-audit` — must pass before declaring done.

For existing MCPs:
1. `/mcp-audit <path>` — see how far it is from house style.
2. Fix in priority: missing escape hatch → missing required docs → missing required sections → tool shape issues.

## References

- Full spec: `~/Projects/adam-mcp-sdk/HOUSE_STYLE.md`
- Reference MCP (model after this): `~/Projects/adam-mcp-sdk/reference-mcp/adam-greet/`
- Audit CLI: `adam-mcp audit <path>`
