#!/usr/bin/env python3
"""Regression-test reproducible integration without changing designer resources.

These tests exercise text adaptation and preservation, not LLM conversation behavior.
"""
from pathlib import Path
import unittest
from zipfile import ZipFile

from product_stage_adapter import adapt_figma_product_stage, adapt_product_stage

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'downloads/fusion-product-agent-v0.3.1.zip'
PREFIX = 'fusion-product-agent-v0.3.1/'
DESIGN = 'skills/fusion-design-core/'
CHANGED_DESIGN = {'SKILL.md', 'methods-intake.md', 'methods-routing.md'}


class ProductStageAdapterTests(unittest.TestCase):
    def old_bytes(self, path):
        with ZipFile(BASELINE) as archive:
            return archive.read(PREFIX + path)

    def test_existing_design_snapshot_upgrades_to_current_package(self):
        for name in sorted(CHANGED_DESIGN):
            with self.subTest(name=name):
                old = self.old_bytes(DESIGN + name).decode('utf-8')
                expected = (ROOT / 'package' / DESIGN / name).read_text(encoding='utf-8')
                self.assertEqual(adapt_product_stage(old, name), expected)

    def test_reapplying_design_adapter_is_idempotent(self):
        for name in sorted(CHANGED_DESIGN):
            with self.subTest(name=name):
                text = (ROOT / 'package' / DESIGN / name).read_text(encoding='utf-8')
                self.assertEqual(adapt_product_stage(text, name), text)

    def test_all_other_designer_resources_remain_byte_identical(self):
        prefixes = tuple(PREFIX + 'skills/' + name + '/' for name in
                         ('fusion-design-core', 'fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'))
        with ZipFile(BASELINE) as archive:
            names = [name for name in archive.namelist() if name.startswith(prefixes) and not name.endswith('/')]
            self.assertEqual(len(names), 434)
            for name in names:
                relative = name.removeprefix(PREFIX)
                if relative in {DESIGN + filename for filename in CHANGED_DESIGN}:
                    continue
                with self.subTest(path=relative):
                    self.assertEqual(archive.read(name), (ROOT / 'package' / relative).read_bytes())

    def test_figma_upgrade_is_reproducible_and_idempotent(self):
        relative = 'skills/fusion-figma-workflow/SKILL.md'
        old = self.old_bytes(relative).decode('utf-8')
        current = (ROOT / 'package' / relative).read_text(encoding='utf-8')
        self.assertEqual(adapt_figma_product_stage(old), current)
        self.assertEqual(adapt_figma_product_stage(current), current)

    def test_figma_execution_manuals_are_preserved(self):
        with ZipFile(BASELINE) as archive:
            names = [name for name in archive.namelist()
                     if name.startswith(PREFIX + 'skills/fusion-figma-workflow/references/') and not name.endswith('/')]
            self.assertEqual(len(names), 6)
            for name in names:
                relative = name.removeprefix(PREFIX)
                with self.subTest(path=relative):
                    self.assertEqual(archive.read(name), (ROOT / 'package' / relative).read_bytes())

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
