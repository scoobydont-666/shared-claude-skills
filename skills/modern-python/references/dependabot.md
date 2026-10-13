# Dependabot Configuration

Select the ecosystem for the actual manifest and lockfile. GitHub currently has
an explicit `uv` ecosystem for uv projects; `pip` remains appropriate for its
supported pip/Poetry files. Check GitHub's current support matrix and the repository's
hosting version before using this example.

```yaml
version: 2
updates:
  - package-ecosystem: uv
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

For monorepos, configure the directories containing independently maintained
manifests. Add reviewers or assignees only after resolving actual repository
members; this template does not nominate a personal account. Keep registry
credentials in supported secret storage, never in the configuration file.

Version-update scheduling and security updates are separate controls. Enable and
verify security alerts/updates through the repository's supported settings. A daily
version-update schedule is not a security-only configuration. Use explicit,
reviewed exclusions sparingly; ignoring all patch updates can suppress needed fixes.

Update PRs still require meaningful tests and the project's review policy. Do not
infer trust from a bot name or automatically merge a minor version solely from its
version number. Configure auto-merge only under an already approved policy with
required branch checks/reviews. Avoid giving PR-controlled code a write token.

Validation workflows use GitHub-hosted runners for public repositories and approved
private runners for private repositories. Inspect Dependabot job logs and actual
manifest/lockfile diffs to prove that updates work; the presence of a config file
or an empty PR list is not evidence of successful update processing.

Official references (checked 2026-10-13):
- https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories
- https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference
