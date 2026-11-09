#!/usr/bin/env python3
"""Test reference curation, safe retrieval, integrity, and real isolated installs.

Run: python3 -m unittest discover -s tools -p test_visual_reference_library.py -v
No test rebuilds or edits the repository package manifest.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'package'
SCRIPT = PACKAGE / 'skills/fusion-design-core/scripts/visual_reference.py'
LIBRARY = SCRIPT.parents[1] / 'visual-reference-library'
AUDIT = PACKAGE / 'visual-reference-source.json'
INSTALLER = PACKAGE / 'scripts/install.py'
spec = importlib.util.spec_from_file_location('fusion_visual_reference', SCRIPT)
visual_reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visual_reference)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run_json(script, *arguments, cwd=None):
    result = subprocess.run([sys.executable, str(script), *arguments], cwd=cwd,
                            text=True, capture_output=True, check=False)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError('Expected JSON output; stdout=' + result.stdout[:1000] + '; stderr=' + result.stderr[:1000]) from exc
    return result, payload


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fusion-visual-reference-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / 'skill'
        self.script = self.skill / 'scripts/visual_reference.py'
        self.script.parent.mkdir(parents=True)
        shutil.copy2(SCRIPT, self.script)
        self.library = self.skill / 'visual-reference-library'
        (self.library / 'images').mkdir(parents=True)
        self.catalog = {
            'schema_version': 1, 'scope': 'global-visual-reference', 'curated_on': '2026-11-07',
            'families': [{'id': key, 'label': key, 'description': 'family ' + key} for key in visual_reference.FAMILIES],
            'roles': [{'id': key, 'label': key} for key in visual_reference.ROLES],
            'images': [],
        }
        self.add_image('DESCRIPTION', b'description image', 'ordinary texture', 'A long description mentions Knit and warm paper.', ['纸艺'], ['paper-collage'], ['material'])
        self.add_image('KNIT', b'knitted image', 'warm character', 'A soft character.', ['Knit', '针织', 'warm'], ['tactile-3d'], ['material', 'kv'])
        self.add_image('POSTER', b'poster image', 'paper poster', 'A graphic composition.', ['paper'], ['paper-collage'], ['composition', 'kv'])
        self.save()

    def add_image(self, identifier, data, title, summary, tags, families, roles):
        relative = 'images/' + identifier.lower() + '.webp'
        (self.library / relative).write_bytes(data)
        self.catalog['images'].append({
            'id': identifier, 'file': relative, 'sha256': sha(data), 'width': 64, 'height': 64,
            'title': title, 'summary': summary, 'families': families, 'roles': roles,
            'tags': {key: tags if key == 'material' else [] for key in visual_reference.TAG_FIELDS},
            'observations': {key: [] for key in visual_reference.OBSERVATION_FIELDS},
            'source': {'filename': identifier.lower() + '.webp', 'url_hint': None,
                       'url_verified': False, 'publication_date': None, 'license_status': 'unverified'},
            'review': {'decision': 'include', 'ui_reference': False, 'reason': 'Static art reference.'},
            'limitations': ['Original publication date is unknown.'],
        })

    def save(self, reindex=True):
        if reindex:
            self.catalog['indexes'] = visual_reference.expected_indexes(self.catalog)
        (self.library / 'catalog.json').write_text(json.dumps(self.catalog, ensure_ascii=False), encoding='utf-8')

    def call(self, *arguments):
        return run_json(self.script, *arguments, cwd=self.root)

    def assert_fails(self, *arguments, contains=None):
        process, payload = self.call(*arguments)
        self.assertNotEqual(process.returncode, 0)
        self.assertFalse(payload['ok'])
        self.assertNotIn('Traceback', process.stderr + process.stdout)
        if contains:
            self.assertIn(contains, json.dumps(payload))

    def test_list_counts_without_dumping_images(self):
        process, payload = self.call('list')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(payload['image_count'], 3)
        self.assertNotIn('images', payload)
        self.assertNotIn('results', payload)
        self.assertEqual(next(item['count'] for item in payload['roles'] if item['id'] == 'material'), 2)

    def test_search_exact_tag_ranks_above_description_and_all_terms_are_required(self):
        process, payload = self.call('search', 'kNiT', '--role', 'material')
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual([item['id'] for item in payload['results']], ['KNIT', 'DESCRIPTION'])
        first = payload['results'][0]
        self.assertTrue(Path(first['image_path']).is_absolute())
        self.assertIn('tags.material', first['matched_fields'][0]['exact_tag_fields'])
        self.assertIsNone(first['publication_date'])
        self.assertEqual(first['date_note'], '原作日期未知')
        self.assertNotIn('score', first)
        self.assertNotIn('rank', first)
        _, filtered = self.call('search', 'knit warm', '--family', 'tactile-3d', '--role', 'material', '--limit', '1')
        self.assertEqual([item['id'] for item in filtered['results']], ['KNIT'])
        process, empty = self.call('search', 'knit', 'absent')
        self.assertEqual(process.returncode, 0)
        self.assertEqual(empty['total_matches'], 0)

    def test_search_limit_and_argument_errors_are_json(self):
        for arguments in [('search', 'knit', '--limit', '13'), ('search', 'knit', '--limit', '0'),
                          ('search', 'knit', '--limit', 'text'), ('search', 'knit', '--role', 'unknown'),
                          ('search',), ('unknown',)]:
            with self.subTest(arguments=arguments):
                self.assert_fails(*arguments)

    def test_missing_malformed_and_invalid_metadata_errors_are_json(self):
        catalog_path = self.library / 'catalog.json'
        catalog_path.unlink()
        self.assert_fails('list', contains='missing')
        catalog_path.write_text('{broken json', encoding='utf-8')
        self.assert_fails('validate', contains='cannot read reference catalog')
        self.catalog['schema_version'] = True
        self.save()
        self.assert_fails('validate', contains='schema_version')

    def test_show_contains_complete_metadata_and_absolute_image_path(self):
        process, payload = self.call('show', 'KNIT')
        self.assertEqual(process.returncode, 0, process.stderr)
        expected = next(item for item in self.catalog['images'] if item['id'] == 'KNIT')
        for key, value in expected.items():
            self.assertEqual(payload[key], value)
        self.assertEqual(Path(payload['image_path']), (self.library / expected['file']).resolve())
        self.assert_fails('show', 'ABSENT', contains='unknown reference id')

    def test_validate_accepts_intact_library(self):
        process, payload = self.call('validate')
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(payload['error_count'], 0)
        self.assertEqual(payload['verified_hashes'], 3)

    def test_tampering_is_detected_only_by_explicit_hash_validation(self):
        (self.library / 'images/knit.webp').write_bytes(b'tampered')
        for arguments in [('list',), ('search', '针织', '--role', 'material')]:
            process, _payload = self.call(*arguments)
            self.assertEqual(process.returncode, 0, process.stderr)
        self.assert_fails('validate', contains='sha256 mismatch')

    def test_validate_rejects_path_escape_and_absolute_paths(self):
        for relative in ('images/../../outside.webp', '../outside.webp', '/tmp/outside.webp',
                         'C:/outside.webp', 'images\\outside.webp', 'images/./knit.webp'):
            with self.subTest(relative=relative):
                self.catalog['images'][1]['file'] = relative
                self.save()
                self.assert_fails('validate')
                self.assert_fails('show', 'KNIT')

    def test_validate_rejects_symlink_files_and_directories(self):
        target = self.library / 'images/knit.webp'
        target.unlink()
        target.symlink_to(self.library / 'images/poster.webp')
        self.assert_fails('validate', contains='symlink')
        self.assert_fails('show', 'KNIT', contains='symlink')
        target.unlink()
        target.write_bytes(b'knitted image')
        (self.library / 'images/linked-directory').symlink_to(self.root, target_is_directory=True)
        self.assert_fails('validate', contains='symlink')

    def test_validate_rejects_catalog_and_library_symlinks(self):
        catalog = self.library / 'catalog.json'
        copy = self.root / 'catalog-copy.json'
        catalog.rename(copy)
        catalog.symlink_to(copy)
        self.assert_fails('validate', contains='symlink')
        catalog.unlink()
        copy.rename(catalog)
        original = self.root / 'library-copy'
        self.library.rename(original)
        self.library.symlink_to(original, target_is_directory=True)
        self.assert_fails('validate', contains='symlink')

    def test_validate_rejects_all_three_index_mismatches(self):
        for index in ('family', 'role', 'tag'):
            with self.subTest(index=index):
                self.catalog['indexes'] = visual_reference.expected_indexes(self.catalog)
                key = next(key for key, values in self.catalog['indexes'][index].items() if values)
                self.catalog['indexes'][index][key] = []
                self.save(reindex=False)
                self.assert_fails('validate', contains='index mismatch: ' + index)

    def test_validate_rejects_unlisted_missing_and_duplicate_resources(self):
        extra = self.library / 'images/unlisted.webp'
        extra.write_bytes(b'unlisted')
        self.assert_fails('validate', contains='unlisted image resource')
        extra.unlink()
        target = self.library / 'images/knit.webp'
        target.unlink()
        self.assert_fails('validate', contains='missing')
        target.write_bytes(b'knitted image')
        for key in ('id', 'sha256', 'file'):
            with self.subTest(key=key):
                original = self.catalog['images'][1][key]
                self.catalog['images'][1][key] = self.catalog['images'][0][key]
                self.save()
                self.assert_fails('validate', contains='duplicate ' + key)
                self.catalog['images'][1][key] = original

    def test_validate_rejects_unknown_enums_and_ui_review(self):
        for key in ('families', 'roles'):
            original = self.catalog['images'][0][key]
            self.catalog['images'][0][key] = ['unknown']
            self.save(reindex=False)
            self.assert_fails('validate', contains='invalid ' + key)
            self.catalog['images'][0][key] = original
        self.catalog['images'][0]['review']['ui_reference'] = True
        self.save()
        self.assert_fails('validate', contains='non-UI')


class PackagedLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((LIBRARY / 'catalog.json').read_text(encoding='utf-8'))
        cls.audit = json.loads(AUDIT.read_text(encoding='utf-8'))

    def test_independent_curation_audit_matches_only_included_resource_hashes(self):
        records = self.audit['records']
        self.assertEqual(len({item['sha256'] for item in records}), len(records))
        self.assertEqual(self.audit['unique_images'], len(records))
        self.assertEqual(self.audit['input_files'], sum(len(item['sources']) for item in records))
        self.assertTrue(all(item['decision'] in ('include', 'exclude-ui') for item in records))
        included = {item['sha256'] for item in records if item['decision'] == 'include'}
        excluded = {item['sha256'] for item in records if item['decision'] == 'exclude-ui'}
        actual = {sha(path.read_bytes()) for path in (LIBRARY / 'images').rglob('*') if path.is_file()}
        self.assertTrue(included)
        self.assertTrue(excluded)
        self.assertTrue(included.isdisjoint(excluded))
        self.assertEqual(included, actual)
        self.assertTrue(actual.isdisjoint(excluded))
        self.assertEqual({item['sha256'] for item in self.catalog['images']}, actual)
        self.assertEqual(self.audit['bundled_images'], len(included))
        self.assertEqual(self.audit['excluded_ui'], len(excluded))
        self.assertEqual(len(self.catalog['images']), len(included))
        self.assertTrue(all(source['collection'] in ('first', 'second') for item in records for source in item['sources']))

    def test_real_material_query_show_and_validate(self):
        process, payload = run_json(SCRIPT, 'search', '针织', '--role', 'material', cwd=ROOT.parent)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertGreater(payload['total_matches'], 0, 'The curated library must include a knitting material reference')
        self.assertLessEqual(payload['returned'], 6)
        for hit in payload['results']:
            self.assertIn('material', hit['roles'])
            self.assertTrue(Path(hit['image_path']).is_file())
            self.assertTrue(hit['matched_fields'])
        identifier = payload['results'][0]['id']
        process, shown = run_json(SCRIPT, 'show', identifier, cwd=ROOT.parent)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(shown['id'], identifier)
        self.assertEqual(shown['review']['ui_reference'], False)
        self.assertTrue(Path(shown['image_path']).is_absolute())
        process, valid = run_json(SCRIPT, 'validate', cwd=ROOT.parent)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertTrue(valid['ok'])

    def test_actual_skill_and_agent_installations_locate_resources_from_other_cwds(self):
        with tempfile.TemporaryDirectory(prefix='fusion-reference-install-') as temporary:
            temporary = Path(temporary)
            identifier = self.catalog['images'][0]['id']
            for mode in ('skill', 'agent'):
                with self.subTest(mode=mode):
                    project = temporary / ('project-' + mode)
                    process, installed = run_json(INSTALLER, '--project', str(project), '--mode', mode, cwd=temporary)
                    self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                    self.assertTrue(installed['installed'])
                    resource = Path(installed['resources']['fusion-design-core'])
                    script = resource / 'scripts/visual_reference.py'
                    unrelated = temporary / ('unrelated-' + mode)
                    unrelated.mkdir()
                    for current_directory in (project, unrelated):
                        process, shown = run_json(script, 'show', identifier, cwd=current_directory)
                        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                        path = Path(shown['image_path'])
                        self.assertTrue(path.is_absolute())
                        self.assertTrue(path.is_relative_to(resource))
                        self.assertTrue(path.is_file())
                    process, valid = run_json(script, 'validate', cwd=unrelated)
                    self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                    self.assertTrue(valid['ok'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
