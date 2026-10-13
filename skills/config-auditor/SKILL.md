---
name: config-auditor
description: "Audit configuration, project instructions, registries and skill references for contradictions, stale claims and missing dependencies."
---
# Configuration coherence audit

Read the user-named repositories and applicable project instructions. Inventory configuration files and their consumers before comparing them. Never assume a global configuration applies to every project.

For each claim, record its file/line, scope, expected consumer and evidence date. Compare declared values with the actual source or an authorized read-only runtime query. Separate desired state, observed state and historical notes.

Check:
- Conflicting toolchain versions, endpoints, feature defaults, permissions and installation paths.
- References to absent files, skills, commands, services or generated artifacts.
- Duplicated settings whose precedence differs between clients.
- Stale examples, retired components, unsupported model or price claims.
- Secrets and personal information in sample configuration or logs.

Classify each finding as confirmed contradiction, stale claim, missing dependency or unknown. Do not resolve unknowns by choosing the newest-looking file. Identify the owner and authoritative source.

Propose the smallest correction, preview its consumers, and edit only authorized paths. Verify the rendered configuration and the consuming path after a change. Report findings with evidence and unresolved questions; unavailable runtime access is not a passing audit.
