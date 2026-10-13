# Python Security Checks

Select dependency scanning, source analysis, secret scanning and workflow review
based on the actual project. No combination of scanners covers the entire security
surface. Install development tools through the project's dependency groups and
commit the resolved lockfile.

## Dependency audit

```bash
uv add --group dev pip-audit
uv run --locked pip-audit --format json --output pip-audit.json
```

This audits the selected environment, which may include development tools. To
check a production dependency set, export the relevant locked groups to a
requirements file and audit that file with `pip-audit -r PATH`. Confirm handling of
private indexes and local packages. `--no-deps` skips dependency resolution; it
does not exclude development dependencies. Do not label a network/authentication
failure or an unsupported dependency as a clean audit.

Automated fixes can change installed packages or a requirements file. Apply them
only in a disposable environment, review the resulting dependency changes, and
update the project's actual manifest/lockfile through its package manager. Any
suppression needs a specific advisory, justification, owner and review date.

Reference: https://github.com/pypa/pip-audit.

## Source analysis

```bash
uv add --group dev 'bandit[toml]'
uv run --locked bandit -r src/ -f json -o bandit.json
```

Adapt the source directory to the project. If configuration is in `pyproject.toml`,
pass `-c pyproject.toml` as required by Bandit. A broad skip list can hide production
issues. Review each finding in context and use the tool's documented targeted
suppression syntax; Ruff's `noqa` codes are not Bandit's `nosec` syntax.

Reference: https://bandit.readthedocs.io/en/latest/config.html.

## CI integration

Use GitHub-hosted runners for public repositories and approved private runners for
private repositories. Keep permissions minimal and pin actions to verified full
commit SHAs. Install reviewed tool versions; execute each required scanner as its
own failing step so an earlier error is not hidden by a later command's success.
Publish redacted reports after failure where useful, but retain the failed status.
Never place secret values in reports or upload private source to public artifacts.

Local hooks can give early feedback. CI must still run the required checks even
when local hooks were absent. Verify that the pipeline detects a known fixture
finding and that an unavailable scanner cannot report success.
