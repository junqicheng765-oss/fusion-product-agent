#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore the original JQ 1.1.5 execution workflow with local, bundled references."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'skills/jq-figma-workflow/SKILL.md': 'SKILL.md',
    'skills/jq-figma-workflow/references/figma-execution.md': 'references/figma-execution.md',
    'skills/jq-figma-workflow/references/design-to-demo.md': 'references/design-to-demo.md',
    'skills/tc-product-agent/references/26-设计能力初始化与复用.md': 'references/initialization.md',
    'skills/tc-product-agent/references/18-Figma执行前核对卡.md': 'references/preflight.md',
    'skills/tc-product-agent/references/15-设计交付与Figma回传规范.md': 'references/task-package.md',
    'skills/tc-product-agent/references/24-Demo文案与交互复核.md': 'references/demo-review.md',
}


def adapt(text, target):
    main = target == 'SKILL.md'
    local = 'references/' if main else ''
    parent = '../fusion-product-agent/' if main else '../../fusion-product-agent/'
    core = '../fusion-design-core/' if main else '../../fusion-design-core/'
    replacements = {
        'name: jq-figma-workflow': 'name: fusion-figma-workflow',
        'JQ Product Agent': 'Fusion Product Agent',
        '# JQ Figma': '# Fusion Figma',
        '../tc-product-agent/references/15-设计交付与Figma回传规范.md#4-设计任务包': local + 'task-package.md',
        '../tc-product-agent/references/26-设计能力初始化与复用.md': local + 'initialization.md',
        '../tc-product-agent/references/18-Figma执行前核对卡.md': local + 'preflight.md',
        '../../tc-product-agent/references/18-Figma执行前核对卡.md': 'preflight.md',
        '../tc-product-agent/references/27-流程导航与按需确认.md#21-question-弹出交互合同': parent + 'references/dialogue-and-state.md',
        '../tc-product-agent/references/27-流程导航与按需确认.md': parent + 'references/dialogue-and-state.md',
        '27-流程导航与按需确认.md#21-question-弹出交互合同': parent + 'references/dialogue-and-state.md',
        '26-设计能力初始化与复用.md': 'initialization.md',
        '../../jq-figma-workflow/SKILL.md': '../SKILL.md',
        '[jq-figma-workflow]': '[fusion-figma-workflow]',
        '[Demo 质量 Skill](../../jq-demo-quality/SKILL.md)': '[Demo 文案与交互复核](demo-review.md)，并由同包设计专家执行 [QA0](../../fusion-design-core/methods-close.md)',
        '初始化不增加 A–F 业务阶段': '初始化是设计执行准备，不增加产品业务阶段',
        '按 `18`': '按[执行前核对卡](preflight.md)',
        '及 `18` 核对卡': '及[执行前核对卡](preflight.md)',
        '及 `15` §2.2 的页面分流': '及[执行手册](figma-execution.md)的页面分流',
        '引用 25 的基线摘要及版本': '引用本任务产品类型与设计基线摘要及版本',
        '当前 `01` 版本': '当前产品正文版本',
        '`01` 版本': '当前产品正文版本',
        '{01、SC/UC、R、UX、AC、DesignTaskPackage 版本}': '{产品正文、SC/UC、R、UX、AC、DesignTaskPackage 版本}',
    }
    # Long paths must be replaced before their suffixes.
    for old in sorted(replacements, key=len, reverse=True):
        text = text.replace(old, replacements[old])
    text = text.replace('D1', '执行就绪').replace('D2', '设计回审')
    text = text.replace('D 可只覆盖代表链路，E 增量扩展', '可先覆盖代表链路，再增量扩展')
    text = text.replace('D 先形成代表链路所需的 Figma 页面/状态，再还原流程 Demo；E 扩展时先更新主稿，再同步 Demo。', '代表链路先形成所需的 Figma 页面/状态，再还原流程 Demo；模块扩展时先更新主稿，再同步 Demo。')
    text = text.replace('在 D/E 的 Demo 展示与交付前', '在当前范围的 Demo 展示与交付前')
    text = text.replace('- D 代表页面送审前', '- 代表页面送审前')
    text = text.replace('- E 随模块与状态扩展', '- 随模块与状态扩展')
    text = text.replace('- F 核对交接 Demo', '- 正式交接时核对 Demo')
    if main:
        text = text.replace('主产品 Agent 负责当前事实、业务规则、体验/视觉判断、提示词和验收要求。', '主产品 Agent 负责当前事实、业务规则、范围和业务验收；同包 [设计专家](../fusion-design-core/SKILL.md)负责交互、风格、组件/素材、提示词及 QA0。')
        text = text.replace('依赖同包合同', '使用同包产品/设计接口与本目录执行手册')
        text = text.replace('执行前读取 [生成与直接精修手册]', '专业设计推导与风格选择沿用设计专家的方法和有效决定，不由执行模块重新访谈或自行定风格。\n\n执行前读取 [生成与直接精修手册]')
        text = text.replace('由主 Agent 通过 Question 获取选择或复用明确委托，再展开。', '这是可视化候选，不替代设计专家要求的制作前方向选择；由主 Agent 通过 Question 获取选择或复用明确委托，再展开。')
        text = text.replace('设计形成后核对本次页面', '设计形成后由设计专家按 [QA0](../fusion-design-core/methods-close.md)核对，并核对本次页面')
        text += '\nDemo 交付前自动执行 [文案与交互专项复核](references/demo-review.md)，无须使用者额外提出。流程位置与下一动作只在对话/工作记录展示，不放进最终用户页面。\n'
        text += '\n## 存量系统的资产延续\n\n已有本产品正式Figma文件是迭代设计基线，不只取色参考。包括新增页面在内，优先复用其组件实例、Variables / Styles、字体、布局、图标和状态惯例，不重新生成三套风格。确需新增组件或偏离基线时说明缺口、范围与影响，仅对实质性设计取舍收集决定。按[执行手册](references/figma-execution.md)记录复用/新增资产与设计—代码映射；视觉延续不自动证明代码、依赖和真实系统已可直接接入。\n'
    if target.endswith('figma-execution.md'):
        text = text.replace('## 新整页生成后精修', '''## 存量设计资产与下游可接入性

在修改范围和必要相邻页面中识别当前有效组件、Variables / Styles、字体、布局/密度、图标、素材及状态规范，记录对应节点/库和版本。新增整页也沿用这套基线，不能因新页面就重选风格、重造全局主题或用通用模板覆盖既有设计。

优先复用组件实例并继承变量，不为生成方便随意拆散实例、重建变量或修改全局组件。确需新增组件/变体/状态时，在允许范围创建并说明原因、命名和与既有资产的关系；变更共享组件须回查受影响页面，重大偏离由主Agent收集决定。

生成任务显式带入可访问的组件/变量、真实素材和代表页面，生成后核对实际实例/样式和画布，不凭提示词“沿用风格”判定通过。回传沿用/新增/变更清单、准确节点与版本，以及与现有代码组件/Token的映射；不能映射的项标明接入工作，不保证设计稿直接生成即可上线。

## 新整页生成后精修''')
    if target.endswith('task-package.md'):
        text = text.replace('- 视觉/组件基线：', '- 资产延续与实现映射：<复用的组件实例/变量/样式/字体/布局/图标及版本；本次新增或变更项；现有代码组件/Token对应与未验证接入项；存量新增页面不重选全局风格>。\n- 视觉/组件基线：')
    if target.endswith('task-package.md'):
        text = '# 设计执行任务包\n\n沿用当前项目任务文档或以下 Markdown 骨架，产品正文是规则唯一来源；设计专家补齐交互、风格、组件/素材与提示词，执行模块记录真实工具结果。\n\n' + text.split('## 4. 设计任务包\n', 1)[1].split('## 5. 页面交互规格', 1)[0]
    if target.endswith('demo-review.md'):
        text = re.sub(r'^主 Agent 负责安排与汇总，同包.*$', '主 Agent 安排与汇总，同包 [设计专家](../../fusion-design-core/SKILL.md)执行 QA0 与下列专项复核；业务含义由产品主线按[产品方法](../../fusion-product-agent/references/product-method.md)及相关正式能力定义判断。它属于已授权制作与修正，不新增人工审批。制作完成 → 专项复核 → 修正与复验 → 展示给人；有阻断时仅交付边界明确的草稿或不受影响部分。', text, flags=re.M)
        text = re.sub(r'^先使用 \[P3.*$', '文案按同包[语义与表达能力](../../fusion-product-agent/knowledge/product-capability-model/standards/P3/model.md)及相关定义判断，结合[设计文案与控件方法](../../fusion-design-core/methods-ui.md)；规则含义引用当前产品正文，不重复加载全部能力。', text, flags=re.M)
        text = re.sub(r'^先使用 \[P5.*$', '交互按同包[交互与反馈能力](../../fusion-product-agent/knowledge/product-capability-model/standards/P5/model.md)与[交互设计方法](../../fusion-design-core/methods-interaction.md)核验；专业设计建议与业务规则冲突时回产品主线处理，不自行改写已确认规则。', text, flags=re.M)
        text = re.sub(r'^严重度沿用.*$', '严重度按[产品评审与交接](../../fusion-product-agent/references/review-and-handoff.md)和设计 QA0 处理。阻断/重大问题，或核心/关键风险交互缺少动态证据时，对应范围不得标为“复核通过”；可交付明确标注的待修/待验证草稿。品质问题暂缓须说明理由、责任和影响，不藏在总体通过中。', text, flags=re.M)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-plugin-root', required=True, type=Path)
    args = parser.parse_args()
    files = []
    for source, target in FILES.items():
        raw = (args.source_plugin_root / source).read_bytes()
        data = adapt(raw.decode('utf-8'), target).encode('utf-8')
        dest = ROOT / 'package/skills/fusion-figma-workflow' / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        files.append({'source': source, 'destination': str(dest.relative_to(ROOT / 'package')), 'source_sha256': hashlib.sha256(raw).hexdigest(), 'sha256': hashlib.sha256(data).hexdigest(), 'adapted': True, 'excerpt': target.endswith('task-package.md')})
    (ROOT / 'package/figma-source.json').write_text(json.dumps({'source': 'JQ Product Agent 1.1.5', 'repository': 'https://github.com/junqicheng765-oss/jq-product-agent', 'adaptations': 'Restore execution, configuration reuse, task/preflight, generation, Computer Use, Dev Mode reconstruction and copy/interaction review. Relink all dependencies within this package; design judgment and QA0 belong to designer core, product facts to fusion product entry; no legacy product-stage wrappers imported.', 'files': files}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'imported': len(files), 'source': 'JQ Product Agent 1.1.5'}))


if __name__ == '__main__':
    main()
