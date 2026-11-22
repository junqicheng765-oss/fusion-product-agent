#!/usr/bin/env python3
"""Test reference curation, safe retrieval, integrity, and real isolated installs.

Run: python3 -m unittest discover -s tools -p test_visual_reference_library.py -v
No test rebuilds or edits the repository package manifest.
"""

import hashlib
import importlib.util
import io
from http.client import IncompleteRead
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock
from urllib.error import URLError


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


def run_json(script, *arguments, cwd=None, env=None):
    if env is None:
        env = dict(os.environ)
        env.pop('FUSION_VISUAL_RESOURCE_ROOT', None)
        env.pop('FUSION_VISUAL_CACHE_DIR', None)
    result = subprocess.run([sys.executable, str(script), *arguments], cwd=cwd,
                            text=True, capture_output=True, check=False, env=env)
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
        self.assertEqual(payload['mode'], 'catalog')
        self.assertEqual(payload['verified_hashes'], 0)
        process, payload = self.call('validate', '--resources')
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(payload['error_count'], 0)
        self.assertEqual(payload['verified_hashes'], 3)

    def test_tampering_is_detected_only_by_explicit_hash_validation(self):
        (self.library / 'images/knit.webp').write_bytes(b'tampered')
        for arguments in [('list',), ('search', '针织', '--role', 'material')]:
            process, _payload = self.call(*arguments)
            self.assertEqual(process.returncode, 0, process.stderr)
        self.assert_fails('validate', '--resources', contains='sha256 mismatch')

    def test_validate_rejects_path_escape_and_absolute_paths(self):
        for relative in ('images/../../outside.webp', '../outside.webp', '/tmp/outside.webp',
                         'C:/outside.webp', 'images\\outside.webp', 'images/./knit.webp', 'images/C:/outside.webp'):
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
        self.assert_fails('validate', '--resources', contains='symlink')

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
        self.assert_fails('validate', '--resources', contains='unlisted image resource')
        extra.unlink()
        target = self.library / 'images/knit.webp'
        target.unlink()
        self.assert_fails('validate', '--resources', contains='missing')
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
        actual = {item['sha256'] for item in self.catalog['images']}
        self.assertTrue(included)
        self.assertTrue(excluded)
        self.assertTrue(included.isdisjoint(excluded))
        self.assertEqual(included, actual)
        self.assertTrue(actual.isdisjoint(excluded))
        self.assertEqual({item['sha256'] for item in self.catalog['images']}, actual)
        self.assertEqual(self.audit['included_images'], len(included))
        self.assertEqual(self.audit['bundled_images'], 0)
        self.assertFalse((LIBRARY / 'images').exists())
        self.assertEqual(self.audit['excluded_ui'], len(excluded))
        self.assertEqual(len(self.catalog['images']), len(included))
        self.assertTrue(all(source['collection'] in ('first', 'second') for item in records for source in item['sources']))

    def test_real_material_query_and_catalog_validation_need_no_images(self):
        with tempfile.TemporaryDirectory(prefix='fusion-catalog-only-') as temporary:
            temporary = Path(temporary)
            skill = temporary / 'skill'
            library = skill / 'visual-reference-library'
            library.mkdir(parents=True)
            script = skill / 'scripts/visual_reference.py'
            script.parent.mkdir()
            shutil.copy2(SCRIPT, script)
            shutil.copy2(LIBRARY / 'catalog.json', library / 'catalog.json')
            if (LIBRARY / 'resource-store.json').is_file():
                shutil.copy2(LIBRARY / 'resource-store.json', library / 'resource-store.json')
            process, payload = run_json(script, 'search', '针织', '--role', 'material', '--cache-dir', str(temporary / 'empty-cache'), cwd=ROOT.parent)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertGreater(payload['total_matches'], 0, 'The curated library must include a knitting material reference')
            self.assertLessEqual(payload['returned'], 6)
            for hit in payload['results']:
                self.assertIn('material', hit['roles'])
                self.assertEqual(hit['resource_status'], 'missing')
                self.assertNotIn('image_path', hit)
                self.assertTrue(hit['matched_fields'])
            process, valid = run_json(script, 'validate', '--cache-dir', str(temporary / 'empty-cache'), cwd=ROOT.parent)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(valid['verified_hashes'], 0)
            self.assertEqual(valid['resources']['missing'], len(self.catalog['images']))
            self.assertFalse((temporary / 'empty-cache').exists())

    def test_actual_skill_and_agent_installations_locate_catalogs_from_other_cwds(self):
        with tempfile.TemporaryDirectory(prefix='fusion-reference-install-') as temporary:
            temporary = Path(temporary)
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
                        process, found = run_json(script, 'search', '针织', '--role', 'material', '--cache-dir', str(temporary / 'empty-cache'), cwd=current_directory)
                        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                        self.assertGreater(found['total_matches'], 0)
                    process, valid = run_json(script, 'validate', '--cache-dir', str(temporary / 'empty-cache'), cwd=unrelated)
                    self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                    self.assertEqual(valid['image_count'], len(self.catalog['images']))
                    self.assertFalse((resource / 'visual-reference-library/images').exists())
                    # A temporary installed catalog exercises actual file retrieval
                    # without requiring resource-branch access or a network in CI.
                    fixture = json.loads(json.dumps(self.catalog))
                    fixture['images'] = fixture['images'][:1]
                    fixture['images'][0]['sha256'] = sha(b'installed fixture image')
                    fixture['indexes'] = visual_reference.expected_indexes(fixture)
                    (resource / 'visual-reference-library/catalog.json').write_text(json.dumps(fixture), encoding='utf-8')
                    local_root = temporary / ('external-' + mode)
                    local_image = local_root / fixture['images'][0]['file']
                    local_image.parent.mkdir(parents=True)
                    local_image.write_bytes(b'installed fixture image')
                    for current_directory in (project, unrelated):
                        process, shown = run_json(script, 'show', fixture['images'][0]['id'], '--resource-root', str(local_root), cwd=current_directory)
                        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
                        self.assertEqual(shown['resource_status'], 'local')
                        self.assertEqual(Path(shown['image_path']), local_image.resolve())


