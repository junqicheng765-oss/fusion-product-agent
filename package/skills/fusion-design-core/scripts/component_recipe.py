#!/usr/bin/env python3
"""通用组件配方库工具：查、拷、预览纯 HTML/CSS 组件配方。

配方在 component-recipes/recipes/<id>.html，只读风格预设写进 :root 的变量
（--background --foreground --primary --border --radius --font-sans ...），
所以任何技术栈、任何风格预设都能用。

用法：
  python3 component_recipe.py index                       重建 component-recipes/registry.json
  python3 component_recipe.py list [--tag travel]          列出配方（标签：base form mobile-consumer content travel ai game-table motion）
  python3 component_recipe.py show <id>                    看一个配方的用途、禁忌、状态、来源和代码
  python3 component_recipe.py search <关键词>              按名称、标签、用途搜索
  python3 component_recipe.py copy <id> [<id> ...] --to <目录> [--preset <风格编号>]
        把配方（连同依赖、用到的图标文件）拷进项目：<目录>/recipes.css、recipes.js、recipes-markup.html、icons/
        给了 --preset 时，额外写 <目录>/theme.css（风格变量）
  python3 component_recipe.py preview --preset <风格编号> [--tag <标签> | --ids a,b,c] -o <文件.html>
        用某个风格预设渲染配方预览页，截图看效果
  python3 component_recipe.py icon-css --dir <项目里的 svg 目录> -o <icons.css>
        把 IconScout / 品牌图标文件转成 .i-<文件名> 类，写法 <span class="r-ico i-文件名"></span>

规则：
  - 图标是真实文件（icons/ 下的 Lucide，ISC 许可；或换成 IconScout / 品牌文件），用 .r-ico 遮罩上色，不手画 path。
    图标以 data URI 写进 CSS：遮罩按 URL 加载时，file:// 打开的页面会被浏览器拦掉。
  - preview-assets/ 只给预览用。正式页面的图片、地图必须换成真实素材（产品图、目的地照片、地图 SDK）。
  - 配方给的是组件的结构、交互和状态；页面构图来自 design-decisions.md 第 2 块，页面长相来自 VT 视觉目标稿。
    拷进项目后按目标稿改字体、照片处理、容器和点睛元素；只用配方默认样式拼出来的页面就是模板脸。
"""
import argparse, base64, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "component-recipes"))
RECIPES = os.path.join(ROOT, "recipes")
REGISTRY = os.path.join(ROOT, "registry.json")
TAGS = ["base", "form", "mobile-consumer", "content", "travel", "ai", "game-table", "motion"]

META_RE = re.compile(r"<!--\s*recipe\s*(\{.*?\})\s*-->", re.S)
STYLE_RE = re.compile(r"<style>(.*?)</style>", re.S)
DEMO_RE = re.compile(r"<!--\s*demo\s*-->(.*?)<!--\s*/demo\s*-->", re.S)
SCRIPT_RE = re.compile(r"<script>(.*?)</script>", re.S)
ICON_RE = re.compile(r"(?<=[\"\s])i-([a-z][a-z0-9-]*)(?=[\"\s])")


def icon_rule(name, svg_path):
    svg = open(svg_path, encoding="utf-8").read()
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"\s+", " ", svg).strip()
    return f'.i-{name} {{ --ico: url("data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"); }}'


def icons_css(names, folder=None):
    folder = folder or os.path.join(ROOT, "icons")
    return "\n".join(icon_rule(n, os.path.join(folder, n + ".svg")) for n in sorted(names))


def parse(path):
    text = open(path, encoding="utf-8").read()
    m = META_RE.search(text)
    if not m:
        sys.exit(f"{path} 缺少 <!-- recipe {{...}} --> 元数据")
    try:
        meta = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        sys.exit(f"{path} 元数据不是合法 JSON：{e}")
    style = "\n".join(s.strip() for s in STYLE_RE.findall(text))
    demo = DEMO_RE.search(text)
    script = "\n".join(s.strip() for s in SCRIPT_RE.findall(text))
    icons = sorted(set(meta.get("icons", [])) | set(ICON_RE.findall(text)))
    return {
        "meta": meta,
        "style": style,
        "demo": demo.group(1).strip() if demo else "",
        "script": script,
        "icons": icons,
        "file": os.path.relpath(path, ROOT),
    }


def load_all():
    out = {}
    for name in sorted(os.listdir(RECIPES)):
        if name.endswith(".html"):
            r = parse(os.path.join(RECIPES, name))
            rid = r["meta"]["id"]
            if rid + ".html" != name:
                sys.exit(f"{name} 的 id 是 {rid}，文件名必须和 id 一致")
            out[rid] = r
    return out


