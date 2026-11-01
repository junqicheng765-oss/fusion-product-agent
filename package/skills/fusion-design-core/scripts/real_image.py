#!/usr/bin/env python3
"""Real Image Library：统一搜索真实摄影并下载到项目里。

主库：Pixabay（有 PIXABAY_API_KEY）+ Openverse（可匿名）
补充：Unsplash（已预置 Access Key，环境变量 UNSPLASH_ACCESS_KEY 可覆盖）、Pexels（PEXELS_API_KEY，仅已有 key）
地点：Wikimedia Commons（无需 key，适合具体景点）

  python3 real_image.py search "桂林山水首页" --role hero --tone cool
  python3 real_image.py get wikimedia:File:Guilin_mifan.jpg --out ./assets/real-images

图片免费 ≠ API 可无限调用。没有 key 的库自动跳过，不编造成功。
Unsplash 必须走它返回的 URL，选用时打 download 追踪，不把图囤成自己的图库。
"""
import argparse, json, os, re, ssl, sys, urllib.parse, urllib.request
from pathlib import Path

UA = "DeepTripDesignOS/1.0 (real-image-library; +https://github.com)"
DEFAULT_UNSPLASH_ACCESS_KEY = os.environ.get(
    "UNSPLASH_ACCESS_KEY",
    "fTAH6txY6VP7rP8xkBEQSZxJxWE18z79T5DzQWCMZQc",
).strip()
CTX = ssl.create_default_context()
ROLE = {
    "hero": {"orientation": "landscape", "min_w": 1600, "extra": "cinematic wide shot landscape no text no watermark"},
    "card": {"orientation": "landscape", "min_w": 800, "extra": "clear subject centered photo"},
    "portrait": {"orientation": "portrait", "min_w": 800, "extra": "portrait photo"},
    "background": {"orientation": "landscape", "min_w": 1400, "extra": "background atmosphere bokeh no text"},
    "place": {"orientation": "landscape", "min_w": 1200, "extra": "landmark photography"},
}
TONE = {
    "warm": {"pixabay": "orange,yellow,brown", "unsplash": "orange"},
    "cool": {"pixabay": "blue,green,turquoise", "unsplash": "blue"},
    "neutral": {"pixabay": "white,gray", "unsplash": "white"},
    "dark": {"pixabay": "black,gray", "unsplash": "black"},
    "green": {"pixabay": "green", "unsplash": "green"},
}
TERM = {
    "旅游": "travel", "旅行": "travel", "首页": "", "官网": "", "英雄图": "",
    "风景": "landscape", "山水": "landscape mountains river", "城市": "city skyline",
    "美食": "food cuisine", "建筑": "architecture", "人物": "people lifestyle",
    "自然": "nature", "海滩": "beach", "夜晚": "night", "白天": "daylight",
    "中国": "China", "北京": "Beijing", "上海": "Shanghai", "杭州": "Hangzhou",
    "成都": "Chengdu", "西安": "Xian", "桂林": "Guilin", "阳朔": "Yangshuo",
    "张家界": "Zhangjiajie", "黄山": "Huangshan", "西湖": "West Lake Hangzhou",
    "故宫": "Forbidden City Beijing", "长城": "Great Wall of China",
    "外滩": "the Bund Shanghai", "丽江": "Lijiang", "大理": "Dali Yunnan",
    "西藏": "Tibet", "新疆": "Xinjiang", "云南": "Yunnan", "川西": "western Sichuan",
}


def env(name, default=""):
    return (os.environ.get(name) or default or "").strip()


def unsplash_key():
    return env("UNSPLASH_ACCESS_KEY", DEFAULT_UNSPLASH_ACCESS_KEY)


def get_json(url, headers=None, timeout=18):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


