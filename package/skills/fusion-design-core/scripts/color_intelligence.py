#!/usr/bin/env python3
"""Color Intelligence：产品级语义色的检索、生成、验收与应用。

用法：
  python3 color_intelligence.py list
  python3 color_intelligence.py show apple-minimal
  python3 color_intelligence.py from-brand 1677FF
  python3 color_intelligence.py from-palette F5F0E8,191918,CC785C,5C5852,E6DEC8
  python3 color_intelligence.py contrast --preset apple-minimal
  python3 color_intelligence.py preview apple-minimal,warm-editorial,ai-gradient -o /tmp/color-preview.html
  python3 color_intelligence.py apply nature-calm --css app/globals.css

不调用 Coolors / Color Hunt / Huemint API，也不抓取这些站点。
用户粘贴的 hex 或分享链接里的 hex，用 from-palette 转成语义色。
"""
import argparse, colorsys, json, math, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "color-presets")
START, END = "/* dto-color:start */", "/* dto-color:end */"
DARK_TEXT = {"sky", "mint", "lime", "yellow", "amber"}
NEUTRALS = ["gray", "slate", "mauve", "sage", "olive", "sand"]
ACCENTS = ["blue", "indigo", "violet", "iris", "purple", "plum", "pink", "crimson",
           "ruby", "red", "tomato", "orange", "amber", "yellow", "lime", "green",
           "grass", "teal", "jade", "cyan", "sky", "mint", "brown", "bronze", "gold"]


def registry():
    return json.load(open(os.path.join(ROOT, "registry.json"), encoding="utf-8"))


def scales():
    return json.load(open(os.path.join(ROOT, "radix/scales.json"), encoding="utf-8"))


def load_system(pid):
    path = os.path.join(ROOT, "systems", pid + ".json")
    if not os.path.exists(path):
        sys.exit(f"找不到配色系统 {pid}。可用：{', '.join(p['id'] for p in registry()['systems'])}")
    return json.load(open(path, encoding="utf-8"))


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def parse_hex_list(s):
    return ["#" + x.strip().lstrip("#") for x in re.split(r"[,|\s]+", s) if x.strip()]


def rel_lum(rgb):
    def f(x):
        x = x / 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    L1, L2 = sorted((rel_lum(hex_to_rgb(a) if isinstance(a, str) else a),
                     rel_lum(hex_to_rgb(b) if isinstance(b, str) else b)), reverse=True)
    return (L1 + 0.05) / (L2 + 0.05)


def hue_of(h):
    r, g, b = [c / 255 for c in hex_to_rgb(h)]
    return colorsys.rgb_to_hls(r, g, b)[0]


def dist_hex(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(hex_to_rgb(a), hex_to_rgb(b))))


def nearest_accent(hex_color):
    s = scales()
    best, name = 1e9, "blue"
    for n in ACCENTS:
        key = n
        if key not in s:
            continue
        d = dist_hex(hex_color, s[key][f"{n}9"])
        if d < best:
            best, name = d, n
    return name, best


def nearest_neutral(hex_color):
    s = scales()
    best, name = 1e9, "slate"
    for n in NEUTRALS:
        d = dist_hex(hex_color, s[n][f"{n}2"])
        if d < best:
            best, name = d, n
    return name


def pick_neutral_for_accent(accent):
    warm = {"orange", "amber", "yellow", "brown", "bronze", "gold", "tomato"}
    greenish = {"green", "grass", "teal", "jade", "mint", "lime"}
    if accent in warm:
        return "sand"
    if accent in greenish:
        return "sage"
    if accent in {"purple", "plum", "violet", "pink", "crimson"}:
        return "mauve"
    return "slate"


def step_of(name, i, dark=False):
    key = name + ("Dark" if dark else "")
    return scales()[key][f"{name}{i}"]


def solid_pair(*hexes):
    """Radix step 9 follows APCA. Filled buttons here must pass WCAG 4.5:1."""
    white, ink = "#ffffff", "#1c2024"
    for bg in hexes:
        if not bg:
            continue
        if contrast(white, bg) >= 4.5:
            return bg, white
        if contrast(ink, bg) >= 4.5:
            return bg, ink
    return hexes[0], white


