---
name: claude-to-cursor
description: Convert selected Claude Code skills into scoped Cursor project rules when asked to port skills, export Cursor rules, or produce .mdc files. Preserve reference dependencies and verify target-client behavior.
---
# Claude to Cursor

Inspect the selected skill, bundled resources and destination's existing rules.
Use the requested output repository or directory; preserve source configuration
and unrelated destination content. Review private paths, contacts and tool
assumptions before sharing a rule.

## Conversion

1. Retain portable instructions and replace tool-specific calls with capabilities
   actually available in the target client. Do not discard general workflows just
   because their source used Claude tools. Token budgeting and evidence-based
   review, for example, remain portable.
2. Write focused `.mdc` project rules in `.cursor/rules/`. Use a description for
   agent-selected relevance, globs for file-specific rules, or `alwaysApply: true`
   only when the user intends the rule to apply to every conversation.
3. Keep essential instructions in the rule body. Preserve supporting documents or
   scripts at explicit destination paths, update references, and verify they can
   be read after installation. A file reference does not automatically inline it.
4. Preserve licensing and attribution. Treat hooks and executable integrations
   separately: copying their prose does not install or activate them in Cursor.
5. Inspect the rule in the installed Cursor client and exercise a representative
   request. Report any unsupported capability and whether client activation was
   actually checked.

Example rule:

```markdown
---
description: Python conventions for this repository
globs: "**/*.py"
alwaysApply: false
---

Follow this repository's configured formatter and test conventions.
```

Current format reference: https://cursor.com/docs/rules (checked 2026-10-13).
This skill is a conversion procedure; it does not bundle an automatic converter.
