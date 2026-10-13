---
name: verification-before-completion
description: Run fresh checks and inspect exact-revision evidence before claiming a bug is fixed,
  tests pass, a PR is ready, or a deployment works.
---
# Evidence before completion claims

Before making a claim:
1. Name the exact claim and acceptance criterion.
2. Choose the check that can actually prove it, including an important failure case.
3. Run it on the current candidate with the actual consumed configuration/artifact.
4. Read the complete result and exit status; confirm expected tests were collected.
5. State the observed result and scope. Missing, failed, cancelled or stale evidence remains unverified.

| Claim | Required evidence | Insufficient by itself |
|---|---|---|
| Tests pass | Current required suite output, counts, no unexplained skips | Previous run or tests merely written |
| Bug fixed | Reproduction no longer fails; meaningful regression check | Code changed |
| Hook functions | Installed command receives an event fixture and produces intended output; real client check where available | File exists or syntax passes |
| Frontend works | Intended user transaction including backend/auth behavior | HTTP 200 or screenshot alone |
| Deployed | Actual artifact/config identity on each intended consumer and behavior verification | Merge, process running or health-only check |
| Migration correct | Required data invariants and recovery evidence | Script exit 0 or row counts alone |
| Security control enforced | Allowed and denied paths exercise the actual boundary | Documentation or mock-only success |

Re-run invalidated checks after edits; do not transfer success to different bytes. Test from the intended consumer's network/permissions perspective without widening service exposure just to make a probe succeed. Report unavailable client, host or CI checks as NOT_RUN or PENDING with an owner. A PR deliverable does not require unrequested deployment.

Do not hide a red baseline, suppress errors to make a scanner look absent, or retry until green without explaining the cause. Keep verification proportional to risk and the requested scope; follow `definition-of-done` for the overall delivery checklist.
