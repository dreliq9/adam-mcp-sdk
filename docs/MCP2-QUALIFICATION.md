# MCP 2 migration qualification

Qualified locally on 2026-10-26 from PR 5 `b69b4279f159c19a8f7c4d86901418b9bb0e7d4d`.
Current main `82baa178c851513bd711cf9dcae9dc2f9e59383a` is already an ancestor.
The original PR/remote refs and local SDK histories are preserved separately.
No active checkout or MCP environment is adopted by this work.

## Locked contract and repairs

The committed lock resolves 50 packages: `adam-mcp-py==0.3.3`,
`adam-mcp-cli==0.2.3`, `adam-greet==0.1.0` and `mcp==2.0.0`.
The original lock still described SDK 0.3.2/CLI 0.2.2/MCP 1.28.1;
locked checking and a manifest/lock regression reproduced that drift.
CI sync/test commands now require the lock instead of silently regenerating it.

MCP 2 wraps structured dataclass output under `result`. Protocol tests and the
CI wheel smoke use that contract, while the text payload and version-1 Adam
Result envelope are unchanged. BaseServer advertises its actual enforced Result
return type even for missing/wrong hints; unknown return forward references no
longer prevent registration. Unknown input annotations still fail explicitly.
Typed Result return annotations remain typed. Focused protocol regressions cover
these cases through the real MCP 2 client, with failing-before/passing-after logs.

Scaffolding quotes metadata and Python descriptions, normalizes safe project
names (including dots, repeated separators and numeric-leading names), and rejects
Python-keyword packages before writing. Regressions parse generated TOML/JSON,
round-trip quotes/backslashes/newlines/Unicode/DEL, and compile generated Python.
The reference and scaffold Pydantic requirement uses compatible-release syntax.
Reference distribution readme metadata passes strict packaging checks.
Test output fixtures use task directories across platforms.

## Executed gates

| Platform | Python | Source tests |
| --- | --- | --- |
| Windows x64 | 3.11.15 | 116 passed |
| Windows x64 | 3.12.13 | 116 passed |
| Windows x64 | 3.13.15 | 116 passed |
| Alpine 3.24.3 x64/musl, uid 1000 | 3.13.13 | 116 passed |

Every final run has zero failed and zero skipped tests. Each run includes
53 library, 44 CLI, 10 command-pack and 9 reference tests, plus Ruff lint/format
and the house-style self-audit. These repeated matrices are the same tests,
not 464 distinct test cases. `uv lock --check` also passes.

All three wheel/source-distribution pairs build and pass strict metadata checks.
On both Windows and Linux, fresh environments install the same candidate wheels
and locked registry versions offline after cache preparation. From outside the
checkout, the installed CLI generates, audits and dry-runs an upgrade of a new
project; that project installs and serves actual stdio requests. Generated and
reference MCPs each pass modern-auto and legacy-mode client calls (four cases
per platform). Isolated Python mode prevents checkout imports. No production
MCPs or hardware are contacted.

Repeat with a task-owned environment/cache, not an existing server environment:

```text
uv sync --locked --all-extras --all-packages --python 3.13
uv lock --check
python qualification/check_workspace.py --output <new-absolute-evidence-directory>
uv build --all-packages --out-dir <absolute-dist-directory>
uv export --locked --all-extras --all-packages --no-emit-workspace --no-hashes --format requirements-txt --output-file <absolute-constraints-file>
python qualification/check_distributions.py --uv <absolute-uv-path> --dist <absolute-dist-directory> --constraints <absolute-constraints-file> --output <new-absolute-evidence-directory>
python qualification/check_downstream.py
```

The distribution gate requires cached dependencies/build tools before its offline
installs. Use short environment/output paths on Windows: one deliberately deep
task environment hit a dependency-file path limit. Linux tests use native storage;
Windows-mounted temporary files caused a pytest capture failure. Those attempts
are retained, and corrected-location reruns pass. No host path settings changed.

## Downstream compatibility and limits

The dependency projections use the candidate wheel's real Requires-Dist metadata
and the observed consumers' exact MCP/SDK requirements; real offline resolver
probes confirm the results. They are not full consumer graph resolutions.

| Consumer | Constraint result | Adoption status |
| --- | --- | --- |
| KiPilot | Its MCP/SDK ranges admit the candidate | Blocked: imports removed FastMCP and uses private framework APIs; needs a separate port and native qualification |
| CAiD MCP | MCP >=1.25,<2 conflicts with required MCP 2 | Blocked: dependency/API port; it is not a direct Adam SDK consumer |
| S32DS MCP | SDK 0.3.2/MCP 1.28.1 pins conflict | Blocked: align pins and validate its real lifecycle/stdio server before adoption |

A synthetic BaseServer/validates/Result fixture matching the public S32DS pattern
passes in-memory protocol checks. That establishes the exercised SDK pattern,
not the real debugger's lifecycle, transport, safety or hardware behavior.
Consumer modules were inspected as text and were not imported or started.

macOS and Linux Python 3.11/3.12 were not run. Real downstream environments,
KiCad/OCCT/debugger behavior, physical effects and release/publication remain
unqualified. This migration must not be installed into running MCP environments
as a dependency-only update. All running-server definitions and source checkouts
remain outside adoption scope; concurrent process turnover is recorded separately.

Exact source/lock/distribution hashes, matrix receipts, failed attempts, focused
regressions, independent review and recovery bundles are retained outside this
repository in the task's Python SDK PR 5 reconciliation evidence directory.
