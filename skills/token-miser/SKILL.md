---
name: token-miser
description: Reduce model token and cost waste using measured quality, task routing, compact context
  and paired provider usage receipts; verify current model availability and pricing.
---
# Token and cost discipline

Choose the cheapest available model/configuration that meets the task's measured acceptance criteria. Discover the actual model menu, quotas and pricing from the configured provider; do not invent model aliases, free capacity or a private routing service.

- Read relevant context once; send precise excerpts and deltas with enough baseline to interpret them.
- Cache reusable context only when the provider/client supports it. Distinguish cache hits, ordinary input and output usage. Encoding text as base64 is not useful semantic compression.
- Bound output, retries and parallel work. Obtain existing scoped authority for paid calls and additional agents; a cost skill does not authorize spending.
- Route mechanical tasks to smaller models only after testing correctness and tool behavior. Escalate when the failure mode warrants it. Count retries and reviewer time when comparing costs.
- Treat session model changes as recommendations unless the client exposes an authorized switch. Do not pretend a skill can switch a running session by naming a model.
- Compare matched tasks with the same rubric and quality threshold. Report successful-task cost and latency, not only per-token price.

## Optional receipt ledger

`scripts/token_ledger.py` records validated call receipts and reports paired baseline/after observations. It requires Python 3.10+ on a POSIX platform (`fcntl`); it makes no provider calls. Inspect `--help`, `record --help` and `report --help` before use. Run from this skill directory or use the installed absolute script path:

```bash
python3 scripts/token_ledger.py --help
python3 scripts/token_ledger.py report calls.jsonl --format markdown
```

Supply benchmark/input/rubric hashes, declared and observed model, measured token counts, provider-reported cost/latency/quality, and dated pricing provenance. Never fabricate a receipt. Stale pricing, model mismatches, corrupt records and incomplete pairing cannot establish savings. Store receipts in a user-chosen private directory; do not include prompts, credentials or personal content.

Run the bundled regression suite with `python3 -m unittest discover -s tests -v` from this skill directory. Interpret results within the measured workload; do not promise universal savings.
