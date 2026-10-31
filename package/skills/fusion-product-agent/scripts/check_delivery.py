#!/usr/bin/env python3
"""Check declared delivery references; never certifies semantics or user approval."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit


def check(data, root):
    root = Path(root).resolve()
    errors, warnings = [], []
    if data.get('schema_version') != 1:
        errors.append('schema_version must be 1')
    rules, artifacts = {}, {}
    for collection, index in [('rules', rules), ('artifacts', artifacts)]:
        rows = data.get(collection)
        if not isinstance(rows, list):
            errors.append(collection + ' must be a list')
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
                errors.append(collection + ' entry needs a nonempty id')
                continue
            rid = row['id']
            if rid in index:
                errors.append('duplicate ' + collection + ' id: ' + rid)
            index[rid] = row
    def local_path(value, label, expected_hash=None):
        if not isinstance(value, str) or not value:
            errors.append(label + ': nonempty local path required')
            return
        if urlsplit(value).scheme:
            errors.append(label + ': local path required; external links need manual evidence')
            return
        target = (root / value).resolve()
        if not target.is_relative_to(root):
            errors.append(label + ': path escapes project')
        elif not target.is_file():
            errors.append(label + ': missing file ' + value)
        elif expected_hash is not None and hashlib.sha256(target.read_bytes()).hexdigest() != expected_hash:
            errors.append(label + ': content hash changed ' + value)
    for rid, rule in rules.items():
        if not isinstance(rule.get('version'), str) or not rule['version']:
            errors.append(rid + ': rule version required')
        local_path(rule.get('source'), rid + ' source', rule.get('source_sha256'))
        if not rule.get('source_sha256'):
            warnings.append(rid + ': no source hash; unchanged version cannot prove unchanged content')
        if rule.get('status') not in ['confirmed', 'delegated', 'proposed']:
            errors.append(rid + ': status must be confirmed, delegated or proposed')
        if rule.get('status') in ['confirmed', 'delegated']:
            local_path(rule.get('decision_evidence'), rid + ' decision_evidence')
    for aid, artifact in artifacts.items():
        status = artifact.get('status')
        if status not in ['done', 'draft', 'blocked', 'not_applicable']:
            errors.append(aid + ': invalid artifact status')
        if not isinstance(artifact.get('required'), bool):
            errors.append(aid + ': required must be boolean')
        if status == 'not_applicable':
            if artifact.get('required'):
                errors.append(aid + ': required artifact cannot be not_applicable; resolve contract explicitly')
            if not artifact.get('reason'):
                errors.append(aid + ': not_applicable needs reason')
            continue
        if status == 'done':
            local_path(artifact.get('path'), aid, artifact.get('sha256'))
        elif artifact.get('required'):
            errors.append(aid + ': required artifact not done')
        covered = artifact.get('covers', {})
        if not isinstance(covered, dict):
            errors.append(aid + ': covers must map rule ids to versions')
            continue
        for rid, version in covered.items():
            if rid not in rules:
                errors.append(aid + ': unknown rule ' + rid)
            elif version != rules[rid].get('version'):
                errors.append(aid + ': stale rule reference ' + rid)
            elif artifact.get('required') and rules[rid].get('status') == 'proposed':
                errors.append(aid + ': required delivery depends on proposed rule ' + rid)
        if status == 'done' and not covered:
            warnings.append(aid + ': no rule coverage declared; manual review needed')
    if not artifacts:
        errors.append('at least one artifact required')
    return {'reference_check_passed': not errors, 'errors': errors, 'warnings': warnings,
            'limits': 'Only checks declared local files, ids, decision-evidence existence and rule-version references. Does not prove coverage completeness, semantic consistency, authenticity, usability or production capability.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root', type=Path, help='Project root; defaults to manifest parent')
    args = parser.parse_args()
    root = (args.root or args.manifest.parent).resolve()
    try:
        data = json.loads(args.manifest.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('manifest must be an object')
        result = check(data, root)
    except (ValueError, OSError, TypeError) as exc:
        result = {'reference_check_passed': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['reference_check_passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
