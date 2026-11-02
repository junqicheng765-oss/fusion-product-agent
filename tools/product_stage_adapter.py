"""Keep imported design capabilities inside the Fusion product workflow."""


def insert_before(text, anchor, addition):
    if addition in text:
        return text
    if text.count(anchor) != 1:
        raise ValueError('Expected one product-stage insertion anchor: ' + anchor)
    return text.replace(anchor, addition + anchor, 1)


def replace_once(text, old, new):
    if new in text:
        return text
    if text.count(old) != 1:
        raise ValueError('Expected one product-stage replacement anchor: ' + old)
    return text.replace(old, new, 1)


def adapt_product_stage(text, filename):
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        begin = text.index('description: >-\n')
        end = text.index('\n---', begin)
        text = text[:begin] + '''description: >-
  Product/UI/visual design stage within Fusion Product Agent. Takes a product
  brief with traceable goals, scope and decisions or explicit delegation; researches
  interaction, selects visual direction, creates assets and runs design review (QA0).
  For vague new-product ideas, restore the product intake before making designs or
  demos. This capability does not replace the product workflow or decide user intent.''' + text[end:]
        text = insert_before(text, '## ⛔ 开工与分步硬门禁', '''## 产品主线先于设计

本模块是融合产品锤中的设计环节，产品主入口统一组织目标、领域需求、边界、方案、PRD和交接。先读取同包[产品启动条件](../fusion-product-agent/references/product-start.md)，核对本轮目标、核心范围、终点及其用户输入/既有决定/明确委托来源。只有产品名称或AI自行写出的候选画像、目标、流程，不算有效产品输入。

若目标或核心范围仍有改变方向的缺口，回到产品主线给出可理解的推荐并通过原生Question询问，等待必要答案；不得直接开展受影响的正式设计或Demo制作。设计研究可以支持讨论，不能替人决定为什么做和先做什么。直接调用本Skill也遵守此条件，不要求另启一个Agent。专业设计判断、调研和QA0继续按下述方法执行；已有有效输入、局部改动或明确委托按范围复用，不重做访谈。

''')
        text = replace_once(text,
            '2. **0→1 需求必须严格分【两轮】推进',
            '2. **产品启动条件已满足后的0→1设计需求，必须严格分【两轮】推进')
        text = replace_once(text,
            '### 第一步：看需求给到了什么程度，决定从哪切入（研究 → 竞品 → 流程 → 交互）',
            '### 第一步：核对产品输入有效后，再决定设计从哪切入（研究 → 竞品 → 流程 → 交互）')
        text = replace_once(text,
            '1. **0→1 需求第一轮怎么汇报与提问（先给出用研/竞品/交互方案，再请用户选视觉风格与确认交互）**：',
            '1. **产品目标与范围已有有效依据后，0→1设计第一轮怎么汇报与提问（先给出用研/竞品/交互方案，再请用户选视觉风格与确认交互）**：')
        text = replace_once(text,
            '   - 当用户给了一个 0→1 需求（如“给我做一个掼蛋”），**严禁第一轮什么都不分析就只抛一个空问题，更严禁一上来就直接宣布用什么视觉风格！**',
            '   - 如“给我做一个掼蛋”尚无产品目标和范围，先回产品主线给候选方向、推荐和关键问题；不能直接套用下面的风格问题。产品输入足够后，**严禁什么都不分析就只抛空问题，更严禁直接宣布视觉风格！**')
        text = insert_before(text, '## ⛔ 开工与分步硬门禁', '''## 流程位置与回传

本环节沿用[产品主线六阶段与设计四步骤](../fusion-product-agent/references/progress-navigation.md)。每次成果、修订或提问回复，最终首行保留产品第几/6阶段，设计中附设计第几/4步、当前模块及真实状态；结尾交代下一动作或用户所需选择。四步骤对应下文的研究/流程交互、视觉决策、制作、终审，不按回复次数推进。向产品主入口回传同样的信息，不因要求自然语言、隐藏方法代号而省略导航，也不增加人工审批。

''')
    elif filename == 'methods-intake.md':
        text = insert_before(text, '## 1. 提取任务事实', '''## 产品输入先决条件

先核对同包[产品启动条件](../fusion-product-agent/references/product-start.md)。产品主线负责校准用途、使用者/情境、核心范围与终点；设计不能把自行推导的这些内容写成用户决定。关键意图缺失时回传产品主线，以具体候选和推荐询问；已有有效依据、明确委托或局部任务直接复用。设计自身的分诊与专业研究继续执行，但不替代这个条件。

''')
        text = replace_once(text,
            '其余情况使用 `ASSUMPTION:` 推进，并写最小补证。',
            '产品启动条件成立后，其余普通可逆设计细节可使用 `ASSUMPTION:` 推进，并写最小补证；不能据此自行确定尚未校准的产品目标、目标用户和核心范围，也不能在等待必要答案时制作受影响的正式成品。')
    elif filename == 'methods-routing.md':
        text = insert_before(text, '## RT0 先定本轮终点', '''## 产品与设计路由的边界

本文件只路由产品主线中的设计工作，先复用[产品启动依据](../fusion-product-agent/references/product-start.md)。若缺少会改变方向的产品意图，回传产品主线补齐推荐与必要问答，不通过选择“测试就绪原型”或设置候选假设绕过。明确委托的探索性制作可以按其范围执行，不能把探索结论写成正式产品基线。

''')
    return text


def adapt_figma_product_stage(text):
    text = insert_before(text, '## 输入与职责', '''## 产品主线的执行前提

本模块是产品锤内部的设计执行能力，不是从一句产品想法直接生成正式设计的独立入口。实际生成、编辑或还原前，先核对同包[产品启动条件](../fusion-product-agent/references/product-start.md)及任务包的目标/范围来源、有效决定或明确委托。关键意图未定时回产品主线补齐；可以先只读核对工具和已有资产，不能借配置初始化直接开工。已有充分输入、精确还原或局部修改不重复访谈，明确授权的探索制作保留假设边界。

''')
    return insert_before(text, '## 输入与职责', '''## 执行位置回传

每次成果、修订、提问与回传按同包[流程位置展示](../fusion-product-agent/references/progress-navigation.md)保留产品第几/6阶段、适用的设计第几/4步、真实状态及下一动作。配置核对是设计准备，不把认证成功写成设计完成；生成、精修、Demo还原与复核分别如实记录。父任务汇总时同样保留导航，不能只交一个文件或结论让使用者猜下一步。

''')
