---
name: mcp-scaffold
description: Scaffold a new MCP from a written SPEC.md. Pre: SPEC.md exists. Runs adam-mcp new, then customizes per spec.
---

Scaffold an MCP from an already-written `SPEC.md`. **Do not run if SPEC.md doesn't exist.** Use `/mcp-spec` first.

## Step 1: Verify SPEC.md exists

If `<target>/SPEC.md` doesn't exist, abort and tell the user to run `/mcp-spec` first.

## Step 2: Extract name and description from SPEC.md

The first H1 (`# <name> — SPEC`) gives the project name. The "## What this is" paragraph gives the description.

## Step 3: Run `adam-mcp new`

```bash
adam-mcp new <name> --description "<description>" --target <target>
```

This generates the full skeleton (pyproject, all docs, code layout, default tools, escape stub).

## Step 4: Customize tools per SPEC.md

For each tool category in the spec:
- Rename `core_tools.py` to the right name (e.g., `edit_tools.py`).
- Add the tool functions described in the spec.
- Run the pre-flight checklist for each tool (questions in `mcp-author` skill).
- Apply `@validates`, `@requires`, set `mode_tag`.

## Step 5: Customize the escape hatch

Replace the stub `<name_snake>_passthrough` body with the real raw-call into the underlying API/engine.

## Step 6: Customize LLM_GUIDE.md

Fill in the TBD sections with content from the spec. Required sections (per llm_guide_lint):
- Overview
- Critical workflow
- Tool categories
- Parameter gotchas
- Failure → fix
- Mode/path transparency
- Escape hatches

## Step 7: Customize CLAUDE.md

Fill in:
- When to use this MCP (trigger phrases)
- When NOT to use this MCP (boundaries)
- When to drop down to underlying APIs (Principle One)
- Co-tools

## Step 8: Run audit

```bash
adam-mcp audit <target>
```

Expected: `"status": "OK"`. If FAIL, fix the findings.

## Step 9: Run tests

```bash
cd <target>
uv sync && pytest tests/ -v
```

## Step 10: Hand back to user

Report: name, target dir, audit result, test result. Suggest commit.
