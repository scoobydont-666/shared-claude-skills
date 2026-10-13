---
name: ansible-hardening
description: Build and review idempotent Ansible security roles for host hardening, audit logging,
  firewall policy, service isolation and scoped privilege.
---
# Ansible hardening

1. Read the existing inventory, roles, supported OS versions and access policy. Identify the target host and authorized change scope before applying anything.
2. Establish current access, service health, configuration backups and a tested recovery route. Preserve a working administrative session during SSH/firewall changes.
3. Use the existing role layout: `defaults/`, `tasks/`, `handlers/`, `templates/`, `meta/`. Prefer fully qualified modules and explicit file ownership/modes.
4. Default privileges and network access to the minimum required. Never blanket-allow a subnet merely because it is local. Document each firewall source, destination, port and purpose.
5. Store secrets in the approved encrypted secret mechanism. Protect task output with `no_log` where necessary; do not expose secrets through check-mode diffs.
6. Preview with syntax validation, lint and `--check --diff` on a disposable representative target. Some modules cannot simulate changes; label that limitation.
7. Apply to an authorized canary, verify real consumer behavior and access, then expand under the rollout policy. Second apply must converge without unnecessary restarts.

## Controls to consider

- SSH: explicit administrative principals, key authentication, tested recovery.
- Firewall and intrusion prevention: limited rules, reviewed exclusions, log/alert delivery. Verify the combined firewall outcome when multiple tools manage it.
- Audit: monitor privilege, service and authentication configuration; bound retention and protect log access.
- Service isolation: dedicated identity, restricted filesystem/network/device access, least capabilities, necessary writable paths only.
- Sudo: prefer no passwordless privilege. If required, allow an exact reviewed command and arguments. Do not grant unrestricted shells, package managers, editors or generic `systemctl` access; these can become root execution.
- Patching: verify supported versions from vendor sources; pin inputs according to the project's update policy.

Validate sudoers with `visudo -cf` before activation and SSH configuration with the target's supported validation command. A clean syntax check does not prove access or policy enforcement. Record revision, target, first/second-apply results, smoke evidence and recovery status.
