# CLI Wheel Publishing Design

## Context

`adam-mcp-cli` 0.2.2 builds a wheel, but the wheel is not usable outside the
monorepo. A clean installation fails at process startup with
`ModuleNotFoundError: No module named 'schemas'`. The CLI imports audit schema
modules by adding `spec/` from a repository-relative path to `sys.path`. Its
scaffolder has the same structural defect: it loads templates from the sibling
`python/templates/_base` directory, which is absent from the wheel.

Workspace tests do not catch either defect because they run against the complete
repository. The CLI has not been published to PyPI, so version 0.2.2 can be
repaired before its first publication.

## Goals

- Make `adam-mcp --help`, `new`, normal `audit`, and `upgrade` work from a clean
  `adam-mcp-cli` wheel installation.
- Keep `audit --self-check` repository-only and return a clear structured failure
  outside an SDK checkout.
- Make packaged resources canonical rather than maintaining synchronized copies.
- Add release metadata and artifact-level CI checks before publishing 0.2.2.
- Publish only `adam-mcp-cli`; do not republish or modify `adam-mcp-py` 0.3.2.

## Non-goals

- Making `audit --self-check` independent of the SDK repository.
- Changing audit rules, scaffolded project behavior, or the `Result` contract.
- Publishing the CLI under the already-occupied `adam-mcp` PyPI project name.
- Refactoring unrelated CLI commands.

## Architecture

### Canonical runtime resources

Move the two Python audit-schema modules from `spec/schemas/` into
`cli/adam_mcp_cli/schemas/`. `audit_rules.py` will use package-relative imports
and will no longer mutate `sys.path` or infer a repository root at import time.
The JSON server schema remains under `spec/schemas/` because the CLI does not load
it at runtime.

Move the scaffold tree from `python/templates/_base/` into
`cli/adam_mcp_cli/templates/_base/`. Update the house-style documentation to
point to the new canonical location. There will be one template tree, not a
generated or synchronized duplicate.

`templates_loader.py` will use `importlib.resources.files()` and the
`Traversable` interface. Rendering will recurse through package resources,
substitute path components, render `.j2` text as UTF-8, and copy non-template
bytes. It will not assume resources are ordinary filesystem paths.

### Repository-only self-check

Normal CLI import and command dispatch must not read repository files.
`audit --self-check` will resolve an explicit repository root, defaulting to the
current working directory, and verify its required sentinels before running:

- `HOUSE_STYLE.md`
- `CHANGELOG.md`
- `cli/adam_mcp_cli/audit_rules.py`
- `python/adam_mcp_py/validation.py`

If the sentinels are absent, the command will return a structured `FAIL` report
whose hint says that self-check must be run from the `adam-mcp-sdk` checkout. It
must not raise an import or file-not-found exception. Tests will inject the root
explicitly rather than depending on the module installation path.

### Distribution metadata

Keep the first public CLI version at 0.2.2 because that version has never existed
on PyPI. Add a package-local Markdown README, MIT license inclusion, authors,
classifiers, and project URLs. Explicit Hatch configuration will include the
schema package and template resource tree in both wheel and sdist.

The console command remains `adam-mcp`; the distribution name remains
`adam-mcp-cli`.

## Data flow

For `adam-mcp new`, command arguments become a render context, the loader walks
the packaged template tree, and rendered files are written to the requested
target. For normal `audit`, packaged schema functions and audit rules inspect the
target project without consulting the SDK checkout. For `upgrade`, the CLI reads
the target project's dependency, resolves `adam-mcp-py` from PyPI, and preserves
the existing dry-run and downgrade protections.

`audit --self-check` is the only repository-coupled path. It validates the
checkout boundary before reading internal specification or source files.

## Error handling

- Missing packaged templates are a release invariant violation and produce a
  concise runtime error naming the missing resource.
- Invalid template variables continue to fail through Jinja `StrictUndefined`.
- Missing self-check repository files return a structured `FAIL` result.
- Existing scaffold, audit, and upgrade error envelopes remain unchanged.

## Testing

Development follows a red-green cycle beginning with a test that builds and
installs the current wheel and reproduces the startup failure. Focused tests will
then cover package-relative schema imports, resource traversal and rendering,
complete scaffold output, normal audit behavior, and the repository-only
self-check diagnostic.

CI will build `adam-mcp-cli` into a clean directory, run strict `twine check`,
install the wheel in an isolated environment, and execute:

- `adam-mcp --help`
- `adam-mcp new` followed by layout assertions
- normal `adam-mcp audit` on the generated project
- `adam-mcp upgrade --dry-run`
- `adam-mcp audit --self-check` outside the repository, asserting the documented
  failure instead of a traceback

The existing macOS, Linux, and Windows source-test matrix remains in place.

## Release

After tests, artifact checks, independent review, and PR CI pass, merge the CLI
fix, tag the source as `cli-v0.2.2`, build wheel and sdist from that commit in a
clean directory, and publish only those artifacts to PyPI. Verify public JSON
metadata, hashes, and an index-only installation before creating the matching
GitHub release.
