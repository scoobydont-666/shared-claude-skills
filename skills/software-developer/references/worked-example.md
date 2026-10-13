# Worked developer example: implement the retry-safe job slice

**Illustrative exercise; no code, tests or deployment are claimed by this example.**
Input is the architect's scoped contract, not an instruction to replace the queue
or change production. Verify the real endpoint, transaction semantics and worker
before selecting implementation details.

## Establish the failing behavior

Build an isolated integration fixture for the actual database boundary. Submit
one request, simulate response loss after the durable creation point, then retry
with the same tenant/key/payload. The regression must fail because two logical
jobs appear on the baseline, not because a fixture, command or dependency is
missing. Preserve both the baseline and candidate identity in the evidence.

## Implement the smallest complete path

Use the existing request authentication and validation. Add a compatible scoped
uniqueness constraint and record binding tenant, operation, key, request hash and
job ID. Keep record creation and job creation in one transaction when supported
by the existing data model. Handle a uniqueness conflict by resolving the original
record under the database's actual isolation rules; do not catch every exception
and return success. Define bounded waiting for an in-flight conflicting request.

Same key and same payload returns the original job identity. Same key and different
payload returns the agreed conflict. Cross-tenant access is refused regardless
of key similarity. Do not log request payloads, raw keys or secrets as metric labels.
Do not add an outbox if the database job table already is the authoritative queue.
If an external broker introduces a publish gap, return that material design issue
to the architect rather than inventing unreviewed semantics.

## Required discriminating checks

| Check | What must be observed |
|---|---|
| First submission | Exactly the expected durable record/job and valid response. |
| Same request retried | Same job identity; no duplicate logical job. |
| Different payload/same key | Explicit conflict; no overwritten original. |
| Different tenant | No data disclosure or unauthorized result reuse. |
| Concurrent submissions | Uniqueness/transaction behavior holds under actual concurrent calls. |
| Interruption before commit | No half-created durable record presented as success. |
| Response lost after commit | Retry resolves committed outcome without repeating effects. |
| Database unavailable or wait budget exhausted | Explicit bounded failure, not an empty successful result. |
| Old client and mixed version | Agreed compatibility behavior; no hidden mandatory upgrade. |

A test that mocks the whole transaction can prove wrapper behavior but not the
concurrency invariant. Use negative controls: remove the uniqueness behavior in
a disposable fixture and confirm the relevant test fails; retain normal success
checks so a permanently failing endpoint cannot pass the suite.

## Handoff and recovery limits

Return the real diff, candidate revision, test outcomes, schema/API notes and
unverified work. Preserve two independent final-head reviews. A reversible app
release may still rely on an additive schema that should not be destructively
downgraded. Give CI/CD those constraints; do not test rollback on real customer
data or report production verification from a local integration test.
