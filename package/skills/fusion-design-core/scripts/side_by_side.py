#!/usr/bin/env python3
"""并排对比：把我们的页面截图、视觉目标稿、同类标杆截图拼成一张图，用来做审美验收。

用法：
  python3 side_by_side.py --page index.html --width 390 --height 844 \
      --target target.png --refs refs/airbnb.png refs/klook.png -o compare-r1.png

输出：
  - 一张横向拼图：OURS | TARGET | REF 1 | REF 2 ...，统一高度，便于一眼比较
  - JSON 报告（stdout）：截图路径、页面实际用上的字体、是否只用了系统字体

规则：
  - 脚本拒绝无效对比：没有目标稿、标杆少于 2 张、目标稿和成品几乎同一张、竖屏页面配了横屏标杆。这些是 FAIL，进程退出码 1。
  - 图放在一起之后，好不好仍要按 methods-close.md 的三个问题看图回答。脚本退出码 0 不能代替看图。
  - 只用系统默认字体（没有加载任何网页字体或本地字体文件）会给出 WARN。
"""
import argparse, json, os, sys

SYSTEM_FONTS = {
    "-apple-system", "blinkmacsystemfont", "system-ui", "sans-serif", "serif", "monospace", "ui-sans-serif",
    "ui-serif", "ui-monospace", "pingfang sc", "helvetica", "helvetica neue", "arial", "times new roman",
    "segoe ui", "roboto", "sf pro", "sf pro text", "sf pro display", "noto sans sc", "microsoft yahei",
}


def screenshot(page_path, width, height, out):
    from playwright.sync_api import sync_playwright
    url = page_path if page_path.startswith(("http://", "https://", "file://")) else "file://" + os.path.abspath(page_path)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
        pg.goto(url)
        pg.wait_for_timeout(800)
        pg.evaluate("document.fonts && document.fonts.ready")
        fonts = pg.evaluate("""() => {
          const loaded = [];
          if (document.fonts) document.fonts.forEach(f => { if (f.status === 'loaded') loaded.push(f.family.replace(/["']/g, '')); });
          const used = new Set();
          document.querySelectorAll('h1,h2,h3,p,span,a,button,li,label,strong').forEach(el => {
            if (!el.textContent.trim()) return;
            const fam = getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, '').trim();
            used.add(fam);
          });
          return { loaded: [...new Set(loaded)], firstFamilies: [...used] };
        }""")
        pg.screenshot(path=out)
        b.close()
    return fonts


def thumb_mae(a_path, b_path, n=32):
    from PIL import Image
    def gray(path):
        im = Image.open(path).convert("L").resize((n, n), Image.LANCZOS)
        return list(im.getdata())
    aa, bb = gray(a_path), gray(b_path)
    return sum(abs(x - y) for x, y in zip(aa, bb)) / len(aa)


def image_is_wide(path):
    from PIL import Image
    im = Image.open(path)
    return im.width > im.height * 1.15


def band_corr(a_path, b_path, bands=12):
    from PIL import Image
    def sig(path):
        im = Image.open(path).convert("L").resize((24, bands * 8), Image.LANCZOS)
        w, h = im.size
        px = list(im.getdata())
        bh = h // bands
        out = []
        for i in range(bands):
            chunk = px[i * bh * w:(i + 1) * bh * w]
            out.append(sum(chunk) / len(chunk))
        return out
    aa, bb = sig(a_path), sig(b_path)
    n = len(aa)
    ma, mb = sum(aa) / n, sum(bb) / n
    va = sum((x - ma) ** 2 for x in aa)
    vb = sum((y - mb) ** 2 for y in bb)
    if va < 1 or vb < 1:
        return 1.0
    cov = sum((x - ma) * (y - mb) for x, y in zip(aa, bb))
    return cov / ((va ** 0.5) * (vb ** 0.5))


def refs_matching_page(directory, portrait):
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    found = []
    for name in sorted(os.listdir(directory)):
        if os.path.splitext(name)[1].lower() not in exts:
            continue
        path = os.path.join(directory, name)
        wide = image_is_wide(path)
        if portrait and wide:
            continue
        if (not portrait) and (not wide):
            continue
        found.append(path)
    return found[:3]


def compose(paths, labels, out, height=1200):
    from PIL import Image, ImageDraw, ImageFont
    ims = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        w = round(im.width * height / im.height)
        ims.append(im.resize((w, height), Image.LANCZOS))
    gap, top = 32, 64
    total_w = sum(i.width for i in ims) + gap * (len(ims) + 1)
    canvas = Image.new("RGB", (total_w, height + top + gap), (24, 24, 27))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    except OSError:
        font = ImageFont.load_default()
    x = gap
    for im, label in zip(ims, labels):
        draw.text((x, 18), label, fill=(240, 240, 240), font=font)
        canvas.paste(im, (x, top))
        x += im.width + gap
    canvas.save(out)


