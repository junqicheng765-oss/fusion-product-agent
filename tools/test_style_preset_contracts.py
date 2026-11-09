"""Check effective preset values across readers/exporters without producing UI fixtures."""
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'package/skills/fusion-design-core/scripts'
sys.path.insert(0, str(SCRIPTS))
import style_preset as presets
import style_consistency_audit as consistency


def cli(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / 'style_preset.py'), *args],
                          check=True, capture_output=True, text=True).stdout


def css_blocks(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    return {selector.strip(): dict(re.findall(r'--([\w-]+):\s*([^;]+);', body))
            for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css)}


class PresetContractTests(unittest.TestCase):
    def test_show_exposes_catalogue_connections_beyond_theme_values(self):
        reg = presets.registry()
        for group, entries in reg['presets'].items():
            for entry in entries:
                with self.subTest(group=group, preset=entry['id']):
                    original = deepcopy(reg)
                    stream = io.StringIO()
                    with patch.object(presets, 'registry', return_value=reg):
                        with redirect_stdout(stream):
                            presets.cmd_show(SimpleNamespace(id=entry['id'], json=True))
                    shown = json.loads(stream.getvalue())
                    expected = [family for family in reg['families']
                                if family['id'] in entry.get('family', [])
                                or entry['id'] in family.get(group, [])]
                    self.assertEqual(shown['related_resources']['families'], expected)
                    for category, rows in shown['related_resources']['libraries'].items():
                        source_rows = {row['id']: row for row in reg['libraries'][category]}
                        for row in rows:
                            self.assertEqual(row, source_rows[row['id']])
                    self.assertEqual(reg, original)

    def test_theme_reader_keeps_task_routes_and_their_limits_visible(self):
        travel = json.loads(cli('show', 'CN-02', '--json'))
        family = next(f for f in travel['related_resources']['families'] if f['id'] == 'travel')
        self.assertIn('travel', family['recipes'])
        self.assertEqual(family['layout'], [])
        self.assertTrue(family['layoutNote'])
        warm = json.loads(cli('show', 'INT-05', '--json'))
        self.assertEqual({f['id'] for f in warm['related_resources']['families']},
                         {'ai-product', 'editorial'})
        self.assertIn('scenes', warm['related_resources']['families'][0])
        self.assertNotIn('components', warm['design_spec']['values'])
        system = json.loads(cli('show', 'apple-native', '--json'))
        self.assertTrue(system['design_spec']['values']['components'])
        apple_source = next(row for row in system['related_resources']['libraries']['designSystems']
                            if row['id'] == 'apple-hig')
        self.assertEqual(apple_source['url'], 'https://developer.apple.com/design/human-interface-guidelines')
        self.assertTrue(apple_source['license'])
        self.assertTrue(apple_source['get'])
        text = cli('show', 'apple-native')
        self.assertIn(apple_source['url'], text)
        self.assertIn(apple_source['license'], text)
        unknown = presets.related_resources('dto', {'id': 'unregistered-resource'})
        self.assertEqual(unknown['families'], [])
        self.assertEqual(unknown['libraries'], {})

    def test_json_show_keeps_stored_design_guidance_across_catalogue(self):
        for group, entries in presets.registry()['presets'].items():
            for entry in entries:
                with self.subTest(group=group, preset=entry['id']):
                    _, _, raw = presets.resolve(entry['id'])
                    original = deepcopy(raw)
                    stream = io.StringIO()
                    with redirect_stdout(stream):
                        presets.cmd_show(SimpleNamespace(id=entry['id'], json=True))
                    shown = json.loads(stream.getvalue())
                    expected = {key: value for key, value in raw.get('meta', {}).get('dto', {}).items()
                                if key not in ('palette', 'sourcePalette')}
                    self.assertEqual(shown['design_spec']['values'], expected)
                    self.assertEqual(shown['design_spec']['source'], 'meta.dto')
                    self.assertEqual(shown['design_spec']['role'], 'stored-design-guidance')
                    self.assertEqual(shown['registry_entry'], entry)
                    self.assertEqual(raw, original)

    def test_cli_design_spec_contains_system_rules_and_dto_craft(self):
        system = json.loads(cli('show', 'apple-native', '--json'))
        _, _, raw_system = presets.resolve('apple-native')
        for field in ('typeScale', 'spacing', 'radiusScale', 'components', 'motion',
                      'implementation', 'sources', 'license', 'installables'):
            self.assertEqual(system['design_spec']['values'][field], raw_system['meta']['dto'][field])
        oriental = json.loads(cli('show', 'CN-06', '--json'))
        _, _, raw_oriental = presets.resolve('CN-06')
        for field in ('typeScale', 'spacing', 'radiusScale', 'border', 'shadow', 'blur'):
            self.assertEqual(oriental['design_spec']['values'][field], raw_oriental['meta']['dto'][field])
        self.assertNotIn('components', oriental['design_spec']['values'])
        self.assertNotIn('palette', oriental['design_spec']['values'])
        self.assertEqual(oriental['modes']['light']['primary'], raw_oriental['cssVars']['light']['primary'])
        self.assertIn('not automatically applied', oriental['design_spec']['limits'])

    def test_json_design_spec_preserves_sparse_and_new_fields_without_filling_gaps(self):
        data = {'cssVars': {'light': {'primary': '#123456'}}, 'meta': {'dto': {
            'components': {}, 'motion': False, 'spacing': 0,
            'futureRules': {'layers': [], 'disabled': False},
            'palette': {'primary': '#FA0102'}, 'sourcePalette': {'primary': '#FB0203'},
        }}}
        original = deepcopy(data)
        with patch.object(presets, 'resolve', return_value=('dto', {'id': 'TEST'}, data)):
            stream = io.StringIO()
            with redirect_stdout(stream):
                presets.cmd_show(SimpleNamespace(id='TEST', json=True))
            shown = json.loads(stream.getvalue())
        self.assertEqual(shown['design_spec']['values'], {
            'components': {}, 'motion': False, 'spacing': 0,
            'futureRules': {'layers': [], 'disabled': False},
        })
        self.assertNotIn('typeScale', shown['design_spec']['values'])
        self.assertEqual(shown['modes']['light']['primary'], '#123456')
        self.assertEqual(shown['reference_palette']['values']['primary'], '#FB0203')
        self.assertEqual(data, original)

    def test_registered_presets_report_the_values_they_export(self):
        for group, entries in presets.registry()['presets'].items():
            for entry in entries:
                with self.subTest(group=group, preset=entry['id']):
                    _, _, raw = presets.resolve(entry['id'])
                    stream = io.StringIO()
                    with redirect_stdout(stream):
                        presets.cmd_show(SimpleNamespace(id=entry['id'], json=True))
                    shown = json.loads(stream.getvalue())
                    blocks = css_blocks(presets.to_css(raw))
                    self.assertEqual(shown['application_source'], 'cssVars')
                    self.assertEqual(blocks[':root'], {**shown['theme'], **shown['modes'].get('light', {})})
                    if '.dark' in blocks:
                        self.assertEqual(blocks['.dark'], shown['modes']['dark'])
                    for mode in ('light', 'dark'):
                        if mode in shown['modes']:
                            single = css_blocks(presets.to_css(raw, mode))
                            self.assertEqual(single[':root'], {**shown['theme'], **shown['modes'][mode]})

    def test_cli_show_export_and_prompt_input_have_one_actual_primary(self):
        shown = json.loads(cli('show', 'INT-05', '--json'))
        exported = css_blocks(cli('export', 'INT-05', '--format', 'css'))
        native = json.loads(cli('export', 'INT-05', '--format', 'antd'))
        self.assertEqual(shown['modes']['light']['primary'], '#B65839')
        self.assertEqual(exported[':root']['primary'], '#B65839')
        self.assertEqual(native['token']['colorPrimary'], '#B65839')
        # show --json is the source for composed prompt parameters, not the
        # historical/reference palette, which remains available for tracing.
        self.assertEqual(shown['reference_palette']['values']['primary'], '#CC785C')
        self.assertEqual(shown['reference_palette']['role'], 'reference-only')
        self.assertIn('primary', {row['token'] for row in shown['reference_differences']})

    def test_surface_intent_is_traced_without_replacing_effective_surface(self):
        _, _, raw = presets.resolve('INT-03')
        report = presets.palette_contract(raw)
        self.assertEqual(report['modes']['light']['card'], '#111214')
        self.assertEqual(report['reference_palette']['values']['card'], 'rgba(255,255,255,0.03)')
        self.assertIn('card', {row['token'] for row in report['reference_differences']})

    def test_shadcn_export_preserves_all_runtime_values_and_labels_reference(self):
        for entry in presets.registry()['presets']['dto']:
            with self.subTest(preset=entry['id']):
                _, _, raw = presets.resolve(entry['id'])
                original = deepcopy(raw)
                exported = json.loads(presets.to_shadcn(raw))
                self.assertEqual(raw, original)
                self.assertEqual(exported['cssVars'], original['cssVars'])
                self.assertEqual(exported['meta']['dto']['palette'], original['meta']['dto']['palette'])
                contract = exported['meta']['presetContract']
                self.assertEqual(contract['applicationSource'], 'cssVars')
                self.assertEqual(contract['referencePaletteRole'], 'reference-only')
                expected = raw['cssVars']['light']['primary']
                self.assertEqual(json.loads(presets.to_antd(raw))['token']['colorPrimary'], expected)

    def test_platform_defaults_are_preserved_but_conflicting_semantic_color_is_not(self):
        _, _, raw = presets.resolve('ant-design')
        self.assertEqual(json.loads(presets.to_antd(raw))['token'], raw['meta']['dto']['antdToken'])
        changed = deepcopy(raw)
        changed['meta']['dto']['antdToken']['colorPrimary'] = '#123456'
        token = json.loads(presets.to_antd(changed))['token']
        self.assertEqual(token['colorPrimary'], changed['cssVars']['light']['primary'])
        self.assertEqual(token['controlHeight'], raw['meta']['dto']['antdToken']['controlHeight'])

    def test_unmapped_native_background_override_is_reported_not_promised(self):
        _, _, raw = presets.resolve('ant-design')
        changed = deepcopy(raw)
        changed['cssVars']['light']['background'] = '#123456'
        report = presets.palette_contract(changed)
        css = css_blocks(presets.to_css(changed))
        native = json.loads(presets.to_antd(changed))['token']
        self.assertEqual(report['modes']['light']['background'], '#123456')
        self.assertEqual(css[':root']['background'], '#123456')
        self.assertEqual(native, raw['meta']['dto']['antdToken'])
        boundary = report['platform_export_contracts']['antd']
        self.assertNotIn('background', boundary['propagated_semantic_tokens'])
        self.assertIn('background', boundary['not_propagated_semantic_tokens'])
        self.assertTrue(boundary['native_token_defaults_preserved'])
        exported = json.loads(presets.to_shadcn(changed))
        self.assertEqual(exported['meta']['presetContract']['platformExportContracts']['antd'], boundary)
        with patch.object(presets, 'resolve', return_value=('systems', {'id': 'ant-design'}, changed)):
            stream = io.StringIO()
            with redirect_stdout(stream):
                presets.cmd_show(SimpleNamespace(id='ant-design', json=True))
            shown = json.loads(stream.getvalue())
            self.assertEqual(shown['platform_export_contracts']['antd'], boundary)

    def test_apply_mode_and_idempotence_keep_unrelated_project_css(self):
        all_entries = [entry for items in presets.registry()['presets'].values() for entry in items]
        entry = next(entry for entry in all_entries
                     if presets.resolve(entry['id'])[2].get('cssVars', {}).get('dark') !=
                     presets.resolve(entry['id'])[2].get('cssVars', {}).get('light'))
        _, _, raw = presets.resolve(entry['id'])
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'global.css'
            target.write_text('body { margin: 0; }\n', encoding='utf-8')
            cli('apply', entry['id'], '--css', str(target), '--mode', 'dark')
            first = target.read_text(encoding='utf-8')
            self.assertIn('body { margin: 0; }', first)
            self.assertEqual(css_blocks(first)[':root']['primary'], raw['cssVars']['dark']['primary'])
            cli('apply', entry['id'], '--css', str(target), '--mode', 'dark')
            self.assertEqual(target.read_text(encoding='utf-8'), first)

    def test_human_show_exposes_effective_and_reference_roles(self):
        output = cli('show', 'INT-05')
        self.assertIn('cssVars.<mode>', output)
        self.assertIn('effective=#B65839', output)
        self.assertIn('reference=#CC785C', output)


