"""Observable file/reference regressions; no network, browser or project fixtures."""
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote
import zlib

SCRIPT = Path(__file__).resolve().parents[1] / 'package/skills/fusion-design-core/scripts/verify_library_usage.py'
SPEC = importlib.util.spec_from_file_location('verify_library_usage', SCRIPT)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def png():
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\x00\xff\x00\x00')) + chunk(b'IEND', b''))


SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path d="M0 0L24 24"/></svg>'


class LibraryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, content):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))
        return p

    def manifest(self, **values):
        return self.write('asset-manifest.json', json.dumps(values))

    def check(self, **kwargs):
        return GATE.verify(self.root, **kwargs)

    def codes(self, rep):
        return {x['code'] for x in rep['issues']}

    def asset(self, name='assets/tea.svg', provider='iconscout', source='asset-tool-id', role='icon'):
        return {'file': name, 'provider': provider, 'source': source, 'role': role}

    def test_default_does_not_require_provider_or_component_choice(self):
        rep = self.check()
        self.assertTrue(rep['passed'])
        self.assertEqual(rep['status'], 'NO_REQUIREMENTS_REQUESTED')
        self.assertFalse(rep['execution_verified'])
        self.assertEqual(rep['coverage']['assets'], 'not_requested')

    def test_metadata_filenames_no_longer_prove_iconscout_use(self):
        self.write('icon-sources.json', '{}'); self.write('assets/icon-manifest.json', '{}')
        self.write('recipes.css', ':root { --x: 1; }'); self.write('theme.css', ':root { --x: 1; }')
        rep = self.check(require_iconscout=True)
        self.assertFalse(rep['passed'])
        self.assertEqual(rep['found']['iconscout_files_count'], 0)
        self.assertIn('ICONSCOUT_EVIDENCE_MISSING', self.codes(rep))

    def test_renamed_file_does_not_create_provider_provenance(self):
        self.write('icon-iconscout.svg', SVG)
        self.write('index.html', '<img src="icon-iconscout.svg">')
        rep = self.check(require_iconscout=True)
        self.assertFalse(rep['passed'])
        self.assertEqual(rep['found']['iconscout_files_count'], 0)

    def test_reachable_asset_with_declared_source_has_bounded_evidence(self):
        self.write('assets/tea.svg', SVG); self.write('index.html', '<img src="assets/tea.svg">')
        m = self.manifest(entrypoints=['index.html'], assets=[self.asset()])
        rep = self.check(manifest=m, require_iconscout=True)
        self.assertTrue(rep['passed'], rep)
        self.assertEqual(rep['found']['iconscout_files_count'], 1)
        self.assertTrue(rep['assets'][0]['source_declared'])
        self.assertFalse(rep['assets'][0]['source_authenticity_verified'])
        self.assertFalse(rep['license_verified'])

    def test_other_provider_asset_does_not_meet_iconscout_requirement(self):
        self.write('assets/tea.svg', SVG); self.write('index.html', '<img src="assets/tea.svg">')
        m = self.manifest(assets=[self.asset(provider='local')])
        self.assertFalse(self.check(manifest=m, require_iconscout=True)['passed'])
        self.assertTrue(self.check(manifest=m)['passed'])

    def test_declared_but_unreferenced_asset_fails(self):
        self.write('assets/tea.svg', SVG); self.write('index.html', '<main>Content</main>')
        m = self.manifest(assets=[self.asset()])
        self.assertIn('ASSET_UNVERIFIED', self.codes(self.check(manifest=m)))

    def test_missing_malformed_and_metadata_as_media_fail(self):
        for name, content in [('missing.svg', None), ('bad.svg', '<svg'), ('icon.png', b'{}'), ('icon.json', b'{}')]:
            with self.subTest(name=name):
                if content is not None: self.write(name, content)
                self.write('index.html', '<img src="{}">'.format(name))
                m = self.manifest(assets=[self.asset(name)])
                self.assertIn('ASSET_UNVERIFIED', self.codes(self.check(manifest=m)))

    def test_fake_or_empty_svg_does_not_pass_media_check(self):
        for value in ('<metadata/>', '<svg xmlns="http://www.w3.org/2000/svg"/>'):
            self.write('assets/tea.svg', value); self.write('index.html', '<img src="assets/tea.svg">')
            m = self.manifest(assets=[self.asset()])
            self.assertFalse(self.check(manifest=m)['passed'])

    def test_missing_source_is_unverified(self):
        self.write('assets/tea.svg', SVG); self.write('index.html', '<img src="assets/tea.svg">')
        m = self.manifest(assets=[self.asset(source='')])
        self.assertFalse(self.check(manifest=m)['passed'])

    def test_stylesheet_must_be_reachable_and_imports_are_followed(self):
        self.write('vendor/recipes.css', '.entry { color: red; }')
        self.write('theme.css', ':root { --ink: black; }')
        self.write('main.css', '@import "vendor/recipes.css"; @import url("theme.css");')
        self.write('index.html', '<link rel="stylesheet" href="main.css">')
        self.assertTrue(self.check(require_recipes=True, require_theme=True)['passed'])
        self.write('index.html', '<main>No imported styles</main>')
        rep = self.check(require_recipes=True, require_theme=True)
        self.assertIn('RECIPES_NOT_LOADED', self.codes(rep))
        self.assertIn('THEME_NOT_LOADED', self.codes(rep))

    def test_asset_or_preload_edges_do_not_load_stylesheets(self):
        self.write('theme.css', ':root { --ink: black; }')
        for html in ('<img src="theme.css">', '<script src="theme.css"></script>',
                     '<link rel="preload" as="style" href="theme.css">',
                     '<link rel="stylesheet" href="theme.css" disabled>',
                     '<link rel="alternate stylesheet" href="theme.css">'):
            with self.subTest(html=html):
                self.write('index.html', html)
                rep = self.check(require_theme=True)
                self.assertIn('THEME_NOT_LOADED', self.codes(rep))
                self.assertEqual(rep['found']['theme_css'], [])
                self.assertFalse(self.check(require_stylesheets=['theme.css'])['passed'])

    def test_unloaded_css_cannot_supply_imports_or_embedded_assets(self):
        self.write('theme.css', ':root { --ink: black; }')
        self.write('assets/tea.svg', SVG)
        self.write('main.css', '@import "theme.css"; .i {{ mask: url("data:image/svg+xml,{}"); }}'.format(quote(SVG)))
        self.write('index.html', '<img src="main.css">')
        m = self.manifest(assets=[self.asset()])
        rep = self.check(manifest=m, require_theme=True)
        self.assertIn('THEME_NOT_LOADED', self.codes(rep))
        self.assertIn('ASSET_UNVERIFIED', self.codes(rep))

    def test_inline_style_import_loads_css_but_style_attribute_cannot(self):
        self.write('theme.css', ':root { --ink: black; }')
        self.write('index.html', '<style>@import url("theme.css");</style>')
        self.assertTrue(self.check(require_theme=True)['passed'])
        self.write('index.html', '<div style="@import url(theme.css)"></div>')
        self.assertFalse(self.check(require_theme=True)['passed'])

    def test_manifest_can_name_task_specific_theme(self):
        self.write('ui.css', ':root { --ink: black; }'); self.write('index.html', '<link rel="stylesheet" href="ui.css">')
        m = self.manifest(stylesheets=[{'file': 'ui.css', 'role': 'theme'}])
        self.assertTrue(self.check(manifest=m, require_theme=True)['passed'])

    def test_required_stylesheet_cannot_be_unused_or_comment_only(self):
        self.write('unused.css', ':root { --ink: black; }'); self.write('index.html', '<main>Content</main>')
        self.assertFalse(self.check(require_stylesheets=['unused.css'])['passed'])
        self.write('unused.css', '/* no CSS rules */'); self.write('index.html', '<link rel="stylesheet" href="unused.css">')
        self.assertFalse(self.check(require_stylesheets=['unused.css'])['passed'])

    def test_png_content_and_role_requirements(self):
        self.write('assets/photo.png', png()); self.write('index.html', '<img src="assets/photo.png">')
        m = self.manifest(assets=[self.asset('assets/photo.png', 'original', 'local-shot-id', 'photo')])
        self.assertTrue(self.check(manifest=m, require_photos=True)['passed'])
        self.assertFalse(self.check(manifest=m, require_avatars=1)['passed'])

    def test_png_crc_corruption_is_rejected(self):
        bad = bytearray(png()); bad[30] ^= 1
        self.write('assets/photo.png', bytes(bad)); self.write('index.html', '<img src="assets/photo.png">')
        m = self.manifest(assets=[self.asset('assets/photo.png')])
        self.assertFalse(self.check(manifest=m)['passed'])

    def test_duplicate_canonical_asset_does_not_inflate_role_or_provider_count(self):
        self.write('assets/avatar.svg', SVG)
        (self.root / 'alias.svg').symlink_to(self.root / 'assets/avatar.svg')
        self.write('index.html', '<img src="assets/avatar.svg">')
        rows = [self.asset('assets/avatar.svg', role='avatar'),
                self.asset('assets/../assets/avatar.svg', role='avatar'),
                self.asset('alias.svg', role='avatar')]
        m = self.manifest(assets=rows)
        rep = self.check(manifest=m, require_avatars=3)
        self.assertIn('AVATAR_EVIDENCE_MISSING', self.codes(rep))
        self.assertEqual(rep['found']['iconscout_files_count'], 1)
        self.assertEqual(len(rep['assets']), 1)
        self.assertTrue(self.check(manifest=m, require_avatars=1)['passed'])

    def test_conflicting_duplicate_asset_declarations_fail(self):
        self.write('assets/tea.svg', SVG); self.write('index.html', '<img src="assets/tea.svg">')
        for row in (self.asset(provider='other'), self.asset(source='other-id'), self.asset(role='photo')):
            with self.subTest(row=row):
                m = self.manifest(assets=[self.asset(), row])
                rep = self.check(manifest=m)
                self.assertIn('ASSET_RECORD_CONFLICT', self.codes(rep))
                self.assertEqual(len(rep['assets']), 1)

    def test_asset_role_is_required_and_nonempty(self):
        self.write('assets/tea.svg', SVG); self.write('index.html', '<img src="assets/tea.svg">')
        for role in (None, '', '  ', []):
            with self.subTest(role=role):
                m = self.manifest(assets=[self.asset(role=role)])
                self.assertIn('ASSET_UNVERIFIED', self.codes(self.check(manifest=m)))
        row = self.asset(); row.pop('role')
        m = self.manifest(assets=[row])
        self.assertIn('ASSET_UNVERIFIED', self.codes(self.check(manifest=m)))

    def test_framed_glb_with_wrong_json_types_returns_unverified(self):
        self.write('index.html', '<model-viewer src="asset.glb"></model-viewer>')
        for data in ([], {'asset': []}, {'asset': '2.0'}, {'asset': {'version': '2.0'}, 'meshes': 'wrong'}):
            with self.subTest(data=data):
                body = json.dumps(data).encode('utf-8'); body += b' ' * ((-len(body)) % 4)
                blob = b'glTF' + struct.pack('<III', 2, 20 + len(body), len(body)) + b'JSON' + body
                self.write('asset.glb', blob)
                m = self.manifest(assets=[self.asset('asset.glb')])
                self.assertIn('ASSET_UNVERIFIED', self.codes(self.check(manifest=m)))

    def test_base_href_is_unverified_instead_of_certifying_wrong_local_path(self):
        self.write('icon.svg', SVG)
        self.write('index.html', '<base href="assets/"><img src="icon.svg">')
        m = self.manifest(assets=[self.asset('icon.svg')])
        rep = self.check(manifest=m)
        self.assertIn('LOCAL_REFERENCE_INVALID', self.codes(rep))
        self.assertEqual(rep['assets'], [])

    def test_inert_template_references_are_not_loaded(self):
        self.write('theme.css', ':root { --ink: black; }'); self.write('assets/tea.svg', SVG)
        self.write('index.html', '<template><link rel="stylesheet" href="theme.css"><img src="assets/tea.svg"></template>')
        m = self.manifest(assets=[self.asset()])
        rep = self.check(manifest=m, require_theme=True)
        self.assertIn('THEME_NOT_LOADED', self.codes(rep))
        self.assertIn('ASSET_UNVERIFIED', self.codes(rep))

    def test_lottie_json_is_structurally_distinct_from_manifest(self):
        animation = {'v': '5.9.0', 'fr': 30, 'ip': 0, 'op': 30, 'w': 24, 'h': 24,
                     'layers': [{'ty': 4, 'shapes': [{'ty': 'rc'}]}]}
        self.write('motion.json', json.dumps(animation)); self.write('index.html', '<lottie-player src="motion.json"></lottie-player>')
        m = self.manifest(assets=[self.asset('motion.json', role='motion')])
        self.assertTrue(self.check(manifest=m, require_iconscout=True)['passed'])
        animation['layers'] = []
        self.write('motion.json', json.dumps(animation))
        self.assertFalse(self.check(manifest=m)['passed'])

    def test_css_embedded_asset_matches_real_content(self):
        self.write('assets/tea.svg', SVG)
        self.write('icons.css', '.i {{ mask-image: url("data:image/svg+xml,{}"); }}'.format(quote(SVG)))
        self.write('index.html', '<link rel="stylesheet" href="icons.css"><span class="i"></span>')
        m = self.manifest(assets=[self.asset()])
        rep = self.check(manifest=m, require_iconscout=True)
        self.assertTrue(rep['passed'], rep)
        self.assertTrue(rep['assets'][0]['embedded_content_match'])

    def test_external_css_does_not_prove_local_file_loaded(self):
        self.write('theme.css', ':root { --x: 1; }')
        self.write('index.html', '<link rel="stylesheet" href="https://example.invalid/theme.css">')
        self.assertFalse(self.check(require_theme=True)['passed'])

    def test_role_flags_do_not_accept_comment_only_css(self):
        self.write('theme.css', '/* no CSS */')
        self.write('index.html', '<link rel="stylesheet" href="theme.css">')
        self.assertFalse(self.check(require_theme=True)['passed'])

    def test_empty_css_url_does_not_crash(self):
        self.write('theme.css', '.entry { background: url(""); }')
        self.write('index.html', '<link rel="stylesheet" href="theme.css">')
        self.assertTrue(self.check(require_theme=True)['passed'])

    def test_path_escape_rejected_and_candidates_excluded(self):
        self.write('index.html', '<main>Content</main>')
        m = self.manifest(assets=[self.asset('../outside.svg')])
        self.assertFalse(self.check(manifest=m)['passed'])
        row = self.asset('unmade.svg'); row['required'] = False
        m = self.manifest(assets=[row])
        self.assertTrue(self.check(manifest=m)['passed'])

    def test_symlink_escape_cannot_supply_asset_evidence(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / 'tea.svg'; outside.write_text(SVG)
            (self.root / 'tea.svg').symlink_to(outside)
            self.write('index.html', '<img src="tea.svg">')
            m = self.manifest(assets=[self.asset('tea.svg')])
            self.assertFalse(self.check(manifest=m)['passed'])

    def test_malformed_manifest_and_missing_entrypoint_do_not_crash(self):
        m = self.write('asset-manifest.json', '{')
        self.assertIn('MANIFEST_INVALID', self.codes(self.check(manifest=m)))
        m = self.manifest(entrypoints=['not-there.html'])
        self.assertIn('LOCAL_REFERENCE_INVALID', self.codes(self.check(manifest=m)))

    def test_cli_exit_status_matches_requested_evidence(self):
        self.write('icon-sources.json', '{}')
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--require-iconscout'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)['passed'])
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)['status'], 'NO_REQUIREMENTS_REQUESTED')


if __name__ == '__main__':
    unittest.main()
