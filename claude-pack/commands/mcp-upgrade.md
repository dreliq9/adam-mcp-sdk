---
name: mcp-upgrade
description: Bump the adam-mcp-py pin in this MCP project and apply audit-as-migration findings. Runs `adam-mcp upgrade`, then works through findings as edits in the active session.
---

Apply an SDK upgrade to the current MCP project. The CLI does the deterministic work (pin bump, sync, audit); you do the editing work guided by audit hints.

## Step 1: Verify project root

Determine the MCP project root:
- If the user passed an argument, use it.
- Else use `Path.cwd()`.

Verify `pyproject.toml` exists and contains `adam-mcp-py` as a dependency. If not, abort:

> Not an adam-mcp project: pyproject.toml missing or has no adam-mcp-py dependency.

## Step 2: Dry-run gate

Run:

```bash
adam-mcp upgrade --dry-run <path>
```

Show the user the result: `current → target` versions. Ask:

> Upgrade adam-mcp-py X.Y.Z → A.B.C? (y to proceed, or specify --to <version>)

WAIT for the user's explicit response. Do not proceed without confirmation.

## Step 3: Run the upgrade

Once confirmed, run:

```bash
adam-mcp upgrade <path> --to <chosen>
```

Outcomes:
- `"status": "FAIL"` — show the hint, stop. Do not retry. Common causes: malformed pyproject.toml, downgrade attempt, `uv sync` conflict. The user fixes and re-invokes.
- `"status": "OK"` with no findings — done. Suggest a commit message (see Step 6) and stop.
- `"status": "WARN"` with findings — continue to Step 4.

## Step 4: Read CHANGELOG context

Read `CHANGELOG.md` from the installed `adam-mcp-py` package. Locate entries between the `current` and `target` versions. Surface the `### Breaking` sections to the user as context — these are the *why* behind each finding the audit produced.

## Step 5: Work through findings (batch-fix)

Strategy: batch-fix. Work through every finding, then re-audit. Do NOT pause per finding.

For each finding in the upgrade `Result.value.findings`:
1. Read the finding's `hint` carefully.
2. Read the affected file(s) to understand context.
3. Apply the edit per the hint.
4. If a hint is unclear or the fix needs a judgment call, pause and ask the user (this is the escape hatch — frequent firing here is signal to improve the hint, not the slash command).

After all findings are addressed, re-run:

```bash
adam-mcp audit <path>
```

Outcomes:
- Clean (`"status": "OK"`) — done, proceed to Step 6.
- New findings — repeat Step 5 (max **3 iterations** total). After 3, report what's left and ask the user.

The 3-iteration cap is a hard bound: if findings keep regenerating, that's likely a buggy audit rule causing oscillation. Don't loop forever.

## Step 6: Final report

When the audit comes back clean, report:

> Upgraded adam-mcp-py X.Y.Z → A.B.C. Fixed N findings.
>
> Suggested commit:
>
>     chore: upgrade adam-mcp-py X.Y.Z → A.B.C

Do **not** run git operations automatically. Per CLAUDE.md, git operations need explicit user approval. The user can copy/paste the suggestion or tell you to commit.

## What this command is NOT responsible for

- Running tests (separate concern; user runs them after).
- Committing (above).
- Updating multiple MCPs at once (single-project command; bulk upgrade is later work).
