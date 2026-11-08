#!/usr/bin/env python3
"""Regression-test the imported baseline and declared local design refinements.

These tests exercise adaptation, preservation and resource discovery, not LLM conversation behavior.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import unittest
from zipfile import ZipFile

from product_stage_adapter import adapt_figma_product_stage, adapt_product_stage

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'downloads/fusion-product-agent-v0.3.1.zip'
PREFIX = 'fusion-product-agent-v0.3.1/'
DESIGN = 'skills/fusion-design-core/'
CHANGED_DESIGN = {'SKILL.md', 'methods-intake.md', 'methods-routing.md'}
SHARED_ASSET_REGISTRY = DESIGN + 'resource-adapters/registry.json'
STYLE_RESOURCE_REGISTRY = DESIGN + 'style-presets/registry.json'
IMPORTED_RUNTIME_REFINEMENTS = {
    DESIGN + 'scripts/' + name for name in (
        'verify_library_usage.py', 'ui_geometry_audit.py', 'side_by_side.py',
        'style_preset.py', 'style_consistency_audit.py')
}
SOURCE = json.loads((ROOT / 'package/design-source.json').read_text(encoding='utf-8'))
INVENTORY = {entry['destination']: entry for entry in SOURCE['files']}
FIGMA_SOURCE = json.loads((ROOT / 'package/figma-source.json').read_text(encoding='utf-8'))
FIGMA_INVENTORY = {entry['destination']: entry for entry in FIGMA_SOURCE['files']}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def integration_digest(relative):
    entry = INVENTORY[relative]
    return entry.get('integration_sha256', entry['sha256'])


class ProductStageAdapterTests(unittest.TestCase):
    def old_bytes(self, path):
        with ZipFile(BASELINE) as archive:
            return archive.read(PREFIX + path)

    def test_existing_design_snapshot_upgrades_to_recorded_integration_baseline(self):
        for name in sorted(CHANGED_DESIGN):
            with self.subTest(name=name):
                old = self.old_bytes(DESIGN + name).decode('utf-8')
                result = adapt_product_stage(old, name).encode('utf-8')
                self.assertEqual(digest(result), integration_digest(DESIGN + name))

    def test_reapplying_design_adapter_is_idempotent(self):
        for name in sorted(CHANGED_DESIGN):
            with self.subTest(name=name):
                old = self.old_bytes(DESIGN + name).decode('utf-8')
                text = adapt_product_stage(old, name)
                self.assertEqual(adapt_product_stage(text, name), text)

    def test_imported_resources_preserve_baseline_and_declared_current_bytes(self):
        prefixes = tuple(PREFIX + 'skills/' + name + '/' for name in
                         ('fusion-design-core', 'fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'))
        with ZipFile(BASELINE) as archive:
            names = [name for name in archive.namelist() if name.startswith(prefixes) and not name.endswith('/')]
            self.assertEqual(len(names), 434)
            for name in names:
                relative = name.removeprefix(PREFIX)
                with self.subTest(path=relative):
                    entry = INVENTORY[relative]
                    current = (ROOT / 'package' / relative).read_bytes()
                    self.assertEqual(digest(current), entry['sha256'])
                    if relative not in {DESIGN + filename for filename in CHANGED_DESIGN}:
                        self.assertEqual(digest(archive.read(name)), integration_digest(relative))
                    if entry.get('local_refinement'):
                        self.assertTrue(relative.startswith(DESIGN))
                        self.assertTrue(relative.endswith('.md') or relative in {SHARED_ASSET_REGISTRY, STYLE_RESOURCE_REGISTRY}
                                        or relative in IMPORTED_RUNTIME_REFINEMENTS)
                        self.assertNotEqual(entry['integration_sha256'], entry['sha256'])

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

    def test_local_extensions_and_refinement_inventory_are_explicit(self):
        local = SOURCE['local_refinements']
        changed = {path for path, entry in INVENTORY.items() if entry.get('local_refinement')}
        self.assertEqual(changed, set(local['changed_imported_files']))
        additions = {path for path, entry in INVENTORY.items() if entry.get('origin') == 'local-extension'}
        self.assertEqual(additions, set(local['added_files']))
        self.assertEqual(additions, {DESIGN + 'methods-creative-concept.md',
                                     DESIGN + 'methods-deliverable-routing.md',
                                     DESIGN + 'workflow-product-interface.md'})
        for path in additions:
            with self.subTest(path=path):
                self.assertIsNone(INVENTORY[path]['source'])
                self.assertIsNone(INVENTORY[path]['source_sha256'])
                self.assertEqual(digest((ROOT / 'package' / path).read_bytes()), INVENTORY[path]['sha256'])

    def test_figma_upgrade_is_reproducible_and_idempotent(self):
        relative = 'skills/fusion-figma-workflow/SKILL.md'
        old = self.old_bytes(relative).decode('utf-8')
        integrated = adapt_figma_product_stage(old)
        entry = FIGMA_INVENTORY[relative]
        self.assertEqual(digest(integrated.encode('utf-8')), entry.get('integration_sha256', entry['sha256']))
        self.assertEqual(adapt_figma_product_stage(integrated), integrated)
        self.assertEqual(digest((ROOT / 'package' / relative).read_bytes()), entry['sha256'])

    def test_figma_manual_baseline_and_current_adaptations_are_preserved(self):
        with ZipFile(BASELINE) as archive:
            names = [name for name in archive.namelist()
                     if name.startswith(PREFIX + 'skills/fusion-figma-workflow/references/') and not name.endswith('/')]
            self.assertEqual(len(names), 6)
            for name in names:
                relative = name.removeprefix(PREFIX)
                with self.subTest(path=relative):
                    entry = FIGMA_INVENTORY[relative]
                    self.assertEqual(digest(archive.read(name)), entry.get('integration_sha256', entry['sha256']))
                    self.assertEqual(digest((ROOT / 'package' / relative).read_bytes()), entry['sha256'])

    def test_figma_local_refinement_scope_is_explicit(self):
        changed = {path for path, entry in FIGMA_INVENTORY.items() if entry.get('local_refinement')}
        self.assertEqual(changed, set(FIGMA_SOURCE['local_refinements']['changed_imported_files']))
        for path in changed:
            with self.subTest(path=path):
                self.assertTrue(path.startswith('skills/fusion-figma-workflow/'))
                self.assertTrue(path.endswith('.md'))
                self.assertNotEqual(FIGMA_INVENTORY[path]['integration_sha256'], FIGMA_INVENTORY[path]['sha256'])

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