def build_semantic(neutral, accent, primary=None):
    def side(dark):
        n = lambda i: step_of(neutral, i, dark)
        a = lambda i: step_of(accent, i, dark)
        d = lambda i: step_of("red", i, dark)
        g = lambda i: step_of("green", i, dark)
        w = lambda i: step_of("amber", i, dark)
        p, pfg = solid_pair(primary if primary and not dark else None, a(11), a(10), a(9), a(12))
        dest, dest_fg = solid_pair(d(11), d(10), d(9), d(12))
        suc, suc_fg = solid_pair(g(11), g(10), g(9), g(12))
        warn, warn_fg = solid_pair(w(11), w(10), w(9), w(12))
        return {
            "background": n(1), "foreground": n(12),
            "card": n(2) if dark else "#ffffff", "card-foreground": n(12),
            "popover": n(2) if dark else "#ffffff", "popover-foreground": n(12),
            "primary": p, "primary-foreground": pfg,
            "tint": primary or a(9),
            "secondary": n(3), "secondary-foreground": n(12),
            "muted": n(3), "muted-foreground": n(11),
            "accent": a(4), "accent-foreground": a(11),
            "destructive": dest, "destructive-foreground": dest_fg,
            "success": suc, "success-foreground": suc_fg,
            "warning": warn, "warning-foreground": warn_fg,
            "border": n(6), "input": n(7), "ring": a(8),
        }
    return {"neutral": neutral, "accent": accent, "light": side(False), "dark": side(True)}


def oklch_scale_from_hex(h):
    """When brand color is far from every Radix accent, build a 12-step scale in HLS."""
    r, g, b = [c / 255 for c in hex_to_rgb(h)]
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    lights = [0.98, 0.96, 0.93, 0.89, 0.84, 0.78, 0.68, 0.56, ll, max(0.08, ll - 0.06), 0.32, 0.14]
    sats = [0.08, 0.10, 0.14, 0.18, 0.22, 0.28, 0.36, 0.45, ss, ss, 0.40, 0.28]
    out = {}
    for i, (L, S) in enumerate(zip(lights, sats), 1):
        rgb = colorsys.hls_to_rgb(hh, max(0.04, min(0.98, L)), max(0.04, min(0.95, S)))
        out[i] = rgb_to_hex([c * 255 for c in rgb])
    return out


def pairs_of(tokens):
    pairs = [
        ("正文 / 页面底", tokens["foreground"], tokens["background"], 4.5),
        ("次级文字 / 页面底", tokens["muted-foreground"], tokens["background"], 4.5),
        ("主按钮文字 / 主按钮", tokens["primary-foreground"], tokens["primary"], 4.5),
    ]
    if "success" in tokens:
        pairs.append(("成功按钮文字 / 成功色", tokens.get("success-foreground", "#fff"), tokens["success"], 4.5))
    if "warning" in tokens:
        pairs.append(("警告文字 / 警告色", tokens.get("warning-foreground", "#1c2024"), tokens["warning"], 4.5))
    pairs += [
        ("危险按钮文字 / 危险色", tokens["destructive-foreground"], tokens["destructive"], 4.5),
        ("正文 / 卡片", tokens["card-foreground"], tokens["card"], 4.5),
    ]
    return pairs


