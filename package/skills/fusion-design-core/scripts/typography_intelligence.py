#!/usr/bin/env python3
"""按风格族、语言和密度选出标题 / 正文 / 等宽 / CJK 字体和字阶。

不调用需要 API key 的 Google Fonts 开发者接口。
加载字体用公开的 CSS2 URL（fonts/catalog.json）。
"""
import argparse, json, os, sys
CAT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resource-adapters", "fonts", "catalog.json")


def catalog():
    return json.load(open(CAT, encoding="utf-8"))


def needs_cjk(langs):
    return any(x in {"zh", "zh-hans", "zh-hant", "ja", "ko", "cjk"} for x in langs)


def pick(family, langs, density):
    cat = catalog()
    pair = cat["pairings"].get(family) or cat["pairings"]["minimal-saas"]
    scale = cat["scales"].get(density) or cat["scales"]["default"]
    fonts = cat["fonts"]
    roles = {
        "heading": pair["heading"],
        "body": pair["body"],
        "mono": pair["mono"],
        "cjk": pair["cjk"] if needs_cjk(langs) else None,
    }
    out = {"styleFamily": family, "langs": langs, "density": density, "scale": scale, "roles": {}, "cssLinks": [], "rules": cat["rules"]}
    seen = set()
    for role, key in roles.items():
        if not key:
            continue
        f = fonts[key]
        out["roles"][role] = {"id": key, **{k: f[k] for k in ("family", "weights", "subsets", "license") if k in f}}
        css = f.get("css")
        if css and css not in seen:
            seen.add(css)
            out["cssLinks"].append(css)
    if needs_cjk(langs):
        body_sub = set(fonts[pair["body"]].get("subsets") or [])
        if not body_sub & {"chinese-simplified", "chinese-traditional", "japanese", "korean"}:
            out["warning"] = "正文拉丁字体不含中日韩字形，必须同时加载 CJK 角色，并在 font-family 里把 CJK 栈接在后面。"
    return out


def as_css(result):
    lines = []
    for href in result["cssLinks"]:
        lines.append(f'@import url("{href}");')
    body = result["roles"]["body"]["family"]
    heading = result["roles"]["heading"]["family"]
    cjk = (result["roles"].get("cjk") or {}).get("family")
    stack = heading if not cjk or cjk in heading else f"{heading}, {cjk}"
    body_stack = body if not cjk or cjk in body else f"{body}, {cjk}"
    sc = result["scale"]
    lines += [
        ":root {",
        f"  --font-heading: {stack};",
        f"  --font-sans: {body_stack};",
        f"  --font-mono: {result['roles']['mono']['family']};",
        f"  --text-h1: {sc['h1'][0]}px;",
        f"  --leading-h1: {sc['h1'][1]}px;",
        f"  --weight-h1: {sc['h1'][2]};",
        f"  --text-body: {sc['body'][0]}px;",
        f"  --leading-body: {sc['body'][1]}px;",
        "}",
    ]
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["pick", "list"])
    p.add_argument("--family", default="minimal-saas")
    p.add_argument("--langs", default="en")
    p.add_argument("--density", default="default", choices=["compact", "default", "relaxed", "accessible"])
    p.add_argument("--css", action="store_true")
    a = p.parse_args()
    cat = catalog()
    if a.cmd == "list":
        print("风格族配对：")
        for k, v in cat["pairings"].items():
            print(f"  {k:16} heading={v['heading']} body={v['body']} cjk={v['cjk']}")
        return
    langs = [x.strip() for x in a.langs.split(",") if x.strip()]
    if a.family not in cat["pairings"]:
        sys.exit("未知风格族：" + ", ".join(cat["pairings"]))
    r = pick(a.family, langs, a.density)
    if a.css:
        print(as_css(r))
    else:
        print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
