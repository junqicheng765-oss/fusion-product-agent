#!/usr/bin/env python3
"""Design Asset Memory：先搜内部已验收资产，再考虑外部库。

入库必须同时满足：自动验收通过、用户确认。
  python3 asset_memory.py search 空状态
  python3 asset_memory.py list
  python3 asset_memory.py deposit --type pattern --title "..." --conditions "..." --files a.html --validation path.json --confirm
"""
import argparse, json, os, re, sys, datetime
from pathlib import Path

SKILL_MEM = Path(__file__).resolve().parent.parent / "asset-memory"
TYPES = ("pattern", "page", "style", "motion", "component", "color", "type")


def roots():
    out = [SKILL_MEM]
    proj = Path.cwd() / ".design-memory"
    if proj.resolve() != SKILL_MEM.resolve():
        out.append(proj)
    return out


def index_path(root):
    return root / "index.json"


def load_index(root):
    p = index_path(root)
    if not p.exists():
        return {"version": 1, "entries": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save_index(root, data):
    root.mkdir(parents=True, exist_ok=True)
    index_path(root).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def all_entries():
    rows = []
    for root in roots():
        for e in load_index(root)["entries"]:
            e = dict(e)
            e["_root"] = str(root)
            rows.append(e)
    return rows


def cmd_list(_):
    rows = all_entries()
    if not rows:
        print("内部资产库是空的。验收通过并经用户确认后，用 deposit 入库。")
        return
    for e in rows:
        print(f"{e['id']:28} {e['type']:10} {e['title']}  条件: {e.get('conditions','')[:40]}")


def cmd_search(a):
    q = a.query.lower()
    hits = []
    for e in all_entries():
        blob = " ".join(str(e.get(k, "")) for k in ("title", "conditions", "type", "notes", "id")).lower()
        if q in blob:
            hits.append(e)
    if not hits:
        print("内部资产未命中，再走 resource_router 的外部 adapter。")
        return
    print(f"命中 {len(hits)} 条（先用这些，不要先去外部库）")
    print(json.dumps(hits, ensure_ascii=False, indent=2))


def cmd_deposit(a):
    if not a.confirm:
        sys.exit("入库必须加 --confirm，表示用户已确认这套方案可以复用。")
    if a.type not in TYPES:
        sys.exit("type 必须是 " + ", ".join(TYPES))
    root = Path(a.root) if a.root else (Path.cwd() / ".design-memory")
    data = load_index(root)
    slug = re.sub(r"[^a-z0-9]+", "-", a.title.lower()).strip("-")[:40] or "entry"
    eid = f"{a.type}-{slug}-{datetime.date.today().isoformat()}"
    if any(e["id"] == eid for e in data["entries"]):
        eid += "-2"
    entry = {
        "id": eid,
        "type": a.type,
        "title": a.title,
        "conditions": a.conditions,
        "files": a.files or [],
        "validation": a.validation,
        "notes": a.notes or "",
        "deposited": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": "validated-project",
    }
    data["entries"].append(entry)
    save_index(root, data)
    print("已入库", eid, "→", index_path(root))


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("list").set_defaults(f=cmd_list)
    s = sp.add_parser("search"); s.add_argument("query"); s.set_defaults(f=cmd_search)
    d = sp.add_parser("deposit")
    d.add_argument("--type", required=True)
    d.add_argument("--title", required=True)
    d.add_argument("--conditions", required=True, help="什么任务、平台、风格族下可以复用")
    d.add_argument("--files", nargs="*")
    d.add_argument("--validation", required=True, help="验收记录文件或一句话结果")
    d.add_argument("--notes")
    d.add_argument("--root", help="默认写入当前项目 .design-memory/")
    d.add_argument("--confirm", action="store_true")
    d.set_defaults(f=cmd_deposit)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
