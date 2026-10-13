# Developer handoff template

A review packet should make the change and its evidence independently inspectable.
Use the existing task/PR instead of opening another tracker. Fill with actual
observations, not commands you intend to run.

## Outcome and identity
IMPLEMENTED / NO_CHANGE / INVESTIGATED / PARTIAL / BLOCKED. Task, repository,
owned worktree/branch, baseline, candidate SHA or UNCOMMITTED/NONE, and publication
state. A source SHA is not a deployed version.

## Behavior and scope
Problem, requirement/architecture references, affected consumer path, actual delta,
non-goals and preserved invariants. Explain changes from the accepted design and
which require a decision owner. Identify generated/exported copies separately.

## Acceptance and tests

| AC ID | Expected behavior | Observed result | Evidence reference | Limits/remaining work |
|---|---|---|---|---|
| Actual ID | Input/failure -> response | PASS/FAIL/NOT_RUN/NOT_APPLICABLE | Actual run/source/configuration | Reason and owner |

Record test command or run, environment/tool versions, expected and collected
counts, results, baseline reproduction and candidate. Identify mocks, unavailable
platform tests, baseline failures and any approved exception. Passing declarations
are not independent evidence until verified by the existing trusted path.

## Compatibility and operations
Configuration/secrets references (no values), API/schema/dependency changes,
mixed-version/upgrade implications, idempotence and recovery tests, observability,
packaging/install scope and remaining deployment work. Do not claim rollback is
safe without accounting for changed data.

## Review and next action
Self-review completed with remaining risks. Independent reviews pending or real
links identifying final-head scope. Next owner/action. Do not conflate review,
merge, release, deployment and runtime verification.

For a machine handoff, use the receiving system's documented schema. No validator is bundled.
