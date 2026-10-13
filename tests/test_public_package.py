import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scanner = load('scanner', ROOT / 'scripts/check_public_content.py')
validator = load('validator', ROOT / 'scripts/validate_catalog.py')


class ContentTests(unittest.TestCase):
    def test_public_patterns_reject_private_values(self):
        samples = ['https://' + '192.168.' + '55.22/path', 'user' + '@gmail.com',
                   '/opt/' + 'private-cluster/settings', 'cb_' + 'peek',
                   'gh' + 'p_' + 'A' * 36, 'exam' + 'forge']
        for sample in samples:
            with self.subTest(sample=sample[:8]):
                self.assertTrue(scanner.scan(sample))

    def test_generic_examples_are_allowed(self):
        self.assertEqual(scanner.scan('user@example.com 192.168.0.0/16 https://example.com'), [])

    def test_catalog_passes(self):
        self.assertEqual(validator.validate(), [])

    def test_local_venv_is_ignored_but_exported_symlink_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'repo'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
            environment = target / '.venv'
            environment.mkdir()
            (environment / 'python').symlink_to(sys.executable)
            self.assertEqual(validator.validate(target), [])
            (target / 'skills/cavetech/external').symlink_to(environment)
            self.assertTrue(any('symlink not permitted' in error for error in validator.validate(target)))

    def test_missing_resource_and_unknown_skill_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'repo'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
            (target / 'skills/cavetech/references/examples.md').unlink()
            extra = target / 'skills/unreviewed'
            extra.mkdir()
            (extra / 'SKILL.md').write_text('---\nname: unreviewed\ndescription: Example\n---\n')
            errors = validator.validate(target)
            self.assertTrue(any('missing bundled resource' in error for error in errors))
            self.assertTrue(any('reviewed catalog' in error for error in errors))

    def test_private_runner_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'repo'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
            path = target / '.github/workflows/security.yml'
            path.write_text(path.read_text().replace('runs-on: ubuntu-24.04', 'runs-on: self-hosted'))
            self.assertTrue(any('GitHub-hosted' in error for error in validator.validate(target)))

    def test_new_private_workflow_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'repo'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
            (target / '.github/workflows/extra.yaml').write_text('jobs:\n  unsafe:\n    runs-on: self-hosted\n')
            self.assertTrue(any('GitHub-hosted' in error for error in validator.validate(target)))

    def test_wrong_hook_matcher_and_event_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'repo'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
            path = target / 'hooks/settings.example.json'
            config = json.loads(path.read_text())
            config['hooks']['PreToolUse'][0]['matcher'] = 'NeverAMatchingTool'
            config['hooks']['PostToolUse'] = []
            path.write_text(json.dumps(config))
            errors = validator.validate(target)
            self.assertTrue(any('hook matcher' in error for error in errors))
            self.assertTrue(any('hook event' in error for error in errors))

    def test_repo_only_skill_link_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'repo'
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.venv', '__pycache__'))
            path = target / 'skills/cavetech/SKILL.md'
            path.write_text(path.read_text() + '\n[repo-only link](../../README.md)\n')
            self.assertTrue(any('escapes installed skill' in error for error in validator.validate(target)))


