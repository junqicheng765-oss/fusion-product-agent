#!/usr/bin/env python3
"""Regression-test reproducible integration without changing designer resources.

These tests exercise text adaptation and preservation, not LLM conversation behavior.
"""
from pathlib import Path
import unittest
import hashlib
import json
import subprocess
import sys
import tempfile
from unittest.mock import patch
from zipfile import ZipFile

from product_stage_adapter import adapt_copy_handoff, adapt_figma_product_stage, adapt_product_stage
from resource_location_adapter import adapt_resources
from local_refinement_adapter import bundled_resources, refine, inventory, extensions

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'downloads/fusion-product-agent-v0.3.1.zip'
PREFIX = 'fusion-product-agent-v0.3.1/'
DESIGN = 'skills/fusion-design-core/'
SHARED_ASSET_REGISTRY = DESIGN + 'resource-adapters/registry.json'
CHANGED_DESIGN = {'SKILL.md', 'methods-intake.md', 'methods-routing.md', 'methods-ui.md', 'methods-tool-routing.md', 'methods-visual.md'}


class ProductStageAdapterTests(unittest.TestCase):
    def old_bytes(self, path):
        with ZipFile(BASELINE) as archive:
            return archive.read(PREFIX + path)

    def test_existing_design_snapshot_upgrades_to_current_package(self):
        for name in sorted(CHANGED_DESIGN):
            with self.subTest(name=name):
                old = self.old_bytes(DESIGN + name).decode('utf-8')
                expected = (ROOT / 'package' / DESIGN / name).read_text(encoding='utf-8')
                self.assertEqual(refine(adapt_product_stage(old, name).encode(), DESIGN + name).decode(), expected)

    def test_reapplying_design_adapter_is_idempotent(self):
        for name in sorted(CHANGED_DESIGN):
            with self.subTest(name=name):
                old = self.old_bytes(DESIGN + name).decode('utf-8')
                text = adapt_product_stage(old, name)
                self.assertEqual(adapt_product_stage(text, name), text)
                current = (ROOT / 'package' / DESIGN / name).read_bytes()
                self.assertEqual(refine(current, DESIGN + name), current)

    def test_all_434_designer_resources_reproduce_current_bytes(self):
        prefixes = tuple(PREFIX + 'skills/' + name + '/' for name in
                         ('fusion-design-core', 'fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'))
        with ZipFile(BASELINE) as archive:
            names = [name for name in archive.namelist() if name.startswith(prefixes) and not name.endswith('/')]
            self.assertEqual(len(names), 434)
            for name in names:
                relative = name.removeprefix(PREFIX)
                raw = archive.read(name)
                path = Path(relative)
                with self.subTest(path=relative):
                    baseline = (adapt_product_stage(raw.decode(), path.name).encode()
                                if path.suffix in ('.md', '.yaml', '.yml') else raw)
                    self.assertEqual(refine(baseline, relative), (ROOT / 'package' / relative).read_bytes())

    def test_refinements_reject_unknown_input_and_extensions_are_explicit(self):
        meta = inventory()
        for relative in meta['files']:
            with self.subTest(path=relative):
                current = (ROOT / 'package' / relative).read_bytes()
                self.assertEqual(refine(current, relative), current)
                with self.assertRaisesRegex(ValueError, 'Unknown refinement input'):
                    refine(current + b'\nUnknown edit\n', relative)
        source = json.loads((ROOT / 'package/design-source.json').read_text())
        declared = {entry['destination'] for entry in source['files'] if entry.get('origin') == 'local-extension'}
        self.assertEqual(declared, set(meta['extensions']))
        self.assertEqual(len(declared), 3)
        for relative, data, record in extensions('skills/fusion-design-'):
            self.assertIsNone(record['source'])
            self.assertEqual(data, (ROOT / 'package' / relative).read_bytes())

    def test_localized_entries_reproduce_and_reject_unknown_upstream(self):
        for skill in ('fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'):
            path = 'skills/' + skill + '/SKILL.md'
            old = self.old_bytes(path).decode('utf-8')
            current = (ROOT / 'package' / path).read_text()
            self.assertEqual(adapt_resources(old, 'SKILL.md'), current)
            self.assertEqual(adapt_resources(current, 'SKILL.md'), current)
            with self.assertRaisesRegex(ValueError, 'Unknown translation input'):
                adapt_resources(old + '\nUpstream method changed.\n', 'SKILL.md')

    def test_curated_library_is_registered_on_reimport_without_duplicate_images(self):
        resources = bundled_resources('skills/fusion-design-')
        source = json.loads((ROOT / 'package/design-source.json').read_text())
        records = {entry['destination']: entry for entry in source['files']
                   if entry.get('origin') == 'bundled-visual-reference'}
        self.assertEqual(len(resources), 109)
        self.assertEqual(len([name for name, _, _ in resources if name.endswith('.webp')]), 106)
        self.assertEqual({name for name, _, _ in resources}, set(records))
        for name, data, record in resources:
            self.assertEqual(record, records[name])
            self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])

    def test_reimport_rejects_missing_or_modified_curated_resources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            overlay = root / 'tools/overlays/pr2'
            overlay.mkdir(parents=True)
            name = 'skills/fusion-design-core/visual-reference-library/images/test.webp'
            data = b'curated reference'
            record = {'sha256': hashlib.sha256(data).hexdigest()}
            (overlay / 'metadata.json').write_text(json.dumps({'bundled_resources': {name: record}}))
            with patch('local_refinement_adapter.ROOT', overlay):
                with self.assertRaisesRegex(ValueError, 'Missing bundled resource'):
                    bundled_resources('skills/fusion-design-')
                resource = root / 'package' / name
                resource.parent.mkdir(parents=True)
                resource.write_bytes(data + b'changed')
                with self.assertRaisesRegex(ValueError, 'Bundled resource digest differs'):
                    bundled_resources('skills/fusion-design-')
                resource.write_bytes(data)
                self.assertEqual(bundled_resources('skills/fusion-design-')[0][1], data)

    def test_shared_asset_libraries_are_discoverable_across_stages(self):
        router = ROOT / 'package' / DESIGN / 'scripts/resource_router.py'
        shared = {'iconscout', 'real-image-library', 'svgrepo'}
        for stage in ('research', 'flow', 'interaction', 'ui', 'asset', 'motion', 'close'):
            with self.subTest(stage=stage):
                result = subprocess.run([sys.executable, str(router), 'list', '--stage', stage],
                                        check=True, capture_output=True, text=True)
                listed = {line.split()[1] for line in result.stdout.splitlines()
                          if line.startswith('  [')}
                self.assertTrue(shared.issubset(listed))
                if stage == 'research':
                    self.assertNotIn('shadcn-ui', listed)
        registry = json.loads((ROOT / 'package' / SHARED_ASSET_REGISTRY).read_text(encoding='utf-8'))
        for adapter in registry['adapters']:
            if adapter['id'] in shared:
                with self.subTest(adapter=adapter['id']):
                    for field in ('mode', 'search', 'returns', 'acquire', 'license', 'fallback'):
                        self.assertTrue(adapter.get(field), field)


    def test_figma_upgrade_is_reproducible_and_idempotent(self):
        relative = 'skills/fusion-figma-workflow/SKILL.md'
        old = self.old_bytes(relative).decode('utf-8')
        current = (ROOT / 'package' / relative).read_text(encoding='utf-8')
        baseline = adapt_figma_product_stage(old)
        self.assertEqual(refine(baseline.encode(), relative).decode(), current)
        self.assertEqual(adapt_figma_product_stage(baseline), baseline)
        self.assertEqual(refine(current.encode(), relative).decode(), current)

    def test_figma_execution_manuals_are_preserved_or_reproducibly_adapted(self):
        with ZipFile(BASELINE) as archive:
            names = [name for name in archive.namelist()
                     if name.startswith(PREFIX + 'skills/fusion-figma-workflow/references/') and not name.endswith('/')]
            self.assertEqual(len(names), 6)
            for name in names:
                relative = name.removeprefix(PREFIX)
                with self.subTest(path=relative):
                    target = relative.removeprefix('skills/fusion-figma-workflow/')
                    original = archive.read(name).decode('utf-8')
                    current = (ROOT / 'package' / relative).read_text(encoding='utf-8')
                    baseline = adapt_copy_handoff(original, target)
                    self.assertEqual(refine(baseline.encode(), relative).decode(), current)
                    self.assertEqual(adapt_copy_handoff(baseline, target), baseline)

    def test_missing_upstream_anchor_fails_instead_of_silent_partial_adaptation(self):
        old = self.old_bytes(DESIGN + 'SKILL.md').decode('utf-8')
        old = old.replace('2. **0→1 需求必须严格分【两轮】推进', 'Upstream workflow was changed')
        with self.assertRaisesRegex(ValueError, 'replacement anchor'):
            adapt_product_stage(old, 'SKILL.md')

    def test_ambiguous_upstream_anchor_is_rejected(self):
        old = self.old_bytes(DESIGN + 'methods-intake.md').decode('utf-8')
        old += '\n## 1. 提取任务事实\n'
        with self.assertRaisesRegex(ValueError, 'insertion anchor'):
            adapt_product_stage(old, 'methods-intake.md')

    def test_unrelated_methods_are_not_rewritten(self):
        text = self.old_bytes(DESIGN + 'methods-research.md').decode('utf-8')
        self.assertEqual(adapt_product_stage(text, 'methods-research.md'), text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
