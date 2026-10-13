# PEP 723 — Inline Script Metadata

PEP 723 lets standalone Python scripts declare their own dependencies inline. uv reads this metadata and runs the script in an isolated environment without any manual setup.

## Metadata Block Format

The metadata block must appear at the top of the file (after the shebang if present) and uses TOML syntax inside a `# /// script` block.

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "httpx>=0.27.0",
#   "rich>=13.0.0",
#   "click>=8.1.0",
# ]
# ///

import httpx
import click
from rich.console import Console

console = Console()

@click.command()
@click.argument("url")
def fetch(url: str) -> None:
    """Fetch a URL and print the response."""
    response = httpx.get(url, follow_redirects=True)
    console.print(f"[green]Status:[/green] {response.status_code}")
    console.print(response.text[:500])

if __name__ == "__main__":
    fetch()
```

## Running with uv

```bash
# Run directly — uv auto-installs deps into a temp venv
uv run fetch.py https://example.com

# Run a remote script (URL)
uv run https://example.com/my_script.py

# Run with extra args passed through to the script
uv run fetch.py --help

# Make the script directly executable (requires shebang)
chmod +x fetch.py
./fetch.py https://example.com

# Force reinstall of cached deps
uv run --reinstall fetch.py https://example.com

# Run with a specific Python version
uv run --python 3.13 fetch.py https://example.com
```

## Complete Example — Database Audit Script

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "sqlalchemy>=2.0.0",
#   "aiosqlite>=0.20.0",
#   "rich>=13.0.0",
# ]
# ///
"""Standalone DB audit script — no venv setup required."""

import asyncio
from pathlib import Path
from rich.table import Table
from rich.console import Console
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DB_PATH = Path.home() / "data" / "audit.db"
console = Console()


async def main() -> None:
    engine = create_async_engine(f"sqlite+aiosqlite:///{DB_PATH}")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = result.fetchall()

    table = Table(title="Tables in audit.db")
    table.add_column("Table Name")
    for row in tables:
        table.add_row(row[0])

    console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
```

## Key Rules

1. The `# /// script` block must start at the beginning of a line — no leading spaces.
2. All dependency lines must be commented with `#` and one space.
3. The closing `# ///` must be on its own line.
4. `requires-python` is optional but recommended — ensures correct interpreter.
5. Dependencies use standard PEP 508 requirement specifiers.
6. uv caches the venv per script — subsequent runs are fast.

## When to Use PEP 723

- One-off data migration or audit scripts
- Cron jobs that need isolated dependencies
- Scripts you share with others (self-contained, no setup docs needed)
- Admin/ops scripts that live outside any project

## When NOT to Use PEP 723

- Production services (use a full project with pyproject.toml)
- Scripts with many dependencies (>10) — just make it a project
- Scripts that need editable installs of local packages
