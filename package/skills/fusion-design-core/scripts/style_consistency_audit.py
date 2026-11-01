#!/usr/bin/env python3
"""跨页风格一致性检查（Design Style Engine 的 DS5 验收门）。

在无头 Chrome 里读取每个页面所有可见元素的计算样式，检查：
  1. OFF_TOKEN_COLOR   文字色 / 背景色 / 边框色不在所选预设的色板里（FAIL）
  2. OFF_SCALE_RADIUS  圆角不在预设的圆角阶梯里（FAIL）
  3. OFF_TOKEN_FONT    字体不在预设的字体栈里（FAIL）
  4. CROSS_PAGE_DRIFT  同一类组件（按钮、输入框、卡片、标题、标签等）在不同页面的圆角/字号/字体/底色不一致（FAIL）
  5. PALETTE_SPRAWL    未指定预设时，全站去重颜色过多（WARN）

用法：
  python3 style_consistency_audit.py page1.html page2.html ... [--preset INT-02]
  # 线上或本地开发服务器页面：先打印探针脚本，在浏览器里执行后把 JSON 存成文件，再一起检查
  python3 style_consistency_audit.py --probe-js > probe.js
  python3 style_consistency_audit.py --from-json home.json --from-json settings.json --preset apple-native

不参与检查的元素：加 data-style-exempt（图片、插画、品牌 Logo、第三方嵌入）。
"""
import argparse, html, json, os, re, subprocess, sys, tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from style_preset import resolve, oklch_to_hex, radius_px, theme_vars  # noqa: E402

CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"]

PROBE_JS = r"""
(function() {
  const out = [];
  const sigOf = el => {
    const t = el.tagName.toLowerCase();
    const comp = el.getAttribute('data-component');
    if (comp) return comp;
    const cls = (typeof el.className === 'string' ? el.className : '').toLowerCase();
    const role = el.getAttribute('role') || '';
    if (t === 'button' || role === 'button' || /\b(btn|button)\b/.test(cls)) return 'button';
    if (t === 'input' || t === 'select' || t === 'textarea') return 'input';
    if (/^h[1-4]$/.test(t)) return t;
    if (/\bcard\b/.test(cls)) return 'card';
    if (/\b(tag|chip|badge|pill)\b/.test(cls)) return 'tag';
    if (t === 'nav' || /\b(navbar|tabbar|topbar)\b/.test(cls)) return 'nav';
    return '';
  };
  const sel = el => {
    let s = el.tagName.toLowerCase();
    if (el.id) s += '#' + el.id;
    if (typeof el.className === 'string' && el.className.trim()) s += '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.');
    return s;
  };
  document.querySelectorAll('body *').forEach(el => {
    if (el.closest('[data-style-exempt], svg, script, style, img, video, canvas, iframe')) return;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) return;
    const hasText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
    const bw = parseFloat(cs.borderTopWidth) || 0;
    out.push({
      sel: sel(el), sig: sigOf(el), h: Math.round(r.height),
      color: hasText ? cs.color : null,
      bg: cs.backgroundColor,
      border: bw > 0 && cs.borderTopStyle !== 'none' ? cs.borderTopColor : null,
      gradient: /gradient/.test(cs.backgroundImage) ? cs.backgroundImage : null,
      shadow: cs.boxShadow && cs.boxShadow !== 'none' ? cs.boxShadow : null,
      radius: cs.borderTopLeftRadius,
      font: hasText ? cs.fontFamily : null,
      size: hasText ? cs.fontSize : null
    });
  });
  return { url: location.href, elements: out };
})()
"""

GENERIC_FONTS = {"sans-serif", "serif", "monospace", "system-ui", "ui-sans-serif", "ui-serif", "ui-monospace", "-apple-system",
                 "blinkmacsystemfont", "cursive", "fantasy", "inherit", "apple color emoji", "segoe ui emoji", "noto color emoji"}


def parse_color(s):
    if not s:
        return None
    s = s.strip()
    if s.startswith("oklch"):
        s = oklch_to_hex(s)
    m = re.match(r"#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?$", s)
    if m:
        h = m.group(1)
        a = int(m.group(2), 16) / 255 if m.group(2) else 1.0
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)
    m = re.match(r"#([0-9a-fA-F]{3})$", s)
    if m:
        h = m.group(1)
        return (int(h[0] * 2, 16), int(h[1] * 2, 16), int(h[2] * 2, 16), 1.0)
    m = re.match(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?", s)
    if m:
        a = m.group(4)
        a = (float(a[:-1]) / 100 if a and a.endswith("%") else float(a)) if a else 1.0
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)
    return None


def dist(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1[:3], c2[:3])) ** 0.5 + abs(c1[3] - c2[3]) * 255


