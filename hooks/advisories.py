#!/usr/bin/env python3
"""Portable, stateless advisories adapted from the source hook workflows."""
import json
from pathlib import PurePath
import re
import sys

LANGUAGES = {'.py': 'python', '.sh': 'bash', '.bash': 'bash', '.go': 'golang',
             '.rs': 'rust', '.c': 'c', '.h': 'c', '.ps1': 'powershell',
             '.psm1': 'powershell', '.tf': 'terraform', '.tfvars': 'terraform'}


def advice(kind, data):
    tool = data.get('tool_name')
    args = data.get('tool_input')
    if not isinstance(args, dict):
        return None
    if kind == 'bash-python-escape' and tool == 'Bash':
        command = args.get('command')
        if isinstance(command, str) and re.search(r'\bpython(?:3)?\s+-c\s+[\'"]', command):
            return ('Inline Python and shell quoting can interact. For multiline code or complex quoting, '
                    'write a Python file and run it. Preserve literal dollar signs, braces and newlines. '
                    'This heuristic does not parse or execute the shell command.')
    if kind == 'code-consistency' and tool in {'Write', 'Edit', 'NotebookEdit'}:
        path = args.get('file_path') or args.get('notebook_path')
        if not isinstance(path, str):
            return None
        language = LANGUAGES.get(PurePath(path).suffix)
        if PurePath(path).suffix in {'.yaml', '.yml'} and set(PurePath(path).parts) & {
                'ansible', 'roles', 'playbooks', 'inventory', 'group_vars', 'host_vars'}:
            language = 'ansible'
        if language:
            return (f'Before editing {language}, follow this repository\'s conventions and configured formatter. '
                    f'If installed, consult code-consistency/references/{language}.md for supporting guidance. '
                    'Preserve error handling, input validation and meaningful tests. Do not rewrite style globally.')
    if kind == 'shell-safety' and tool == 'Write':
        path, content = args.get('file_path'), args.get('content')
        if isinstance(path, str) and path.endswith('.sh') and isinstance(content, str):
            if 'set -euo pipefail' not in '\n'.join(content.splitlines()[:20]):
                return ('Shell safety review: choose explicit error/unset-variable/pipeline handling for the '
                        'declared interpreter. Consider set -euo pipefail for Bash and handle its exceptions. '
                        'Do not add Bash-only options to POSIX sh. Quote expansions and use private temporary files.')
    return None


def main():
    raw = sys.stdin.buffer.read(1048577)
    if len(raw) > 1048576:
        return
    data = json.loads(raw)
    if not isinstance(data, dict) or len(sys.argv) != 2:
        return
    message = advice(sys.argv[1], data)
    if message:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': message}}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError, OSError, RecursionError):
        pass
