#!/usr/bin/env python3
"""Validate the explicit public catalog and its bundled dependency closure."""
import json
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
HOOK_MATCHERS = {
    'git-stash-storage-warn.py': 'Bash',
    'pr-size-warn.py': 'Bash',
    'advisories.py:bash-python-escape': 'Bash',
    'advisories.py:code-consistency': 'Write|Edit|NotebookEdit',
    'advisories.py:shell-safety': 'Write',
}


def validate(root=ROOT):
    errors = []
    manifest = json.loads((root / 'catalog.json').read_text())
    actual = {p.parent.name for p in (root / 'skills').glob('*/SKILL.md')}
    if actual != set(manifest['skills']):
        errors.append('skill directories differ from the reviewed catalog')
    for name in sorted(actual):
        folder = root / 'skills' / name
        path = folder / 'SKILL.md'
        text = path.read_text()
        try:
            if not text.startswith('---\n'):
                raise ValueError('missing frontmatter')
            metadata = yaml.safe_load(text.split('---', 2)[1])
            if set(metadata) != {'name', 'description'} or metadata['name'] != name:
                raise ValueError('invalid metadata keys or name')
            if not isinstance(metadata['description'], str) or not metadata['description'].strip():
                raise ValueError('missing description')
        except (ValueError, TypeError, yaml.YAMLError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
        for document in folder.rglob('*.md'):
            content = document.read_text()
            links = re.findall(r'\]\(([^)]+)\)', content)
            for target in links:
                if '://' in target or target.startswith(('#', 'mailto:')):
                    continue
                resolved = (document.parent / target.split('#')[0]).resolve()
                if not resolved.is_relative_to(folder.resolve()):
                    errors.append(f'{document.relative_to(root)}: link escapes installed skill {target}')
                elif not resolved.is_file():
                    errors.append(f'{document.relative_to(root)}: missing local link {target}')
            if document == path:
                for target in re.findall(r'`((?:references|scripts)/[\w./-]+\.(?:md|py|sh))`', content):
                    resolved = (folder / target).resolve()
                    if not resolved.is_relative_to(folder.resolve()) or not resolved.is_file():
                        errors.append(f'{path.relative_to(root)}: missing bundled resource {target}')
    for path in root.rglob('*'):
        if path.relative_to(root).parts[0] in {'.git', '.venv'} or '__pycache__' in path.parts:
            continue
        if path.is_symlink():
            errors.append(f'{path.relative_to(root)}: symlink not permitted in export')
    config = json.loads((root / 'hooks/settings.example.json').read_text())
    expected = set(manifest['hooks'])
    consumed = set()
    if set(config) != {'hooks'} or set(config['hooks']) != {'PreToolUse'}:
        errors.append('unsupported hook event configuration')
    for group in config['hooks']['PreToolUse']:
        for hook in group['hooks']:
            match = re.fullmatch(r'python3 "\$HOME/\.claude/hooks/shared-claude-skills/([\w.-]+\.py)"(?: ([\w-]+))?', hook['command'])
            if not match or hook['type'] != 'command' or hook['timeout'] != 5:
                errors.append('unsupported hook configuration')
                continue
            identity = match[1] + (':' + match[2] if match[2] else '')
            if identity in consumed or group.get('matcher') != HOOK_MATCHERS.get(identity):
                errors.append('unexpected hook matcher or duplicate binding: ' + identity)
            consumed.add(identity)
            if not (root / 'hooks' / match[1]).is_file():
                errors.append('missing hook executable: ' + match[1])
    if consumed != expected or expected != set(HOOK_MATCHERS):
        errors.append('hook wiring differs from catalog')
    workflow_paths = sorted((root / '.github/workflows').glob('*.y*ml'))
    for path in workflow_paths:
        workflow = yaml.safe_load(path.read_text())
        for job in workflow.get('jobs', {}).values():
            # Explicit allowlist: dynamic expressions, private labels and remote
            # reusable workflows need a policy review before being permitted.
            if job.get('runs-on') != 'ubuntu-24.04':
                errors.append(f'{path.relative_to(root)}: public repository requires GitHub-hosted runners')
    return errors


if __name__ == '__main__':
    issues = validate()
    for issue in issues:
        print(issue, file=sys.stderr)
    if issues:
        sys.exit(1)
    print('Catalog, metadata, local references and hook wiring validated.')
