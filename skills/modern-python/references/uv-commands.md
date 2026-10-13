# uv Command Reference

uv is a fast Python package and project manager written in Rust. Replaces pip, pip-tools, virtualenv, and Poetry.

## Project Initialization

```bash
# Create a project; inspect generated files for the selected project type
uv init my-project
uv init my-project --lib          # library with a generated supported backend
uv init my-project --app          # application (no build system)
uv init my-project --script       # single-file script

# Init in current directory
uv init
```

## Managing Dependencies

```bash
# Add runtime dependency
uv add fastapi
uv add "fastapi>=0.115.0"
uv add "pydantic[email]"

# Add dev dependencies (goes to [dependency-groups].dev)
uv add --dev pytest ruff ty
uv add --dev "pytest-asyncio>=0.24.0"

# Add to a named optional group
uv add --optional docs sphinx

# Remove a dependency
uv remove fastapi
uv remove --dev ruff

# Upgrade a dependency
uv add "fastapi>=0.116.0"        # updates pyproject.toml + uv.lock
```

## Syncing and Installing

```bash
# Install all dependencies from uv.lock
uv sync

# Include dev dependencies
uv sync --dev
uv sync --extra feature          # optional product extra, not a dev group

# Install without dev deps (production)
uv sync --no-dev

# Install a specific group
uv sync --group docs

# Reinstall everything from scratch
uv sync --reinstall
```

## Running Commands

```bash
# Run a command in the project venv
uv run python main.py
uv run pytest
uv run ruff check .

# Run a specific Python version
uv run --python 3.12 python script.py

# Run a standalone script (PEP 723)
uv run script.py

# Run without syncing first (faster if already synced)
uv run --no-sync pytest
```

## Virtual Environments

```bash
# Create a venv (usually done automatically by uv init/sync)
uv venv
uv venv .venv                    # explicit path
uv venv --python 3.12            # specific Python version

# Activate (standard venv activation still works)
source .venv/bin/activate
```

## Lock File Management

```bash
# Generate/update uv.lock without installing
uv lock

# Update all dependencies to latest compatible versions
uv lock --upgrade

# Upgrade a specific package
uv lock --upgrade-package fastapi

# Check if lock file is up to date
uv lock --check
```

## Dependency Tree

```bash
# Show full dependency tree
uv tree

# Show why a package is installed
uv tree --package httpx

# Show outdated packages
uv tree --outdated
```

## pip Compatibility

```bash
# Install from requirements.txt (not recommended for new projects)
uv pip install -r requirements.txt

# Install a package directly (into active venv)
uv pip install httpx

# Show installed packages
uv pip list
uv pip show fastapi

# Generate requirements.txt from lock file
uv pip compile pyproject.toml -o requirements.txt
uv export --format requirements-txt > requirements.txt
```

## Python Version Management

```bash
# List available Python versions
uv python list

# Install a Python version
uv python install 3.12
uv python install 3.13

# Pin Python version for project
uv python pin 3.12               # writes .python-version
```

## Common Flags

| Flag | Meaning |
|------|---------|
| `--locked` | Fail if the lockfile is missing or needs updating |
| `--frozen` | Use the lockfile without checking freshness |
| `--no-cache` | Bypass the cache |
| `--quiet` / `-q` | Suppress output |
| `--verbose` / `-v` | More output |
| `--python 3.12` | Use specific Python version |
| `--directory /path` | Run in a different project directory |

## .gitignore Entries for uv Projects

```
.venv/
__pycache__/
*.pyc
.python-version      # commit if you want to pin for the whole team
# Keep uv.lock tracked for reproducible project environments.
```

Commit `uv.lock` for uv project development, including libraries. A library's
lockfile makes its development environment reproducible; it does not pin the
dependencies selected by downstream package installers.
