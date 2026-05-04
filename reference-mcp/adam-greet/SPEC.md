# adam-greet — SPEC

## What this is

A deliberately mundane MCP that exemplifies every rule in `HOUSE_STYLE.md`. Domain: pulls weather + calendar + recent-music to compose context-aware morning greetings. Mundane on purpose — the rules show clearly because the domain doesn't distract.

## Repository layout

```
adam-greet/
  pyproject.toml
  SPEC.md
  LLM_GUIDE.md
  CLAUDE.md
  README.md
  CHANGELOG.md
  ROADMAP.md
  DECISIONS.md
  AUDIT.md
  server.json
  adam_greet/
    __init__.py
    types.py
    schema.py
    cli.py
    backends/
      __init__.py
      local.py        # in-process fakes; no network
      web.py          # would call real APIs in production
    workflows/
      __init__.py
      morning_briefing.py
    mcp/
      __init__.py
      server.py
      greeting_tools.py
      context_tools.py
      history_tools.py
      workflow_tools.py
      escape_tools.py
  tests/
    conftest.py
    test_greeting_tools.py
    test_workflow.py
    test_escape.py
```

## Dependencies

```toml
adam-mcp-py == 0.1.0
mcp >= 1.0
pydantic >= 2.5
```

## Tools (AI-shaped, not API-shaped)

### greeting_tools.py
- `compose_greeting(name: str, formality: int) -> Result[str]` — atomic; produces a single greeting line
- `compose_personalized_greeting(name: str) -> Result[str]` — uses stored preferences

### context_tools.py
- `get_morning_context() -> Result[MorningContext]` — bundles weather + calendar + recent-music

### history_tools.py
- `record_greeting(greeting: str) -> Result[None]` — stateful; remembers what we said
- `recent_greetings(n: int) -> Result[list[str]]` — recall

### workflow_tools.py
- `morning_briefing(name: str) -> Result[str]` — workflow composing 4 atomic ops; the AI-shaped happy path

### escape_tools.py
- `compose_raw_greeting(template: str) -> Result[str]` — `@passthrough`; bypasses synthesis logic

## Backends

`backends/local.py` and `backends/web.py` both implement `BackendProtocol`. `local.py` is the default — deterministic, no network. `web.py` exists to demonstrate mode/path transparency (`mode_tag = "[WEB]"` vs `"[LOCAL]"`).

## Guardrails

`morning_briefing` requires the calendar to be authenticated. Default WARN; with `force=True` it proceeds with placeholder calendar data.

## Output

State persists to `~/adam-greet-output/` via `adam_mcp_py.output_dir`.

## Build instruction

Build exactly what is described above. Do not add features not listed.
