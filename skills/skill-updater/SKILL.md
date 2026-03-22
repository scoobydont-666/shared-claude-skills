---
name: skill-updater
description: >
  Self-assessment and auto-update for Claude Code's installed skills, CLAUDE.md
  files, and reference data. Audits for staleness, gaps, overlaps, and freshness.
  Triggers on: "update your skills", "skill audit", "skill assessment", "refresh
  skills", "are your skills up to date", "check your skills", "review your
  context", "tune yourself up", "make yourself better".
---

# Skill Updater — Self-Assessment & Auto-Update (Claude Code)

## When to Trigger

- "update your skills" / "refresh skills" / "skill audit"
- "are your skills up to date" / "check your skills"
- "tune yourself up" / "make yourself better"

## Workflow

### Phase 1 — Inventory

1. **List all installed skills**: `ls ~/.claude/skills/`
2. **Read CLAUDE.md files**: `~/.claude/CLAUDE.md`, project `CLAUDE.md`, nested
3. **Scan recent git history**: `git log --oneline -20` for active workstreams

### Phase 2 — Audit Each Skill

For every skill directory:

1. **Read the SKILL.md** — check for:
   - Stale dates or version references
   - Overlap with other skills
   - Missing coverage for known active projects
   - Description quality (will it trigger reliably?)
   - References to claude.ai-only tools (`memory_user_edits`, `conversation_search`,
     `recent_chats`) — these don't exist in Claude Code

2. **Read reference files** — check for:
   - Outdated data (prices, versions, API endpoints)
   - Missing reference files that should exist

3. **Freshness checks** (web search only when needed):
   - **token-miser**: Compare `references/model-pricing.md` header date. If >90 days, web search.
   - Any skill with dated reference data: check if >6 months old.

### Phase 3 — Gap Analysis

- **Active projects without skills** — check memory files and CLAUDE.md for gaps
- **CLAUDE.md gaps** — conventions in skills not reflected in CLAUDE.md
- **Skill overlap** — two skills covering the same ground
- **Missing conventions** — patterns in code/commits not captured anywhere
- **Stale CLAUDE.md entries** — rules referencing removed files or outdated versions

### Phase 4 — Report & Propose

Terse tables and bullet points:
1. **What's current** — no changes needed
2. **What's stale** — specific data points that are wrong
3. **What's missing** — skills or entries that should exist
4. **What overlaps** — skills to consolidate
5. **Proposed actions** — ranked by impact

Ask the user which actions to take.

### Phase 5 — Execute

1. **Skill updates** — Edit SKILL.md and reference files in place
2. **New skills** — Create directory + SKILL.md in `~/.claude/skills/`
3. **Reference updates** — Web search for current data, rewrite reference file
4. **CLAUDE.md updates** — Edit the appropriate CLAUDE.md

## Frugality

- Don't web-search every skill — only time-sensitive reference data
- Don't re-read skills already in the current session
- Only propose actions with clear ROI
- Batch file edits

## Output Format

Tables and bullet points, not prose. Flag issues, propose fixes, execute on approval.