def main():
    ap = argparse.ArgumentParser(description="并排对比：我们 vs 目标稿 vs 标杆")
    ap.add_argument("--page", help="我们的页面（html 路径或 URL）；不给时用 --shot")
    ap.add_argument("--shot", help="已经截好的我们的截图")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=844)
    ap.add_argument("--target", help="视觉目标稿图片")
    ap.add_argument("--refs", nargs="*", default=[], help="同类标杆截图。有 --refs-dir 时不用这个")
    ap.add_argument("--refs-dir", help="RR 存图的目录。脚本只取和本屏同方向的图，横屏官网和横幅会被丢掉")
    ap.add_argument("-o", required=True, help="输出拼图 png")
    a = ap.parse_args()

    if not a.page and not a.shot:
        sys.exit("需要 --page 或 --shot")
    if a.refs_dir:
        if not os.path.isdir(a.refs_dir):
            sys.exit(f"找不到标杆目录 {a.refs_dir}")
        a.refs = refs_matching_page(a.refs_dir, a.height > a.width)
        report_note = f"从 {a.refs_dir} 取了同方向标杆 {len(a.refs)} 张"
    else:
        report_note = ""
    report = {"compare": os.path.abspath(a.o), "issues": [], "refs": list(a.refs)}
    if report_note:
        report["refs_note"] = report_note
    ours = a.shot
    if a.page:
        ours = os.path.splitext(a.o)[0] + "-ours.png"
        fonts = screenshot(a.page, a.width, a.height, ours)
        report["fonts"] = fonts
        custom = [f for f in fonts["loaded"] if f.lower() not in SYSTEM_FONTS]
        if not custom:
            report["issues"].append({"code": "SYSTEM_FONT_ONLY", "severity": "WARN",
                                     "message": "页面没有加载任何非系统字体。展示字体（标题、品牌字）要真正加载字体文件，不能只写 font-family 名字。"})
    paths, labels = [ours], ["OURS"]
    if a.target:
        paths.append(a.target); labels.append("TARGET")
    elif a.page:
        report["issues"].append({"code": "NO_TARGET", "severity": "FAIL", "message": "还原代码时必须提供 --target 视觉目标稿。直接验证 UI 视觉稿时请用 --shot <UI视觉稿> --refs-dir <标杆目录>。"})
    for i, r in enumerate(a.refs, 1):
        paths.append(r); labels.append(f"REF {i}")
        if os.path.exists(r) and a.height > a.width and image_is_wide(r):
            report["issues"].append({
                "code": "REF_WRONG_DEVICE", "severity": "FAIL",
                "message": f"{r} 是横屏图。竖屏页面的标杆必须是同一种屏幕的竖屏截图，官网首屏和横幅不能凑数。",
            })
        if os.path.exists(r) and a.width > a.height and not image_is_wide(r):
            report["issues"].append({
                "code": "REF_WRONG_DEVICE", "severity": "FAIL",
                "message": f"{r} 是竖屏图。横屏页面（如棋牌桌/横版游戏）的标杆必须是横屏实机截图。",
            })
    if len(a.refs) < 2:
        report["issues"].append({"code": "FEW_REFS", "severity": "FAIL", "message": "标杆截图少于 2 张，对比不可靠。"})
    for p in paths:
        if not os.path.exists(p):
            sys.exit(f"找不到图片 {p}")
    compose(paths, labels, a.o)
    report["ours"] = os.path.abspath(ours)
    if a.target and os.path.exists(ours):
        mae = round(thumb_mae(ours, a.target), 1)
        report["target_mae"] = mae
        if mae < 18:
            report["issues"].append({
                "code": "TARGET_IS_COPY", "severity": "FAIL",
                "message": f"目标稿和成品几乎是同一张图（差异 {mae}）。这轮对比作废。目标稿要先于成品，并且看得出完成度差在哪。",
            })
        layout = round(band_corr(ours, a.target), 3)
        report["target_layout"] = layout
        if mae >= 18 and layout >= 0.9:
            report["issues"].append({
                "code": "TARGET_SAME_LAYOUT", "severity": "FAIL",
                "message": f"目标稿和成品不是同一张图（像素差 {mae}），但上下结构几乎一样（相关 {layout}）。这轮对比作废。目标稿要先定完成度，不能照着成品的构图再画一张。",
            })
    report["passed"] = not any(i["severity"] == "FAIL" for i in report["issues"])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