def same_hue_shade(c, palette):
    """Allow lighter/darker shades or alpha variations of an existing palette color (for hover/active/tint/depth)."""
    import colorsys
    if c[3] < 0.92:
        # Semi-transparent tint of any palette RGB is valid depth/glass material
        if min((sum((a - b) ** 2 for a, b in zip(c[:3], p[:3])) ** 0.5 for p in palette), default=999) <= 42:
            return True
    h1, l1, s1 = colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)
    for p in palette:
        h2, l2, s2 = colorsys.rgb_to_hls(p[0] / 255, p[1] / 255, p[2] / 255)
        if s1 >= 0.15 and s2 >= 0.15:
            dh = min(abs(h1 - h2), 1.0 - abs(h1 - h2))
            if dh <= 0.045 and abs(s1 - s2) <= 0.35:
                return True
    return False


def preset_spec(pid):
    _, item, data = resolve(pid)
    theme, light, dark = theme_vars(data)
    meta = data.get("meta", {}).get("dto", {})
    raw = list(light.values()) + list(dark.values())
    pal = meta.get("palette", {})
    raw += [pal.get("bg", ""), pal.get("card", ""), pal.get("primary", "")] + list(pal.get("text", [])) + list(pal.get("extra", []))
    for pair in meta.get("platformColors", {}).values():
        raw += list(pair)
    raw += re.findall(r"#[0-9a-fA-F]{6}\b", json.dumps(meta, ensure_ascii=False))
    colors = [c for c in (parse_color(v) for v in raw if isinstance(v, str)) if c]
    base = radius_px(theme.get("radius"))
    radii = {0, base, base - 2, base - 4, base + 4}
    for v in (meta.get("radiusScale") or {}).values():
        if isinstance(v, (int, float)):
            radii.add(int(v))
    fonts = set()
    for k in ("font-sans", "font-serif", "font-mono"):
        for f in (theme.get(k) or "").split(","):
            fonts.add(f.strip().strip('"\'').lower())
    return {"id": item["id"], "colors": colors, "radii": radii, "fonts": fonts - {""}}


def run_page_playwright(path, width, height):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(Path(path).resolve().as_uri())
            page.wait_for_load_state("networkidle")
            d = page.evaluate(PROBE_JS)
            browser.close()
            d["url"] = str(path)
            return d
    except Exception:
        return None


def run_page(path, width, height):
    d = run_page_playwright(path, width, height)
    if d:
        return d
    chrome = next((c for c in CHROME if os.path.exists(c)), None)
    if not chrome:
        return {"error": "找不到 Chrome"}
    src = Path(path).read_text(encoding="utf-8")
    js = "(function(){const r=" + PROBE_JS + ";const s=document.createElement('script');s.id='__dto_style_probe__';s.type='application/json';s.textContent=JSON.stringify(r);document.body.appendChild(s);})();"
    inj = src.replace("</body>", f"<script>window.addEventListener('load',function(){{{js}}});</script></body>") if "</body>" in src else src + f"<script>{js}</script>"
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=str(Path(path).parent), delete=False, encoding="utf-8") as t:
        t.write(inj)
        tp = Path(t.name)
    try:
        p = subprocess.run([chrome, "--headless=new", "--disable-gpu", f"--window-size={width},{height}", "--virtual-time-budget=3000", "--dump-dom", f"file://{tp.resolve()}"],
                           capture_output=True, text=True, timeout=25)
        m = re.search(r'<script id="__dto_style_probe__" type="application/json">(.*?)</script>', p.stdout, re.S)
        if not m:
            return {"error": "读取探针结果失败"}
        d = json.loads(html.unescape(m.group(1)))
        d["url"] = str(path)
        return d
    finally:
        tp.unlink(missing_ok=True)


def audit(pages, spec, tol):
    issues = []
    off_color, off_radius, off_font = defaultdict(list), defaultdict(list), defaultdict(list)
    all_colors = Counter()
    sig_vals = defaultdict(lambda: defaultdict(Counter))
    for pg in pages:
        name = os.path.basename(pg["url"]) or pg["url"]
        for e in pg["elements"]:
            for prop in ("color", "bg", "border"):
                c = parse_color(e.get(prop))
                if not c or c[3] == 0:
                    continue
                key = f"rgba({int(c[0])},{int(c[1])},{int(c[2])},{round(c[3], 2)})"
                all_colors[key] += 1
                if spec and min((dist(c, p) for p in spec["colors"]), default=999) > tol and not same_hue_shade(c, spec["colors"]):
                    off_color[key].append(f"{name}:{e['sel']}({prop})")
            for prop in ("gradient", "shadow"):
                for token in re.findall(r"rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b", e.get(prop) or ""):
                    c = parse_color(token)
                    if not c or c[3] == 0:
                        continue
                    neutral = max(c[:3]) - min(c[:3]) <= 12
                    if neutral and c[3] < 1:
                        continue  # 黑白半透明的高光和投影是材质，不算另造颜色
                    key = f"rgba({int(c[0])},{int(c[1])},{int(c[2])},{round(c[3], 2)})"
                    all_colors[key] += 1
                    if spec and min((dist((*c[:3], 1.0), (*p[:3], 1.0)) for p in spec["colors"]), default=999) > tol and not same_hue_shade(c, spec["colors"]):
                        off_color[key].append(f"{name}:{e['sel']}({prop})")
            r = e.get("radius") or "0px"
            if r.endswith("px"):
                rv = round(float(r[:-2]))
                is_pill = rv * 2 >= e.get("h", 0) - 1 and rv > 0
                if spec and not is_pill and rv not in spec["radii"] and all(abs(rv - x) > 1 for x in spec["radii"]):
                    off_radius[f"{rv}px"].append(f"{name}:{e['sel']}")
            if e.get("font"):
                first = next((f.strip().strip('"\'').lower() for f in e["font"].split(",") if f.strip().strip('"\'').lower() not in GENERIC_FONTS), None)
                if spec and first and first not in spec["fonts"]:
                    off_font[first].append(f"{name}:{e['sel']}")
            if e.get("sig"):
                s = e["sig"]
                sig_vals[s][name]["radius=" + (e.get("radius") or "")] += 1
                if e.get("size"):
                    sig_vals[s][name]["size=" + e["size"]] += 1
                if e.get("font"):
                    sig_vals[s][name]["font=" + e["font"].split(",")[0].strip().strip('"\'')] += 1
                if s in ("button", "card", "tag") and e.get("bg"):
                    sig_vals[s][name]["bg=" + e["bg"]] += 1

    for k, where in sorted(off_color.items(), key=lambda kv: -len(kv[1])):
        issues.append({"code": "OFF_TOKEN_COLOR", "severity": "FAIL", "value": k, "count": len(where), "examples": where[:4]})
    for k, where in sorted(off_radius.items(), key=lambda kv: -len(kv[1])):
        issues.append({"code": "OFF_SCALE_RADIUS", "severity": "FAIL", "value": k, "count": len(where), "examples": where[:4]})
    for k, where in sorted(off_font.items(), key=lambda kv: -len(kv[1])):
        issues.append({"code": "OFF_TOKEN_FONT", "severity": "FAIL", "value": k, "count": len(where), "examples": where[:4]})

    if len(pages) > 1:
        for sig, per_page in sig_vals.items():
            if len(per_page) < 2:
                continue
            for dim in ("radius", "size", "font", "bg"):
                dominant = {}
                for pg, cnt in per_page.items():
                    vals = [(v, n) for v, n in cnt.items() if v.startswith(dim + "=")]
                    if vals:
                        dominant[pg] = max(vals, key=lambda x: x[1])[0].split("=", 1)[1]
                if len(set(dominant.values())) > 1:
                    issues.append({"code": "CROSS_PAGE_DRIFT", "severity": "FAIL", "component": sig, "property": dim, "per_page": dominant})

    if not spec and len(all_colors) > 24:
        issues.append({"code": "PALETTE_SPRAWL", "severity": "WARN", "count": len(all_colors),
                       "message": "全站去重颜色超过 24 个，多半有写死的色值没有收进 Token。"})
    return issues


def main():
    ap = argparse.ArgumentParser(description="跨页风格一致性检查")
    ap.add_argument("pages", nargs="*", help="本地 HTML 文件")
    ap.add_argument("--preset", help="所选预设 ID（apple-native / INT-02 / modern-minimal ...）")
    ap.add_argument("--from-json", action="append", default=[], help="浏览器里执行探针得到的 JSON 文件")
    ap.add_argument("--probe-js", action="store_true", help="打印探针脚本后退出")
    ap.add_argument("--tolerance", type=float, default=14.0, help="颜色允许误差（RGB 距离）")
    ap.add_argument("--width", type=int, default=1440)
    ap.add_argument("--height", type=int, default=900)
    a = ap.parse_args()
    if a.probe_js:
        print(PROBE_JS)
        return
    pages = []
    for p in a.pages:
        r = run_page(p, a.width, a.height)
        if "error" in r:
            sys.exit(f"{p}: {r['error']}")
        pages.append(r)
    for j in a.from_json:
        pages.append(json.load(open(j, encoding="utf-8")))
    if not pages:
        sys.exit("至少给一个页面。")
    spec = preset_spec(a.preset) if a.preset else None
    issues = audit(pages, spec, a.tolerance)
    report = {"preset": spec["id"] if spec else None, "pages": [p["url"] for p in pages],
              "passed": all(i["severity"] != "FAIL" for i in issues), "issue_count": len(issues), "issues": issues}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
