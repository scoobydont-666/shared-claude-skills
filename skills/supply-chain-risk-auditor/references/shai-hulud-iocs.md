# Handling package-worm indicators

For Shai-Hulud or another named incident, fetch the incident-specific current indicator set from primary advisories before scanning. Record indicator provenance and scope. No historical package/version list in this repository is authoritative.

Inspect the exact resolved and installed packages, relevant lifecycle scripts, CI workflow changes, artifacts and execution logs. Do not prune the installed dependency directory from the scan while claiming to inspect it. Search without executing package scripts; preserve timestamps and hashes where required by the response process.

Distinguish exact artifact-digest matches, code/behavior matches and weak filename/string heuristics. Validate a suspected finding in an isolated analysis environment. Never upload private dependencies, source, credentials or logs to an external scanner without scoped authority.

If exposure is confirmed, identify the secrets and systems reachable at execution time and follow the authorized containment/rotation/recovery plan. A generic string match is not authority to revoke all credentials or isolate unrelated systems.

For future builds, review package-manager-specific controls for lifecycle scripts and lockfile integrity against the exact installed tool version. Flags that expose script output do not bypass or create an install-script allowlist. Test controls using harmless positive/negative fixtures before claiming enforcement.
