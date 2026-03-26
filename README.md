# shared-claude-skills

A collection of original [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for developer productivity, infrastructure ops, security, and cost optimization.

These are **Claude Code skills** (SKILL.md files in `~/.claude/skills/`), not Cursor rules. If you want Cursor-compatible `.mdc` files, see the [claude-to-cursor](#claude-to-cursor) skill included here for conversion guidance.

## Skills (23)

### Code Quality & Review
| Skill | Description |
|-------|-------------|
| [code-consistency](skills/code-consistency/) | Language-specific style enforcement for Python, Go, Bash, Rust, PowerShell, Terraform, Ansible. 7 reference files with idiomatic patterns. |
| [code-quality](skills/code-quality/) | Deep analysis: performance (Big-O, hot paths), security (injection, secrets), testability (coverage gaps, DI), architecture (SOLID, coupling). Rust-specific patterns across all 4 domains. |
| [differential-review](skills/differential-review/) | Security-focused PR/commit review. Blast radius calculation, test coverage checks, adversarial pattern detection. Markdown report output. |
| [insecure-defaults](skills/insecure-defaults/) | Detect fail-open security patterns — hardcoded secrets, weak auth, permissive configs that let apps run insecurely in production. |
| [supply-chain-risk-auditor](skills/supply-chain-risk-auditor/) | Identify dependencies at heightened risk of exploitation or takeover. Evaluates dependency health and supply chain attack surface. |

### Development Methodology
| Skill | Description |
|-------|-------------|
| [tdd](skills/tdd/) | Test-driven development with red-green-refactor loop. Rust/TypeScript examples for mocking, interface design, and deep modules. |
| [systematic-debugging](skills/systematic-debugging/) | Structured debugging before proposing fixes. Root cause analysis, hypothesis testing, evidence gathering. Prevents shotgun fixes. |
| [property-based-testing](skills/property-based-testing/) | Property-based testing guidance across Python, JS/TS, Go, Rust, and smart contracts. When to use PBT vs example-based tests. |

### Infrastructure & Ops
| Skill | Description |
|-------|-------------|
| [ansible-hardening](skills/ansible-hardening/) | Security hardening blueprints for Ansible roles — CrowdSec, fail2ban, auditd, Tailscale, Semaphore, scoped sudoers. |
| [fleet-manager](skills/fleet-manager/) | Multi-machine fleet operations via SSH, rsync, and Ansible. Health checks, cross-host syncing, inventory management. |
| [infosec-architect](skills/infosec-architect/) | CISSP/GSE-depth security architecture — threat modeling, container hardening, network segmentation, incident response, NIST/CIS frameworks. |
| [openclaw-ops](skills/openclaw-ops/) | OpenClaw/NemoClaw secure deployment — sandbox management, Tailscale integration, inference config, security hardening. |

### Cost & Session Management
| Skill | Description |
|-------|-------------|
| [token-miser](skills/token-miser/) | Subagent model routing and API cost optimization. Routes Claude Code subagents to the cheapest capable model. Pricing reference data included. |
| [session-miser](skills/session-miser/) | Intelligent model routing for Claude Code sessions. Recommends Opus/Sonnet/Haiku based on task complexity. Delegates mechanical work to cheaper subagents. |
| [cost-optimizer](skills/cost-optimizer/) | Unified cost awareness — API model routing, infrastructure electricity costs, mining profitability, cloud hosting budgets. |
| [budi-analytics](skills/budi-analytics/) | Reference for [budi](https://github.com/jwalsh/budi) (WakaTime for Claude Code) — CLI commands, architecture, cost model. |

### Coordination & Workflow
| Skill | Description |
|-------|-------------|
| [claude-swarm](skills/claude-swarm/) | Multi-instance Claude Code coordination via NFS + git. Task queuing, worktree isolation, session summaries, context handoff. |
| [claude-to-cursor](skills/claude-to-cursor/) | Convert Claude Code skills to Cursor-compatible `.mdc` rule files. Classification logic for what converts well. |
| [inbound-sync](skills/inbound-sync/) | Structured sync bundles for capturing decisions from claude.ai conversations and ingesting into local projects. |
| [skill-updater](skills/skill-updater/) | Meta-skill that audits installed skills for staleness, gaps, overlaps. Cross-references CLAUDE.md and memory files for contradictions. |
| [project-management](skills/project-management/) | Autonomous work execution loop. Priority framework, session protocol, work queue management, fleet resource routing. |
| [config-auditor](skills/config-auditor/) | Cross-reference config files for contradictions, stale data, and inconsistencies across projects. |

### Domain-Specific
| Skill | Description |
|-------|-------------|
| [cpa-tax-specialist](skills/cpa-tax-specialist/) | 50-year CPA veteran persona for tax advisory — federal/state, individual/business, compliance, planning, exam prep. |

## Installation

### Single skill

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

### All skills

```bash
for skill in skills/*/; do
  cp -r "$skill" ~/.claude/skills/
done
```

### Stay updated

```bash
git clone https://github.com/scoobydont-666/shared-claude-skills.git ~/shared-claude-skills
# Then periodically:
cd ~/shared-claude-skills && git pull
for skill in skills/*/; do cp -r "$skill" ~/.claude/skills/; done
```

## Skill Anatomy

Each skill is a directory containing:
- `SKILL.md` — The skill definition (YAML frontmatter + markdown body)
- `references/` — Optional reference data files loaded on demand

The YAML frontmatter includes `name`, `description`, and `triggers` (keywords that activate the skill).

## Contributing

PRs welcome. Each skill should:
1. Have a clear, specific trigger description
2. Be self-contained (no external dependencies beyond standard tools)
3. Include reference files for domain-specific data
4. Not contain personal information, IP addresses, or project-specific paths

## License

MIT
