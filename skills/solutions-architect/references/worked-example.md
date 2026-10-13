# Worked architecture example: retry-safe job submission

**Illustrative design, not a claim about an inspected or deployed repository.**
A client retries after its connection times out. The service currently creates
another job. The outcome needed is one logical durable job for a retry, not the
purchase or construction of a new queue platform.

## Evidence and constraints to obtain

Inspect the real endpoint, authorization layer, job persistence, transaction
support, worker path and release/deployment owners. Establish retry duration,
maximum payload, tenant identity, key retention, compatibility requirements and
whether a database row or external broker actually starts work. Until inspected,
these are assumptions. Do not invent throughput or database guarantees.

## Minimal options

**Process-local key cache:** small, but restart and multiple workers can bypass
it. Reject when durable duplicate prevention is required.

**Transactional record in the existing database:** binds tenant, operation, key,
request fingerprint and durable job identity. Prefer when the job is represented
in the same database and its transaction can create the record and job together.

**Separate deduplication service or broker redesign:** can centralize the concern,
but adds another failure and operating boundary. Do not choose it without an
unmet requirement that the existing database cannot satisfy.

## Proposed contract

Scope keys to authenticated tenant and operation; a different tenant must not
retrieve another tenant's result. Canonicalize the accepted request fields with
a documented version before hashing; never include secret values in logs. The
same scoped key and same request returns the same durable job identity. A reused
key with different request data returns an explicit conflict. Define response
status and shape for the actual API, including an in-progress request.

Use a database uniqueness constraint and transaction, not check-then-insert logic
without atomicity. Concurrent conflicts must converge on the recorded job identity.
If the network fails after commit, a retry reads the prior result. Define what
happens while the first transaction remains uncommitted. Bound waiting/retries.

If an external broker must receive work, examine the transaction-to-publish crash
gap. A transactional outbox may be appropriate; add a publisher and consumer
idempotence only when needed. Do not claim exactly-once external side effects.
Specify key expiration and the duplicate risk after retention expires.

## Developer-ready slices

1. Inspect/reproduce the duplicate and establish tenant/key/payload semantics.
   Add the failing integration check against the actual database type.
2. Add compatible schema and the atomic endpoint path. Prove normal creation,
   same-key retry, conflicting payload, tenant separation and concurrent requests.
3. Exercise interruption before/after commit, bounded waits and existing-client
   compatibility. Add operational metrics without key/payload cardinality leaks.
4. Hand a release to CI/CD with schema/old-version compatibility and recovery
   constraints. Deployment and rollout verification are separate work.

**Design acceptance:** all important semantics are explicit and testable, the real
transaction behavior is supported by evidence, and independent review resolves
critical gaps. This document alone establishes none of those runtime results.
