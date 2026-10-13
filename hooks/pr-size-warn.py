#!/usr/bin/env python3
"""Read-only PR-size advisory; never executes the submitted command."""
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys


def git(cwd, *args):
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0')
    return subprocess.run(['git', '--no-lazy-fetch', '-c', 'core.fsmonitor=false', '-C', str(cwd), *args],
                          capture_output=True, text=True, timeout=1, env=env, check=True).stdout.strip()


def main():
    raw = sys.stdin.buffer.read(1048577)
    if len(raw) > 1048576:
        return
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get('tool_name') != 'Bash':
        return
    args = data.get('tool_input')
    if not isinstance(args, dict) or not isinstance(args.get('command'), str):
        return
    tokens = shlex.split(args['command'])
    cwd = Path(data.get('cwd') or os.getcwd())
    if len(tokens) >= 4 and tokens[0] == 'cd' and tokens[2] == '&&':
        cwd = cwd / tokens[1]
        tokens = tokens[3:]
    if tokens[:3] != ['gh', 'pr', 'create']:
        return
    # Only inspect a simple local invocation. Never guess a remote repository,
    # alternate head or directory reached through compound shell commands.
    base = None
    i = 3
    value_options = {'--title', '-t', '--body', '-b', '--body-file', '-F', '--label', '-l',
                     '--assignee', '-a', '--reviewer', '-r', '--milestone', '-m', '--project', '-p'}
    flags = {'--draft', '-d', '--fill', '-f', '--fill-first', '--fill-verbose', '--no-maintainer-edit'}
    while i < len(tokens):
        token = tokens[i]
        if token in {'--base', '-B'}:
            i += 1
            if i >= len(tokens):
                return
            base = tokens[i]
        elif token.startswith('--base='):
            base = token.split('=', 1)[1]
        elif token in value_options:
            i += 1
            if i >= len(tokens):
                return
        elif token not in flags:
            return
        i += 1
    if base is None:
        ref = git(cwd, 'symbolic-ref', '--quiet', 'refs/remotes/origin/HEAD')
    else:
        if not base or base.startswith('-'):
            return
        ref = 'refs/remotes/origin/' + base
    git(cwd, 'check-ref-format', ref)
    sha = git(cwd, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}')
    ancestor = git(cwd, 'merge-base', '--end-of-options', sha, 'HEAD')
    diff = git(cwd, 'diff', '--no-ext-diff', '--no-textconv', '--numstat', '--end-of-options', ancestor, 'HEAD')
    total = sum(int(cell) for line in diff.splitlines() for cell in line.split('\t')[:2] if cell.isdigit())
    limit = max(1, int(os.environ.get('PR_SIZE_WARN_MAX', '400')))
    if total > limit:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext':
            f'PR SIZE WARNING: {total} changed text lines against the locally cached base, above {limit}. '
            'Consider splitting by independently reviewable behavior. Binary changes are not counted; '
            'the remote base may have advanced. This is an advisory, not a merge gate.'}}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError, OSError, RecursionError, subprocess.SubprocessError):
        pass  # An unavailable advisory must not authorize or deny a tool call.
