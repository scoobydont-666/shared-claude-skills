#!/usr/bin/env python3
"""Validate the explicit public catalog and its bundled dependency closure."""
import json
from pathlib import Path
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
READ_ONLY_PERSONAS = {'mr-fancy', 'mr-hardass', 'ms-research', 'solutions-architect'}
PERSONA_TOOLS = {'Read', 'Grep', 'Glob', 'Bash', 'Edit', 'Write', 'WebFetch', 'WebSearch'}
HOOK_MATCHERS = {
    'git-stash-storage-warn.py': 'Bash',
    'pr-size-warn.py': 'Bash',
    'advisories.py:bash-python-escape': 'Bash',
    'advisories.py:code-consistency': 'Write|Edit|NotebookEdit',
    'advisories.py:shell-safety': 'Write',
}


def catalog_table(root, kind):
    """Derive public descriptions from the installed metadata, without a second copy."""
    manifest = json.loads((root / 'catalog.json').read_text())
    title = 'Skill' if kind == 'skills' else 'Persona'
    rows = [f'| {title} | Purpose |', '|---|---|']
    for name in manifest[kind]:
        relative = f'skills/{name}/SKILL.md' if kind == 'skills' else f'personas/{name}.md'
        metadata = yaml.safe_load((root / relative).read_text().split('---', 2)[1])
        description = ' '.join(metadata['description'].split()).replace('|', r'\|')
        rows.append(f'| [{name}]({relative}) | {description} |')
    return f'## {title} catalog ({len(manifest[kind])})\n\n' + '\n'.join(rows) + '\n'


def update_catalog_docs(root=ROOT):
    path = root / 'README.md'
    text = path.read_text()
    for kind in ('skills', 'personas'):
        start, end = f'<!-- catalog:{kind}:start -->', f'<!-- catalog:{kind}:end -->'
        if text.count(start) != 1 or text.count(end) != 1:
            raise ValueError(f'missing or duplicate README catalog markers: {kind}')
        before, rest = text.split(start)
        _, after = rest.split(end)
        text = before + start + '\n' + catalog_table(root, kind) + end + after
    path.write_text(text)


def validate_personas(root, manifest):
    errors = []
    folder = root / 'personas'
    paths = sorted(p for p in folder.rglob('*.md') if p != folder / 'README.md')
    expected = {f'{name}.md' for name in manifest.get('personas', [])}
    if {str(p.relative_to(folder)) for p in paths} != expected:
        errors.append('persona files differ from the reviewed catalog')
    for path in paths:
        text = path.read_text()
        try:
            if not text.startswith('---\n') or '\n---\n' not in text[4:]:
                raise ValueError('missing persona frontmatter')
            metadata = yaml.safe_load(text.split('---', 2)[1])
            keys = {'name', 'description', 'tools', 'model', 'permissionMode', 'maxTurns'}
            if not isinstance(metadata, dict) or set(metadata) != keys:
                raise ValueError('unsupported persona metadata or dependency')
            if metadata['name'] != path.stem or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', path.stem):
                raise ValueError('invalid persona name')
            if not isinstance(metadata['description'], str) or not metadata['description'].strip():
                raise ValueError('missing persona description')
            if metadata['model'] != 'inherit' or metadata['permissionMode'] != 'default':
                raise ValueError('persona must inherit model and request default permissions')
            if type(metadata['maxTurns']) is not int or not 1 <= metadata['maxTurns'] <= 80:
                raise ValueError('invalid persona turn bound')
            if not isinstance(metadata['tools'], str):
                raise ValueError('persona tools must be an explicit comma-separated allowlist')
            names = [item.strip() for item in metadata['tools'].split(',')]
            if len(names) != len(set(names)) or not set(names) <= PERSONA_TOOLS or not {'Read', 'Grep', 'Glob'} <= set(names):
                raise ValueError('unsupported persona tools')
            if path.stem in READ_ONLY_PERSONAS and {'Bash', 'Edit', 'Write'} & set(names):
                raise ValueError('read-only persona has mutation-capable tools')
        except (ValueError, TypeError, yaml.YAMLError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                errors.append(f'{path.relative_to(root)}: standalone persona has local dependency {target}')
    return errors


def validate(root=ROOT):
    errors = []
    manifest = json.loads((root / 'catalog.json').read_text())
    if manifest.get('schema_version') != 2:
        errors.append('unsupported catalog schema version')
    for kind in ('skills', 'personas', 'hooks'):
        if not isinstance(manifest.get(kind), list) or len(manifest[kind]) != len(set(manifest[kind])):
            errors.append(f'invalid or duplicate {kind} catalog entries')
    errors.extend(validate_personas(root, manifest))
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
    if not errors:
        readme = (root / 'README.md').read_text()
        for kind in ('skills', 'personas'):
            expected = f'<!-- catalog:{kind}:start -->\n' + catalog_table(root, kind) + f'<!-- catalog:{kind}:end -->'
            if expected not in readme:
                errors.append(f'README {kind} catalog is stale; run scripts/validate_catalog.py --write-catalogs')
    documents = [root / 'README.md', root / 'hooks/README.md', root / 'personas/README.md', *sorted((root / 'docs').glob('*.md'))]
    for path in documents:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith(('#', 'mailto:')):
                continue
            resolved = (path.parent / target.split('#')[0]).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                errors.append(f'{path.relative_to(root)}: missing or outside-repository document link {target}')
    return errors


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-catalogs', action='store_true', help='refresh README catalogs from reviewed metadata before validating')
    args = parser.parse_args()
    if args.write_catalogs:
        update_catalog_docs()
    issues = validate()
    for issue in issues:
        print(issue, file=sys.stderr)
    if issues:
        sys.exit(1)
    print('Catalog, skills, personas, documentation, hook wiring and runner policy validated.')