class OnDemandResourceTests(unittest.TestCase):
    add_image = FixtureTests.add_image
    save = FixtureTests.save
    def setUp(self):
        FixtureTests.setUp(self)
        self.external = self.root / 'external-library'
        shutil.move(str(self.library / 'images'), str(self.external / 'images'))
        self.cache = self.root / 'cache'
        self.store = {'schema_version': 1, 'repository': 'https://github.com/example/resources',
                      'revision': 'a' * 40, 'path': 'visual-reference-library'}
        self.save_store()
        spec = importlib.util.spec_from_file_location('isolated_visual_reference', self.script)
        self.runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runtime)
        self.record = self.catalog['images'][1]
        self.data = (self.external / self.record['file']).read_bytes()

    def save_store(self):
        (self.library / 'resource-store.json').write_text(json.dumps(self.store), encoding='utf-8')

    def invoke(self, *arguments):
        output = io.StringIO()
        with mock.patch.object(self.runtime, 'emit', side_effect=lambda value: output.write(json.dumps(value))), \
                mock.patch.dict(self.runtime.os.environ, {'FUSION_VISUAL_CACHE_DIR': str(self.cache), 'FUSION_VISUAL_RESOURCE_ROOT': ''}):
            code = self.runtime.main(arguments)
        return code, json.loads(output.getvalue())

    def response(self, data=None, headers=None):
        response = io.BytesIO(self.data if data is None else data)
        response.headers = {} if headers is None else headers
        return response

    def test_search_and_light_validation_never_open_network_or_hash_images(self):
        with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('no network')), \
                mock.patch.object(self.runtime, 'digest_file', side_effect=AssertionError('no hashing')):
            for arguments in (('list',), ('search', 'knit'), ('validate',)):
                code, payload = self.invoke(*arguments)
                self.assertEqual(code, 0, payload)
                if arguments[0] == 'search':
                    self.assertNotIn('image_path', payload['results'][0])
                    self.assertEqual(payload['results'][0]['resource_status'], 'missing')
                if arguments[0] == 'validate':
                    self.assertEqual(payload['resources']['missing'], 3)
                    self.assertEqual(payload['verified_hashes'], 0)
        self.assertFalse(self.cache.exists())

    def test_only_requested_file_downloads_at_pinned_commit_and_cache_survives_offline(self):
        with mock.patch.object(self.runtime, 'open_resource', return_value=self.response()) as opener:
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload['resource_status'], 'downloaded')
        opener.assert_called_once_with('https://raw.githubusercontent.com/example/resources/' + 'a' * 40 + '/visual-reference-library/images/knit.webp', timeout=self.runtime.DOWNLOAD_TIMEOUT_SECONDS)
        path = Path(payload['image_path'])
        self.assertEqual(path.read_bytes(), self.data)
        self.assertTrue(path.is_relative_to(self.cache.resolve()))
        self.assertEqual([item.resolve() for item in self.cache.rglob('*') if item.is_file()], [path])
        with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('offline')):
            code, cached = self.invoke('show', 'KNIT')
            self.assertEqual(code, 0, cached)
            self.assertEqual(cached['resource_status'], 'cached')
            self.assertEqual(cached['image_path'], str(path))
            code, valid = self.invoke('validate')
            self.assertEqual(valid['resources']['cached'], 1)
            self.assertEqual(valid['resources']['missing'], 2)
            self.assertEqual(valid['resources']['downloaded'], 0)

    def test_network_failure_is_json_and_does_not_create_image_path(self):
        with mock.patch.object(self.runtime, 'open_resource', side_effect=URLError('offline test')):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('resource download failed', payload['error'])
        self.assertNotIn('image_path', payload)
        self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))

    def test_redirects_cannot_change_the_pinned_request(self):
        locations = ['https://example.invalid/unpinned.webp', 'http://example.invalid/plain.webp',
                     'https://raw.githubusercontent.com/example/resources/main/images/knit.webp']
        requested = []

        class RedirectHandler(BaseHTTPRequestHandler):
            def do_GET(handler):
                requested.append(handler.path)
                handler.send_response(302)
                handler.send_header('Location', locations[int(handler.path.lstrip('/'))])
                handler.end_headers()

            def log_message(handler, *arguments):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), RedirectHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for index in range(len(locations)):
                with self.subTest(location=locations[index]), mock.patch.object(self.runtime, 'resource_url', return_value='http://127.0.0.1:' + str(server.server_port) + '/' + str(index)):
                    code, payload = self.invoke('show', 'KNIT')
                    self.assertEqual(code, 2)
                    self.assertIn('redirect is forbidden', payload['error'])
                    self.assertNotIn('image_path', payload)
            self.assertEqual(requested, ['/0', '/1', '/2'])
            self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_cache_publication_is_an_atomic_replace_after_hash_verification(self):
        original_replace = self.runtime.os.replace
        published = []

        def replace(temporary, target):
            self.assertFalse(target.exists())
            self.assertEqual(sha(temporary.read_bytes()), self.record['sha256'])
            published.append(target)
            original_replace(temporary, target)

        with mock.patch.object(self.runtime, 'open_resource', return_value=self.response()), \
                mock.patch.object(self.runtime.os, 'replace', side_effect=replace):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 0, payload)
        self.assertEqual(len(published), 1)
        self.assertEqual(Path(payload['image_path']), published[0].resolve())
        self.assertFalse(any(item.name.startswith('.download-') for item in self.cache.rglob('*')))

    def test_corrupt_cache_is_reported_without_network_or_overwrite(self):
        context = self.runtime.resource_context(self.runtime.parser().parse_args(['show', 'KNIT', '--cache-dir', str(self.cache)]))
        target = context['cache_root'] / self.record['file']
        target.parent.mkdir(parents=True)
        target.write_bytes(b'corrupt existing file')
        with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('no network')):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('sha256 mismatch', payload['error'])
        self.assertEqual(target.read_bytes(), b'corrupt existing file')
        self.assertNotIn('image_path', payload)

    def test_interrupted_stream_is_json_and_removes_partial_download(self):
        response = self.response()
        with mock.patch.object(response, 'read1', side_effect=[b'partial', IncompleteRead(b'broken')]), \
                mock.patch.object(self.runtime, 'open_resource', return_value=response):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('resource download failed', payload['error'])
        self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))

    def test_bad_hash_never_publishes_partial_file_or_overwrites_user_file(self):
        unrelated = self.root / 'keep.txt'
        unrelated.write_bytes(b'keep me')
        with mock.patch.object(self.runtime, 'open_resource', return_value=self.response(b'wrong image')):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('sha256 mismatch', payload['error'])
        self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))
        self.assertEqual(unrelated.read_bytes(), b'keep me')

    def test_download_size_and_timeout_limits_remove_partial_files(self):
        cases = [({'Content-Length': str(self.runtime.MAX_RESOURCE_BYTES + 1)}, self.data, 'size limit'),
                 ({'Content-Length': 'invalid'}, self.data, 'Content-Length'),
                 ({}, b'too much data', 'size limit')]
        for headers, data, message in cases:
            with self.subTest(message=message, headers=headers), \
                    mock.patch.object(self.runtime, 'MAX_RESOURCE_BYTES', 8), \
                    mock.patch.object(self.runtime, 'open_resource', return_value=self.response(data, headers)):
                code, payload = self.invoke('show', 'KNIT')
                self.assertEqual(code, 2)
                self.assertIn(message, payload['error'])
                self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))
        with mock.patch.object(self.runtime, 'open_resource', return_value=self.response()), \
                mock.patch.object(self.runtime.time, 'monotonic', side_effect=[0, self.runtime.DOWNLOAD_DEADLINE_SECONDS + 1]):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('time limit', payload['error'])
        self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))
        # Even an EOF arriving after the deadline must not publish a file.
        with mock.patch.object(self.runtime, 'open_resource', return_value=self.response(b'')), \
                mock.patch.object(self.runtime.time, 'monotonic', side_effect=[0, 0, self.runtime.DOWNLOAD_DEADLINE_SECONDS + 1]):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('time limit', payload['error'])
        self.assertFalse(any(item.is_file() for item in self.cache.rglob('*')))

    def test_local_resource_root_and_relocated_script_work_from_unrelated_cwd(self):
        moved_skill = self.root / 'installed elsewhere/skill'
        moved_skill.parent.mkdir()
        shutil.move(str(self.skill), str(moved_skill))
        unrelated = self.root / 'unrelated'
        unrelated.mkdir()
        script = moved_skill / 'scripts/visual_reference.py'
        process, shown = run_json(script, 'show', 'KNIT', '--resource-root', str(self.external), '--cache-dir', str(self.cache), cwd=unrelated)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(shown['resource_status'], 'local')
        self.assertEqual(Path(shown['image_path']), (self.external / self.record['file']).resolve())
        process, valid = run_json(script, 'validate', '--resources', '--resource-root', str(self.external), '--cache-dir', str(self.cache), cwd=unrelated)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(valid['verified_hashes'], 3)
        self.assertEqual(valid['resources']['local'], 3)
        self.assertFalse(self.cache.exists())

    def test_environment_local_root_and_cache_override(self):
        environment = dict(self.runtime.os.environ, FUSION_VISUAL_RESOURCE_ROOT=str(self.external), FUSION_VISUAL_CACHE_DIR=str(self.cache))
        with mock.patch.dict(self.runtime.os.environ, environment), mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('offline')):
            args = self.runtime.parser().parse_args(['show', 'KNIT'])
            shown = self.runtime.cmd_show(self.catalog, args)
        self.assertEqual(shown['resource_status'], 'local')
        self.assertFalse(self.cache.exists())

    def test_full_resource_validation_never_downloads_missing_files(self):
        with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('no network')):
            code, payload = self.invoke('validate', '--resources')
        self.assertEqual(code, 1)
        self.assertEqual(payload['resources']['missing'], 3)
        self.assertEqual(payload['verified_hashes'], 0)
        self.assertEqual(payload['error_count'], 3)
        self.assertFalse(self.cache.exists())

    def test_resource_revision_and_repository_must_be_pinned_and_safe(self):
        for field, value in (('revision', 'main'), ('revision', '../' + 'a' * 40),
                             ('repository', 'http://github.com/example/resources'),
                             ('repository', 'https://github.com/example/resources?token=bad'),
                             ('path', '../other'), ('path', '/absolute'), ('path', 'foo//bar')):
            with self.subTest(field=field, value=value):
                original = self.store[field]
                self.store[field] = value
                self.save_store()
                with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('unsafe URL')):
                    code, payload = self.invoke('show', 'KNIT')
                self.assertEqual(code, 2, payload)
                self.store[field] = original
        self.assertFalse(self.cache.exists())

    def test_symlink_cache_root_or_image_cannot_touch_external_file(self):
        self.cache.symlink_to(self.external, target_is_directory=True)
        with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('no download')):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('symlink', payload['error'])
        self.cache.unlink()
        context = self.runtime.resource_context(self.runtime.parser().parse_args(['show', 'KNIT', '--cache-dir', str(self.cache)]))
        target = context['cache_root'] / self.record['file']
        target.parent.mkdir(parents=True)
        outside = self.root / 'outside.webp'
        outside.write_bytes(b'never replace')
        target.symlink_to(outside)
        with mock.patch.object(self.runtime, 'open_resource', side_effect=AssertionError('no download')):
            code, payload = self.invoke('show', 'KNIT')
        self.assertEqual(code, 2)
        self.assertIn('symlink', payload['error'])
        self.assertEqual(outside.read_bytes(), b'never replace')


if __name__ == '__main__':
    unittest.main(verbosity=2)
