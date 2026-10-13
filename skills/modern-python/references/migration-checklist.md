# Python Tooling Migration Checklist

## Baseline

- Record Python versions, package/backend versions, lockfiles, indexes and CI jobs.
- Run existing checks and preserve known failures separately from new regressions.
- Identify package data, entry points, extras, markers, editable/local dependencies
  and consumers of requirements exports, tox/nox environments or build scripts.
- Use a scoped branch; preserve local changes and a rollback path.

## Package management

- Inspect existing `pyproject.toml`; do not overwrite it with generated defaults.
- Retain a supported build backend unless a backend change is part of the task.
- Map runtime dependencies to `[project].dependencies`, development groups to
  `[dependency-groups]`, and product extras to `[project.optional-dependencies]`.
- Preserve constraints, hashes, private indexes and platform markers deliberately.
  Keep private credentials out of committed configuration.
- Generate and review `uv.lock`; commit it for the uv project. Verify `uv sync --locked`.
- Verify CLI entry points, package data and clean wheel installation.

## Quality tools

- Compare Ruff rules/formatting against the existing configuration before changing
  checks. Review generated fixes; avoid broad unrelated churn.
- Evaluate a replacement type checker against existing errors, plugins and stubs.
  Do not remove annotations, stubs or rules solely to make the new checker pass.
- Preserve test environment matrices; `uv run pytest` alone does not replace every
  tox/nox packaging or compatibility environment.

## Consumers and cleanup

- Migrate development, CI, release and container consumers with the required files
  and package source available at each install/build step.
- Public repositories use GitHub-hosted runners; private repositories use private
  runners with appropriate isolation.
- Execute the required checks from a clean environment, including package install.
- Remove superseded files only after proving no required consumer still needs them.
  Preserve requirements exports when downstream tools require that format.
- Preserve Git history. Record changes, evidence, remaining limits and rollback.
