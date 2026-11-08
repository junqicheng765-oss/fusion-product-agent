#!/usr/bin/env python3
"""Style Preset Registry 工具：列出、查看、导出、批量应用风格预设。

用法：
  python3 style_preset.py list [--family minimal-saas]
  python3 style_preset.py show <preset-id> [--json]
  python3 style_preset.py export <preset-id> --format css|shadcn|tailwind4|antd [-o 输出文件]
  python3 style_preset.py apply <preset-id> --css <项目里的全局 CSS 文件> [--mode light|dark|both]

preset-id 可以是：系统预设（apple-native / material-3 / ant-design）、V0 编号（INT-02、GAME-09）、
Tweakcn 主题名（modern-minimal、claude ...）。
apply 只改写 CSS 文件里 /* dto-style:start */ 与 /* dto-style:end */ 之间的内容，可重复执行。
"""
import argparse, copy, json, math, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "style-presets")
START, END = "/* dto-style:start */", "/* dto-style:end */"
ANTD_SEMANTIC_MAP = {
    "primary": "colorPrimary", "destructive": "colorError", "background": "colorBgLayout",
    "card": "colorBgContainer", "foreground": "colorText", "muted-foreground": "colorTextSecondary",
    "border": "colorBorder",
}


def registry():
    with open(os.path.join(ROOT, "registry.json"), encoding="utf-8") as handle:
        return json.load(handle)


def resolve(pid):
    reg = registry()
    p = reg["presets"]
    for group in ("systems", "dto", "tweakcn"):
        for item in p[group]:
            if item["id"].lower() == pid.lower():
                with open(os.path.join(ROOT, item["file"]), encoding="utf-8") as handle:
                    return group, item, json.load(handle)
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


