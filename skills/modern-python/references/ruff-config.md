# Ruff Configuration Reference

Ruff is a fast Python linter and formatter written in Rust. Replaces flake8, isort, pyupgrade, black, and dozens of plugins.

## pyproject.toml Configuration

```toml
[tool.ruff]
line-length = 120
target-version = "py312"
# Exclude common non-source directories
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "migrations",
]

[tool.ruff.lint]
# Rule sets to enable
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes (undefined names, unused imports)
    "I",    # isort (import ordering)
    "UP",   # pyupgrade (modernize syntax for target Python version)
    "B",    # flake8-bugbear (likely bugs and design problems)
    "SIM",  # flake8-simplify (suggest simpler code)
]
# Rules to ignore globally
ignore = [
    "E501",   # line too long (handled by formatter, not linter)
    "B008",   # do not perform function calls in default arguments (FastAPI uses this)
    "SIM108", # use ternary operator (sometimes less readable)
]
# Allow autofix for all enabled rules
fixable = ["ALL"]
unfixable = []

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",   # use of assert (fine in tests)
    "ARG001", # unused function argument (fixtures often unused)
    "ARG002", # unused method argument
]
"**/__init__.py" = [
    "F401",   # imported but unused (re-exports are common here)
]
"scripts/**/*.py" = [
    "T201",   # print found (scripts can use print)
]

[tool.ruff.lint.isort]
known-first-party = ["my_service"]
force-single-line = false
split-on-trailing-comma = true

[tool.ruff.format]
# These settings mirror black's defaults
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

## CLI Commands

```bash
# Check for lint errors (no changes)
ruff check .
ruff check src/ tests/

# Auto-fix fixable issues
ruff check --fix .
ruff check --fix --unsafe-fixes .   # also apply unsafe fixes (review carefully)

# Format code (replaces black)
ruff format .
ruff format src/ tests/

# Check formatting without changing files
ruff format --check .

# Show what would be fixed
ruff check --diff .

# Run on a single file
ruff check src/my_service/main.py
ruff format src/my_service/main.py

# Show all available rules
ruff rule --all

# Explain a specific rule
ruff rule E501
ruff rule B008
```

## Common Rule Sets

| Code | Tool Replaced | Description |
|------|--------------|-------------|
| E, W | pycodestyle  | PEP 8 style violations |
| F    | pyflakes     | Logic errors, unused imports |
| I    | isort        | Import sorting |
| UP   | pyupgrade    | Python version modernization |
| B    | flake8-bugbear | Likely bugs |
| SIM  | flake8-simplify | Code simplification |
| S    | bandit       | Security issues (optional, use bandit separately) |
| T20  | flake8-print | Print statement detection |
| ANN  | flake8-annotations | Type annotation enforcement |
| ARG  | flake8-unused-arguments | Unused arguments |
| PTH  | flake8-use-pathlib | Use pathlib instead of os.path |
| RUF  | ruff-specific | Ruff's own rules |

## Inline Suppressions

```python
import os  # noqa: F401           — suppress single rule
import sys  # noqa                 — suppress all rules on this line
x = 1+1    # noqa: E226           — suppress spacing rule

# For a block, use type: ignore comment style isn't supported
# Instead use per-file-ignores in config
```

## Pre-commit Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```