def check_tokens(tokens, aaa=False):
    rows = []
    ok = True
    for name, fg, bg, th in pairs_of(tokens):
        ratio = contrast(fg, bg)
        need = 7.0 if aaa else th
        passed = ratio >= need
        ok = ok and passed
        rows.append({"pair": name, "fg": fg, "bg": bg, "ratio": round(ratio, 2),
                     "need": need, "result": "PASS" if passed else "FAIL"})
    if "primary" in tokens and "primary-foreground" in tokens:
        fg, bg = tokens["primary-foreground"], tokens["primary"]
        _r, _g, _b = [c / 255 for c in hex_to_rgb(bg)]
        _h, _l, sat = colorsys.rgb_to_hls(_r, _g, _b)
        bg_lum = rel_lum(hex_to_rgb(bg))
        text_is_darker = rel_lum(hex_to_rgb(fg)) < bg_lum
        # High-luminance accents (yellow, gold, amber, lime, cyan: bg_lum >= 0.35) naturally pair with dark text.
        # Mid/dark saturated accents (red, blue, orange, green, purple: bg_lum < 0.35) must pair with light text;
        # if contrast is below 4.5, deepen the button background instead of flipping the text to black.
        if sat >= 0.45 and bg_lum < 0.35 and text_is_darker:
            ok = False
            rows.append({
                "pair": "主按钮深字贴在高饱和底上",
                "fg": fg, "bg": bg, "ratio": round(contrast(fg, bg), 2),
                "need": 4.5, "result": "FAIL",
            })
    return ok, rows


def css_block(tokens, extra_theme=None):
    theme = extra_theme or {}
    root = {**theme, **tokens["light"]} if "light" in tokens else tokens
    lines = [":root {"]
    if "light" in tokens:
        for k, v in {**theme, **tokens["light"]}.items():
            lines.append(f"  --{k}: {v};")
        lines.append("}")
        lines.append(".dark {")
        for k, v in tokens["dark"].items():
            lines.append(f"  --{k}: {v};")
        lines.append("}")
    else:
        for k, v in root.items():
            lines.append(f"  --{k}: {v};")
        lines.append("}")
    return "\n".join(lines) + "\n"


def cmd_list(_):
    reg = registry()
    print("产品级语义色（本地，可直接应用）")
    for s in reg["systems"]:
        print(f"  {s['id']:16} {s['title']} — {s['display']}")
        print(f"                   场景: {', '.join(s['scenes'])} | 风格族: {', '.join(s['family'])}")
    print("\n色库（先看 auto 字段）")
    for lib in reg["libraries"]:
        flag = "可自动化" if lib["auto"] else "只作灵感，不抓取"
        print(f"  {lib['id']:16} [{lib['tier']}] {flag}  {lib['url']}")


def cmd_show(a):
    data = load_system(a.id)
    meta = data["meta"]["color"]
    print(f"{meta['id']}  {data['title']} — {meta['displayName']}")
    print(meta["note"])
    print("中性色阶:", meta["neutral"], "| 主色色阶:", meta["accent"], "| 默认模式:", meta["defaultMode"])
    print("Radix 台阶:", meta["radixSteps"])
    L = data["cssVars"]["light"]
    for k in ("background", "foreground", "card", "muted-foreground", "primary", "border", "destructive", "success"):
        print(f"  {k:20} {L[k]}")
    ok, rows = check_tokens(L)
    print("对比度:", "通过" if ok else "未通过")
    for r in rows:
        print(f"  {r['result']:4} {r['ratio']:5}  {r['pair']}  {r['fg']} / {r['bg']}")


def cmd_from_brand(a):
    hx = "#" + a.hex.lstrip("#")
    accent, d = nearest_accent(hx)
    neutral = a.neutral or pick_neutral_for_accent(accent)
    if d > 48:
        print(f"品牌色 {hx} 离最近的 Radix 主色（{accent}）较远（距离 {d:.0f}），主色用品牌色本身，色阶用本地插值；中性色仍用 Radix {neutral}。")
        tokens = build_semantic(neutral, accent, primary=hx)
        tokens["light"]["primary"] = hx
        custom = oklch_scale_from_hex(hx)
        tokens["light"]["accent"] = custom[4]
        tokens["light"]["ring"] = custom[8]
        tokens["source"] = "brand-hex + local scale + radix-neutral"
    else:
        tokens = build_semantic(neutral, accent, primary=hx)
        tokens["light"]["primary"] = hx
        tokens["source"] = f"radix {neutral}+{accent}, primary override {hx}"
    tokens["brand"] = hx
    print(json.dumps({k: tokens[k] for k in ("source", "brand", "neutral", "accent", "light", "dark")}, ensure_ascii=False, indent=2))
    ok, rows = check_tokens(tokens["light"])
    print("浅色对比度:", "通过" if ok else "未通过")
    for r in rows:
        print(f"  {r['result']:4} {r['ratio']:5}  {r['pair']}")


def cmd_from_palette(a):
    colors = parse_hex_list(a.hexes)
    if len(colors) < 3:
        sys.exit("至少 3 个 hex：背景、文字、主色。Coolors 一般是 5 个，Color Hunt 一般是 4 个。")
    bg, fg, primary = colors[0], colors[1], colors[2]
    # 若第一个太深、第二个太浅，对调（用户有时按主色在前的顺序贴）
    if rel_lum(hex_to_rgb(bg)) < rel_lum(hex_to_rgb(fg)) and rel_lum(hex_to_rgb(bg)) < 0.4:
        bg, fg = fg, bg
    accent, _ = nearest_accent(primary)
    neutral = nearest_neutral(bg)
    tokens = build_semantic(neutral, accent, primary=primary)
    tokens["light"]["background"] = bg
    tokens["light"]["foreground"] = fg
    tokens["light"]["tint"] = primary
    p, pfg = solid_pair(primary, tokens["light"]["primary"])
    tokens["light"]["primary"], tokens["light"]["primary-foreground"] = p, pfg
    tokens["light"]["card-foreground"] = fg
    tokens["light"]["popover-foreground"] = fg
    if len(colors) > 3:
        tokens["light"]["muted-foreground"] = colors[3]
    if len(colors) > 4:
        tokens["light"]["border"] = colors[4]
    tokens["source"] = "user-pasted palette (inspiration site, not scraped)"
    tokens["palette"] = colors
    print(json.dumps({k: tokens[k] for k in tokens if k in ("source", "palette", "neutral", "accent", "light", "dark")},
                     ensure_ascii=False, indent=2))
    ok, rows = check_tokens(tokens["light"])
    print("浅色对比度:", "通过" if ok else "未通过")
    for r in rows:
        print(f"  {r['result']:4} {r['ratio']:5}  {r['pair']}")
    if not ok:
        print("未通过的组合必须改到阈值以上，才能写入产品。不要为了好看牺牲正文对比。")


STYLE_ROOT = os.path.join(os.path.dirname(ROOT), "style-presets")


def load_style_preset(pid):
    """风格预设（INT-05、GAME-09、CN-02、Tweakcn 主题等）也能直接做对比度检查。"""
    import glob
    want = pid.strip().lower()
    for path in sorted(glob.glob(os.path.join(STYLE_ROOT, "**", "*.json"), recursive=True)):
        if os.path.basename(path) == "registry.json":
            continue
        try:
            data = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        dto = (data.get("meta") or {}).get("dto") or {}
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        if want in {str(dto.get("id", "")).lower(), stem, str(data.get("name", "")).lower()} or stem.startswith(want + "-"):
            css = data.get("cssVars") or {}
            base = dict(css.get("theme") or {})
            modes = dto.get("modes") or ["light", "dark"]
            packs = []
            for mode in ("light", "dark"):
                if mode in modes and css.get(mode):
                    packs.append((mode, {**base, **css[mode]}))
            return packs
    return None


def tokens_from_css(path):
    text = open(path, encoding="utf-8").read()
    tokens = {}
    for block in re.findall(r":root\s*\{([^}]*)\}", text):
        for name, value in re.findall(r"--([\w-]+)\s*:\s*([^;]+);", block):
            value = value.strip()
            if re.fullmatch(r"#[0-9a-fA-F]{3,8}", value):
                tokens[name] = value
    return tokens