class HookTests(unittest.TestCase):
    def run_hook(self, filename, data, *args):
        result = subprocess.run([sys.executable, str(ROOT / 'hooks' / filename), *args],
                                input=data if isinstance(data, bytes) else json.dumps(data).encode(),
                                capture_output=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        if result.stdout:
            output = json.loads(result.stdout)['hookSpecificOutput']
            self.assertEqual(output['hookEventName'], 'PreToolUse')
            self.assertNotIn('permissionDecision', output)
            self.assertIsInstance(output['additionalContext'], str)
            return output['additionalContext']
        return ''

    def test_stash_warns_without_executing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / 'executed'
            data = {'tool_name': 'Bash', 'tool_input': {'command': f'git stash push; touch {marker}'}}
            self.assertTrue(self.run_hook('git-stash-storage-warn.py', data))
            self.assertFalse(marker.exists())

    def test_stash_read_restore_and_non_bash_are_quiet(self):
        for command in ['git status', 'git stash list', 'git stash pop', 'echo "git stash push"']:
            self.assertFalse(self.run_hook('git-stash-storage-warn.py',
                                          {'tool_name': 'Bash', 'tool_input': {'command': command}}))
        self.assertFalse(self.run_hook('git-stash-storage-warn.py',
                                      {'tool_name': 'Read', 'tool_input': {'command': 'git stash'}}))

    def test_advisories_positive_and_negative(self):
        cases = [('bash-python-escape', 'Bash', {'command': 'python3 -c "print(1)"'}),
                 ('code-consistency', 'Edit', {'file_path': '/project/app.py'}),
                 ('code-consistency', 'Write', {'file_path': 'roles/web/tasks/main.yml'}),
                 ('shell-safety', 'Write', {'file_path': 'test.sh', 'content': '#!/bin/sh\necho ok\n'})]
        for kind, tool, args in cases:
            self.assertTrue(self.run_hook('advisories.py', {'tool_name': tool, 'tool_input': args}, kind))
        self.assertFalse(self.run_hook('advisories.py',
                         {'tool_name': 'Edit', 'tool_input': {'file_path': 'test.sh', 'new_string': 'echo ok'}}, 'shell-safety'))
        self.assertFalse(self.run_hook('advisories.py',
                         {'tool_name': 'Write', 'tool_input': {'file_path': 'test.sh', 'content': '#!/usr/bin/env bash\nset -euo pipefail\n'}}, 'shell-safety'))
        self.assertFalse(self.run_hook('advisories.py',
                         {'tool_name': 'Bash', 'tool_input': {'command': 'python3 file.py'}}, 'bash-python-escape'))

    def test_malformed_and_oversized_are_quiet(self):
        for filename, args in [('git-stash-storage-warn.py', ()), ('pr-size-warn.py', ()), ('advisories.py', ('shell-safety',))]:
            for raw in [b'', b'{bad', b'[]', b'null', b'x' * 1048577, b'[' * 10000 + b']' * 10000]:
                self.assertFalse(self.run_hook(filename, raw, *args))

    def test_pr_size_uses_local_base_and_does_not_run_commands(self):
        with tempfile.TemporaryDirectory(prefix='public hook ') as tmp:
            repo = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', '-C', tmp, *args], stderr=subprocess.DEVNULL, text=True).strip()
            git('init', '-b', 'main')
            git('config', 'user.name', 'Fixture Author')
            git('config', 'user.email', 'fixture@example.com')
            (repo / 'example.txt').write_text('base\n')
            git('add', 'example.txt')
            git('commit', '-m', 'base')
            git('update-ref', 'refs/remotes/origin/main', 'HEAD')
            git('symbolic-ref', 'refs/remotes/origin/HEAD', 'refs/remotes/origin/main')
            git('switch', '-c', 'feature')
            (repo / 'example.txt').write_text('base\n' + 'new\n' * 401)
            git('add', 'example.txt')
            git('commit', '-m', 'change')
            data = {'cwd': tmp, 'tool_name': 'Bash', 'tool_input': {'command': 'gh pr create --title "Example" --body "text"'}}
            self.assertIn('401', self.run_hook('pr-size-warn.py', data))
            for command in ['gh pr create --repo other/repo', 'gh pr create --head other',
                            'gh pr create --base missing', 'gh pr create; touch marker']:
                data['tool_input']['command'] = command
                self.assertFalse(self.run_hook('pr-size-warn.py', data))
            self.assertFalse((repo / 'marker').exists())

    def test_all_installed_bindings_execute(self):
        config = json.loads((ROOT / 'hooks/settings.example.json').read_text())
        with tempfile.TemporaryDirectory(prefix='installed hooks ') as tmp:
            install = Path(tmp) / 'shared-claude-skills'
            install.mkdir()
            for path in (ROOT / 'hooks').glob('*.py'):
                shutil.copy2(path, install / path.name)
            for group in config['hooks']['PreToolUse']:
                for hook in group['hooks']:
                    command = hook['command'].replace('$HOME/.claude/hooks/shared-claude-skills', str(install))
                    result = subprocess.run(command, shell=True, input=b'{"tool_name":"Read","tool_input":{}}',
                                            capture_output=True, timeout=hook['timeout'])
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, b'')


if __name__ == '__main__':
    unittest.main()
