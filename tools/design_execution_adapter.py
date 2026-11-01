# -*- coding: utf-8 -*-
"""Keep designer judgment while routing Figma execution through the bundled adapter."""
import re


def adapt_execution(text, filename):
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text = text.replace('还是需要同步进 Figma', '还是先在 Figma 完成设计后还原 Demo')
        text = text.replace('还是需要进 Figma', '还是先在 Figma 完成设计后还原 Demo')
        text = text.replace('2. `python3 scripts/component_recipe.py copy', '2. 仅本地组件代码路线执行 `python3 scripts/component_recipe.py copy')
        text = text.replace('5. 写出完整的 `<任务目录>/design-decisions.md`，并运行', '5. 写出完整的 `<任务目录>/design-decisions.md`；仅本地组件代码路线运行')
        text = text.replace('返回 `"passed": true` 后才允许进入工具制作！', '返回 `"passed": true`。Figma 路线把配方结构、主题参数和真实素材引用纳入设计任务包，检查目标组件/变量与素材可访问性，不以本地 CSS 已生成作为 Figma 开工条件。')
        start = text.index('   - **路线 A｜')
        end = text.index('   - **路线 B｜', start)
        text = text[:start] + '''   - **路线 A｜UI / 产品界面**
     - 先读取同包 [Figma 执行入口](../fusion-figma-workflow/SKILL.md)的初始化部分，复用配置、目标和有效决定。已有本产品 Figma 主稿或已选择 Figma 时，先在指定 Figma 中完成设计，再按同版 Dev Mode / MCP 上下文还原 Demo；竞品参考链接不触发此默认。
     - 设计专家负责交互、风格、组件/真实素材、提示词和 QA0；Figma 执行模块负责工具配置、文件边界、实际生成/编辑、证据和还原。已有页用 Computer Use 精修；需要生成的新增整页用实际可用的 Figma Agent 后串行精修，不为局部修改强制生成。
     - 本地配方 CSS、素材路径和代码不会自动传入 Figma Agent。将参数、真实素材及组件映射显式带入任务包，核验实际画布；不能只传风格词，也不能把整屏位图当作可编辑 UI 稿。
     - 用户明确选择本地代码路线时，复用组件、主题与真实素材制作高保真页面并执行适用脚本。选定 Figma 但工具缺项时引导配置，不静默改成本地页面。
     - HTML 转 Figma 仅在用户明确选择、实际转换能力可用时采用；核验可编辑图层、组件、素材和版本，不承诺一键转换已实现或已验证。
''' + text[end:]
        text = text.replace('**必跑调库核验脚本（防止“只看不用、自己瞎画”）**', '**按制作载体核验真实调库（防止“只看不用、自己瞎画”）**')
        text = text.replace('- `python3 scripts/verify_library_usage.py <任务目录>', '- 本地组件代码路线运行 `python3 scripts/verify_library_usage.py <任务目录>')
        text = text.replace('   - 凡产出 HTML/代码界面，交付前还必须运行：', '   - Figma 原生稿核对实际组件实例、Variables / Styles、字体、真实素材及同版截图，记录证据；CSS 文件不作为原生设计稿的门槛。按稿还原复用既有项目组件时，核验真实组件/Token映射，不强造配方 CSS。\n   - 凡产出 HTML/代码界面，交付前还必须运行适用的检查，工具不适配时用等价实测并记录原因，不能把未检查写成通过：')
    if filename == 'methods-tool-routing.md':
        text = re.sub(r'^   - \*\*产出是 UI / 产品界面.*$', '   - **产出是 UI / 产品界面**：先按同包 [Figma 执行入口](../fusion-figma-workflow/SKILL.md)初始化与分流；已有本产品 Figma 主稿或已选 Figma 时，先生成/精修设计主稿，再由同版 Dev Mode / MCP 还原 Demo。已明确选择本地代码时才走本地组件路线。HTML 转 Figma 仅在显式选择且实际可用时采用，不作为默认承诺。设计参数、组件结构和真实素材须按目标载体实际应用并核验，不能用整屏位图充当可编辑 UI。', text, flags=re.M)
        text = re.sub(r'^7\. 工具不可用时.*$', '7. 素材工具可换用等效渠道；用户已选择 Figma 或已有本产品主稿时，缺失执行能力先按同包工作流引导恢复，不自行改成本地独立设计。交付载体变更需要明确决定。未检查、占位或近似产物不冒充正式交付。', text, flags=re.M)
        text = text.replace('## TR3 UI 设计：Figma 正式主稿', '## TR3 UI 设计：按已定路线制作与核验')
        text = text.replace('进入 Figma UI 前先按', '进入 UI 制作前先按')
        text = text.replace('- 正式 UI 以 Figma 文件、页面、Frame/组件/变量和准确版本为主稿。', '- 已选择 Figma 或已有本产品设计主稿时，以指定文件、页面、Frame/组件/变量和准确版本为主稿；本地路线记录对应代码与预览版本。')
        text = text.replace('- 所有界面视觉在 Figma 完成，包括颜色、字体、间距、密度、图标、插画、图片裁切和状态表现。', '- Figma 路线在主稿完成颜色、字体、间距、密度、图标、图片裁切及状态；已有页直接精修，新增整页按需生成后精修，再还原 Demo。具体执行、配置及授权见同包 [工作流](../fusion-figma-workflow/SKILL.md)。本地路线沿用组件与素材要求。')
    if filename == 'methods-visual.md':
        text = re.sub(r'^\| \*\*1\. UI / 产品界面.*$', '| **1. UI / 产品界面** | 先按 [Figma 执行工作流](../fusion-figma-workflow/SKILL.md)初始化：已有本产品 Figma 主稿或已选择 Figma时，设计专家准备交互/风格/真实素材任务包，旧页 Computer Use 精修，新增整页按需 Figma Agent 生成后精修；画布核验后按同版 Dev Mode / MCP 还原 Demo。用户明确选择本地代码时才用配方、主题与素材制作本地页面。 | 本地 CSS 与文件不会自动进入 Figma Agent，必须显式传递参数、素材及组件映射并检查画布。HTML 转 Figma 为显式且实际可用的可选路线，不是默认已实现能力。 |', text, flags=re.M)
    if filename == 'methods-ui.md':
        text = re.sub(r'^正式 UI 方案按.*$', '正式 UI 方案按 [methods-tool-routing.md](methods-tool-routing.md) `TR3` 与 [methods-visual.md](methods-visual.md) `VT` 分流。制作载体由同包 [Figma执行工作流](../fusion-figma-workflow/SKILL.md)恢复或收集：已有本产品Figma主稿或已选Figma时，先在Figma设计、精修，再还原Demo；B端或只换文案也不自动改变此路线。明确选择本地代码时复用组件与配方。UI与界面视觉组成同一分支，不固定另开视觉阶段。', text, flags=re.M)
    if filename == 'methods-close.md':
        text = text.replace('全部界面视觉以 Figma UI 主稿为准', 'Figma 路线的界面视觉以当前有效 Figma UI 主稿为准，经同包执行工作流完成设计后还原 Demo；本地路线以已明确选择的代码与预览版本为准')
        text = text.replace('（强制运行 `scripts/verify_library_usage.py`）', '（按实际制作载体检查）')
        text = text.replace('交付前必须运行 `python3 scripts/verify_library_usage.py', '本地组件代码路线交付前必须运行 `python3 scripts/verify_library_usage.py')
        text = text.replace('    - 已通过 `component_recipe.py copy`', '    - 仅本地组件代码路线：已通过 `component_recipe.py copy`')
        anchor = '- [ ] **3. 组件库/素材库真调核验与图标资产标准'
        start = text.index(anchor)
        text = text[:start] + text[start:].replace('\n', '\n  - Figma 原生稿以实际组件实例、变量/样式、字体、真实素材、截图与版本为证据，不要求先生成 recipes.css/theme.css；按稿还原复用项目组件时核对组件/Token映射。缺少适用实测证据不能判通过。\n', 1)
    return text
