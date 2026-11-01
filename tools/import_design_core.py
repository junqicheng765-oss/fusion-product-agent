#!/usr/bin/env python3
"""Import a fixed designer snapshot, preserving all assets and recording adaptations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

COMMIT = '6dcc771bb7b5d0c5f4d2ca25fc13994af12c73a1'
MAPPING = {'design-thinking-os': 'fusion-design-core', 'impeccable': 'fusion-design-impeccable', 'ui-ux-pro-max': 'fusion-design-ui-ux-pro-max'}
ROOT = Path(__file__).resolve().parents[1]


def adapt(data, suffix, filename):
    if suffix not in ('.md', '.yaml', '.yml'):
        return data
    text = data.decode('utf-8')
    for old, new in MAPPING.items():
        text = re.sub(r'(?m)^name: ' + re.escape(old) + r'$', 'name: ' + new, text)
        text = text.replace('$' + old, '$' + new)
        text = text.replace('skills/' + old + '/', 'skills/' + new + '/')
    text = text.replace('$tc-product-agent', '$fusion-product-agent')
    text = text.replace('`jq-product-agent`', '`fusion-product-agent`')
    text = text.replace('`tc-product-agent`', '`fusion-product-agent`')
    text = text.replace('通过 tc-product-agent 插件', '通过 fusion-product-agent 插件')
    text = text.replace('## JQ Product Agent integration', '## Fusion Product Agent integration')
    text = text.replace('invokes this bundled Skill in D/E', 'invokes this bundled Skill for design work')
    # Align two inherited blanket Figma statements with the author's latest HTML-first route.
    if filename == 'methods-close.md':
        text = text.replace('全部界面视觉以 Figma UI 主稿为准', '界面视觉以本轮已确认的交付载体及准确版本为准；需要 Figma 主稿时按最新工具路线从高保真组件页面转换并核对，按已有正式稿还原时仍以该稿为依据')
    if filename == 'methods-tool-routing.md':
        text = text.replace('## TR3 UI 设计：Figma 正式主稿', '## TR3 UI 设计：高保真组件页面与按需 Figma 主稿')
        text = text.replace('进入 Figma UI 前先按', '进入 UI 制作前先按')
        text = text.replace('- 正式 UI 以 Figma 文件、页面、Frame/组件/变量和准确版本为主稿。', '- 最终载体按 TR0 合同确定；需要 Figma 正式主稿时，记录文件、页面、Frame/组件/变量和准确版本。')
        text = text.replace('- 所有界面视觉在 Figma 完成，包括颜色、字体、间距、密度、图标、插画、图片裁切和状态表现。', '- 新建界面按本文件核心规则与主入口第三步，先在本地组件页面完成颜色、字体、间距、密度、图标、插画、图片裁切和状态表现；需要 Figma 时转换并核对，不改回 Figma 云端 Agents 重画。')
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text += '\n\n## 同包集成说明\n\n本模块沿用作者最新主入口的开工门禁及第三步工具路线；细则中较早的概括不覆盖这两处明确要求。具体工具名称只表示能力目标，实际按宿主可用工具及权限调用，不把文档中的自动安装描述视为全局配置或账号授权。产品主线提供目标、领域规则与约束，设计推导和QA0由本模块负责。\n'
    return text.encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-repo', required=True, type=Path)
    args = parser.parse_args()
    files = []
    for old, new in MAPPING.items():
        prefix = 'plugins/tc-product-agent/skills/' + old + '/'
        names = subprocess.check_output(['git', '-C', str(args.source_repo), 'ls-tree', '-r', '--name-only', COMMIT, prefix], text=True).splitlines()
        for source in names:
            raw = subprocess.check_output(['git', '-C', str(args.source_repo), 'show', COMMIT + ':' + source])
            rel = Path('skills') / new / source[len(prefix):]
            dest = ROOT / 'package' / rel
            converted = adapt(raw, dest.suffix, dest.name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(converted)
            files.append({'source': source, 'destination': rel.as_posix(), 'source_sha256': hashlib.sha256(raw).hexdigest(), 'sha256': hashlib.sha256(converted).hexdigest(), 'adapted': converted != raw})
    (ROOT / 'package/design-source.json').write_text(json.dumps({'repository': 'https://github.com/savvydd/jq-product-agent', 'branch': 'feat/design-handoff-contract', 'commit': COMMIT, 'adaptations': 'Isolated Skill names and parent references; remove old D/E wrapper alias; align two inherited blanket Figma statements with latest author HTML-first route; clarify entrypoint precedence and host permissions. No script, component or asset removed. Product-stage wrapper skills are not imported.', 'files': files}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'imported': len(files), 'adapted': sum(f['adapted'] for f in files), 'commit': COMMIT}))


if __name__ == '__main__':
    main()
