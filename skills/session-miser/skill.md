---
name: session-miser
description: >
  Intelligent model routing for Claude Code sessions. Recommends optimal model
  (Opus/Sonnet/Haiku) and effort level based on task complexity. Delegates
  mechanical work to cheaper subagents. Maximizes quality-per-dollar across
  the entire session. Trigger on: any new session, "save tokens", "cheaper model",
  "delegate this", "use sonnet", "effort level", "cost", or automatically when
  task complexity is clearly below the current model's tier.
---

# Session-Miser — Session-Level Cost Optimization

## Core Principle
Use the cheapest model that can do the job well. Opus for thinking, Sonnet for doing, Haiku for fetching.

For **per-call routing, pricing data, and API-level optimization**, see the `token-miser` skill.
This skill covers **session-level decisions only**: which model to start on, when to switch, and what to delegate.

## Planning Phase Exemption
During the **planning phase** (before ExitPlanMode), use Opus for all subagents:
- project-management planning — Explore/Plan agents building the work queue
- /plan mode — implementation design

**Once ExitPlanMode is called, normal routing resumes.**

## Session Start Assessment

At session start, assess the work and recommend:

| Work Profile | Recommendation |
|---|---|
| Architecture, design, complex planning | Stay on Opus |
| Debugging root cause analysis | Stay on Opus |
| Mixed planning + execution | Stay on Opus, DELEGATE mechanical tasks to subagents |
| Primarily code edits, file changes, deploys | Suggest `/model sonnet` |
| Bulk operations, config changes, formatting | Suggest `/model sonnet` |

## When to Switch Models Mid-Session

| Signal | Action |
|---|---|
| Planning phase complete, entering execution | Suggest `/model sonnet` |
| Hit unexpected architectural decision | Switch back to Opus for that decision |
| 30+ minutes of file edits on Opus | Suggest `/model sonnet` |
| Debugging shifts from "apply known fix" to "investigate root cause" | Switch to Opus |
| Cost climbing fast with no complex reasoning | Suggest delegation or model switch |

## Delegation Rules

**ALWAYS delegate (automatic, don't ask):**
- File exploration → Explore agent (haiku)
- Git status, diff, log → haiku subagent
- Searching codebase → haiku subagent
- Running bash for status checks → haiku subagent

**SUGGEST delegating (mention to user):**
- Bulk file edits across repos → sonnet subagent
- Running test suites → haiku subagent
- Documentation generation → sonnet subagent
- Config file updates → sonnet subagent

**NEVER delegate:**
- Active user discussion topics
- Security-sensitive operations
- Complex multi-step reasoning chains

## Effort Level Guide

| Effort | Use For | Relative Cost |
|---|---|---|
| high | Complex problems, architecture, security | 1x |
| medium | Most coding, debugging, research | ~0.7x |
| low | Simple edits, formatting, git ops | ~0.4x |

Prefer `opus:low` for simple tasks over switching to Sonnet entirely — preserves Opus quality for unexpected complexity.

## Cost Tracking

Check session cost via hydra-pulse / session-snitch:
```bash
# If hydra-pulse CLI available
hydra-pulse stats
```

If cost climbing fast: delegate more, switch model, or reduce effort level.

## Anti-Patterns

- Using Opus to read a file and report contents (haiku job)
- Using Opus for `git status` (haiku job)
- Using Opus for JSON/YAML formatting (sonnet:low)
- Staying on Opus for 30+ minutes of mechanical edits
- Switching to Haiku for anything requiring judgment
