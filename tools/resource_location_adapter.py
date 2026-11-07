"""Reproduce MR1 localization and cross-Skill references after every import.

Only owned entry overlays are stored; designer libraries and methods remain upstream.
Unknown translation inputs fail rather than silently overwriting new upstream work.
"""
import hashlib
import json
from pathlib import Path
import re

OVERLAYS = Path(__file__).resolve().parent / 'overlays/mr1'
LINK = re.compile(r'\[([^\]]+)\]\((?:\.\./)+(fusion-[^/()]+)/([^()]+)\)')


def resource_references(text):
    return LINK.sub(lambda m: m[1] + '（技能 `' + m[2] + '` 内的 `' + m[3] + '`）', text)


def equivalent_fragment(fragment, text):
    compact = lambda value: re.sub(r'\s+', '', resource_references(value))
    return compact(fragment) in compact(text)


def adapt_resources(text, filename):
    text = resource_references(text)
    if filename != 'SKILL.md':
        return text
    name = re.search(r'^name: (fusion-[\w-]+)$', text, re.M)
    if not name:
        return text
    name = name[1]
    if name in ('fusion-design-impeccable', 'fusion-design-ui-ux-pro-max'):
        metadata = json.loads((OVERLAYS / 'metadata.json').read_text())[name]
        overlay = (OVERLAYS / (name + '.md')).read_text()
        if hashlib.sha256(overlay.encode()).hexdigest() != metadata['overlay_sha256']:
            raise ValueError('Localized overlay changed without provenance update: ' + name)
        if text != resource_references(overlay):
            digest = hashlib.sha256(text.encode()).hexdigest()
            if digest != metadata['input_sha256']:
                raise ValueError('Unknown translation input; review upstream changes: ' + name)
        return resource_references(overlay)
    if name == 'fusion-design-core':
        metadata = (OVERLAYS / 'core-metadata.txt').read_text()
        text = re.sub(r'\A---\n.*?\n---', lambda _: '---' + metadata + '---', text, count=1, flags=re.S)
        text = text.replace('# 设计师完整工作流（Design Thinking OS）', '# 设计师完整工作流（设计思维操作系统）')
    if name in ('fusion-product-agent', 'fusion-design-core', 'fusion-figma-workflow') and '## 技能与资源定位\n' not in text:
        rule = '## 技能与资源定位\n' + (OVERLAYS / 'resource-rule.md').read_text()
        if name == 'fusion-design-core':
            rule += '执行本文及方法文件中 `scripts/...` 的脚本示例时，将脚本路径展开为本技能实际安装目录的绝对路径，例如 `python3 "<skill-base-dir>/scripts/style_preset.py" ...`。当前工作目录保持为用户的业务项目，产物路径按任务显式指定；`<skill-base-dir>` 始终指脚本所属技能的目录。\n\n'
        match = re.search(r'^## ', text, re.M)
        if not match:
            raise ValueError('No section anchor for resource-location contract: ' + name)
        text = text[:match.start()] + rule + text[match.start():]
    return text
