# CLI Wheel Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `adam-mcp-cli` 0.2.2 installable and fully usable from its wheel, then validate and publish that first public CLI release without changing `adam-mcp-py` 0.3.2.

**Architecture:** Runtime audit schemas and scaffold templates become canonical resources inside `adam_mcp_cli`. Package-relative imports and `importlib.resources` replace repository-relative paths. Only `audit --self-check` retains an SDK-checkout dependency, guarded by explicit sentinel validation and a structured failure outside the repository.

**Tech Stack:** Python 3.11+, Typer, Jinja2, `importlib.resources`, Hatchling, uv, pytest, Ruff, Twine, GitHub Actions, PyPI trusted publishing.

## Global Constraints

- Work on `agent/cli-wheel-publishing` from `/Users/adamsteen/projects/adam-mcp-sdk`.
- Preserve `adam-mcp-cli==0.2.2`; this version has not been published to PyPI.
- Do not change, rebuild, or republish `adam-mcp-py==0.3.2`.
- Keep `spec/schemas/server_json.schema.json` in place; it is not a CLI runtime import.
- Maintain one canonical schema implementation and one canonical template tree—no synchronized copies.
- Preserve existing normal audit, scaffold, and upgrade result envelopes.
- Run each red test before its implementation and record that it fails for the intended reason.
- Use `apply_patch` for content edits and preserve unrelated worktree changes.
- Commit after each green task with the exact commit subject shown.

---

## Task 1: Add package-resource regression tests

**Files:**

- Create: `cli/tests/test_packaged_resources.py`
- Test: `cli/tests/test_packaged_resources.py`

- [ ] **Step 1: Add tests that specify the installed-package resource boundary**

Create `cli/tests/test_packaged_resources.py`:

```python
"""Release invariants for resources required by an installed CLI wheel."""

from importlib import resources


def test_audit_schema_modules_are_packaged():
    package = resources.files("adam_mcp_cli.schemas")
    assert package.joinpath("spec_md_lint.py").is_file()
    assert package.joinpath("llm_guide_lint.py").is_file()


def test_scaffold_templates_are_packaged():
    templates = resources.files("adam_mcp_cli").joinpath("templates", "_base")
    required = (
        "pyproject.toml.j2",
        "SPEC.md.j2",
        "server.json.j2",
        "tests/test_core_tools.py.j2",
        "{{name_snake}}/mcp/server.py.j2",
    )
    for relative_path in required:
        resource = templates.joinpath(*relative_path.split("/"))
        assert resource.is_file(), relative_path
```

- [ ] **Step 2: Run the new tests and confirm the expected red state**

Run:

```bash
uv run python -m pytest cli/tests/test_packaged_resources.py -q
```

Expected: failure because `adam_mcp_cli.schemas` and `adam_mcp_cli/templates/_base` do not exist.

- [ ] **Step 3: Leave the red tests uncommitted for Task 2**

Do not create a deliberately broken commit. Task 2 makes the schema half of this
test file green and includes the regression test in that focused commit; Task 3
makes the template half green.

---

## Task 2: Package audit schema modules and remove the path hack

**Files:**

- Create: `cli/adam_mcp_cli/schemas/__init__.py`
- Move: `spec/schemas/spec_md_lint.py` → `cli/adam_mcp_cli/schemas/spec_md_lint.py`
- Move: `spec/schemas/llm_guide_lint.py` → `cli/adam_mcp_cli/schemas/llm_guide_lint.py`
- Modify: `cli/adam_mcp_cli/audit_rules.py:7-18`
- Preserve: `spec/schemas/server_json.schema.json`
- Test: `cli/tests/test_packaged_resources.py`
- Test: `cli/tests/test_cmd_audit.py`

- [ ] **Step 1: Move the schema implementations into the CLI package**

Create `cli/adam_mcp_cli/schemas/__init__.py` with:

```python
"""Schema-oriented lint helpers bundled with adam-mcp-cli."""
```

Move the two lint modules without changing their behavior. Confirm the source directory retains only the JSON schema:

```bash
find spec/schemas -maxdepth 1 -type f -print | sort
```

Expected: `spec/schemas/server_json.schema.json` only.

- [ ] **Step 2: Replace repository path mutation with relative imports**

In `cli/adam_mcp_cli/audit_rules.py`, remove `import sys`, `_REPO_ROOT`, `sys.path.insert`, and the `# noqa: E402` imports. Use:

```python
from .schemas.llm_guide_lint import check_llm_guide
from .schemas.spec_md_lint import check_spec_md
```

- [ ] **Step 3: Run focused schema and audit tests**

```bash
uv run python -m pytest \
  cli/tests/test_packaged_resources.py::test_audit_schema_modules_are_packaged \
  cli/tests/test_cmd_audit.py -q
```

Expected: schema-resource test passes; audit tests remain green.

- [ ] **Step 4: Prove importing the command no longer depends on `spec/`**

```bash
uv run --project cli python -c 'from adam_mcp_cli.main import app; print(app.info.help)'
```

Expected: prints `Adam MCP CLI.` with no `ModuleNotFoundError`.

- [ ] **Step 5: Commit the schema relocation**

```bash
git add cli/adam_mcp_cli/audit_rules.py cli/adam_mcp_cli/schemas cli/tests/test_packaged_resources.py spec/schemas
git commit -m "fix: package CLI audit schemas"
```

---

## Task 3: Move and render scaffold templates as package resources

**Files:**

- Move: `python/templates/_base/**` → `cli/adam_mcp_cli/templates/_base/**`
- Create: `cli/adam_mcp_cli/templates/__init__.py`
- Modify: `cli/adam_mcp_cli/templates_loader.py`
- Modify: `HOUSE_STYLE.md:95`
- Test: `cli/tests/test_packaged_resources.py`
- Test: `cli/tests/test_cmd_new.py`
- Test: `cli/tests/test_cmd_audit.py`

- [ ] **Step 1: Extend the renderer tests for nested traversal and binary copying**

Append to `cli/tests/test_packaged_resources.py`:

```python
from adam_mcp_cli.templates_loader import render_tree


def test_render_tree_handles_nested_resources_and_binary_files(tmp_path, monkeypatch):
    class FakeResource:
        def __init__(self, name, *, children=(), text=None, data=None):
            self.name = name
            self._children = tuple(children)
            self._text = text
            self._data = data

        def is_dir(self):
            return bool(self._children)

        def is_file(self):
            return not self._children

        def iterdir(self):
            return iter(self._children)

        def read_text(self, encoding="utf-8"):
            assert encoding == "utf-8"
            return self._text

        def read_bytes(self):
            return self._data

    root = FakeResource(
        "_base",
        children=(
            FakeResource(
                "{{name_snake}}",
                children=(FakeResource("value.txt.j2", text="{{ description }}"),),
            ),
            FakeResource("logo.bin", data=b"\x00\xff"),
        ),
    )
    monkeypatch.setattr("adam_mcp_cli.templates_loader.template_root", lambda: root)

    render_tree(tmp_path, {"name_snake": "demo", "description": "hello"})

    assert (tmp_path / "demo" / "value.txt").read_text() == "hello"
    assert (tmp_path / "logo.bin").read_bytes() == b"\x00\xff"
```

Run it before implementation:

```bash
uv run python -m pytest \
  cli/tests/test_packaged_resources.py::test_render_tree_handles_nested_resources_and_binary_files -q
```

Expected: failure because the current loader calls `rglob()` and assumes `Path` resources.

- [ ] **Step 2: Move the canonical template tree into the distribution package**

Move all files under `python/templates/_base/` into `cli/adam_mcp_cli/templates/_base/`. Add:

```python
# cli/adam_mcp_cli/templates/__init__.py
"""Scaffold resources bundled with adam-mcp-cli."""
```

Delete the now-empty `python/templates/` tree. Do not retain a second copy.

- [ ] **Step 3: Implement Traversable-safe recursion**

Replace `cli/adam_mcp_cli/templates_loader.py` with:

