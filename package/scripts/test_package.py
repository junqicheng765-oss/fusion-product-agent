#!/usr/bin/env python3
"""Exercise installation safety and delivery-reference failure handling offline."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    install = load('fusion_install', ROOT / 'scripts/install.py')
    checker = load('delivery_check', ROOT / 'skills/fusion-product-agent/scripts/check_delivery.py')
    checks = []
    with tempfile.TemporaryDirectory(prefix='fusion-package-test-') as tmp:
        base = Path(tmp)
        for mode in ['skill', 'agent']:
            project = base / mode
            install.install(project, mode, dry_run=True)
            assert not project.exists(), 'dry run wrote project'
            checks.append(mode + ': dry run makes no files')
            result = install.install(project, mode)
            target = Path(result['skill_or_resource'])
            assert install.digest_tree(target) == install.digest_tree(ROOT / 'skills/fusion-product-agent')
            assert len(result['resources']) == 4
            for name, dest in result['resources'].items():
                assert install.digest_tree(Path(dest)) == install.digest_tree(ROOT / 'skills' / name)
            assert (target.parent / 'fusion-design-core/component-recipes/registry.json').is_file()
            assert (target.parent / 'fusion-design-ui-ux-pro-max/scripts/search.py').is_file()
            assert (target.parent / 'fusion-design-impeccable/SKILL.md').is_file()
            checks.append(mode + ': designer methods, scripts and assets installed with relative sibling paths intact')
            assert not (project / ('.codex/resources/fusion-product-agent' if mode == 'skill' else '.agents/skills/fusion-product-agent')).exists()
            checks.append(mode + ': copied complete independent rule tree; only selected registration mode')
            before = install.digest_tree(project)
            try:
                install.install(project, mode)
                raise AssertionError('existing install overwritten')
            except ValueError:
                pass
            assert before == install.digest_tree(project)
            checks.append(mode + ': repeat install refused without changing files')
        project = base / 'existing-config'
        (project / '.codex').mkdir(parents=True)
        config = project / '.codex/config.toml'
        original = '# project preferences\nmodel = "existing-model"\n'
        config.write_text(original)
        install.install(project, 'agent')
        assert config.read_text() == original
        checks.append('existing project config preserved byte-for-byte')
        outside = base / 'outside'
        outside.mkdir()
        project = base / 'symlink'
        project.mkdir()
        (project / '.agents').symlink_to(outside, target_is_directory=True)
        try:
            install.install(project, 'skill')
            raise AssertionError('symlink escape accepted')
        except ValueError:
            pass
        assert not list(outside.iterdir())
        checks.append('symlink destination escape refused')
        for mode in ['skill', 'agent']:
            project = base / ('dependency-collision-' + mode)
            dependency = project / ('.agents/skills' if mode == 'skill' else '.codex/resources') / 'fusion-design-core'
            dependency.mkdir(parents=True)
            (dependency / 'custom.txt').write_text('keep local work')
            before = install.digest_tree(project)
            try:
                install.install(project, mode)
                raise AssertionError('existing design dependency overwritten')
            except ValueError:
                pass
            assert before == install.digest_tree(project)
            checks.append(mode + ': dependency collision refuses entire install without partial writes')
        project = base / 'rollback'
        real_rename = install.os.rename
        moves = []
        def fail_second_move(src, dst):
            moves.append(dst)
            if len(moves) == 2:
                raise OSError('simulated failure during dependency installation')
            return real_rename(src, dst)
        with patch.object(install.os, 'rename', side_effect=fail_second_move):
            try:
                install.install(project, 'agent')
                raise AssertionError('simulated failure not raised')
            except OSError:
                pass
        assert not install.digest_tree(project), 'failed install left files behind'
        checks.append('failure during multi-Skill installation rolls back copied resources')
        fixture = base / 'delivery'
        fixture.mkdir()
        (fixture / 'rules.md').write_text('Rule R1 version 2\n')
        (fixture / 'decision.md').write_text('User source reference, scope R1 v2\n')
        (fixture / 'demo.html').write_text('<button>Submit</button>')
        data = {'schema_version': 1, 'rules': [{'id': 'R1', 'version': '2', 'status': 'confirmed', 'source': 'rules.md', 'source_sha256': hashlib.sha256((fixture / 'rules.md').read_bytes()).hexdigest(), 'decision_evidence': 'decision.md'}],
                'artifacts': [{'id': 'demo', 'required': True, 'status': 'done', 'path': 'demo.html', 'covers': {'R1': '2'}}]}
        assert checker.check(data, fixture)['reference_check_passed']
        checks.append('valid declared local references pass with explicit semantic limitation')
        variants = []
        d = copy.deepcopy(data); d['artifacts'][0]['covers']['R1'] = '1'; variants.append(('stale rule coverage', d))
        d = copy.deepcopy(data); d['artifacts'][0]['path'] = 'missing.html'; variants.append(('missing delivered file', d))
        d = copy.deepcopy(data); d['artifacts'][0]['path'] = '../outside'; variants.append(('delivery path escape', d))
        d = copy.deepcopy(data); d['rules'][0]['status'] = 'proposed'; variants.append(('required delivery using undecided rule', d))
        d = copy.deepcopy(data); d['artifacts'][0]['status'] = 'not_applicable'; d['artifacts'][0]['reason'] = 'skip'; variants.append(('required artifact silently marked not applicable', d))
        d = copy.deepcopy(data); d['rules'][0]['decision_evidence'] = 'missing.md'; variants.append(('missing declared decision evidence', d))
        d = copy.deepcopy(data); d['artifacts'].append(d['artifacts'][0]); variants.append(('duplicate artifact id', d))
        for label, variant in variants:
            assert not checker.check(variant, fixture)['reference_check_passed'], label
            checks.append('rejects ' + label)
        (fixture / 'rules.md').write_text('Changed rule, same declared version\n')
        assert not checker.check(data, fixture)['reference_check_passed']
        checks.append('source hash detects changed content despite unchanged declared version')
    return {'test_check_passed': True, 'checks': checks, 'count': len(checks),
            'limits': 'Offline script behavior only. Fixtures are synthetic and do not prove semantic product quality.'}


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False, indent=2))
