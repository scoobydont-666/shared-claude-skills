---
name: stay-ready
description: >-
  Keep work moving while a CI, review, merge or deploy gate is pending. Prepare the
  next verified step, unblock later dependencies and finish peripheral work, without
  moving frozen heads or claiming green before evidence exists.
---

# Stay ready

> Do prework while a gate is pending: unblock a likely roadblock or finish peripheral
> work. When the gate opens, be ready to move.

## Rules while a gate is pending
1. Preserve the exact candidate and its evidence. Never push to a frozen head, rerun a
   failed check without a diagnosed cause, or manufacture a green result.
2. Run bounded prework: independent review, deploy check-mode, readiness probes,
   timing analysis, docs, blocker repair on isolated branches.
3. Prepare the next command set now: change identity, worktree, credential
   presence (never values), runner capacity, IaC inputs, rollback, evidence locations.
4. Fix deterministic blockers in their owning source, with the failure, commit and proof.
5. Keep expensive work bounded: use the host's existing admission controls or disposable CI
   capacity, and protect interactive and inference headroom.
6. Reconcile live changes back to IaC in the same cycle; temporary changes get an owner,
   expiry and source counterpart.
7. At every gate transition re-derive the current head; stale reviews, plans and commands
   are invalid until re-stamped.

## Prework catalog
- **Freeze the candidate**: lock the PR head branch (`lock_branch: true`, enforce admins,
  no force-push). Findings go on the finder's own branch from the frozen head; the author
  makes ONE batched update (unlock, push, re-lock); reviewers re-stamp only the delta.
- **Local qualification**: run the full suite at the exact head AND at its merge base on
  an idle host with the same environment; report only head-only failures
  (`comm -23 head.txt base.txt`). Environment gaps (missing tool on PATH) are not product.
- **Reviewer eligibility**: list authors with `git log --format=%an main..HEAD`; authors and
  co-authors cannot be legs. Line up two clean independent reviewers before the head is final.
- **Post-merge runbook**: exact check/diff command, expected diff, apply, readback, proof,
  rollback, written before merge.
- **Supersession**: for a PR the candidate replaces, compute file containment
  (blob equality per path) and have the close comment ready, missing only the merge sha.
- **CI diagnosis**: read the failing job's own classification (new vs baseline failures);
  compare against the same tests at the merge base before blaming the candidate.
- **Anticipate the next failure**: look one stage downstream (size limits, timeouts,
  budgets) and record it before it fires.

## Status report
Name the active gate, each live prework lane, the blocker it attacks, and the evidence
ready for the next transition. "Waiting on CI" alone is an incomplete report.
