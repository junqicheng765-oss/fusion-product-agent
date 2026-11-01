# UI 界面视觉方法库

本文件属于 Figma UI 设计，处理界面中的视觉系统与资产应用，不是 UI 后必须追加的独立阶段。视觉方法不改变已确认的路径、职责和主行动含义。实现设计参考时必须以正式主稿和真实资产为准，不得近似降级。

界面中的插画、图片、图标和品牌图形属于 Figma UI。只有最终产物是非界面视觉成品，或用户明确把某项资产拆成独立视觉委托时，才按 [methods-tool-routing.md](methods-tool-routing.md) `TR4` 调用视觉工具；确认后的独立资产可再导入 Figma。不得用占位或近似资产代替正式生产。

所有视觉方法同时遵守以下记录规则：

- 把正式来源、设计推导、待确认候选和人的决定分开记录；候选不能写成品牌事实或已确认规范。
- 每个实现值必须给出准确来源与版本、正式系统引用，或标为 `CANDIDATE_PENDING_CONFIRMATION`；不能凭常识补品牌值。
- 来源缺失且不同答案会改变成品时暂停受影响部分：可由本轮设计探索解决且已有授权时标 `MISSING/RESOLVE_NOW`；必须等待正式来源、资产或授权时标 `BLOCKED/WAIT_EXTERNAL`。只有明确委托或可追溯依据时才形成候选。
- 实现或还原设计参考时，布局、字体、间距、颜色、真实内容、真实资产和交互均须忠实应用，不用近似值、占位符或简化替代品冒充完成。只有用户方才有的素材（Logo、真实产品图、真实数据等）或权限缺失时才停止受影响部分；图标/3D/插画按 `V5` 从 IconScout 获取，真实摄影按 [methods-image.md](methods-image.md) 检索，虚构或无匹配再 AI 生成，不停（见 `SKILL.md`「问人规则」）。
- 所有产出都写适用页面、组件、平台、主题、表面、状态和版本，使新会话能够直接实现并逐项验收。

## V0 0→1 视觉风格库与 6 维决策漏斗

**触发问题**：在页面职责、信息层级（U1–U3）与所用组件（U4）已确认、且经 `U0` 判定属于 **C 端或强品牌差异化产品从 0 到 1 新建** 时，如何系统地帮用户选定风格并敲定具体视觉构件？  
**最低输入**：已确认的页面结构与组件选型、市场生态（国际化 / 国内）、行业与任务严肃度、目标人群。  
**跳过**：
- 有现成相关页面或既有设计系统（走 `U0` 路线 1：存量延展模式，直接提取现有 5 个视觉常量复用）；
- 纯 B 端/企业中后台从 0 到 1（走 `U0` 路线 2：直接绑定 `Ant Design` / `Arco Design` / `TDesign` / `shadcn/ui` / `MUI` / `Fluent UI` 等公开组件库快搭）。

### Step 1：语境自动剪枝（先过滤，不把违和选项抛给用户）

根据前面已确认的 4 个条件自动排除不匹配的风格与视觉构件：

1. **市场生态与品类池**：
   - 出海 / 国际化产品优先从「A. 国际化产品风格池（`INT-01`～`INT-08`）」选；
   - 国内主流 App / 小程序优先从「B. 国内产品风格池（`CN-01`～`CN-08`）」选；
   - 游戏界面、游戏官网或强游戏化互动活动页，直接进入「D. 游戏与互动娱乐 UI 风格池（`GAME-01`～`GAME-10`）」按世界观与题材匹配；
   - 以上均可叠加「C. 通用视觉质感手法（`TEX-01`～`TEX-06`）」。
2. **行业与风险底线**：高严肃、高风险行业（金融、银行、医疗诊断、法律、政务、核心交易台）**强制剔除**糖果游戏化（`INT-07`）、先锋粗野撞色（`INT-08`）、高能量大促红海（`CN-05`）、Z 世代暗黑霓虹（`CN-07`）以及卡通手绘插画、花哨多色渐变。
3. **任务形态**：高频重操作、高密度数据比对任务，优先克制背景、强层级对比与清晰容器；低频浏览、内容消费、品牌展示任务，可引入强氛围感、大留白或大图视觉。
4. **目标人群**：银发族、大众民生或下沉市场，强制高可见度、大字号与明确文字标签，剔除极简小字留白和暗黑微光风。
5. **按内容和行业的感受选，不按技术标签选**：先问用户打开它时该感受到什么（旅行是想去那里、理财是可信、棋牌是牌桌质感），按这个选。「AI 产品」「AI 助手」只说明交互方式（对话、生成、等待），不决定风格；只有产品本身就是 AI 对话或生成工具时，才进「AI 产品」风格族。例如 AI 行程规划是旅行产品，按旅行与目的地选，不按 AI 产品选。

### Step 2：在前置用研、竞品与交互方案汇报后，推导 2–3 个视觉风格方向征求用户选择（严禁未做前置推导就一上来锁死风格）

**风格决策铁律（先交互后视觉，0→1 必给选项征求用户意见）**：
1. **严禁一上来就宣布视觉风格**：在还没向用户汇报完【用户研究、三类竞品调研、任务流程、具体交互控件方案】之前，**绝不允许提前锁定或宣布任何视觉风格（如一上来就说“采用绿毡胡桃木风”并跑 `style_preset.py`）**！
2. **0→1 新产品（用户原话未指定具体视觉风格时）：提供 2–3 个差异化风格方向让用户选**：
   - 结合前面的用研与竞品调研，思考这个 UI 要传达什么意思、通过什么视觉手段表达，从下方风格池（`INT-01..08` / `CN-01..08` / `GAME-01..10`）中筛出 **2–3 个合理的差异化风格方向**（例如做棋牌/掼蛋，可提供：① 沉稳绿毡胡桃木茶室风、② 新中式水墨丹青国风、③ 明快立体 Q 弹休闲风；做 AI/效率/消费级产品，可提供：① 现代毛玻璃通透风、② 暗色微光便当盒风、③ 暖纸人文书刊风 / 清爽大图生活卡片风）；
   - 用宿主提问工具弹出（首项标 `(Recommended)`），让用户选择他想表达的视觉形式；
   - 一旦用户选定大方向，底下的 **6 个具体视觉技术参数（主色 Hex、底色冷暖、容器材质、圆角数值、字阶密度、图标网格）全部由 Agent 按专业最优解自动配齐**，不再逐项追问技术参数。
3. **汇报与提问禁令**：向用户描述风格时，**一律只用纯粹的视觉语言、色彩、材质与排版特征命名和描述，严禁出现“像某某品牌 / 某某大厂 / 某某游戏一样”的点名表述**；同时严禁把本 Skill 的内部术语（风格编号、六维/6 维、参数组合、决策漏斗、token、`V0`、`D1–D9` 等）写进给用户看的问题、选项或汇报里。此禁令只管给用户看的文字；发给生图模型、Figma 的提示词片段和字体、色值等技术参数**应保留**厂商与产品参照（如 `Apple HIG`、`Clash Royale`、`Supercell-Magic`），以保证生成效果准确，不要删改。

#### A. 国际化现代产品设计风格池（8 类）

| 编号 | 风格名称 | 视觉气质定位 | 核心视觉特征 | 适用产品 | 强制排除条件 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `INT-01` | **现代毛玻璃通透风**<br>*(Translucent Frosted Minimal)* | 轻盈通透、呼吸感留白、细腻层叠 | 大留白、字体粗细强对比、毛玻璃半透明导航/浮层、16px 细腻圆角、克制单主色 | 出海移动应用、个人效率工具、品质生活与健康硬件配套 | 重度多列后台表格、低端机为主的下沉市场 |
| `INT-02` | **瑞士极简细线网格风**<br>*(Swiss Hairline Grid)* | 理性秩序、内容至上、零多余装饰 | 黑白灰高纯度主导、1px 细描边分割、极少装饰色、排版秩序感极强、内容即界面 | AI 工具、知识库、生产力 SaaS、专业工作台、文档社区 | 强促销氛围电商、重娱乐游戏化产品 |
| `INT-03` | **暗色微光便当盒风**<br>*(Dark Bento & Luminous Glow)* | 前沿科技、深邃精密、微光边界 | 深炭黑底（非纯黑）、Bento 便当盒模块化网格、1px 渐变发光边框、低饱和蓝紫/青绿微光、毛玻璃叠层 | 开发者工具、AI 前沿产品、高阶科技官网、专业创作者工具 | 银发族/大众民生工具、强日光户外场景、传统母婴/医疗 |
| `INT-04` | **冷灰理性流体渐变风**<br>*(Refined Fluid & Tabular)* | 专业可信、清晰结构、局部流体点睛 | 主体干净理性的白/浅冷灰底 + 局部高质量流体/网格渐变或高对比品牌色、等宽数字字体精良 | 出海金融科技、跨境支付、企业服务官网、高客单价 SaaS | 追求极致朴素零装饰的内部后台 |
| `INT-05` | **暖纸人文书刊风**<br>*(Warm Paper Editorial)* | 温润知性、纸张触感、沉浸阅读 | 暖米白/纸张底色、低饱和赤陶橙/墨绿/深棕点缀、衬线体标题 + 无衬线正文混排、长文阅读舒适 | AI 对话/阅读产品、深度内容平台、文化/教育/心理健康、品质品牌站 | 高频秒级盯盘交易、强促销导购 |
| `INT-06` | **柔和色阶胶囊亲和风**<br>*(Tonal Surface & Pill)* | 温和灵动、表面色阶分层、圆润友好 | 柔和粉彩容器底色、20px+ 大圆角容器与胶囊按钮、靠清晰表面色阶代替生硬边框与重阴影 | 现代移动消费应用、大众日常工具、跨设备通用应用 | 要求极度冷峻威严的机构或重奢品牌 |
| `INT-07` | **高饱和立体按压糖果风**<br>*(Tactile Gamified Candy)* | 活力欢快、立体按压反馈、零距离感 | 高明度高饱和友好色块、圆润卡片、带底部实心硬阴影的立体可按压按钮、轻量几何图形 | 语言/技能学习、习惯打卡、青少年产品、轻互动工具 | 严肃金融、医疗诊断、法律政务、B 端严肃审批 |
| `INT-08` | **先锋粗黑描边撞色风**<br>*(Neo-Brutalist Bold Block)* | 张扬锐利、高反差撞色、打破常规 | 2.5px 纯黑粗描边、无模糊硬阴影偏移、高饱和撞色块、超大粗体字、反传统网格 | 潮流电商、创作者经济、设计/音乐先锋活动、潮玩社区 | 传统金融、医疗、政务、大众中老年产品 |

#### B. 国内主流产品设计风格池（8 类）

| 编号 | 风格名称 | 视觉气质定位 | 核心视觉特征 | 适用产品 | 强制排除条件 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CN-01` | **标准蓝白高效工作台风**<br>*(Clean Blue-White Workbench)* | 严谨清晰、高密有序、稳定可靠 | 冷白+微冷浅蓝灰底（`#F7F8FA`）、科技蓝主色、8px 标准圆角、高信息密度且对齐工整 | 企业 SaaS、协同办公、中后台系统、政务/医疗专业端 | 追求强情绪感染力的潮流消费/娱乐产品 |
| `CN-02` | **清爽大图生活卡片风**<br>*(Airy Lifestyle Magazine Card)* | 精致生活感、视觉种草、轻盈透气 | 纯白底、弱化分割线、大比例高质量配图+精炼标题、克制品牌点缀色、12px 圆润卡片与精致标签 | 生活方式社区、品质消费/文旅、新消费品牌商城、图文内容流 | 纯文字/纯表单重度录入工具 |
| `CN-03` | **深海藏青稳重财富风**<br>*(Deep Navy & Gold Trust)* | 权威稳重、尊贵可信、数据醒目 | 上深（深海藏青/黑金头卡）下浅（纯白列表）、香槟金点缀、金额强制高辨识度等宽字体（`DIN`）、风险与收益层级分明 | 银行、保险、理财、证券、征信、企业财务、高信任交易 | 泛娱乐、儿童教育、随意涂鸦社区 |
| `CN-04` | **轻快白卡直达工具风**<br>*(Lightweight Zero-Friction Card)* | 即用即走、路径极短、零学习成本 | 浅灰底配纯白圆角卡片、单屏主按钮极其醒目、功能胶囊/宫格清晰、无多余装饰干扰 | 轻量小程序、到店点单、出行/快递/生活缴费、民生便民工具 | 需要深度复杂配置的专业桌面软件 |
| `CN-05` | **暖橙红高密导购转化风**<br>*(High-Conversion Promo Grid)* | 热闹促动、利益点突出、高转化导向 | 暖红/亮橙高饱和渐变主色、价格与优惠券标签强对比（红/橙/金）、紧凑宫格入口、超大粗体到手价 | 综合电商、本地生活团购、外卖生鲜、领券促销活动页 | 高冷奢侈品、严肃医疗/法律、极简效率工具 |
| `CN-06` | **东方宣纸留白雅致风**<br>*(Modern Oriental Poetic)* | 温润内敛、诗意留白、东方气韵 | 中国传统低饱和色（黛青、竹青、宣纸白、赭石、朱砂）、适度留白、1px 细线边框、人文宋体/衬线标题 | 茶饮/香氛/东方消费品牌、文旅景区、文化博物馆、中医养生 | 现代硬核代码工具、西式高频金融交易台 |
| `CN-07` | **暗黑酸性机能潮酷风**<br>*(Dark Cyber & Acid Neon)* | 先锋酷感、金属玻璃、高能机能 | 深黑底色 + 酸性荧光绿/电光紫高亮对比、金属玻璃质感徽章、斜切角与强动感宽体字排版 | 潮玩、电竞、音乐/演出票务、年轻潮流社交、数码硬件营销 | 中老年产品、严肃 B 端、传统金融政务 |
| `CN-08` | **大字高对比普惠直白风**<br>*(High-Visibility Accessible Large-Type)* | 清晰醒目、零阅读障碍、防误触 | 全站字号放大 1–2 档（正文 $\ge 18\text{px}$）、AAA 级超高对比度、52px+ 高纯度实心大按钮、全部图标带明确中文标签 | 银发群体产品、县域/下沉市场大众工具、社区服务、基层政务 | 追求极简小字留白的先锋设计师品牌 |

