# Fast CI harness contract v1

## Boundary

This package supplies small deterministic functions to the existing harness,
not an executor, resource collector, scheduler, receipt signer, policy authority,
cache server or new canonical cross-repo ABI. Its JSON types are local adapter
contracts. They do not replace your host's reservations, lifecycle policy,
review receipts or delivery acceptance manifests.

The protected caller owns selection policy, complete change evidence, placement,
resource observations and collected test records. Inputs returned by a worker
must not be substituted for those protected inputs. A SHA-shaped field or a
content hash does not authenticate a statement. `verify` always explicitly emits
`evidence_authenticated: false` and `grants_merge_or_deploy: false`.

## Entry points

All commands use Python 3.10+ and standard-library modules. File inputs are
bounded to 128 KiB, JSON collections to 512 entries and nesting to 32. Duplicate
keys, nonfinite numbers, booleans where integers are required, unexpected fields,
invalid IDs/paths and malformed records are rejected. The POSIX process deadline
is two seconds after argument parsing; use a runtime-owned three-second timeout
as well. Native Windows deadline behavior requires its own qualified adapter.
Return codes: 0 = successful calculation (or report-only hook); 1 = DEFER,
FAIL or BLOCKED result; 2 = invalid/unavailable input. Never translate rc=2 to PASS.

### `plan --policy FILE --context FILE`

`fast-ci-policy/v1` contains jobs (`id`, `paths`, `needs`, `always`, `min_tests`)
and nonempty `global_paths`. At least one always-run control job is required.
`needs` describes both impact dependencies and execution prerequisites. A direct
change to a prerequisite selects its consumers transitively; a consumer change
adds its prerequisites without selecting unrelated sibling consumers merely
because they share a prerequisite. An always-run prerequisite selects dependent
jobs, so do not model a universal setup step as an impact edge unless intended.
Cycles, duplicate IDs and nonexistent needs are invalid.

Patterns use Python `fnmatchcase` against normalized repository-relative POSIX
paths. `*` can span `/`; this is not gitignore or GitHub paths syntax. Do not use
negated patterns. The collector emits both sides of a rename/deletion, validates
its Git source/base and confirms the diff is complete. `changes: null`, `[]`,
unmapped paths or global changes select ALL declared jobs. Non-PR events also
select the full declared job roster in v1. No implicit docs-only skip exists.
The package does not discover Git history or prove a caller's diff is complete.

Context binds repository, base/head/tested Git object IDs, visibility, trust,
event, platform, toolchain/dependency/suite/harness digests and changed paths.
Source and tested merge SHA remain separate. Changes are sorted for stable
identity. Plan identity includes the canonical context and policy digest plus
selection and placement. The caller verifies that declared suite/harness digests
match the actual invoked, custodied code. Hashes are not credential signatures.

Placement is a REQUIREMENT, not an automatically selected runner label:
public -> github-hosted; private/internal -> private-isolated;
private/untrusted -> private-untrusted-isolated-required. The last requirement
must block without a qualified private sandbox; never fall back to privileged
privileged shared execution or change repo visibility to obtain cheaper compute.

### `fit --capacity FILE --request FILE`

This is CPU-only arithmetic. Extra GPU fields are rejected; GPU admission stays
with the current physical-GPU authority. Capacity includes `host`, `generation`,
`observed_at`, effective CI `ceiling`, `protected` headroom, all `active`
allocations, current `free_memory_mb`/`free_disk_mb` and `pressure_ok`.

Resources are integer `cpu`, `memory_mb`, `disk_mb`, `pids`. Use MiB consistently
for the historical `_mb` field names. Effective whole CPU units are bounded by
the actual CPU quota/cpuset and CI allocation, rounded DOWN; less than one whole
unit cannot admit a worker here. No use of host core count alone. `pids` budgets
include subprocesses AND threads. No negative/zero requested resource or unlimited
timeout. Request workers must fit its CPU/pid budget; timeout is 1–7200 seconds.
Memory requests include measured per-worker/linker peaks, not just heap settings.

The allocator derives `pressure_ok` from its existing CPU/memory/I/O pressure,
swap, inode availability, disk latency, interactive responsiveness and inference health policy.
This module does NOT measure these values or choose their thresholds. Free memory
and disk are fresh actual observations; protected memory/disk amounts are also
minimum free headroom floors after admitting the request, intentionally
conservative. Missing, future or older-than-30-second observations cannot fit.

Under the EXISTING allocator transaction/lock: read generation and active leases,
collect/validate current pressure, calculate fit, revalidate generation, reserve
atomically, then invoke the existing sandboxed executor with enforced limits.
A generation race recomputes; it does not reuse a stale FIT. A lost release or
unknown cancellation retains capacity until reconciliation. Fit creates no lease,
lock, resource limit, process, authorization or side effect. Multiple callers
outside that transaction can all FIT the same space: that is NOT safe admission.

