# shared-claude-skills

A clean-slate, drop-in Claude Code skill + hook + harness kit for teams
who want a curated, generic, redistributable collection.

This kit is the full Claude Code kit — generic skills (development
methodology, infrastructure ops, security, planning, session
persistence, code review), generic hooks, and a generic harness
configuration. Every skill is portable to a fresh team's environment
via `git pull` and `CONFIGURATION.md` substitution.

## Status

`status: ACTIVE` · `tier: tool` · `license: MIT`

## What's in this repo

* **`skills/`** — Claude Code skills (SKILL.md files in directories,
  installable to `~/.claude/skills/`)
* **`hooks/`** — generic Claude Code hooks
* **`harness/`** — generic harness configuration
* **`kit-manifest.yaml`** — the triage manifest that records every
  decision: which skills are included, which are excluded, what
  rewrite-level each needs, what placeholders each requires
* **`CONFIGURATION.md`** — the user-supplied placeholder values
  (paths, credentials, environment identifiers)
* **`scripts/`** — the build pipeline (`sanitize.py` + `build.py`)
* **`README.md`** — this file

## Quick start

```bash
# 1. Clone the kit
git clone https://github.com/scoobydont-666/shared-claude-skills.git
cd shared-claude-skills

# 2. Fill in CONFIGURATION.md with your environment values
$EDITOR CONFIGURATION.md

# 3. Render the kit (substitutes placeholders, sanitizes lab content)
python3 scripts/build.py render

# 4. Install to ~/.claude/skills/
python3 scripts/build.py install

# 5. Verify
python3 scripts/build.py validate
```

For consumers who just want a curated set of skills without filling in
configuration: `python3 scripts/build.py install --defaults` installs
the kit with `{{...}}` placeholders left literal (skills that need
real values will display the placeholder until you set them).

## Selection rule

Every skill in this kit is **generic and portable** — the doctrine is
transferable across teams, the examples use `{{...}}` placeholders
for environment-specific values, and every lab-specific reference is
sanitized out.

We explicitly REMOVE:

* **Instance-only skills** (couple to a single project's infrastructure)
* **Personal-domain skills** (US tax, Monero, solar, resume, short-term
  rental)
* **Vendor lock-in** (Claude Code-specific plumbing, vendor-locked
  assistants, single-vendor eval stacks)
* **Deprecated** skills

The full triage decisions live in `kit-manifest.yaml`. The triage is
auditable — every keep/remove decision has a written reason.

## Distribution contract

Every file in this repo is safe to read by a stranger. There are zero
references to internal hostnames, personal names, ticket ids, lab
project paths, or vendor-locked credentials. Every environment-specific
value is a `{{...}}` placeholder that `CONFIGURATION.md` resolves at
build time.

The build pipeline (`scripts/build.py`) enforces this contract:

1. **`scripts/sanitize.py`** — applies generic patterns (RFC1918 IPs,
   secret formats, bare user-home paths) plus lab-specific patterns
   from `FACT_PACKS_DENY_FILE` (a user-supplied deny file the lab
   operator maintains externally)
2. **Placeholder substitution** — every `{{...}}` token is replaced
   with the operator's value from `CONFIGURATION.md`

## License

MIT. See the `LICENSE` file.

## Contributing

Pull requests welcome. Before adding a new skill:

1. Verify the skill is generic (transferable across teams)
2. Identify placeholders for any environment-specific value
3. Add the skill to `kit-manifest.yaml` with `decision: keep` and the
   appropriate `rewrite_level`
4. Add the placeholders to the placeholder inventory in
   `kit-manifest.yaml`
5. Add the skill to `skills/<name>/SKILL.md` with `{{...}}` tokens

The CI pipeline runs `scripts/build.py validate` on every PR and
rejects any change that introduces a lab-specific pattern.

## Pointers

* `kit-manifest.yaml` — full triage + placeholder inventory
* `CONFIGURATION.md` — operator-supplied values
* `scripts/sanitize.py` — sanitizer (generic-only; lab-specific
  patterns live in `FACT_PACKS_DENY_FILE`)
* `scripts/build.py` — orchestrator