#### C. 通用视觉质感手法标签（6 种，可单选或与 A/B/D 组合）

1. `TEX-01 极简扁平（Clean Flat）`：纯色块 + 留白 + 细线，无复杂光影，开发还原最稳。
2. `TEX-02 毛玻璃通透（Glassmorphism / 液态玻璃）`：半透明背景模糊 + 1px 高光细边，适合悬浮导航、卡片叠层、深浅过渡。
3. `TEX-03 Bento 便当盒分块（Bento Grid）`：规整圆角矩形模块化拼图，适合首页总览、功能聚合、数据看板。
4. `TEX-04 轻质感微立体（Soft UI）`：极柔和多层投影与微渐变表面，按钮和卡片有细腻触感（禁用老式厚重拟物）。
5. `TEX-05 弥散光氛围（Aurora / Mesh Gradient）`：底层柔和多色高斯模糊光晕，上层承载干净界面，适合首屏 Hero、AI 状态、情绪类应用。
6. `TEX-06 杂志感大字报（Editorial Typography）`：弱化框线，靠超大标题字重反差与严密网格撑起气场。

#### D. 游戏与互动娱乐 UI 风格池（10 类，面向游戏界面 / 游戏官网 / 强游戏化活动页）

| 编号 | 风格名称 | 视觉气质定位 | 核心视觉与材质特征 | 适用游戏题材与场景 | 强制排除条件 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GAME-01` | **史诗暗黑锻金重拟物风**<br>*(Dark Fantasy Forged Metal & Stone)* | 恢弘厚重、古典雕琢、暗黑史诗感 | 深炭黑岩石/羊皮卷肌理底、锻造黄铜/古金金属包边与铆钉角、内发光宝石按钮、厚重斜面浮雕阴影、古典衬线大写标题 | 西幻 MMORPG、暗黑刷宝 ARPG、重度策略卡牌、史诗级游戏官网与资料库 | 现代极简效率工具、清新日常小程序 |
| `GAME-02` | **高饱和粗描边 Q 弹立体卡通风**<br>*(Vibrant Glossy Tactile Cartoon)* | 明快爽脆、强按压反馈、休闲竞技感 | 高饱和明快色块（宝石蓝/亮黄/翠绿）、2.5px 纯黑粗外描边、顶部白高光条+底部 6px 厚实硬阴影 Q 弹按钮、微倾斜黑描边粗体字 | 休闲竞技、卡牌对战、塔防、潮玩盲盒、高转化大转盘/闯关互动活动 | 硬核写实军事/恐怖题材、严肃金融政务 |
| `GAME-03` | **深海鎏金斜切流光竞技风**<br>*(Chamfered Gold-Tech Competitive)* | 荣耀仪式感、锐利流光、大众赛事风 | 深海夜空蓝半透明磨砂底、45° 斜切双层鎏金金属边框、青蓝能量流光高光边、锐利斜体粗黑大字与段位勋章质感 | MOBA、战术竞技、竞技手游大厅/战绩/商城、电竞赛事专题与战报页 | 低龄儿童绘本、极简无装饰文档工具 |
| `GAME-04` | **哥特羊皮纸手绘拼贴悬疑风**<br>*(Gothic Parchment & Crosshatch Sketch)* | 复古怪诞、手绘排线、档案悬疑感 | 做旧羊皮档案纸/暗褐底、钢笔手绘交叉排线阴影、纽扣/缝线/火漆印章/撕纸锯齿边缘、高反差哥特衬线与打字机字体 | 非对称竞技、剧本杀/推理解谜、怪谈悬疑题材、暗黑主题活动 | 阳光运动健康、大众民生政务、标准企业后台 |
| `GAME-05` | **珠光毛玻璃玫瑰金浪漫轻奢风**<br>*(Pearlescent Glass & Rose-Gold Dreamy)* | 梦幻通透、星芒细金、浪漫高定感 | 通透浅色珠光毛玻璃/母贝流光底、0.8px 玫瑰香槟金极细描边配四角星芒点缀、纤细高雅衬线体配宽字距小字、柔和弥散光晕 | 女性向恋爱互动、换装养成、浪漫叙事、美妆/香氛/轻奢联名活动页 | 硬核重工业/暗黑血腥题材、高密度数据后台 |
| `GAME-06` | **水墨丹青鎏金云纹国风仙侠风**<br>*(Oriental Ink-Wash & Gold Fretwork)* | 写意山水、鎏金回纹、东方仙侠感 | 宣纸水墨晕染渐变底、鎏金云纹/回纹细框与海棠折角、朱砂红印章标识、苍劲毛笔书法标题配雅致宋刻正文、半透明纱感图层 | 国风武侠/仙侠 MMO、志怪卡牌、国潮文旅联动、古风剧情互动页 | 西式赛博朋克、现代极客代码工具 |
| `GAME-07` | **斜切战术面板轻机能二次元风**<br>*(Sleek Tactical Sci-Fi Anime)* | 利落干练、几何机能、幻想科技感 | 高对比深灰/冷白几何斜切色块 + 高亮单色条（明黄/青蓝）、微缩英文机能编码与十字准星装饰、超薄半透明磨砂战术面板 | 二次元开放世界、科幻机甲/抽卡养成、动漫展会与虚拟偶像专题页 | 传统中老年应用、古典写实历史题材 |
| `GAME-08` | **复古阶梯边框 8-Bit 像素街机风**<br>*(Retro 8-Bit Stepped Pixel Arcade)* | 怀旧颗粒、硬朗阶梯、街机卡带感 | 严格像素网格对齐（禁用平滑抗锯齿）、4px 阶梯状像素边框与硬偏移阴影、复古卡带色板、8-Bit 点阵像素字体 | 独立游戏、像素模拟经营/肉鸽（Roguelike）、复古怀旧彩蛋活动页 | 追求写实高精渲染的奢品或严肃金融 |
| `GAME-09` | **绿毡胡桃木奢金棋牌桌游风**<br>*(Emerald Felt & Mahogany Gold Table)* | 沉稳贵宾厅、台呢木艺、完整牌面 | 祖母绿台呢、胡桃木与金线桌沿、完整白卡纸牌面（角标加牌心花色）、分色胶囊操作按钮。牌面和按钮皮肤用图片，不用 CSS 角标代替 | 掼蛋、德州扑克、斗地主、麻将、桥牌、棋牌会客厅与赛事牌桌 | 极简冷淡文档、严肃政务医疗 |
| `GAME-10` | **等轴立体棋盘果冻漆面富豪派对风**<br>*(Isometric Glossy Board & Dice)* | 缤纷立体、金币飞溅、强庆典爽感 | 2.5D/3D 等轴立体彩色棋盘格、钞票绿/富豪金/喜庆红高光果冻漆面、底部居中超大立体投骰子圆弧按钮、丝带横幅弹窗 | 大富翁棋盘、掷骰子闯关、社交派对桌游、“掷骰走格子领奖励”营销活动 | 阴郁恐怖暗黑题材、严肃B端审批 |

### Step 3：由 Agent 自动推导并配齐 6 个具体视觉维度（专业细节默认代填，不拿技术选项烦用户）

选定大方向后，**Agent 直接根据产品语境与所选风格预设，自动推导并锁定以下 6 个具体维度**（仅当用户主动提出特殊偏好如指定品牌色时才覆盖，默认不逐项弹窗询问）：

1. **主色与色彩表现**：
   - 是否有既定品牌主色？若无，按语境推荐色相（HSB 右上高明度高饱和区或稳重深色区）。
   - **主色表现形式**：`纯色填充（Solid）`（严肃金融/B端/极简默认） / `同色系微渐变（Subtle Gradient）` / `多色流体或弥散渐变（Fluid / Mesh）`（严肃行业禁用）。
   - **辅助色策略**：`单色系克制` / `双色冷暖平衡（如蓝主色+香槟金/暖橙点缀价格或会员）` / `多色分类标签`。
2. **背景底色与中性色冷暖**：
   - **明暗模式**：`亮色清爽底` / `暖纸人文底` / `深色沉浸底` / `上深下浅混合底（头部核心卡深色凸显品质+下方亮色保易读，金融/会员常用）`。
   - **中性灰冷暖倾向**：禁用死板纯黑纯灰（`S=0`），按主色混入 1%–3% 冷暖色相（明度越高饱和度越低，明度越深饱和度略高），选 `微冷蓝灰` / `微暖米灰` / `高对比纯黑白`。
3. **容器分隔与表面材质**：
   - `无框留白 + 1px 细分割线` / `浅灰底配纯白无阴影卡片` / `微阴影悬浮卡片` / `毛玻璃半透明叠层`。
4. **圆角与几何性格**（全套圆润与尖锐必须统一，不得混用）：
   - `0–4px 利落直角/微圆角` / `6–10px 理性标准圆角` / `12–16px 现代亲和圆角 + 胶囊按钮` / `20px+ 超圆角软萌`。
5. **字体气质与排版密度**：
   - **字体组合**：`系统标准黑体（苹方/思源/SF/Inter）` / `标准黑体 + 强化等宽数字字体（如 DIN 风格，金融/电商/看板必推）` / `人文衬线标题 + 无衬线正文`。
   - **信息密度**：`紧凑高效型` / `均衡标准型` / `舒展留白型`。
6. **图标风格与配图边界**：
   - **工具图标**（粗细、圆角、透视三统一，4px 倍数画布与像素对齐）：`精致细线性（1.5–2px）` / `醒目面性填充` / `双色线面结合` / `微质感图标（轻渐变/毛玻璃/轻3D，用于核心宫格入口）`。
   - **图标与动效来源**：选定风格后，图标、3D 图标、插画、Lottie 动效先按 `V5` 第 6 条从 IconScout 拉同一套系的现成素材；不手写 SVG 路径、不用 CSS/Canvas 拼简陋图形。返回、设置、关闭等功能图标同样先下载成品再放进按钮。IconScout 没有合适的，图标改用成熟开源图标库的同风格整套，3D/插画按统一风格 AI 生成。
   - **现实对象的表现形式**：界面里用户认得的对象（卡牌、票据、商品、地图、文件、角色等）按 [methods-ui.md](methods-ui.md) `U7` 先定识别特征和各尺寸档的形式，再在这里配素材和风格。
   - **配图与空状态图形**（按行业严肃度过滤）：高严肃行业只推 `纯文字与数据图形 / 克制几何抽象图形 / 真实专业摄影`（屏蔽卡通手绘）；消费/社区可选 `高清真实场景摄影 / 扁平现代矢量插画 / 3D 质感元素 / 温暖手绘风`。其中**真实专业摄影 / 高清真实场景摄影**必须先走 [methods-image.md](methods-image.md)，不得先 AI 生一张「像照片的图」。

**贯穿 6 维的硬要求：材质语言覆盖每一个组件。** 选定风格的材质与工艺（高光、阴影、边缘、描边、纹理、圆角）必须用到全屏每一个组件上：按钮、标签、胶囊、面板、输入框、弹窗、图标、徽章，不能只做背景和主视觉。检查方法是找全屏做得最弱的那个元素，它也必须达到风格参数。常见失败有三种：质感风格里按钮只有一条平铺渐变；精致界面里配了粗糙的手画图标；有材质的面板旁边放一个系统默认样式的控件。参数表没写到的组件，从同一风格的已有参数推出来，不留默认样式。

### Step 4：单页先行与模块化提炼

先挑权重最高的 **1 个核心代表页**（如首页或核心操作页）落地上述选择，自检通过后直接将配色、文字层级、控件和组件提炼到同一组件/资源画板，再模块化拼装其余页面；不停下来等用户批准，用户中途提出修改时再回到代表页调整。

### Step 5：Agent 怎样调用选定的视觉风格（直接选定 → 写入任务包 → 自动拼进 Figma/生图指令）

用户进入 C 端 0→1 视觉决策后，**Agent 严禁只拿一个风格名字去凭感觉画图或写代码**，必须严格执行以下 3 步闭环：

1. **Step 5.1｜先向用户汇报前置推导（用研+竞品+交互方案）并提供 2–3 个风格方向让用户选，选定后再加载参数包**：
   - **0→1 新产品（用户原话未指定风格时）**：必须在汇报完用研、三类竞品和具体交互控件方案后，用提问工具给出 2–3 个风格方向（首项标 `(Recommended)`，用大白话描述想传达的视觉感受与手段，**严禁出现风格编号、六维/6 维、token、`V0`、`D1–D9` 等内部术语**，也严禁点名第三方品牌/游戏），由用户选定（自动化无人工交互测试环境除外）。
   - **主色 Hex、底色、卡片阴影、圆角数值、字体、图标网格这些具体技术细项一律不问**，在用户选定风格大方向后由 Agent 自动配齐；用户主动提出要改某一项时再改。
2. **Step 5.2｜查表加载参数包并写入任务包（唯一视觉数据源）**：
   - 从下方「可执行参数字典」读取所选风格编号对应的精确数值配方（底色/卡片 Hex、主辅色与中性字色阶梯、圆角 px、边框/阴影/毛玻璃 `blur`、字号/字重/行高/间距、专用 Prompt 片段），并用用户的 6 维微调值覆盖对应字段。
   - 同一份数值已打包成可直接应用的预设文件 `style-presets/dto/<编号>-*.json`。运行 `python3 scripts/style_preset.py show <编号>` 读取，并一起取出它所属风格族在 `style-presets/registry.json` 里绑定的资源：
     - 最接近的 Tweakcn 主题；
     - 对应的系统预设（Apple / Material 3 / Ant Design）；
     - 通用组件配方标签（`recipes`，所有技术栈先用）、React 区块库与动效库。
     选完风格不只用参数表：组件先从 [component-recipes/](component-recipes/registry.json) 取；React 项目缺的再从区块库补；本地缺的再按 [methods-style-engine.md](methods-style-engine.md) `DS6` 去线上补。
   - 立即写入当前任务的 `V0 视觉方向与 6 维决策卡`（或 `DESIGN-<模块>-任务包.md`），锁死为本轮唯一视觉数据源。
3. **Step 5.3｜自动拼进 Figma / 组件库 / 生图执行指令**：
   - **操作 Figma AI 生成 UI（严禁 Codex 用 `use_figma` 从零手画矩形框）**：Codex 只负责使用下方模板把前置推导的页面功能区块、交互控件、锁定的 Token 数值与参考图（`refs/`）组装成完整的结构化提示词，然后通过 Computer Use / 宿主操作 **Figma AI（Figma Agent / First Draft / Make）** 生成可编辑的设计稿 Frame，再将搜集好的 IconScout / 真图素材带入微调：
     ```text
     [Figma 视觉执行指令组装模板]
     - 绑定风格：{style_id} {style_name}
     - 画布与表面色：Page Canvas = {bg_hex}；Card Surface = {card_hex}；Text Hierarchy = {text_primary} / {text_secondary} / {text_muted}
     - 品牌主色与表现：Primary = {primary_hex}（表现方式：{solid_or_gradient}）；Accent = {accent_hex}
     - 容器与材质：Border = {border_spec}；Shadow = {shadow_spec}；Blur = {blur_spec}
     - 圆角阶梯：Card Radius = {card_radius}；Button/Input Radius = {control_radius}
     - 字体与字阶：Font Family = {font_family}（数字规则：{numeric_font_rule}）；Scale = {type_scale_and_spacing}
     - 图标与配图规范：Icon = {icon_spec}；Imagery = {imagery_rule}
     - 风格 Prompt 注入：{style_prompt_snippet}
     ```
   - **调用公开组件库（纯 B 端 `U0` 路线 2）**：直接连接对应组件库（如 `user-shadcn-ui` MCP 或 Ant Design / Arco / TDesign 规范 token），将 `colorPrimary`、`borderRadius`、`fontSize` 与 `compact/default` 密度一键写入主题配置。
   - **写成 HTML / 代码（含 C 端）**：不在页面里逐个写色值。用 `python3 scripts/style_preset.py apply <编号> --css <全局 CSS>`，或导出对应格式（`css` / `tailwind4` / `antd` / `shadcn`），把整套 token 写进一处，页面和组件只引用 `var(--…)`。多页面交付前跑 `scripts/style_consistency_audit.py`。详见 [methods-style-engine.md](methods-style-engine.md) `DS3`–`DS5`。
   - **仅当 `V7` 已经判定必须生图时**：才把该风格的 `{style_prompt_snippet}`、主色 `{primary_hex}` 与底色冷暖追加进生图模型的 `prompt`。真实摄影仍先走 [methods-image.md](methods-image.md)，不因本条直接生图。

#### 国际化风格可执行参数字典（`INT-01`～`INT-08`）

| 编号 | 底色 / 卡片 / 字色阶梯（主·次·弱） | 默认主色参考（可被品牌色覆盖） | 边框 / 阴影 / 模糊参数 | 圆角阶梯（卡片 / 按钮控件） | 字族 / 字阶（H1·H2·正文·辅助） / 间距 | Figma / 代码 / 生图专用 Prompt 片段 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `INT-01`<br>现代毛玻璃通透风 | 底：`#F2F2F7`<br>卡：`#FFFFFF` 或 `rgba(255,255,255,0.78)`<br>字：`#000000` / `#3C3C43` / `#8E8E93` | `#007AFF`（纯色或极轻同色微渐变） | 边框：`0.5px solid rgba(0,0,0,0.06)`<br>浮层：`backdrop-filter: blur(20px)`<br>阴影：`0 4px 20px rgba(0,0,0,0.05)` | 卡片 `16px`<br>按钮 `12px` 或胶囊 `999px` | 系统字体栈 `-apple-system` / `PingFang SC`（苹果设备上即显示 SF Pro；不嵌入 SF Pro 字体文件，其授权仅限苹果平台）<br>字阶：`28/20/16/13px`（标题 `700`，正文 `400` 行高 `1.45`）<br>内边距：`16–20px`，间距 `12/16px` | `Apple HIG modern iOS aesthetic, frosted glass translucent bar (blur 20px), #F2F2F7 canvas, 16px card radius, generous whitespace, crisp SF typography, subtle elevation` |
| `INT-02`<br>瑞士极简细线网格风 | 底：`#FFFFFF` / `#FAFAFA`<br>卡：`#FFFFFF`<br>字：`#09090B` / `#52525B` / `#A1A1AA` | `#111827`（近黑主按钮）+ 点缀 `#2563EB` | 边框：`1px solid #E4E4E7`<br>阴影：无或极轻 `0 1px 2px rgba(0,0,0,0.04)`<br>模糊：无 | 卡片 `8px`<br>按钮/输入 `6px` | `Inter` / `Geist` + `PingFang SC`<br>字阶：`24/18/14/12px`（标题 `600` 字距 `-0.02em`，行高 `1.5`）<br>内边距：`16–24px`，间距 `8/16px` | `Swiss minimal SaaS UI, crisp 1px #E4E4E7 hairline borders, high-contrast monochrome with single accent, 8px radius, zero clutter, Notion/Vercel inspired` |
| `INT-03`<br>暗色微光便当盒风 | 底：`#08090A`<br>卡：`rgba(255,255,255,0.03)`<br>字：`#F7F8F8` / `#8A8F98` / `#575BC7` | `#5E6AD2` 或微光渐变 `#4EA7FC -> #B59AFF` | 边框：`1px solid rgba(255,255,255,0.08)`<br>微光：`0 0 24px rgba(94,106,210,0.22)`<br>模糊：`blur(16px)` | 卡片 `12px`<br>按钮 `8px` | `Inter` / `Geist` + `JetBrains Mono`<br>字阶：`28/20/14/12px`（标题 `600`，数字/标签等宽）<br>内边距：`20–24px`，网格间距 `12/16px` | `Dark mode Bento grid UI, deep charcoal #08090A surface, 1px rgba(255,255,255,0.08) luminous border, subtle ambient glow, blur 16px, Linear/Cursor aesthetic` |
| `INT-04`<br>冷灰理性流体渐变风 | 底：`#F6F9FC`<br>卡：`#FFFFFF`<br>字：`#0A2540` / `#425466` / `#8898AA` | `#635BFF`（主按钮纯色，局部 Hero 流体渐变） | 边框：`1px solid #E3E8EE`<br>阴影：`0 6px 24px rgba(15,23,42,0.06)`<br>模糊：局部 `blur(12px)` | 卡片 `10px`<br>按钮 `6px` | `Inter` + 强制等宽数字 `tabular-nums`<br>字阶：`28/20/15/13px`（数字 `700`）<br>内边距：`20–24px`，间距 `12/16px` | `Refined fintech UI, clean cool-grey #F6F9FC canvas, structured white 10px cards, #635BFF primary, controlled fluid mesh gradient accent, precise tabular numbers` |
| `INT-05`<br>暖纸人文书刊风 | 底：`#F5F0E8`（暖纸色）<br>卡：`#FAF7F2`<br>字：`#191918` / `#5C5852` / `#8C857B` | `#CC785C`（赤陶橙）或 `#1F4E3D`（深墨绿），纯色 | 边框：`1px solid #E6DEC8`<br>阴影：无，靠暖色阶与细线分层<br>模糊：无 | 卡片 `8px`<br>按钮 `6px` | 标题衬线 `Fraunces`/`Newsreader`/`宋体` `600`<br>正文无衬线：`30/22/16/13px`（正文行高 `1.65`）<br>内边距：`24–32px` | `Warm editorial UI, cream paper #F5F0E8 background, #CC785C terracotta accent, high-contrast serif headlines with clean sans body, bookish calm` |
| `INT-06`<br>柔和色阶胶囊亲和风 | 底：`#FEF7FF`<br>卡：`#F3EDF7`（Tonal 色阶）<br>字：`#1D1B20` / `#49454F` / `#79747E` | `#6750A4`（配粉彩容器 `#EADDFF`） | 边框：无（纯靠 Tonal Surface 色阶区分）<br>阴影：极轻或无<br>模糊：无 | 卡片 `20px`–`24px`<br>按钮胶囊 `999px` | `Roboto` / `Google Sans` / `思源黑体`<br>字阶：`28/22/16/12px`（标题 `500/600`）<br>内边距：`16–24px`，间距 `12/16px` | `Material You expressive UI, tonal surface color hierarchy (#FEF7FF / #F3EDF7) without heavy shadows, pill-shaped buttons, 20px rounded containers` |
| `INT-07`<br>高饱和立体按压糖果风 | 底：`#FFFFFF`<br>卡：`#F7F9FA`<br>字：`#3C3C3C` / `#777777` / `#AFAFAF` | `#58CC02`（活力绿）+ `#FFC800`（明黄）+ `#1CB0F6`（亮蓝） | 边框：`2px solid #E5E5E5`<br>按钮立体底阴影：`0 4px 0 #46A302`（零模糊） | 卡片 `16px`<br>按钮 `14px` | `Nunito` / `Baloo 2` / 圆体 `700/800`<br>字阶：`26/20/16/14px`<br>内边距：`16–20px`，间距 `12/16px` | `Friendly gamified UI, vibrant candy colors (#58CC02 / #FFC800), tactile 3D pressable buttons with 4px solid bottom shadow, 16px chunky rounded corners` |
| `INT-08`<br>先锋粗黑描边撞色风 | 底：`#FFFDF7` 或 `#F8E000`<br>卡：`#FFFFFF`<br>字：`#000000` / `#222222` / `#555555` | `#FF433D` / `#5200FF` 高饱和撞色块 | 边框：`2.5px solid #000000`<br>硬偏移阴影：`4px 4px 0 #000000`（零模糊） | 卡片 `0px`–`4px`<br>按钮 `4px` | `Space Grotesk` / `Archivo Black` `800`<br>字阶：`36/22/15/12px`<br>内边距：`16–24px`，间距 `12/16px` | `Neo-brutalist UI, thick 2.5px solid #000 borders, hard 4px offset drop shadows without blur, high-saturation color blocks, bold display type` |

#### 国内风格可执行参数字典（`CN-01`～`CN-08`）

| 编号 | 底色 / 卡片 / 字色阶梯（主·次·弱） | 默认主色参考（可被品牌色覆盖） | 边框 / 阴影 / 模糊参数 | 圆角阶梯（卡片 / 按钮控件） | 字族 / 字阶（H1·H2·正文·辅助） / 间距 | Figma / 代码 / 生图专用 Prompt 片段 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CN-01`<br>标准蓝白高效工作台风 | 底：`#F7F8FA`（微冷蓝灰）<br>卡：`#FFFFFF`<br>字：`#1D2129` / `#4E5969` / `#86909C` | `#1677FF` / `#3370FF`（科技蓝纯色） | 边框：`1px solid #E5E6EB`<br>阴影：`0 2px 8px rgba(0,0,0,0.04)`<br>模糊：无 | 卡片 `8px`<br>按钮/输入 `6px` | `PingFang SC` / `HarmonyOS Sans`<br>字阶：`20/16/14/12px`（表头/标题 `500/600`）<br>内边距：`16–20px`，间距 `8/12/16px` | `Enterprise clean blue-and-white workbench UI, #F7F8FA cool-grey canvas, #1677FF primary, structured 8px white cards, high information clarity` |
| `CN-02`<br>清爽大图生活卡片风 | 底：`#F8F8F8` 或 `#FFFFFF`<br>卡：`#FFFFFF`<br>字：`#111111` / `#666666` / `#999999` | `#FF2442` 或克制黑金/青灰点缀 | 弱化分割线，无框或极淡底色差 `0 2px 12px rgba(0,0,0,0.03)` | 卡片 `12px`<br>按钮胶囊 `999px` | `PingFang SC`<br>字阶：`22/17/15/12px`（标题 `600` 精炼，行高 `1.5`）<br>内边距：`12–16px`，间距 `8/12px` | `Modern Chinese lifestyle magazine feed UI, clean 12px white cards, high-ratio photography, refined pill tags, airy spacing` |
| `CN-03`<br>深海藏青稳重财富风 | 底：上深 `#0F2942` + 下浅 `#F5F7FA`<br>卡：`#FFFFFF` / 黑金卡 `#1A2233`<br>字：`#141E28` / `#5A6675` / `#8C97A6` | `#0F2942`（深海藏青）或 `#165DFF` + 香槟金 `#D4AF37` | 边框：`1px solid #E8EDF3`<br>阴影：`0 4px 16px rgba(15,41,66,0.06)`<br>模糊：无 | 卡片 `8px`–`10px`<br>按钮 `8px` | `PingFang SC` + 金额/收益率强制 `DIN Alternate` / `tabular-nums` `700`<br>字阶：`26(金额)/18/14/12px`<br>内边距：`16–20px`，间距 `10/12px` | `Trustworthy wealth management & banking UI, deep navy #0F2942 and champagne gold #D4AF37 header card, crisp white data cards, bold DIN tabular numbers` |
| `CN-04`<br>轻快白卡直达工具风 | 底：`#F5F5F5`<br>卡：`#FFFFFF`<br>字：`#191919` / `#576B95`(链接) / `#888888` | `#07C160`（微信绿）或品牌高明度主色 | 无多余描边，浅灰底托纯白模块，底部固定操作栏 `0 -2px 10px rgba(0,0,0,0.04)` | 卡片 `10px`–`12px`<br>按钮 `8px` 或胶囊 `999px` | `PingFang SC`<br>字阶：`20/17/15/12px`（主按钮 `16px` `600`）<br>内边距：`12–16px`，间距 `8/12px` | `Lightweight WeChat Mini-Program native style, #F5F5F5 background with clean 12px white rounded cards, prominent single bottom CTA, zero friction` |
| `CN-05`<br>暖橙红高密导购转化风 | 底：`#F4F4F4`（局部深暖红头）<br>卡：`#FFFFFF`<br>字：`#111111` / `#666666` / `#FF5000`(价格) | `#FF5000` / `#E1251B`（暖橙红渐变 `#FF7A00 -> #FF2A00`） | 价格/券标签高对比描边 `1px solid #FFD6CC`，宫格紧凑无阴影 | 卡片 `12px`<br>按钮胶囊 `999px` | `PingFang SC` + 价格超大 `DIN` `700`<br>字阶：`28(到手价)/16/13/11px`<br>内边距：`10–12px`，间距 `6/8px`（紧凑） | `High-conversion e-commerce promotional UI, warm orange-red gradient (#FF7A00 to #FF2A00) CTA, bold DIN price callouts, compact grid entry, clear coupon badges` |
| `CN-06`<br>东方宣纸留白雅致风 | 底：`#F7F4ED`（宣纸米白）<br>卡：`#FCFBF7`<br>字：`#2B2B28` / `#6E6A63` / `#9E988E` | `#2F4F4F`（黛青）/ `#5B7A57`（竹青）/ `#9E2A2B`（朱砂点缀） | 边框：`1px solid #DED6C6` 细线框，留白充足，禁用刺眼荧光色 | 卡片 `4px`–`6px`（内敛微圆角）<br>按钮 `4px` | 标题人文宋体/衬线 `600`，正文清秀黑体<br>字阶：`24/18/15/12px`（行高 `1.6`）<br>内边距：`20–24px`，间距 `16/20px` | `Modern Oriental neo-Chinese aesthetic UI, warm Xuan-paper #F7F4ED background, muted slate-green and cinnabar accents, 1px #DED6C6 border, serif headlines, poetic whitespace` |
| `CN-07`<br>暗黑酸性机能潮酷风 | 底：`#0B0C10`<br>卡：`#161821`<br>字：`#FFFFFF` / `#A0A6B8` / `#CCFF00` | `#CCFF00`（酸性荧光绿）或 `#7000FF -> #00F0FF` 高亮渐变 | 金属/玻璃边框 `1px solid rgba(204,255,0,0.35)`<br>微光：`0 0 16px rgba(204,255,0,0.2)` | 卡片 `4px` 或斜切角<br>按钮 `4px` 或胶囊 | 粗黑体 / 几何宽体 `800` + 等宽机能标签<br>字阶：`28/20/14/11px`<br>内边距：`16px`，间距 `10/12px` | `Gen-Z cyber street-culture UI, pitch dark #0B0C10 background, acid neon lime #CCFF00 accent, metallic glass badges, kinetic bold typography` |
| `CN-08`<br>大字高对比普惠直白风 | 底：`#F5F5F5`<br>卡：`#FFFFFF`<br>字：`#000000` / `#333333`（禁用浅灰字） | `#D93025` 或 `#0066CC`（高纯度正色实心主按钮） | 边框：`1.5px solid #CCCCCC`<br>对比度强制 $\ge 7:1$（AAA 级） | 卡片 `12px`<br>按钮 `10px`（高度 $\ge 52\text{px}$） | `PingFang SC` 全站放大 1–2 档<br>字阶：`26/22/18/16px`（正文 $\ge 18\text{px}$ `500`，标题 `700`）<br>内边距：`16–20px`，间距 `12/16px` | `Senior-friendly high-visibility accessible UI, extra-large 18px+ body text, 52px+ tall solid buttons, explicit Chinese text labels under every icon, ultra-high AAA contrast` |

