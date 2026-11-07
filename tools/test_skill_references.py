"""Exercise logical cross-Skill references against relocated installations."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('package_validator', ROOT / 'package/scripts/validate_package.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class SkillReferenceTests(unittest.TestCase):
    def test_complete_package_with_non_sibling_host_selected_roots(self):
        with tempfile.TemporaryDirectory(prefix='fusion relocated skills ') as folder:
            locations = {}
            for i, source in enumerate(sorted((ROOT / 'package/skills').iterdir())):
                target = Path(folder) / ('separate root ' + str(i)) / 'selected version' / source.name
                shutil.copytree(source, target)
                locations[source.name] = target
            count = 0
            for location in locations.values():
                for path in location.rglob('*.md'):
                    text = path.read_text()
                    count += len(validator.SKILL_REFERENCE.findall(text))
                    self.assertEqual(validator.skill_reference_errors(text, locations), [], str(path))
            self.assertGreater(count, 42)

    def test_missing_skill_and_resource_reported(self):
        locations = {'fusion-product-agent': ROOT / 'package/skills/fusion-product-agent'}
        self.assertTrue(validator.skill_reference_errors('技能 `fusion-missing` 内的 `SKILL.md`', locations))
        self.assertTrue(validator.skill_reference_errors('技能 `fusion-product-agent` 内的 `missing.md`', locations))

    def test_escape_absolute_encoded_and_symlink_targets_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'skill'; root.mkdir()
            outside = Path(folder) / 'outside.md'; outside.write_text('outside')
            (root / 'escape.md').symlink_to(outside)
            locations = {'fusion-test': root}
            for target in ('../outside.md', '%2e%2e/outside.md', str(outside), 'escape.md'):
                with self.subTest(target=target):
                    self.assertTrue(validator.skill_reference_errors('技能 `fusion-test` 内的 `' + target + '`', locations))

    def test_host_selected_version_used_instead_of_other_installed_version(self):
        with tempfile.TemporaryDirectory() as folder:
            old = Path(folder) / 'old'; old.mkdir()
            new = Path(folder) / 'new'; new.mkdir()
            (old / 'removed.md').write_text('obsolete')
            self.assertTrue(validator.skill_reference_errors('技能 `fusion-test` 内的 `removed.md`', {'fusion-test': new}))


if __name__ == '__main__':
    unittest.main(verbosity=2)