CLASS_DEF_RE = re.compile(r"\.([rg]-[a-z0-9_-]+)")
CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')


def defined_classes(r):
    return set(CLASS_DEF_RE.findall(r["style"]))


def check_classes(recs, rid):
    """Every r-/g- class a recipe's markup uses must be styled by itself, a requires, or (demo only) a demoRequires."""
    base = set(CLASS_DEF_RE.findall(open(os.path.join(ROOT, "base.css"), encoding="utf-8").read()))
    r = recs[rid]
    m = r["meta"]
    runtime = closure(recs, [rid])
    demo_all = closure(recs, [rid], include_demo=True)
    have_runtime = base.union(*(defined_classes(recs[i]) for i in runtime))
    have_demo = base.union(*(defined_classes(recs[i]) for i in demo_all))
    used = {c for attr in CLASS_ATTR_RE.findall(r["demo"] + r["script"]) for c in attr.split() if re.match(r"[rg]-", c)}
    missing = sorted(c for c in used - have_demo)
    if missing:
        owners = {c: [o for o, ro in recs.items() if c in defined_classes(ro)] for c in missing}
        hint = "；".join(f"{c} ← {', '.join(o) or '没有配方定义'}" for c, o in owners.items())
        sys.exit(f"{rid} 用了没有样式来源的类：{hint}。把来源配方加进 requires（组件本身需要）或 demoRequires（只是示例需要）")
    demo_only = sorted(c for c in used - have_runtime)
    if demo_only and not m.get("demoRequires"):
        sys.exit(f"{rid} 的类 {demo_only} 只在示例依赖里有样式，需要声明 requires 或 demoRequires")