#### 游戏与互动娱乐 UI 可执行参数字典（`GAME-01`～`GAME-10`）

| 编号 | 底色 / 面板表面色 / 字色阶梯 | 默认主色与能量色参考 | 边框 / 材质高光 / 阴影参数 | 圆角与异形切角阶梯 | 字族 / 字阶 / 排版特征 | Figma / 代码 / 生图专用 Prompt 片段 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GAME-01`<br>史诗暗黑锻金重拟物风 | 底：`#0D0A08`（暗黑岩石）<br>面：`#1C1613`（黑铁/羊皮卷 `#D8C39E`）<br>字：`#F3E5AB`（古金白） / `#B8A68E` / `#7A6A58` | 传奇橙 `#FF8000` / 奥术紫 `#A335EE` / 血红 `#9E1B1B`（内发光宝石按钮） | 边框：`2px solid #8C6D3F`（锻造黄铜渐变框）<br>内发光：`inset 0 1px 0 rgba(255,230,160,0.45)`<br>重浮雕阴影：`0 8px 24px rgba(0,0,0,0.85)` | 卡片 `2px`–`4px`（带金属包角装饰）<br>按钮 `4px` 斜面浮雕 | `Cinzel` / `Friz Quadrata` / 力量感衬线粗体 `700`<br>字阶：`32/22/15/12px`（标题带 `0 2px 4px #000` 文字投影） | `Blizzard dark fantasy RPG UI, forged aged brass & stone frame, glowing gemstone CTA button, deep bevel embossing, Cinzel serif gold-leaf typography, Diablo/Warcraft HUD aesthetic` |
| `GAME-02`<br>高饱和粗描边 Q 弹立体卡通风 | 底：`#1E5799`（皇室蓝底）或 `#2C3E50`<br>面：`#F4F6F9` 或木板/石砖色<br>字：`#FFFFFF`（必带 2px 纯黑外描边） / `#FFE600` | 对战亮黄 `#FFCC00 -> #FF9900` / 宝石绿 `#38E54D` / 史诗紫 `#B537F2` | 边框：`2.5px solid #000000`（纯黑粗描边）<br>顶高光：`inset 0 3px 0 rgba(255,255,255,0.65)`<br>厚底硬阴影：`0 6px 0 #995500, 0 8px 12px rgba(0,0,0,0.45)` | 卡片 `16px`–`20px`<br>按钮 `14px`（按下时 `translateY(4px)` 压缩底阴影） | `Supercell-Magic` / `Lilita One` / `Luckiest Guy` / 超粗圆体 `900`<br>字阶：`30/22/16/13px`（微倾斜 `-3deg` + 黑描边） | `Supercell Clash Royale tactile cartoon game UI, vibrant glossy 3D button with top white highlight bar, thick black outline, 6px solid bottom press shadow, chunky tilted outlined typography` |
| `GAME-03`<br>深海鎏金斜切流光竞技风 | 底：`#0A1324`（深海夜空蓝）<br>面：`rgba(16,28,52,0.82)` 半透明磨砂<br>字：`#F7E6C4`（香槟亮金） / `#D0DDF0` / `#6C84A6` | 荣耀灿金渐变 `#F5D08A -> #C49346` + 竞技青蓝 `#00E5FF` | 边框：`1.5px solid #C89D54`（45° 斜切双层金属线）<br>流光：`0 0 18px rgba(245,208,138,0.35)`<br>模糊：`blur(12px)` | `clip-path` 45° 斜切角（Chamfer `8px–12px`）或 `2px` 锐角 | 锐利斜体粗黑 / `剑体` + `DINPro-Bold` 战绩数字<br>字阶：`28/20/14/12px`（字重 `700/800`） | `Honor of Kings competitive MOBA game lobby UI, deep navy translucent HUD with 45-degree chamfered metallic gold borders, cyan energy glow, sharp italic bold Chinese typography, esports crest` |
| `GAME-04`<br>哥特羊皮纸手绘拼贴悬疑风 | 底：`#1A1615`（暗夜煤黑）<br>面：`#D8CBB8`（做旧羊皮档案纸）<br>字：`#241C18`（墨迹黑） / `#5E4B3E` / `#8C1D1D`（暗血红） | 火漆暗红 `#8C1D1D` / 古董铜 `#9C7A44` | 边框：手绘不规则双墨线 `2px dashed/solid #2B221E` + 撕纸锯齿边缘<br>阴影：`4px 6px 14px rgba(0,0,0,0.65)`（交叉排线暗影感） | 不规则手绘微折角 `2px` + 纽扣/回形针/火漆印章角标 | 哥特衬线 / 打字机字体 `Special Elite` / `Playfair Display` + 手写批注字<br>字阶：`28/20/15/12px` | `Identity V gothic vintage detective game UI, distressed parchment paper dossier, hand-drawn crosshatch ink lines, wax seal & button fasteners, eerie serif & typewriter typography` |
| `GAME-05`<br>珠光毛玻璃玫瑰金浪漫轻奢风 | 底：`#F8F4F9` 或星夜紫蓝 `#161426`<br>面：`rgba(255,255,255,0.68)`（珠光毛玻璃）<br>字：`#2E2532` / `#7A6B82` / `#B5A3BE` | 玫瑰香槟金 `#E5C1BD -> #C99E9A` / 星光银白 `#F0EBF8` | 边框：`0.8px solid rgba(229,193,189,0.75)`（细金线 + 四角十字星芒 `✦`）<br>模糊：`backdrop-filter: blur(24px)`<br>柔光：`0 8px 32px rgba(180,140,190,0.18)` | 卡片 `12px` 或优雅菱形/拱形切角<br>按钮胶囊 `999px` | 纤细高反差衬线 `Cormorant Garamond` / `Didot` / `方正清刻本悦宋` `500` + 细黑体<br>字阶：`26/18/14/11px`（宽字距 `+0.08em`） | `Papergames Love and Deepspace / Shining Nikki otome luxury game UI, pearlescent frosted glass panel, ultra-thin rose-gold hairline frame with 4-point star sparkles, dreamy aurora bokeh, elegant serif` |
| `GAME-06`<br>水墨丹青鎏金云纹国风仙侠风 | 底：`#ECE6DA`（宣纸水墨底）或玄黑 `#141619`<br>面：`rgba(247,244,237,0.85)` 纱感面板<br>字：`#1F1E1B`（徽墨） / `#5C574F` / `#9E2A2B` | 鎏金 `#C89B57` + 朱砂印章红 `#B82923` + 青绿山水 `#3B6E6C` | 边框：`1px solid #C89B57`（内嵌中式回纹/云雷纹细角花）<br>阴影：水墨晕染淡影 `0 6px 20px rgba(31,30,27,0.12)` | 卡片 `4px` 中式折角 / 海棠角<br>按钮卷轴或玉佩胶囊形 | 苍劲毛笔书法标题 + `思源宋体` / `方正宋刻` 正文<br>字阶：`30/20/15/12px`（支持局部竖排点缀与朱文印章） | `Oriental Xianxia ink-and-gold game UI (Justice Online / Onmyoji style), Xuan paper & mist wash surface, delicate gold cloud-fretwork corners, cinnabar red seal stamp, calligraphy title` |
| `GAME-07`<br>斜切战术面板轻机能二次元风 | 底：`#121316` 或冷灰白 `#ECEFF4`<br>面：`rgba(24,26,32,0.88)` 极薄战术面板<br>字：`#FFFFFF` / `#9AA4B2` / `#FFE600` | 机能明黄 `#FFE600` 或星铁青蓝 `#00D2FF` / 活力橙 `#FF6B00` | 边框：`1px solid rgba(255,255,255,0.15)` + 局部 `3px` 高亮色块条与十字准星 `+` 装饰 | 卡片 `2px` 结合单侧 45° 斜切角<br>按钮硬朗斜切矩形 | 几何无衬线粗体 `HarmonyOS Sans` / `Rajdhani` / `DIN` `700` + 微缩 `8px` 英文机能编号 | `Hoyoverse / Arknights anime sci-fi tactical flat UI, sleek dark translucent HUD, sharp geometric diagonal cut corners, bright yellow/cyan accent bar, micro-tech typography & crosshair decals` |
| `GAME-08`<br>复古阶梯边框 8-Bit 像素街机风 | 底：`#1A1C2C`（PICO-8 深紫蓝）<br>面：`#333C57` 或像素木框 `#8F563B`<br>字：`#F4F4F4` / `#94B0C2` / `#FFCD75` | 街机红 `#E43B44` / 像素金 `#FEAE34` / 能量绿 `#38B764` | 边框：`4px` 阶梯状像素边框（`box-shadow` 阶梯拼合，零模糊）<br>硬阴影：`4px 4px 0 #0F101A` | `0px` 纯直角像素阶梯切角（严禁平滑圆角与抗锯齿模糊） | 点阵像素字体 `Press Start 2P` / `Zpix (最像素)` / `VT323`<br>字阶：`24/16/12/8px`（严格按 `8px` 整数倍缩放） | `Retro 16-bit pixel art indie game UI (Stardew Valley / Balatro style), crisp pixelated stepped frame, zero anti-aliasing blur, 8-bit bitmap font, tactile arcade button with hard pixel shadow` |
| `GAME-09`<br>绿毡胡桃木奢金棋牌桌游风 | 底：径向渐变祖母绿台呢 `#0F5132 -> #072B1A`（或深蓝天鹅绒 `#0C2340`）<br>牌面：完整白卡纸，不是只有角标。出牌区和自己的手牌都要看见角标和牌心花色<br>字：`#FFF8E7` / `#FFD700`(筹码金) / 牌面红 `#D92626`·黑 `#1A1A1A` | 出牌/加注亮橙黄 `#FFB800 -> #E67E00` + 跟注/提示翠绿 `#2ECC71` + 不要/弃牌冷蓝灰 `#4A6572` | 桌沿、牌面、按钮皮肤以目标稿图片为准。下面这些 CSS 只是还没有图片时的占位，不能当成已经做出质感：桌沿 `6px` 深胡桃木 `#3E2723` 配 `1.5px` 香槟金内嵌线 `#D4AF37`；牌阴 `0 4px 10px rgba(0,0,0,0.45)`；按钮顶高光 `inset 0 2px 0 rgba(255,255,255,0.5)` + 底内阴影 `inset 0 -3px 0 rgba(0,0,0,0.28)` | 扑克牌 `6px`–`8px` 标准圆角<br>操作按钮胶囊 `999px`（高 $\ge 48\text{px}$ 防误触） | 牌面用图片。角标字体 `DIN` / `Roboto Condensed Bold` `800` 只写在牌面图里，不用 CSS 角标代替整张牌 | `Guandan card table, emerald felt, mahogany and gold rail, full playing-card faces with corner index and center pip, glossy pill buttons. Do not reduce the hand to corner indexes` |
| `GAME-10`<br>等轴立体棋盘果冻漆面富豪派对风 | 底：明亮天蓝/薄荷绿环绕 `#E0F7FA` + 奶油白棋盘格 `#FFFDF9`<br>面：`#FFFFFF` 配彩色地产色带顶栏<br>字：`#FFFFFF`（带深色描边） / `#2D3436` / `#00B894`(钞票绿) | 富豪金 `#FFD700 -> #FFA502` + 钞票翠绿 `#00C853` + 大亨红 `#FF3838` | 边框：`2px solid #FFFFFF` 内高光 + 饱满 3D 膨胀果冻漆面光泽<br>投骰主按钮底阴影：`0 8px 0 #C23616, 0 12px 20px rgba(0,0,0,0.3)` | 棋盘格 `10px`<br>弹窗 `24px` 大圆角（带拱形丝带横幅头）<br>投骰主按钮超大圆弧/正圆 | `Fredoka` / `Baloo 2` / 圆润胖体字 `800` + 超大立体金币数字<br>字阶：`32/22/16/13px` | `Monopoly GO! & Richman 3D board game UI, isometric colorful property tiles, glossy candy-coated 3D dice roll centerpiece button, floating cash & gold coin counters, festive ribbon banner modal` |