def cmd_contrast(a):
    if a.css:
        tokens = tokens_from_css(a.css)
        missing = [k for k in ("foreground", "background", "muted-foreground", "primary", "primary-foreground",
                               "destructive", "destructive-foreground", "card", "card-foreground") if k not in tokens]
        if missing:
            sys.exit(f"{a.css} 的 :root 里缺这些十六进制变量：{', '.join(missing)}")
        packs = [("page", tokens)]
    elif a.preset:
        system = os.path.join(ROOT, "systems", a.preset + ".json")
        if os.path.exists(system):
            data = load_system(a.preset)
            packs = [("light", data["cssVars"]["light"]), ("dark", data["cssVars"]["dark"])]
        else:
            packs = load_style_preset(a.preset)
            if not packs:
                sys.exit(f"找不到 {a.preset}。可用配色系统：{', '.join(p['id'] for p in registry()['systems'])}；"
                         "风格预设用编号，例如 INT-05、GAME-09、CN-02。")
    else:
        sys.exit("请用 --preset <配色系统或风格预设编号>，或 --css <页面实际使用的 CSS 文件>")
    all_ok = True
    for mode, tokens in packs:
        ok, rows = check_tokens(tokens, aaa=a.aaa)
        all_ok = all_ok and ok
        print(f"[{mode}] {'通过' if ok else '未通过'}")
        for r in rows:
            note = "（只够 24px 以上或 19px 粗体的大字）" if r["result"] == "FAIL" and r["ratio"] >= 3.0 and not r["pair"].startswith("主按钮深字") else ""
            extra = ""
        if r["pair"].startswith("主按钮深字"):
            extra = "  把按钮底在同一色相里加深，直到浅色字达到 4.5:1。不要改成黑字。"
        print(f"  {r['result']:4} {r['ratio']:5}  需要 ≥{r['need']}  {r['pair']}  {r['fg']} / {r['bg']}{note}{extra}")
    if not all_ok and a.preset and not a.css:
        print("预设本身有组合不达标：在页面里把这块底色在同一色相加深，直到浅色字达标。不要把主按钮改成深色字贴在高饱和底上。再用 --css <页面 CSS> 检查页面实际用的颜色。")
    sys.exit(0 if all_ok else 1)


def cmd_preview(a):
    ids = [x.strip() for x in a.ids.split(",") if x.strip()]
    if not (2 <= len(ids) <= 3):
        sys.exit("preview 需要 2–3 个系统 ID，用逗号分隔。")
    cols = []
    for i in ids:
        d = load_system(i)
        L = d["cssVars"]["light"]
        D = d["cssVars"]["dark"]
        meta = d["meta"]["color"]
        cols.append((i, d["title"], meta["displayName"], L, D))
    pal = "-".join(c[3]["background"].lstrip("#") + c[3]["foreground"].lstrip("#") + c[3]["primary"].lstrip("#") for c in cols[:1])
    # Realtime Colors uses 5 slots; give user one link per candidate
    links = []
    for i, title, _, L, _ in cols:
        colors = "-".join(L[k].lstrip("#") for k in ("background", "foreground", "primary", "secondary", "accent"))
        links.append((title, f"https://www.realtimecolors.com/?colors={colors}"))
    html = ["<!doctype html><html lang='zh'><head><meta charset='utf-8'><title>配色候选</title>",
            "<style>body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}",
            ".row{display:flex;min-height:100vh}.col{flex:1;padding:28px 24px;border-right:1px solid rgba(0,0,0,.06)}",
            "h2{margin:0 0 4px;font-size:20px}p.sub{margin:0 0 20px;opacity:.7;font-size:13px}",
            ".card{border-radius:12px;padding:16px 18px;margin:12px 0}",
            "button{border:0;border-radius:8px;padding:8px 14px;font:600 14px inherit;margin-right:8px}",
            ".ghost{background:transparent;border:1px solid currentColor}",
            ".alert{border-radius:8px;padding:10px 12px;margin-top:12px;font-size:13px}",
            "a{font-size:12px}</style></head><body><div class='row'>"]
    for i, title, display, L, D in cols:
        html.append(
            f"<section class='col' style='background:{L['background']};color:{L['foreground']}'>"
            f"<h2>{title}</h2><p class='sub'>{display}</p>"
            f"<div class='card' style='background:{L['card']};border:1px solid {L['border']}'>"
            f"<div style='font-size:13px;color:{L['muted-foreground']}'>次级说明</div>"
            f"<div style='font-size:18px;font-weight:650;margin:6px 0 12px'>卡片标题</div>"
            f"<button style='background:{L['primary']};color:{L['primary-foreground']}'>主行动</button>"
            f"<button class='ghost' style='color:{L['foreground']};border-color:{L['border']}'>次要</button>"
            f"<div class='alert' style='background:{L['destructive']};color:{L['destructive-foreground']}'>错误：请检查输入</div>"
            f"<div class='alert' style='background:{L['success']};color:{L['success-foreground']}'>成功：已保存</div>"
            f"</div>"
            f"<div class='card' style='background:{D['background']};color:{D['foreground']};border:1px solid {D['border']}'>"
            f"<div style='font-size:13px;opacity:.75'>暗色预览</div>"
            f"<button style='background:{D['primary']};color:{D['primary-foreground']};margin-top:10px'>主行动</button>"
            f"</div></section>"
        )
    html.append("</div><p style='padding:12px 24px;font-size:12px;color:#666'>本地预览。也可到 Realtime Colors 看整页：" +
                " · ".join(f"<a href='{u}'>{t}</a>" for t, u in links) + "</p></body></html>")
    out = a.o or "/tmp/color-preview.html"
    open(out, "w", encoding="utf-8").write("".join(html))
    print("已写入", out)
    print("Realtime Colors 链接（不抓取，只生成预览 URL）：")
    for t, u in links:
        print(f"  {t}: {u}")


