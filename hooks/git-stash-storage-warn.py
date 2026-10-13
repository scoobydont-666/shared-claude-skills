#!/usr/bin/env python3
"""Warn when git stash is used as storage. Never blocks."""

import json
import re
import shlex
import sys


def emit(msg: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": msg,
        }
    }))
    raise SystemExit(0)


def strip_heredocs(text: str) -> str:
    lines = text.splitlines()
    out = []
    index = 0
    while index < len(lines):
        match = re.search(r"<<\s*-?\s*['\"]?([A-Za-z0-9_]+)['\"]?", lines[index])
        if match:
            marker = match.group(1)
            out.append(lines[index].split("<<", 1)[0])
            index += 1
            while index < len(lines) and lines[index].strip() != marker:
                index += 1
            index += 1
            continue
        out.append(lines[index])
        index += 1
    return "\n".join(out)


def segments(text: str) -> list[str]:
    parts = []
    buf = []
    quote = None
    index = 0
    while index < len(text):
        ch = text[index]
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            index += 1
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            index += 1
            continue
        if text.startswith("&&", index) or text.startswith("||", index):
            parts.append("".join(buf))
            buf = []
            index += 2
            continue
        if ch in ";\n|":
            parts.append("".join(buf))
            buf = []
            index += 1
            continue
        buf.append(ch)
        index += 1
    parts.append("".join(buf))
    return [part for part in parts if part.strip()]


def stash_kind(tokens: list[str]) -> str | None:
    index = 1
    while index < len(tokens):
        tok = tokens[index]
        if tok in ("-C", "--git-dir", "--work-tree", "-c") and index + 1 < len(tokens):
            index += 2
            continue
        if tok.startswith(("-c", "--git-dir=", "--work-tree=")):
            index += 1
            continue
        if tok == "stash":
            sub = tokens[index + 1] if index + 1 < len(tokens) else ""
            if sub in ("pop", "apply"):
                return "restore"
            if sub in ("list", "show", "drop", "clear", "branch", "--help", "-h"):
                return "other"
            return "storage"
        return None
    return None


def classify(text: str, depth: int = 0) -> tuple[bool, bool]:
    if depth > 8:
        return False, False
    storage = False
    restore = False
    for part in segments(strip_heredocs(text)):
        try:
            tokens = shlex.split(part, posix=True)
        except ValueError:
            continue
        while tokens and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]):
            tokens = tokens[1:]
        if not tokens:
            continue
        tokens[0] = tokens[0].lstrip("(")
        if tokens[0] in ("bash", "sh") and len(tokens) >= 3 and tokens[1] == "-c":
            inner_storage, inner_restore = classify(tokens[2], depth + 1)
            storage = storage or inner_storage
            restore = restore or inner_restore
            continue
        if tokens[0] == "git":
            kind = stash_kind(tokens)
            if kind == "storage":
                storage = True
            elif kind == "restore":
                restore = True
    return storage, restore


def main() -> None:
    try:
        raw = sys.stdin.buffer.read(1048577)
        if len(raw) > 1048576:
            return
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return
    if not isinstance(payload, dict) or payload.get("tool_name") != "Bash":
        return
    tool_input = payload.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str) or not command.strip():
        return
    storage, restore = classify(command)
    if storage and not restore:
        emit(
            "STASH STORAGE WARNING (warn-only, not a block): "
            "git stash push/save is not storage. Commit the WIP on your own branch "
            "in an owned worktree. Review staged paths and publish only when authorized. "
            "A temporary stash is not a durable handoff."
        )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass
