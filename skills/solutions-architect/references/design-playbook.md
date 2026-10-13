# Design playbook: use the axes that affect this decision

This is a working reference, not a mandatory checklist for every task. A design
is valuable when it removes an important implementation or operational ambiguity.

## Discovery and problem framing

Interview the requirement, not just its proposed implementation. Who experiences
the problem? What evidence shows its frequency/severity? What is the present
workaround and cost? Who will own operations, security exceptions and retirement?
What must remain unchanged? What would make doing nothing the better choice?

Inspect source and real runtime evidence separately. Inventory existing entry
points, services, shared libraries, contracts, data stores, configuration owners,
release units and deployers. Map relevant in-flight PRs so a new plan does not
reimplement work already under review. Record uncertainty rather than treating
unavailable inventory as empty. Summarize the important gaps for the decision owner.

## Quality-attribute scenarios

Use: **actor/stimulus -> environment/workload -> affected boundary -> response ->
measure -> threshold -> evidence/owner**. For example, a dependency times out while
processing a retried job submission; the service either returns the existing
job identity or an explicit retriable failure without creating a second job.
The latency budget and maximum retry duration must be agreed, not invented.

| Attribute | Questions that lead to implementation |
|---|---|
| Availability/recovery | Which user journeys matter? What is the tolerated outage/data loss? Which dependency failures can be isolated? Who performs restore? |
| Latency/capacity | At which percentile and offered load? What work is synchronous? What queues/backpressure bound overload? |
| Consistency/durability | Who is authoritative? Which writes must be atomic? What does a client observe after retry, failover or stale read? |
| Security/privacy | What are the assets, actors, tenant boundaries, retention rules and privileged operations? How are permissions verified? |
| Operability | Can an operator identify version/configuration, diagnose failures and safely recover without the original author? |
| Compatibility | Which existing clients and mixed-version deployments must work? What is the deprecation/exit path? |
| Usability/accessibility | What errors, progress, cancellation and keyboard/assistive access does the user need? |
| Economics | Build/support effort, fixed/variable runtime cost, licensing, switching cost and team capacity? |

A service objective should describe a user-relevant indicator, evaluation window
and target. Distinguish a desired objective from a measured result and a contractual
promise. Avoid turning every metric into a page-worthy alert. Proposed thresholds
need owner agreement and representative traffic before they can certify rollout.

## Option selection and decision records

Reject options violating hard constraints before weighting preferences. Compare
reuse/no change, a minimal extension, and a genuinely different alternative.
Describe the operational burden of each: deployment, secrets, backup/restore,
patching, new skills, incident ownership and removal. Include external vendor
pricing/licensing assumptions as dated evidence; do not infer redistribution rights.

Decision record:

```text
ID / status (PROPOSED, ACCEPTED, SUPERSEDED) / owner:
Problem, constraints and evidence:
Options considered and disqualifiers:
Decision and rationale:
Positive and negative consequences:
Compatibility, delivery and operational obligations:
Unknowns / experiment needed:
Reconsider when:
```

The architect proposes status; only the existing decision process establishes
acceptance. Do not pick microservices, event sourcing, a service mesh, a vector
store or a new orchestrator because the words appear in a requirement.

## Interface and data contracts

Name the provider, consumer, version, wire/schema format and data owner. Define
success and failure shapes, authorization scope, limits, deadline/cancellation,
idempotency/retry, duplicate/misordered events, and backward compatibility.
Specify pagination consistency and limits for collection APIs; never assume an
empty page means no resources when collection failed. Document partial success
for batch operations. For asynchronous work distinguish accepted, persisted,
executing, completed and externally observed states.

For persisted data specify key/tenant boundaries, constraints/indexes, transactions,
retention/deletion, encryption/key ownership, backups and recovery. For dual writes,
explain crash windows and reconciliation. A transactional outbox can bridge a
local transaction and later event publication but does not make an external
consumer's effects exactly once; consumers still need appropriate deduplication.
Use it only when that boundary exists and the operational cost is justified.

## Failure and threat table

For each important scenario record detection, containment, user-visible behavior,
recovery, verification and owner. Include negative/positive controls for security
boundaries. Think through compromise of a dependency, tool result, build job or
privileged identity, not only malformed HTTP inputs. A signed record needs a
trusted issuer and subject binding; a hash identifies bytes, not a trusted source.

Treat cache invalidation and fallback as design decisions. Is stale data safe?
Does fallback preserve authorization and semantics? What prevents a fallback from
bypassing metering, tenant separation or limits? When outcome is unknown, who
reconciles it before retry? Record data loss risk before automating rollback.

## Capacity and cost worksheet

State units and distinguish measurement, estimate and target. Use a representative
request mix rather than one average request. Include saturation/queueing, memory
per active task, storage growth/retention, read/write rates, connection limits,
network/egress and accelerator constraints where applicable. Ask which assumption
changes the recommendation rather than computing false precision.

Illustrative calculation only: 20 completed requests/second at 0.15 seconds mean
in-system time corresponds to about 3 requests in flight in a stable measured
system. That does not establish tail latency, peak capacity, queue bounds or
required headroom. Test bursts and slow dependencies separately.

Count total ownership cost: implementation, reviews, migration, security updates,
backup/recovery, monitoring and human interventions. Use low/normal/peak scenarios
and identify the inputs needing measurement. A reused component can still be
expensive if its maintenance or failure coupling is unacceptable.

## AI/harness-specific design questions

Separate inference, retrieval, planning and execution. Bind evaluations to model,
quantization, prompt/skill, tools, dataset/split, configuration and hardware.
Do not compare incompatible benchmarks and call one implementation faster.
Treat retrieved documents, model outputs and tool data as untrusted inputs;
separate instructions/authority from those data. Define token/time/concurrency
budgets, context truncation policy, safe fallback, cancellation and stale-evidence
rules. Keep protected keys and permissions outside agent-writable task packets.

Favor existing harness/IPC/evidence/learning systems. Plan sanitized distribution
as a separate provenance/license/privacy review, not a rename-and-publish action.
Document where adapters do not enforce the same behavior. A portable skill file
is not portable runtime enforcement.

## Primary reference basis

These inform selected techniques; this skill is not certified against them.
Checked 2026-10-10. Reverify relevant product behavior when maintaining adapters.

- C4 context and selective diagram depth: https://c4model.com/diagrams
- Google SRE, implementing user-relevant objectives: https://sre.google/workbook/implementing-slos/
- OWASP ASVS, application verification requirements: https://owasp.org/projects/asvs
- AWS Well-Architected, operational/security/reliability/performance/cost/sustainability perspectives: https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html
- Agent Skills packaging/progressive disclosure: https://agentskills.io/specification