#### 通用质感手法叠加参数（`TEX-01`～`TEX-06`）

- `TEX-01 极简扁平`：移除投影与模糊，使用 `1px` 实线或纯底色差区分层级。
- `TEX-02 毛玻璃通透`：浮层/卡片使用 `background: rgba(255,255,255,0.72)`（暗色 `rgba(20,22,30,0.68)`）+ `backdrop-filter: blur(20px)` + `1px solid rgba(255,255,255,0.35)` 高光边。
- `TEX-03 Bento 便当盒分块`：容器统一 `12px–16px` 圆角、固定网格间距 `12px` 或 `16px`，模块按 `1x1 / 2x1 / 2x2` 严密拼合。
- `TEX-04 轻质感微立体`：卡片表面微渐变 + 双层柔光阴影 `0 8px 24px rgba(0,0,0,0.06), inset 0 1px 0 rgba(255,255,255,0.8)`。
- `TEX-05 弥散光氛围`：底层铺 `filter: blur(60px)` 低透明度双色/三色径向渐变光斑（透明度 `12%–22%`），不干扰上层文字对比度。
- `TEX-06 杂志感大字报`：主标题字号拉大至正文的 `2.5x–3.5x`，去掉多余卡片外框，用 `1px` 细横线与大留白切分章节。

**产出**：`V0 视觉方向与 6 维决策卡`（选定风格编号、预设参数包、6 维确认值、排除项及核心代表页范围），作为 V1–V6 及下游工具调用的直接输入。  
**完成证据**：候选方向经过语境与行业严肃度剪枝；主色纯色/渐变、底色、容器、圆角、字体密度、图标风格 6 项均已明确，且已映射为具体可执行数值与专用 Prompt 片段。  
**不得替代**：不能跳过 U1–U4 直接在结构未定时选风格。

## V1 视觉依据

**触发问题**：本次视觉决定依据什么？  
**最低输入**：设计系统、正式主稿、品牌材料、用户委托或允许探索的范围。  
**跳过**：任务不包含视觉。

**步骤**

1. 为每项来源记录来源 ID、类型、所有者、准确文件或节点、版本或日期、适用范围及状态；优先引用正式设计系统或主稿。
2. 写清哪些值已锁定、哪些允许探索、哪些不得改变，以及谁有权确认。
3. 无基线时记录用户委托及可追溯依据。0→1 没有品牌规范时，`V0` 风格库参数或组件库默认值就是可追溯依据，Agent 直接采用并标注“可替换为品牌值”，不请求输入、不阻断；只有用户声明已有正式品牌规范但未提供文件时，才按“缺了就无法开工”处理。
4. 区分参考文件和可编辑目标，记录目标版本、允许修改范围和验收对象。
5. 只有用户方才有的真实资产缺失时，停止受影响部分并向用户要；图标/3D/插画按 `V5` 从 IconScout 获取，真实摄影按 [methods-image.md](methods-image.md) 检索，虚构或无匹配再按 `V7` 生成。两种情况都不用占位、近似或简化替代后称完成。

**产出**：视觉依据卡。  
**完成证据**：每项实现值都能回到正式来源、系统引用或待确认候选；允许范围、确认人和阻断项明确。  
**不得替代**：用“类似品牌风格”伪造规范。

## V2 语义色

**触发问题**：颜色如何表达行动和状态？  
**最低输入**：主行动、文字层级和状态列表。  
**跳过**：已有 token 且只需忠实应用。

**步骤**

1. 先列出主行动、主/次文字、链接、边框、焦点、选择、成功、警告、错误、禁用和各层背景表面的语义角色，再考虑氛围色。氛围不得降低主行动、状态或关键文本的辨识度。
2. 每个 token 必须形成以下实现记录；不适用的状态也要写 `N/A` 及理由：

```text
Token ID：
语义角色：
用途及对应对象：
来源：来源 ID / 版本 / 变量、样式或节点路径
值状态：CONFIRMED / CANDIDATE_PENDING_CONFIRMATION / MISSING / BLOCKED
实际值或正式系统引用：
前景对象及 token：
背景或表面及 token：
状态映射：
- default：
- hover：
- pressed：
- focus：含焦点指示器、粗细和偏移所用 token
- disabled：
对比验证：
- 采用标准、级别、阈值及来源：
- 各状态 × 主题 × 表面的前景/背景实际值、实测比值、工具或方法：
- 结果：PASS / FAIL / NOT_TESTED / NOT_APPLICABLE
非颜色辅助：文字、图标、形状、边框、位置、纹理或其他线索
亮色 / 暗色 / 其他表面映射：
适用范围：页面 / 组件 / 平台 / 主题 / 表面 / 状态 / 版本
责任人及确认人：
```

3. 有正式系统时引用准确 token 路径和版本，不把当前渲染值抄成新的品牌规范；正式系统未覆盖的状态标缺口。
4. 无基线时，按 [methods-color.md](methods-color.md) 从本地语义色系统或 `from-brand` / `from-palette` 产出 token，再填进本表。不得在既无风格库、又无配色系统、也无组件库依据时凭空选色。
5. 对每个实际使用的前景/背景组合，覆盖 default、hover、pressed、focus、disabled 以及亮暗主题和多层表面，记录实测对比结果。运行 `python3 scripts/color_intelligence.py contrast --css <页面引入的主题 CSS>`（选色前可先用 `--preset <风格编号>` 预检），只目测或只测一个背景不能写通过。
6. 成功、警告、错误、选择、焦点和禁用等关键含义必须同时定义非颜色辅助；只换颜色不算完整状态。
7. 若同一 token 在不同主题或表面映射到不同值，逐项记录映射、继承关系和作用域，不允许实现者自行推断。

**产出**：实现级语义色 token 记录、状态映射和对比验证记录。  
**完成证据**：每个已使用 token 有来源或候选状态、实际值或系统引用、完整状态、前景/背景、主题与表面映射、适用范围和实测结果；关键状态不只靠颜色。  
**不得替代**：品牌色规范和无障碍实测。

## V3 字体与密度

**触发问题**：字体和密度是否匹配任务并保持信息层级？  
**最低输入**：UI 层级、内容长度、使用场景。  
**跳过**：字体和密度由正式系统锁定。

**步骤**

1. 沿用正式字族、fallback、字体文件和版本；记录授权或系统可用性。无正式系统时，只有在明确委托或可追溯依据下才能提出候选，不能把默认选择写成品牌字体。
2. 每个排版角色形成以下实现记录：

```text
Typography Token ID：
角色及用途：
字族与 fallback：
字族来源、文件或系统引用、版本及授权状态：
字号：
行高：
字重：
字距：
最大行宽或文本容器限制：
各实际值的来源或系统引用：
值状态：CONFIRMED / CANDIDATE_PENDING_CONFIRMATION / MISSING / BLOCKED
适用范围：页面 / 组件 / 平台 / 语言 / 宽度 / 状态 / 版本
```

3. 每种密度模式形成 spacing token 记录，写明 token ID、实际值或系统引用、来源、组件内边距、组内间距、组间间距、布局沟槽、触控或点击区域及适用范围。操作密集任务可减少装饰并保持组内紧凑，浏览任务可增加留白和图像，但两者都不能改变已确认的信息和行动层级。
4. 所有字号、行高、字重、字距、行宽和 spacing 实际值都必须来自正式系统、`V0` 风格参数包、组件库默认主题，或 `scripts/typography_intelligence.py` 按风格族与语言选出的结果（见 [methods-resource-routing.md](methods-resource-routing.md) `TY`）。目标语言含中日韩时必须带 CJK 字族。0→1 无正式系统时直接采用并标注“可按品牌规范替换”，不能凭经验随手编值。
5. 建立内容压力测试记录：使用目标范围内可取得的真实最长标题、正文、标签、按钮、数字、日期和错误信息，记录内容 ID、来源、语言、字符或词数、页面、组件和状态。真实最长内容缺失时标 `MISSING`，不能用短假文案宣称已通过。
6. 在最窄受支持视口或容器宽度检查换行、截断、溢出、层级、点击区域和相邻组件，记录准确宽度、页面、状态、截图或检查结果及修复去向。
7. 对所有目标语言逐项检查字形覆盖、fallback、字重可用性、断行、标点、数字格式、文本扩张、从右到左方向及混排中实际适用的项目；没有覆盖的语言标 `NOT_TESTED`，不能泛称“多语言通过”。

**产出**：实现级排版 token、密度与 spacing token、真实内容压力测试记录。  
**完成证据**：字族、角色、字号、行高、字重、字距、行宽和间距均有来源、系统引用或候选状态；真实最长内容、窄宽和全部目标语言有可追溯检查结果，次要信息不压过主任务。  
**不得替代**：UI 信息层级。

## V4 气质句

**触发问题**：视觉气质如何变成可执行约束？  
**最低输入**：品牌目标、使用情境或明确委托。  
**跳过**：只做严格还原。

