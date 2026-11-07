"""Keep imported design capabilities inside the Fusion product workflow."""
from resource_location_adapter import adapt_resources, equivalent_fragment, resource_references


def insert_before(text, anchor, addition):
    if equivalent_fragment(addition, text):
        return text
    if text.count(anchor) != 1:
        raise ValueError('Expected one product-stage insertion anchor: ' + anchor)
    return text.replace(anchor, addition + anchor, 1)


def replace_once(text, old, new):
    if equivalent_fragment(new, text):
        return text
    if text.count(old) != 1:
        normalized = resource_references(old)
        if text.count(normalized) == 1:
            return text.replace(normalized, resource_references(new), 1)
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
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text = insert_before(text, '## ⛔ 开工与分步硬门禁', '''## 文案与异常的承接职责

正式页面制作前，承接产品主线已编写审查的《界面文案基线》及版本、适用COPY ID和原文；执行技能 `fusion-product-agent` 内的 `references/product-copy.md`。U6的文案编写由该上游步骤完成，设计不另写最终文案，只核对呈现、理解和实际操作；改字建议回产品主线修订同一来源后同步。研究和交互推导可以先行，三套正式风格候选使用同一就绪文案。

异常按技能 `fusion-product-agent` 内的 `references/exception-layers.md` 承接共享规则、差异状态、异常ID与COPY引用；设计补页面位置、优先级、阻断、操作去向、输入保留与状态更新。不为每个技术触发新增页面，不省略真实不同的业务后果。QA0与实屏/动态复核仍执行。

''')
    elif filename == 'methods-ui.md':
        text = insert_before(text, '## U6', '''## 融合产品锤中的文案职责

本任务正式界面文字由产品主线按技能 `fusion-product-agent` 内的 `references/product-copy.md` 编写、审查和维护；设计承接同一《界面文案基线》。以下U6用于检查呈现和提出修改建议，不重复生成另一套最终文字；缺字、改字或页面变体返回产品主线更新基线。异常ID关联规则/状态并引用COPY ID，页面规则不复制可独立编辑的文案。适用方法和QA0不因此跳过。

''')
        text = replace_once(text,
            '**跳过**：正式文案冻结且本轮不得修改。',
            '**编写边界**：本包使用产品主线已审查就绪的文案，不在U6重新编写；实屏呈现和可用性检查继续执行。内容缺口或改字回产品文案步骤，无须另设逐句冻结审批。')
        text = replace_once(text,
            '**产出**：页面文案表。',
            '**产出**：文案基线/COPY引用、实屏呈现检查与修改建议；需要改字回产品主线维护同一基线，不另建最终文案表。')
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text = insert_before(text, '## ⛔ 开工与分步硬门禁', '''## 文案审查结果的可见回传

按技能 `fusion-product-agent` 内的 `references/product-copy.md` 的“文案审查摘要”回传：本轮文案基线/版本、复用或新审查的范围与证据、关键修改前后及理由（无变化如实说明）、内容/实屏/动态检查结论、阻断与下一动作。产品主线在最终可见回复保留本轮摘要；直接面向使用者时本模块展示。只改呈现不冒称改过文案，不把内部自检或保存文件当已向用户展示，不增加逐句审批。

''')
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text = insert_before(text, '## ⛔ 开工与分步硬门禁', '''## 正式设计交付约束

正式界面设计和还原读取技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md`。探索原型只验证指定问题，不默认先做也不自动升级成主稿；正式页面从结构、文案、内容、控件到状态都面向实际用户。使用就绪文案，讲解、评审备注与模拟控制留在协作说明。已有本产品Figma或已选Figma先完成主稿再按同版还原；明确本地路线可直接形成正式页面。QA0及文案/交互复核一并核对产物性质、用户视角、设计源版本和实际行为；回传检查结论、证据与未覆盖，不增加批准轮次。

''')
    elif filename == 'methods-routing.md':
        text = insert_before(text, '## RT0 先定本轮终点', '''## 正式交付与探索的路由依据

读取技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md`，在下方产出合同中标明探索原型、正式设计或按稿还原、有效源版本及本轮范围。探索原型可作为明确终点，不自动升级为正式主稿；正式设计不默认先做探索Demo。沿用既有有效风格与决定，按本轮范围完成设计，再按已约定路线还原可操作体验，QA0核对真实用户视角及源版本。

''')
    elif filename == 'methods-tool-routing.md':
        text = replace_once(text,
            '- [ ] UI 已先完成「存量延展 / 纯 B 端连接公开组件库 / C 端 0→1 风格库由 Agent 直接选定」三路分流；要画面的页面已在 Figma 里先出 AI 方向、再拼装成可编辑 Frame（只换文案、灰框、B 端、写明不验观感的，用 HTML/代码，并先用画面级配方）；UI 内写实配图先走 Real Image Library，无匹配或虚构才原位生图。',
            '- [ ] UI 已按既有风格/组件与有效选择分流，范围和产物性质明确；已有本产品Figma主稿或已选Figma先完成本轮可编辑设计，再按同版还原。B端、只改文案或探索灰框不自动改变既定载体；本地正式页面须有明确路线选择。UI内写实配图仍先走Real Image Library，无匹配或虚构才原位生图。')
        text = replace_once(text,
            '- [ ] 工具不可用时已换载体，通用素材已获取或生成；只有用户方素材或指定格式无法产出时才阻断；没有近似降级或占位交付。',
            '- [ ] 工具不可用时已核对受影响范围并引导恢复，通用素材按现有方法获取或生成；已有Figma主稿、已选路线或指定格式不能静默更换。载体变更有明确决定；未制作/未验证与占位草稿据实标明，不冒充正式交付。')
    if filename == 'SKILL.md' and 'name: fusion-design-core\n' in text:
        text = insert_before(text, '## ⛔ 开工与分步硬门禁', '''## Demo即正式产品前端

本包Demo按技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md` 交付与目标生产规格一致的本地前端，界面/样式/响应、交互与文案不因Demo降级；本地数据和受控返回仅替代服务接入。关键操作、校验、状态反馈及恢复须实际按规则发生，必要前端缺项就是未完成；不把讲解、假设或测试控制放入用户画面。QA0与专项复核分别报告前端规格一致性及真实服务接入，不用缺后端作为省略前端体验的理由；明确委托的探索稿另行标明，不当作正式Demo。

''')
    return adapt_resources(text, filename)


