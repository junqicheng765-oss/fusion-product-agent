#!/usr/bin/env python3
"""Import a fixed designer snapshot, preserving all assets and recording adaptations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from design_execution_adapter import adapt_execution
from product_stage_adapter import adapt_product_stage

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
    text = adapt_execution(text, filename)
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text += '\n\n## 同包集成说明\n\n本模块负责设计研究、交互、风格、素材、提示词和QA0专业判断；工具配置、目标绑定、Figma生成/精修与Dev Mode还原执行同包 [fusion-figma-workflow](../fusion-figma-workflow/SKILL.md)。初始化只读核对可先于视觉选择，实际制作仍遵守有效设计决定。工具名称不是能力或权限证明，不把自动安装描述当成全局配置授权。已有有效选择或委托直接复用，缺少外部工具不静默更换设计主稿。\n'
    return adapt_product_stage(text, filename).encode('utf-8')


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
    (ROOT / 'package/design-source.json').write_text(json.dumps({'repository': 'https://github.com/savvydd/jq-product-agent', 'branch': 'feat/design-handoff-contract', 'commit': COMMIT, 'adaptations': 'Isolated Skill names and parent references; remove old D/E wrapper alias. Preserve designer methods, style decisions and QA0; route Figma execution to bundled workflow, remove mandatory HTML-first and Figma-Agent bans, scope CSS-only gates to local component code. Bind design discovery, intake and routing to the product goal/scope evidence or explicit delegation; design is a stage, not a replacement product entry. No script, component or asset removed. Product-stage wrapper skills are not imported.', 'files': files}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'imported': len(files), 'adapted': sum(f['adapted'] for f in files), 'commit': COMMIT}))


if __name__ == '__main__':
    main()
