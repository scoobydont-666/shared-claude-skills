---
name: skill-updater
description: "Review and update skills for staleness, duplication, unsafe instructions, broken references and missing dependencies with reproducible validation."
---
# Skill maintenance

Inventory the actual installed skill directories and their source revisions. Read project instructions and installation policy. Do not treat a historical inventory or a memory entry as the current catalog.

For each skill assess its trigger, scope, source provenance, supported tools, local references, executable helpers, network/service dependencies and overlap. Verify version-sensitive claims against current primary documentation. Treat prices, CVEs and benchmark claims as dated evidence.

Classify KEEP, UPDATE, CONSOLIDATE, RETIRE or INVESTIGATE with a concrete reason. A skill mentioning infrastructure is not automatically internal; the dependency on a specific private environment is what matters.

Prepare changes in an owned branch. Preserve license/attribution and useful references. Replace private service assumptions with documented optional dependencies or remove the component if its purpose is internal. Do not replace a hostname and claim the workflow is portable.

Validate YAML, links, bundled resources, install paths, secret/internal-reference scans and executable behavior. Forward-test substantial workflow changes on a representative disposable task. Skill files describe behavior; they do not install hooks or enforce access control.

Record the removal/replacement mapping and manual migration steps. Never recursively synchronize with deletion into a user's skill directory; preserve local customizations and require explicit path review before removing obsolete installations.