def effective_auxiliary_colors(data):
    """Only explicit application color contracts extend cssVars, never arbitrary metadata."""
    meta = data.get("meta", {}).get("dto", {})
    result = {}

    def leaves(value, prefix):
        if isinstance(value, dict):
            for key, item in value.items():
                leaves(item, prefix + "." + str(key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                leaves(item, prefix + "." + str(index))
        elif isinstance(value, str):
            result[prefix] = value

    # Existing Apple semantic colors are explicit platform application values.
    leaves(meta.get("platformColors", {}), "platformColors")
    # A task/preset can explicitly declare additional application colors here.
    leaves(meta.get("effectiveAuxiliaryColors", {}), "effectiveAuxiliaryColors")
    # Native Ant Design status tokens remain valid; algorithm seed/base colors do not
    # turn every documented color into an allowed rendered value.
    native = meta.get("antdToken", {})
    for key in ("colorSuccess", "colorWarning", "colorInfo"):
        if isinstance(native.get(key), str):
            result["antdToken." + key] = native[key]
    return result


def antd_semantic_values(light):
    """The existing AntD exporter supports these non-rgba light semantic colors."""
    return {target: oklch_to_hex(light[source]) for source, target in ANTD_SEMANTIC_MAP.items()
            if light.get(source) and not str(light[source]).startswith("rgba")}


def antd_export_contract(data):
    _, light, _ = theme_vars(data)
    native = data.get("meta", {}).get("dto", {}).get("antdToken", {})
    supported = antd_semantic_values(light)
    mapped = {source: target for source, target in ANTD_SEMANTIC_MAP.items()
              if target in supported and (not native or target in native)}
    return {
        "source": "meta.dto.antdToken + supported cssVars.light overrides" if native else "cssVars.light semantic mapping",
        "mode": "light",
        "mapping_boundary": "existing native semantic color keys only" if native else "supported semantic color keys only",
        "propagated_semantic_tokens": mapped,
        "not_propagated_semantic_tokens": sorted(set(light) - set(mapped)),
        "native_token_defaults_preserved": bool(native),
        "limits": "This exporter does not execute a native theme algorithm or promise that unmapped CSS values/modes are applied. Verify native platform rendering separately.",
    }


def palette_contract(data):
    """Separate actual semantic tokens from the historical design/reference palette."""
    theme, light, dark = theme_vars(data)
    meta = data.get("meta", {}).get("dto", {})
    reference_key = "sourcePalette" if "sourcePalette" in meta else "palette"
    reference = copy.deepcopy(meta.get(reference_key, {}))
    differences = []
    mappings = (("bg", "background"), ("card", "card"), ("primary", "primary"))
    for mode, values in (("light", light), ("dark", dark)):
        for field, token in mappings:
            old, effective = reference.get(field), values.get(token)
            if old is not None and effective is not None and old != effective:
                differences.append({"mode": mode, "token": token,
                                    "reference_field": field, "reference": old,
                                    "effective": effective})
        for index, token in enumerate(("foreground", "muted-foreground")):
            old = reference.get("text", [])
            if isinstance(old, list) and len(old) > index and token in values and old[index] != values[token]:
                differences.append({"mode": mode, "token": token,
                                    "reference_field": "text." + str(index),
                                    "reference": old[index], "effective": values[token]})
    return {
        "application_source": "cssVars",
        "application_scope": "CSS semantic output and DTO-derived semantic exports; native exports follow platform_export_contracts, not blanket CSS propagation.",
        "theme": theme,
        "modes": {mode: values for mode, values in (("light", light), ("dark", dark)) if values},
        "declared_design_modes": meta.get("modes", []),
        "reference_palette": {"source": "meta.dto." + reference_key,
                              "role": "reference-only", "values": reference},
        "reference_differences": differences,
        "effective_auxiliary_colors": effective_auxiliary_colors(data),
        "platform_export_contracts": {"antd": antd_export_contract(data)},
        "limits": "Values are reported as stored; differences do not establish why an adaptation was made, visual quality, contrast or approval.",
    }


def to_shadcn(data):
    exported = copy.deepcopy(data)
    contract = palette_contract(data)
    exported.setdefault("meta", {})["presetContract"] = {
        "applicationSource": contract["application_source"],
        "applicationScope": contract["application_scope"],
        "referencePaletteSource": contract["reference_palette"]["source"],
        "referencePaletteRole": "reference-only",
        "referenceDifferences": contract["reference_differences"],
        "platformExportContracts": contract["platform_export_contracts"],
    }
    return json.dumps(exported, ensure_ascii=False, indent=2)


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
    theme, light, _ = theme_vars(data)
    token = {k: v for k, v in {
        **antd_semantic_values(light), "borderRadius": radius_px(theme.get("radius")),
        "fontFamily": theme.get("font-sans"),
    }.items() if v and not str(v).startswith("rgba")}
    if meta.get("antdToken"):
        native = copy.deepcopy(meta["antdToken"])
        # Keep platform-specific settings/defaults, but an existing semantic color
        # cannot disagree with the effective cssVars value used by other exporters.
        for key, value in token.items():
            if key in native and key.startswith("color") and str(native[key]).lower() != str(value).lower():
                native[key] = value
        token = native
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


def related_resources(group, item):
    """Expose catalogue connections without claiming they were adopted or fit a task."""
    reg = registry()
    family_ids = set(item.get("family", []))
    families = [f for f in reg.get("families", [])
                if f.get("id") in family_ids or item["id"] in f.get(group, [])]
    linked_ids = {rid for family in families
                  for key in ("systems", "layout", "motion")
                  for rid in family.get(key, [])}
    libraries = {}
    for category, entries in reg.get("libraries", {}).items():
        if isinstance(entries, list):
            selected = [entry for entry in entries
                        if entry.get("id") in linked_ids
                        or linked_ids.intersection(entry.get("presetIds", []))]
            if selected:
                libraries[category] = copy.deepcopy(selected)
    return {
        "source": "style-presets/registry.json",
        "families": copy.deepcopy(families),
        "libraries": libraries,
        "limits": "Related discovery routes only: not task suitability, adoption, installation or visual completion. Recipe tags lead to component-recipes/registry.json; motion IDs lead to methods-motion.md. Select resources by the current task, including other families when appropriate.",
    }


def cmd_show(a):
    group, item, data = resolve(a.id)
    theme, light, dark = theme_vars(data)
    meta = data.get("meta", {}).get("dto", {})
    contract = palette_contract(data)
    resources = related_resources(group, item)
    if getattr(a, "json", False):
        print(json.dumps({"id": item["id"], "group": group, "title": data.get("title", ""),
                          **contract,
                          "registry_entry": copy.deepcopy(item),
                          "related_resources": resources,
                          "design_spec": {
                              "source": "meta.dto",
                              "role": "stored-design-guidance",
                              "values": copy.deepcopy({k: v for k, v in meta.items()
                                                       if k not in ("palette", "sourcePalette")}),
                              "limits": "Stored design guidance is not automatically applied or verified. Embedded color literals and prompt snippets do not override effective CSS/DTO colors in theme/modes; native exports follow platform_export_contracts. Missing rules remain unspecified.",
                          }}, ensure_ascii=False, indent=2))
        return
    print(f"{item['id']}（{group}）{data.get('title', '')}")
    print("CSS/DTO 生效语义色来源: cssVars.<mode>；meta.dto.palette/sourcePalette 仅供设计追溯，不覆盖语义值。")
    print("字体:", theme.get("font-sans"), "| 圆角:", theme.get("radius"))
    for mode, values in contract["modes"].items():
        print(f"[{mode}]（实际存储的语义值，不表示已验证该模式设计）")
        for k in ("background", "card", "foreground", "muted-foreground", "primary", "border"):
            if k in values:
                print(f"  {k:18} {values[k]}  ->  {oklch_to_hex(values[k])}")
    if contract["reference_differences"]:
        print("参考色板与实际语义值的差异（原因未据此推定）:")
        for row in contract["reference_differences"]:
            print(f"  {row['mode']}.{row['token']}: reference={row['reference']} -> effective={row['effective']}")
    native_contract = contract["platform_export_contracts"]["antd"]
    print("AntD 导出边界:", json.dumps(native_contract, ensure_ascii=False))
    for k in ("displayName", "scenes", "typeScale", "spacing", "radiusScale", "components", "motion", "implementation", "installables", "license"):
        if meta.get(k):
            print(f"{k}: {json.dumps(meta[k], ensure_ascii=False)}")
    print("关联资源入口（不代表已采用或适合本轮任务）:")
    for family in resources["families"]:
        print(f"  [{family['id']}] {family.get('name', '')} — {family.get('scenes', '')}")
        print(f"    系统: {', '.join(family.get('systems', [])) or '-'} | 配方标签: {', '.join(family.get('recipes', [])) or '-'} | 区块: {', '.join(family.get('layout', [])) or '-'} | 动效: {', '.join(family.get('motion', [])) or '-'}")
        if family.get("layoutNote"):
            print("   ", family["layoutNote"])
    for category, entries in resources["libraries"].items():
        for library in entries:
            print(f"  {category}: {json.dumps(library, ensure_ascii=False)}")
    if group == "tweakcn":
        print("安装:", item["install"], "| 许可: Apache-2.0")


def cmd_export(a):
    _, _, data = resolve(a.id)
    fmt = {"css": to_css, "tailwind4": to_tailwind4, "antd": to_antd,
           "shadcn": to_shadcn}[a.format]
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
    s = sp.add_parser("show"); s.add_argument("id"); s.add_argument("--json", action="store_true", help="输出生效语义值、参考色板与差异；应用/提示词使用 modes 而非参考色板"); s.set_defaults(f=cmd_show)
    e = sp.add_parser("export"); e.add_argument("id"); e.add_argument("--format", required=True, choices=["css", "shadcn", "tailwind4", "antd"]); e.add_argument("-o"); e.set_defaults(f=cmd_export)
    ap = sp.add_parser("apply"); ap.add_argument("id"); ap.add_argument("--css", required=True); ap.add_argument("--mode", default="both", choices=["light", "dark", "both"]); ap.set_defaults(f=cmd_apply)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
