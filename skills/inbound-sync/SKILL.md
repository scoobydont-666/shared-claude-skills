---
name: inbound-sync
description: >
  Generate a structured sync bundle that captures decisions, architecture changes,
  conventions, bug fixes, and roadmap updates from the current Claude.ai conversation
  for ingestion into local projects via Claude Code. Trigger when the user says
  "sync", "sync project details", "generate sync bundle", "save this for Claude Code",
  "update local projects", "export decisions", or any variation of requesting that
  conversation outcomes be persisted to the local codebase. Also trigger at the end
  of long conversations where significant decisions were made, if the user asks to
  wrap up or summarize. Do NOT trigger for general summaries unrelated to project sync.
---

# Inbound Sync — Claude.ai to Local Projects

Generate a structured sync bundle from this conversation that Claude Code can
ingest into local repositories.

---

## When to Use

The user will say something like:
- "sync project details"
- "sync"
- "generate a sync bundle"
- "save this for Claude Code"
- "export decisions"
- "wrap up and sync"

## What to Do

### Step 1 — Scan the Conversation

Review the ENTIRE conversation from the beginning. Identify every instance of:

- **Decisions made** — architecture choices, technology selections, design patterns chosen
- **Code changes discussed** — new files, modified functions, refactored modules
- **Bug fixes** — problems identified and solutions determined
- **Roadmap updates** — phases started/completed, milestones reached, priorities changed
- **Conventions established** — naming rules, workflow changes, new patterns to follow
- **Configuration changes** — env vars, service configs, port changes, dependency updates
- **Known issues found** — new bugs, limitations, workarounds discovered

### Step 2 — Classify Each Item

For each item found, determine:

1. **Project**: Which sub-project does it affect? Use your project names.

2. **Type**: What kind of change?
   - `decision` — An architecture or design choice
   - `architecture` — Structural change to the codebase
   - `bugfix` — A problem identified and fixed
   - `roadmap` — Phase/milestone status change
   - `convention` — A new rule or pattern to follow

3. **Impact**: What files or systems need updating?
   - CLAUDE.md updates (rules, patterns, known issues)
   - Source code changes (specific files)
   - Memory file updates
   - Config changes (env vars, service files)
   - Roadmap status changes

### Step 3 — Generate the Bundle

Output a single fenced code block containing one or more sync entries separated
by `---`. Use today's date. Each entry MUST follow this exact format:

```markdown
# [Short Descriptive Title]

## Date
YYYY-MM-DD

## Project
[your-project-name]

## Type
[decision | architecture | bugfix | roadmap | convention]

## Summary
[1-3 sentences: what was decided or changed and why]

## Details
[Full details. Include:
- Code snippets if functions were written or modified
- File paths affected
- Configuration values (env vars, ports, settings)
- Before/after descriptions for changes
- Rationale for decisions
- Any caveats or edge cases discussed]

## Action Items
- [ ] [Specific action]: Update [file] in [project] with [what]
- [ ] [Specific action]: Add [what] to [where]
- [ ] [Specific action]: Test [what] with [command]

---
```

### Step 4 — Add Save Instructions

After the code block, tell the user exactly how to ingest it:

```
Save this to: /path/to/your/project/sync/inbound/YYYY-MM-DD-[topic].md
Then run:     /path/to/your/project/sync/reconcile.sh
```

Customize the paths above for your project structure.

## Rules

1. **Be thorough** — Capture EVERYTHING significant. When in doubt, include it.
   A decision not synced is a decision that gets forgotten or contradicted later.

2. **Be specific** — Include file paths, function names, line numbers, env var names,
   exact values. Vague entries are useless for reconciliation.

3. **Be atomic** — One entry per distinct decision/change. Don't combine unrelated
   items. Multiple entries in one bundle is fine and expected.

4. **Use the exact template** — The reconcile script parses the headers (`## Date`,
   `## Project`, `## Type`, etc.). Do not rename or reorder them.

5. **Action items are critical** — Every entry MUST have at least one action item.
   This is how Claude Code knows what to update.

6. **Include code** — If code was written, modified, or designed during the
   conversation, include the relevant snippets in the Details section. Claude Code
   needs to see the actual implementation, not just a description.

7. **Flag conflicts** — If a decision contradicts something in the uploaded knowledge
   files, explicitly note this in the Details section so Claude Code knows to update
   the source of truth.

## Example Output

````markdown
# Redis Session Backend Wired into Production

## Date
2026-03-05

## Project
my-app

## Type
architecture

## Summary
Wired Redis session backend into the API, replacing in-memory SessionStore for production deployments. Sessions now persist across API restarts.

## Details
- Modified `api.py` to use `storage.factory.create_session_backend()` instead of in-memory `SessionStore`
- Redis backend selected when `SESSION_BACKEND=redis` is set
- Fallback to memory backend when Redis unavailable
- Session TTL and max messages still configurable via env vars
- Tested with: `curl -H "X-Session-ID: test123" ...` across service restarts

## Action Items
- [ ] Update CLAUDE.md: add Redis session backend to architecture section
- [ ] Update architecture docs: document session persistence behavior
- [ ] Update .env.example: add SESSION_BACKEND variable
- [ ] Test: `sudo systemctl restart my-app && curl http://127.0.0.1:8501/health`

---

# Agent Timeout Increased to 180s

## Date
2026-03-05

## Project
my-app

## Type
bugfix

## Summary
Complex agent was timing out on multi-step queries. Increased timeout from 120s to 180s for complex-routed queries.

## Details
- Root cause: agent decomposes into 3-5 sub-queries, each taking 30-40s
- Fix: conditional timeout in api.py — 180s for complex routes, 120s otherwise

## Action Items
- [ ] Update CLAUDE.md: add timeout note to Known Issues
- [ ] Update debugging docs: add "agent timeout" entry
- [ ] Update .env.example: document AGENT_TIMEOUT variable
````
