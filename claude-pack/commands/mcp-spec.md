---
name: mcp-spec
description: Brainstorm and write SPEC.md for a new MCP, walking through Principle Zero questions before any code.
---

Walk the user through writing `SPEC.md` for a new MCP. Do **not** scaffold or write code — that's `/mcp-scaffold`.

## Step 1: Confirm the project name and target directory

Ask the user:
- What's the MCP called? (kebab-case)
- Where should it live? (default: `~/Projects/<name>`)

## Step 2: Walk through Principle Zero questions

Ask one at a time:

1. **What domain is this MCP serving?** (one paragraph)
2. **What does the agent want to do in this domain?** Phrase it as actions, not API calls. List 3–7 jobs.
3. **For each job: atomic or workflow?** If you'd describe the job with "and" — fetch X **and** transform **and** post — it's a workflow. Otherwise atomic.
4. **What underlying API/library/engine does this wrap?** What's the raw surface like?
5. **What state does the server need to remember?** (profile, history, watchlist, config — or none)
6. **What backends could serve this?** (local-only, web-only, both, with mode tags)
7. **What's the escape hatch?** Required by §6.30. For an external-API wrap: a raw-call tool. For an own-engine wrap: a raw-script-runner.

## Step 3: Categorize the tools

Group the jobs into `_tools.py` categories. Examples: `edit_tools.py`, `analysis_tools.py`, `query_tools.py`, `workflow_tools.py`, `escape_tools.py`. Each category becomes a file.

## Step 4: Identify guardrails

For each tool, ask: is there a precondition? (auth required, prior step needed, schema valid). Default WARN severity; FAIL only if destructive (data loss, irreversible action).

## Step 5: Write SPEC.md

Generate a SPEC.md mirroring the structure of `~/Projects/adam-mcp-sdk/reference-mcp/adam-greet/SPEC.md`:

- `## What this is` (paragraph)
- `## Repository layout` (tree)
- `## Dependencies` (toml block)
- `## Tools` (organized by `_tools.py` category, each with `name(args) -> Result[T] — description`)
- `## Backends` (each backend, mode_tag, what it wraps)
- `## Guardrails` (which tools have which preconditions)
- `## Output` (predictable directory)
- `## Build instruction` ("Build exactly what is described above. Do not add features not listed.")

Write the file to `<target>/SPEC.md`.

## Step 6: Confirm with the user

Show them the SPEC.md, ask for changes. Iterate until they approve.

**Do not run `/mcp-scaffold` yet.** Hand control back.
