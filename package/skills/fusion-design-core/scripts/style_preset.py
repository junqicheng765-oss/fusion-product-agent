#!/usr/bin/env python3
"""Style Preset Registry 工具：列出、查看、导出、批量应用风格预设。

用法：
  python3 style_preset.py list [--family minimal-saas]
  python3 style_preset.py show <preset-id>
  python3 style_preset.py export <preset-id> --format css|shadcn|tailwind4|antd [-o 输出文件]
  python3 style_preset.py apply <preset-id> --css <项目里的全局 CSS 文件> [--mode light|dark|both]

preset-id 可以是：系统预设（apple-native / material-3 / ant-design）、V0 编号（INT-02、GAME-09）、
Tweakcn 主题名（modern-minimal、claude ...）。
apply 只改写 CSS 文件里 /* dto-style:start */ 与 /* dto-style:end */ 之间的内容，可重复执行。
"""
import argparse, json, math, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "style-presets")
START, END = "/* dto-style:start */", "/* dto-style:end */"


def registry():
    return json.load(open(os.path.join(ROOT, "registry.json"), encoding="utf-8"))


def resolve(pid):
    reg = registry()
    p = reg["presets"]
    for group in ("systems", "dto", "tweakcn"):
        for item in p[group]:
            if item["id"].lower() == pid.lower():
                return group, item, json.load(open(os.path.join(ROOT, item["file"]), encoding="utf-8"))
    sys.exit(f"找不到预设 {pid}。先运行 list 查看可用 ID；本地没有时去线上库检索后再沉淀进 style-presets/。")


def oklch_to_hex(s):
    m = re.match(r"oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)", s)
    if not m:
        return s
    L = float(m.group(1).rstrip("%")) / (100 if m.group(1).endswith("%") else 1)
    C, H = float(m.group(2)), math.radians(float(m.group(3)))
    a, b = C * math.cos(H), C * math.sin(H)
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = [4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
           -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
           -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_]
    out = []
    for c in rgb:
        c = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        out.append(max(0, min(255, round(c * 255))))
    return "#%02x%02x%02x" % tuple(out)


def radius_px(r):
    if not r:
        return 8
    if r.endswith("rem"):
        return round(float(r[:-3]) * 16)
    if r.endswith("px"):
        return round(float(r[:-2]))
    return 8


def theme_vars(data):
    cv = data.get("cssVars", {})
    theme = dict(cv.get("theme", {}))
    light, dark = dict(cv.get("light", {})), dict(cv.get("dark", {}))
    for k in ("radius", "font-sans", "font-serif", "font-mono"):
        if k in light and k not in theme:
            theme[k] = light.pop(k)
        dark.pop(k, None)
    return theme, light, dark


def block(sel, d):
    return sel + " {\n" + "".join(f"  --{k}: {v};\n" for k, v in d.items()) + "}\n"


def to_css(data, mode="both"):
    theme, light, dark = theme_vars(data)
    root = {**theme, **(light if mode in ("both", "light") else dark)}
    css = block(":root", root)
    if mode == "both" and dark and dark != light:
        css += block(".dark", dark)
    return css


def to_tailwind4(data):
    keys = [k for k in theme_vars(data)[1].keys()]
    inline = {f"color-{k}": f"var(--{k})" for k in keys if not k.startswith("shadow")}
    inline.update({"font-sans": "var(--font-sans)", "radius-sm": "calc(var(--radius) - 4px)", "radius-md": "calc(var(--radius) - 2px)",
                   "radius-lg": "var(--radius)", "radius-xl": "calc(var(--radius) + 4px)"})
    return to_css(data) + "@theme inline {\n" + "".join(f"  --{k}: {v};\n" for k, v in inline.items()) + "}\n"


def to_antd(data):
    meta = data.get("meta", {}).get("dto", {})
    if meta.get("antdToken"):
        return json.dumps({"token": meta["antdToken"]}, ensure_ascii=False, indent=2)
    theme, light, _ = theme_vars(data)
    hx = lambda k: oklch_to_hex(light.get(k, "")) if light.get(k) else None
    token = {k: v for k, v in {
        "colorPrimary": hx("primary"), "colorError": hx("destructive"), "colorBgLayout": hx("background"),
        "colorBgContainer": hx("card"), "colorText": hx("foreground"), "colorTextSecondary": hx("muted-foreground"),
        "colorBorder": hx("border"), "borderRadius": radius_px(theme.get("radius")),
        "fontFamily": theme.get("font-sans"),
    }.items() if v and not str(v).startswith("rgba")}
    return json.dumps({"token": token}, ensure_ascii=False, indent=2)


