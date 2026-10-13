#!/usr/bin/env python3
"""Scan public files; report paths and rule IDs without echoing sensitive lines."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    'private-project-path': r'/(?:opt|home)/[^\s`"\']*(?:swarm|cluster|claude-config|hydra|chimi)',
    'private-service': r'\b(?:mcp__[h]ydra|cb_[p]eek|hnn_[a-z_]+|agent-ipc-[n]ats|CHIMI_[A-Z_]+)\b',
    'private-project-example': r'\b[Ee]xam[Ff]orge\b',
    'personal-email': r'\b[\w.+-]+@(?:gmail|hotmail|yahoo|outlook)\.com\b',
    'private-host-address': r'\b(?:10\.\d+\.\d+\.[1-9]\d*|192\.168\.\d+\.[1-9]\d*|172\.(?:1[6-9]|2\d|3[01])\.\d+\.[1-9]\d*)\b',
    'credential': r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|sk-[A-Za-z0-9]{32,})',
    'private-key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
}


def scan(text):
    return [name for name, pattern in RULES.items() if re.search(pattern, text)]


def main():
    # Tracked plus newly authored files; deleted paths are ignored. No broad folder exemption.
    output = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'])
    errors = []
    for name in sorted(set(output.decode().split('\0')) - {''}):
        path = ROOT / name
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeError:
            errors.append((name, ['non-text-file-requires-review']))
            continue
        hits = scan(content)
        if hits:
            errors.append((name, hits))
    for name, hits in errors:
        print(f'{name}: {", ".join(hits)}', file=sys.stderr)
    if errors:
        return 1
    print('Public content scan passed (heuristic; use alongside secret scanning and review).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
