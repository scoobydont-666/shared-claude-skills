# pyproject.toml reference

Use the project's existing supported build backend. For a new package, `uv init --package` generates a compatible backend configuration; preserve the generated version constraint and confirm current uv documentation before customizing it. This skill does not require migrating a functioning Hatchling/setuptools project merely for style.

Example project/tool sections (merge into the generated configuration):

```toml
[project]
name = "example-package"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[dependency-groups]
dev = ["ruff", "ty", "pytest"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.ty.environment]
python-version = "3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Use `uv add` for runtime dependencies and `uv add --group dev` for development dependencies, then commit the resolved lockfile under project policy. Optional-dependency extras describe optional installed product features; development groups are not published extras.

For an installable package use `src/example_package/` and ensure the build backend discovers it. Verify the wheel contents and installation in a clean environment. A CLI entry under `[project.scripts]` must name an existing callable. Match Python, Ruff and type-checker target versions to the supported interpreter range.

Sources: https://docs.astral.sh/uv/concepts/projects/init/ and https://docs.astral.sh/ty/reference/configuration/ (consult the version used by the project).
