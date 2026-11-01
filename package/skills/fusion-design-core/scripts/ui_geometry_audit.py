#!/usr/bin/env python3
"""
UI Geometry, Alignment & Asset Audit Script for design-thinking-os (QA0 Automated Gate)
Executes real DOM getBoundingClientRect() & computed-style checks via headless Chrome (--dump-dom)
with zero third-party Python dependencies.

Checks, for any page:
  1. ICON_RAW_TEXT_GLYPH / ICON_INLINE_HAND_DRAWN / ICON_CHILD_OFF_CENTER: icon buttons must hold a downloaded
     icon file (not a text glyph, not a hand-written <path>) and be optically centered.
  2. HEADER_VERTICAL_MISALIGNMENT: children of horizontal bars not vertically centered (centerY diff > 3px).
  3. ZONE_MARKUP_MISSING / ZONE_BOUNDING_BOX_COLLISION: top-level functional areas marked with data-zone must not overlap.
  4. AVATAR_CULTURAL_FIT_CHECK (WARN) / BANNED_HAND_DRAWN_SVG_AVATAR: stock 3D character avatars need a style review;
     hand-coded SVG faces fail.
  5. HERO_AREA_SHORT: with --hero ZONE=PCT, that data-zone must cover at least PCT percent of the viewport.
  6. FORM_SCREEN: with --consumer, three or more form controls on the first screen and no picture
     covering at least 40% of the viewport fails. A consumer home cannot be a form.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome",
    "chromium",
]

AUDIT_JS = r"""
(function() {
  const issues = [];
  const W = window.innerWidth || document.documentElement.clientWidth || 1600;
  const H = window.innerHeight || document.documentElement.clientHeight || 900;

  function rect(el) {
    const r = el.getBoundingClientRect();
    return {
      left: r.left, top: r.top, right: r.right, bottom: r.bottom,
      width: r.width, height: r.height,
      cx: r.left + r.width / 2,
      cy: r.top + r.height / 2
    };
  }

  function selectorOf(el) {
    if (!el || !el.tagName) return '';
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (el.className && typeof el.className === 'string') {
      s += '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.');
    }
    return s;
  }

  // 1. Check all small square/circular icon buttons for raw text glyphs (<, >, ‹, ←) or off-center SVG
  document.querySelectorAll('button, a, div, span').forEach(btn => {
    const r = rect(btn);
    if (r.width < 24 || r.width > 72 || r.height < 24 || r.height > 72) return;
    if (Math.abs(r.width - r.height) > 8) return;
    const cs = window.getComputedStyle(btn);
    const br = parseFloat(cs.borderRadius) || 0;
    const isIconBtn = br >= r.width * 0.35 || /icon|back|btn|circle/i.test(btn.className || '');
    if (!isIconBtn) return;

    const svg = btn.querySelector('svg');
    const rawText = (btn.textContent || '').trim();
    if (!svg && /^[<>‹›«»←→×+⚙🎙＜＞]$/.test(rawText)) {
      issues.push({
        code: 'ICON_RAW_TEXT_GLYPH',
        severity: 'FAIL',
        element: selectorOf(btn),
        message: `Icon button contains raw text character "${rawText}" instead of optically centered <svg>; font baseline causes visual off-centering.`
      });
    }
    if (svg) {
      const sr = rect(svg);
      const dx = Math.abs(r.cx - sr.cx);
      const dy = Math.abs(r.cy - sr.cy);
      if (dx > 2.0 || dy > 2.0) {
        issues.push({
          code: 'ICON_CHILD_OFF_CENTER',
          severity: 'FAIL',
          element: selectorOf(btn),
          message: `SVG inside ${selectorOf(btn)} is off-center by (dx=${dx.toFixed(1)}px, dy=${dy.toFixed(1)}px).`
        });
      }
      const usesAssetFile = btn.querySelector('img') || svg.querySelector('use[href*=".svg"], use[*|href*=".svg"]');
      const drawn = svg.querySelector('path, circle, line, polyline, polygon, rect');
      if (!usesAssetFile && drawn) {
        issues.push({
          code: 'ICON_INLINE_HAND_DRAWN',
          severity: 'FAIL',
          element: selectorOf(btn),
          message: `Icon button ${selectorOf(btn)} draws its own SVG path. Use an IconScout or icon-library file via <img> or <use href="assets/….svg">.`
        });
      }
    }
  });

  // 2. Check horizontal flex bars/headers for vertical center alignment (centerY consistency)
  document.querySelectorAll('header, nav, [class*="hud"], [class*="header"], [class*="top-bar"], [class*="toolbar"], [class*="action-bar"]').forEach(group => {
    const style = window.getComputedStyle(group);
    if (style.display !== 'flex' && style.display !== 'inline-flex') return;
    if (style.flexDirection && style.flexDirection.startsWith('column')) return;
    const children = Array.from(group.children).filter(c => {
      const cs = window.getComputedStyle(c);
      return cs.position !== 'absolute' && cs.display !== 'none' && rect(c).height > 0;
    });
    if (children.length < 2) return;
    const baseCy = rect(children[0]).cy;
    children.slice(1).forEach(ch => {
      const cy = rect(ch).cy;
      const diff = Math.abs(cy - baseCy);
      if (diff > 3.0) {
        issues.push({
          code: 'HEADER_VERTICAL_MISALIGNMENT',
          severity: 'FAIL',
          element: `${selectorOf(group)} -> ${selectorOf(ch)}`,
          message: `Child ${selectorOf(ch)} centerY (${cy.toFixed(1)}px) deviates from first sibling (${baseCy.toFixed(1)}px) by ${diff.toFixed(1)}px. Use align-items: center.`
        });
      }
      // Also check if child is a 2-line title stack next to a single icon button, causing the main title line to sit above the icon button center
      if (ch.children && ch.children.length >= 2) {
        const firstLineCy = rect(ch.children[0]).cy;
        if (Math.abs(firstLineCy - baseCy) > 4.0 && /title|brand|room/i.test(ch.className || '')) {
          issues.push({
            code: 'HEADER_MAIN_TITLE_OFFSET_FROM_ICON',
            severity: 'FAIL',
            element: `${selectorOf(ch)} -> ${selectorOf(ch.children[0])}`,
            message: `Two-line title stack pushes main title centerY (${firstLineCy.toFixed(1)}px) away from icon button centerY (${baseCy.toFixed(1)}px). Use single-line horizontal header alignment.`
          });
        }
      }
    });
  });

  // 2b. Check card rows and UI containers for crooked/tilted rotation (e.g. transform: rotate(-2deg))
  //     or vertical staircase drift across unselected sibling cards in the same horizontal row.
  document.querySelectorAll('section, div, ul, .g-card').forEach(el => {
    const cs = window.getComputedStyle(el);
    const tr = cs.transform;
    if (tr && tr !== 'none' && tr.startsWith('matrix(')) {
      const nums = tr.slice(7, -1).split(',').map(Number);
      const a = nums[0], b = nums[1];
      // 180deg flip has b ~ 0; a crooked tilt (1deg..45deg) has |b| > 0.015 and |a| > 0.5
      if (Math.abs(b) > 0.015 && Math.abs(a) > 0.5) {
        const deg = (Math.atan2(b, a) * 180 / Math.PI).toFixed(1);
        issues.push({
          code: 'CROOKED_ROTATED_ELEMENT',
          severity: 'FAIL',
          element: selectorOf(el),
          message: `Element ${selectorOf(el)} is tilted by ${deg}deg (transform: ${tr}), making the row/cards look crooked. Keep card rows and UI containers horizontally level (0deg).`
        });
      }
    }
    if (cs.display === 'flex' || cs.display === 'inline-flex') {
      if (cs.flexDirection && cs.flexDirection.startsWith('column')) return;
      const cards = Array.from(el.children).filter(c =>
        c.classList && c.classList.contains('g-card') &&
        c.getAttribute('aria-pressed') !== 'true' &&
        c.getAttribute('data-selected') !== 'true'
      );
      if (cards.length >= 2) {
        const baseCy = rect(cards[0]).cy;
        cards.slice(1).forEach(card => {
          const diff = Math.abs(rect(card).cy - baseCy);
          if (diff > 2.0) {
            issues.push({
              code: 'CARD_ROW_NOT_LEVEL',
              severity: 'FAIL',
              element: `${selectorOf(el)} -> ${selectorOf(card)}`,
              message: `Unselected cards in horizontal row ${selectorOf(el)} are not level: centerY drifts by ${diff.toFixed(1)}px. Remove container rotation or uneven margins.`
            });
          }
        });
      }
    }
  });

  // 3. Flag stock 3D character avatars for a cultural-fit review, and fail hand-drawn SVG faces.
  //    3D icons/props/badges are not flagged; only human avatars need the style-match check.
  document.querySelectorAll('img').forEach(img => {
    const src = (img.getAttribute('src') || '').toLowerCase();
    if (/3d-.*avatar|3d-man-|3d-woman-|3d-old-man|cdn3d\.iconscout\.com.*avatar/.test(src)) {
      issues.push({
        code: 'AVATAR_CULTURAL_FIT_CHECK',
        severity: 'WARN',
        element: selectorOf(img),
        message: `Stock 3D character avatar detected (${src}). Confirm it matches the product's cultural style and that all on-screen avatars share one pack; otherwise switch to style-locked AI portraits.`
      });
    }
  });
  document.querySelectorAll('[class*="avatar"] svg').forEach(svg => {
    if (svg.querySelectorAll('circle').length >= 2) {
      issues.push({
        code: 'BANNED_HAND_DRAWN_SVG_AVATAR',
        severity: 'FAIL',
        element: selectorOf(svg),
        message: `Hand-coded SVG face detected inside avatar container. Use AI-generated character portraits or real photography instead.`
      });
    }
  });

  // 4. Functional zones (declared with data-zone, per methods-ui U3):
  //    Allow intentional layered UI (hero + overlapping card/search bar, floating tab bar, full-width card fan).
  //    Only fail when two visible text leaves from different zones actually collide on screen.
  const zones = [];
  document.querySelectorAll('[data-zone]').forEach(el => {
    const r = rect(el);
    if (r.width > 0 && r.height > 0) {
      zones.push({ sel: `${selectorOf(el)}[data-zone="${el.getAttribute('data-zone')}"]`, r, el });
    }
  });
  const regionCount = document.querySelectorAll('header, nav, main, aside, footer, section').length;
  if (zones.length < 2 && regionCount >= 3) {
    issues.push({
      code: 'ZONE_MARKUP_MISSING',
      severity: 'FAIL',
      element: 'document',
      message: `Multi-region page declares ${zones.length} data-zone area(s). Mark every top-level functional area with data-zone="<name>" so zone collisions can be checked.`
    });
  }

  const textLeavesOf = (root) => {
    const out = [];
    root.querySelectorAll('*').forEach(el => {
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return;
      const hasDirectText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
      if (!hasDirectText) return;
      const r = rect(el);
      if (r.width > 4 && r.height > 4) out.push({ el, r });
    });
    return out;
  };

  for (let i = 0; i < zones.length; i++) {
    for (let j = i + 1; j < zones.length; j++) {
      const A = zones[i], B = zones[j];
      if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
      const xOverlap = Math.max(0, Math.min(A.r.right, B.r.right) - Math.max(A.r.left, B.r.left));
      const yOverlap = Math.max(0, Math.min(A.r.bottom, B.r.bottom) - Math.max(A.r.top, B.r.top));
      if (xOverlap <= 4 || yOverlap <= 4) continue;
      const leavesA = textLeavesOf(A.el);
      const leavesB = textLeavesOf(B.el);
      let collided = false;
      for (const la of leavesA) {
        if (collided) break;
        for (const lb of leavesB) {
          const tx = Math.max(0, Math.min(la.r.right, lb.r.right) - Math.max(la.r.left, lb.r.left));
          const ty = Math.max(0, Math.min(la.r.bottom, lb.r.bottom) - Math.max(la.r.top, lb.r.top));
          if (tx > 2 && ty > 2) {
            collided = true;
            issues.push({
              code: 'ZONE_TEXT_COLLISION',
              severity: 'FAIL',
              element: `${selectorOf(la.el)} (in ${A.sel}) <-> ${selectorOf(lb.el)} (in ${B.sel})`,
              message: `Text in two zones collides by ${Math.round(tx)}x${Math.round(ty)}px.`
            });
            break;
          }
        }
      }
    }
  }

  // 6. Zone map on a 3x3 grid, so the screenshot can be compared with design-decisions.md block 2.
  const COLS = ['左', '中', '右'], ROWS = ['上', '中', '下'];
  const zoneMap = zones.map(z => {
    const cx = (z.r.left + z.r.right) / 2, cy = (z.r.top + z.r.bottom) / 2;
    const col = Math.min(2, Math.max(0, Math.floor(cx / (W / 3))));
    const row = Math.min(2, Math.max(0, Math.floor(cy / (H / 3))));
    let label;
    if (row === 1 && col === 1) label = '正中';
    else if (row === 1) label = COLS[col] + '中';
    else if (col === 1) label = ROWS[row] + '中';
    else label = COLS[col] + ROWS[row];
    return {
      zone: z.el.getAttribute('data-zone'),
      position: label,
      x: Math.round(z.r.left), y: Math.round(z.r.top),
      w: Math.round(z.r.width), h: Math.round(z.r.height),
      area_pct: Math.round(100 * z.r.width * z.r.height / (W * H))
    };
  });

  const expected = (window.__QA0_EXPECT__ || {});
  Object.keys(expected).forEach(name => {
    const want = expected[name];
    const got = zoneMap.find(z => z.zone === name);
    if (!got) {
      issues.push({ code: 'ZONE_EXPECTED_MISSING', severity: 'FAIL', element: name,
        message: `design-decisions.md block 2 declares zone "${name}", but no visible data-zone="${name}" exists.` });
    }
  });

  // 7. Declared visual hero must occupy the share written in design-decisions.md block 2.
  const heroSpec = window.__QA0_HERO__ || null;
  if (heroSpec && heroSpec.zone) {
    const got = zoneMap.find(z => z.zone === heroSpec.zone);
    const min = Number(heroSpec.min) || 0;
    if (!got) {
      issues.push({ code: 'HERO_ZONE_MISSING', severity: 'FAIL', element: heroSpec.zone,
        message: `Block 2 names "${heroSpec.zone}" as the visual hero, but no visible data-zone with that name exists.` });
    } else if (got.area_pct < min) {
      issues.push({ code: 'HERO_AREA_SHORT', severity: 'FAIL', element: heroSpec.zone,
        message: `Block 2 says this hero covers at least ${min}% of the screen; measured ${got.area_pct}% (${got.w}x${got.h}).` });
    }
  }

  // 8. Consumer home: a form with only small pictures is still a prototype, even if cards and hairlines are styled.
  if (window.__QA0_CONSUMER__) {
    const visible = (el) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      return r.width > 8 && r.height > 8 && cs.visibility !== 'hidden' && cs.display !== 'none' && r.top < H && r.bottom > 0;
    };
    const controls = [...document.querySelectorAll('input, select, textarea')].filter(el => {
      if (el.tagName === 'INPUT' && (el.type === 'hidden' || el.type === 'submit' || el.type === 'button')) return false;
      return visible(el);
    });
    let maxMedia = 0;
    document.querySelectorAll('img, video, canvas, [data-hero]').forEach(el => {
      const r = el.getBoundingClientRect();
      const visW = Math.min(r.right, W) - Math.max(r.left, 0);
      const visH = Math.min(r.bottom, H) - Math.max(r.top, 0);
      if (visW > 40 && visH > 40) maxMedia = Math.max(maxMedia, visW * visH);
    });
    const mediaPct = Math.round(100 * maxMedia / (W * H));
    if (controls.length >= 3 && mediaPct < 40) {
      issues.push({ code: 'FORM_SCREEN', severity: 'FAIL', element: 'document',
        message: `First screen has ${controls.length} form controls and the largest picture is ${mediaPct}% of the screen. A consumer home cannot be a form. Start from a screen recipe (destination hero, itinerary preview, media hero, table) so one picture carries the first glance.` });
    }
  }

  const pageText = (document.body && document.body.innerText) || '';
  if (/photo\s*:|cc\s*by|creativecommons|图片来源|版权所有/i.test(pageText)) {
    issues.push({ code: 'LICENSE_ON_SCREEN', severity: 'FAIL', element: 'document',
      message: 'Author or license text is painted on the screen. Keep it in the asset sidecar, not on the product UI.' });
  }
  if ((window.__QA0_PAGE_TYPE__ || '') === 'home') {
    const stops = [...document.querySelectorAll('[data-stop]')].filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 8 && r.height > 8 && r.top < H && r.bottom > 0;
    });
    if (stops.length < 3) {
      issues.push({ code: 'HOME_IS_ONE_OBJECT', severity: 'FAIL', element: 'document',
        message: `Homepage marks ${stops.length} stops. A home screen must show what the product produces: at least 3 data-stop places or days in an example, not one picture, a slogan, and a button.` });
    }
  }

  const out = document.createElement('script');
  out.id = '__qa0_geometry_report__';
  out.type = 'application/json';
  out.textContent = JSON.stringify({
    viewport: { width: W, height: H },
    zone_map: zoneMap,
    passed: issues.every(i => i.severity !== 'FAIL'),
    issue_count: issues.length,
    issues: issues
  });
  document.body.appendChild(out);
})();
"""


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    return ""


def run_playwright(html_path: Path, width: int, height: int, expect: dict, hero, consumer: bool, page_type: str):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(html_path.resolve().as_uri())
            page.wait_for_load_state("networkidle")
            page.evaluate(
                """cfg => {
                  window.__QA0_EXPECT__ = cfg.expect;
                  window.__QA0_HERO__ = cfg.hero;
                  window.__QA0_CONSUMER__ = cfg.consumer;
                  window.__QA0_PAGE_TYPE__ = cfg.pageType;
                }""",
                {"expect": expect, "hero": hero, "consumer": consumer, "pageType": page_type},
            )
            page.evaluate(AUDIT_JS)
            raw = page.evaluate("document.getElementById('__qa0_geometry_report__').textContent")
            browser.close()
            report = json.loads(raw)
            report["engine"] = "playwright"
            return report
    except Exception as exc:  # browser missing or page error: fall back to Chrome
        return {"_fallback_reason": str(exc)[:200]}


def check_viewport(report: dict, width: int, height: int) -> dict:
    vp = report.get("viewport") or {}
    if vp.get("width") != width or vp.get("height") != height:
        report.setdefault("issues", []).append({
            "code": "VIEWPORT_MISMATCH",
            "severity": "FAIL",
            "element": "document",
            "message": f"Requested {width}x{height}, measured {vp.get('width')}x{vp.get('height')}. "
                       "Results do not describe the target screen. Install Playwright (pip install playwright && playwright install chromium) or use a wider window.",
        })
        report["passed"] = False
        report["issue_count"] = len(report["issues"])
    return report


def run_audit(html_path: Path, width: int, height: int, expect: dict = None, hero=None, consumer: bool = False, page_type: str = ""):
    expect = expect or {}
    pw = run_playwright(html_path, width, height, expect, hero, consumer, page_type)
    if pw and "_fallback_reason" not in pw:
        return check_viewport(pw, width, height)

    chrome = find_chrome()
    if not chrome:
        return {"error": "Neither Playwright nor headless Chrome is available."}

    orig = html_path.read_text(encoding="utf-8")
    expect_js = (
        "<script>"
        f"window.__QA0_EXPECT__ = {json.dumps(expect, ensure_ascii=False)};"
        f"window.__QA0_HERO__ = {json.dumps(hero, ensure_ascii=False)};"
        f"window.__QA0_CONSUMER__ = {json.dumps(bool(consumer))};"
        f"window.__QA0_PAGE_TYPE__ = {json.dumps(page_type)};"
        "</script>"
    )
    injected = orig.replace("</body>", f"{expect_js}<script>{AUDIT_JS}</script></body>")
    if "<script>" not in injected:
        injected = orig + f"<script>{AUDIT_JS}</script>"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", dir=str(html_path.parent), delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(injected)
        tmp_path = Path(tmp.name)

    try:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            f"--window-size={width},{height}",
            "--dump-dom",
            f"file://{tmp_path.resolve()}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        dom = proc.stdout
        m = re.search(
            r'<script id="__qa0_geometry_report__" type="application/json">(.*?)</script>',
            dom,
            re.S,
        )
        if not m:
            return {"error": "Failed to extract geometry report from DOM."}
        report = json.loads(html.unescape(m.group(1)))
        report["engine"] = "chrome-dump-dom"
        if pw and "_fallback_reason" in pw:
            report["playwright_error"] = pw["_fallback_reason"]
        return check_viewport(report, width, height)
    finally:
        tmp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="QA0 UI Geometry & Alignment Automated Audit")
    parser.add_argument("html_file", help="Path to HTML file to audit")
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument(
        "--expect", action="append", default=[], metavar="ZONE=位置",
        help="design-decisions.md 第 2 块写的区位置，可重复。位置用 3x3 九宫格：左上 上中 右上 左中 正中 右中 左下 下中 右下。"
             "例：--expect seat-left=左中 --expect play-center=正中",
    )
    parser.add_argument(
        "--hero", default="", metavar="ZONE=百分比",
        help="第 2 块写的视觉主角区，以及它至少占屏幕的百分比。例：--hero destination=50",
    )
    parser.add_argument(
        "--consumer", action="store_true",
        help="消费级主屏。第一屏有 3 个及以上输入框、且最大的图不足屏幕 40%，判 FORM_SCREEN。",
    )
    parser.add_argument(
        "--page-type", default="", choices=["", "home", "list", "detail", "step", "tool"],
        help="页面类型。home 时，首屏可见的 data-stop 少于 3 个就判 HOME_IS_ONE_OBJECT。",
    )
    args = parser.parse_args()

    valid = {"左上", "上中", "右上", "左中", "正中", "右中", "左下", "下中", "右下"}
    expect = {}
    for item in args.expect:
        name, _, pos = item.partition("=")
        if pos not in valid:
            sys.exit(f"--expect {item}: 位置必须是 {' '.join(sorted(valid))} 之一")
        expect[name.strip()] = pos.strip()

    hero = None
    if args.hero:
        zone, _, pct = args.hero.partition("=")
        try:
            pct_n = int(pct)
        except ValueError:
            sys.exit(f"--hero {args.hero}: 百分比必须是整数，例 --hero destination=50")
        if not zone.strip() or pct_n < 1 or pct_n > 100:
            sys.exit(f"--hero {args.hero}: 写成 区名=1到100 的整数")
        hero = {"zone": zone.strip(), "min": pct_n}

    report = run_audit(Path(args.html_file), args.width, args.height, expect, hero, args.consumer, args.page_type)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report.get("passed", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
