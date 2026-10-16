---
name: fast-ci
description: >-
  Design, repair and optimize fast, resource-efficient CI on GitHub and local
  multi-agent hosts. Use for slow builds, runner queues, repeated tests, cache
  misses, excessive parallelism, flaky reruns and affected-test selection. Plan
  the smallest sufficient checks and keep missing or failed evidence out of green CI.
---

# Fast CI: smallest sufficient proof, least wasted work

**Make trustworthy feedback arrive sooner. Do not make green cheaper by making it false.**

Use alongside `ci-cd` and `software-development-lifecycle`; keep their delivery,
security and two-independent-review requirements. This is the performance
specialist, not another scheduler, permission gate, release system or test runner.

## Operating contract

For every CI change, name the protected decision, candidate/integration identity,
owner, canonical repository command, affected components/consumers, required
checks, placement, time/CPU/memory/disk/process budget and evidence destination.
Read the live main branch, relevant open PRs and current runner controls before
changing them. Preserve other agents' branches, worktrees and active build jobs.

Success means lower **time to useful, correct feedback** and lower total resource
cost per qualified change, with unchanged necessary coverage and no new host
interference. Optimize queue + setup + critical path + evidence publication,
not just the duration printed by a test runner.

## 1. Check cheap things first

1. Inspect the first causal failure, source identity, working-tree state, runner
   availability and existing evidence. Do not start by rerunning the whole suite.
2. Run syntax/format/schema/manifest checks and the nearest regression test.
   Stop dependent expensive work when an earlier prerequisite fails. Preserve
   independent diagnostic checks and publish truthful failure evidence.
3. Expand through affected components and reverse consumers. Qualify the full
   candidate where risk or policy requires it, then hand the same evidence to
   both reviewers. Independent reviews do not inherently require two identical
   builds, but one test result is never two independent code reviews.

Targets to tune after measurement, **not guarantees or waiver thresholds**:

| Lane | Intended feedback | Scope |
|---|---|---|
| Edit loop | roughly 5–30 seconds | Cheap format/syntax and narrow regression checks. |
| Local candidate | roughly 30–120 seconds warm | Affected units and changed boundary contracts. |
| PR fast lane | p95 about 5 minutes warm; 10 minutes cold | Mandatory controls plus affected suites and evidence. |
| Deep/release/hardware | Explicit workload-specific budget | Broad regression, matrices, mutation/load/recovery and artifact qualification. |

A required expensive test stays required. Establish a measured timeout above
ordinary p95 with justified headroom; a timeout is failure/blocked evidence,
not an optimization. Never label a narrow test command full-preflight success.

## 2. Select deterministically; fail wide, not empty

Use a reviewed component-to-suite map plus reverse-dependency relationships.
The selector and expected job set must come from the trusted base/protected
harness, not the candidate's convenient replacement. A model may propose a map;
it may not authoritatively waive tests based on prose or semantic similarity.

Include both old and new paths for renames, deletions, generated outputs and
shared consumer effects. Compare the actual integration candidate to the proper
base. Missing/shallow history, truncated diff, unmapped paths, uncertain impact
or missing policy means a conservative full suite or a visible block. An empty
diff observation is not permission to skip everything.

Treat workflows, hooks, agent instructions, schemas, build scripts, generators,
lockfiles, toolchain changes, authentication and shared libraries as sensitive.
They are not harmless documentation. Plain documentation may select only its
checks plus mandatory controls through an explicit map, not a blanket `.md` rule.

Keep a stable required aggregate check. Select within the workflow; do not make
required workflows disappear using top-level paths. Support merge-group events
where the repository uses a merge queue. A skipped job may look successful to
GitHub: the aggregate must require the complete planned set, genuine exit
statuses and test counts. Missing, cancelled, timed-out, unexpected-skipped and
zero-collection expected tests must not become green.

## 3. Local hosts come first: bound the aggregate

**Agent concurrency is not build concurrency.** Many model sessions can share an
inference endpoint; that does not authorize every agent to launch an all-core
compiler or full test suite simultaneously.

Use the host's own resource allocator or lock (for example a lease file, a
cgroup slice or a CI runner concurrency limit) to obtain an isolated CPU build
slot. Respect live ownership and its atomic admission/lease mechanism. Before admission use a fresh
observation of effective CPU quotas/cpusets, available memory, swap/pressure,
free bytes AND inodes on the actual workspace/cache mount, disk latency, process
limits and other active CI allocations. Unknown capacity is DEFER, not idle.