def cmd_apply(a):
    data = load_system(a.id)
    css = f"{START}\n/* color-system: {a.id} */\n{css_block({'light': data['cssVars']['light'], 'dark': data['cssVars']['dark']})}{END}"
    src = open(a.css, encoding="utf-8").read() if os.path.exists(a.css) else ""
    if START in src and END in src:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: css, src, flags=re.S)
    else:
        new = src.rstrip() + "\n\n" + css + "\n"
    open(a.css, "w", encoding="utf-8").write(new)
    print(f"已把 {a.id} 的语义色写入 {a.css}。只改颜色变量，不改字体和圆角。接着跑 contrast 和 style_consistency_audit.py。")


def cmd_export(a):
    data = load_system(a.id)
    if a.format == "css":
        out = css_block({"light": data["cssVars"]["light"], "dark": data["cssVars"]["dark"]})
    else:
        out = json.dumps(data, ensure_ascii=False, indent=2)
    if a.o:
        open(a.o, "w", encoding="utf-8").write(out)
        print("已写入", a.o)
    else:
        print(out)


def main():
    p = argparse.ArgumentParser(description="Color Intelligence")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list").set_defaults(f=cmd_list)
    s = sp.add_parser("show"); s.add_argument("id"); s.set_defaults(f=cmd_show)
    b = sp.add_parser("from-brand"); b.add_argument("hex"); b.add_argument("--neutral"); b.set_defaults(f=cmd_from_brand)
    pal = sp.add_parser("from-palette"); pal.add_argument("hexes"); pal.set_defaults(f=cmd_from_palette)
    c = sp.add_parser("contrast"); c.add_argument("--preset"); c.add_argument("--css", help="页面实际引入的 CSS 文件，检查 :root 里的变量"); c.add_argument("--aaa", action="store_true"); c.set_defaults(f=cmd_contrast)
    pr = sp.add_parser("preview"); pr.add_argument("ids"); pr.add_argument("-o"); pr.set_defaults(f=cmd_preview)
    ap = sp.add_parser("apply"); ap.add_argument("id"); ap.add_argument("--css", required=True); ap.set_defaults(f=cmd_apply)
    e = sp.add_parser("export"); e.add_argument("id"); e.add_argument("--format", default="css", choices=["css", "shadcn"]); e.add_argument("-o"); e.set_defaults(f=cmd_export)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
