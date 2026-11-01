#!/usr/bin/env python3
"""
IconScout v3 API Helper for design-thinking-os
Docs: https://api-docs.iconscout.com/#description/credits-and-limits
OpenAPI: https://cdn.iconscout.com/openapi.json

Pre-configured Client-ID: 232598791050530
Supports:
  1. Search assets (`icon`, `3d`, `lottie`, `illustration`, `ai-image`) with style/grid/price/sort filters
  2. Fetch item metadata & direct CDN preview/PNG/MP4 URLs (requires only Client-ID)
  3. Download preview/PNG/MP4 assets directly to local disk (requires only Client-ID)
  4. Full vector/source download (`svg`, `json`, `lottie`, `glb`) & format conversion (`svg-to-lottie`, `lottie-to-gif`, `lottie-to-webp`, `lottie-to-mp4`) when ICONSCOUT_CLIENT_SECRET is provided
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_URL = "https://api.iconscout.com"
DEFAULT_CLIENT_ID = os.environ.get("ICONSCOUT_CLIENT_ID", "232598791050530")
DEFAULT_CLIENT_SECRET = os.environ.get("ICONSCOUT_CLIENT_SECRET", "")


def build_headers(client_id: str, client_secret: str = "", json_body: bool = False) -> dict:
    headers = {
        "Client-ID": client_id,
        "User-Agent": "design-thinking-os/1.0",
        "Accept": "application/json",
    }
    if client_secret:
        headers["Client-Secret"] = client_secret
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def api_request(method: str, path: str, params: dict = None, body: dict = None,
                client_id: str = DEFAULT_CLIENT_ID, client_secret: str = DEFAULT_CLIENT_SECRET) -> dict:
    url = f"{BASE_URL}{path}"
    if params:
        query_pairs = []
        for k, v in params.items():
            if v is None or v == "":
                continue
            if isinstance(v, list):
                for item in v:
                    query_pairs.append((k, str(item)))
            else:
                query_pairs.append((k, str(v)))
        if query_pairs:
            url += "?" + urllib.parse.urlencode(query_pairs)

    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers=build_headers(client_id, client_secret, json_body=(body is not None)),
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"HTTP {e.code} Error calling {url}: {err_body}", file=sys.stderr)
        sys.exit(1)


def extract_best_preview_url(item: dict) -> str:
    urls = item.get("urls") or {}
    for key in ["png_512", "png_256", "png_128", "thumb", "preview_image", "png_64"]:
        if urls.get(key):
            return urls[key]
    return next(iter(urls.values()), "")


def cmd_search(args):
    params = {
        "query": args.query,
        "asset": args.asset,
        "price": args.price,
        "sort": args.sort,
        "per_page": args.per_page,
        "page": args.page,
        "icon_grid": args.icon_grid,
        "styles[]": args.styles,
        "formats[]": args.formats,
    }
    res = api_request("GET", "/v3/search", params=params, client_id=args.client_id)
    items_block = (res.get("response") or {}).get("items") or {}
    data = items_block.get("data") or []
    simplified = []
    for it in data:
        simplified.append({
            "uuid": it.get("uuid"),
            "id": it.get("id"),
            "asset": it.get("asset"),
            "name": it.get("name"),
            "slug": it.get("slug"),
            "price": it.get("price"),
            "best_url": extract_best_preview_url(it),
            "urls": it.get("urls"),
        })

    if args.download_dir:
        out_dir = Path(args.download_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for item in simplified:
            u = item["best_url"]
            if not u:
                continue
            ext = Path(urllib.parse.urlparse(u).path).suffix or ".png"
            fname = f"{item['asset']}-{item['slug'][:40]}-{item['id']}{ext}"
            dest = out_dir / fname
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                dest.write_bytes(r.read())
            item["downloaded_path"] = str(dest.resolve())

    output = {
        "total": items_block.get("total", len(simplified)),
        "count": len(simplified),
        "query": args.query,
        "asset": args.asset,
        "items": simplified,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def cmd_item(args):
    res = api_request(
        "GET",
        f"/v3/items/{args.uuid}",
        params={"additional_informations": "true"},
        client_id=args.client_id,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))


def cmd_download(args):
    if not args.client_secret:
        print(
            "Note: Client-Secret not provided; falling back to highest-resolution direct CDN asset via Client-ID.",
            file=sys.stderr,
        )
        res = api_request(
            "GET",
            f"/v3/items/{args.uuid}",
            params={"additional_informations": "true"},
            client_id=args.client_id,
        )
        item = (res.get("response") or {}).get("item") or {}
        u = extract_best_preview_url(item)
        if not u:
            print("No direct URL found on item.", file=sys.stderr)
            sys.exit(1)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            out_path.write_bytes(r.read())
        print(json.dumps({"mode": "cdn_preview", "url": u, "saved_to": str(out_path.resolve())}, indent=2, ensure_ascii=False))
        return

    body = {"format": args.format}
    if args.width is not None:
        body["width"] = args.width
    if args.height is not None:
        body["height"] = args.height
    res = api_request(
        "POST",
        f"/v3/items/{args.uuid}/api-download",
        body=body,
        client_id=args.client_id,
        client_secret=args.client_secret,
    )
    dl_url = ((res.get("response") or {}).get("download") or {}).get("url")
    if dl_url and args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            out_path.write_bytes(r.read())
        res["saved_to"] = str(out_path.resolve())
    print(json.dumps(res, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="IconScout v3 API CLI for icons, 3D icons, Lottie animations, and illustrations")
    parser.add_argument("--client-id", default=DEFAULT_CLIENT_ID, help="IconScout Client-ID (default: 232598791050530)")
    parser.add_argument("--client-secret", default=DEFAULT_CLIENT_SECRET, help="IconScout Client-Secret (optional, for source download/convert)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search icons, 3d, lottie, illustration, or ai-image")
    p_search.add_argument("--query", "-q", required=True, help="Search keywords in English (e.g. 'wallet', 'gift box')")
    p_search.add_argument("--asset", "-a", default="icon", choices=["icon", "3d", "lottie", "illustration", "ai-image"])
    p_search.add_argument("--styles", "-s", nargs="*", help="Filter styles: line, glyph, dualtone, flat, colored-outline, gradient, isometric, rounded, doodle, sticker, tile")
    p_search.add_argument("--formats", "-f", nargs="*", help="Filter formats: svg, png, eps, json, lottie, gif, mp4, gltf, glb, blend")
    p_search.add_argument("--price", choices=["free", "premium"], help="Filter by free or premium")
    p_search.add_argument("--sort", default="relevant", choices=["relevant", "popular", "latest", "featured"])
    p_search.add_argument("--icon-grid", type=int, help="Icon grid size in px (e.g. 24)")
    p_search.add_argument("--per-page", type=int, default=6, help="Results per page")
    p_search.add_argument("--page", type=int, default=1)
    p_search.add_argument("--download-dir", "-d", help="Optional directory to immediately download matched preview/PNG/MP4 files")
    p_search.set_defaults(func=cmd_search)

    p_item = sub.add_parser("item", help="Get detailed metadata for an asset UUID")
    p_item.add_argument("uuid", help="Asset UUID")
    p_item.set_defaults(func=cmd_item)

    p_dl = sub.add_parser("download", help="Download asset by UUID")
    p_dl.add_argument("uuid", help="Asset UUID")
    p_dl.add_argument("--format", default="svg", help="svg, png, json, lottie, gif, mp4, glb, etc.")
    p_dl.add_argument("--width", type=int)
    p_dl.add_argument("--height", type=int)
    p_dl.add_argument("--out", "-o", required=True, help="Output file path")
    p_dl.set_defaults(func=cmd_download)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