def download_bytes(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read(), r.headers.get("Content-Type", "")


def english_query(raw, role):
    q = raw.strip()
    extra = []
    for zh, en in TERM.items():
        if zh in q:
            q = q.replace(zh, " ")
            if en:
                extra.append(en)
    q = re.sub(r"\s+", " ", q).strip()
    # leftover CJK kept for Pixabay lang=zh / Wikimedia; English part for others
    en = " ".join(extra + ([q] if re.search(r"[A-Za-z]", q) else []))
    en = (en + " " + ROLE[role]["extra"]).strip()
    return {"raw": raw, "english": en or ROLE[role]["extra"], "has_cjk": bool(re.search(r"[\u4e00-\u9fff]", raw))}


def looks_place(raw, role):
    if role == "place":
        return True
    keys = ["故宫", "长城", "桂林", "西湖", "黄山", "外滩", "张家界", "丽江", "大理",
            "Beijing", "Shanghai", "Guilin", "temple", "palace", "landmark"]
    return any(k.lower() in raw.lower() for k in keys)


def rec(source, sid, title, creator, license_, license_url, page, preview, full, w, h, extra=None):
    return {
        "id": f"{source}:{sid}",
        "source": source,
        "title": title or "",
        "creator": creator or "unknown",
        "license": license_ or "",
        "license_url": license_url or "",
        "page_url": page or "",
        "preview_url": preview or full,
        "download_url": full,
        "width": w or 0,
        "height": h or 0,
        "attribution": f"{title or sid} — {creator} / {source} / {license_}".strip(" —"),
        "extra": extra or {},
    }


def search_openverse(en, role, n):
    spec = ROLE[role]
    params = {
        "q": en, "page_size": min(n, 20), "license_type": "commercial",
        "aspect_ratio": "wide" if spec["orientation"] == "landscape" else ("tall" if spec["orientation"] == "portrait" else "square"),
        "size": "large",
    }
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)
    data, _ = get_json(url, timeout=20)
    out = []
    for it in data.get("results") or []:
        out.append(rec(
            "openverse", it.get("id"), it.get("title"), it.get("creator"),
            it.get("license"), it.get("license_url"), it.get("foreign_landing_url"),
            it.get("thumbnail"), it.get("url"), it.get("width"), it.get("height"),
            {"attribution": it.get("attribution")},
        ))
    return out


