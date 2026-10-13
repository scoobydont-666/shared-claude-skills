# Public export review and provenance

Source inventory: revision `6d18ef344325de74887df91821af33b2d2a4e529`, canonical `skills/user/` and `claude-code/hooks/` trees. Public baseline: `25bc5959708e54cebb4abece14aecedd5e4b6283`. Source snapshots are inputs for curation, not automatic publication or deployment evidence.

## Selection and changes

The explicit allowlist is [catalog.json](../catalog.json). Canonical source skills were compared with the existing public catalog. Generated/exported duplicates, third-party vendored packs and archived workflows were excluded. The current public tax skill is retained because it contains newer evidence and reconciliation controls.

Private services, identifiers, contacts, machine paths, incident narratives and model-price assumptions were removed. Reusable source concepts that depended on missing local executors were recast as documented procedures. No unverified execution helper is advertised as installed.

Corrections made during curation include unsafe sandbox credential mounts, broad sudo examples, filesystem string-prefix containment advice, scanner failure masking, fictitious model-quality formulas, and branch-triage guidance that equated nonempty diffs with shippability. These are public adaptations, not fixes applied to the private source repository.

The five exported advisories derive from the stash, PR-size, inline-Python, pre-edit conventions and shell-safety hooks. Their public forms have no private state/logging dependency, bounded inputs, explicit event wiring and no authorization effect. Private enforcement gates with pending fixes/dependencies were excluded.

## Verification scope

Canonical commands are in the README and GitHub workflow. They validate metadata, local references, catalog membership, hook wiring, public runner selection, content patterns, installed-command fixtures, hook behavior and the receipt ledger. Secret scanning covers the candidate files and available Git history. Negative controls verify that missing or out-of-skill resources, detectable private content, altered hook matchers/events and private runners in additional workflows are rejected.

Tests use disposable directories and repositories. Actual interactive Claude Code activation remains a consumer installation check; fixture success is not a claim that hooks are enabled on anyone's machine. Heuristic content scans are not exhaustive privacy or security audits.

## Recorded local evidence

On 2026-10-13, the package tests passed (15), the receipt-ledger tests passed (20),
and catalog/reference validation and public-content scanning passed. Gitleaks
8.30.1 found no secrets in the candidate and the full fetched public history
(the scanner reported 18 scanned commits; the baseline has 20 reachable commits). This is a scoped scan result, not a claim that historical public content
has been erased. Suppressed Bash debug logging was checked under strict error
handling after correcting its unintended failure exit.

Two independent reviewers inspected skill guidance and executable packaging.
Their findings drove corrections to stale Python examples, unsafe C/security
recipes, private resume examples, missing resource dependencies, hook error
handling and validation coverage. Five instruction-following scenarios exercised
exact-head review, branch deletions, hostile-code isolation, MCP path containment
and fully blocked plan handoff; these were reasoning tests, not live deployments.
Final source identity and hosted CI results belong in the PR's evidence record.

## Maintenance and recovery

Public CI runs on GitHub-hosted runners with read-only repository permissions and no persisted checkout credential. Private repositories use private runners under their own isolation policy. No private repository workflow is changed by this export.

Review future imports individually and preserve bundled licensing and attribution. Do not copy source settings, logs, private topology or vendored packages wholesale. Revert the public change through an ordinary reviewed Git revert if needed; migrate local installations using their backups. No public history rewrite is part of this change.