写：`气质 = 两个可观察特征；不做 = 三条具体禁令；来源 = 准确材料或委托；范围 = 页面 / 组件 / 平台 / 版本。`  
禁用“高级、国际化、有灵魂”等无法验收的词。
无正式品牌依据时只能写待确认候选，不把气质推导成未经确认的颜色、字体或资产值。

**产出**：气质与禁令。  
**完成证据**：第三人可以据此判断符合/不符合。  
**不得替代**：完整品牌战略。

## V5 图标与图片

**触发问题**：图像资产是否帮助识别、内容或信任？  
**最低输入**：内容职责、真实资产或资产要求。  
**跳过**：无图任务。

**步骤**

1. 按代表页面和状态枚举所有图标、标志、照片、插画及其他必需视觉资产；图标不承担唯一信息，一套内的网格、尺寸、描边、端点和填充规则保持来源一致。
2. 每项资产建立以下 manifest，禁止用笼统“后补图片”代替：

```text
资产 ID：
资产类型：
用途及出现位置：
来源及授权：创建者 / 提供方 / 链接或库 / 许可范围 / 到期或限制
文件及版本：准确文件名或路径 / 格式 / 版本或日期 / 变体
尺寸与比例：源尺寸 / 目标尺寸或密度 / 宽高比
裁切规则：焦点 / 安全区 / 各断点裁切或禁止裁切
真实内容要求：必须呈现的对象、地点、产品、语言、数据或状态；不得出现什么
当前状态：APPROVED / AVAILABLE_UNVERIFIED / NEEDS_EXPORT / NEEDS_LICENSE / MISSING / BLOCKED
责任人：
缺失阻断：受影响页面或组件 / 被阻断产物 / 所需输入 / 恢复条件
```

3. 图片必须与任务相关，并满足 manifest 中的真实内容要求；真实内容、授权、文件版本或裁切信息不足时，受影响成品保持阻断。
4. 将实际装载文件与 manifest 的文件、版本、尺寸比例和裁切逐项对照；错版本、低清导出、错误比例或未经授权的替代均不得通过。
5. 缺资产时请求准确导出或授权，不随机寻找相似素材，不使用占位、表情、假内容或简化图形冒充成品。
6. **IconScout 双通道真实资产调取（优先官方 MCP `https://mcp.iconscout.com/mcp` + 内置 v3 API 脚本自动兜底，用于 `icon` 图标、`3d` 图标、`lottie` 动画、`illustration` 插画）**：
   - 当项目中需要工具图标、金刚区 3D 图标、空状态/引导页插画或 Lottie 微动效且无现成内部资产时，按 **「通道 A（MCP 优先）→ 通道 B（内置 API 脚本零配置兜底）」** 执行：
   - **通道 A｜优先检测并调用 IconScout 官方 MCP Server（支持自然语言搜同系列 Pack、改色与直下 `.svg / .json` 源文件）**：
     1. 先检查当前宿主环境是否已连接 `iconscout` MCP（Cursor 用 `GetDynamicTools`，Codex 看可用工具列表）。通过 `fusion-product-agent` 插件安装时，插件已自带 IconScout MCP 声明（插件根目录 `.mcp.json`），无需用户手动添加。
     2. **已连接**：直接调用 IconScout MCP 工具，支持用自然语言描述风格与色板、拉取同一视觉系列的配套资产（Consistent Pack），并直接按用户账号权限下载 `SVG`、`PNG`、`Lottie JSON`、`GIF` 或 `MP4`。
     3. **未连接：Agent 直接替用户安装，不询问、不只给提示**（地址：`https://mcp.iconscout.com/mcp`，参考 `https://iconscout.com/mcp`，无需 API Key）：
        - 按当前宿主执行下方对应的安装动作：能跑命令的直接跑命令；需要改配置文件的，先读取现有配置，只追加 `iconscout` 一项，保留其他服务和格式不变，已存在则跳过。
        - 安装后立即发起登录（如 `codex mcp login iconscout`），浏览器会弹出 IconScout 授权页；用一句话告诉用户“浏览器弹出了 IconScout 登录页，点一下授权即可”。这一步是账号授权，只能由用户本人点击。
        - 新装的服务通常要新开会话或重载后才可用：**本轮不等待**，先用下方通道 B 内置脚本完成素材获取，下一轮起自动走 MCP。
        - 只有宿主不允许 Agent 执行命令或写配置文件时，才把下方对应的安装方式原样给用户。
        - **Cursor / Claude Desktop / Windsurf**：在用户级 `mcp.json`（Cursor 为 `~/.cursor/mcp.json`）的 `mcpServers` 中追加：
          ```json
          {
            "mcpServers": {
              "iconscout": {
                "url": "https://mcp.iconscout.com/mcp"
              }
            }
          }
          ```
        - **Claude Code CLI**：`claude mcp add --transport http iconscout https://mcp.iconscout.com/mcp`
        - **Codex**：通过 `fusion-product-agent` 插件安装已自动包含，只需运行 `codex mcp login iconscout` 登录；单独使用本 Skill 时先运行 `codex mcp add iconscout --url https://mcp.iconscout.com/mcp`，再运行登录命令。
        - **ChatGPT**：`Settings -> Connectors -> Add custom connector`，填入 `https://mcp.iconscout.com/mcp` 并完成浏览器登录授权。
   - **通道 B｜内置 IconScout v3 REST API 脚本自动兜底（免安装、开箱即用）**：
     - MCP 刚安装尚未生效、登录未完成或宿主无法安装时，**严禁卡死流程或退回手画劣质 SVG**，立即自动调用本 Skill 预置的 v3 API 脚本（已内置 `Client-ID: 232598791050530`，文档：`https://api-docs.iconscout.com/#description/credits-and-limits`，OpenAPI：`https://cdn.iconscout.com/openapi.json`）：
     - **直接调用命令**：`python3 scripts/iconscout.py search -q "<英文关键词>" -a <icon|3d|lottie|illustration> -s <风格> --icon-grid 24 -d <本地保存目录>`（在 `design-thinking-os` Skill 目录下执行）
   - **与 `V0` 第 6 维图标/配图风格的精确参数映射（MCP 与 API 通用）**：

| `V0` 选定的图标/配图类型 | IconScout `asset` 参数 | IconScout `styles[]` 过滤参数 | 附加参数与一致性要求 |
| :--- | :--- | :--- | :--- |
| **人物头像 / 用户形象（Avatar）**（唯一需要额外把关的类别：库内通用人物多为欧美职场画风，问题是风格不匹配，不是 3D 不能用） | `3d` 或 `illustration`，先检索并过「文化风格 + 同套系判断门」；**不匹配则立即转 AI 同母体成套生图** | 插画用 `flat / dualtone`；3D 人物只要画风、人种面孔、服饰与产品母体一致即可采用（如欧美社交/SaaS 产品可直接用） | 先看产品文化母体（如掼蛋/国风需东方形象与新中式画风）且同屏必须 100% 同风格；**库里无匹配同套系素材时，禁止强凑，自动走 AI 锁定统一风格前缀成套生成** |
| 精致细线性图标（1.5–2px） | `icon` | `line` 或 `rounded` | `--icon-grid 24`，全套保持同一 `styles[]` 或同一 Pack |
| 醒目面性 / 填充图标 | `icon` | `glyph` 或 `flat` | `--icon-grid 24`，用于选中态或高权重入口 |
| 双色 / 线面结合图标 | `icon` | `dualtone` 或 `colored-outline` | `--icon-grid 24`，金融/生活服务金刚区常用 |
| 微质感 / 渐变图标 | `icon` | `gradient` | 适合核心宫格入口提亮品质 |
| 3D 质感图标 / 道具 / 徽章 / 主题物件 / 海报主视觉立体物 | `3d` | —（可加 `isometric`） | **3D 库是主力素材源，覆盖面远不止金币**：功能入口图标（钱包/日历/定位/消息/设置/购物车）、行业主题物（机票/行李箱/地标/酒店/银行卡/盾牌/图表）、游戏与活动道具（宝箱/骰子/扑克/卡牌/奖杯/勋章/礼盒/红包/灯笼/火箭）、等级徽章与成就、空状态/引导主视觉。按关键词 + 同一 Pack 拉齐材质、光源与配色后，获取高清透明底 `PNG`，用于金刚区、卡片、弹窗、活动页或**快速拼装海报/主视觉 KV**；唯一检查点是同屏同材质同打光，不因"是 3D"而降级 |
| 扁平现代矢量 / 等轴插画 | `illustration` | `flat` / `dualtone` / `isometric` / `colored-outline` | 用于空状态、引导页、卡片配图或**快速拼装运营海报** |
| 温暖手绘风插画 | `illustration` | `doodle` | 仅限轻松消费/社区场景，严肃行业禁用 |
| **真实专业摄影 / 高清真实场景 / 地点地标** | **不走 IconScout** | — | 按 [methods-image.md](methods-image.md) 运行 `scripts/real_image.py`；无匹配或必须虚构才转 `V7` 生图 |
| 轻量矢量动画 / 微动效 | `lottie` | — | MCP 直接下 `Lottie JSON / GIF / MP4`；API 脚本免密直取预览 `MP4/PNG`（可直接嵌入动态海报或 UI） |

   - **API 通道鉴权与额度边界**：
     - 仅靠预置 `Client-ID: 232598791050530` 即可免费调用 `GET /v3/search` 与 `GET /v3/items/{uuid}`，直接拿回可用的高清 CDN 预览文件（图标 `png_64/128/256`、3D 与插画透明底 `thumb` PNG、Lottie `thumb` MP4 与 `preview_image`）；
     - 若走 API 通道下载源文件（`svg` / `json` / `lottie` / `glb`）、调用格式转换 `POST /v3/convert/{operation}`（如 `svg-to-lottie`、`lottie-to-gif`、`lottie-to-webp`、`lottie-to-mp4`）或 `POST /v3/ai/{operation}`，需同时传入 `Client-Secret`（或直接使用已登录的通道 A 官方 MCP）。
7. **人物头像与主题素材的「先问用户偏好（卡通 vs 插画 vs 真人）+ 同屏成套判断 → AI 同母体成套生图」闭环**：
   - **Step 1｜在第一轮提问时先确认用户想要的头像画风（不要擅自生成写实真人头像）**：
     - 凡界面包含玩家或用户头像（如棋牌四家、社交/社区用户、角色席位），在第一轮征求视觉风格时，顺带问清用户偏好哪种头像表现形式：**① 3D 潮玩 / Q 版卡通头像**、**② 国风 / 精致半身插画头像**、还是 **③ 写实人物肖像**。
   - **Step 2｜素材库检索后的「两问判断门（Library Fit Gate）」**：
     - 从 IconScout（MCP 或 API）检索候选素材并调用 `Read` 读图检查，同时回答两问：
       1. **符合用户选定的画风与产品文化语境吗？**（如中国风游戏里搜出来的是金发卷毛大胡子欧美橡皮泥人 → **判定不匹配**）；
       2. **同屏多个头像能凑齐同一套系（100% 同一画风、同一头肩比、同一打光与底色）吗？**（如 4 个玩家来自不同作者、画风割裂 → **判定不匹配**）。
   - **Step 3｜判断通过 vs 不通过的自动分流**：
     - **✅ 两问皆通过**：直接采用素材库中该同一套系（Same Pack）的资产；
     - **❌ 任一问不通过（库里没有符合该画风或凑不齐同风格成套头像）**：**立即放弃素材库结果，严禁将就硬塞，严禁用“名字首字圆圈”充数，自动按用户选定的头像画风切换走「AI 同母体成套生图（Batch Style-Locked Generation）」**！
   - **Step 4｜AI 同母体成套生图的锁死规则**：
     - 固定一套完全相同的 **【母体风格前缀词（Master Style Prefix）】**：严格按用户选定的画风（Q版3D潮玩卡通 / 新中式国风插画 / 写实人物）锁死画风、人物文化特征、构图（居中胸像占 75%）、光影与背景底色（与界面同频的深翠绿/暗金渐变底，禁死板纯黑底）；
     - 仅替换每个角色的人设变量，成套调用生图模型（宿主 `GenerateImage` / `imagegen`）生成，保证一个界面上的所有头像 100% 像同一个美术主笔画出的一整套！
8. 界面资产在 Figma UI 范围内完成：图标/3D/插画先用 IconScout；**真实场景、建筑、自然、地点、生活摄影先按 [methods-image.md](methods-image.md) `IM` 检索并 `get` 到本地**，再导入 Figma 或 HTML。只有搜不到合适真图、或画面必须虚构时，才按 `V7 路径 A` 原位生图。Figma 未连接时，把真实图或生成图放入 HTML/代码界面。只有用户方才有的素材（Logo、真实产品图等）无法取得时，才标 `BLOCKED/WAIT_EXTERNAL` 并向用户要，不自动扩成独立视觉工具任务。只有用户明确建立独立视觉成品或资产委托（如海报、运营图、KV）时，才将 manifest 作为 TR4 与 `V7 路径 B` 输入；外部产物验收后记录准确文件与版本，再按需回到 Figma 完成界面内应用。

**产出**：可交付实现的资产 manifest、缺失阻断和恢复清单；若存在明确独立视觉资产委托，附视觉工具动作 ID、已确认文件版本和 Figma 导入位置。  
**完成证据**：每项已用资产都有 ID、用途、来源与授权、准确文件版本、尺寸比例、裁切、真实内容要求、状态和责任人；所有缺失项明确阻断范围，无无关图片、假内容或占位符冒充成品。  
**不得替代**：版权和品牌授权。

