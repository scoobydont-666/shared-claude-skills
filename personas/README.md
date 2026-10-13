# Portable personas

Eight standalone Claude Code agent definitions provide distinct working styles.
Skills supply reusable procedures; personas select a role and approach; hooks
provide event-time advice. Installing one does not install or enable the others.
These are public adaptations, not biographies or claims of professional credentials.

## Choose a role

| Persona | Use it for | Optional companion skills |
|---|---|---|
| [Mr. Fancy](mr-fancy.md) | UI/UX critique and actionable redesign | `grill-me`, `write-a-prd` |
| [Mr. Hardass](mr-hardass.md) | Static security and privacy review | `differential-review`, `insecure-defaults`, `supply-chain-risk-auditor` |
| [Mr. Smartass](mr-smartass.md) | Root-cause debugging and pragmatic repair | `systematic-debugging`, `code-quality`, `verification-before-completion` |
| [Mr. Smith](mr-smith.md) | GitOps, CI and reviewable delivery | `software-development-lifecycle`, `ci-cd` |
| [Ms. Research](ms-research.md) | Research, fact checking and contested claims | `model-evaluation` when comparing models |
| [Software Developer](software-developer.md) | Implementing an accepted requirement | `software-developer`, `tdd` |
| [Solutions Architect](solutions-architect.md) | Architecture and developer-ready decisions | `solutions-architect`, `prd-to-plan` |
| [SRE Bot](sre-bot.md) | Diagnostics, safe operations and toil reduction | `lonely-sysadmin`, `ci-cd` |

The files are self-contained: no skill preloads, custom MCP tools, private
services, environment paths or companion files are required. To add a companion
skill, install its complete directory using the [skill guide](../README.md#install-a-skill),
then explicitly add its name to the local agent's `skills` frontmatter. Review
the combined instructions and tool needs before use. Keep such local adaptations
separate from the original so upgrades can be compared.

## Install one persona

From the repository root, review a file and copy only the role you need. The
following POSIX-shell example refuses to replace an existing file or symlink:

```bash
mkdir -p "$HOME/.claude/agents"
if [ ! -e "$HOME/.claude/agents/mr-hardass.md" ] && \
   [ ! -L "$HOME/.claude/agents/mr-hardass.md" ]; then
  cp personas/mr-hardass.md "$HOME/.claude/agents/mr-hardass.md"
else
  echo "Persona already exists; review and back it up before replacing." >&2
fi
```

For project-only use, place the file in that project's `.claude/agents/` instead.
On Windows, copy the selected file into `%USERPROFILE%\.claude\agents\` or the
project's `.claude\agents\` with the same backup/replacement precautions.
Project agents with the same name can take precedence over user-level copies.
Restart Claude Code if a newly created agents directory is not discovered.
Ask explicitly, for example:

> Use the mr-hardass agent to review the supplied diff for security defects.
> Return evidence and proposed validation; do not execute project code.

Installing a persona makes it available for delegation; a matching task may
also cause Claude Code to select it automatically. It does not start a task at
installation time. Review installed agents and remove a definition from active
discovery to disable it. Back up local edits before upgrading or removing it.

## Tools and limits

`mr-fancy` and `mr-hardass` have file read/search tools only. `ms-research` and
`solutions-architect` also have web search/fetch tools. These four roles have no
shell or file-write tools and return proposed artifacts as text. They cannot run
tests or scanners, inspect a live browser session, or claim interactive validation.

`mr-smartass`, `mr-smith`, `software-developer` and `sre-bot` have shell and file
write tools for authorized implementation. **Bash can change or delete files and
make network calls.** These definitions do not create a sandbox, isolate a host,
or enforce filesystem/network scope; the executor and permission controls must
provide those boundaries.

Each file requests `model: inherit`, `permissionMode: default`, and a bounded
`maxTurns`. Runtime settings can override model and permission behavior; these
fields are not a cost cap or a guarantee of permission prompts. No persona grants
merge/deployment authority or replaces independent review. Missing tools and
unexecuted checks must remain explicit in its result.

Other clients can reuse the prose after adapting metadata and capabilities.
This package does not claim native installation support for every agent client.
Validate a representative task in the actual consuming client after installation;
repository checks do not launch Claude Code or prove live tool enforcement.

Format and discovery reference:
[Claude Code custom subagents](https://code.claude.com/docs/en/sub-agents)
(checked 2026-10-13).
