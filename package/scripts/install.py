#!/usr/bin/env python3
"""Install an isolated project Skill OR custom agent, without editing global files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

NAME = 'fusion-product-agent'
PACKAGE = Path(__file__).resolve().parents[1]


def digest_tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def install(project, mode, dry_run=False):
    if mode not in ('skill', 'agent'):
        raise ValueError('Unsupported installation mode')
    project = project.expanduser().resolve()
    if project in [Path('/'), Path.home(), Path.home() / '.codex', Path.home() / '.agents']:
        raise ValueError('Choose a dedicated project directory, not home or global config')
    if project.exists() and not project.is_dir():
        raise ValueError('Project must be a directory')
    relative = '.agents/skills/' + NAME if mode == 'skill' else '.codex/resources/' + NAME
    target = project / relative
    sources = sorted(p for p in (PACKAGE / 'skills').iterdir() if (p / 'SKILL.md').is_file())
    resources = {p.name: target.parent / p.name for p in sources}
    preset = project / '.codex/agents' / (NAME + '.toml')
    record = project / '.codex' / (NAME + '-install.json')
    config = project / '.codex/config.toml'
    destinations = list(resources.values()) + [record] + ([preset] if mode == 'agent' else [])
    for dest in destinations + [config]:
        if not dest.resolve().is_relative_to(project):
            raise ValueError('Destination resolves outside project: ' + str(dest))
    for dest in destinations:
        if dest.exists() or dest.is_symlink():
            raise ValueError('Refusing to overwrite existing installation: ' + str(dest))
    manifest = json.loads((PACKAGE / 'manifest.json').read_text(encoding='utf-8'))
    for rel, expected in manifest['files'].items():
        p = PACKAGE / rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError('Package integrity failed: ' + rel)
    plan = {'project': str(project), 'mode': mode, 'skill_or_resource': str(target),
            'resources': {name: str(dest) for name, dest in resources.items()},
            'preset': str(preset) if mode == 'agent' else None,
            'create_project_config': mode == 'agent' and not config.exists(),
            'existing_config_preserved': config.exists(), 'global_changes': False,
            'version': manifest['version'], 'dry_run': dry_run}
    if dry_run:
        return plan
    project.mkdir(parents=True, exist_ok=True)
    created = []
    staging = Path(tempfile.mkdtemp(prefix='.fusion-install-', dir=project))
    try:
        for source in sources:
            shutil.copytree(source, staging / source.name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        target.parent.mkdir(parents=True, exist_ok=True)
        for name, dest in resources.items():
            os.rename(staging / name, dest)
            created.append(dest)
        if mode == 'agent':
            preset.parent.mkdir(parents=True, exist_ok=True)
            instructions = (
                '你是融合产品锤，使用父任务的业务工作区和授权范围。\n'
                '先读取规则根目录的SKILL.md，按当前任务加载同包参考，不读取原三套或作者本机路径。\n'
                '规则根目录：' + str(target) + '\n'
                '规则目录不是业务产物目录。用户决定由父任务统一询问，不重复访谈。\n'
                '只读委派不写项目基线；写入任务按明确责任完成，保留他人成果。\n'
                '返回实际成果、验证层次、限制及待决事项，不把自检写成独立验收。'
            )
            text = 'name = "fusion-product-agent"\ndescription = "融合产品锤：业务表达、可操作体验与复杂规则追溯。"\ndeveloper_instructions = ' + json.dumps(instructions, ensure_ascii=False) + '\n'
            with preset.open('x', encoding='utf-8') as handle:
                handle.write(text)
            created.append(preset)
            if not config.exists():
                with config.open('x', encoding='utf-8') as handle:
                    handle.write('[agents]\nenabled = true\n')
                created.append(config)
        record.parent.mkdir(parents=True, exist_ok=True)
        with record.open('x', encoding='utf-8') as handle:
            json.dump({**plan, 'files': digest_tree(target),
                       'resource_files': {name: digest_tree(dest) for name, dest in resources.items()}},
                      handle, ensure_ascii=False, indent=2)
        created.append(record)
    except Exception:
        for p in reversed(created):
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(staging)
    plan['installed'] = True
    plan['load_note'] = 'Use a fresh project chat. Static installation alone does not prove runtime discovery or model execution. Existing project config may require agent enablement; it was preserved.'
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--mode', required=True, choices=['skill', 'agent'])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.project, args.mode, args.dry_run), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    main()
