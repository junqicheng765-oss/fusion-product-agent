#!/usr/bin/env python3
"""Offline structural/integrity validation for the standalone package."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate():
    errors = []
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    actual = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in ROOT.rglob('*') if p.is_file() and p.name != 'manifest.json'
              and '__pycache__' not in p.parts and not p.name.endswith('.pyc')}
    if actual != manifest['files']:
        errors.extend('missing/unexpected/changed: ' + name for name in sorted(set(actual) | set(manifest['files']))
                      if actual.get(name) != manifest['files'].get(name))
    runtime = ROOT / 'skills/fusion-product-agent'
    entry = (runtime / 'SKILL.md').read_text(encoding='utf-8')
    if not entry.startswith('---\nname: fusion-product-agent\n'):
        errors.append('main Skill frontmatter/name invalid')
    skills = list((ROOT / 'skills').glob('*/SKILL.md'))
    expected_skills = {'fusion-product-agent', 'fusion-design-core', 'fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'}
    if {p.parent.name for p in skills} != expected_skills:
        errors.append('expected product entry and three bundled design Skills')
    for p in skills:
        if not p.read_text(encoding='utf-8').startswith('---\nname: ' + p.parent.name + '\n'):
            errors.append('Skill frontmatter/name invalid: ' + p.parent.name)
    metadata = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    if metadata['name'] != manifest['name'] or metadata['version'] != manifest['version']:
        errors.append('plugin and manifest identities differ')
    for p in ROOT.rglob('*.md'):
        text = p.read_text(encoding='utf-8')
        if '/Users/' in text or re.search(r'\[TODO\]|TODO:|TBD', text):
            errors.append(str(p.relative_to(ROOT)) + ': author path or scaffold marker')
        for raw in re.findall(r'\]\(([^\s)]+)\)', text):
            u = urlsplit(raw.strip('<>'))
            if u.scheme or u.netloc or not u.path:
                continue
            target = (p.parent / unquote(u.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(str(p.relative_to(ROOT)) + ': invalid local link ' + raw)
    provenance = json.loads((ROOT / 'provenance.json').read_text(encoding='utf-8'))
    design = json.loads((ROOT / 'design-source.json').read_text(encoding='utf-8'))
    expected_design = {f['destination']: f['sha256'] for f in design['files']}
    actual_design = {k: v for k, v in actual.items() if any(k.startswith('skills/' + n + '/') for n in expected_skills - {'fusion-product-agent'})}
    if expected_design != actual_design:
        errors.append('designer source adaptation inventory differs')
    for rel, expected in provenance['bundled_knowledge']['files'].items():
        p = ROOT / rel
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            errors.append('bundled knowledge differs: ' + rel)
    model = runtime / 'knowledge/product-capability-model/standards'
    capabilities = [p for p in model.rglob('*.md') if re.fullmatch(r'P[1-7]-\d+\.md', p.name)]
    if len(capabilities) != 48:
        errors.append('expected 48 secondary capability definitions')
    return {'structural_check_passed': not errors, 'errors': errors,
            'files': len(actual), 'discoverable_skills': len(skills),
            'bundled_knowledge_files': len(provenance['bundled_knowledge']['files']),
            'capability_definitions': len(capabilities),
            'limits': 'Checks structure, local reference closure and byte integrity; does not prove product quality or host runtime discovery.'}


if __name__ == '__main__':
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['structural_check_passed'] else 2)
