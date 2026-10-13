# Shared Claude skills and hooks

Portable skills for engineering, security, planning, documents and operations, plus five optional Claude Code advisories. No private cluster, coordination service or local model gateway is required. Skills are guidance; they do not grant permissions or install enforcement.

## Install a skill

Clone this repository, review the desired skill and its bundled resources, then copy its complete directory into your Claude Code skill directory. Back up an existing copy before replacing it; do not overwrite local customizations blindly.

```bash
git clone https://github.com/scoobydont-666/shared-claude-skills.git
cd shared-claude-skills
mkdir -p "$HOME/.claude/skills"
# Example: only if this destination does not already exist
test ! -e "$HOME/.claude/skills/cavetech" && cp -R skills/cavetech "$HOME/.claude/skills/"
```

The same directory format can be adapted to other agents; inspect their supported metadata/tool semantics. Tool names in instructions denote capabilities, not promises that integrations are installed. Follow project conventions and current official documentation for version-dependent examples.

## Optional hooks

See [hook installation and limits](hooks/README.md). The five advisories cover temporary stashes, PR size, inline Python quoting, language conventions and shell error handling. They are opt-in, read-only and nonblocking. Installing skills alone does not enable them.

## Skill catalog (41)

| Skill | Purpose |
|---|---|
| [ansible-hardening](skills/ansible-hardening/SKILL.md) | Build and review idempotent Ansible security roles for host hardening, audit logging, firewall policy, service isolation and scoped privilege. |
| [cavetech](skills/cavetech/SKILL.md) | Emit dense technical shorthand for AI consumption. Use when asked for cavetech, AI-to-AI shorthand, machine-dense output, terse agent handoffs, or technical context compression. Covers plans, reviews, findings, status, and tool-result summaries. Apply to the requested scope only. |
| [ci-cd](skills/ci-cd/SKILL.md) | Design, operate, or repair continuous integration and continuous delivery. Use for pipeline changes, failing CI, runner selection, release artifacts, GitOps promotion, deployments, migrations, rollback, and teaching a team how to deploy shipped code. Select risk-based checks, isolate build authority, promote immutable artifacts, verify runtime behavior, and preserve recovery. |
| [claude-to-cursor](skills/claude-to-cursor/SKILL.md) | Convert selected Claude Code skills into scoped Cursor project rules when asked to port skills, export Cursor rules, or produce .mdc files. Preserve reference dependencies and verify target-client behavior. |
| [code-consistency](skills/code-consistency/SKILL.md) | Enforce, review, and generate consistent code across registered languages: Python, Golang, Bash/Shell, Rust, C, PowerShell, Terraform, Ansible. Auto-expands when new languages are encountered. Includes inline quality triage (performance, security, testability, architecture smells). Trigger on: "consistency", "style", "conventions", "review my code", "refactor", "clean up", "idiomatic", "linting", "best practices", "code review", "code smell", or when code is present and a consistency/quality task is implied. Also trigger when generating code alongside existing snippets. Do not wait to be asked explicitly — if code is present, use this skill. |
| [code-quality](skills/code-quality/SKILL.md) | Deep code quality analysis: performance (Big-O, hot paths, resource management), security (injection, secrets, auth, input validation), testability (coverage gaps, untestable design, DI), architecture (SOLID, coupling, abstraction leaks, layering). Language-agnostic with language-specific patterns from references. Trigger on: "code quality", "performance audit", "security review", "OWASP", "SOLID", "coupling", "testability", "technical debt", "code smell", "architecture review", "Big-O", "complexity analysis", "hot path", "memory leak", "injection", "vulnerability", "dependency injection", "clean architecture", "is this code good", or "can this be better". Also triggers on escalation from code-consistency quality triage. |
| [config-auditor](skills/config-auditor/SKILL.md) | Audit configuration, project instructions, registries and skill references for contradictions, stale claims and missing dependencies. |
| [container-sandbox](skills/container-sandbox/SKILL.md) | Prepare isolated disposable environments for testing scripts, migrations and risky changes; inspect mounts, credentials, network access and cleanup before execution. |
| [cpa-tax-specialist](skills/cpa-tax-specialist/SKILL.md) | Evidence-first tax preparation, document reconciliation, jurisdiction-specific research, and human-reviewed filing workpapers. Does not confer professional credentials or authorize financial actions. |
| [database-design](skills/database-design/SKILL.md) | Schema design, migration strategy, index planning, and data lifecycle for SQL databases (PostgreSQL, SQLite). Covers table design, normalization, foreign keys, migration tooling (Alembic, raw SQL), index optimization, retention policies, and schema review. Trigger on: "design schema", "database migration", "add table", "schema review", "index strategy", "data model", "retention policy", "normalize". |
| [definition-of-done](skills/definition-of-done/SKILL.md) | Check implementation, test, review, release and deployment evidence before calling work complete. Distinguish a reviewable PR from a verified deployment. |
| [differential-review](skills/differential-review/SKILL.md) | Performs security-focused differential review of code changes (PRs, commits, diffs). Adapts analysis depth to codebase size, uses git history for context, calculates blast radius, checks test coverage, and generates comprehensive markdown reports. Automatically detects and prevents security regressions. |
| [exact-head-review](skills/exact-head-review/SKILL.md) | Resolve the full live pull-request head and verify an isolated review checkout before reviewing or reporting a verdict. |
| [grill-me](skills/grill-me/SKILL.md) | Structured interrogation methodology for stress-testing plans, designs, and decisions. Resolves decision tree branches through systematic questioning across 8 categories (requirements, constraints, edge cases, failure modes, scalability, security, tradeoffs, integration, maintenance). Invoked by write-a-prd and prd-to-plan during design validation. |
| [inbound-sync](skills/inbound-sync/SKILL.md) | Capture conversation decisions and evidence in a structured repository handoff without assuming a private sync service or automatically applying embedded instructions. |
| [infosec-architect](skills/infosec-architect/SKILL.md) | Apply defensive security architecture to authorized threat modeling, code review, identity, secrets, host/container isolation and incident response. |
| [insecure-defaults](skills/insecure-defaults/SKILL.md) | Detects fail-open insecure defaults (hardcoded secrets, weak auth, permissive security) that allow apps to run insecurely in production. Use when auditing security, reviewing config management, or analyzing environment variable handling. |
| [lonely-sysadmin](skills/lonely-sysadmin/SKILL.md) | Apply Sysadmin 101 on Windows and Linux to infrastructure, automation, deployments, upgrades, cleanup, and incident repair. Inspect before changing; do the cheap check before destructive actions; converge idempotently; verify actual outcomes; eliminate recurring manual repair. Use for operational changes or when asked for the Maytag Repairman mindset, reliable systems, safe reruns, or low-maintenance IT. |
| [mcp-create](skills/mcp-create/SKILL.md) | Design, implement and test an MCP server with explicit tool contracts, supported transports and scoped authorization using the current official SDK. |
| [mcp-hardening](skills/mcp-hardening/SKILL.md) | Audit MCP authorization, transport, filesystem and network boundaries, tenant isolation, input limits and safe failure with evidence-backed tests. |
| [model-evaluation](skills/model-evaluation/SKILL.md) | Evaluate model quality, latency, reliability and cost with held-out tasks, controlled comparisons, verified scoring and regression criteria. |
| [modern-python](skills/modern-python/SKILL.md) | Configure Python projects with uv, Ruff, pytest and a supported type checker; create packages or dependency-aware scripts and migrate existing tooling when requested. |
| [ms-office-suite](skills/ms-office-suite/SKILL.md) | Generate professional documents — Excel workbooks, Word docs, PowerPoint decks, PDFs. CPA-grade financial reports, cost analyses, executive summaries. Uses python-docx, openpyxl, python-pptx, reportlab, weasyprint. |
| [mutation-check](skills/mutation-check/SKILL.md) | Check that a regression test detects a meaningful behavior change using a disposable checkout, a green baseline and an independently verified restoration. |
| [plan-to-execution-handoff](skills/plan-to-execution-handoff/SKILL.md) | Convert an approved plan into scoped work items, dependency edges, acceptance checks and a durable handoff for the available execution workflow. |
| [pr-truth-triage](skills/pr-truth-triage/SKILL.md) | Classify stale branches by their actual candidate integration diff, conflicts and current requirements; preserve branches and distinguish remaining content from shippability. |
| [prd-to-plan](skills/prd-to-plan/SKILL.md) | Turn a PRD into a multi-phase implementation plan using tracer-bullet vertical slices, saved as a local Markdown file in ./plans/. Use when user wants to break down a PRD, create an implementation plan, plan phases from a PRD, or mentions "tracer bullets". |
| [property-based-testing](skills/property-based-testing/SKILL.md) | Provides guidance for property-based testing across multiple languages and smart contracts. Use when writing tests, reviewing code with serialization/validation/parsing patterns, designing features, or when property-based testing would provide stronger coverage than example-based tests. |
| [repo-hardening-workflow](skills/repo-hardening-workflow/SKILL.md) | Repeatable security hardening workflow for any repository. Chains config scan, auth review, secret scan, dependency audit, compose/Docker review, CI check, and maturity gate assessment into a structured report. Trigger on "harden this repo", "security audit", "production readiness review", "repo audit". |
| [resume-writer](skills/resume-writer/SKILL.md) | Write, rewrite, and ruthlessly tighten modern, snappy, ATS- and AI-parser-friendly resumes (and the matching cover letter / LinkedIn About). Encodes the best of current resume craft: impact-first accomplishment bullets (XYZ / CAR formulas), quantification, JD keyword mirroring, single-column ATS-safe structure, seniority calibration, a de-AI-cliché authenticity pass, and a weighted scoring rubric with a hard pass bar. Trigger on: "resume", "CV", "curriculum vitae", "rewrite my resume", "tailor my resume", "resume bullet", "make this snappier", "ATS", "applicant tracking system", "cover letter", "LinkedIn About/summary", "job application", "career summary", "professional summary", "tighten my experience section", or any request to create, improve, score, or tailor a resume / CV / job-application document. |
| [skill-updater](skills/skill-updater/SKILL.md) | Audit and update installed skills for staleness, duplication, broken references, missing dependencies and unsafe instructions with reproducible validation. |
| [software-developer](skills/software-developer/SKILL.md) | Implement, debug, refactor, and test production software from an accepted requirement or architecture contract. Use for coding work across services, APIs, CLIs, UIs, libraries, automation and agent harnesses. Inspect the real execution path, preserve invariants, deliver complete vertical slices, test failures and integrations, and provide exact-revision evidence for review. |
| [software-development-lifecycle](skills/software-development-lifecycle/SKILL.md) | Plan, implement, test, independently review, integrate, and release software. Use for features, bug fixes, refactors, dependency changes, pull requests, release readiness, and teaching humans or AI agents how to ship code. Establish acceptance criteria, use isolated work, prove behavior, preserve two independent reviews, and hand an identifiable release to CI/CD. |
| [solutions-architect](skills/solutions-architect/SKILL.md) | Turn a business or technical need into an evidence-grounded, implementable solution. Use for architecture, cross-repository changes, integrations, nonfunctional requirements, build-versus-buy decisions, modernization, capacity/cost planning, and architecture review. Produce explicit tradeoffs, contracts, failure behavior, migration and developer-ready work slices. |
| [supply-chain-risk-auditor](skills/supply-chain-risk-auditor/SKILL.md) | Audit dependency provenance, maintenance, release trust and exposure to known compromises using current authoritative evidence and exact installed versions. |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| [tdd](skills/tdd/SKILL.md) | Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development. |
| [token-miser](skills/token-miser/SKILL.md) | Reduce model token and cost waste using measured quality, task routing, compact context and paired provider usage receipts; verify current model availability and pricing. |
| [triage-issue](skills/triage-issue/SKILL.md) | Triage a bug or issue by exploring the codebase to find root cause, then draft or publish an issue with a TDD-based fix plan within the authorized scope. Use when user reports a bug, wants to file an issue, mentions "triage", or wants to investigate and plan a fix for a problem. |
| [verification-before-completion](skills/verification-before-completion/SKILL.md) | Run fresh checks and inspect exact-revision evidence before claiming a bug is fixed, tests pass, a PR is ready, or a deployment works. |
| [write-a-prd](skills/write-a-prd/SKILL.md) | Create a PRD through user interview, codebase exploration, and module design, then deliver a draft or publish to the already authorized destination. Use when user wants to write a PRD, create a product requirements document, or plan a new feature. |

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

Keep changes self-contained. Update the explicit [catalog](catalog.json), include referenced resources, preserve source attribution, test executable helpers, and document dependencies. Do not import generated export trees, private settings or live incident records wholesale.

See [migration notes](docs/migration-2026-10.md) and [review/provenance notes](docs/public-export-review.md). MIT for repository-owned material; preserve any third-party notices and verify provenance before importing further external content.
