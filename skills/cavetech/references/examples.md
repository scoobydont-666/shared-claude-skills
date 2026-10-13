# cavetech examples

All operational scenarios below are synthetic fixtures, not reports about a live
system. Record labels are optional when an exact direct answer is sufficient.

## 1. Direct technical answer

Verbose:
> The observed p95 latency is 420 milliseconds. The target is no more than 250
> milliseconds, so this result does not meet the target.

cavetech:
```text
res: latency; observed_p95=420ms; target_p95<=250ms; state=failed
```

The metric percentile, unit, comparison, and observed/target distinction survive.
In real reporting, retain the actual run ID, time, and evidence anchor when relevant.

## 2. Review finding: fact vs inference

Synthetic source excerpt:
```text
app/cache.py, lines 41-42:
cache_key = tenant_id
return cache.get(cache_key)
```

cavetech:
```text
ctx: fixture=true; scope=quoted app/cache.py excerpt only
obs: cache_key=tenant_id; user_id absent from key; src=excerpt:41-42
hyp: users within one tenant may receive each other's cached data; pre=cached data is user-specific
block: cache writer/value semantics unknown; impact=cross-user exposure unconfirmed
next: inspect cache writer/value contract; if user-specific, key by tenant_id AND user_id; add same-tenant/different-user isolation test
```

Do not turn a plausible defect into a confirmed incident. Do not claim the fix
was applied, tested, or deployed.

## 3. Small-model implementation handoff

Synthetic task: add a request timeout, but preserve existing retries and avoid
modifying deployment manifests.

```text
ctx: fixture=true; owner=worker-a; write_scope=client.py,tests/test_client.py
req: request timeout=10s; preserve retry behavior; MUST_NOT edit deployment manifests
block: current client API/timeout behavior unknown
next: inspect client.py + tests/test_client.py before edits; return observed API + affected callsites
```

A precise inspection step is better than inventing function names or a patch from
missing repository context. Once grounded, replace the blocker with exact ordered
steps and observable acceptance checks.

## 4. Preserve a dangerous negation

Input:
> Delete only the worktrees that this task created, and only after confirming that
> they are clean and that their work has been merged. Do not delete any other
> worktree. If ownership cannot be established, leave it untouched.

cavetech:
```text
do: delete worktree ONLY IF created_by=this_task AND clean=true AND merged=true
req: ownership unknown => leave untouched; every non-task worktree => leave untouched
```

Invalid compression:
```text
do: clean worktrees
```

The invalid form loses ownership, merge, cleanliness, and unknown-state constraints.
These examples do not grant deletion authority; existing authorization still applies.

## 5. Tests vs deployment

Synthetic supplied evidence:
```text
unit-run-17: passed=18 failed=0
integration-run-18: not started; database unavailable
deployment: not attempted
```

cavetech:
```text
ctx: fixture=true
res: unit tests; state=passed; passed=18; failed=0; evidence=quoted unit-run-17
res: integration tests; state=not_tested; evidence=quoted integration-run-18
block: database unavailable; impact=integration coverage absent
res: deployment; state=not_tested; detail=not attempted; evidence=quoted deployment record
next: restore test database; run integration suite; deployment readiness remains unverified
```

Never compress this to `done`, `green`, or `ready to deploy`.

## 6. Exact commands remain exact

A requested command is a planned action, not execution evidence.

```text
do: 1. run unit tests from repository root; expect=exit 0
```
```bash
python -m pytest tests/unit -q
```

Do not change a supplied path, quoting, flag, or literal to save tokens.
Do not emit shell-looking pseudocode such as `pytest unit => green` as an executable.

## 7. Delta needs an available baseline

```text
ctx: fixture=true; recipient_has_baseline=false
block: baseline unavailable; impact=delta-only handoff insufficient
next: provide self-contained current snapshot or retrieve exact baseline
```

A checksum identifies bytes; it does not supply their meaning. An inaccessible
reference is a missing dependency, not successful compression.

## 8. Preserve a conflict

Synthetic supplied records disagree about one workload at different times.

```text
ctx: fixture=true; workload=api
obs: replicas_ready=3; at=2026-09-25T10:00:00Z; src=quoted sample-A
obs: replicas_ready=1; at=2026-09-25T10:05:00Z; src=quoted sample-B
hyp: ready replicas decreased; verify=confirm identical workload scope + refresh observation
next: query current ready/desired counts; do not report sample-A as current state
```

## 9. Required schema wins

When a consumer requires `{"status": "...", "summary": "..."}`, use exactly that
schema. Apply brevity inside allowed text fields; do not rename fields or replace
JSON with cavetech records. Never add unsupported keys merely to fit this skill.

## 10. Round-trip acceptance

For a representative before/after sample, a receiving agent should reconstruct:
1. The requested outcome and exact constraints.
2. What is observed, inferred, planned, attempted, or verified.
3. Scope, ownership, dependencies, evidence, and unresolved information.
4. The next permitted action and its success/failure conditions.

A material mismatch fails the sample. Expand/rewrite; do not accept ambiguity in
exchange for a smaller token count. Measure token cost with the actual target
model/tokenizer, including skill loading and follow-up clarification overhead.
No model-specific token savings or execution-quality improvement is asserted here.