def adapt_figma_product_stage(text):
    text = insert_before(text, '## 输入与职责', '''## 产品主线的执行前提

本模块是产品锤内部的设计执行能力，不是从一句产品想法直接生成正式设计的独立入口。实际生成、编辑或还原前，先核对同包[产品启动条件](../fusion-product-agent/references/product-start.md)及任务包的目标/范围来源、有效决定或明确委托。关键意图未定时回产品主线补齐；可以先只读核对工具和已有资产，不能借配置初始化直接开工。已有充分输入、精确还原或局部修改不重复访谈，明确授权的探索制作保留假设边界。

''')
    text = insert_before(text, '## 输入与职责', '''## 执行位置回传

每次成果、修订、提问与回传按同包[流程位置展示](../fusion-product-agent/references/progress-navigation.md)保留产品第几/6阶段、适用的设计第几/4步、真实状态及下一动作。配置核对是设计准备，不把认证成功写成设计完成；生成、精修、Demo还原与复核分别如实记录。父任务汇总时同样保留导航，不能只交一个文件或结论让使用者猜下一步。

''')
    return adapt_copy_handoff(text, 'SKILL.md')


def adapt_copy_handoff(text, target):
    """Preserve execution methods while passing reviewed product copy downstream."""
    if target == 'SKILL.md':
        text = insert_before(text, '## 输入与职责', '''## 文案就绪后再制作

正式页面生成、编辑或Demo还原前，读取同包[产品文案步骤](../fusion-product-agent/references/product-copy.md)及本轮《界面文案基线》。主产品Agent编写、审查和维护内容，设计直接使用已就绪的原文，执行模块不临场补字。设计研究/交互推导可先行；只读配置与资产核对不受此条件阻断。

任务包必须带文案入口/版本、本次页面与状态的COPY ID及原文、动态变量和呈现约束。缺失或有影响本范围的文案阻断，先返回产品文案步骤；不能把自动补字的稿件交作正式设计。三套风格候选使用同一份就绪的代表页文案。生成提示词与Computer Use均按原文放置，不自行润色；必要增删或缩写返回产品主线更新同一基线后，再同步主稿和Demo。

设计后的QA0及实屏文案/交互复核仍执行，检查基线一致、截断、遗漏和动作结果；文案内容有问题先回文案步骤修订，不维护画布、代码和文案表三套不同文字。

''')
    elif target == 'references/task-package.md':
        text = replace_once(text,
            '产品正文是规则唯一来源；设计专家补齐交互、风格、组件/素材与提示词，执行模块记录真实工具结果。',
            '产品正文是规则唯一来源，已审查的界面文案基线是文字内容唯一来源；设计专家补齐交互、风格、组件/素材与提示词，按基线使用文字，执行模块记录真实工具结果。')
        text = replace_once(text,
            '- 本次意图与范围：',
            '- 界面文案基线：<入口、有效版本、已审查就绪范围与记录；本轮COPY ID及原文，变量/缺值、呈现约束与需制作后验证的适用要求；阻断项和影响。缺少时回产品文案步骤，不交给设计临场补字>。\n- 本次意图与范围：')
        text = replace_once(text,
            '- 必须展示：<对象、字段、状态、文案、风险或依据>。',
            '- 必须展示：<对象、字段、状态、风险或依据>。\n- 必用文案：<COPY ID、基线版本及准确原文/模板；对应控件与状态、变量和必要约束；不能只有无法读取的ID>。')
        text = replace_once(text,
            '<由上述事实生成；提示词是传输载体，不高于产品基线>。',
            '<由上述事实生成，内含适用COPY ID及准确原文/变量约束；明确逐项采用，不自行补写、润色或加入Demo讲解。三套风格候选使用同一代表页文案；缺字或需要改字返回产品文案步骤。提示词是传输载体，不高于产品与文案基线>。')
    elif target == 'references/preflight.md':
        text = replace_once(text,
            '| 目标定位 |',
            '| 文案输入 | 当前界面文案基线入口/版本、本次COPY ID及原文、审查就绪、动态约束和需制作后验证的适用要求。 | 返回产品文案步骤，暂停受影响页面正式制作；只读配置/资产核对与无关研究可继续。 |\n| 目标定位 |')
        text = replace_once(text,
            '- 配置引用：',
            '- 文案输入：{基线入口与版本、适用COPY ID/原文、就绪/阻断范围及约束；内容由产品主线维护，设计直接使用}。\n- 配置引用：')
    elif target == 'references/design-to-demo.md':
        text = insert_before(text, '## 1. 定位与版本', '''## 同版文案输入

读取本轮[界面文案基线](../../fusion-product-agent/references/product-copy.md)，核对设计任务包、Figma实际文本与文案版本。Demo按同版设计与文案还原，不在代码中重新撰写或润色；动态值按已定义模板替换。旧稿文字与有效基线不一致时，先由产品主线判断，按有效版本修订主稿后再还原；不能为了照旧稿而保留错误文案，也不能只改本地代码后声称Figma已同步。

''')
    elif target == 'references/demo-review.md':
        text = replace_once(text,
            '文案按同包[语义与表达能力](../../fusion-product-agent/knowledge/product-capability-model/standards/P3/model.md)及相关定义判断，结合[设计文案与控件方法](../../fusion-design-core/methods-ui.md)；规则含义引用当前产品正文，不重复加载全部能力。',
            '文案按同包[统一质量标准](../../fusion-product-agent/references/copy-quality.md)及其相关正式能力定义判断，结合[设计文案与控件方法](../../fusion-design-core/methods-ui.md)。承接文案基线中的制作后验证要求，按适用性检查实际画面和行为；规则含义引用当前产品正文，不重复加载全部能力，也不只看P3文字。')
        text = replace_once(text,
            '## 2. 建立覆盖并检查真实画面',
            '''## 文案前置输入与问题回流

本复核承接[独立文案步骤](../../fusion-product-agent/references/product-copy.md)已形成的《界面文案基线》，不是设计现场首次编字。先取得当前基线版本、适用COPY ID和设计/Demo版本对应；缺失时回产品主线编写与审查，不能用事后看一遍代替这个产物。已有文字仍需在实屏检验。

对照实际画面与模板，核查准确用字、状态/位置匹配、遗漏、变量、截断和提示与实际行为。内容缺陷或新增文字返回产品文案步骤，产品主线更新同一基线后同步Figma与Demo；纯呈现问题由设计修正，行为缺陷回交互/实现环节。普通表达修正不新增人工确认，有业务含义变化才回相关决定点。

## 2. 建立覆盖并检查真实画面''')
        text = replace_once(text,
            '保留被核版本、范围、覆盖/未覆盖、检查方法、发现、修正与复验；',
            '引用文案基线版本与适用COPY ID，不另抄全量文案；保留被核设计/Demo版本、范围、覆盖/未覆盖、检查方法、发现、修正与复验；')
    if target == 'SKILL.md':
        text = insert_before(text, '## 输入与职责', '''## 文案检查结果的可见回传

按技能 `fusion-product-agent` 内的 `references/product-copy.md` 的“文案审查摘要”，随成果回传基线/设计/Demo版本、本轮复用或检查范围、实际文字变化及理由或未改字说明、内容与实屏/动态验证的不同结论、阻断及下一动作。涉及改字先回产品主线更新同一基线再同步；产品主线最终回复保留本轮摘要，直接交付使用者时本模块展示，不能只有“检查通过”。

''')
    elif target == 'references/demo-review.md':
        text = insert_before(text, '## 6. 通过与交付表述', '''## 本轮文案复核的可见摘要

交付回复按技能 `fusion-product-agent` 内的 `references/product-copy.md` 的“文案审查摘要”展示本轮文案基线与设计/Demo版本、实际覆盖和方法、关键文字前后差异及理由、未改字时的呈现修正或沿用说明、未覆盖/阻断与下一动作，并链接原有检查及修改记录。内容审查、实屏对照和动态行为分别报告；未操作的状态不能写成已验证。回传产品主线时带上摘要，由其在本轮最终可见回复保留，不复制另一份正式文字。

''')
    if target == 'SKILL.md':
        text = insert_before(text, '## 输入与职责', '''## 正式设计与还原顺序

执行技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md`：本轮先形成指定Figma中的有效设计并核验，再按同版Frame/Dev Mode还原Demo，不默认先本地制作再反推正式稿。探索原型、正式设计和按稿还原分别标明；画面采用最终用户的任务结构、就绪文案与合理内容，模拟控制/评审讲解放协作说明。探索或未就绪稿不能靠改名成为正式主稿。送审在既有QA0/专项复核中记录用户视角、源版本和未覆盖；工具或权限缺失先引导恢复，不静默换载体。

''')
    elif target == 'references/task-package.md':
        text = insert_before(text, '- Figma 目标：', '''- 产物性质与正式设计要求：<探索原型 / 正式设计 / 按稿还原及真实状态；当前有效源与版本/范围，承接探索时的差异与修订。按技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md` 组织真实用户任务、就绪文案和内容；Figma路线先完成本轮主稿，再同版还原；正式检查纳入QA0/专项复核，模拟边界及测试控制写协作说明>。
''')
    elif target == 'references/design-to-demo.md':
        text = insert_before(text, '## 1. 定位与版本', '''## 正式源与用户体验

按技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md` 核对本轮产物性质、有效主稿和范围。探索原型不自动成为正式源；已有本产品Figma或已选Figma时，先完成本轮设计并核验再同版还原，不能用先写本地Demo后补Figma代替。还原用户真正看到的页面、文字和操作，不把步骤讲解、模拟控制或评审提示做成产品功能；运行边界单独说明。未接入不等于已生产可用，未实测不写动态通过。

''')
    elif target == 'references/demo-review.md':
        text = insert_before(text, '## 6. 通过与交付表述', '''## 正式设计交付专项核对

在上述QA0、文案和交互复核中落实技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md`：检查实际画面的信息与控件是否服务真实用户任务、有无制作/评审口吻及模拟控制混入、内容和资产是否满足正式设计范围、探索稿是否冒充主稿，以及Figma有效源与Demo是否同版且先设计后还原。必要的新手帮助、规则和安全提示保留；合理模拟按真实产品反馈表达，不能无动作报成功。结论随现有成果回复展示产物性质、设计源版本、范围/证据和未覆盖；有缺口的对应范围先修订或如实标草稿，不靠删“Demo”二字宣称正式交付通过。

''')
    if target == 'SKILL.md':
        text = insert_before(text, '## 输入与职责', '''## Demo的正式前端交付标准

按技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md`，Demo是与目标生产规格一致的本地正式前端：设计画面、样式/响应、文字及实际交互全部照同一有效规格执行。仅运行与服务接入层使用本地数据/受控返回，不改用户操作、校验、状态变化或反馈；不得加入演示解释、假设和模拟控制。必需体验缺项先修复，前端未完成与服务未接入分别记录，不能以Demo名义降级。

''')
    elif target == 'references/task-package.md':
        text = insert_before(text, '- Figma 目标：', '''- 目标生产前端对照：<有效设计/产品行为/文案版本；按同端/尺寸/状态核对画面、组件样式、响应布局、实际操作/校验/状态反馈和文字；本轮必需前端缺项及修复。Demo交付同一正式用户体验，本地数据及受控返回只替代服务接入，后端未接入单独记，不作为前端降级理由>。
''')
    elif target == 'references/design-to-demo.md':
        text = replace_once(text,
            'Codex 负责把设计转成可运行页面和必要模拟交互；业务规则仍引用产品事实源。',
            'Codex负责交付与目标生产规格一致的本地正式前端，页面/样式/响应、文字及本轮必要交互均按有效设计和业务规则完成。本地数据和受控返回仅替代服务接入，输入校验、操作顺序、状态变化、结果反馈及返回恢复必须实际发生，不能用跳页、静态按钮或一句成功提示代替；业务规则仍引用产品事实源。')
        text = insert_before(text, '## 4. 核验与回传', '''## 目标生产前端一致性

按技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md` 逐项对照本轮目标生产规格的画面、组件样式、响应布局、文案和实际交互；已有产品结合正式现状与本轮有效变更，0到1依据有效设计/行为/文案规格，不虚称已和不存在的线上版本比对。正式用户页面不放演示说明、假设或调试控制，服务未接入单写交付说明。未完成必需前端体验先修复或如实保留缺项，不以Demo降低验收；前端完成度和服务接入分别回传。

''')
    elif target == 'references/demo-review.md':
        text = replace_once(text,
            '4. **与行为一致**：提示对应 Demo 中实际可观察的结果。合理模拟可表达已模拟完成的结果，但无动作、未完成或结果未知时不得显示“成功”；不可实现的重试、恢复或撤销不能被文案承诺。',
            '4. **与目标产品行为一致**：本地前端按正式规则实际完成操作、校验、状态变化与反馈；受控返回只替代后端接入，不能简化用户流程。无动作、未完成或结果未知不得显示“成功”；不可实现的重试、恢复或撤销不能被文案承诺。')
        text = replace_once(text,
            '- 随模块与状态扩展补齐复核。完整 Demo 交付前必须覆盖本次交付的全部用户可见产品文案及核心、关键风险交互；排除内容显式列明，未覆盖的必需内容不得靠缩小声明变成通过。',
            '- 随模块与状态扩展补齐复核。完整Demo交付前必须覆盖约定交付范围内全部用户可见界面、交互及文案，与目标生产规格逐项对照，不能只验核心/高风险路径或把非核心入口做成静态占位。未覆盖或未实现的约定内容保留缺项，不得自行缩小声明变成通过。')
        text = insert_before(text, '## 6. 通过与交付表述', '''## 正式前端体验验收

Demo按技能 `fusion-product-agent` 内的 `references/formal-design-delivery.md` 是与目标生产规格一致的正式前端交付。将约定范围内全部实际画面/组件样式/响应、文案和实际交互分别与有效源逐项对照，核验用户操作、校验、等待、状态/结果及返回恢复；不能只验截图或主路径能点。必要体验缺项须修复，对应范围不通过，不因本地数据或后端未接入降低标准。协作/模拟说明与假设不混入用户界面；真实产品本身需要的引导和提示保留。既有记录和最终成果回复分别说明前端已完成/未完成及差异、实际验证证据和服务接入情况；前端验证不冒充后端上线验证。

''')
    return adapt_resources(text, target.rsplit("/", 1)[-1])
