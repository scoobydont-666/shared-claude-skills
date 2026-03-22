# Anthropic Model Pricing & Benchmarks
*Last verified: 2026-03-17 from https://platform.claude.com/docs/en/about-claude/pricing*

> **FRESHNESS NOTE:** This file is a snapshot. The token-miser freshness protocol
> in SKILL.md instructs Claude to web-search for updates before making cost-critical
> routing decisions. If this file is >90 days old, treat it as a baseline only.

## Current-Generation Models (Claude 4.5 / 4.6)

| Model | API String | Input/MTok | Output/MTok | 5m Cache Write | 1h Cache Write | Cache Hit | Context |
|-------|-----------|-----------|------------|----------------|----------------|-----------|---------|
| Haiku 4.5 | `claude-haiku-4-5-20251001` | $1.00 | $5.00 | $1.25 | $2.00 | $0.10 | 200K |
| Sonnet 4.6 | `claude-sonnet-4-6` | $3.00 | $15.00 | $3.75 | $6.00 | $0.30 | 200K |
| Sonnet 4.5 | `claude-sonnet-4-5-20250514` | $3.00 | $15.00 | $3.75 | $6.00 | $0.30 | 200K |
| Opus 4.6 | `claude-opus-4-6` | $5.00 | $25.00 | $6.25 | $10.00 | $0.50 | 200K (1M beta) |
| Opus 4.5 | `claude-opus-4-5-20250415` | $5.00 | $25.00 | $6.25 | $10.00 | $0.50 | 200K |

### Fast Mode (Research Preview — Opus 4.6 only)

| Mode | Input/MTok | Output/MTok | Speedup |
|------|-----------|------------|---------|
| Standard | $5.00 | $25.00 | 1x |
| Fast | $30.00 | $150.00 | ~2.5x |

Fast mode requires beta header `fast-mode-2026-02-01`. Same model, faster inference only.

## Previous-Generation Models (higher cost, avoid for new work)

| Model | API String | Input/MTok | Output/MTok |
|-------|-----------|-----------|------------|
| Opus 4.1 | `claude-opus-4-1-20250415` | $15.00 | $75.00 |
| Opus 4 | `claude-opus-4-20250514` | $15.00 | $75.00 |
| Sonnet 4 | `claude-sonnet-4-20250514` | $3.00 | $15.00 |
| Haiku 3.5 | `claude-3-5-haiku-20241022` | $0.80 | $4.00 |

## Extended Thinking

Extended thinking tokens are billed as **output tokens** at standard rates — no separate tier.
Minimum budget: 1,024 tokens. Available on Opus 4.6, Sonnet 4.5, Haiku 4.5.

## Batch API

50% discount on all models for non-time-sensitive workloads.

| Model | Batch Input/MTok | Batch Output/MTok |
|-------|-----------------|------------------|
| Haiku 4.5 | $0.50 | $2.50 |
| Sonnet 4.6 | $1.50 | $7.50 |
| Opus 4.6 | $2.50 | $12.50 |

## Long Context Pricing (>200K input tokens)

For Sonnet 4.5, Haiku 4.5, and all future models: inputs exceeding 200K tokens
are charged at **2x** standard input rates. Output rates unchanged.

| Model | Standard Input | >200K Input |
|-------|---------------|-------------|
| Haiku 4.5 | $1.00 | $2.00 |
| Sonnet 4.6 | $3.00 | $6.00 |
| Opus 4.6 | $5.00 | $10.00 |

## Cost-Per-Call Reference

A typical call: 1,000 input + 500 output tokens:

| Model | Cost/call | 1M calls/month |
|-------|----------|---------------|
| Haiku 4.5 | $0.0035 | $3,500 |
| Sonnet 4.6 | $0.0105 | $10,500 |
| Opus 4.6 | $0.0175 | $17,500 |

**Key insight:** Opus 4.6 is only **1.67x** Sonnet's cost (was 5x with legacy Opus 4.1
pricing). This dramatically changes the routing calculus — Opus is now viable for
many tasks previously reserved for Sonnet.

## Relative Cost Ratios (Current Gen)

```
Haiku : Sonnet : Opus  =  1x : 3x : 5x  (input)
Haiku : Sonnet : Opus  =  1x : 3x : 5x  (output)
```

Compare to legacy Opus 4.1: 1x : 3.75x : 18.75x — current Opus is ~3.75x cheaper.

## Prompt Caching ROI

Two cache tiers (new with current-gen models):
- **5-minute cache**: Write costs 1.25x base input; reads cost 10% of base input
- **1-hour cache**: Write costs 2x base input; reads cost 10% of base input

Break-even: 5m cache pays off after ~2 calls; 1h cache after ~3 calls.
Best candidates: System prompts, RAG reference docs, static instructions.

## Capability Notes

### Haiku 4.5
- Best for: classification, extraction, simple transforms, JSON formatting, single-turn Q&A
- Weaknesses: multi-hop reasoning, ambiguous instructions, very long context synthesis
- Speed: fastest (~2-3x faster than Sonnet)

### Sonnet 4.6
- Best for: code generation, analysis, summarization, tool use, most user-facing tasks
- The default workhorse — handles ~80% of real-world tasks well
- Speed: moderate

### Opus 4.6
- Best for: complex reasoning, autonomous agents, open-ended analysis, highest-stakes outputs
- **New in 4.6**: 1M token context (beta), 128K max output, agent teams, compaction
- Speed: slowest (but fast mode available at 6x cost)
- **At $5/$25, now cost-effective for more tasks than legacy Opus**

## Model String Stability

- `claude-haiku-4-5-20251001` — pinned version, stable
- `claude-sonnet-4-6` — latest Sonnet 4.6, may receive minor updates
- `claude-opus-4-6` — latest Opus 4.6, may receive minor updates

Use pinned strings in production pipelines when reproducibility matters.