```python
"""Render the packaged scaffold resource tree."""

from __future__ import annotations

from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path

from jinja2 import BaseLoader, Environment, StrictUndefined


def template_root() -> Traversable:
    """Return the canonical packaged scaffold tree."""
    return resources.files("adam_mcp_cli.templates").joinpath("_base")


def _render_name(name: str, context: dict[str, str]) -> str:
    for key, value in context.items():
        name = name.replace("{{" + key + "}}", value)
    return name


def _render_resource(
    source: Traversable,
    destination: Path,
    context: dict[str, str],
    environment: Environment,
) -> None:
    for child in source.iterdir():
        rendered_name = _render_name(child.name, context)
        target = destination / rendered_name
        if child.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            _render_resource(child, target, context, environment)
        elif child.name.endswith(".j2"):
            target = destination / rendered_name.removesuffix(".j2")
            target.parent.mkdir(parents=True, exist_ok=True)
            template = environment.from_string(child.read_text(encoding="utf-8"))
            target.write_text(template.render(**context), encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(child.read_bytes())


def render_tree(target_dir: Path, context: dict[str, str]) -> None:
    """Render the packaged scaffold into ``target_dir``."""
    source = template_root()
    if not source.is_dir():
        raise RuntimeError("adam-mcp-cli package is missing templates/_base")
    environment = Environment(loader=BaseLoader(), undefined=StrictUndefined)
    target_dir.mkdir(parents=True, exist_ok=True)
    _render_resource(source, target_dir, context, environment)
```

- [ ] **Step 4: Update the canonical template documentation link**

In `HOUSE_STYLE.md`, replace `python/templates/_base/` with `cli/adam_mcp_cli/templates/_base/`.

- [ ] **Step 5: Run focused package and behavior tests**

```bash
uv run python -m pytest \
  cli/tests/test_packaged_resources.py \
  cli/tests/test_cmd_new.py \
  cli/tests/test_cmd_audit.py::test_audit_passes_freshly_scaffolded_project -q
```

Expected: all pass and the nested fake resource test proves no filesystem-only API is used.

- [ ] **Step 6: Check for stale template paths**

```bash
rg -n "python/templates/_base|_TEMPLATES_ROOT" . --glob '!docs/superpowers/specs/**' --glob '!docs/superpowers/plans/**'
```

Expected: no matches.

- [ ] **Step 7: Commit the template relocation**

```bash
git add HOUSE_STYLE.md cli/adam_mcp_cli/templates cli/adam_mcp_cli/templates_loader.py cli/tests/test_packaged_resources.py python/templates
git commit -m "fix: package CLI scaffold templates"
```

---

## Task 4: Make self-check explicitly repository-only

**Files:**

- Modify: `cli/adam_mcp_cli/main.py:1-105`
- Modify: `cli/tests/test_cmd_audit.py:61-127`
- Test: `cli/tests/test_cmd_audit.py`

- [ ] **Step 1: Replace module-path monkeypatch tests with explicit-root tests**

Add this test near the other self-check tests:

```python
def test_self_check_outside_sdk_checkout_returns_structured_failure(tmp_path: Path):
    from adam_mcp_cli.main import _self_check_v2

    report = _self_check_v2(tmp_path)

    assert report["status"] == "FAIL"
    assert report["mode"] == "self-check"
    assert report["value"] is None
    assert "adam-mcp-sdk checkout" in report["hint"]
    assert "HOUSE_STYLE.md" in report["diagnostics"]
    assert report["findings"] == []
```

Change the two synthetic tests to call `_self_check_v2(tmp_path)` and remove their `monkeypatch` arguments and `_SELF_CHECK_REPO_ROOT` patches. Change the real-repository test to:

```python
def test_self_check_passes_on_real_repo():
    from adam_mcp_cli.main import _self_check_v2

    repo_root = Path(__file__).resolve().parents[2]
    report = _self_check_v2(repo_root)
    assert report["status"] == "OK", (
        f"Self-check failed on real SDK repo. Findings: {report['findings']}"
    )
```

Because the sentinel check requires source files, add minimal sentinels to both synthetic repo fixtures before calling the function:

```python
(tmp_path / "cli" / "adam_mcp_cli").mkdir(parents=True)
(tmp_path / "cli" / "adam_mcp_cli" / "audit_rules.py").write_text("", encoding="utf-8")
(tmp_path / "python" / "adam_mcp_py").mkdir(parents=True)
(tmp_path / "python" / "adam_mcp_py" / "validation.py").write_text(
    "def wrapper(input):\n    return input\n", encoding="utf-8"
)
```

- [ ] **Step 2: Run the outside-checkout test and confirm it is red**

```bash
uv run python -m pytest \
  cli/tests/test_cmd_audit.py::test_self_check_outside_sdk_checkout_returns_structured_failure -q
```

Expected: failure because `_self_check_v2` accepts no root and still derives it from the installed module.

- [ ] **Step 3: Pass the command path explicitly and validate SDK sentinels**

Remove `_SELF_CHECK_REPO_ROOT`. Change command dispatch to:

