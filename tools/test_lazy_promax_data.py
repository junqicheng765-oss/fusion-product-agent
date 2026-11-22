#!/usr/bin/env python3
"""Offline contracts for ProMax's per-file design resource integration.

Run: python3 -m unittest discover -s tools -p test_lazy_promax_data.py -v
Fixtures install the real scripts as sibling Skills; no repository data or
network access is needed, and no package metadata is edited.
"""

import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PROMAX_SCRIPTS = ROOT / 'package/skills/fusion-design-ui-ux-pro-max/scripts'
RESOURCE_SCRIPT = ROOT / 'package/skills/fusion-design-core/scripts/design_resources.py'
REVISION = '1' * 40


def csv_bytes(*rows):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=list(dict.fromkeys(
        key for row in rows for key in row)))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8')


FIXTURES = {
    'styles.csv': csv_bytes({
        'Style ID': 'fixture-look', 'Style Category': 'Fixture Look',
        'Status': 'active', 'Aliases': 'Fixture Alias', 'Keywords': 'fixture ui',
        'Preferred Mode': 'light', 'Best For': 'Fixture Service',
    }),
    'products.csv': csv_bytes({
        'Product Type': 'Fixture Service', 'Keywords': 'fixture service',
        'Primary Style Recommendation': 'Fixture Look',
    }),
    'colors.csv': csv_bytes({
        'Product Type': 'Fixture Service', 'Notes': 'fixture palette',
        'Primary': '#2563EB', 'Background': '#FFFFFF', 'Foreground': '#111111',
    }),
    'landing.csv': csv_bytes({
        'Pattern ID': 'fixture-landing', 'Pattern Name': 'Fixture Landing',
        'Keywords': 'fixture service', 'Section Order': 'Hero > CTA',
    }),
    'typography.csv': csv_bytes({
        'Font Pairing Name': 'Fixture Fonts', 'Best For': 'fixture service',
        'Heading Font': 'Fixture Sans', 'Body Font': 'Fixture Sans',
    }),
    'ui-reasoning.csv': csv_bytes({
        'UI_Category': 'General', 'Recommended_Pattern': 'Fixture Landing',
        'Style_Priority': 'Fixture Look', 'Decision_Rules': '{}',
    }),
    'motion.csv': csv_bytes({
        'Category': 'Fixture motion', 'Intensity Tier': 'Subtle',
        'Keywords': 'fixture service', 'GSAP Snippet': 'gsap.to(element, {opacity: 1})',
    }),
    'stacks/react.csv': csv_bytes({
        'Category': 'Fixture', 'Guideline': 'fixture-react-id',
        'Description': 'fixture component', 'Status': 'current',
        'Applies To': 'react 19.2.x',
    }),
    # Unrelated files are listed to catch eager corpus downloads.
    'icons.csv': csv_bytes({'Icon Name': 'Unused', 'Keywords': 'unused'}),
    'stacks/vue.csv': csv_bytes({'Guideline': 'unused-vue-id'}),
}


class LazyProMaxDataTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='fusion-promax-lazy-test-')
        self.addCleanup(temporary.cleanup)
        # The shared resolver rejects symlink ancestors; macOS /var is a link.
        self.root = Path(temporary.name).resolve()
        self.skills = self.root / 'skills'
        self.promax = self.skills / 'fusion-design-ui-ux-pro-max'
        self.scripts = self.promax / 'scripts'
        self.shared = self.skills / 'fusion-design-core'
        self.scripts.mkdir(parents=True)
        (self.shared / 'scripts').mkdir(parents=True)
        for name in ('core.py', 'design_system.py', 'search.py', 'reasoning_contract.py'):
            shutil.copy2(PROMAX_SCRIPTS / name, self.scripts / name)
        shutil.copy2(RESOURCE_SCRIPT, self.shared / 'scripts/design_resources.py')
        self.mirror = self.root / 'mirror'
        self.library = self.mirror / 'libraries/ui-ux-pro-max-data'
        for relative, content in FIXTURES.items():
            target = self.library / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        adapter = self.shared / 'resource-adapters/library-store.json'
        adapter.parent.mkdir()
        adapter.write_text(json.dumps({
            'schema_version': 1,
            'repository': 'https://github.com/junqicheng765-oss/fusion-product-agent',
            'revision': REVISION,
            'libraries': {'ui-ux-pro-max-data': {
                'path': 'libraries/ui-ux-pro-max-data',
                'files': {name: {'sha256': hashlib.sha256(content).hexdigest(),
                                 'bytes': len(content)}
                          for name, content in FIXTURES.items()},
            }},
        }), encoding='utf-8')
        self.cache = self.root / 'cache'
        environment = dict(os.environ)
        environment.pop('FUSION_DESIGN_RESOURCE_ROOT', None)
        environment['FUSION_DESIGN_RESOURCE_CACHE'] = str(self.cache)
        self.environment = environment
        self.environment_patch = mock.patch.dict(os.environ, environment, clear=True)
        self.environment_patch.start()
        self.addCleanup(self.environment_patch.stop)
        self.network = mock.patch('urllib.request.OpenerDirector.open',
                                  side_effect=AssertionError('real network forbidden'))
        self.network_mock = self.network.start()
        self.addCleanup(self.network.stop)
        self.module_patch = mock.patch.dict(sys.modules)
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)
        for name in ('core', 'design_system', 'reasoning_contract',
                     'fusion_design_resources'):
            sys.modules.pop(name, None)
        sys.path.insert(0, str(self.scripts))
        self.addCleanup(sys.path.remove, str(self.scripts))
        self.core = self.load('core')
        self.design_system = self.load('design_system')
        self.resources = self.core._resource_client

    def load(self, name):
        spec = importlib.util.spec_from_file_location(name, self.scripts / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    def downloader(self, url, timeout):
        prefix = ('https://raw.githubusercontent.com/junqicheng765-oss/'
                  'fusion-product-agent/' + REVISION + '/libraries/ui-ux-pro-max-data/')
        self.assertTrue(url.startswith(prefix), url)
        relative = url[len(prefix):]
        self.requested.append(relative)
        response = io.BytesIO(FIXTURES[relative])
        response.headers = {'Content-Length': str(len(FIXTURES[relative]))}
        return response

    def downloading(self):
        self.requested = []
        return mock.patch.object(self.resources, 'open_resource', side_effect=self.downloader)

    def cached_files(self):
        directory = self.cache / REVISION / 'ui-ux-pro-max-data'
        return {path.relative_to(directory).as_posix()
                for path in directory.rglob('*') if path.is_file()}

    def cli(self, script, *arguments):
        runner = (
            'import runpy, sys; from pathlib import Path; from unittest.mock import patch; '
            'sys.argv = sys.argv[1:]; '
            'sys.path.insert(0, str(Path(sys.argv[0]).parent)); '
            'guard = patch("urllib.request.OpenerDirector.open", '
            'side_effect=AssertionError("real network forbidden")); '
            'guard.start(); runpy.run_path(sys.argv[0], run_name="__main__")'
        )
        return subprocess.run([sys.executable, '-c', runner,
                               str(self.scripts / script), *arguments],
                              cwd=self.root, env=dict(os.environ), text=True,
                              capture_output=True, check=False, timeout=15)

    def test_imports_from_arbitrary_cwd_do_not_fetch_or_create_cache(self):
        self.network_mock.assert_not_called()
        self.assertFalse(self.cache.exists())
        self.assertIsNone(self.core._DOMAIN_KEYWORDS)
        result = self.cli('search.py', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.cache.exists())

    def test_explicit_domain_fetches_only_its_csv_and_reuses_verified_cache(self):
        with self.downloading():
            first = self.core.search('fixture palette', 'color')
            second = self.core.search('fixture palette', 'color')
        self.assertGreater(first['count'], 0)
        self.assertEqual(first, second)
        self.assertEqual(self.requested, ['colors.csv'])
        self.assertEqual(self.cached_files(), {'colors.csv'})

    def test_stack_fetches_only_selected_stack_csv(self):
        with self.downloading():
            result = self.core.search_stack('fixture-react-id', 'react')
        self.assertEqual(result['count'], 1)
        self.assertEqual(self.requested, ['stacks/react.csv'])
        self.assertEqual(self.cached_files(), {'stacks/react.csv'})

    def test_exact_style_auto_routing_does_not_need_product_or_other_domains(self):
        with self.downloading():
            result = self.core.search('Fixture Alias')
        self.assertEqual(result['domain'], 'style')
        self.assertEqual(result['results'][0]['Style ID'], 'fixture-look')
        self.assertEqual(self.requested, ['styles.csv'])

    def test_general_auto_routing_fetches_only_routing_and_selected_domain_data(self):
        with self.downloading():
            result = self.core.search('fixture palette')
        self.assertEqual(result['domain'], 'color')
        self.assertEqual(self.requested, ['styles.csv', 'products.csv', 'colors.csv'])
        self.assertEqual(self.cached_files(), set(self.requested))
        self.assertIn('fixture service', self.core._domain_keywords()['product'])

    def test_design_system_direct_loaders_use_shared_resource_paths(self):
        with self.downloading():
            generator = self.design_system.DesignSystemGenerator()
        self.assertEqual(self.requested, ['ui-reasoning.csv', 'styles.csv', 'landing.csv'])
        self.assertEqual(generator.reasoning_data[0]['UI_Category'], 'General')
        self.assertEqual(generator.style_data[0]['Style ID'], 'fixture-look')
        self.assertEqual(generator.landing_lookup['fixture-landing']['Pattern Name'],
                         'Fixture Landing')

    def test_design_system_fetches_its_domains_and_motion_only_when_requested(self):
        needed = {'ui-reasoning.csv', 'styles.csv', 'landing.csv', 'products.csv',
                  'colors.csv', 'typography.csv'}
        with self.downloading():
            result = self.design_system.generate_design_system('fixture service')
            self.assertEqual(set(self.requested), needed)
            self.assertEqual(result['design_system']['style']['id'], 'fixture-look')
            self.assertEqual(self.cached_files(), needed)
            self.design_system.generate_design_system('fixture service', motion=1)
        self.assertEqual(set(self.requested), needed | {'motion.csv'})
        self.assertEqual(len(self.requested), len(needed) + 1)

    def test_explicit_resource_root_works_without_network_or_cache(self):
        os.environ['FUSION_DESIGN_RESOURCE_ROOT'] = str(self.mirror)
        with mock.patch.object(self.resources, 'open_resource',
                               side_effect=AssertionError('mirror must not download')):
            result = self.core.search('fixture palette', 'color')
            generator = self.design_system.DesignSystemGenerator()
        self.assertGreater(result['count'], 0)
        self.assertTrue(generator.reasoning_data)
        self.assertFalse(self.cache.exists())

    def test_missing_external_file_raises_instead_of_becoming_empty_or_seed(self):
        os.environ['FUSION_DESIGN_RESOURCE_ROOT'] = str(self.mirror)
        for relative, action in (
            ('colors.csv', lambda: self.core.search('fixture palette', 'color')),
            ('styles.csv', lambda: self.core.search('fixture palette')),
            ('products.csv', lambda: self.core.detect_domain('fixture service')),
            ('ui-reasoning.csv', self.design_system.DesignSystemGenerator),
            ('styles.csv', self.design_system.DesignSystemGenerator),
            ('landing.csv', self.design_system.DesignSystemGenerator),
        ):
            with self.subTest(relative=relative, action=action):
                target = self.library / relative
                original = target.read_bytes()
                target.unlink()
                try:
                    with self.assertRaisesRegex(self.core.ResourceError, 'missing'):
                        action()
                finally:
                    target.write_bytes(original)
        self.network_mock.assert_not_called()

    def test_failed_download_never_reports_success_or_leaves_a_cache_hit(self):
        with mock.patch.object(self.resources, 'open_resource', side_effect=TimeoutError('offline')):
            with self.assertRaisesRegex(self.core.ResourceError, 'download failed'):
                self.core.search('fixture palette', 'color')
        self.assertEqual(self.cached_files(), set())

    def test_explicit_data_dir_keeps_fixture_missing_file_behavior(self):
        empty = self.root / 'empty-fixture'
        empty.mkdir()
        with mock.patch.object(self.core, 'DATA_DIR', empty), \
                mock.patch.object(self.resources, 'resource_file',
                                  side_effect=AssertionError('fixtures must not resolve resources')):
            self.assertIn('File not found:', self.core.search('fixture', 'color')['error'])
            self.assertIn('Stack file not found:', self.core.search_stack('fixture', 'react')['error'])
            self.assertEqual(self.core._search_csv_detailed(
                empty / 'missing.csv', [], [], 'fixture', 1)[2]['reason'], 'missing-file')
            self.assertEqual(self.core.detect_domain('saas'), 'product')
            generator = self.design_system.DesignSystemGenerator()
            self.assertEqual(generator.reasoning_data, [])
            self.assertEqual(generator.style_data, [])
            self.assertEqual(generator.landing_lookup, {})

    def test_legacy_bundled_data_works_without_a_resource_manifest(self):
        bundled = self.promax / 'data'
        bundled.mkdir()
        (bundled / 'colors.csv').write_bytes(FIXTURES['colors.csv'])
        (self.shared / 'resource-adapters/library-store.json').unlink()
        result = self.core.search('fixture palette', 'color')
        self.assertGreater(result['count'], 0)
        self.assertIn('File not found:', self.core.search('fixture', 'style')['error'])
        self.network_mock.assert_not_called()

    def test_resource_errors_are_clean_nonzero_cli_failures_without_persistence(self):
        os.environ['FUSION_DESIGN_RESOURCE_ROOT'] = str(self.mirror)
        (self.library / 'colors.csv').unlink()
        domain = self.cli('search.py', 'fixture palette', '--domain', 'color', '--json')
        self.assertNotEqual(domain.returncode, 0)
        self.assertIn('error', json.loads(domain.stdout))
        self.assertNotIn('Traceback', domain.stderr)
        design = self.cli('search.py', 'fixture service', '--design-system', '--json',
                          '--persist', '--output-dir', str(self.root))
        self.assertNotEqual(design.returncode, 0)
        payload = json.loads(design.stdout)
        self.assertIn('error', payload)
        self.assertNotIn('design_system', payload)
        self.assertFalse((self.root / 'design-system').exists())
        (self.library / 'ui-reasoning.csv').unlink()
        direct = self.cli('design_system.py', 'fixture service')
        self.assertNotEqual(direct.returncode, 0)
        self.assertIn('Error:', direct.stderr)
        self.assertNotIn('Traceback', direct.stderr)


if __name__ == '__main__':
    unittest.main()