def build_index(recs):
    items = []
    for rid, r in recs.items():
        m = r["meta"]
        bad = [t for t in m.get("tags", []) if t not in TAGS]
        if bad:
            sys.exit(f"{rid} 用了未登记的标签 {bad}，可用：{TAGS}")
        for dep in m.get("requires", []) + m.get("demoRequires", []):
            if dep not in recs:
                sys.exit(f"{rid} 依赖的 {dep} 不存在")
        for ic in r["icons"]:
            if not os.path.exists(os.path.join(ROOT, "icons", ic + ".svg")):
                sys.exit(f"{rid} 用到的图标 icons/{ic}.svg 不存在")
        check_classes(recs, rid)
        items.append({
            "id": rid, "name": m["name"], "tags": m.get("tags", []), "use": m.get("use", ""), "dont": m.get("dont", ""),
            "states": m.get("states", []), "variants": m.get("variants", []), "requires": m.get("requires", []),
            "icons": r["icons"], "source": m.get("source", ""), "license": m.get("license", ""), "file": r["file"],
        })
    data = {
        "version": 1,
        "about": "通用组件配方：纯 HTML/CSS，只读风格预设变量。由 scripts/component_recipe.py index 生成，不要手改。",
        "tags": TAGS,
        "recipes": items,
    }
    with open(REGISTRY, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return data


def closure(recs, ids, include_demo=False):
    seen, order = set(), []

    def visit(i):
        if i in seen:
            return
        if i not in recs:
            sys.exit(f"找不到配方 {i}。先运行 list 或 search。")
        seen.add(i)
        m = recs[i]["meta"]
        for d in m.get("requires", []) + (m.get("demoRequires", []) if include_demo else []):
            visit(d)
        order.append(i)

    for i in ids:
        visit(i)
    return order


def preset_css(pid):
    if not pid:
        return ""
    res = subprocess.run([sys.executable, os.path.join(HERE, "style_preset.py"), "export", pid, "--format", "css"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit(res.stderr.strip() or res.stdout.strip())
    return res.stdout


def cmd_index(a):
    data = build_index(load_all())
    print(f"已写入 {os.path.relpath(REGISTRY)}：{len(data['recipes'])} 个配方")


def cmd_list(a):
    recs = load_all()
    build_index(recs)
    for rid, r in recs.items():
        m = r["meta"]
        if a.tag and a.tag not in m.get("tags", []):
            continue
        print(f"{rid:24} {m['name']}  [{', '.join(m.get('tags', []))}]")
        print(f"{'':24} 用在：{m.get('use', '')}")


def cmd_show(a):
    recs = load_all()
    r = recs.get(a.id) or sys.exit(f"找不到配方 {a.id}")
    m = r["meta"]
    print(f"# {m['id']} · {m['name']}")
    print(f"标签：{', '.join(m.get('tags', []))}")
    print(f"用在：{m.get('use', '')}")
    print(f"别用在：{m.get('dont', '')}")
    if m.get("variants"):
        print(f"变体：{'；'.join(m['variants'])}")
    print(f"状态：{'、'.join(m.get('states', []))}")
    if m.get("requires"):
        print(f"依赖：{', '.join(m['requires'])}（copy 会一起拷）")
    if r["icons"]:
        print(f"图标：{', '.join(r['icons'])}")
    if m.get("assets"):
        print(f"素材：{m['assets']}")
    if m.get("skin"):
        print(f"皮肤：{m['skin']}")
    print(f"来源：{m.get('source', '')}（{m.get('license', '')}）")
    print(f"文件：{os.path.join(ROOT, r['file'])}")
    print("\n--- 样式 ---\n" + r["style"])
    print("\n--- 结构示例 ---\n" + r["demo"])
    if r["script"]:
        print("\n--- 脚本 ---\n" + r["script"])


def cmd_search(a):
    recs = load_all()
    kw = a.keyword.lower()
    hits = 0
    for rid, r in recs.items():
        m = r["meta"]
        hay = " ".join([rid, m["name"], " ".join(m.get("tags", [])), m.get("use", ""), m.get("dont", ""), " ".join(m.get("variants", []))]).lower()
        if kw in hay:
            hits += 1
            print(f"{rid:24} {m['name']}  [{', '.join(m.get('tags', []))}]")
            print(f"{'':24} 用在：{m.get('use', '')}")
    if not hits:
        print(f"没有匹配「{a.keyword}」的配方。试试标签：{', '.join(TAGS)}；仍没有就按 shadcn 的变量约定新写一个，放进 recipes/ 后运行 index。")


def cmd_copy(a):
    recs = load_all()
    ids = closure(recs, a.ids)
    os.makedirs(a.to, exist_ok=True)
    base = open(os.path.join(ROOT, "base.css"), encoding="utf-8").read()
    css = [base]
    js, markup, icons = [], [], set()
    for rid in ids:
        r = recs[rid]
        css.append(f"/* ---- recipe: {rid} ({r['meta'].get('source', '')}) ---- */\n{r['style']}")
        if r["script"]:
            js.append(f"/* ---- recipe: {rid} ---- */\n{r['script']}")
        markup.append(f"<!-- ---- {rid} · {r['meta']['name']} ---- -->\n<!-- 用在：{r['meta'].get('use', '')} -->\n<!-- 别用在：{r['meta'].get('dont', '')} -->\n{r['demo']}")
        icons.update(r["icons"])
    if icons:
        css.append("/* ---- icons (Lucide, ISC) as data URIs; add your own with: component_recipe.py icon-css --dir <svg 目录> ---- */\n" + icons_css(icons))
    open(os.path.join(a.to, "recipes.css"), "w", encoding="utf-8").write("\n\n".join(css) + "\n")
    if js:
        open(os.path.join(a.to, "recipes.js"), "w", encoding="utf-8").write("\n\n".join(js) + "\n")
    open(os.path.join(a.to, "recipes-markup.html"), "w", encoding="utf-8").write(
        "<!-- 结构参考：文案、图片、数据按 design-decisions.md 替换；preview-assets/ 下的图片不能进正式页面 -->\n\n" + "\n\n".join(markup) + "\n")
    if icons:
        os.makedirs(os.path.join(a.to, "icons"), exist_ok=True)
        for ic in sorted(icons):
            shutil.copy(os.path.join(ROOT, "icons", ic + ".svg"), os.path.join(a.to, "icons", ic + ".svg"))
        shutil.copy(os.path.join(ROOT, "icons", "LICENSE-lucide.txt"), os.path.join(a.to, "icons", "LICENSE-lucide.txt"))
    if a.preset:
        open(os.path.join(a.to, "theme.css"), "w", encoding="utf-8").write(preset_css(a.preset))
    print(f"已拷贝 {len(ids)} 个配方到 {a.to}：{', '.join(ids)}")
    print(f"图标 {len(icons)} 个 → {os.path.join(a.to, 'icons')}")
    print("页面里按顺序引入：theme.css（风格变量）→ recipes.css → 页面自己的 css；外层容器加 class=\"r-root\"。")


PREVIEW_CSS = """
body { margin: 0; }
.pv-head { padding: 28px 32px 8px; font: 600 13px/1.4 var(--r-font); color: var(--muted-foreground); }
.pv-head h1 { margin: 0 0 4px; font: 700 24px/1.2 var(--r-font); color: var(--foreground); }
.pv-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(390px, 1fr)); gap: 20px; padding: 16px 32px 48px; align-items: start; }
.pv-item { display: grid; gap: 12px; padding: 16px 0; border-radius: 16px; background: var(--background); box-shadow: 0 0 0 1px var(--border); overflow: hidden; }
.pv-item > header { padding: 0 16px; }
.pv-item > header b { display: block; font: 600 14px/1.3 var(--r-font); color: var(--foreground); }
.pv-item > header span { font: 400 12px/1.4 var(--r-font); color: var(--muted-foreground); }
.pv-item > .pv-demo { padding: 0 16px; }
.pv-item[data-bleed] > .pv-demo { padding: 0; }
"""
BLEED = {"tabs", "chip-group", "carousel", "section-header", "hero-media", "feed-masonry", "destination-hero", "itinerary-timeline",
         "place-row", "trip-summary-bar", "map-with-sheet", "app-bar", "tab-bar", "sticky-cta", "prompt-composer", "felt-table", "photo-card"}


def cmd_preview(a):
    recs = load_all()
    if a.ids:
        ids = [i.strip() for i in a.ids.split(",") if i.strip()]
    elif a.tag:
        ids = [rid for rid, r in recs.items() if a.tag in r["meta"].get("tags", [])]
    else:
        ids = list(recs)
    if not ids:
        sys.exit("没有要预览的配方")
    styles = closure(recs, ids, include_demo=True)
    base = open(os.path.join(ROOT, "base.css"), encoding="utf-8").read()
    used_icons = set().union(*(recs[i]["icons"] for i in styles))
    css = "\n".join([preset_css(a.preset), base] + [recs[i]["style"] for i in styles] + [icons_css(used_icons), PREVIEW_CSS])
    cells = []
    for rid in ids:
        m = recs[rid]["meta"]
        bleed = " data-bleed" if rid in BLEED else ""
        cells.append(f'<section class="pv-item" data-recipe="{rid}"{bleed}><header><b>{m["name"]} · {rid}</b><span>{m.get("use", "")}</span></header><div class="pv-demo">{recs[rid]["demo"]}</div></section>')
    js = "\n".join(recs[i]["script"] for i in styles if recs[i]["script"])
    title = f"组件配方预览 · {a.preset}" + (f" · {a.tag}" if a.tag else "")
    base_href = "file://" + ROOT.rstrip("/") + "/"
    html = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<base href="{base_href}">
<title>{title}</title>
<style>
{css}
</style></head>
<body class="r-root">
<div class="pv-head"><h1>{title}</h1>预览图片和地图瓦片只供预览；正式页面换成真实素材。</div>
<div class="pv-grid">
{chr(10).join(cells)}
</div>
<script>
{js}
</script>
</body></html>
"""
    out = os.path.abspath(a.o)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    print(f"已写入 {out}（{len(ids)} 个配方，风格 {a.preset}）")


def cmd_icon_css(a):
    names = sorted(f[:-4] for f in os.listdir(a.dir) if f.endswith(".svg"))
    if not names:
        sys.exit(f"{a.dir} 下没有 .svg 文件")
    bad = [n for n in names if not re.fullmatch(r"[a-z][a-z0-9-]*", n)]
    if bad:
        sys.exit(f"图标文件名只能用小写字母、数字和连字符：{bad}")
    open(a.o, "w", encoding="utf-8").write(f"/* generated by component_recipe.py icon-css from {a.dir} */\n" + icons_css(names, a.dir) + "\n")
    print(f"已写入 {a.o}：{len(names)} 个图标，用法 <span class=\"r-ico i-{names[0]}\" aria-hidden=\"true\"></span>")


def main():
    ap = argparse.ArgumentParser(description="通用组件配方库工具")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("index").set_defaults(f=cmd_index)
    l = sp.add_parser("list"); l.add_argument("--tag", choices=TAGS); l.set_defaults(f=cmd_list)
    s = sp.add_parser("show"); s.add_argument("id"); s.set_defaults(f=cmd_show)
    q = sp.add_parser("search"); q.add_argument("keyword"); q.set_defaults(f=cmd_search)
    c = sp.add_parser("copy"); c.add_argument("ids", nargs="+"); c.add_argument("--to", required=True); c.add_argument("--preset"); c.set_defaults(f=cmd_copy)
    ic = sp.add_parser("icon-css"); ic.add_argument("--dir", required=True); ic.add_argument("-o", required=True); ic.set_defaults(f=cmd_icon_css)
    p = sp.add_parser("preview"); p.add_argument("--preset", required=True); p.add_argument("--tag", choices=TAGS); p.add_argument("--ids"); p.add_argument("-o", required=True); p.set_defaults(f=cmd_preview)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