```python
if self_check:
    report = _self_check_v2(path.resolve())
else:
    report = audit_project(path)
```

Change the helper signature and initial block to:

```python
_SELF_CHECK_SENTINELS = (
    "HOUSE_STYLE.md",
    "CHANGELOG.md",
    "cli/adam_mcp_cli/audit_rules.py",
    "python/adam_mcp_py/validation.py",
)


def _self_check_v2(repo_root: Path | None = None) -> dict:
    """Run SDK repository cross-link checks from an explicit checkout root."""
    from .audit_rules import REGISTRY

    repo = (repo_root or Path.cwd()).resolve()
    missing = [relative for relative in _SELF_CHECK_SENTINELS if not (repo / relative).is_file()]
    if missing:
        return {
            "status": "FAIL",
            "mode": "self-check",
            "value": None,
            "metrics": {"findings": 0, "fails": 1},
            "diagnostics": missing,
            "findings": [],
            "hint": "Run audit --self-check from the adam-mcp-sdk checkout root.",
        }

    findings: list[dict] = []
```

Retain the existing four checks after this guard. Remove the old special-case `HOUSE_STYLE.md` missing block because the sentinel guard owns it.

- [ ] **Step 4: Run all self-check tests and real CLI invocations**

```bash
uv run python -m pytest cli/tests/test_cmd_audit.py -q
uv run --project cli adam-mcp audit . --self-check
outside=$(mktemp -d)
uv run --project cli adam-mcp audit "$outside" --self-check; test $? -eq 1
```

Expected: tests pass; repository invocation reports `OK`; outside invocation prints structured JSON, exits 1, and contains no traceback.

- [ ] **Step 5: Commit the repository boundary**

```bash
git add cli/adam_mcp_cli/main.py cli/tests/test_cmd_audit.py
git commit -m "fix: guard repository-only CLI self-check"
```

---

## Task 5: Add complete CLI distribution metadata and resource inclusion

**Files:**

- Create: `cli/README.md`
- Create: `cli/LICENSE`
- Modify: `cli/pyproject.toml`
- Test: built artifacts under temporary directories only

- [ ] **Step 1: Add package-local release documentation**

Create `cli/README.md` containing:

```markdown
# Adam MCP CLI

`adam-mcp-cli` scaffolds and audits MCP servers that follow the Adam MCP house style.

## Install

```bash
uv tool install adam-mcp-cli
```

The installed command is `adam-mcp`.

## Commands

```bash
adam-mcp --help
adam-mcp new example-mcp --target ./example-mcp
adam-mcp audit ./example-mcp
adam-mcp upgrade ./example-mcp --dry-run
```

`adam-mcp audit --self-check` is an SDK-maintainer command and must run from the
root of an `adam-mcp-sdk` checkout.
```

Copy the repository MIT license text into `cli/LICENSE` so the CLI sdist is self-contained.

- [ ] **Step 2: Complete project metadata and declare packaged artifacts**

Expand `cli/pyproject.toml` to include:

```toml
[project]
name = "adam-mcp-cli"
version = "0.2.2"
description = "Scaffold and audit MCP servers using the Adam MCP house style"
readme = "README.md"
license = "MIT"
authors = [{ name = "Adam Steen" }]
requires-python = ">=3.11"
keywords = ["mcp", "model-context-protocol", "cli", "scaffolding", "audit"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Software Development :: Code Generators",
]
```

Keep existing dependencies and scripts, then add:

```toml
[project.urls]
Homepage = "https://github.com/dreliq9/adam-mcp-sdk"
Repository = "https://github.com/dreliq9/adam-mcp-sdk"
Issues = "https://github.com/dreliq9/adam-mcp-sdk/issues"
Changelog = "https://github.com/dreliq9/adam-mcp-sdk/blob/main/CHANGELOG.md"

[tool.hatch.build.targets.wheel]
packages = ["adam_mcp_cli"]
artifacts = ["adam_mcp_cli/templates/**/*.j2"]

[tool.hatch.build.targets.sdist]
include = [
    "/adam_mcp_cli",
    "/tests",
    "/README.md",
    "/LICENSE",
    "/pyproject.toml",
]
```

The package directory already makes schema `.py` modules wheel content; the explicit artifact glob protects template `.j2` files from omission.

- [ ] **Step 3: Build artifacts into an isolated directory**

