---
name: modern-python
description: Configure Python projects with uv, Ruff, pytest and a supported type checker; create packages or dependency-aware scripts and migrate existing tooling when requested.
---
# Modern Python

Inspect the supported Python versions, existing package manager, build backend,
lockfile, CI and tests first. Preserve functioning project conventions unless a
migration is requested. A different formatter or type checker is not itself a
defect. Background inspiration: https://github.com/trailofbits/cookiecutter-python.

## New project

Use an approved installation of uv and inspect the installed version's help.
For a plain application, `uv init myproject` creates a root `main.py`; for an
installable package, use `uv init --package myproject` and inspect its generated
source layout and build configuration. Do not copy a stale backend version pin.

```bash
uv init myproject
cd myproject
uv add --group dev ruff pytest
uv run python main.py
uv run ruff check .
uv run pytest
```

Add actual runtime dependencies with `uv add`. Choose a type checker compatible
with the project's annotations and integrations; ty is one option, while existing
mypy or Pyright configurations may remain appropriate. Do not remove stubs or
checks simply because a different tool produces fewer findings.

Use `[dependency-groups]` for development tools and `[project.optional-dependencies]`
for optional installed product features. Commit the resolved lockfile for a uv
project. Match Python/tool targets to the supported interpreter range. Configure
Ruff incrementally around existing style, and keep formatting changes separate
when they would obscure a behavior change.

See [pyproject configuration](references/pyproject.md),
[uv commands](references/uv-commands.md), and [Ruff settings](references/ruff-config.md).

## Scripts

For a standalone script with dependencies, consider PEP 723 inline metadata and
`uv run script.py`. Inspect dependencies and source before execution; metadata is
not a trust guarantee. See [script examples](references/pep723-scripts.md).

## Migration

Record baseline tests, supported platforms, entry points, dependency groups and
build artifacts. Work in an isolated branch and keep the old configuration until
the replacement preserves required behavior. Translate constraints, indexes,
extras and environment markers deliberately; do not filter requirement lines
through a loop that hides errors and then delete the source files.

Validate the lockfile with `uv lock --check` or use `uv sync --locked`. The
`--frozen` flag skips the freshness check; it is not a substitute. Test package
build and installation in a clean environment as well as source-tree tests.
Only remove obsolete configuration after all consumers, including CI and release
jobs, have migrated. Preserve history and a practical rollback path.

Follow the [migration checklist](references/migration-checklist.md).

## Tests, security and CI

Use meaningful tests for accepted behavior, error paths and state isolation.
Coverage percentages supplement those checks; they do not establish correctness.
See [pytest examples](references/testing.md) and adapt fixtures to the actual app
and installed plugins, including ASGI lifespan and database transaction behavior.

Choose scanners for the project's threats; distinguish findings from tool/network
failures, and preserve nonzero outcomes. See [security setup](references/security-setup.md).
Run local checks through [pre-commit or prek](references/prek.md) if the repository
uses them. Keep CI as the authoritative execution path for required checks.

Public repositories use GitHub-hosted runners. Private repositories use approved
private runners with isolation suitable for the code's trust level. Pin external
Actions to verified full commit SHAs and use minimal token permissions. Use
[Dependabot configuration](references/dependabot.md) for reviewed dependency updates.

## Verification and handoff

Run the selected formatting, linting, typing, tests, build and installation checks
against the changed revision. Record what executed, what failed or could not run,
and the exact interpreter/tool versions. Never claim migration success when the
lockfile changed unexpectedly, tests were not collected, or a required consumer
still uses the old configuration.
