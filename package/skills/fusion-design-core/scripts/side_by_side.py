#!/usr/bin/env python3
"""Create comparison evidence for visual review; do not issue an aesthetic verdict.

用法：
  python3 side_by_side.py --mode restore --page index.html --width 390 --height 844 \
      --target target.png --refs refs/airbnb.png refs/klook.png -o compare-r1.png

输出：
  - 一张横向拼图：OURS | TARGET | REF 1 | REF 2 ...，统一高度，便于一眼比较
  - JSON 报告（stdout）：截图路径、页面实际用上的字体、是否只用了系统字体

Modes:
  compare (default): compare against at least one actual reference or target.
  restore: compare against a required target; additional references are optional.
Success means readable comparison inputs/output, not visual quality or fidelity approval.
Similarity metrics cannot establish chronology, copying, legitimacy, or beauty.
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
    with Image.open(path) as im:
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


def comparison_report(ours, target=None, refs=None, width=390, height=844, mode="compare"):
    """Validate comparison evidence and report diagnostic metrics without judging design."""
    from PIL import Image

    refs = list(refs or [])
    report = {
        "mode": mode,
        "ours": os.path.abspath(ours),
        "target": os.path.abspath(target) if target else None,
        "refs": refs,
        "issues": [],
        "visual_verdict": "NOT_EVALUATED",
        "fidelity_verdict": "NOT_EVALUATED",
        "limits": "Readability of comparison inputs and diagnostic image similarity only; not an aesthetic verdict, semantic review or proof of source chronology.",
    }
    if mode not in ("compare", "restore"):
        report["issues"].append({"code": "INVALID_MODE", "severity": "FAIL", "message": "Use compare or restore."})
    if mode == "restore" and not target:
        report["issues"].append({"code": "TARGET_REQUIRED", "severity": "FAIL", "message": "还原对照需要准确的 --target；标杆不代替正式目标稿。"})
    if mode == "compare" and not target and not refs:
        report["issues"].append({"code": "NO_COMPARISON_INPUT", "severity": "FAIL", "message": "至少提供一张适用参考或目标图；只有成品不能构成对比。"})

    inputs = [("ours", ours)] + ([("target", target)] if target else [])
    inputs += [("reference", path) for path in refs]
    readable = True
    for role, path in inputs:
        try:
            with Image.open(path) as im:
                im.load()
                if im.width <= 0 or im.height <= 0:
                    raise ValueError("Empty image")
        except (OSError, ValueError) as exc:
            readable = False
            report["issues"].append({"code": "COMPARISON_IMAGE_UNREADABLE", "severity": "FAIL", "element": str(path), "message": f"{role}: {exc}"})
    if readable:
        for path in refs:
            if (height > width and image_is_wide(path)) or (width > height and not image_is_wide(path)):
                report["issues"].append({"code": "REF_ORIENTATION_DIFFERENT", "severity": "WARN", "element": str(path), "message": "参考与目标视口方向不同；核对其实际支持范围，局部手法参考不能自动为整页平台构图背书。"})
        if target:
            report["target_mae"] = round(thumb_mae(ours, target), 1)
            report["target_layout"] = round(band_corr(ours, target), 3)
            report["similarity_note"] = "Thumbnail metrics are diagnostic only. High similarity is compatible with accurate restoration; confirm exact content, states, source versions and rendering in visual review."

    report["evidence_ready"] = not any(i["severity"] == "FAIL" for i in report["issues"])
    # Backward-compatible key: it refers only to this script's evidence checks.
    report["passed"] = report["evidence_ready"]
    return report


def main():
    ap = argparse.ArgumentParser(description="并排对比：我们 vs 目标稿 vs 标杆")
    ap.add_argument("--page", help="我们的页面（html 路径或 URL）；不给时用 --shot")
    ap.add_argument("--shot", help="已经截好的我们的截图")
    ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=844)
    ap.add_argument("--mode", choices=["compare", "restore"], default="compare", help="compare：方向/标杆比较；restore：正式目标稿还原对照。成功仅表示对比材料有效。")
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
    ours = a.shot
    fonts = None
    if a.page:
        ours = os.path.splitext(a.o)[0] + "-ours.png"
        fonts = screenshot(a.page, a.width, a.height, ours)
    report = comparison_report(ours, a.target, a.refs, a.width, a.height, a.mode)
    report["compare"] = None
    if report_note:
        report["refs_note"] = report_note
    if fonts is not None:
        report["fonts"] = fonts
        custom = [f for f in fonts["loaded"] if f.lower() not in SYSTEM_FONTS]
        if not custom:
            report["issues"].append({"code": "SYSTEM_FONT_ONLY", "severity": "INFO", "message": "当前未检测到非系统字体；系统字体可按任务采用，此记录不评价排版或字形质量。"})
    paths, labels = [ours], ["OURS"]
    if a.target:
        paths.append(a.target); labels.append("TARGET")
    for i, r in enumerate(a.refs, 1):
        paths.append(r); labels.append(f"REF {i}")
    if report["evidence_ready"]:
        compose(paths, labels, a.o)
        report["compare"] = os.path.abspath(a.o)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
