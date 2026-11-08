#!/usr/bin/env python3
"""Regression checks for evidence scope; JS tests use a DOM unit fixture, not a browser.

No screenshots, product examples or generated fixture media are packaged.
"""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = ImageDraw = None


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'package/skills/fusion-design-core/scripts'


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


comparison = module('side_by_side')
geometry = module('ui_geometry_audit')


@unittest.skipUnless(Image is not None, 'Pillow is required by the comparison-image helper')
class ComparisonEvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='visual-quality-check-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.shot = self.image('shot.png')
        self.target = self.image('target.png')
        self.reference = self.image('reference.png', (36, 128, 70))

    def image(self, name, color=(120, 80, 140), size=(78, 168)):
        path = self.root / name
        im = Image.new('RGB', size, color)
        draw = ImageDraw.Draw(im)
        draw.rectangle((4, 7, size[0] - 4, size[1] // 3), fill=(15, 30, 45))
        im.save(path)
        return str(path)

    def test_identical_restore_target_is_valid_evidence_not_visual_approval(self):
        report = comparison.comparison_report(self.shot, self.target, mode='restore')
        self.assertTrue(report['evidence_ready'])
        self.assertEqual(report['target_mae'], 0)
        self.assertEqual(report['target_layout'], 1)
        self.assertEqual(report['visual_verdict'], 'NOT_EVALUATED')
        self.assertEqual(report['fidelity_verdict'], 'NOT_EVALUATED')
        self.assertFalse(any(i['severity'] == 'FAIL' for i in report['issues']))

    def test_single_reference_is_enough_to_create_comparison_evidence(self):
        report = comparison.comparison_report(self.shot, refs=[self.reference])
        self.assertTrue(report['passed'])
        self.assertTrue(report['evidence_ready'])

    def test_similar_layout_does_not_infer_copying_or_invalid_chronology(self):
        target = self.image('different-colors.png', color=(230, 230, 230))
        report = comparison.comparison_report(self.shot, target, mode='compare')
        self.assertGreaterEqual(report['target_mae'], 18)
        self.assertGreaterEqual(report['target_layout'], 0.9)
        self.assertTrue(report['evidence_ready'])
        self.assertFalse(any(i['severity'] == 'FAIL' for i in report['issues']))

    def test_compare_without_any_comparison_input_is_not_ready(self):
        report = comparison.comparison_report(self.shot)
        self.assertFalse(report['passed'])
        self.assertIn('NO_COMPARISON_INPUT', [i['code'] for i in report['issues']])

    def test_restore_needs_target_even_when_references_exist(self):
        report = comparison.comparison_report(self.shot, refs=[self.reference], mode='restore')
        self.assertFalse(report['passed'])
        self.assertIn('TARGET_REQUIRED', [i['code'] for i in report['issues']])

    def test_missing_or_corrupt_reference_cannot_be_evidence(self):
        corrupt = self.root / 'corrupt.png'
        corrupt.write_text('not an image', encoding='utf-8')
        for path in [str(self.root / 'missing.png'), str(corrupt)]:
            with self.subTest(path=path):
                report = comparison.comparison_report(self.shot, refs=[path])
                self.assertFalse(report['evidence_ready'])
                self.assertIn('COMPARISON_IMAGE_UNREADABLE', [i['code'] for i in report['issues']])

    def test_other_orientation_is_scoped_warning_not_automatic_failure(self):
        wide = self.image('wide.png', size=(168, 78))
        report = comparison.comparison_report(self.shot, refs=[wide])
        self.assertTrue(report['evidence_ready'])
        self.assertIn('REF_ORIENTATION_DIFFERENT', [i['code'] for i in report['issues']])

    def test_cli_creates_real_comparison_and_does_not_certify_appearance(self):
        out = self.root / 'comparison.png'
        process = subprocess.run([sys.executable, str(SCRIPTS / 'side_by_side.py'),
                                  '--mode', 'restore', '--shot', self.shot,
                                  '--target', self.target, '-o', str(out)],
                                 capture_output=True, text=True, check=False)
        self.assertEqual(process.returncode, 0, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report['compare'], str(out))
        self.assertEqual(report['visual_verdict'], 'NOT_EVALUATED')
        with Image.open(out) as image:
            image.load()
            self.assertGreater(image.width, 0)
            self.assertGreater(image.height, 0)

    def test_cli_with_no_comparison_input_creates_no_false_comparison(self):
        out = self.root / 'not-a-comparison.png'
        process = subprocess.run([sys.executable, str(SCRIPTS / 'side_by_side.py'),
                                  '--shot', self.shot, '-o', str(out)],
                                 capture_output=True, text=True, check=False)
        self.assertNotEqual(process.returncode, 0)
        report = json.loads(process.stdout)
        self.assertFalse(report['evidence_ready'])
        self.assertIsNone(report['compare'])
        self.assertFalse(out.exists())


# This executes the exact audit JS against explicit measured-rectangle fixtures.
# It proves rule behavior only; it is not DOM rendering or a browser QA result.
DOM_FIXTURE_JS = r"""
const fs = require('fs'), vm = require('vm');
const cfg = JSON.parse(fs.readFileSync(0, 'utf8'));
const rect = (x,y,w,h) => ({left:x,top:y,right:x+w,bottom:y+h,width:w,height:h});
const leaf = (name,r) => ({tagName:'SPAN',className:'',id:'',childNodes:[{nodeType:3,textContent:name}],
  children:[],textContent:name,getBoundingClientRect:()=>r,querySelectorAll:()=>[],getAttribute:()=>null});
const zone = (name,r,textRect) => {const text=leaf(name,textRect); return {tagName:'SECTION',className:'',id:name,
  children:[text],getAttribute:k=>k==='data-zone'?name:null,getBoundingClientRect:()=>r,
  querySelectorAll:s=>s==='*'?[text]:[],contains:other=>other===text};};
const zones = cfg.collision
  ? [zone('one',rect(0,0,390,300),rect(10,20,180,30)), zone('two',rect(0,0,390,300),rect(20,25,180,30))]
  : [zone('one',rect(0,0,390,160),rect(10,20,180,30)), zone('two',rect(0,170,390,400),rect(10,190,180,30))];
const fields=[0,1,2].map(i=>({tagName:'INPUT',type:'text',getBoundingClientRect:()=>rect(10,70+i*50,100,32)}));
const images=[{tagName:'IMG',getAttribute:()=>'',getBoundingClientRect:()=>rect(10,360,60,60)}];
const inlineSvg={tagName:'svg',className:'',getAttribute:()=>null,
  getBoundingClientRect:()=>rect(8,8,24,24),
  querySelector:s=>s.startsWith('use[')?null:{tagName:'path'},
  querySelectorAll:s=>s==='circle'?[{},{}]:[]};
const iconButton={tagName:'BUTTON',className:'icon-btn',textContent:cfg.rawIcon?'+':'',
  getAttribute:()=>null,getBoundingClientRect:()=>rect(0,0,40,40),
  querySelector:s=>s==='svg'&&!cfg.rawIcon?inlineSvg:null};
let report;
const style = () => ({display:'block',visibility:'visible',position:'static',opacity:'1',transform:'none',borderRadius:'0'});
const document={documentElement:{clientWidth:390,clientHeight:844},
  querySelectorAll:s=>s==='[data-zone]'?zones:s==='img'?images:
    s==='input, select, textarea'?fields:s==='img, video, canvas, [data-hero]'?images:
    s==='button, a, div, span'&&(cfg.inlineIcon||cfg.rawIcon)?[iconButton]:
    s==='[class*="avatar"] svg'&&cfg.avatarSvg?[inlineSvg]:[],
  createElement:()=>({}),body:{innerText:'Products',appendChild:node=>{report=JSON.parse(node.textContent);}}};
const window={innerWidth:390,innerHeight:844,__QA0_CONSUMER__:true,__QA0_PAGE_TYPE__:'home',
  __QA0_HERO__:cfg.hero||null,__QA0_EXPECT__:cfg.expect||{},getComputedStyle:style};
vm.runInNewContext(cfg.script,{document,window,getComputedStyle:style,console});
process.stdout.write(JSON.stringify(report));
"""


@unittest.skipUnless(shutil.which('node'), 'Node is needed for isolated audit-JS unit tests')
class GeometryRuleTests(unittest.TestCase):
    def audit(self, **values):
        process = subprocess.run(['node', '-e', DOM_FIXTURE_JS],
                                 input=json.dumps(dict(script=geometry.AUDIT_JS, **values)),
                                 capture_output=True, text=True, check=False)
        self.assertEqual(process.returncode, 0, process.stderr)
        return json.loads(process.stdout)

    def test_home_with_small_product_images_and_no_travel_markers_is_not_rejected(self):
        report = self.audit()
        self.assertTrue(report['passed'])
        self.assertEqual(report['context'], {'consumer': True, 'page_type': 'home'})
        self.assertEqual(report['visual_verdict'], 'NOT_EVALUATED')
        self.assertEqual(report['issues'], [])

    def test_actual_cross_zone_text_collision_still_fails(self):
        report = self.audit(collision=True)
        self.assertFalse(report['passed'])
        self.assertIn('ZONE_TEXT_COLLISION', [i['code'] for i in report['issues']])

    def test_inline_svg_requests_source_review_without_inventing_authorship(self):
        report = self.audit(inlineIcon=True)
        self.assertTrue(report['passed'])
        issue = next(i for i in report['issues'] if i['code'] == 'INLINE_SVG_SOURCE_UNVERIFIED')
        self.assertEqual(issue['severity'], 'WARN')

    def test_svg_shapes_in_avatar_do_not_prove_hand_drawing(self):
        report = self.audit(avatarSvg=True)
        self.assertTrue(report['passed'])
        self.assertIn('AVATAR_SVG_SOURCE_UNVERIFIED', [i['code'] for i in report['issues']])

    def test_raw_icon_glyph_check_is_still_enforced(self):
        report = self.audit(rawIcon=True)
        self.assertFalse(report['passed'])
        self.assertIn('ICON_RAW_TEXT_GLYPH', [i['code'] for i in report['issues']])

    def test_explicit_task_hero_expectation_is_still_enforced(self):
        report = self.audit(hero={'zone': 'one', 'min': 50})
        self.assertFalse(report['passed'])
        self.assertIn('HERO_AREA_SHORT', [i['code'] for i in report['issues']])

    def test_declared_missing_zone_is_not_waived(self):
        report = self.audit(expect={'missing': '左上'})
        self.assertFalse(report['passed'])
        self.assertIn('ZONE_EXPECTED_MISSING', [i['code'] for i in report['issues']])

    def test_wrong_measured_viewport_still_fails(self):
        report = geometry.check_viewport(self.audit(), 320, 844)
        self.assertFalse(report['passed'])
        self.assertIn('VIEWPORT_MISMATCH', [i['code'] for i in report['issues']])


if __name__ == '__main__':
    unittest.main()