Budget the entire tree: simultaneous jobs, shards, compiler workers, test-worker
processes and each test's native/BLAS thread pools. A starting bound is:

```text
all active CI allocations + requested allocation + protected headroom <= CI ceiling
worker count <= allocated CPUs
peak build/test memory + protected free-memory floor <= observed available memory
scratch expansion + protected disk floor <= observed free bytes
```

The ceiling is derived by the existing owner from real host/container limits;
it is not `nproc` and is not the machine's advertised core count. Peak compiler
memory is measured, not inferred from CPUs. Account for overlapping phases;
do not multiply sequential phases as if they always overlap. Keep admission
checks and lease creation atomic. A passed preflight alone is not a reservation.

Default to CPU-only, bounded jobs. Protect interactive responsiveness, inference
TTFT and resident model memory. GPU tests require the existing physical-GPU
reservation plus explicit hardware scope; do not seize an inference GPU, unload
a model, reset a device or treat an unavailable GPU as permission for CPU fallback.
Do not spill failed private-runner admission to a different trust domain.

Keep a bounded queue and coalesce superseded candidate work. Fair scheduling and
aging must prevent a busy repository from starving others. Reserve the approved
release/deployment lane independently; ordinary CI cannot consume that reserve.
Do not invent a second queue or permanently pin capacity to fixed agent names.

## 4. Eliminate repeated work before adding workers

Use one canonical command set for local and GitHub execution. Invoke existing
repository entrypoints rather than adding a slightly different definition of
PASS. Batch edits into a validation epoch: cheap checks while editing; an
identified candidate before broad tests. Never mark a dirty checkout's result
as evidence for its clean HEAD. Untracked inputs need explicit input identity.

Dedupe only the same repository, source AND tested integration SHA, suite/harness
revision, policy, lock/dependency identity, toolchain/platform/configuration,
trust domain and required outcome. Share the existing custodied artifact/receipt;
do not make every agent rebuild it. New base, configuration or required evidence
invalidates reuse. Patch equivalence alone is not test or review equivalence.

Freeze review candidates through the repository's existing freeze process. New development
may continue elsewhere; do not repeatedly invalidate reviewers and CI by pushing
onto their fixed head. Cancel obsolete PR test runs, not active deployments,
migrations or uncertain backend operations. Retain all failed/cancelled attempts.

Run tiny checks in one process/job where setup dominates. Split a job only when
parallel execution reduces the measured critical path more than it adds queue,
checkout, bootstrap and artifact overhead. Use timing-balanced shards rather
than equal file counts; every selected test belongs to exactly one shard, with
necessary serial/resource-affinity groups kept together. Unknown timings get a
conservative estimate, not zero weight. Do not shard order-dependent tests.

## 5. Caches are accelerators, not proof

Use native tool caches first. Prefer measured fast local storage for hot compiler
and dependency I/O; use shared storage for immutable artifacts where appropriate.
Do not force random compiler I/O through a shared filesystem merely for dedup.

| Stack | Safe first optimizations |
|---|---|
| Rust | Reuse the admitted job's target within its validation epoch; bound `CARGO_BUILD_JOBS` and test threads separately; use locked inputs; target affected packages/features before required full preflight. Measure incremental and compiler-cache behavior instead of enabling every cache. |
| Python | Resolve/pin once; reuse a job-private environment for compatible steps; use the existing dependency cache; target mapped tests; explicitly cap xdist and native numerical thread pools. Do not install pytest again in every step. Preserve intentionally distinct dependency environments. |
| Go | Reuse native module/build caches within the same trust domain; budget package parallelism, `GOMAXPROCS` and test parallelism together; select affected packages before required broad tests. |
| C/C++ | Bound compiler/linker concurrency; use configured ccache/sccache where already qualified; retain dependency-correct incremental builds; never issue bare `make -j`. |
| Node/containers | Use lockfile-frozen installation and native content/layer caches; bound test-worker and BuildKit concurrency; keep immutable artifact provenance. |

Partition writable caches by trust domain, repository where necessary, architecture,
toolchain, relevant flags/features, dependency locks and build mode. Do not share
one mutable Cargo target directory between unrelated concurrent worktrees.
Dependency-download caches and output artifacts have different validity rules.
A lock-keyed compiler cache can still contain candidate-produced bytes.

