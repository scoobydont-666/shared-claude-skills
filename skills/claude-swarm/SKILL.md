---
name: claude-swarm
description: "Distributed Claude Code coordination v2 — autonomous multi-instance orchestration via NFS + git. Agent registry with heartbeat, priority work queue with capability matching, event bus for cross-agent context, auto git sync, GPU slot management, session lifecycle protocol. Replaces OpenClaw for self-hosted agent coordination."
triggers:
  - swarm
  - other instances
  - node_gpu is working on
  - send to node_primary
  - share this
  - who else is online
  - coordinate
  - distribute this work
  - swarm status
  - swarm task
  - decompose task
  - worktree
  - session summary
  - last session
  - context from
---

# claude-swarm — Multi-Instance Coordination

## What This Does
Coordinates multiple Claude Code instances across the Swarm cluster using NFS-backed shared state at `/opt/swarm/`. Provides awareness of what other instances are doing, task queuing, messaging, artifact sharing, task decomposition, worktree isolation, and session summary context sharing.

## Quick Reference

### Check swarm status before starting work
```bash
python3 /opt/claude-swarm/src/swarm_cli.py status
```

### Create a task for another instance
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks create "Task title" \
  --desc "Description" --project /opt/target-project --priority high \
  --requires gpu --minutes 30
```

### Claim a task
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks claim task-001
```

### Claim with worktree isolation (conflict-free editing)
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks claim task-001 --isolate --project /opt/target-project
```

### Complete a task
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks complete task-001 --artifact results.md
```

### Complete + merge worktree to main
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks complete task-001 --merge --project /opt/target-project
```

### Complete + push branch only (another instance merges)
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks complete task-001 --branch --project /opt/target-project
```

### Task Decomposition — suggest splitting a large task
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks decompose task-001
```

### Task Decomposition — apply the suggested split
```bash
python3 /opt/claude-swarm/src/swarm_cli.py tasks decompose task-001 --apply
```

### Send a message to another instance
```bash
python3 /opt/claude-swarm/src/swarm_cli.py message node_gpu "Need the ProjectA RAG results"
python3 /opt/claude-swarm/src/swarm_cli.py message --broadcast "Deploying v2 in 5 min"
```

### Check inbox
```bash
python3 /opt/claude-swarm/src/swarm_cli.py inbox
```

### Share an artifact
```bash
python3 /opt/claude-swarm/src/swarm_cli.py artifacts share /path/to/results.md
```

### List active worktrees across fleet
```bash
python3 /opt/claude-swarm/src/swarm_cli.py worktrees --project /opt/target-project
```

### View session summaries
```bash
python3 /opt/claude-swarm/src/swarm_cli.py summaries
python3 /opt/claude-swarm/src/swarm_cli.py summaries --project /opt/swarm-projects/project-a
```

### Show what the last instance left for you
```bash
python3 /opt/claude-swarm/src/swarm_cli.py context --project /opt/swarm-projects/project-a
```

### Health check
```bash
python3 /opt/claude-swarm/src/swarm_cli.py health
```

### Force git sync
```bash
python3 /opt/claude-swarm/src/swarm_cli.py sync
```

## Task Decomposition Workflow
1. Create a large task: `tasks create "Generate 50 CPA questions across all sections"`
2. Suggest decomposition: `tasks decompose task-001` — shows subtasks based on rules
3. Apply if acceptable: `tasks decompose task-001 --apply` — creates subtask files, parent moves to `decomposed` state
4. Subtasks can be claimed independently by different nodes
5. When ALL subtasks complete, parent auto-completes

Decomposition rules:
- "all sections" or "across" + CPA sections -> split per FAR/AUD/REG/BAR + validation
- "generate AND validate" -> split into generate + validate phases
- Multiple project names mentioned -> split per project
- Capabilities auto-inferred: ollama/gpu/docker keywords tag subtasks for routing

## Worktree Isolation
- `--isolate` on claim creates a git worktree branch `swarm/<hostname>/<task-id>`
- Each instance works in its own branch, no merge conflicts
- On completion: `--merge` merges to main, `--branch` pushes branch only
- Worktree paths and branches recorded in task YAML and artifacts

## Session Summaries for Context Continuity
- On session end, a summary is auto-generated with files changed, decisions, context
- On session start, the hook loads the last relevant summary and injects into systemMessage
- This gives the new instance immediate context without re-exploring the project
- `context` command shows what the previous instance left for you

## v2 Autonomous Behavior Rules
- Agents auto-register on session start, deregister on end
- Heartbeat every 60s — stale after 5 min, tasks auto-released
- Auto-claim highest-priority matching task (by capability)
- Emit events on commit, test, task completion — other agents consume
- Auto git pull when commit events arrive from other hosts
- GPU slot claiming prevents model contention
- Session summaries auto-generated from event stream
- Conflict detection: warn if two agents editing same project
- **This is NOT advisory** — agents act autonomously within the priority framework

## v2 Modules (in /opt/claude-swarm/src/)
| Module | Purpose |
|--------|---------|
| `registry.py` | Agent presence, heartbeat, capability detection |
| `orchestrator.py` | Work queue, claim/release, priority matching, plan scanning |
| `events.py` | Event bus (NFS JSON), query by time/type/project |
| `sync_engine.py` | Auto git pull/push, config sync, dirty repo detection |
| `conflicts.py` | Project/file conflict detection, GPU slot management |
| `session.py` | Full lifecycle: start → heartbeat → work → events → end |

## Session Protocol
```python
from session import start_session, end_session

# On session start:
info = start_session(model="opus-4.6", project="/opt/swarm-projects/project-e")
# → registers agent, starts heartbeat, pulls repos, reads event catchup

# During work: events auto-emitted on commit/test/task completion

# On session end:
result = end_session()
# → pushes repos, syncs config, writes summary, deregisters
```

## Node Map
| Host | IP | Role | Capabilities |
|------|-----|------|-------------|
| node_gpu | 10.0.0.10 | NFS primary | docker, gpu, ollama, tailscale |
| node_primary | 10.0.0.20 | NFS replica | docker, tailscale |
| node_reserve1 | TBD | client | TBD |
| node_reserve2 | TBD | client | TBD |

## Task States
- `pending` — available for claiming
- `claimed` — being worked on by a specific host
- `completed` — done
- `decomposed` — split into subtasks (auto-completes when all subtasks done)

## Node States
- `active` — instance running, available for coordination
- `idle` — no active session
- `offline` — no heartbeat for >5 minutes
- `busy` — active but do not interrupt

## File Locations
- Project: `/opt/claude-swarm/`
- NFS share: `/opt/swarm/` (mounted from node_gpu or node_primary replica)
- Config: `/opt/claude-swarm/config/swarm.yaml`
- CLI: `/opt/claude-swarm/src/swarm_cli.py`
