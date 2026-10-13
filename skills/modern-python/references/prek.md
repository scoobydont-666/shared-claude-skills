# Local Checks with pre-commit or prek

Preserve the runner already used by the project. pre-commit and prek can use
`.pre-commit-config.yaml`; inspect the installed version's supported features
before migrating. Do not assume every configuration or hook environment is
interchangeable. Official references: https://pre-commit.com/ and
https://prek.j178.dev/configuration/.

A project using uv can define local checks against its locked development tools:

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff lint
        entry: uv run --locked ruff check
        language: system
        types: [python]
      - id: ruff-format
        name: Ruff format check
        entry: uv run --locked ruff format --check
        language: system
        types: [python]
      - id: pytest-unit
        name: Fast unit tests
        entry: uv run --locked pytest tests/unit/ -q
        language: system
        pass_filenames: false
        always_run: true
```

The fixture assumes Ruff and pytest are installed in the development group and
that `tests/unit/` exists. Adapt it to the real repository; empty or wrong test
selection is not a passing check. Add type checking using the actual configured
checker. Keep slow integration checks in the appropriate CI lane.

For external hook repositories, pin a reviewed revision and inspect updates
before accepting them. Install the hook using the chosen tool's documented
`install` command and run it against the complete candidate once. Do not install
both runners over the same Git hook without understanding their interaction.
Local hooks supplement required CI; a missing local hook cannot waive validation.

If a hook modifies files, inspect the diff and rerun checks before committing.
Report genuine tool failures; do not make disabling hooks the normal recovery path.
