# Sysadmin 101

Basic operating rules for Windows, Linux, humans, and AI agents.

**Check first. Change less. Make reruns harmless. Prove the result. Prevent the repeat.**

Operator-supplied addendum, 2026-10-07. The numbered rules below preserve the
operator's requirements. Platform references support specific mechanisms; they
are not the source of the whole policy.

**MUST** means required. **MUST NOT** means forbidden. **STOP** means make no
further changes; report what is unknown and get the missing information or
authorization.

## 1. Know exactly what you are touching.

Before changing anything, confirm the computer, operating system, account,
environment, and exact target. Verify the full file path, disk identity, or service
name. Check where links and mounted folders actually lead. Access to a system is
not permission to change everything on it.

## 2. Perform the cheap, safe check first.

Read the error. Check service status, logs, free space, permissions, connectivity,
and recent changes. Do not start with a reboot, reinstall, reset, deletion, or
rebuild. A failed check means “unknown”—not “missing,” “empty,” or “safe to replace.”

## 3. Separate the operating system from application storage where practical.

Prefer separate storage for critical applications when supported, especially their
databases, working data, large files, and growing logs. Do not scatter application
files directly into `C:\` or `/`.

Windows normally uses Program Files; Linux uses defined locations such as `/usr`
and `/opt`. Respect the installer and operating-system layout—do not manually move
managed program files merely to get them off the system volume.

Verify the intended data drive or mounted filesystem is present before writing.
Never silently substitute the operating-system disk.

## 4. Never delete by guesswork or broad wildcard.

Do not use commands such as `rm -rf *.*` or `Remove-Item * -Recurse -Force` as
cleanup shortcuts. Identify and inspect the exact items first. Use explicit, full
paths; stop on empty variables or unexpectedly broad targets. In PowerShell, use
`-LiteralPath` for exact names and `-WhatIf` to preview supported operations.
Adding “force” is not a safety check.

## 5. Have verified recovery before risking important data.

Before deleting, overwriting, formatting, or making a potentially disabling
change, verify a current backup of the affected data and configuration. Know how
to restore it, and test restoration. Keep protected recovery copies outside the
affected system. A successful backup job alone does not prove recoverability.
No verified recovery means no destructive change to important data.

## 6. Treat hidden files, keys, and configuration as protected—not junk.

Do not delete something because it is hidden, starts with a dot, looks old, or is
unfamiliar. Explicitly include required hidden files in backups.

Protect `.ssh`, `.gnupg`, `.env`, `.git`, application configuration, Windows AppData
and ProgramData, relevant Registry settings, certificates, private keys, and
recovery keys. Never regenerate keys or overwrite configuration just to make an
error disappear. Back up secrets securely; never expose them in Git, logs,
screenshots, or AI prompts.

## 7. Use only the permissions the task needs.

Use a normal account for normal work. Elevate to Administrator or root only for a
specific authorized operation; Windows UAC supports this separation. Do not
routinely run applications or agents with unrestricted administrative rights.

Do not “fix” permission errors by granting everyone full control, applying broad
recursive permission changes, or disabling security controls. Identify the exact
access needed and grant only that.

## 8. Install and update through supported, repeatable methods.

Use approved sources, installers, and package managers. Review downloaded scripts
before executing them; do not blindly execute internet content with
administrative privileges. Record versions and installation choices. Test risky
updates and retain a rollback path. Do not replace shared system components to
satisfy one application without checking the impact.

## 9. Make repeated execution safe: be idempotent.

Check whether the desired state already exists. If it does, leave it alone. A
second run must not duplicate settings, recreate resources, reset passwords, or
restart healthy services unnecessarily. After a timeout or interrupted operation,
inspect the actual result before retrying.

## 10. Make one controlled change at a time.

Preserve other people's and agents' work. Coordinate before changing shared files
or services. Do not discard uncommitted work, overwrite configuration wholesale,
or run competing maintenance tasks. Obtain approval for downtime. Before changing
networking, authentication, or remote access, establish another tested way back
into the machine.

## 11. Verify the result—not merely the command's exit status.

Read back the changed configuration. Check service health and new errors. Test
the application the way its user actually uses it. Confirm important data,
permissions, and unrelated services remain intact. If verification fails, stop
additional changes and follow the recovery plan. Never label untested work “done.”

## 12. Leave the system easier to maintain.

Record what changed, why, where, how it was tested, and how to undo it—without
recording secret values. Update the maintained configuration or automation so the
next deployment preserves the fix. Establish appropriate backup, capacity, and
health checks. Fix the cause; do not make the same emergency repair a routine.

## Mandatory stop rule

If the target, authorization, consequences, or required recovery method is
unknown, **STOP**. A request to “fix it” or “clean it up” is not permission to guess,
erase, bypass security, or destroy evidence.

In this skill, stopping the affected change still permits authorized safe
diagnosis. Existing authorization remains valid within its verified scope; STOP
does not create a repeated-approval loop.

## Platform references

- [Windows Known Folders](https://learn.microsoft.com/en-us/windows/win32/shell/knownfolderid)
  identifies supported application and data locations; actual paths depend on
  the system and application architecture.
- [PowerShell Remove-Item](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/remove-item?view=powershell-7.5)
  documents literal paths, force and supported preview behavior.
- [How UAC works](https://learn.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works)
  distinguishes ordinary and elevated access tokens.
- [SQL Server backup and restore](https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/back-up-and-restore-of-sql-server-databases)
  gives a concrete example of verifying restoration rather than relying on backup
  completion alone; it is not a generic command recipe for other applications.
