---
name: claude-swarm
description: >
  Distributed Claude Code coordination — multi-instance awareness, task sharing,
  decomposition, worktree isolation, and session summaries via NFS + git.
  Trigger on: "swarm", "other instances", "coordinate", "distribute work",
  "who else is online", "share this", "send to node".
---

# claude-swarm

Coordinate multiple Claude Code instances across a fleet of machines.

## Architecture

- NFS for real-time local coordination (sub-second)
- Git for durable remote sync and cross-network instances
- Shared task queue with capability-based routing
- Session summaries for context continuity between instances
- Zero new dependencies — just NFS + git + bash

## Key Commands

```bash
swarm status              # Who's online, what they're doing
swarm tasks               # Shared task queue
swarm tasks create "..."  # Create a task
swarm tasks claim <id>    # Claim for this host
swarm message <host> "…"  # Direct message
swarm inbox               # Check messages
swarm artifacts share <f> # Share a file with the fleet
swarm context             # What the last instance left for you
```

## Hooks

- SessionStart: registers node, shows who's online
- SessionEnd: marks idle, generates session summary
- Heartbeat: updates timestamp, checks inbox
- TaskCheck: finds capability-matching tasks

See https://github.com/your-github-user/claude-swarm for the full system.
