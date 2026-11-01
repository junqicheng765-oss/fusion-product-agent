#!/usr/bin/env python3
"""按设计阶段列出资源 adapter，并查询 ARIA APG。"""
import argparse, json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resource-adapters")


def registry():
    return json.load(open(os.path.join(ROOT, "registry.json"), encoding="utf-8"))


def cmd_list(a):
    ads = registry()["adapters"]
    if a.stage:
        ads = [x for x in ads if a.stage in x.get("stage", []) or "all" in x.get("stage", [])]
    print("检索顺序：内部资产 → 本地预设 → 可自动调用 → 已授权 MCP → 参考链接")
    print(registry()["rule"])
    for x in ads:
        print(f"  [{x['priority']}] {x['id']:20} {x['mode']:12} {x['capability']:10} 阶段={','.join(x.get('stage', []))}")
        if x.get("fallback"):
            print(f"       失败则：{x['fallback'][:80]}")


def cmd_show(a):
    for x in registry()["adapters"]:
        if x["id"] == a.id:
            print(json.dumps(x, ensure_ascii=False, indent=2))
            return
    sys.exit("没有这个 adapter")


def cmd_apg(a):
    data = json.load(open(os.path.join(ROOT, "aria-apg.json"), encoding="utf-8"))
    q = (a.pattern or "").lower()
    hits = [p for p in data["patterns"] if q in p["id"] or q in p["use"]]
    if not hits:
        print("可用模式：", ", ".join(p["id"] for p in data["patterns"]))
        return
    for p in hits:
        print(f"{p['id']:16} {p['use']}  {p['url']}")


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("list"); l.add_argument("--stage", choices=["research", "flow", "interaction", "ui", "asset", "motion", "close"]); l.set_defaults(f=cmd_list)
    s = sp.add_parser("show"); s.add_argument("id"); s.set_defaults(f=cmd_show)
    g = sp.add_parser("apg"); g.add_argument("pattern", nargs="?"); g.set_defaults(f=cmd_apg)
    a = p.parse_args(); a.f(a)


if __name__ == "__main__":
    main()
