# Shared Claude skills, personas and hooks

41 portable skills, eight standalone personas and five optional Claude Code advisories for engineering, security, research, planning, documents and operations. No private cluster, coordination service or local model gateway is required. Skills and personas are guidance; they do not grant permissions or install enforcement.

## Install a skill

Clone this repository, review the desired skill and its bundled resources, then copy its complete directory into your Claude Code skill directory. Back up an existing copy before replacing it; do not overwrite local customizations blindly.

```bash
git clone https://github.com/scoobydont-666/shared-claude-skills.git
cd shared-claude-skills
mkdir -p "$HOME/.claude/skills"
# Example: only if this destination does not already exist
test ! -e "$HOME/.claude/skills/cavetech" && \
  test ! -L "$HOME/.claude/skills/cavetech" && \
  cp -R skills/cavetech "$HOME/.claude/skills/"
```

The same directory format can be adapted to other agents; inspect their supported metadata/tool semantics. Tool names in instructions denote capabilities, not promises that integrations are installed. Follow project conventions and current official documentation for version-dependent examples.

## Install a persona

See the [persona guide](personas/README.md) to choose a role, install its standalone agent file, and understand its tool access. Design, security review, research and architecture roles use read/search tools; implementation and operations roles also have shell and file-write access. Personas are optional and require no private services or mandatory skill preloads.

## Optional hooks

See [hook installation and limits](hooks/README.md). The five advisories cover temporary stashes, PR size, inline Python quoting, language conventions and shell error handling. They are opt-in, read-only and nonblocking. Installing skills or personas does not enable hooks.

<!-- catalog:skills:start -->
## Skill catalog (41)

