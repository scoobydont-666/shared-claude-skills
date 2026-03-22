# shared-claude-skills

A collection of original [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for developer productivity, infrastructure ops, and cost optimization.

These are **Claude Code skills** (SKILL.md files in `~/.claude/skills/`), not Cursor rules. If you want Cursor-compatible `.mdc` files, see the [claude-to-cursor](#claude-to-cursor) skill included here for conversion guidance.

## Skills

| Skill | Description |
|-------|-------------|
| [token-miser](skills/token-miser/) | Subagent model routing and API cost optimization. Routes every Claude Code subagent and API call to the cheapest model that can handle it. Includes pricing reference data, routing tables, escalation logic, and pipeline design patterns. |
| [skill-updater](skills/skill-updater/) | Meta-skill that audits your installed skills for staleness, gaps, overlaps, and freshness. Proposes and executes updates on approval. |
| [ansible-hardening](skills/ansible-hardening/) | Security hardening blueprints for Ansible roles — CrowdSec, fail2ban, auditd, Tailscale, Semaphore, scoped sudoers. Ready-to-implement role definitions with defaults. |
| [claude-to-cursor](skills/claude-to-cursor/) | Converts Claude Code skills to Cursor-compatible `.mdc` rule files. Includes classification logic for which skills convert well and which are Claude Code-only. |
| [fleet-manager](skills/fleet-manager/) | Multi-machine fleet operations via SSH, rsync, and Ansible. Health checks, cross-host syncing, inventory management. Templated for any fleet topology. |
| [budi-analytics](skills/budi-analytics/) | Reference for [budi](https://github.com/jwalsh/budi) (WakaTime for Claude Code) — CLI commands, architecture, hook coexistence, cost model, troubleshooting. |
| [openclaw-ops](skills/openclaw-ops/) | OpenClaw/NemoClaw secure deployment guide — sandbox management, Tailscale integration, inference config, security hardening, ClawHub skill vetting. |
| [inbound-sync](skills/inbound-sync/) | Structured sync bundles for capturing decisions from claude.ai conversations and ingesting them into local projects via Claude Code. Template-based with reconcile script integration. |

## Installation

### Single skill

```bash
cp -r skills/<skill-name> ~/.claude/skills/
```

### All skills

```bash
cp -r skills/* ~/.claude/skills/
```

### Verify

```bash
ls ~/.claude/skills/
```

Skills are loaded automatically by Claude Code when their trigger phrases match your prompt. No restart required.

## How Skills Work

Claude Code skills are markdown files (`SKILL.md`) placed in `~/.claude/skills/<name>/`. Each skill has:

- **YAML frontmatter** with `name` and `description` (including trigger phrases)
- **Markdown body** with instructions, tables, rules, and reference data
- **Optional `references/` subdirectory** for large reference data (pricing tables, etc.)

Claude Code reads all installed skills at session start and activates them based on description matching against your prompts.

## Customization

These skills are designed to be forked and customized:

- **fleet-manager**: Replace `YOUR_IP` and `YOUR_HOST` placeholders with your actual fleet inventory
- **openclaw-ops**: Replace `YOUR_TAILSCALE_IP`, `YOUR_HOST`, and `YOUR_TAILNET` with your Tailscale details
- **token-miser**: The routing tables work as-is; update `references/model-pricing.md` when Anthropic changes pricing
- **inbound-sync**: Customize the save path and reconcile script path for your project structure

## Acknowledgments

Some skills in this collection were inspired by community work:

- [Matt Pocock's claude-code-skills](https://github.com/mattpocock/claude-code-skills) — pioneered the skill-sharing pattern
- [Trail of Bits](https://github.com/trailofbits) — security-focused AI tooling patterns that influenced the hardening and ops skills

## License

MIT. See [LICENSE](LICENSE).

## Author

Created by [your-github-user](https://github.com/your-github-user).
