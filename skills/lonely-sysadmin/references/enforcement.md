# Sysadmin 101: shared harness enforcement contract

Use this reference when implementing or reviewing the harness. It defines required
behavior, not a claim that every adapter currently provides it. The skill is
doctrine; hooks expose the decision; the shared policy evaluates evidence; the
protected executor enforces permissions, target identity and resource bounds.
User interfaces display these results and are not another policy authority.

## Evidence and authorization

Reuse the existing operation taxonomy, ownership/lease controls, authorization
mechanism and evidence store. Do not create another classifier, database, daemon,
or model call on the blocking path. A hash identifies bytes; it does not
authenticate their producer. A seat's JSON assertion, timestamp, checkmark or
exit-zero report is not an independent observation.

Bind relevant evidence to host, OS, effective account, environment, exact resolved
target, device/volume or service identity, operation, artifact/config revision,
actor/lease, and policy revision. Have the protected executor revalidate changing
identity/version immediately before mutation. A newer mount, changed target,
expired grant or different revision invalidates the affected evidence. Unknown,
failed, stale, missing and unsupported are never silently converted to absent,
empty, healthy, safe, or authorized.

Missing prerequisites block the affected mutation, with a precise reason and the
next safe check. They do not block authorized diagnosis or require another human
approval when existing scope already covers the action. Policy failure cannot
grant permission. Preserve existing safeguards while qualifying new decisions in
observation; label observation honestly and keep it distinct from enforcement.

Sanctioned workspace roots come from current operator/site policy. Preserve a
positive control for normal owned worktree creation, fetch/checkout, edits and
bounded tests there. Match the particular risky operation and resource condition;
do not deny a whole approved workspace or demand repeat approval for routine work.

## Rule map

| Rule | Before mutation | After execution / completion | Required refusal or regression fixture |
|---|---|---|---|
| 1: identity | Resolve machine, OS, account, environment, path/link/mount/device or service; bind authority and ownership. | Read back the same identity and resulting version. | Wrong host, changed symlink/junction, mount or service identity cannot reuse evidence. |
| 2: cheap checks | Require the applicable safe diagnostics; preserve unavailable observations as unknown. | Record observed findings and coverage limits. | Access-denied inventory causes zero deletion; available safe checks still run. |
| 3: storage | Require expected application-data volume and layout, and measured headroom before admitting writes/jobs. | Verify actual backing storage and growth/side effects. | Missing data mount or changed drive identity never falls back to the OS volume. |
| 4: exact cleanup | Bind the exact reviewed inventory; reject empty/broad/escaped targets. Preview only supported semantics. | Compare actual removals with that inventory. | Wildcard metacharacters in an exact Windows name are handled literally; forced deletion cannot replace preflight. |
| 5: recovery | Important-data destructive changes require current backup coverage plus successful relevant restore evidence outside the affected system. | Preserve recovery evidence and verify any rollback/restoration. | Backup exit zero with a failed restore blocks destruction; stale rollback cannot overwrite new data. |
| 6: protected data | Include relevant hidden files, key material, configuration and permissions in target/backup coverage. | Compare names, counts, hashes and permissions without exposing values. | Hidden/private/recovery data is not discarded by age or appearance; no automatic key regeneration. |
| 7: least rights | Use scoped effective privileges; verify the specific elevation grant where required. | Verify exact ACL/owner changes and unrelated access. | Broad recursive/full-control or security-disable fixes fail; ordinary authorized work gains no new prompt. |
| 8: supported installation | Bind approved source, version, installer, shared-component impact and rollback. | Verify installed bytes/version and consumer behavior. | An unreviewed elevated downloaded script or unmanaged binary move does not satisfy installation evidence. |
| 9: idempotence | Compare desired/current state; reconcile uncertain outcomes before retry. | Independently observe writes, restarts, rotations and duplicate external effects. | Second apply produces no unnecessary effects; timeout after creation never blindly creates a second resource. |
| 10: coordination | Preserve work; use the existing writer/lease fence. Verify downtime authority and alternate access for access-changing operations. | Reconcile interrupted/concurrent work; preserve newly written data. | Stale writer, conflicting maintenance or untested alternate access cannot pass. |
| 11: verification | Define the consumer acceptance checks for the exact resulting revision. | Require executed readback, consumer checks and preservation checks before verified success. | Process/port/exit-zero alone cannot pass a failing user request. |
| 12: durable repair | Use the maintained source/configuration and a bounded rollout/recovery plan. | Record change/recovery provenance, capacity/health/backup checks and regression coverage. | A mitigation without the lasting change cannot be labeled permanent repair. |

Resource admission must count existing work and include memory, swap, process
count, storage identity/headroom and the cost/bounds of new work. A healthy
preflight cannot prevent an unbounded recursive process tree. Enforce per-seat or
per-operation resource and lifetime limits at the execution boundary, including
descendant cleanup; state which remote execution routes remain uncovered.

## Outcome and qualification

Keep outcomes distinct: no-change verified, changed but unverified, verified,
failed, unknown outcome, and mitigated. An agent may stop honestly with missing
verification or a blocker. Completion control must be durable; a Stop hook may
offer a bounded reminder but must not trap the agent in an endless retry loop.

Qualify the actual consuming adapter and executor, not just a library mock.
Exercise wrong/stale targets, interrupted writes, concurrent owners, protected
data, failed collectors, hook timeouts, retry exhaustion and ordinary low-risk
positive controls. Check harmless reapplication in disposable environments; do
not repeat destructive production operations to prove idempotence. Windows
collector behavior requires Windows qualification; Linux path tests do not prove
Windows junction, Registry, ACL or UAC behavior.

For each rule/consumer report source revision, installed revision, loaded
revision, observed/enforced mode, executed evidence and remaining gaps. A
machine-readable map or a successful package export alone proves none of these
runtime properties.