```bash
rm -rf /tmp/adam-mcp-cli-artifacts
uv build --package adam-mcp-cli --out-dir /tmp/adam-mcp-cli-artifacts
uvx --from twine twine check --strict /tmp/adam-mcp-cli-artifacts/*
```

Expected: one `adam_mcp_cli-0.2.2-py3-none-any.whl`, one sdist, and strict Twine validation passes.

- [ ] **Step 4: Inspect wheel and sdist contents**

```bash
python -m zipfile -l /tmp/adam-mcp-cli-artifacts/adam_mcp_cli-0.2.2-py3-none-any.whl
tar -tzf /tmp/adam-mcp-cli-artifacts/adam_mcp_cli-0.2.2.tar.gz
```

Expected in both artifacts:

- `adam_mcp_cli/schemas/spec_md_lint.py`
- `adam_mcp_cli/schemas/llm_guide_lint.py`
- `adam_mcp_cli/templates/_base/pyproject.toml.j2`
- `adam_mcp_cli/templates/_base/{{name_snake}}/mcp/server.py.j2`
- README and MIT license metadata

- [ ] **Step 5: Commit metadata and artifact configuration**

```bash
git add cli/README.md cli/LICENSE cli/pyproject.toml
git commit -m "chore: prepare adam-mcp-cli 0.2.2 metadata"
```

---

## Task 6: Add an installed-wheel CI release gate

**Files:**

- Modify: `.github/workflows/ci.yml`
- Test: local shell equivalent of the new job

- [ ] **Step 1: Add a dedicated CLI artifact job**

Append this job to `.github/workflows/ci.yml`:

```yaml
  build-cli:
    name: build + smoke test (adam-mcp-cli)
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
      - run: uv python install 3.12
      - name: Build cli/
        run: uv build --package adam-mcp-cli --out-dir dist-cli
      - name: Validate distributions
        run: uvx --from twine twine check --strict dist-cli/*
      - name: Smoke-test installed wheel
        shell: bash
        run: |
          set -euo pipefail
          wheel=$(find dist-cli -name '*.whl' -print -quit)
          target=$(mktemp -d)/example-mcp
          outside=$(mktemp -d)

          uv run --isolated --no-project --with "$wheel" adam-mcp --help
          uv run --isolated --no-project --with "$wheel" \
            adam-mcp new example-mcp --description "wheel smoke test" --target "$target"
          test -f "$target/example_mcp/mcp/server.py"
          uv run --isolated --no-project --with "$wheel" adam-mcp audit "$target"
          uv run --isolated --no-project --with "$wheel" \
            adam-mcp upgrade "$target" --to 0.3.2 --dry-run

          set +e
          output=$(uv run --isolated --no-project --with "$wheel" \
            adam-mcp audit "$outside" --self-check 2>&1)
          status=$?
          set -e
          test "$status" -eq 1
          grep -F "adam-mcp-sdk checkout" <<<"$output"
          ! grep -F "Traceback" <<<"$output"
      - uses: actions/upload-artifact@v4
        with:
          name: dist-cli
          path: dist-cli/
```

- [ ] **Step 2: Run the complete smoke sequence locally against the built wheel**

Use the exact commands from the job, changing only `dist-cli` to `/tmp/adam-mcp-cli-artifacts`. Expected: help, scaffold, audit, and dry-run upgrade pass; outside self-check exits 1 with its checkout hint and no traceback.

- [ ] **Step 3: Ensure tag triggers include the CLI tag namespace**

The current `tags: ["v*"]` does not match `cli-v0.2.2`. Change it to:

```yaml
    tags: ["v*", "cli-v*"]
```

- [ ] **Step 4: Validate YAML structure and run source checks**

```bash
uv run python -c 'import yaml; yaml.safe_load(open(".github/workflows/ci.yml"))'
uv run ruff check cli/ cli/tests/
uv run ruff format --check cli/ cli/tests/
```

If PyYAML is not in the workspace environment, replace only the first command with:

```bash
uv run --with pyyaml python -c 'import yaml; yaml.safe_load(open(".github/workflows/ci.yml"))'
```

Expected: all commands exit 0.

- [ ] **Step 5: Commit the release gate**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: validate installed CLI artifacts"
```

---

## Task 7: Update release-facing documentation

**Files:**

- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `DIRECTION.md`
- Test: documentation path and version scans

- [ ] **Step 1: Document the published distribution and command name**

Add a short CLI install section to the root `README.md`:

```markdown
### CLI