## V6 同结构候选

**触发问题**：没有既定基线且确实需要人做视觉方向选择。  
**最低输入**：已确认的同一内容、结构、状态和代表页面。  
**跳过**：已有设计系统、存量迭代沿用基线、或用户已明确委托方向。

**步骤**

1. 每轮先冻结内容、信息层级、结构、行为、资产、数据、平台、视口、页面状态及不在本轮比较的 token，并记录准确版本。
2. 每条比较记录只能有一个唯一变化变量；为该变量提供 2–3 个有依据且标为待确认的候选值。若需比较另一个变量，另开一轮并重新冻结基线。
3. 使用关键任务的代表页面及实际相关状态，至少覆盖正常状态和会暴露差异的 hover、pressed、focus、disabled、空、错误或长内容状态；不用闪屏或纯情绪板代替。
4. 在同一设备、视口、内容、状态和资产条件下，比较主行动可见性、关键判断、状态辨识、对比、内容承载和品牌边界，并保留结果证据。
5. 每轮填写：

```text
比较 ID 及待回答问题：
固定变量及准确版本：
唯一变化变量：
候选 ID、值、依据和状态：
代表页面、视口及状态：
比较标准：
逐候选比较结果及证据：
结论：推荐 / 不推荐 / 无结论
确认人及其权限：
当前状态：DRAFT / READY_FOR_REVIEW / PENDING_CONFIRMATION / CONFIRMED / REJECTED / NO_CONCLUSION / BLOCKED
选择来源、适用范围及可吸收部分：
```

6. 未经有权的人确认，结果保持 `PENDING_CONFIRMATION`。如果一轮同时改变了多个变量，该轮不能把结果归因到任何一个变量，也不能据此确认 token；必须拆分并重做单变量比较。

**产出**：每轮 2–3 个同结构、单变量真实候选及完整比较记录。  
**完成证据**：固定变量、唯一变化变量、代表页面与状态、比较结果、确认人和当前状态完整；候选差异可解释，未确认前不称确认。  
**不得替代**：用三套结构不同的方案假装视觉比较。

## VT 按最终交付物类型选择工具与工作流（UI 进 Figma 拼装再还原 Demo / 单图出提示词与垫图调生图 / 海报搜素材进 Figma 拼装或双垫生图）

**触发问题**：交互形式（`I1–I6`、`U4`）和视觉风格（`U0` / `V0`）确定后，根据本次最终要交的是「UI 界面 & 可交互 Demo」「单张图片资产」还是「海报/运营图」，分别走哪条工具链路？  
**最低输入**：已确认的产出类型、页面职责与交互形式、`RR` 同类竞品参考、`U0/V0` 选定的风格预设、从 IconScout 与 Real Image Library 调取的真实素材。  
**跳过**：只替换已批准文案；已有正式设计定稿且任务仅还原。

### 三类交付物的标准工具工作流（严禁混用）

| 最终交付物类型 | 标准工具工作流 | 核心纪律与原因 |
| :--- | :--- | :--- |
| **1. UI / 产品界面**<br>*(最终要接入 Product Agent 做出可交互 Demo 或 Figma 稿)* | **先用本地组件库 + 素材库搭出高保真 HTML 组件页 → 再按需用 `generate_figma_design` / `html_to_figma` / `send_code_to_figma` 一键转入 Figma**<br>1. **一律先在本地让所有库 100% 生效**：运行 `component_recipe.py copy`（`recipes.css`）、`style_preset.py`（`theme.css`）、`iconscout.py`（真实图标/3D）、`real_image.py` / 成套头像生成，搭出高保真 HTML/前端页面，在内置浏览器（`127.0.0.1`）预览并跑通 `verify_library_usage.py`、`ui_geometry_audit.py`、`style_consistency_audit.py`、`color_intelligence.py`；<br>2. **需要进 Figma 时，直接把本地高保真页转入 Figma**：调用 Figma MCP 的 `generate_figma_design` / `html_to_figma`（转为可编辑 Figma 图层）或 `send_code_to_figma`（转为可运行 Code Layer）。<br>**严禁打开 Figma 左边栏自带的 `Agents` 聊天框让它徒手画丑方块，也严禁调 `use_figma` 手写平涂矩形！** | Figma 云端自带的 `Agents` 读不到本地 `recipes.css`、`shadcn` 和 IconScout 素材，只会徒手画平涂简陋方块；必须先在本地用组件库做出高保真页面，再捕获/转换进 Figma |
| **2. 单张图 / 视觉图像资产**<br>*(概念图、插画、角色头像、局部材质/背景图)* | **Codex 产出结构化提示词（Prompt）+ 准备参考垫图（`reference_image_paths`）→ 直接调用生图工具（`GenerateImage` / Figma `generate_image`）** | 交付物本身就是图像时，重点是锁定画风、构图与光影，用精选垫图 + 结构化提示词直接出图 |
| **3. 海报 / 运营图 / Banner / 主视觉 KV**<br>*(见下方 `V7 路径 B`)* | 先定图文占比与**版面结构草图（`layout_sketch`）**，二选一：<br>1. **搜索素材去 Figma 拼装**：从 IconScout 搜透明底 3D/插画素材、从 `real_image.py` 搜真图，导入 Figma 配合 Figma AI / 版式底板与矢量文字拼装；<br>2. **垫图 + 提示词调生图工具**：先搜 2–3 张风格参考图让用户选定感觉（`style_ref`），再拿「结构草图 + 风格垫图 + 提示词」调生图工具 | 复杂版式（如上下结构、多模块）在 Figma 里搜素材拼装最清晰可控；需要全画幅光影融合时用双垫生图 |

### 关键执行纪律

1. **绝不让 AI 现画简陋图标或手写劣质 SVG**：界面里的所有功能图标、装饰图标、3D 元素、插画、Lottie，一律先走 **IconScout**（MCP 或 `scripts/iconscout.py`）或成熟开源图标库；真实风景/建筑/人文配图一律先走 **Real Image Library**（`scripts/real_image.py`）。
2. **需要垫图生成时，先搜参考图选感觉**：无论是复杂游戏 UI 还是风格化海报，不要只靠干巴巴的文字提示词盲生。先从 `RR` 或风格参考图里选定最对味的那张图作为 `reference_image_paths` 垫图，再结合我们自己的界面结构生成。
3. **重材质部件必须用图片资产，不拿简陋 CSS 充数**：当游戏 UI 或强质感页面需要写成 HTML/代码时，牌桌绒面与木框、完整扑克牌面（含角标与牌心花色）、立体高光按钮皮肤、字标等代码画不出的部分，必须切图或生成透明底图片资产贴入，CSS 只负责布局与交互状态。

**产出**：高保真 UI 视觉稿 / Figma 主稿 / 材质件资产包与前端实现。  
**完成证据**：工具选择符合上表规律；所有图标/配图有真实素材库来源；与 `RR` 同类标杆并排对比（`side_by_side.py`）不掉档。  
**不得替代**：未完成交互形式判断（`I1–I6`、`U4`）前，不得跳过交互直接画视觉。

## V7 视觉素材拼装与图片生成双路径协议（IconScout 快拼 / 真实摄影 / 必要时才 AI 生图）

**触发问题**：当任务需要人物头像、图标、3D 元素、插画、真实摄影配图，或需要制作独立运营图/海报/主视觉（KV）时，何时用 IconScout、何时用真实图库、何时才调 AI 生图？  
**最低输入**：视觉用途（UI 内部元素 vs 独立海报/主视觉交付）、核心传达信息与尺寸比例。  
**跳过**：纯文字/纯组件界面且无任何图标、头像、图片或海报需求。

> **核心选型铁律（分清每个库管什么，不走无用功，更不跳过必调库）**：
> 1. **禁止“只看不用”**：调取组件配方库（`component_recipe.py`）必须执行 `copy <配方ID...> --to <目录> --preset <风格编号>` 实际落盘并复用其完整样式（渐变、高光、阴影、尺寸），**严禁只运行 `show` 看一眼就自己用 `use_figma` 手画平涂纯色块！**
> 2. **禁止在 0→1 空白 Figma 文件里白搜 `search_design_system`**：新建的空白 Figma 文件没有业务组件库（只会搜出无关的 Material 通用卡片），0→1 任务直接跳过 `search_design_system` / `get_libraries`。
> 3. **工具/装饰图标（Icon）、3D 立体图标与道具（3D）、标准场景插画（Illustration）、轻量动画（Lottie）**：**必须实际执行 IconScout（官方 MCP 或 `scripts/iconscout.py search ... -d <目录>`）检索下载落盘**，严禁手画 SVG，也严禁去 GitHub 乱扒第三方老旧剪贴画（如 `SVG-cards`）替代。
> 4. **人物头像（User Avatar）**：**必须实际执行检索或成套生成，严禁用“名字首字文字圆圈（如 周/林/宁/我）”回退充数！** 先搜 IconScout 并过 `V5` 第 7 条「文化风格 + 同套系判断门」；库内无匹配同套系头像时，立即用统一风格前缀调用 AI 生图成套生成真实头像图片。
> 5. **真实世界摄影 vs 游戏/UI 表面材质（边界分清，不白跑）**：
>    - **真实世界摄影（风景、城市地标、建筑、人物生活）**：必须走 [methods-image.md](methods-image.md) `IM`，用 `scripts/real_image.py` 检索下载；
>    - **游戏/UI 表面纹理材质（如牌桌丝绒台呢、胡桃木边框、金属/宝石底纹）**：不属于真实风景摄影，**不需要跑 `real_image.py`**，直接用预设纹理或原位生图生成局部材质贴图。
> 6. **快捷生成海报 / 主视觉（KV） / 运营 Banner**：能用 **「清晰版式底板 + 真实矢量文字 + IconScout 透明底 3D/插画」** 完成的，先快拼。需要全画幅真实场景时，先从真实图库取图再叠字；只有虚构合成或图库无匹配时，才走整图 AI 生图。

### 路径 A：UI 界面内头像 / 图标 / 配图 / 背景（IconScout + 真实摄影；必要时才原位生图）

适用：元素是 UI 页面的一部分，服务于用户资料、金刚区入口、卡片、Banner 位、头部背景或空状态。

1. **优先按「文化风格匹配 + 同屏成套判断门」获取头像与透明底道具/图标**：
   - **人物头像（先搜库做文化与成套判断 → 不匹配立即转 AI 同母体成套生图）**：先识别产品的文化语境（如掼蛋/麻将/国风产品需中国风东方形象）；若素材库（IconScout）中没有符合该文化风格且同一套系（Same Pack）的高颜值成套头像，**立即放弃素材库结果，改用统一风格前缀词调用 AI 生图成套生成**（严禁拿欧美豆豆眼 3D 泥人或代码手画 SVG 简笔人脸充数）！
   - **图标 / 3D 图标与道具 / 徽章 / 主题物件 / 空状态插画**：按 `V5` 映射表从 IconScout 拉取同系列素材导入 Figma。3D 库覆盖功能入口、行业主题物、游戏与活动道具、徽章成就等大量品类，是默认首选；只需保证同屏同 Pack、同材质、同打光。
2. **真实摄影配图 / Hero / 氛围背景（先 Real Image Library，禁止跳过直接生图）**：
   - 主题、构图、比例、冷暖明确后，运行 `python3 scripts/real_image.py search "<主题>" --role hero|card|background|place --tone <warm|cool|neutral|dark|green>`；
   - 用 `Read` 看预览，按角色选图（Hero 要横构图和叠字留白，卡片要主体清楚，地点要能认出那个地方）；
   - `get` 到本地，写入资产 manifest（作者、许可证、作品页），再填进 Figma 图层或 HTML。
3. **Figma 原位调用 AI 生图（仅当真实图库无匹配，或画面必须虚构时）**：
   - 直接读取当前 Figma 目标图层的宽高比、已确认的 `V0` UI 风格、主色与冷暖色调；
   - 优先通过 Figma MCP 原生生图接口（如 `generate_image` 直接传入目标 `fileKey` 与 `nodeId` 替换图层填充，或调用 Figma Weave 生图模型），或由 Codex / Agent 通过 GUI 操作调用 Figma 内置生图插件，在目标 Frame 图层内原位生成。

### 路径 B：独立海报 / 运营图 / 主视觉 KV（先定结构草图 → IconScout 快拼 / 真实摄影 / 必要时才 AI）

适用：最终交付物本身是一张运营图、活动海报、宣发主视觉（KV）或社媒配图。**严禁跳过版面结构分析直接写一段提示词盲目生图。**

#### Step 1：先判断图文角色与占比（谁是主角？）

根据这张运营图要传达的核心信息，先定 3 种角色模式之一：

- **模式 A｜画面主导型（图占 70%–90%）**：靠视觉冲击、产品特写或氛围吸引点击（如新品首发、穿搭/美食/旅行大图）。图片占绝对主体，文字浓缩为极简标题嵌入留白区。
- **模式 B｜标题/信息主导型（字占 50%–70%，图只做装饰或局部点缀）**：大促折扣、核心利益点喊话、规则通知、战报。主标题和利益点必须极大极醒目（并同步确定标题造型：超大强对比色块字 / 3D 立体膨胀字 / 金属质感字 / 手写书法字）；图片只做角落装饰、底纹或小主体，严禁抢夺标题注意力。
- **模式 C｜图文均衡型（图 50% + 字 50% 分区）**：活动宣发、课程/沙龙海报、功能介绍卡。采用上下分割、左右分割或中心构图，图文各守一区、互不遮挡。