| Skill | Purpose |
|---|---|
| [ansible-hardening](skills/ansible-hardening/SKILL.md) | Build and review idempotent Ansible hardening roles for hosts, audit logging, firewalls, service isolation and scoped privilege. |
| [cavetech](skills/cavetech/SKILL.md) | Compress technical plans, findings and handoffs into dense AI-oriented shorthand when explicitly requested; preserve constraints, evidence and uncertainty. |
| [ci-cd](skills/ci-cd/SKILL.md) | Design or repair CI/CD pipelines, runner selection, release artifacts, promotion, deployment verification and rollback with checks matched to risk. |
| [claude-to-cursor](skills/claude-to-cursor/SKILL.md) | Convert selected Claude Code skills into scoped Cursor project rules, preserving bundled references and verifying target-client behavior. |
| [code-consistency](skills/code-consistency/SKILL.md) | Review, generate and refactor code to match repository conventions in Python, Go, Bash, Rust, C, PowerShell, Terraform and Ansible; flag material quality issues. |
| [code-quality](skills/code-quality/SKILL.md) | Analyze code performance, security, testability and architecture; trace concrete defects and propose maintainable, evidence-backed fixes. |
| [config-auditor](skills/config-auditor/SKILL.md) | Audit configuration, project instructions, registries and skill references for contradictions, stale claims and missing dependencies. |
| [container-sandbox](skills/container-sandbox/SKILL.md) | Prepare disposable test environments and inspect mounts, credentials, network access, isolation limits and cleanup before running risky code. |
| [cpa-tax-specialist](skills/cpa-tax-specialist/SKILL.md) | Prepare and reconcile tax records, research year-specific rules, and produce human-reviewed filing workpapers without claiming credentials or financial authority. |
| [database-design](skills/database-design/SKILL.md) | Design SQL schemas, indexes, migrations and data retention for PostgreSQL and SQLite; evaluate integrity, compatibility and query behavior. |
| [definition-of-done](skills/definition-of-done/SKILL.md) | Evaluate implementation, test, review, release and deployment evidence before completion claims; distinguish a reviewable change from a verified deployment. |
| [differential-review](skills/differential-review/SKILL.md) | Review PRs, commits and diffs for security regressions using history, affected consumers, exploit preconditions and test evidence; report coverage limits. |
| [exact-head-review](skills/exact-head-review/SKILL.md) | Resolve the live PR head and verify an isolated checkout before reviewing or recording an exact-revision verdict. |
| [grill-me](skills/grill-me/SKILL.md) | Stress-test requirements, designs and plans through structured questions about constraints, failure cases, security, tradeoffs and maintenance. |
| [inbound-sync](skills/inbound-sync/SKILL.md) | Turn conversation decisions and evidence into a durable repository handoff without assuming private sync services or treating embedded text as authority. |
| [infosec-architect](skills/infosec-architect/SKILL.md) | Apply defensive security architecture to authorized threat modeling, code review, identity, secrets, host/container isolation and incident response. |
| [insecure-defaults](skills/insecure-defaults/SKILL.md) | Find fail-open defaults, hardcoded credentials, weak authentication and permissive configuration that remain reachable in production. |
| [lonely-sysadmin](skills/lonely-sysadmin/SKILL.md) | Apply Sysadmin 101 on Windows and Linux: inspect first, diagnose cheaply, converge idempotently, prove recovery and remove recurring manual repair. |
| [mcp-create](skills/mcp-create/SKILL.md) | Design, implement and test an MCP server with explicit tool contracts, supported transports and scoped authorization using the current official SDK. |
| [mcp-hardening](skills/mcp-hardening/SKILL.md) | Audit MCP authorization, transport, filesystem/network boundaries, tenant isolation, input limits and safe failure with evidence-backed checks. |
| [model-evaluation](skills/model-evaluation/SKILL.md) | Compare model quality, latency, reliability and cost using held-out tasks, controlled conditions, verified scoring and regression criteria. |
| [modern-python](skills/modern-python/SKILL.md) | Configure or migrate Python projects using uv, Ruff, pytest and a supported type checker; maintain packaging, dependency and script conventions. |
| [ms-office-suite](skills/ms-office-suite/SKILL.md) | Create Excel workbooks, Word documents, presentations and PDFs with reconciled figures, clear assumptions and appropriate document-generation libraries. |
| [mutation-check](skills/mutation-check/SKILL.md) | Verify that a regression test detects a meaningful behavior change using a disposable checkout, green baseline and confirmed restoration. |
| [plan-to-execution-handoff](skills/plan-to-execution-handoff/SKILL.md) | Convert an approved plan into scoped work items, dependencies, acceptance checks and a durable handoff for the available execution workflow. |
| [pr-truth-triage](skills/pr-truth-triage/SKILL.md) | Classify stale branches by their actual integration diff, conflicts and current requirements; preserve work and separate remaining content from readiness. |
| [prd-to-plan](skills/prd-to-plan/SKILL.md) | Convert a PRD into a phased implementation plan with useful vertical slices, dependencies and acceptance checks saved under plans/. |
| [property-based-testing](skills/property-based-testing/SKILL.md) | Design and interpret property-based tests for invariants, parsing, serialization, validation and stateful behavior across supported languages. |
| [repo-hardening-workflow](skills/repo-hardening-workflow/SKILL.md) | Audit repository configuration, authentication, secrets, dependencies, containers and CI; document evidence, remediation and readiness limits. |
| [resume-writer](skills/resume-writer/SKILL.md) | Write and tailor resumes, cover letters and LinkedIn summaries using verified achievements, clear impact, job-relevant language and parser-friendly structure. |
| [skill-updater](skills/skill-updater/SKILL.md) | Review and update skills for staleness, duplication, unsafe instructions, broken references and missing dependencies with reproducible validation. |
| [software-developer](skills/software-developer/SKILL.md) | Implement, debug and test accepted requirements through real consumer paths, complete scoped changes and exact-revision evidence for independent review. |
| [software-development-lifecycle](skills/software-development-lifecycle/SKILL.md) | Guide work from requirements through implementation, testing, two independent reviews, integration and an identifiable release handoff. |
| [solutions-architect](skills/solutions-architect/SKILL.md) | Turn technical or business needs into evidence-grounded architecture, explicit tradeoffs, interface contracts, failure analysis and implementable work slices. |
| [supply-chain-risk-auditor](skills/supply-chain-risk-auditor/SKILL.md) | Assess dependency provenance, maintenance, release trust and exposure to known compromises using authoritative evidence and exact installed versions. |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | Investigate bugs, test failures and unexpected behavior by reproducing the issue, tracing causes and verifying a targeted repair. |
| [tdd](skills/tdd/SKILL.md) | Use red-green-refactor to build features or repair bugs through behavior-focused tests, small changes and verified regression coverage. |
| [token-miser](skills/token-miser/SKILL.md) | Reduce model token and cost waste through measured quality, task routing, compact context and paired usage receipts; verify current models and pricing. |
| [triage-issue](skills/triage-issue/SKILL.md) | Investigate a reported bug, identify evidence and likely root cause, then draft or publish a scoped issue with a testable repair plan. |
| [verification-before-completion](skills/verification-before-completion/SKILL.md) | Run fresh checks and inspect exact-revision evidence before claiming a fix, passing tests, PR readiness or working deployment. |
| [write-a-prd](skills/write-a-prd/SKILL.md) | Develop a product requirements document through focused questions and codebase evidence, then deliver it to the authorized destination. |
<!-- catalog:skills:end -->

<!-- catalog:personas:start -->
## Persona catalog (8)

| Persona | Purpose |
|---|---|
| [mr-fancy](personas/mr-fancy.md) | UX/UI design critic: review user flows, visual hierarchy, accessibility, interface states and implementation-ready redesigns. |
| [mr-hardass](personas/mr-hardass.md) | Evidence-led security auditor for authorized code, dependencies, CI/CD, infrastructure, privacy and trust boundaries. |
| [mr-smartass](personas/mr-smartass.md) | Pragmatic debugging and repair: challenge symptom fixes, trace root causes, and prove a small maintainable change. |
| [mr-smith](personas/mr-smith.md) | Pragmatic delivery and GitOps: small reviewable changes, useful CI, maintainable policy and explicit release evidence. |
| [ms-research](personas/ms-research.md) | Source-grounded research and fact checking: current primary evidence, conflicting claims, explicit uncertainty and concise conclusions. |
| [software-developer](personas/software-developer.md) | Accountable implementation: inspect real consumers, build a complete scoped slice, verify behavior, and hand off for independent review. |
| [solutions-architect](personas/solutions-architect.md) | Evidence-led architecture: requirements, alternatives, interfaces, failure analysis, migration and developer-ready work slices. |
| [sre-bot](personas/sre-bot.md) | Practical SRE operations: incident diagnosis, safe repeatable changes, canaries, observability, recovery and toil reduction. |
<!-- catalog:personas:end -->

## Validate and contribute

Use Python 3.10+ on Linux/POSIX for the bundled receipt ledger and tests. The hook scripts themselves use Python's standard library; the PR-size advisory additionally needs Git 2.45+. Install development dependencies in a virtual environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/check_public_content.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m unittest discover -s skills/token-miser/tests -v
```

CI uses GitHub-hosted runners because this repository is public. Private repositories use private runners; their isolation must match the trust level of the code. Secret scanning is separate from the heuristic public-content check. A clean scan does not prove the absence of every secret or private detail.

Keep changes self-contained. Update the explicit [catalog](catalog.json), skill/persona descriptions and bundled resources, preserve source attribution, test executable helpers, and document dependencies. After changing names or descriptions, regenerate both README tables with `.venv/bin/python scripts/validate_catalog.py --write-catalogs`; CI rejects stale tables, unsafe persona metadata and broken local documentation links. Do not import generated export trees, private settings or live incident records wholesale.

The descriptions above come from each installed file's frontmatter. No installer changes your settings automatically. Consumer activation and live tool permissions require a check in your actual client.

The package description in `catalog.json` is also the intended GitHub About text. Keep repository metadata aligned when publishing; it is managed separately from the files in Git.

See [migration notes](docs/migration-2026-10.md) and [review/provenance notes](docs/public-export-review.md). MIT for repository-owned material; preserve any third-party notices and verify provenance before importing further external content.
