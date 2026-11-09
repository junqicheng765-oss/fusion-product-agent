"""Replay reviewed PR refinements after the deterministic rc.6 import adapters."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent / 'overlays' / 'pr2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory():
    return json.loads((ROOT / 'metadata.json').read_text(encoding='utf-8'))


def refine(data, relative):
    record = inventory()['files'].get(relative)
    if record is None:
        return data
    if digest(data) == record['sha256']:
        return data
    if digest(data) != record['baseline_sha256']:
        raise ValueError('Unknown refinement input: ' + relative)
    patch = ROOT / record['patch']
    if digest(patch.read_bytes()) != record['patch_sha256']:
        raise ValueError('Refinement patch digest differs: ' + relative)
    with tempfile.TemporaryDirectory(prefix='fusion-refinement-') as temporary:
        target = Path(temporary) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        subprocess.run(['git', 'apply', '--whitespace=error', str(patch)], cwd=temporary,
                       check=True, capture_output=True)
        result = target.read_bytes()
    if digest(result) != record['sha256']:
        raise ValueError('Refinement output differs: ' + relative)
    return result


def source_record(record, baseline):
    relative = record['destination']
    record['sha256'] = digest(refine(baseline, relative))
    if relative in inventory()['files']:
        record.update(integration_sha256=digest(baseline), local_refinement=True)
    return record


def extensions(prefix):
    result = []
    for relative, record in inventory()['extensions'].items():
        if not relative.startswith(prefix):
            continue
        data = (ROOT / record['file']).read_bytes()
        if digest(data) != record['sha256']:
            raise ValueError('Local extension digest differs: ' + relative)
        result.append((relative, data, dict(source=None, destination=relative,
                      source_sha256=None, sha256=digest(data), adapted=False,
                      origin='local-extension')))
    return result


def bundled_resources(prefix):
    """Retain the single canonical copy of separately curated package resources.

    These authored resources are versioned with the package, not imported from
    the older designer repository. Missing or changed data must be reviewed or
    restored from Git before import; it must never disappear from provenance.
    """
    package = ROOT.parents[2] / 'package'
    result = []
    for relative, record in inventory().get('bundled_resources', {}).items():
        if not relative.startswith(prefix):
            continue
        path = package / relative
        if not path.resolve().is_relative_to(package.resolve()) or not path.is_file():
            raise ValueError('Missing bundled resource; restore from Git: ' + relative)
        data = path.read_bytes()
        if digest(data) != record['sha256']:
            raise ValueError('Bundled resource digest differs: ' + relative)
        result.append((relative, data, dict(record)))
    return result


def provenance(prefix):
    data = inventory()
    return dict(date='2026-11-09', pr=data['pr'], pr_head=data['pr_head'],
                integrated_prs=data.get('integrated_prs', []),
                integration_baseline='0.3.6-rc.6',
                changed_imported_files=[p for p in data['files'] if p.startswith(prefix)],
                added_files=[p for p in data['extensions'] if p.startswith(prefix)],
                bundled_files=[p for p in data.get('bundled_resources', {}) if p.startswith(prefix)],
                rebuild_note='Import adapters reconstruct the rc.6 baseline; hash-pinned PR2/PR4 patches and explicit local extensions are replayed automatically. Separately curated resources remain in their single Git-versioned package location and are hash-checked and registered again. Missing resources must be restored from Git; unknown inputs fail.')
