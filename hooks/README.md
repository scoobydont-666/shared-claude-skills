# Optional Claude Code advisories

These five advisories require Python 3.10+. PR-size also requires Git 2.45+ (supporting `--no-lazy-fetch`) and a locally fetched base ref; unsupported Git versions skip the advisory. They read a bounded JSON event from stdin and may emit `hookSpecificOutput.additionalContext` for `PreToolUse`. They never execute the submitted command, make network calls, write state, return an allow/deny decision, or replace security controls. Malformed or oversized input produces no advice.

| Hook | Matcher | Behavior and limits |
|---|---|---|
| `git-stash-storage-warn.py` | Bash | Reminds that an unmatched stash operation is not a durable handoff. Heuristic shell parsing; may miss wrappers or complex syntax. |
| `pr-size-warn.py` | Bash | Warns above 400 changed text lines (override `PR_SIZE_WARN_MAX`). Supports simple local `gh pr create`, optionally preceded by `cd PATH &&`, and `--base`/`-B`. Skips remote/alternate-head/complex forms. Uses cached origin refs; excludes binary size. |
| `advisories.py bash-python-escape` | Bash | Suggests a script file for inline Python with fragile shell quoting. |
| `advisories.py code-consistency` | Write, Edit, NotebookEdit | Points supported language edits at repository conventions and the optional installed language reference. |
| `advisories.py shell-safety` | Write | Prompts review of error handling for new shell files. Does not misread a partial Edit as a complete script. |

## Installation

Review [settings.example.json](settings.example.json) and the scripts before opting in. From the repository root, copy into a **new** hook directory:

```bash
mkdir -p "$HOME/.claude/hooks"
test ! -e "$HOME/.claude/hooks/shared-claude-skills" && \
  mkdir "$HOME/.claude/hooks/shared-claude-skills" && \
  cp hooks/*.py "$HOME/.claude/hooks/shared-claude-skills/"
```

Back up existing settings. Merge only the desired `PreToolUse` entries from the example into `~/.claude/settings.json`; preserve all existing settings and hooks. Do not replace the settings file wholesale. Every command uses a quoted installation path and a five-second timeout. The code-consistency advice is most useful with that skill installed.

Inspect the resulting bindings in Claude Code's `/hooks` menu, restart the session if required by the installed client, and trigger a representative event. For example, proposing a temporary `git stash push` should surface an advisory. Confirm existing permission prompts and safety controls still apply. Fixture tests validate the documented JSON contract, but are not a substitute for checking your actual client version.

To disable, remove only these entries from settings and reload/restart as required. Installed script files can remain inert. Review and back up local edits before any upgrade or removal. No script here changes your settings automatically.

Contract reference: https://code.claude.com/docs/en/hooks (checked 2026-10-13).
