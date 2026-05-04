# House Style — Rationale

The "why" behind each rule in `HOUSE_STYLE.md`. Stories, citations, and the MCP that taught us each lesson.

## Principle Zero — AI-shaped, not API-shaped

The agentic default — when given an API and asked to wrap it for MCP — is to write one tool per endpoint. This produces tools an AI can technically call but can't use well. Every MCP we've built that works has rejected this default.

**Examples:**
- `declip`'s `workflows/` directory — `vertical`, `ingest`, `beat_sync`, `cutdown`, `speech_cleanup`. None of these are FFmpeg endpoints. They're "things an AI editor wants to do," composed from many endpoints.
- `caid-mcp`'s `add_hole` takes *radius*, not diameter — the underlying OCP API takes diameter. Radius matches how an AI thinks about it (M3 = r1.5).
- `kipilot`'s `list_schematic_pins` hides the Y-axis flip math an AI shouldn't have to do. The KiCad library API exposes the raw coordinate system.
- `vulnerability-intelligence`'s `vulnerability_analyze` composes NVD + KEV + EPSS into one call. The agent doesn't chain three lookups; it asks one question.

## Principle One — Escape hatches always available

We almost shipped MCPs that trapped the agent inside our view of the world. The fix came from `caid-mcp`: even with 50+ validated tools, there's always something the user wants that the toolset doesn't cover. `run_cadquery_script` is the release valve — the agent writes raw CadQuery code, the MCP just executes and returns results.

## §1.1 Result type

Returning raw API responses produced two failure modes:
1. The agent gets confused parsing varied response shapes per tool.
2. Errors come back as exceptions or untyped dicts, with no actionable next step.

A unified `Result` shape gives the agent one parsing pattern across all tools, and the `hint` field forces the tool author to think about recovery.

## §1.3 Guardrails default WARN

Early MCPs hard-failed on edge cases that turned out to be common-but-fine. Agents learned to avoid those tools. Defaulting to WARN with a `force=True` override keeps the happy path strict and the escape-hatch path open.

## §2.5 Three-layer

`CAiD` (the lib) → `caid-mcp` (the wrapper). `kipilot` (the lib) → `kipilot/server.py` (the wrapper). `declip` (the lib) → `declip/mcp/` (the wrapper) → `declip/cli.py` (another wrapper).

The pattern: keep the domain logic usable as a Python library. The MCP and CLI are thin agent-facing surfaces over the library. This makes the library testable independently and reusable in non-MCP contexts.

## §2.7 Tool file organization

`mtg-mcp-server`'s server.py was 2000 lines. Refactoring tool-by-tool wasn't possible because everything imported everything. `_tools.py` files grouped by concern make refactoring a per-file activity.

## §3.14 LLM_GUIDE.md

Separate from README (human-facing) and CLAUDE.md (routing rules). The LLM_GUIDE is what the agent reads when about to use the MCP — it's the bridge between "I have a task" and "here's what to call." `caid-mcp`'s LLM_GUIDE is the canonical example: critical workflow order, parameter gotchas, coordinate systems, failure → fix.

## §5.27 Audit self-check

The risk: spec says one thing, library does another, templates do a third. Mechanical cross-link enforcement catches drift before it's released.
