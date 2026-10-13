# Architecture handoff template

Fill only applicable sections. A local decision can fit in a paragraph; a risky
integration needs the corresponding evidence. This document is a proposal, not
approval, executable instructions, or a trusted evidence receipt.

## Decision summary
Problem, stakeholders, decision owner, recommended option, key constraint,
material tradeoff, and why the smallest viable alternative is insufficient.

## Current and desired state
Name inspected repositories/revisions, relevant implementation/configuration and
consumers. Distinguish source from deployment observations. Describe context,
component/data boundaries and normal/failure flows. Mark observed, assumed and
unknown statements; link current evidence.

## Requirements and verification map

| Requirement/AC ID | Observable behavior/quality target | Contract/component | Verification and evidence | Owner |
|---|---|---|---|---|
| Replace with actual ID | Input/failure/workload -> measurable response | Exact boundary | Test, measurement or review required | Actual owner or unassigned |

## Alternatives and decision record
Baseline/reuse, minimal change and credible alternative. Show hard constraints,
advantages/costs, uncertainties, choice and reconsideration trigger. Include
compatibility, security, operating burden and eventual exit.

## Contracts and compatibility
Provider/consumer identities and versions; request/response/event schema;
authorization/data ownership; errors/limits/deadline/cancellation; retry and
idempotency; ordering/concurrency; old/new compatibility and deprecation.

## Risks and operations
Threat and failure scenarios -> mitigation -> detection -> verification -> owner.
Capacity/cost assumptions with units and ranges. User-relevant health objectives,
configuration/secrets, backup/restore, maintenance and recovery constraints.

## Work slices

| Slice | Target and owned scope | Depends on | End-to-end acceptance | Evidence required | Recovery/rollback | Role |
|---|---|---|---|---|---|---|
| Replace | Repository/component/files | Real prerequisite or none | Working behavior | Relevant tests and review | Data/version limits | Developer/operator |

Keep code implementation, release, deployment and verification separate. Name
mixed-version ordering for multiple repositories. A slice must not require a
coordinated unsafe switch hidden inside a broad task description.

## Questions or bounded spikes
For each: decision affected, hypothesis, fixture/workload, cost/time bound,
accept/reject criteria, owner and safe cleanup. Do not record predicted outcomes
as observed evidence. Supply a useful partial design while blocked questions
remain explicit.

## Handoff
Design status; remaining decisions; next owner/action; evidence references;
independent review pending/completed with real authenticated scope. For a typed
harness, inspect and validate against the receiving tool's installed schema;
this package does not supply or assume a particular integration contract.
The named architect returns content; the designated writer persists it.
