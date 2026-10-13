---
name: supply-chain-risk-auditor
description: "Assess dependency provenance, maintenance, release trust and exposure to known compromises using authoritative evidence and exact installed versions."
---
# Supply-chain risk audit

Inventory direct and transitive dependencies from actual lockfiles, installed artifacts and build inputs. Record package ecosystem/name/version, source URL, integrity/provenance, execution phase, permissions and reachable consumer. Include CI actions and install scripts.

Use the available repository connector, package registry metadata and current vendor advisories. A missing `gh` binary need not block other authorized evidence gathering. Do not install or execute a suspicious package to inspect it.

Assess maintainer/release access controls, provenance, ownership transfers, unusual release changes, supported versions, response to verified vulnerabilities and dangerous capabilities. Popularity, anonymity, number of maintainers or raw CVE counts are signals for investigation, not proof of maliciousness or a standalone high-risk verdict.

Match advisories to exact affected versions and artifact digests. Check whether affected code ran and what credentials/data it could reach. Follow [incident verification](references/known-compromises.md) and [indicator handling](references/shai-hulud-iocs.md). A name/string match alone is not confirmation; a missing match is not proof of safety.

Write a report using [the report template](references/results-template.md). Include the complete assessed inventory or a coverage summary so omitted packages are not interpreted as safe. Distinguish confirmed exposure, risk needing investigation, no finding within scope and unavailable evidence.

Recommend proportional fixes, verified supported alternatives and a migration/test plan. Preserve evidence and follow the authorized incident-response process before disruptive containment, credential rotation or reinstall. Do not prescribe a stale 'safe version' from a static skill file.