class AuditPaletteTests(unittest.TestCase):
    def test_history_and_documentation_do_not_grant_color_exemptions(self):
        data = {'cssVars': {'light': {'primary': '#123456'}, 'dark': {'primary': '#234567'}},
                'meta': {'dto': {'palette': {'primary': '#FA0102', 'extra': ['#FB0203']},
                                 'sourcePalette': {'primary': '#FC0304'},
                                 'history': {'old': '#FD0405'}, 'notes': 'source #FE0506',
                                 'effectiveAuxiliaryColors': {'highlight': '#345678'},
                                 'platformColors': {'status': ['#456789', '#56789A']},
                                 'antdToken': {'colorSuccess': '#6789AB', 'colorBgBase': '#FAFA01'}}}}
        with patch.object(consistency, 'resolve', return_value=('dto', {'id': 'TEST'}, data)):
            spec = consistency.preset_spec('TEST')
        allowed = set(spec['colors'])
        for value in ('#123456', '#234567', '#345678', '#456789', '#56789A', '#6789AB'):
            self.assertIn(consistency.parse_color(value), allowed)
        for value in ('#FA0102', '#FB0203', '#FC0304', '#FD0405', '#FE0506', '#FAFA01'):
            self.assertNotIn(consistency.parse_color(value), allowed)
        issues = consistency.audit([{'url': 'saved-probe', 'elements': [
            {'sel': 'p', 'color': 'rgb(250, 1, 2)'}]}], spec, 0)
        self.assertIn('OFF_TOKEN_COLOR', {issue['code'] for issue in issues})

    def test_registered_system_semantic_colors_and_actual_mode_tokens_remain_supported(self):
        for entries in presets.registry()['presets'].values():
            for entry in entries:
                with self.subTest(preset=entry['id']):
                    _, _, raw = presets.resolve(entry['id'])
                    spec = consistency.preset_spec(entry['id'])
                    for values in presets.palette_contract(raw)['modes'].values():
                        for value in values.values():
                            color = consistency.parse_color(value)
                            if color:
                                self.assertIn(color, spec['colors'])
        apple = consistency.preset_spec('apple-native')
        self.assertIn(consistency.parse_color('#34C759'), apple['colors'])
        ant = consistency.preset_spec('ant-design')
        self.assertIn(consistency.parse_color('#52c41a'), ant['colors'])


if __name__ == '__main__':
    unittest.main()
