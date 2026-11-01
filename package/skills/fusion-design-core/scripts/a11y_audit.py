#!/usr/bin/env python3
"""用 axe-core 做无障碍自动检测。优先 npx @axe-core/cli，否则用无头 Chrome 注入 CDN 脚本。

  python3 a11y_audit.py page.html
  python3 a11y_audit.py https://localhost:3000
"""
import argparse, html, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from urllib.parse import urlparse

CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium"]
AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js"


def run_npx(target):
    try:
        proc = subprocess.run(
            ["npx", "--yes", "@axe-core/cli@4.10.3", target, "--stdout", "--exit"],
            capture_output=True, text=True, timeout=90,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if proc.returncode in (0, 1) and proc.stdout.strip().startswith("{"):
        return json.loads(proc.stdout)
    if proc.returncode in (0, 1) and "[" in proc.stdout:
        return {"raw": proc.stdout, "passed": proc.returncode == 0}
    return None


def run_chrome(target):
    chrome = next((c for c in CHROME if os.path.exists(c)), None)
    if not chrome:
        return None
    is_url = urlparse(target).scheme in {"http", "https"}
    if is_url:
        src = f"<script src='{AXE_CDN}'></script><script>axe.run().then(r=>{{const s=document.createElement('script');s.id='__axe__';s.type='application/json';s.textContent=JSON.stringify(r);document.body.appendChild(s);}});</script>"
        # can't inject into remote easily via dump-dom of remote after our script...
        # use data url wrapper? skip remote without npx
        return {"error": "远程 URL 请安装 Node 后用 npx @axe-core/cli，或先保存为本地 HTML"}
    raw = Path(target).read_text(encoding="utf-8")
    inject = f"<script src='{AXE_CDN}'></script><script>window.addEventListener('load',()=>axe.run().then(r=>{{const s=document.createElement('script');s.id='__axe__';s.type='application/json';s.textContent=JSON.stringify({{violations:r.violations.map(v=>({{id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.length}})),passes:r.passes.length}});document.body.appendChild(s);}}));</script>"
    html_doc = raw.replace("</body>", inject + "</body>") if "</body>" in raw else raw + inject
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=str(Path(target).parent), delete=False, encoding="utf-8") as t:
        t.write(html_doc)
        tp = Path(t.name)
    try:
        proc = subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000", "--dump-dom", f"file://{tp.resolve()}"],
            capture_output=True, text=True, timeout=30,
        )
        m = re.search(r'<script id="__axe__" type="application/json">(.*?)</script>', proc.stdout, re.S)
        if not m:
            return {"error": "未能读取 axe 结果（可能被离线环境拦住 CDN）。请安装 Node 后重试。"}
        return json.loads(html.unescape(m.group(1)))
    finally:
        tp.unlink(missing_ok=True)


def summarize(data):
    if not data or data.get("error"):
        return data
    viol = data.get("violations") or []
    if isinstance(viol, list) and viol and isinstance(viol[0], dict):
        serious = [v for v in viol if v.get("impact") in {"critical", "serious"}]
        return {
            "passed": len(serious) == 0,
            "serious_or_critical": serious,
            "other": [v for v in viol if v not in serious],
            "passes_count": data.get("passes", 0),
        }
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    a = ap.parse_args()
    target = a.target
    if not urlparse(target).scheme and not Path(target).exists():
        sys.exit("找不到文件 " + target)
    data = run_npx(target if urlparse(target).scheme else str(Path(target).resolve()))
    if data is None:
        data = run_chrome(target)
    report = summarize(data) if data else {"error": "axe-core 不可用"}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if isinstance(report, dict) and report.get("passed") is False:
        sys.exit(1)
    if report.get("error"):
        sys.exit(2)


if __name__ == "__main__":
    main()
