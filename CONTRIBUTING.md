# Contributing to adam-mcp-sdk

Thanks for your interest. A few expectations before sending a PR.

## File an issue first

For anything beyond a typo or a one-line bug fix, open an issue first so we can sanity-check direction before you spend time on a patch. Small docs / typo PRs without a prior issue are welcome.

## Required reading

[`HOUSE_STYLE.md`](./HOUSE_STYLE.md) is the cross-language source of truth for what a tool is, what a `Result` is, and what an escape hatch is. This Python SDK is the reference implementation; the [Zig sibling](https://github.com/dreliq9/adam-mcp-zig) is a port that obeys the same spec.

[`DECISIONS.md`](./DECISIONS.md) is the architectural decision log. Major changes should land an entry there.

## Testing

```bash
# Sync once
uv sync --all-extras

# Then per test suite (each has its own root):
uv run python -m pytest python/tests/                  # 36 tests
uv run python -m pytest cli/tests/                     # 29 tests
uv run python -m pytest claude-pack/tests/             # 10 tests
uv run python -m pytest reference-mcp/adam-greet/tests/  # 9 tests

# Self-check (cross-link integrity in this repo):
uv run --project python adam-mcp audit --self-check
```

Tests must pass on macOS/Linux and Windows. CI runs the matrix on every PR.

**Tip:** use `uv run python -m pytest`, not `uv run pytest`. The `python -m` form invokes the venv's pytest directly; the script form can pick up a system pytest from Homebrew/Scoop/etc. if it's earlier in your `$PATH`.

## Code style

- **Format / lint with `ruff`.** CI rejects unformatted code:
  ```bash
  uv run ruff format .
  uv run ruff check .
  ```
- **Type hints required** on public functions. The `Result[T]` generic should always be parameterized.
- **No `print()` in library code.** Use the `adam_mcp_py` logger (stderr-only — keeps stdio JSON-RPC clean).

## Cross-platform rules

- Use `pathlib.Path` and `Path.home()` — they handle Windows `USERPROFILE` automatically.
- Don't hardcode `/Users/` or `/home/` style paths in tests; use `tmp_path` fixtures.
- Don't import POSIX-only modules (`fcntl`, `pwd`, `grp`, etc.) without an `if sys.platform != "win32"` guard.

## Audit rule IDs are stable

`rule_id` strings (`§N.NN`) in `cli/adam_mcp_cli/audit_rules.py::REGISTRY` are frozen forever once published. See §3.18 in the spec. A rule may be deprecated (removed from `REGISTRY`) but its `rule_id` is reserved permanently — never reassigned to a different rule. Removals get a `DECISIONS.md` entry.

The `--self-check` extension verifies every CHANGELOG `### Breaking` bullet's `**§X.Y**` resolves to a registered `rule_id`. Don't break this.

## Pre-1.0

The public API of `adam_mcp_py` may break between minor versions until v1.0. Breaking changes require a `CHANGELOG.md ### Breaking` entry citing the affected `rule_id`.

## House style discipline

When you add or change a tool/decorator in the library, the cross-link contract requires:

- A spec entry in `HOUSE_STYLE.md` with a `→ Library:` pointer to the exact symbol name.
- A docstring on the public symbol naming the rule it implements (e.g., `"""Implements §1.1."""`).
- `adam-mcp audit --self-check` must pass before commit.

These cross-link checks are mechanical, not aesthetic — they're what keep the spec and implementation honest with each other across the Python and Zig packs.

## License

By contributing, you agree your contributions will be licensed under the MIT License, same as the rest of the project. See [LICENSE](./LICENSE).