#### Step 2：画出「海报版面结构草图（Layout Sketch）」并选择制作方式（快拼 / 真图 / 必要时才 AI）

先根据 Step 1 产出一张可视化的 **结构草图**（可用 HTML/SVG/Figma 快速排出并导出为 `layout_sketch.png`），明确标出 `L1 主标题 / L2 副标题利益点 / L3 时间地点规则 / L4 品牌 Logo 与行动区` 的字号比例、位置和配图区域，然后按下面三条决定制作方式：

- **制作方式 1｜IconScout 素材快捷拼装模式（默认优先推荐：适合模式 B / 模式 C、功能发布 KV、嘉宾/人物海报、常规运营 Banner）**
  - **为什么优先**：不需要整张图跑 AI 生图！文字 100% 矢量锐利无乱码，每个元素位置大小随时可改，出图极快。
  - **怎么拼装**：
    1. 在 Figma 或 HTML/CSS 画布中，按 `V0` 风格参数搭好背景底板（纯色、弥散光晕渐变、Bento 色块或几何网格线）并排好 L1–L4 真实文字层级；
    2. 调用 IconScout（MCP 或 `scripts/iconscout.py`）检索拉取高清透明底的 **主视觉 3D 模型（`--asset 3d`，如礼盒、奖杯、火箭、金币、地球）、主题插画（`--asset illustration`）、嘉宾/人物头像（`user avatar`，须先过 `V5` 第 7 条判断门，不通过改为 AI 成套生成）或装饰角标（`--asset icon`）**；
    3. 将透明底素材按结构草图摆放到主视觉区或标题四周做层次穿插，直接合成导出高清海报！
    4. **若需动效版海报**：可直接从 IconScout 拉取同主题 **`--asset lottie` 动态元素** 嵌入版面并导出为 `MP4 / GIF / 动态 WebP`，连生视频模型都无需调用即可获得丝滑动态海报。
- **制作方式 2｜全画幅真实摄影或整图合成（先图库，再必要时 AI）**
  - `KV-03` 商业静物摄影、`KV-08` 胶片生活纪实，以及任何「真实地点 / 真实风景 / 真实人文」主题：**先按 [methods-image.md](methods-image.md) 取一张真图**，按结构草图裁切并叠矢量字。能成稿就结束，不跑整图生图。
  - 只有图库无匹配、或必须虚构光影一体合成时，才继续执行下方 Step 3–Step 4 的 AI 双垫生图。

#### Step 3：从运营图风格表选 2–3 个方向，「搜索直观风格参考图」给用户看图挑选垫图

1. 不搜竞品业务截图，而是按下方「运营图 / KV 专用风格表」挑选 2–3 个契合主题的美学/材质/光影方向，搜索或调取对应的直观风格参考图。
2. **把 2–3 张参考图并排展示给用户挑 1 张**作为风格参考垫图（`style_ref.png`）；用户已提供参考图时直接用用户的，不再展示。这是海报流程里固定要问的一步：只问“挑哪张”，每张配一句大白话描述观感，首张标推荐，不出现风格编号或品牌名。
3. 怎么垫（只垫材质光影与色调 / 垫构图+画风 / 垫真实产品白底原图生成周边场景）、主色调与标题质感由 Agent 按选中的图和主题直接决定，不另外追问。

| 编号 | 运营图风格名称 | 直观画面与材质特征 | 搜索参考图关键词（中 / 英） | 适用运营场景 |
| :--- | :--- | :--- | :--- | :--- |
| `KV-01` | **C4D / 3D 礼盒微距渲染风** | 圆润精致 3D 模型、柔和全局光照、磨砂塑料与金属混合材质、悬浮几何元素 | `3D Blender C4D podium product render pastel studio lighting` / `C4D 电商微距渲染 运营海报` | 大促活动 Banner、会员权益图、互联网功能发布 |
| `KV-02` | **清透亚克力与液态玻璃风** | 半透明折射玻璃、柔和弥散彩色光斑、极简几何空间、通透科技质感 | `abstract frosted glass acrylic refraction dispersion 3d art` / `液态玻璃 亚克力折射 海报背景` | AI/科技新品发布、金融高端权益、美妆/数码质感海报 |
| `KV-03` | **杂志级商业静物摄影风** | 真实自然阳光树影或影棚布光、极高材质真实感（水滴、织物、木纹、石材） | `editorial still life product photography natural shadow sunlight` / `静物商业摄影 光影质感` | 品质消费品、咖啡茶饮、家居生活、实体商品宣发 |
| `KV-04` | **软萌粘土 / 膨化玩具风** | 彩色软陶或充气膨胀材质、圆润饱满、温暖治愈、高亲和力 | `3d claymorphism inflatable puffy cute illustration` / `3D 粘土风 膨胀材质 插画` | 节日打卡活动、教育/亲子、宠物、年轻化社媒互动图 |
| `KV-05` | **新中式东方美学 / 国潮风** | 宣纸肌理、留白意境、工笔/水墨晕染结合现代几何、黛青/朱砂/鎏金传统色 | `modern oriental aesthetics minimal ink wash gold foil poster` / `新中式 东方美学 节气海报` | 传统节气/节日营销、茶饮/东方品牌、文旅文创活动 |
| `KV-06` | **现代扁平噪点插画风** | 明快几何色块构图 + 细腻复古颗粒噪点肌理、人物或生活场景故事感强 | `modern flat vector illustration grain texture editorial` / `扁平肌理感插画 运营配图` | 品牌故事、生活服务长图、社区话题头图、引导页大图 |
| `KV-07` | **暗黑赛博 / 酸性金属流体风** | 深色背景、液态铬金属反射、霓虹流光或高对比荧光色、未来先锋感 | `dark futuristic liquid chrome iridescent 3d abstract` / `液态金属 酸性设计 潮流海报` | 音乐节/演出、潮玩首发、电竞游戏活动、夜经济营销 |
| `KV-08` | **温暖胶片生活纪实风** | 真实人物或生活一角、微颗粒胶片色调、温暖自然光、松弛不摆拍 | `warm film photography lifestyle candid natural light` / `胶片感 生活方式 摄影` | 旅行/民宿、心理健康、社区氛围、人文故事型 Banner |

#### Step 4：「结构草图 + 风格垫图 + 结构化提示词」双图同垫喂给生图模型

调用生图工具（如宿主生图工具 `GenerateImage`、Nano Banana / GPT-Image / Gemini Image 等）时，将 **两张垫图 + 结构化提示词** 一并传入：

```text
垫图输入 (reference_image_paths)：
1. 结构草图 (layout_sketch.png)：锁定版面构图、标题与信息块位置、图文面积比与留白区
2. 风格参考图 (style_ref.png)：锁定渲染材质、光影氛围、色调与艺术画风
（若有真实产品原图，作为第 3 张主体垫图传入）

结构化提示词 (Prompt)：
- 【构图与版式指令】：严格参照参考图 1 的版面结构、图文占比与留白区域排布；
- 【风格与材质指令】：严格采用参考图 2 的视觉画风、材质表现与光影色调；
- 【画面主体与文案信息】：具体主体物细节 + 标题/副标题内容及造型要求（或留出纯净留白区由设计工具精准叠字）；
- 【色彩与布光】：主色、辅助色与光线方向；
- 【纯净度约束】：禁止无关杂物、禁止错乱伪文字、保持文字区背景干净可读。
画幅比例 (aspect_ratio)：1:1 / 3:4 / 4:3 / 16:9 / 9:16
```

#### Step 5：静态海报/单图交付后的「动效版升级判断与预期对齐」（场景支持时必须用提问工具问用户）

当用户的原始需求是生成一张海报、运营图或单图时，Agent **必须主动判断该图的使用场景是否支持动图、以及做成微动图是否效果更好**：

1. **先判使用场景是否支持并受益于动图**：
   - **不支持或不宜动（直接只交静态图，不提）**：线下印刷海报/易拉宝、纯文字规则长图、严禁闪烁的严肃公告。
   - **支持且动图明显更吸睛**：App 开屏、首页弹窗、Banner/金刚区、网页 Hero 首屏、微信朋友圈/公众号嵌入 GIF、小红书/社媒动态封面、电子邀请函、新品发布 KV。
   - **用户原话已要求动图**：直接做动效版，不问。
2. **支持动图时，交付静态图后用提问工具（如 `AskQuestion` / 宿主原生提问）明确问用户要不要动态版**，选项为“要，做一版动态版”（首项推荐）/“不用，静态就够”：
   - 问题示例：*“这张图投放的位置支持动图，做成微动态通常比静态更抓眼球。要不要再出一版背景和主体微动、文字保持清晰的动态版（GIF / 动态 WebP / MP4）？”*
   - **问题里用一两句大白话说明真实效果预期（管理预期，不夸大）**，按以下标准判断能做什么：
     - **能做到的高质感效果（微动氛围 Loop）**：
       1. `光影与材质流转`：液态玻璃折射流光、金属边缘高光扫过、霓虹呼吸闪烁、自然阳光树影摇曳；
       2. `主体微动态`：3D 礼盒/核心产品轻微悬浮或缓速自转、热气/云雾升腾、水面涟漪、粒子/气泡/花瓣缓慢漂浮；
       3. `镜头呼吸感`：极缓慢的推进（Slow Zoom-in）或前景背景微视差（Parallax）。
     - **明确不能靠生视频模型硬做的（防翻车说明）**：
       画面上的小字、优惠规则、二维码如果直接交给生视频模型运动，容易出现笔画扭曲或模糊。因此最佳实现方案是：**拿无字/少字的主体底图作为【首帧垫图】送入生视频模型做背景与主体微动，保持文字层清晰稳定（或后期叠字），最后导出为高清 `GIF` / `动态 WebP` / 循环 `MP4`**。
3. **用户选择“需要动效版”后的无缝衔接执行**：
   - 直接复用 Step 4 已确认的静态图（或去字版底图）作为 **【首帧静帧垫图】**，转入 [methods-tool-routing.md](methods-tool-routing.md) `TR5-B`；
   - 附上微动控制提示词（如 `subtle floating motion, soft caustic light sweeping across surface, camera gentle push-in, keep main subject structure stable, seamless loop`）；
   - 调用生视频模型生成 3–5 秒动态视频后，按投放渠道一键转码交付 **高清 `GIF`、`动态 WebP` 或循环 `MP4 / WebM`**。

**产出**：
- 路径 A：已导入图层的配图（真实摄影文件 + 授权，或仅在无匹配/虚构时的生图）及节点版本记录。
- 路径 B：图文角色判断、版面结构草图；快拼或真图成稿时无需风格垫图；走 AI 时才有用户看图挑选的风格垫图和双垫参数包；最终静态海报/运营图成品；以及（若用户选择要动态版或原话要求动图）基于静态图首帧生成的微动态版本（`MP4 / GIF / 动态 WebP`）。

**完成证据**：路径 A 配图与 UI 风格及容器尺寸一致；真实摄影能指到来源；没搜过图库就生写实图的不算完成。路径 B 具备明确的结构草图；快拼或真图能成稿则不必再选风格垫图；走 AI 时才有用户看图挑选的风格垫图。图文主次分明、标题可读、无盲目生图；支持动图的场景已用提问工具问过用户是否要动态版，并说明了效果预期。
**不得替代**：不能不经结构草图就随机出运营海报；走 AI 时不能没有用户看过的风格垫图；不能把满屏小字海报直接丢进生视频模型。

## 视觉规格通过门

- [ ] V0–V7 中本轮适用的方法均有触发问题、最低输入、准确产物和完成证据；跳过项有理由。
- [ ] UI 视觉已先做三路分流：存量延展直接复用、纯 B 端绑定公开组件库快搭、C 端 0→1 经过语境剪枝并由 Agent 选定风格与参数（仅方向高度开放时问过 1 个大白话问题）。
- [ ] 所有颜色、字体、间距、密度和资产实现值都有正式来源、系统引用或明确的待确认候选，没有编造品牌值。
- [ ] 语义色覆盖实际状态、前景/背景、亮暗主题、多层表面、非颜色辅助、作用域和实测对比（`color_intelligence.py contrast` PASS）。
- [ ] 排版与密度覆盖字族、角色、字号、行高、字重、字距、行宽、spacing token、真实最长内容、窄宽和目标语言。
- [ ] 资产 manifest 可定位到准确文件和授权；真实摄影有来源、作者和许可证；UI 内写实配图已先搜 Real Image Library，无匹配或必须虚构才原位生图；独立运营图/海报能快拼则快拼，能用真图则用真图，否则才「结构草图 + 风格垫图 + 提示词」双垫生图；图标/3D/插画已从 IconScout 获取，只有用户方素材缺失时才阻断受影响成品，没有近似降级或占位替代。
- [ ] 候选比较冻结了共同变量，每轮仅改变一个变量；结果有证据、确认人和当前状态。
- [ ] 实现者无需猜测即可制作，验收者可按来源、状态、范围和检查记录逐项判定通过、失败、未测或阻断。
