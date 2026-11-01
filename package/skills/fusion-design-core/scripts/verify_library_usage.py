#!/usr/bin/env python3
"""
Design Thinking OS — Library & Asset Execution Gate (verify_library_usage.py)

Prevents the agent from "reading about libraries or running `show` without actually
copying component recipes, running IconScout retrieval, or generating/fetching avatar images."

Usage:
  python3 scripts/verify_library_usage.py <task_dir> [--require-avatars N] [--require-photos]

Exit code 0 if all required libraries were actually executed and produced files on disk;
Exit code 1 otherwise.
"""
import argparse
import json
import sys
from pathlib import Path


def verify(task_dir: Path, require_avatars: int = 0, require_photos: bool = False) -> dict:
    issues = []
    if not task_dir.exists():
        return {
            "passed": False,
            "task_dir": str(task_dir),
            "issues": [{"code": "TASK_DIR_MISSING", "severity": "FAIL", "message": f"目录不存在：{task_dir}"}],
        }

    # 1. Check that component_recipe.py copy & style_preset.py were actually executed (not just `show`)
    recipes_css = list(task_dir.rglob("recipes.css"))
    theme_css = list(task_dir.rglob("theme.css"))
    if not recipes_css:
        issues.append({
            "code": "RECIPES_NOT_COPIED",
            "severity": "FAIL",
            "message": "未找到 recipes.css！不能只用 `component_recipe.py show` 看一眼就自己瞎画，必须运行 `python3 scripts/component_recipe.py copy <配方ID...> --to <目录> --preset <风格编号>` 实际导出并复用配方实现。",
        })
    if not theme_css:
        issues.append({
            "code": "STYLE_PRESET_NOT_EXPORTED",
            "severity": "FAIL",
            "message": "未找到 theme.css！必须运行 `python3 scripts/style_preset.py export <风格编号> --format css -o <目录>/theme.css`（或带 `--preset` 运行 `component_recipe.py copy`）。",
        })

    # 2. Check that IconScout was actually called and downloaded assets to disk
    all_files = [p for p in task_dir.rglob("*") if p.is_file()]
    iconscout_files = [
        p for p in all_files
        if p.name.startswith(("3d-", "icon-", "illustration-", "lottie-"))
        or "iconscout" in p.name.lower()
    ]
    if not iconscout_files:
        issues.append({
            "code": "ICONSCOUT_NOT_EXECUTED",
            "severity": "FAIL",
            "message": "未检测到任何 IconScout 下载文件（如 `3d-*.png` / `icon-*.svg` / `illustration-*.png`）！严禁跳过 IconScout 自己瞎画或去 GitHub 下老旧 SVG-cards，必须运行 `python3 scripts/iconscout.py search -q \"<英文关键词>\" -a <icon|3d|illustration|lottie> -d <目录>/assets`。",
        })

    # 3. Check banned third-party clipart workarounds (e.g., htdebeer/SVG-cards)
    banned = [p for p in all_files if "svg-cards" in str(p).lower() or "htdebeer" in str(p).lower()]
    if banned:
        issues.append({
            "code": "BANNED_CLIPART_CARDS",
            "severity": "FAIL",
            "message": f"检测到禁止使用的第三方老旧剪贴画扑克（{banned[0].name}）！扑克牌必须使用内置 `playing-card` + `hand-fan` 配方与 IconScout / 风格锁定资产，禁止从 GitHub 乱扒 SVG-cards。",
        })

    # 4. Check avatars if required (blocks name-initial text circle fallback)
    if require_avatars > 0:
        avatar_imgs = [
            p for p in all_files
            if "avatar" in p.name.lower() and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
        ]
        if len(avatar_imgs) < require_avatars:
            issues.append({
                "code": "AVATARS_MISSING_OR_TEXT_FALLBACK",
                "severity": "FAIL",
                "message": f"当前任务需要至少 {require_avatars} 张真实头像图片文件（`avatar*.png/jpg`），实际只找到 {len(avatar_imgs)} 张！严禁用“名字首字圆圈（如 周/林/宁/我）”回退充数；必须先搜 IconScout 并过文化风格判断门，不匹配则按统一母体风格前缀成套生成头像图片。",
            })

    # 5. Check real photography if required
    if require_photos:
        real_imgs = [
            p for p in all_files
            if ("real-images" in str(p) or p.name.startswith(("unsplash-", "wikimedia-", "pixabay-", "openverse-", "pexels-")))
            and p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
        ]
        if not real_imgs:
            issues.append({
                "code": "REAL_IMAGE_LIBRARY_NOT_EXECUTED",
                "severity": "FAIL",
                "message": "未检测到 `real_image.py` 下载的真实摄影配图！真实风景/城市/建筑场景必须运行 `python3 scripts/real_image.py search` 并 `get` 到本地。",
            })

    return {
        "passed": len(issues) == 0,
        "task_dir": str(task_dir),
        "found": {
            "recipes_css": [str(p) for p in recipes_css],
            "theme_css": [str(p) for p in theme_css],
            "iconscout_files_count": len(iconscout_files),
        },
        "issue_count": len(issues),
        "issues": issues,
    }


def main():
    ap = argparse.ArgumentParser(description="Verify that design-thinking-os libraries were actually executed")
    ap.add_argument("task_dir", help="Task working directory")
    ap.add_argument("--require-avatars", type=int, default=0, help="Minimum number of avatar image files required")
    ap.add_argument("--require-photos", action="store_true", help="Require real_image.py photography downloads")
    args = ap.parse_args()
    rep = verify(Path(args.task_dir), args.require_avatars, args.require_photos)
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    if not rep["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