### `shard --timings FILE --count N`

Input is a nonempty list of unique independent test IDs and positive duration
estimates. Up to 32 shards, never more than test IDs. Place longest first into
the least-loaded shard, with deterministic ties. The result preserves every ID
exactly once. Timings affect placement, not which tests are necessary. Serial,
shared-fixture and hardware-affinity groups must be grouped by the existing
collector before this function. Missing timings require a conservative estimate
from that collector or an unsharded run; the function rejects zero durations.
The toy example is arithmetic, not a real CI performance benchmark.

### `verify --policy FILE --context FILE --evidence FILE`

Recompute the expected plan from protected inputs. Every selected job requires
one unique bound record; unselected or duplicate records are invalid. Bind the
full plan ID and artifact digest. Each record carries terminal status, exit code,
collected/executed/failed/skipped counts and duration. Require collected = executed
+ skipped and failed <= executed. A passed selected test job must execute at least
its declared `min_tests`; exit code must be zero. Failed jobs/failed tests/nonzero
exits produce FAIL; absent, skipped, timed-out, cancelled, unknown, empty expected
tests or missing exit codes produce BLOCKED unless another failure dominates.

These counts are a normalized schema: `executed` includes failed test executions,
not suite nodes or collection errors. Framework-specific collectors must validate
JUnit/TAP/etc., collection errors, expected test IDs, skipped-test policy and the
real process exit; this script does not parse raw logs or authenticate counters.
The minimum count catches an empty collection, not arbitrary test removal.
Do not replace existing test-selection or required-check controls with this check.

V1 accepts ONE terminal record per selected job and has no retry authorization.
The trusted collector must refuse a green replacement after a failed attempt
unless the existing explicit retry policy qualifies it, retaining all attempts
outside this packet. Do not feed only a cherry-picked final green attempt. No
result reuse is enabled by this module; the existing authenticated evidence store
remains the authority. Hash-shaped artifact refs are not byte or signature checks.

### `hook --event EVENT`

Three executable adapters accept the Claude envelope on stdin, only for Bash:
PreToolUse warns on recognizable unbounded parallelism, broad suites, destructive
cache commands and repeated environment bootstrap; PostToolUse and
PostToolUseFailure remind CI invocations to capture evidence and diagnose first.
Ordinary bounded pre-tool commands are silent. Regexes are advisory heuristics,
not a complete shell parser; wrappers, aliases and generated commands can evade
them, while quoted examples can warn. They do not implement security enforcement.

The hooks never execute supplied commands, fetch URIs, inspect transcripts, echo
payloads, create state files, invoke a model, rerun tests or return permission
allow/deny. Invalid input produces a fixed visible audit-not-completed message
with rc=0 to preserve report-only behavior. Process failures/timeouts are not a
successful audit. There are no Stop hooks or forced retry/continuation loops.

To opt in, add three hook entries by hand to your own settings: events
PreToolUse, PostToolUse and PostToolUseFailure; matcher `Bash`; timeout 3 seconds;
command `python3 -I "$HOME/.claude/skills/fast-ci/scripts/fast_ci.py" hook --event EVENT`.
Preserve every other hook/deny rule and do not overwrite the settings file. Register
each entry once; repeated installation must not duplicate invocations. Match actual
runtime tool names. Other agent runtimes do not consume Claude event JSON
automatically: their protected adapter must map the envelope, enforce input
and output deadlines and verify real invocation before claiming parity.

## Integration and qualification

The test file runs with `python3 -I tests/test_fast_ci.py -v`, needs no runner,
venv, package download or matrix, and is picked up by the repository's existing
unittest discovery. Defaults do not activate hooks or replace live
selection/admission. Qualify source -> installed -> loaded -> exercised ->
host behavior separately; merge is not deployment.

The synthetic examples must never be copied into a live allocator as capacity
or used as attested test evidence. They use fake identities and a deliberately
stale capacity timestamp. Standalone plan/evidence examples illustrate structural
consistency only. Produce live inputs through existing trusted collectors.

## Primary references (checked 2026-10-16)

- GitHub required checks and skips: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- GitHub concurrency: https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/control-the-concurrency-of-workflows-and-jobs
- GitHub secure runner/action use: https://docs.github.com/en/actions/reference/security/secure-use
- Cargo build/test environment controls: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo cache identity and directories: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Claude hook envelopes and registration: https://code.claude.com/docs/en/hooks

Current documentation does not prove the version installed on any given host.