Untrusted jobs must not write cache/artifact namespaces later trusted for releases.
Never cache secrets, credentials or a populated shared agent home. Treat cache
miss as ordinary; verify the real build/test outcome after restore. Measure hit
rate, restore/save time, transfer bytes and net benefit. Schedule a clean-build
control to detect poisoned or incomplete inputs.

Cleanup requires owner, live-lease exclusion, explicit allowlisted cache root,
retention/watermark policy and cheap checks. No blanket `cargo clean`, `git clean`,
`docker system prune`, recursive deletion or killing another agent's build to
make CI faster. Stop admission under pressure; use the existing maintenance path.

## 6. GitHub placement and workflow shape

**Public repos: GitHub-hosted runners. Private repos: approved private runners.**
Visibility and trust are separate. Private untrusted code needs a qualified
untrusted-code private sandbox; absent one, block it. Runner labels alone are
not isolation. Ordinary jobs get no production credentials, Docker socket,
shared agent home or unrestricted host network. Keep protected promotion
identities separate. Do not execute PR code in a privileged trigger context.

Use minimal token permissions, reviewed SHA-pinned external actions, locked
inputs and bounded job/matrix concurrency. Cancel superseded PR work with groups
scoped to repository/workflow/PR; keep post-merge evidence and deployments out of
that cancellation group. Avoid full duplicate branch-push and PR pipelines
proving exactly the same property; keep post-merge integration checks where the
subject differs. Do not trigger broad jobs merely for a metadata-only PR edit.

Bootstrap once per compatible job; keep cache/checkout/action overhead visible.
Use conditional jobs and a real aggregate, not `continue-on-error`, `|| true` or
an unconditional final success to manufacture green required checks. Use typed
action inputs or environment variables; never interpolate untrusted PR text into
shell code. A queued or non-started job is not a code failure and not success.

## 7. Diagnose once; preserve evidence

Classify the first cause as product, test, infrastructure, capacity, selection or
policy. Repair that cause. Retry only identified transient faults with a small
explicit limit and retained attempt records. Do not erase a failed test by
rerunning until green. Quarantine needs an existing authorized exception with an
owner, expiry, risk and replacement evidence; no self-issued waiver.

Use the existing observability pipeline to record queue/setup/build/test/evidence
p50/p95, CPU-seconds, peak RSS, I/O and cache bytes, selected/collected/executed/
failed/skipped counts, retries, cancellations, infra failures, cache net savings,
and interference with interactive and inference service levels. Compare cold and warm
runs separately on equivalent inputs/hardware, including all failed attempts.
Do not equate a local subprocess cleanup with confirmed remote cancellation.

## Executable package and invocation

`scripts/fast_ci.py` has no third-party runtime dependencies:

- `plan`: affected suites, reverse consumers, prerequisites, fail-wide fallback,
  placement requirement and a full-context plan identity.
- `fit`: resource/headroom arithmetic over fresh existing-allocator observations.
  FIT explicitly still requires an atomic reservation; it grants nothing.
- `shard`: deterministic longest-first placement for independent timed tests.
- `verify`: recompute the planned roster from trusted inputs and reject misleading
  job evidence. It validates consistency, not the authenticity of assertions.
- `hook`: bounded report-only PreToolUse/PostToolUse/PostToolUseFailure advice.
  Never launches tests, reads transcripts, persists commands or overrides gates.

Read [the harness contract](references/harness.md) before integration. The JSON
examples are **synthetic fixtures, not live policy, leases or measured capacity**.
Installing this skill does not register its `hook` subcommand; registering it in
your own settings is a manual opt-in. Run the regression tests from a repository
checkout, and run the planner from the installed skill directory:

```bash
python3 -I tests/test_fast_ci.py -v
python3 -I scripts/fast_ci.py plan \
  --policy examples/policy.json \
  --context examples/context.json
```

## Completion report

```text
Candidate / tested integration / policy / suite / harness identities:
Selected checks and exclusions with reasons:
Placement / actual resource limits / reservation evidence:
Baseline vs candidate: cold/warm p50/p95, CPU-time, peak RAM, failures:
Checks: PASS | FAIL | BLOCKED | NOT_RUN; exact evidence references:
Existing required gates preserved / independent reviews pending:
Source shipped / installed / loaded / exercised / host-qualified:
Remaining work / owner / rollback:
```

Do not claim a speedup until measured, or deployment because a PR merged.
