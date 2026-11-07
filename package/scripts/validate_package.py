#!/usr/bin/env python3
"""Offline structural/integrity validation for the standalone package."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL_REFERENCE = re.compile(r'技能\s+`([^`]+)`\s+内的\s+`([^`]+)`')


def skill_reference_errors(text, locations):
    """Validate logical references using host-selected Skill roots, not siblings."""
    errors = []
    for name, relative in SKILL_REFERENCE.findall(text):
        if name not in locations:
            errors.append('unknown Skill: ' + name)
            continue
        root = Path(locations[name]).resolve()
        path = unquote(urlsplit(relative).path)
        target = (root / path).resolve()
        if Path(path).is_absolute() or not target.is_relative_to(root) or not target.is_file():
            errors.append('invalid Skill resource: ' + name + '/' + relative)
    return errors


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
    design_skills = {'fusion-design-core', 'fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'}
    expected_skills = design_skills | {'fusion-product-agent', 'fusion-figma-workflow'}
    if {p.parent.name for p in skills} != expected_skills:
        errors.append('expected product entry, three design Skills and bundled Figma execution Skill')
    for p in skills:
        if not p.read_text(encoding='utf-8').startswith('---\nname: ' + p.parent.name + '\n'):
            errors.append('Skill frontmatter/name invalid: ' + p.parent.name)
    metadata = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    if metadata['name'] != manifest['name'] or metadata['version'] != manifest['version']:
        errors.append('plugin and manifest identities differ')
    locations = {p.parent.name: p.parent for p in skills}
    logical_references = 0
    for p in ROOT.rglob('*.md'):
        text = p.read_text(encoding='utf-8')
        logical_references += len(SKILL_REFERENCE.findall(text))
        errors.extend(str(p.relative_to(ROOT)) + ': ' + error
                      for error in skill_reference_errors(text, locations))
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
    actual_design = {k: v for k, v in actual.items() if any(k.startswith('skills/' + n + '/') for n in design_skills)}
    if expected_design != actual_design:
        errors.append('designer source adaptation inventory differs')
    figma = json.loads((ROOT / 'figma-source.json').read_text(encoding='utf-8'))
    expected_figma = {f['destination']: f['sha256'] for f in figma['files']}
    actual_figma = {k: v for k, v in actual.items() if k.startswith('skills/fusion-figma-workflow/')}
    if expected_figma != actual_figma:
        errors.append('Figma execution source adaptation inventory differs')
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
            'logical_skill_references': logical_references,
            'bundled_knowledge_files': len(provenance['bundled_knowledge']['files']),
            'capability_definitions': len(capabilities),
            'limits': 'Checks structure, local reference closure and byte integrity; does not prove product quality or host runtime discovery.'}


if __name__ == '__main__':
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['structural_check_passed'] else 2)
