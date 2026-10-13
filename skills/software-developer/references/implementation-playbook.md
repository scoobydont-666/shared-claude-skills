# Implementation playbook: select by changed boundary

These are engineering prompts, not a mandate to add every technology or test type.
Follow the actual repository's supported versions and canonical commands.

## Code-reading and debugging method

Trace entrypoint -> routing/configuration -> handler -> dependency/data operation
-> consumer response. Identify authoritative versus generated/exported copies.
Inspect call sites and negative tests before altering a helper. For suspected
behavior, write down observation, hypothesis and the smallest discriminating test.
A stack trace suggests a location, not necessarily the causal defect.

Confirm the baseline, environment and inputs. Minimize the reproduction without
removing the real boundary that fails. Preserve relevant logs with secrets removed.
Do not start by increasing timeouts, swallowing errors or disabling validation.
After a correction, demonstrate why the previous implementation fails and what
else the fix could affect. Label an incident workaround as mitigation.

## APIs and services

Define validation and authorization at the actual trust boundary, including
resource ownership/tenant scope. Specify error status and response shape, partial
success, pagination, deadlines and cancellation. Preserve compatible serialization
and old clients. Test invalid and unauthorized inputs alongside valid ones.

Use parameterized queries and bounded collections. Prevent inconsistent states
through real transactions/constraints rather than only application checks. Scope
idempotency to the logical operation and caller/tenant, compare request identity,
and define retention/in-progress/conflict semantics. Test commit-success followed
by response loss. Do not retry a non-idempotent effect blindly after timeout.

## Data and concurrency

Name the invariant and write authority. Reason about competing transactions,
lock order, stale reads, interrupted writes, duplicates, reordering and replay.
Use realistic database semantics for critical transaction tests; a SQLite fixture
cannot establish the behavior of an unrelated production database automatically.
Use barriers/controlled scheduling where feasible rather than arbitrary sleeps.

For schema changes test existing data, mixed-version behavior, backfill bounds and
repeated/partially completed migration. Separate expand, compatible use and later
contract. Verify backups/restores outside production for destructive transitions.
A schema downgrade is not the default answer when the app rollback fails.

## Filesystems, automation and shell

Resolve the exact authorized target through the existing executor. Lexical path
checks are not symlink, junction or mount protection. Preserve ownership, modes,
important hidden files and unrelated work. Use transactions/atomic replacement
where supported; account for crash consistency and concurrent writers.

Quote data arguments; prefer arrays/argv over assembled shell. Understand exit
codes and pipe behavior rather than assuming `set -e` catches everything. Avoid
`eval`, blanket permission changes, root-disk fallbacks and destructive wildcards.
Bound external commands and descendant lifetime through the approved execution
path. Test first apply, harmless repeat, partial failure and safe recovery using
real disposable filesystem fixtures where practical.

## UI, TUI and CLI

Trace the real operator/user journey. Cover loading, empty, error, cancelled,
partial and success states. Preserve keyboard/controller/accessibility behavior
where supported. Avoid misleading success toasts, silent failures and blocking
long operations on the UI thread. Present actionable failures and consistent
machine-readable output/exit codes for automation.

Validate server-side despite client controls. Test the UI against the real
interface contract; a mocked happy page is not end-to-end evidence. Preserve
state and recoverability across interruptions. Screenshots can support visual
review but cannot prove authorization, keyboard access or data integrity.

## Language-specific watch points

| Stack | Inspect rather than assume |
|---|---|
| Rust | Ownership/lifetimes, error propagation, panic paths, Send/Sync assumptions, cancellation safety, unsafe blocks and feature combinations. Use locked dependencies and the repo's fmt/clippy/test commands. |
| Python | Supported interpreter, isolated dependency environment, type/schema boundaries, async blocking, context-manager cleanup, exception scope and import side effects. Do not install into system Python to hide a dependency problem. |
| TypeScript/JavaScript | Runtime validation beyond static types, rejected promises, cancellation, package/lock consistency, client/server boundaries and test discovery. |
| Go | Context propagation, error wrapping, goroutine/channel lifetime, resource cleanup and race tests where supported. |
| Shell/PowerShell | Native exit-code handling, quoting/literal target semantics, privileges, WhatIf/dry-run limits, encoding, pipeline failures and OS-specific paths. |

Do not guess current library APIs, action SHAs or kernel/runtime support. Read the
installed/locked version and primary documentation; route missing research to
an authorized source. Language tools are evidence only when actually executed.

## Test design and evidence

Choose the smallest tests that distinguish required from broken behavior. Unit
checks isolate a function; integration checks verify a real boundary; consumer
checks prove the user path. Property/fuzz tests help explore parsers/state spaces;
load/soak tests address resource and temporal behavior. No single test type proves
all of them. Document representative inputs and what remains uncovered.

For a critical guard, test both refused and permitted cases. Check malformed,
missing, duplicate, oversized, stale, cross-tenant and wrong-revision inputs where
relevant. Negative evidence must not disappear into a fallback success. A schema
validator is not an evidence authenticator; a signed record still needs a trusted
issuer and correct subject. Bind results to exact source and test configuration.

When a test is flaky, preserve its failures and diagnose timing, order, fixtures
or infrastructure. Quarantine only under the existing exception process with an
owner, deadline and replacement evidence as necessary. Never silently turn a
required failure into an advisory check. Verify expected test collection/counts.

## Performance without correctness regression

Measure before optimizing: workload mix, hardware, toolchain/dependencies,
configuration, warm/cold state, throughput, latency distribution and resource use.
Keep correctness/quality checks alongside speed measurements. Vary the suspected
bottleneck rather than comparing unrelated configurations. Consider tail latency,
peak memory, contention, cleanup and cache invalidation, not only average speed.
A microbenchmark improvement is not an end-to-end service claim.

## Security and observability

Use least privilege and verified trust boundaries. Avoid unsafe deserialization,
unbounded parsing, command injection, authorization gaps and leaking secrets in
errors or traces. Apply relevant ASVS criteria and supply-chain controls without
claiming universal security from a scan. Choose audit events that answer who did
what to which authorized resource; redact values and bound cardinality/retention.

For harness hooks, prefer bounded deterministic local checks. No model/network call
on the routine blocking path unless the accepted policy explicitly requires it.
Separate absent evidence, denial and success. Test malformed payloads, process
failure, timeout, ignored config and bypass routes in the actual runtime before
claiming enforcement. A local test of JSON output is not that runtime test.

## Review and maintenance

A useful PR explains intent, changed behavior, evidence and remaining risk.
Answer each blocking review finding with a fix or evidence-based rebuttal. Do not
substitute cosmetic cleanup for correctness. Keep the branch scoped and avoid
editing another worker's tree. Record residual work durably through the existing
tracker; don't invent a second status database.

Primary references for maintenance: OWASP ASVS https://owasp.org/projects/asvs ;
Agent Skills https://agentskills.io/specification ; Claude hooks semantics
https://code.claude.com/docs/en/hooks . These are reference inputs, not proof the
local runtime or implementation conforms. Checked 2026-10-10.