def cmd_list(a):
    reg = registry()
    fams = reg["families"]
    if a.family:
        fams = [f for f in fams if f["id"] == a.family]
        if not fams:
            sys.exit("没有这个风格族。可用：" + ", ".join(f["id"] for f in reg["families"]))
    for f in fams:
        print(f"[{f['id']}] {f['name']} — {f['scenes']}")
        print(f"   系统预设: {', '.join(f['systems']) or '-'} | 内置风格: {', '.join(f['dto']) or '-'} | Tweakcn: {', '.join(f['tweakcn']) or '-'}")
        print(f"   通用组件配方: {', '.join(f.get('recipes', [])) or '-'}（python3 scripts/component_recipe.py list --tag <标签>）")
        print(f"   React 区块库: {', '.join(f['layout']) or '-'} | 动效库: {', '.join(f['motion']) or '-'}")
    if not a.family:
        print(f"\n共 {len(reg['presets']['systems'])} 个系统预设、{len(reg['presets']['dto'])} 个内置风格、{len(reg['presets']['tweakcn'])} 个 Tweakcn 主题。")


def cmd_show(a):
    group, item, data = resolve(a.id)
    theme, light, dark = theme_vars(data)
    meta = data.get("meta", {}).get("dto", {})
    print(f"{item['id']}（{group}）{data.get('title', '')}")
    print("字体:", theme.get("font-sans"), "| 圆角:", theme.get("radius"))
    for k in ("background", "card", "foreground", "muted-foreground", "primary", "border"):
        if k in light:
            print(f"  {k:18} {light[k]}  ->  {oklch_to_hex(light[k])}")
    for k in ("displayName", "scenes", "typeScale", "spacing", "radiusScale", "components", "motion", "implementation", "installables", "license"):
        if meta.get(k):
            print(f"{k}: {json.dumps(meta[k], ensure_ascii=False)}")
    if group == "tweakcn":
        print("安装:", item["install"], "| 许可: Apache-2.0")


def cmd_export(a):
    _, _, data = resolve(a.id)
    fmt = {"css": to_css, "tailwind4": to_tailwind4, "antd": to_antd,
           "shadcn": lambda d: json.dumps(d, ensure_ascii=False, indent=2)}[a.format]
    out = fmt(data)
    if a.o:
        open(a.o, "w", encoding="utf-8").write(out)
        print("已写入", a.o)
    else:
        print(out)


def cmd_apply(a):
    _, item, data = resolve(a.id)
    css = f"{START}\n/* preset: {item['id']} */\n{to_css(data, a.mode)}{END}"
    src = open(a.css, encoding="utf-8").read() if os.path.exists(a.css) else ""
    if START in src and END in src:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: css, src, flags=re.S)
    else:
        new = src.rstrip() + "\n\n" + css + "\n"
    open(a.css, "w", encoding="utf-8").write(new)
    print(f"已把 {item['id']} 写入 {a.css}。接着把页面里写死的颜色/圆角/字体替换成 var(--…)，再跑 style_consistency_audit.py。")


def main():
    p = argparse.ArgumentParser(description="Style Preset Registry 工具")
    sp = p.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("list"); l.add_argument("--family"); l.set_defaults(f=cmd_list)
    s = sp.add_parser("show"); s.add_argument("id"); s.set_defaults(f=cmd_show)
    e = sp.add_parser("export"); e.add_argument("id"); e.add_argument("--format", required=True, choices=["css", "shadcn", "tailwind4", "antd"]); e.add_argument("-o"); e.set_defaults(f=cmd_export)
    ap = sp.add_parser("apply"); ap.add_argument("id"); ap.add_argument("--css", required=True); ap.add_argument("--mode", default="both", choices=["light", "dark", "both"]); ap.set_defaults(f=cmd_apply)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
