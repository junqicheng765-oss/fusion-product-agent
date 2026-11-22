"""Exercise lazy preset readers with local payloads; never contact a resource host."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'package/skills/fusion-design-core/scripts'
sys.path.insert(0, str(SCRIPTS))
import color_intelligence as colors
import design_resources as resources
import style_preset as styles
from design_resources import ResourceError


class LazyPresetReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.style_root = self.root / 'style-presets'
        self.color_root = self.root / 'color-presets'
        self.style_root.mkdir()
        self.color_root.mkdir()
        self.style_entry = {'id': 'INT-05', 'file': 'dto/int-05-warm-editorial.json'}
        self.style_registry = {'presets': {'systems': [], 'dto': [self.style_entry], 'tweakcn': []}}
        self.color_registry = {'systems': [{'id': 'warm-editorial'}]}
        (self.style_root / 'registry.json').write_text(json.dumps(self.style_registry), encoding='utf-8')
        (self.color_root / 'registry.json').write_text(json.dumps(self.color_registry), encoding='utf-8')
        self.data = {
            'cssVars': {
                'theme': {'radius': '0.5rem'},
                'light': {'primary': '#B65839', 'background': '#F5F0E8'},
                'dark': {'primary': '#CC785C', 'background': '#191918'},
            },
            'meta': {'dto': {'id': 'INT-05', 'modes': ['light']}},
        }
        self.payload = self.root / 'payload.json'
        self.payload.write_text(json.dumps(self.data), encoding='utf-8')

    def test_list_commands_only_read_bundled_indexes(self):
        for module, args in ((styles, SimpleNamespace(family=None)),
                             (colors, SimpleNamespace())):
            with self.subTest(module=module.__name__):
                with patch.object(module, 'resource_file', side_effect=AssertionError('list fetched payload')):
                    with redirect_stdout(io.StringIO()):
                        module.cmd_list(args)

    def test_style_resolve_fetches_only_the_registered_file(self):
        with patch.object(styles, 'ROOT', str(self.style_root)):
            with patch.object(styles, 'resource_file', return_value=self.payload) as resource:
                group, item, data = styles.resolve('int-05')
        self.assertEqual((group, item, data), ('dto', self.style_entry, self.data))
        resource.assert_called_once_with('style-presets', self.style_entry['file'],
                                         bundled_path=str(self.style_root / self.style_entry['file']))

    def test_color_system_uses_index_when_payload_is_not_bundled(self):
        with patch.object(colors, 'ROOT', str(self.color_root)):
            with patch.object(colors, 'resource_file', return_value=self.payload) as resource:
                self.assertEqual(colors.load_system('warm-editorial'), self.data)
        resource.assert_called_once_with('color-presets', 'systems/warm-editorial.json',
                                         bundled_path=str(self.color_root / 'systems/warm-editorial.json'))

    def test_radix_scales_request_one_resource_file(self):
        self.payload.write_text('{"blue":{"blue9":"#0090ff"}}', encoding='utf-8')
        with patch.object(colors, 'ROOT', str(self.color_root)):
            with patch.object(colors, 'resource_file', return_value=self.payload) as resource:
                self.assertEqual(colors.scales(), {'blue': {'blue9': '#0090ff'}})
        resource.assert_called_once_with('color-presets', 'radix/scales.json',
                                         bundled_path=str(self.color_root / 'radix/scales.json'))

    def test_style_contrast_resolves_aliases_before_fetching_one_payload(self):
        for alias in ('INT-05', 'int-05-warm-editorial', 'dto-int-05-warm-editorial'):
            with self.subTest(alias=alias):
                with patch.object(colors, 'STYLE_ROOT', str(self.style_root)):
                    with patch.object(colors, 'resource_file', return_value=self.payload) as resource:
                        packs = colors.load_style_preset(alias)
                self.assertEqual(packs, [('light', {'radius': '0.5rem', **self.data['cssVars']['light']})])
                resource.assert_called_once_with('style-presets', self.style_entry['file'],
                                                 bundled_path=str(self.style_root / self.style_entry['file']))

    def test_contrast_uses_registered_color_system_without_bundled_file(self):
        row = {'pair': '正文', 'result': 'PASS', 'ratio': 21, 'need': 4.5,
               'fg': '#000000', 'bg': '#ffffff'}
        with patch.object(colors, 'ROOT', str(self.color_root)):
            with patch.object(colors, 'load_system', return_value=self.data) as load:
                with patch.object(colors, 'load_style_preset', side_effect=AssertionError('wrong library')):
                    with patch.object(colors, 'check_tokens', return_value=(True, [row])):
                        with redirect_stdout(io.StringIO()):
                            with self.assertRaises(SystemExit) as result:
                                colors.cmd_contrast(SimpleNamespace(css=None, preset='warm-editorial', aaa=False))
        self.assertEqual(result.exception.code, 0)
        load.assert_called_once_with('warm-editorial')

    def test_unknown_ids_do_not_request_payloads(self):
        with patch.object(styles, 'ROOT', str(self.style_root)):
            with patch.object(styles, 'resource_file', side_effect=AssertionError('unknown style fetched')):
                with self.assertRaises(SystemExit):
                    styles.resolve('missing')
        with patch.object(colors, 'ROOT', str(self.color_root)):
            with patch.object(colors, 'STYLE_ROOT', str(self.style_root)):
                with patch.object(colors, 'resource_file', side_effect=AssertionError('unknown color fetched')):
                    with self.assertRaises(SystemExit):
                        colors.load_system('missing')
                    self.assertIsNone(colors.load_style_preset('missing'))

    def test_selected_style_resource_failure_is_not_swallowed(self):
        with patch.object(colors, 'STYLE_ROOT', str(self.style_root)):
            with patch.object(colors, 'resource_file', side_effect=ResourceError('fixture unavailable')):
                with self.assertRaisesRegex(ResourceError, 'fixture unavailable'):
                    colors.load_style_preset('INT-05')

    def test_command_entrypoints_report_resource_errors_without_traceback(self):
        for module, label in ((styles, '风格资源不可用'), (colors, '配色资源不可用')):
            with self.subTest(module=module.__name__):
                with patch.object(sys, 'argv', [module.__file__, 'show', 'fixture']):
                    with patch.object(module, 'cmd_show', side_effect=ResourceError('fixture unavailable')):
                        with self.assertRaisesRegex(SystemExit, label + '：fixture unavailable'):
                            module.main()

    def test_external_fixture_library_keeps_effective_payloads_without_network(self):
        external = self.root / 'external'
        skill = self.root / 'skill'
        store = {'schema_version': 1, 'repository': resources.REPOSITORY,
                 'revision': 'a' * 40, 'libraries': {}}
        payloads = {
            'style-presets': {self.style_entry['file']: self.data},
            'color-presets': {'systems/warm-editorial.json': self.data,
                              'radix/scales.json': {'blue': {'blue9': '#0090ff'}}},
        }
        for library, files in payloads.items():
            profile = {'path': 'libraries/' + library, 'files': {}}
            for relative, payload in files.items():
                content = json.dumps(payload).encode('utf-8')
                target = external / profile['path'] / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                profile['files'][relative] = {'bytes': len(content),
                                               'sha256': hashlib.sha256(content).hexdigest()}
            store['libraries'][library] = profile
        store_path = skill / 'resource-adapters/library-store.json'
        store_path.parent.mkdir(parents=True)
        store_path.write_text(json.dumps(store), encoding='utf-8')
        with patch.dict(os.environ, {'FUSION_DESIGN_RESOURCE_ROOT': str(external),
                                     'FUSION_DESIGN_RESOURCE_CACHE': str(self.root / 'cache')}):
            with patch.object(resources, 'SKILL_ROOT', skill):
                with patch.object(resources, 'open_resource', side_effect=AssertionError('network forbidden')):
                    with patch.object(styles, 'ROOT', str(self.style_root)):
                        self.assertEqual(styles.resolve('INT-05')[2], self.data)
                    with patch.object(colors, 'ROOT', str(self.color_root)):
                        with patch.object(colors, 'STYLE_ROOT', str(self.style_root)):
                            self.assertEqual(colors.load_system('warm-editorial'), self.data)
                            self.assertEqual(colors.scales(), payloads['color-presets']['radix/scales.json'])
                            self.assertEqual(colors.load_style_preset('INT-05')[0][1]['primary'], '#B65839')
        self.assertFalse((self.root / 'cache').exists())

    def test_older_bundled_payloads_work_without_a_resource_store(self):
        for root, relative, payload in (
                (self.style_root, self.style_entry['file'], self.data),
                (self.color_root, 'systems/warm-editorial.json', self.data),
                (self.color_root, 'radix/scales.json', {'blue': {'blue9': '#0090ff'}})):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload), encoding='utf-8')
        with patch.object(resources, 'SKILL_ROOT', self.root / 'missing-store'):
            with patch.object(resources, 'open_resource', side_effect=AssertionError('network forbidden')):
                with patch.object(styles, 'ROOT', str(self.style_root)):
                    self.assertEqual(styles.resolve('INT-05')[2], self.data)
                with patch.object(colors, 'ROOT', str(self.color_root)):
                    with patch.object(colors, 'STYLE_ROOT', str(self.style_root)):
                        self.assertEqual(colors.load_system('warm-editorial'), self.data)
                        self.assertEqual(colors.scales(), {'blue': {'blue9': '#0090ff'}})
                        self.assertEqual(colors.load_style_preset('INT-05')[0][1]['primary'], '#B65839')


if __name__ == '__main__':
    unittest.main()
