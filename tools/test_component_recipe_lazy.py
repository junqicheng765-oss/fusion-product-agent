"""Exercise offline recipe discovery and selected dependency/asset loading."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'package/skills/fusion-design-core/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('lazy_component_recipe_tested', SCRIPTS / 'component_recipe.py')
recipes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recipes)


class RecipeLoadingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle, self.store = self.root / 'bundle', self.root / 'store'
        self.bundle.mkdir()
        (self.bundle / 'base.css').write_text('.r-root { color: black; }')
        records = []
        for name in ('alpha', 'beta', 'spare'):
            meta = {'id': name, 'name': name, 'tags': ['base'], 'use': 'select ' + name,
                    'dont': '', 'states': [], 'source': 'test fixture', 'license': 'MIT',
                    'requires': ['beta'] if name == 'alpha' else [],
                    'icons': ['send'] if name == 'alpha' else []}
            records.append({**meta, 'file': 'recipes/' + name + '.html'})
            if name != 'spare':
                path = self.store / 'recipes' / (name + '.html')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('<!-- recipe\n' + json.dumps(meta) + '\n-->\n<style>.r-' + name +
                                ' { padding: 4px; }</style>\n<!-- demo -->\n<div class="r-' + name +
                                '"><img src="preview-assets/one.jpg"></div>\n<!-- /demo -->')
        (self.bundle / 'registry.json').write_text(json.dumps({'recipes': records}))
        for relative, content in [('icons/send.svg', '<svg viewBox="0 0 1 1"></svg>'),
                                  ('icons/LICENSE-lucide.txt', 'fixture license'),
                                  ('preview-assets/one.jpg', 'fixture image')]:
            target = self.store / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        self.fetched = []

        def fetch(relative):
            self.fetched.append(relative)
            target = self.store / relative
            if not target.is_file():
                raise recipes.ResourceError('fixture resource missing: ' + relative)
            return target

        for name, value in [('ROOT', str(self.bundle)), ('RECIPES', str(self.bundle / 'recipes')),
                            ('REGISTRY', str(self.bundle / 'registry.json')), ('recipe_resource', fetch)]:
            active = patch.object(recipes, name, value)
            active.start()
            self.addCleanup(active.stop)

    def test_list_and_search_never_materialize_payload(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            recipes.cmd_list(SimpleNamespace(tag=None))
            recipes.cmd_search(SimpleNamespace(keyword='alpha'))
        self.assertIn('alpha', output.getvalue())
        self.assertIn('spare', output.getvalue())
        self.assertEqual(self.fetched, [])

    def test_only_selected_recipe_and_dependencies_are_loaded(self):
        selected = recipes.load_selected(['alpha'])
        self.assertEqual(set(selected), {'alpha', 'beta'})
        self.assertEqual(self.fetched, ['recipes/alpha.html', 'recipes/beta.html'])
        self.assertEqual(selected['alpha']['file'], 'recipes/alpha.html')

    def test_copy_materializes_runtime_icons_and_license_but_not_preview_images(self):
        target = self.root / 'output'
        with contextlib.redirect_stdout(io.StringIO()):
            recipes.cmd_copy(SimpleNamespace(ids=['alpha'], to=str(target), preset=None))
        self.assertTrue((target / 'recipes.css').is_file())
        self.assertTrue((target / 'icons/LICENSE-lucide.txt').is_file())
        self.assertNotIn('preview-assets/one.jpg', self.fetched)
        self.assertNotIn('recipes/spare.html', self.fetched)

    def test_selected_preview_embeds_only_its_assets(self):
        target = self.root / 'preview.html'
        with patch.object(recipes, 'preset_css', return_value=':root { --primary: red; }'), \
                contextlib.redirect_stdout(io.StringIO()):
            recipes.cmd_preview(SimpleNamespace(ids='alpha', tag=None, all=False,
                                                preset='fixture', o=str(target)))
        content = target.read_text()
        self.assertIn('data:image/jpeg;base64,', content)
        self.assertNotIn('src="preview-assets/', content)
        self.assertNotIn('file://', content)
        self.assertEqual(self.fetched.count('preview-assets/one.jpg'), 1)
        self.assertNotIn('recipes/spare.html', self.fetched)

    def test_full_preview_is_not_an_implicit_default(self):
        with self.assertRaisesRegex(recipes.ResourceError, '--ids or --tag'):
            recipes.cmd_preview(SimpleNamespace(ids=None, tag=None, all=False))
        self.assertEqual(self.fetched, [])

    def test_index_refuses_partial_cache_without_downloading_missing_recipes(self):
        with patch.object(recipes, 'resource_directory', return_value=self.store):
            with self.assertRaisesRegex(recipes.ResourceError, 'partial recipe cache'):
                recipes.load_all()
        self.assertEqual(self.fetched, [])

    def test_index_with_complete_html_does_not_fetch_missing_icons(self):
        data = json.loads((self.bundle / 'registry.json').read_text())
        data['recipes'] = [row for row in data['recipes'] if row['id'] != 'spare']
        (self.bundle / 'registry.json').write_text(json.dumps(data))
        (self.store / 'icons/send.svg').unlink()
        with patch.object(recipes, 'resource_directory', return_value=self.store):
            loaded = recipes.load_all()
            with self.assertRaisesRegex(recipes.ResourceError, 'complete local icon resources'):
                recipes.build_index(loaded)
        self.assertEqual(self.fetched, [])


if __name__ == '__main__':
    unittest.main()
