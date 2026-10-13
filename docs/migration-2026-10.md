# Portable catalog migration — October 2026

The current package contains 41 skills, eight standalone personas and five optional advisories. It replaces an older catalog of 32 skills, removes environment-bound workflows and includes the resources needed by the retained skills.

| Removed skill | Reason / replacement |
|---|---|
| `hydra-swarm` | Internal distributed coordination; excluded from the public package. |
| `fleet-manager` | Private host inventory and delivery workflow. |
| `openclaw-ops` | Retired environment-specific deployment instructions. |
| `budi-analytics` | Superseded analytics integration with no current canonical skill in the source inventory. |
| `project-management` | Private board/executor assumptions; use `software-development-lifecycle` and `plan-to-execution-handoff` for portable guidance. |
| `session-miser` | Consolidated into `token-miser`; no frozen session model menu. |
| `cost-optimizer` | Private operational economics removed; model-usage guidance consolidated into `token-miser`. |

The existing public `cpa-tax-specialist` evidence/reconciliation workflow is preserved. It is not replaced with the older private persona. Reference metadata is normalized without dropping its controls.

Before updating an existing installation:

1. Record the current installed skill paths and back up locally customized copies outside the active skills directory.
2. Review each removed skill above. Move only the corresponding obsolete directory out of active discovery; do not delete a broader directory or another tool's skill tree.
3. Compare replacement skills against local customizations before copying. A merge-copy can leave obsolete reference files behind, so review the full destination directory against the new package.
4. Install desired personas separately using the [persona guide](../personas/README.md). Compare existing agents with the same name before replacing them; public tool allowlists and instructions intentionally differ from private variants. No companion skill is mandatory.
5. Skills and personas do not enable hooks. Install and merge the optional bindings separately using the [hook guide](../hooks/README.md).
6. Verify discovery and a representative task in the consuming client. Roll back with the backed-up directory/settings if needed.

The public package intentionally excludes private IPC, dispatch, model-serving and training operations, host inventories, incident traces, generated harness copies and retired source trees. Security gates requiring private validators, grants or services are not weakened into public lookalikes. The exported hook subset is advisory only.

Existing Git history is preserved. Removing files from this revision does not erase prior public commits or rewrite other branches. The older manifest branch was inspected and left intact; this revision's `catalog.json` describes the curated package, not a fleet deployment contract.

## Persona and documentation update

The eight personas cover design, security review, pragmatic debugging, delivery, research, implementation, architecture and SRE. Personal-biography and project-specific operators, generated copies and vendored third-party packs are excluded. Public files remove private integrations, machine details, personal history, local dispatch contracts and hardcoded model selection.

`catalog.json` schema version 2 adds `personas` and a package description; the `skills` and `hooks` arrays retain their earlier meaning. Consumers that enforce a schema must recognize version 2 before consuming it. README tables are generated from skill/persona metadata, and validation rejects stale descriptions. Skill names and bundled paths remain stable.

Personas request the parent model and normal permissions, but the consuming runtime controls the effective settings. Verify actual tool availability and permissions after installation. A local copy can be reverted from its backup without changing any hook bindings or installed skills.