```bash
uv tool install adam-mcp-cli
adam-mcp --help
```

The PyPI distribution is `adam-mcp-cli`; the installed command is `adam-mcp`.
```

- [ ] **Step 2: Record the 0.2.2 packaging repair**

Add a new topmost `## [adam-mcp-cli 0.2.2] — 2026-07-13` section in
`CHANGELOG.md`, separate from the already-published library 0.3.2 section. Under
`### Fixed`, state that:

- audit schema helpers and scaffolding templates now ship inside the wheel;
- normal installed-wheel commands no longer depend on an SDK checkout;
- `audit --self-check` now returns a structured failure outside the SDK repository;
- CI installs and exercises the built CLI wheel.

Do not alter the `adam-mcp-py` 0.3.2 release notes.

- [ ] **Step 3: Mark CLI PyPI publication readiness in direction tracking**

Update the CLI row to state that 0.2.2 is prepared for first publication, with
installed-wheel validation as its gate. Update the PyPI row and strategic item
to reflect the current split state accurately: `adam-mcp-py` 0.3.2 is published;
`adam-mcp-cli` 0.2.2 remains pending until this plan completes.

- [ ] **Step 4: Scan documentation for stale canonical paths and ambiguous package names**

```bash
rg -n "python/templates/_base|pip install adam-mcp([^_-]|$)|uv tool install adam-mcp([^_-]|$)" \
  README.md HOUSE_STYLE.md CHANGELOG.md DIRECTION.md cli/README.md
```

Expected: no stale template path and no instruction that treats the occupied `adam-mcp` project as the distribution name.

- [ ] **Step 5: Commit documentation**

```bash
git add README.md CHANGELOG.md DIRECTION.md
git commit -m "docs: prepare first CLI publication"
```

---

## Task 8: Run full verification and independent review

**Files:**

- Verify: all changed source, tests, docs, and built artifacts
- Do not modify files unless verification or review finds a concrete defect

- [ ] **Step 1: Run the full repository test matrix locally**

```bash
uv run python -m pytest python/tests/ -q
uv run python -m pytest cli/tests/ -q
uv run python -m pytest claude-pack/tests/ -q
uv run python -m pytest reference-mcp/adam-greet/tests/ -q
```

Expected baseline: 45 library, 30+ CLI, 10 plugin, and 9 reference tests pass; the CLI count increases by the tests added above.

- [ ] **Step 2: Run formatting, lint, and repository self-check**

```bash
uv run ruff check .
uv run ruff format --check .
uv run --project cli adam-mcp audit . --self-check
```

Expected: all exit 0.

- [ ] **Step 3: Rebuild from a clean artifact directory and repeat artifact validation**

```bash
rm -rf /tmp/adam-mcp-cli-release-candidate
uv build --package adam-mcp-cli --out-dir /tmp/adam-mcp-cli-release-candidate
uvx --from twine twine check --strict /tmp/adam-mcp-cli-release-candidate/*
```

Repeat every installed-wheel command from Task 6 against this fresh wheel.

- [ ] **Step 4: Verify the diff is scoped and contains no placeholders**

```bash
git diff main...HEAD --stat
git diff --check main...HEAD
rg -n "TODO|FIXME|PLACEHOLDER|your-name|example\.com" \
  cli/adam_mcp_cli cli/README.md cli/pyproject.toml .github/workflows/ci.yml
git status --short
```

Expected: only intended CLI packaging, tests, CI, and docs changes; no whitespace errors or release placeholders; clean working tree.

- [ ] **Step 5: Request independent review**

Invoke `superpowers:requesting-code-review` against `main...HEAD`. The review must specifically check:

- clean-wheel startup and command behavior;
- absence of repository-relative runtime imports;
- `Traversable` compatibility (including zipped resources);
- sdist and wheel resource completeness;
- structured repository-only self-check behavior;
- publication scope excludes `adam-mcp-py` artifacts.

Address confirmed findings with a red regression test, implementation, and a focused commit before repeating Steps 1–4.

---

## Task 9: Open the PR and verify hosted CI

**Files:**

- No source changes expected

- [ ] **Step 1: Push the branch and open a pull request**

Use `github:yeet` to confirm the diff, push `agent/cli-wheel-publishing`, and open a PR titled:

```text
fix: make adam-mcp-cli wheel self-contained
```

The PR body must summarize the packaged schemas/templates, repository-only self-check boundary, and installed-wheel CI gate. It must include the exact local test counts and artifact smoke commands.

- [ ] **Step 2: Verify all GitHub Actions checks**

```bash
gh pr checks --watch
```

Expected: the 9-platform source test matrix, Ruff job, `adam-mcp-py` build job, and new `adam-mcp-cli` build/smoke job all pass.

- [ ] **Step 3: Inspect failed checks before changing code**

If any check fails, use `github:gh-fix-ci` and `superpowers:systematic-debugging`; reproduce the failure locally before editing. Push only verified fixes and wait for the complete matrix again.

- [ ] **Step 4: Merge only after approval and green CI**

Merge the PR using the repository's established merge method. Record the resulting `main` commit hash; that exact commit is the release source.

---

## Task 10: Publish and verify `adam-mcp-cli` 0.2.2

**Files:**

- No source edits
- Publish only artifacts built from the recorded merge commit

- [ ] **Step 1: Verify the public version remains unused immediately before publishing**

```bash
curl -fsS https://pypi.org/pypi/adam-mcp-cli/0.2.2/json
```

Expected before first publication: HTTP 404. If it exists, stop; do not overwrite or silently bump the version.

- [ ] **Step 2: Tag the exact merge commit**

```bash
git switch main
git pull --ff-only
git tag -s cli-v0.2.2 -m "adam-mcp-cli 0.2.2"
git push origin cli-v0.2.2
```

If signed tags are not configured, stop and obtain explicit direction before substituting an unsigned tag.

- [ ] **Step 3: Wait for tag CI and download its CLI artifact**

```bash
run_id=$(gh run list --workflow CI --branch cli-v0.2.2 --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$run_id"
```

Expected: all CI jobs pass. Download the `dist-cli` artifact from this run into a new empty release directory. Do not publish the `dist` artifact from the library build job.

- [ ] **Step 4: Record and validate release hashes**

```bash
shasum -a 256 adam_mcp_cli-0.2.2-py3-none-any.whl adam_mcp_cli-0.2.2.tar.gz
uvx --from twine twine check --strict adam_mcp_cli-0.2.2-*
```

Save both SHA-256 values in the release notes.

- [ ] **Step 5: Publish only the CLI wheel and sdist**

Use the repository's configured PyPI trusted-publishing workflow if present. Otherwise run Twine only after confirming credentials and artifact paths:

```bash
uvx --from twine twine upload \
  adam_mcp_cli-0.2.2-py3-none-any.whl \
  adam_mcp_cli-0.2.2.tar.gz
```

Expected: both CLI artifacts accepted. There must be no `adam_mcp_py-*` file in the upload command or directory glob.

- [ ] **Step 6: Verify public metadata and hashes**

```bash
curl -fsS https://pypi.org/pypi/adam-mcp-cli/0.2.2/json
```

Confirm project name, version, Python requirement, console dependency metadata, and both published SHA-256 digests match Step 4.

- [ ] **Step 7: Verify an index-only installation**

```bash
release_venv=$(mktemp -d)/venv
uv venv "$release_venv"
uv pip install --python "$release_venv/bin/python" \
  --no-cache adam-mcp-cli==0.2.2
"$release_venv/bin/adam-mcp" --help
target=$(mktemp -d)/published-smoke
"$release_venv/bin/adam-mcp" new published-smoke --target "$target"
"$release_venv/bin/adam-mcp" audit "$target"
"$release_venv/bin/adam-mcp" upgrade "$target" --to 0.3.2 --dry-run
```

Expected: installation resolves `adam-mcp-py==0.3.2` from PyPI and all commands pass without the source checkout on `sys.path`.

- [ ] **Step 8: Create the matching GitHub release**

Create a GitHub release for `cli-v0.2.2` with:

- distribution name `adam-mcp-cli` and command name `adam-mcp`;
- PyPI project link;
- wheel and sdist SHA-256 hashes;
- concise install and smoke-test commands;
- note that `audit --self-check` is SDK-checkout-only.

- [ ] **Step 9: Final state verification**

```bash
git status --short --branch
git rev-parse HEAD
git rev-list -n 1 cli-v0.2.2
```

Expected: clean `main`, and `HEAD`, the tag target, GitHub release target, and published artifact source all identify the same merge commit.