def wiki_term(raw, en):
    cleaned = raw
    for stop in ("首页", "官网", "英雄图", "配图", "背景", "Banner", "hero"):
        cleaned = cleaned.replace(stop, "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if re.search(r"[\u4e00-\u9fff]", cleaned) and len(cleaned) >= 2:
        return cleaned
    return en


def search_wikimedia(raw, en, n):
    term = wiki_term(raw, en)
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": f"{term} filetype:bitmap",
        "gsrnamespace": "6", "gsrlimit": str(min(n, 10)),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": "1280",
        "format": "json", "origin": "*",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    data, _ = get_json(url, timeout=18)
    out = []
    for page in (data.get("query") or {}).get("pages", {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value", "")
        artist = re.sub("<[^>]+>", "", (meta.get("Artist") or {}).get("value", "") or "Wikimedia Commons")
        mime = info.get("mime") or ""
        if not mime.startswith("image/") or "svg" in mime:
            continue
        sized = info.get("thumburl") or info.get("url")
        out.append(rec(
            "wikimedia", page.get("title", "").replace("File:", ""),
            page.get("title", ""), artist, lic,
            (meta.get("LicenseUrl") or {}).get("value", ""),
            info.get("descriptionurl"), sized, sized,
            info.get("thumbwidth") or info.get("width"),
            info.get("thumbheight") or info.get("height"),
            {"original_url": info.get("url"), "original_width": info.get("width"), "original_height": info.get("height")},
        ))
    return out


def search_pixabay(en, raw, role, tone, n):
    key = env("PIXABAY_API_KEY")
    if not key:
        return [], "skip:PIXABAY_API_KEY"
    spec = ROLE[role]
    params = {
        "key": key, "q": en[:100], "image_type": "photo",
        "orientation": "horizontal" if spec["orientation"] == "landscape" else ("vertical" if spec["orientation"] == "portrait" else "all"),
        "min_width": spec["min_w"], "safesearch": "true",
        "per_page": min(max(n, 3), 20),
    }
    if raw and re.search(r"[\u4e00-\u9fff]", raw):
        params["lang"] = "zh"
        params["q"] = raw[:100]
    if tone in TONE:
        params["colors"] = TONE[tone]["pixabay"]
    data, _ = get_json("https://pixabay.com/api/?" + urllib.parse.urlencode(params))
    out = []
    for it in data.get("hits") or []:
        # 用 webformat / large 而不是 8MB 原图
        sized = it.get("largeImageURL") or it.get("webformatURL")
        out.append(rec(
            "pixabay", it.get("id"), it.get("tags"), it.get("user"),
            "Pixabay License", "https://pixabay.com/service/license/",
            it.get("pageURL"), it.get("previewURL"), sized,
            it.get("imageWidth"), it.get("imageHeight"),
        ))
    return out, None


def search_unsplash(en, role, tone, n):
    key = unsplash_key()
    if not key:
        return [], "skip:UNSPLASH_ACCESS_KEY"
    spec = ROLE[role]
    ori = {"landscape": "landscape", "portrait": "portrait"}.get(spec["orientation"], "landscape")
    params = {"query": en, "per_page": min(n, 10), "orientation": ori, "content_filter": "high"}
    if tone in TONE:
        params["color"] = TONE[tone]["unsplash"]
    data, _ = get_json(
        "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(params),
        headers={"Authorization": f"Client-ID {key}"},
    )
    out = []
    for it in data.get("results") or []:
        user = (it.get("user") or {})
        urls = it.get("urls") or {}
        links = it.get("links") or {}
        # regular ≈ 1080px，不要 raw
        out.append(rec(
            "unsplash", it.get("id"), it.get("description") or it.get("alt_description"),
            user.get("name"), "Unsplash License", "https://unsplash.com/license",
            it.get("links", {}).get("html"), urls.get("small"), urls.get("regular"),
            it.get("width"), it.get("height"),
            {"download_location": links.get("download_location"), "username": user.get("username")},
        ))
    return out, None


def search_pexels(en, role, n):
    key = env("PEXELS_API_KEY")
    if not key:
        return [], "skip:PEXELS_API_KEY"
    spec = ROLE[role]
    ori = "landscape" if spec["orientation"] == "landscape" else "portrait"
    params = {"query": en, "per_page": min(n, 15), "orientation": ori}
    data, _ = get_json(
        "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(params),
        headers={"Authorization": key},
    )
    out = []
    for it in data.get("photos") or []:
        src = it.get("src") or {}
        # large ≈ 940px 宽，large2x 更高；不用 original
        sized = src.get("large2x") or src.get("large")
        out.append(rec(
            "pexels", it.get("id"), it.get("alt"), (it.get("photographer")),
            "Pexels License", "https://www.pexels.com/license/",
            it.get("url"), src.get("medium"), sized,
            it.get("width"), it.get("height"),
        ))
    return out, None


def score(item, role, tone):
    spec = ROLE[role]
    s = 0
    w, h = item["width"], item["height"]
    if w >= spec["min_w"]:
        s += 3
    elif w >= spec["min_w"] * 0.6:
        s += 1
    if spec["orientation"] == "landscape" and w > h:
        s += 2
    if spec["orientation"] == "portrait" and h > w:
        s += 2
    lic = (item["license"] or "").lower()
    if any(x in lic for x in ("cc0", "pdm", "public domain", "pixabay", "unsplash", "pexels")):
        s += 2
    if "nc" in lic or "nd" in lic:
        s -= 3
    if item["source"] == "wikimedia" and looks_place(item["title"], role):
        s += 2
    return s


def run_search(query, role, tone, sources, n, place):
    q = english_query(query, role)
    skipped, errors, items = [], [], []
    order = sources or (["wikimedia", "pixabay", "openverse", "unsplash", "pexels"] if place or looks_place(query, role)
                        else ["pixabay", "openverse", "unsplash", "pexels", "wikimedia"])
    for src in order:
        try:
            if src == "openverse":
                items.extend(search_openverse(q["english"], role, n))
            elif src == "wikimedia":
                items.extend(search_wikimedia(query, q["english"], n))
            elif src == "pixabay":
                got, skip = search_pixabay(q["english"], query, role, tone, n)
                if skip:
                    skipped.append(skip)
                items.extend(got)
            elif src == "unsplash":
                got, skip = search_unsplash(q["english"], role, tone, n)
                if skip:
                    skipped.append(skip)
                items.extend(got)
            elif src == "pexels":
                got, skip = search_pexels(q["english"], role, n)
                if skip:
                    skipped.append(skip)
                items.extend(got)
        except Exception as e:
            errors.append(f"{src}:{e.__class__.__name__}")
    items.sort(key=lambda x: score(x, role, tone), reverse=True)
    return {"query": q, "role": role, "tone": tone, "skipped": skipped, "errors": errors, "results": items[:n]}


def save_one(item, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if item["source"] == "unsplash":
        loc = (item.get("extra") or {}).get("download_location")
        key = unsplash_key()
        if loc and key:
            try:
                get_json(loc, headers={"Authorization": f"Client-ID {key}"}, timeout=12)
            except Exception:
                pass
    data, ctype = download_bytes(item["download_url"])
    ext = ".jpg"
    if "png" in ctype:
        ext = ".png"
    elif "webp" in ctype:
        ext = ".webp"
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", item["id"])[:80]
    stem = re.sub(r"\.(jpe?g|png|webp|gif)$", "", stem, flags=re.I)
    img = out / (stem + ext)
    meta = out / (stem + ".json")
    img.write_bytes(data)
    meta.write_text(json.dumps({**item, "local_file": str(img), "bytes": len(data)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    credits = out / "ATTRIBUTION.md"
    line = f"- {item['attribution']}  <{item['page_url']}>\n"
    prev = credits.read_text(encoding="utf-8") if credits.exists() else "# Real Image Library 来源\n\n"
    if line not in prev:
        credits.write_text(prev + line, encoding="utf-8")
    return str(img), str(meta)


def find_in_report(report, iid):
    for it in report.get("results") or []:
        if it["id"] == iid or it["id"].endswith(":" + iid) or iid in it["id"]:
            return it
    return None


def cmd_search(a):
    sources = [x.strip() for x in (a.sources or "").split(",") if x.strip()] or None
    report = run_search(a.query, a.role, a.tone, sources, a.n, a.place)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if a.json:
        Path(a.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if not report["results"]:
        sys.exit("没有结果。检查网络、API key，或换关键词。不得因此直接编造图片来源。")


def cmd_get(a):
    if a.from_json:
        report = json.loads(Path(a.from_json).read_text(encoding="utf-8"))
        item = find_in_report(report, a.id)
        if not item:
            sys.exit("json 里没有这个 id")
    else:
        # id like wikimedia:Guilin_mifan.jpg
        source, _, rest = a.id.partition(":")
        if source == "wikimedia" and rest:
            item = rec("wikimedia", rest, rest, "Wikimedia Commons", "", "", "", "",
                       f"https://commons.wikimedia.org/wiki/Special:FilePath/{urllib.parse.quote(rest)}", 0, 0)
            # resolve via API
            hits = search_wikimedia(rest.replace("_", " "), rest, 3)
            item = next((h for h in hits if rest.replace(" ", "_") in h["id"] or rest in h["title"]), hits[0] if hits else item)
        else:
            sys.exit("请先 search --json 再 get，或使用 wikimedia:FileName")
    path, meta = save_one(item, a.out)
    print(json.dumps({"saved": path, "meta": meta, "attribution": item["attribution"]}, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="Real Image Library")
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("search")
    s.add_argument("query")
    s.add_argument("--role", default="hero", choices=list(ROLE))
    s.add_argument("--tone", default="neutral", choices=list(TONE))
    s.add_argument("--sources", help="逗号分隔：pixabay,openverse,unsplash,pexels,wikimedia")
    s.add_argument("--n", type=int, default=8)
    s.add_argument("--place", action="store_true")
    s.add_argument("--json")
    s.set_defaults(f=cmd_search)
    g = sp.add_parser("get")
    g.add_argument("id")
    g.add_argument("--out", default="./assets/real-images")
    g.add_argument("--from-json")
    g.set_defaults(f=cmd_get)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
