---
name: cost-optimizer
description: Unified cost awareness across Swarm operations. Claude API model routing, infrastructure electricity/TOU costs, mining profitability, cloud hosting budgets.
triggers:
  - cost
  - spending
  - how much
  - save money
  - cheaper
  - expensive
  - budget
  - budi stats
  - token cost
  - electricity cost
  - hosting cost
  - optimize cost
  - reduce spending
  - cost analysis
  - cost breakdown
  - token usage
  - API cost
---

# Cost Optimizer

Three cost dimensions: Claude API, Infrastructure, Cloud Hosting.

## 1. Claude API Costs

### Model Pricing (per million tokens — input/output)

| Model         | Input    | Output   | Use For                              |
|---------------|----------|----------|--------------------------------------|
| opus          | $5.00    | $25.00   | Architecture decisions, adversarial review |
| sonnet        | $3.00    | $15.00   | Default — code edits, analysis       |
| haiku         | $1.00    | $5.00    | Status checks, file reads, git ops   |

### Session-Miser Routing Rules
- Start every session on `sonnet` (default)
- Escalate to `opus` only for: deep reasoning, security review, complex architecture
- Delegate to `haiku` subagents for: search, log tails, file reads, git status, simple transforms
- Use effort levels: `opus:low` is cheaper than full opus for structured tasks

See: `session-miser` skill for full routing logic.
See: `token-miser` skill for subagent cost controls.

### Anti-Patterns (Avoid)
- Using Opus for git commits or file reads
- Not delegating read-only work to Haiku subagents
- Running full sessions on Opus when Sonnet suffices
- Skipping effort level specification on Opus calls

### Token Tracking: budi

```bash
# Session cost summary
budi stats

# Cost by model
budi cost

# Dashboard (local)
open http://127.0.0.1:7878

# Weekly report
budi report --period week
```

See: `budi-analytics` skill for full budi usage.

## 2. Infrastructure Costs

### Electricity
- TOU rates apply — peak hours cost 2-3x off-peak
- Solar offset via Enphase IQ Gateway (10.0.0.50)
- Key metric: `solar_net_watts` — positive = free electricity (exporting)
- When net_watts > 0: run full mining fleet, cost = $0 for that power

### Mining Profitability (Hashrate Hedger)
- Inputs: XMR spot price, network difficulty, pool hashrate, electricity rate, solar_net_watts
- Decision: run full fleet / throttle / pause based on break-even threshold
- ProjectB hosts: node-primary (P2Pool relay), node-miner (XMRig ~10.5 KH/s), node-gpu (XMRig)
- Never run XMRig on node-primary — it is NOT a miner

### Service Power Draw (approximate)
| System       | Draw    | Notes                         |
|--------------|---------|-------------------------------|
| node-gpu (idle)  | ~150W   | 2x RTX 5080 servers           |
| node-gpu (mining)| ~400W+  | GPU-accelerated RandomX       |
| node-primary     | ~35W    | i5-8500, no discrete GPU      |
| node-miner      | ~90W    | Ryzen 9600X mining            |

See: `solar-energy` skill for TOU and battery pre-positioning.
See: `crypto-monero-wizard` skill for mining profitability formulas.

## 3. Cloud Hosting — ProjectE

Projected Year 1 costs (when deployed):
- AWS/Azure app hosting: $40-80/mo
- Ollama inference stays on node-gpu (self-hosted, no cloud cost)
- PostgreSQL: RDS ~$15/mo or self-hosted on node-gpu (~$0 marginal)
- CDN/storage: minimal (<$5/mo at launch volume)

Strategy: maximize self-hosted workloads on node-gpu before adding cloud spend.

## Weekly Cost Review Checklist
1. `budi stats` — check session token spend vs prior week
2. Grafana dashboard — GPU power draw trend
3. Check solar production vs consumption ratio
4. Review any cloud services added since last review
5. Confirm no Opus usage for mechanical tasks (check budi by model)

## Related Skills
- `session-miser` — model routing decisions
- `token-miser` — subagent cost enforcement
- `budi-analytics` — token spend dashboards and CLI
- `solar-energy` — electricity offset via solar
- `crypto-monero-wizard` — mining cost/profitability
