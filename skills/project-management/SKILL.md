---
name: project-management
description: >
  Track, plan, and coordinate work across multiple projects. Maintains
  awareness of project phases, dependencies, and resource allocation.
  Trigger on: "what's the status", "project status", "what needs work",
  "prioritize", "what's next", "plan work", "coordinate", "roadmap", "backlog".
---

# Project Management

Track and coordinate work across a multi-project platform.

## Decision Framework

When prioritizing work:
1. **Revenue potential** — highest-value project first
2. **Dependencies** — what unblocks the most other work?
3. **Resource fit** — GPU work on GPU hosts, CPU work on CPU hosts
4. **Risk** — security hardening before feature work
5. **Quick wins** — small tasks that close out a phase

## Phase Tracking Convention

Each project uses its own phase prefix (M1, H1, C1, P1, D1, etc.).
Plans live in `<project>/plans/` as markdown files.

## Coordination Rules

- Check swarm status before starting work
- Don't work on the same project another instance is actively editing
- Use git worktrees for parallel work on the same repo
- Commit frequently — other instances pull your changes
