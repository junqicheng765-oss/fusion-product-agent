#!/usr/bin/env python3
"""Offline tests for pinned, single-file design-library retrieval.

Run: python3 -m unittest discover -s tools -p test_design_resources.py -v
"""

import hashlib
from http.client import IncompleteRead
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from urllib.error import URLError


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'package/skills/fusion-design-core/scripts/design_resources.py'
spec = importlib.util.spec_from_file_location('fusion_design_resources_test', SCRIPT)
resources = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resources)


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='fusion-design-resources-')
        self.addCleanup(self.temporary.cleanup)
        # Resolve the OS temporary alias once; intentional fixture symlinks below
        # remain unresolved, so tests work on macOS where /var itself is a link.
        self.root = Path(self.temporary.name).resolve()
        self.skill = self.root / 'skill'
        self.config = self.skill / 'resource-adapters/library-store.json'
        self.cache = self.root / 'cache'
        self.local = self.root / 'external'
        self.library_id = 'style-presets'
        self.relative = 'themes/paper.json'
        self.data = b'{"name":"paper"}\n'
        self.revision = 'a' * 40
        self.record = {'sha256': hashlib.sha256(self.data).hexdigest(), 'bytes': len(self.data)}
        self.store = {'schema_version': 1, 'repository': resources.REPOSITORY,
                      'revision': self.revision,
                      'libraries': {self.library_id: {'path': 'libraries/' + self.library_id,
                                                      'files': {self.relative: self.record}}}}
        self.save()
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(resources, 'SKILL_ROOT', self.skill).start()
        mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_CACHE': str(self.cache),
                                    'FUSION_DESIGN_RESOURCE_ROOT': ''}).start()
        mock.patch.object(resources, 'open_resource', side_effect=AssertionError('unexpected network access')).start()

    @property
    def target(self):
        return self.cache / self.revision / self.library_id / self.relative

    @property
    def mirror_file(self):
        return self.local / 'libraries' / self.library_id / self.relative

    def save(self):
        self.config.parent.mkdir(parents=True, exist_ok=True)
        self.config.write_text(json.dumps(self.store), encoding='utf-8')

    def write(self, path, data=None):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.data if data is None else data)
        return path

    def response(self, data=None, headers=None):
        response = io.BytesIO(self.data if data is None else data)
        response.headers = {} if headers is None else headers
        return response

    def get(self, **kwargs):
        return resources.resource_file(self.library_id, self.relative, **kwargs)

    def assert_no_partial(self):
        self.assertFalse(any(path.is_file() for path in self.cache.rglob('*')))

    def test_import_has_no_configuration_or_network_side_effects(self):
        with mock.patch('builtins.open', side_effect=AssertionError('import reads files')), \
                mock.patch('urllib.request.build_opener', side_effect=AssertionError('import opens network')):
            isolated_spec = importlib.util.spec_from_file_location('isolated_design_resources', SCRIPT)
            isolated = importlib.util.module_from_spec(isolated_spec)
            isolated_spec.loader.exec_module(isolated)
            self.assertTrue(callable(isolated.resource_file))

    def test_one_pinned_file_download_is_atomic_and_reused_offline(self):
        original_link = resources.os.link
        published = []

        def publish(temporary, target, **kwargs):
            self.assertFalse(target.exists())
            self.assertEqual(temporary.read_bytes(), self.data)
            published.append(target)
            return original_link(temporary, target, **kwargs)

        with mock.patch.object(resources, 'open_resource', return_value=self.response()) as opener, \
                mock.patch.object(resources.os, 'link', side_effect=publish):
            result = self.get()
        self.assertEqual(result, self.target)
        opener.assert_called_once_with(
            'https://raw.githubusercontent.com/junqicheng765-oss/fusion-product-agent/' +
            self.revision + '/libraries/style-presets/themes/paper.json',
            timeout=resources.DOWNLOAD_TIMEOUT_SECONDS)
        self.assertEqual(published, [self.target])
        self.assertEqual([path for path in self.cache.rglob('*') if path.is_file()], [self.target])
        self.assertEqual(self.get(), result)
        self.assertFalse(any(path.name.startswith('.download-') for path in self.cache.rglob('*')))

    def test_every_cache_hit_rechecks_hash_and_never_repairs_user_file(self):
        self.write(self.target)
        self.assertEqual(self.get(), self.target)
        changed = b'x' * len(self.data)
        self.target.write_bytes(changed)
        with self.assertRaisesRegex(resources.ResourceError, 'sha256 mismatch'):
            self.get()
        self.assertEqual(self.target.read_bytes(), changed)

    def test_cached_file_byte_count_is_checked(self):
        self.write(self.target, b'short')
        with self.assertRaisesRegex(resources.ResourceError, 'byte count mismatch'):
            self.get()
        self.assertEqual(self.target.read_bytes(), b'short')

    def test_existing_bundled_file_and_directory_need_no_configuration(self):
        bundled = self.write(self.root / 'legacy/themes/paper.json', b'caller fixture')
        self.config.unlink()
        self.assertEqual(self.get(bundled_path=bundled), bundled)
        self.assertEqual(resources.resource_directory(self.library_id, bundled_root=bundled.parent), bundled.parent)
        self.assertFalse(self.cache.exists())

    def test_bundled_resource_has_priority_over_explicit_mirror_and_bad_config(self):
        bundled = self.write(self.root / 'legacy/paper.json')
        self.config.write_text('broken', encoding='utf-8')
        with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(self.local)}):
            self.assertEqual(self.get(bundled_path=bundled), bundled)

    def test_missing_bundle_uses_verified_explicit_resource_worktree(self):
        self.write(self.mirror_file)
        with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(self.local)}):
            result = self.get(bundled_path=self.root / 'missing.json')
            self.assertEqual(result, self.mirror_file)
        self.assertFalse(self.cache.exists())

    def test_explicit_missing_or_corrupt_mirror_never_uses_cache_or_network(self):
        self.write(self.target)
        with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(self.local)}):
            with self.assertRaisesRegex(resources.ResourceError, 'missing from explicit'):
                self.get()
            self.write(self.mirror_file, b'x' * len(self.data))
            with self.assertRaisesRegex(resources.ResourceError, 'sha256 mismatch'):
                self.get()

    def test_directory_lookup_does_not_create_hash_or_download(self):
        with mock.patch.object(resources, '_read_file', wraps=resources._read_file) as reader:
            result = resources.resource_directory(self.library_id)
        self.assertEqual(result, self.target.parents[1])
        self.assertEqual(reader.call_count, 1)  # manifest only
        self.assertFalse(self.cache.exists())
        with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(self.local)}):
            self.assertEqual(resources.resource_directory(self.library_id), self.mirror_file.parents[1])
        self.assertFalse(self.local.exists())

    def test_default_cache_location_is_stable(self):
        with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_CACHE': ''}), \
                mock.patch.object(resources.Path, 'home', return_value=self.root / 'home'):
            result = resources.resource_directory(self.library_id)
        self.assertEqual(result, self.root / 'home/.cache/fusion-product-agent/design-resources' /
                         self.revision / self.library_id)

    def test_missing_configuration_unknown_library_and_unlisted_file_are_friendly(self):
        for identifier in ('unknown', '../style-presets', None):
            with self.subTest(identifier=identifier), self.assertRaisesRegex(resources.ResourceError, 'unknown'):
                resources.resource_file(identifier, self.relative)
        with self.assertRaisesRegex(resources.ResourceError, 'not listed'):
            resources.resource_file(self.library_id, 'themes/unlisted.json')
        with self.assertRaisesRegex(resources.ResourceError, 'profile is missing'):
            resources.resource_directory('color-presets')
        self.config.unlink()
        with self.assertRaisesRegex(resources.ResourceError, 'library-store.json is missing'):
            self.get()

    def test_relative_paths_are_validated_even_when_bundle_exists(self):
        bundled = self.write(self.root / 'legacy.json')
        for relative in ('', '../escape', '/absolute', 'a//b', 'a/./b', 'a/../b',
                         'C:/drive', 'a/C:/drive', 'a\\b', 'a\x00b', 'a\nb', 'a./b'):
            with self.subTest(relative=relative), self.assertRaises(resources.ResourceError):
                resources.resource_file(self.library_id, relative, bundled_path=bundled)

    def test_profile_validation_rejects_unpinned_or_unsafe_configuration(self):
        cases = [('schema_version', True), ('revision', 'main'),
                 ('revision', '../' + self.revision),
                 ('repository', 'https://user:password@github.com/junqicheng765-oss/fusion-product-agent'),
                 ('repository', resources.REPOSITORY + '?token=private')]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                original = self.store[field]
                self.store[field] = value
                self.save()
                with self.assertRaises(resources.ResourceError):
                    resources.resource_directory(self.library_id)
                self.store[field] = original
        profile = self.store['libraries'][self.library_id]
        for unsafe in ('../libraries/style-presets', '/libraries/style-presets',
                       'libraries//style-presets', 'libraries/color-presets'):
            profile['path'] = unsafe
            self.save()
            with self.assertRaisesRegex(resources.ResourceError, 'library path'):
                self.get()

    def test_every_configured_file_path_and_integrity_record_is_validated(self):
        files = self.store['libraries'][self.library_id]['files']
        for key, record in (('../escape.json', self.record), ('/escape', self.record),
                            ('bad.json', {'sha256': 'bad', 'bytes': 2}),
                            ('bad.json', {'sha256': 'a' * 64, 'bytes': True}),
                            ('bad.json', {'sha256': 'a' * 64, 'bytes': -1}),
                            ('bad.json', {'sha256': 'a' * 64, 'bytes': resources.MAX_RESOURCE_BYTES + 1})):
            with self.subTest(key=key, record=record):
                files[key] = record
                self.save()
                with self.assertRaises(resources.ResourceError):
                    self.get()
                del files[key]

    def test_config_symlink_or_parent_symlink_is_rejected(self):
        copy = self.root / 'config.json'
        self.config.rename(copy)
        self.config.symlink_to(copy)
        with self.assertRaisesRegex(resources.ResourceError, 'symlink'):
            self.get()
        self.config.unlink()
        copy.rename(self.config)
        directory = self.root / 'adapters'
        self.config.parent.rename(directory)
        self.config.parent.symlink_to(directory, target_is_directory=True)
        with self.assertRaisesRegex(resources.ResourceError, 'symlink'):
            resources.resource_directory(self.library_id)

    def test_local_root_parent_and_descendant_symlinks_are_rejected(self):
        self.write(self.mirror_file)
        alias = self.root / 'mirror-alias'
        alias.symlink_to(self.local, target_is_directory=True)
        for root in (alias, alias / 'nested'):
            with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(root)}), \
                    self.assertRaisesRegex(resources.ResourceError, 'symlink'):
                self.get()
        original = self.mirror_file
        original.unlink()
        outside = self.write(self.root / 'outside.json')
        original.symlink_to(outside)
        with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(self.local)}), \
                self.assertRaisesRegex(resources.ResourceError, 'symlink'):
            self.get()
        self.assertEqual(outside.read_bytes(), self.data)

    def test_cache_parent_root_file_and_nested_directory_symlinks_are_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        alias = self.root / 'cache-alias'
        alias.symlink_to(outside, target_is_directory=True)
        for base in (alias, alias / 'nested'):
            with mock.patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_CACHE': str(base)}), \
                    self.assertRaisesRegex(resources.ResourceError, 'symlink'):
                self.get()
        self.target.parent.mkdir(parents=True)
        target_data = self.write(outside / 'user.json', b'keep user content')
        self.target.symlink_to(target_data)
        with self.assertRaisesRegex(resources.ResourceError, 'symlink'):
            self.get()
        self.target.unlink()
        self.target.parent.rmdir()
        self.target.parent.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(resources.ResourceError, 'symlink'):
            self.get()
        self.assertEqual(target_data.read_bytes(), b'keep user content')

    def test_network_failures_and_interrupted_read1_leave_no_partial_files(self):
        with mock.patch.object(resources, 'open_resource', side_effect=URLError('offline')):
            with self.assertRaisesRegex(resources.ResourceError, 'download failed'):
                self.get()
        self.assert_no_partial()
        response = self.response()
        with mock.patch.object(response, 'read1', side_effect=[b'part', IncompleteRead(b'broken')]), \
                mock.patch.object(resources, 'open_resource', return_value=response):
            with self.assertRaisesRegex(resources.ResourceError, 'download failed'):
                self.get()
        self.assert_no_partial()

    def test_download_must_match_declared_bytes_and_hash(self):
        for data, message in ((b'', 'byte count mismatch'),
                              (self.data + b'extra', 'byte count mismatch'),
                              (b'x' * len(self.data), 'sha256 mismatch')):
            with self.subTest(data=data), mock.patch.object(resources, 'open_resource', return_value=self.response(data)):
                with self.assertRaisesRegex(resources.ResourceError, message):
                    self.get()
                self.assert_no_partial()

    def test_content_length_and_stream_size_limits_are_enforced(self):
        for length, message in (('bad', 'Content-Length'), ('-1', 'size limit'),
                                (str(resources.MAX_RESOURCE_BYTES + 1), 'size limit'),
                                (str(len(self.data) + 1), 'byte count mismatch')):
            with self.subTest(length=length), mock.patch.object(
                    resources, 'open_resource', return_value=self.response(headers={'Content-Length': length})):
                with self.assertRaisesRegex(resources.ResourceError, message):
                    self.get()
                self.assert_no_partial()
        response = self.response()
        with mock.patch.object(response, 'read1', return_value=b'x' * (resources.MAX_RESOURCE_BYTES + 1)), \
                mock.patch.object(resources, 'open_resource', return_value=response):
            with self.assertRaisesRegex(resources.ResourceError, 'size limit'):
                self.get()
        self.assert_no_partial()

    def test_deadline_includes_late_eof_and_socket_timeouts(self):
        for clocks in ([0, resources.DOWNLOAD_DEADLINE_SECONDS + 1],
                       [0, 0, resources.DOWNLOAD_DEADLINE_SECONDS + 1]):
            with self.subTest(clocks=clocks), mock.patch.object(resources.time, 'monotonic', side_effect=clocks), \
                    mock.patch.object(resources, 'open_resource', return_value=self.response(b'')):
                with self.assertRaisesRegex(resources.ResourceError, 'time limit'):
                    self.get()
                self.assert_no_partial()
        response = self.response()
        with mock.patch.object(response, 'read1', side_effect=TimeoutError('socket timeout')), \
                mock.patch.object(resources, 'open_resource', return_value=response):
            with self.assertRaisesRegex(resources.ResourceError, 'download failed'):
                self.get()
        self.assert_no_partial()

    def test_redirect_handler_rejects_every_destination_and_opener_disables_proxies(self):
        handler = resources.PinnedResourceRedirectHandler()
        for destination in ('https://example.com/file', resources.REPOSITORY + '/main/file', 'http://example.com/file'):
            with self.assertRaisesRegex(resources.ResourceError, 'redirect is forbidden'):
                handler.redirect_request(None, None, 302, 'redirect', {}, destination)
        # Exercise the real opener factory separately from the fixture's network guard.
        original_spec = importlib.util.spec_from_file_location('unmocked_design_resources', SCRIPT)
        unmocked = importlib.util.module_from_spec(original_spec)
        original_spec.loader.exec_module(unmocked)
        with mock.patch.object(unmocked, 'build_opener') as factory:
            unmocked.open_resource('https://example.invalid/pinned', timeout=20)
        proxy = factory.call_args.args[0]
        self.assertEqual(proxy.proxies, {})
        factory.return_value.open.assert_called_once_with('https://example.invalid/pinned', timeout=20)

    def test_concurrent_user_file_is_never_overwritten(self):
        original_link = resources.os.link

        def race(temporary, target, **kwargs):
            target.write_bytes(b'keep user content')
            return original_link(temporary, target, **kwargs)

        with mock.patch.object(resources, 'open_resource', return_value=self.response()), \
                mock.patch.object(resources.os, 'link', side_effect=race):
            with self.assertRaises(resources.ResourceError):
                self.get()
        self.assertEqual(self.target.read_bytes(), b'keep user content')
        self.assertFalse(any(path.name.startswith('.download-') for path in self.cache.rglob('*')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
