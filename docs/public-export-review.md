# Public export review and provenance

Reviewed source inventory: revision `6d18ef344325de74887df91821af33b2d2a4e529`,
canonical `skills/user/`, `claude-code/hooks/` and `claude-code/agents/` trees.
The initial portable export was integrated at
`05092cf040553a167811a081389ec9789c5a2d08`; that is the base for the persona
and documentation update. `catalog.json` retains the original pre-curation
`public_baseline` for provenance. Source snapshots are curation inputs, not
deployment evidence.

## Current package and selection

The [catalog](../catalog.json) explicitly lists 43 skills, nine personas and
five advisory hook bindings. Generated/exported duplicates, personal-biography
and project-specific personas, vendored third-party packs, private fleet tools
and retired workflows are excluded. The public tax preparation skill preserves
its evidence and reconciliation controls.

Private services, identifiers, contacts, machine paths, incident narratives,
local dispatch contracts and fixed model-price assumptions were removed.
Reusable concepts with missing private executors were recast as procedures.
No execution helper is advertised as installed merely because a prompt names it.

The eight persona filenames preserve the reusable source role names. Their
public instructions are self-contained, with explicit built-in tool allowlists,
inherited model selection, default permission requests and bounded turns.
Architecture/research/design/audit roles return text artifacts without shell or
file-write tools. Implementation and operations roles explain the limits of
shell access. Persona identity does not confer credentials, permission or
independent-review status. See the [installation and capability guide](../personas/README.md).

Descriptions were refreshed across the complete skill catalog, removing long
trigger lists and claims of automatic protection. README skill/persona tables
are generated from the installed metadata and checked for drift. Names and
bundled skill paths remain stable; catalog schema 2 adds persona membership.

## Corrections during adaptation

Initial skill/hook curation corrected unsafe sandbox credential mounts, broad
sudo examples, filesystem string-prefix containment, scanner failure masking,
unsupported model-quality formulas and misleading branch-readiness shortcuts.
These public adaptations did not modify the private source repository.

Persona adaptation removes fictional career/credential claims, private-service
fallback probes, internal approval annotations, blanket severity assignments
based on code style, and assertions that all data changes have a one-command
rollback. Severity depends on evidence and reachability; recovery limits remain
explicit. Publication does not activate personas or hooks on a user's machine.

## Verification and evidence

The README and GitHub workflow contain the canonical commands. They check:

- Skill and persona membership, metadata and local dependency closure.
- Standalone persona files, read-only role tool limits and permission defaults.
- README description/count synchronization and local documentation links.
- Hook event wiring, bounded-input behavior and installed-command fixtures.
- Public runner selection, heuristic public-content patterns and receipt ledger behavior.

Negative controls reject missing resources, unreviewed personas, private tools,
permission escalation, mutation tools in read-only roles, stale descriptions,
broken documentation links and private runners. Tests run in disposable paths.
Gitleaks scans available history and candidate files in CI. Its results and the
independent reviews must be tied to the final PR head, not copied from an older
candidate. See [pull requests](https://github.com/scoobydont-666/shared-claude-skills/pulls)
and [workflow runs](https://github.com/scoobydont-666/shared-claude-skills/actions)
for revision-specific evidence.

The environment used for this update does not have an interactive Claude Code
client. Metadata, installation examples and role behavior can be checked here;
actual discovery, model selection and permission enforcement remain consumer
installation checks. Prompt guidance and heuristic scans are not enforcement
or a guarantee that every private detail is absent.

## Historical secret and privacy audit

On 2026-10-13, a separate audit of base revision
`05092cf040553a167811a081389ec9789c5a2d08` fetched both published branches and
five PR refs: 50 reachable commits and 269 unique Git file objects. Gitleaks
8.30.1 and TruffleHog 3.99.2 reported no credential candidates across extracted
content and available GitHub surfaces. Positive controls confirmed token-pattern
detection; candidate credentials were not sent to external services for validation.

The privacy review found expected author attribution and older personal/internal
context in history, an older branch and PR discussions. Six available CI logs
were scanned; 34 older logs were unavailable. These are scoped historical
findings, not results for later commits. Current-file sanitization does not erase
old public refs, metadata, discussions, external clones or caches. No history
rewrite is part of this package update.

## Maintenance and recovery

Public CI uses GitHub-hosted runners with read-only repository permissions and
no persisted checkout credential. Private repositories use private runners under
their own isolation policy. This update changes no private workflow.

Review imports individually and preserve any bundled licensing/attribution.
Repository-owned adaptations use the existing MIT license; third-party content
requires a provenance review before import. Do not copy settings, logs, private
topology or vendored packs wholesale. Revert a public change through an ordinary
reviewed Git revert. Recover local installations from their backups, preserving
unrelated skills, agents, hooks and settings.
