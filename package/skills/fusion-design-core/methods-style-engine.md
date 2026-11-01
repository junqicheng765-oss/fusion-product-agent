# 设计风格引擎（Design Style Engine）

风格引擎负责把一整套设计风格识别出来、选定、落成可执行的规格，并批量应用到整个产品，最后检查各页面风格是否统一。它不只找组件，而是把颜色、字体、圆角、间距、导航、卡片、交互和动效规则作为一个整体来处理。

它和其他方法的分工：
- [methods-visual.md](methods-visual.md) `V0` 负责按语境**选**风格（26 种风格 + 6 种质感手法的参数字典）；
- 本文件负责把选定的风格**落到代码和设计稿上**：找到对应的设计系统和组件、映射到项目的技术栈、批量应用、验收一致性；
- 动效组件检索走 [methods-motion.md](methods-motion.md) `MI`，本文件只在资源层里引用它。
- 配色的检索、语义化、对比度走 [methods-color.md](methods-color.md) `CI`；本文件在 `DS2` 取颜色规格时调用它，不另起一套选色逻辑。

## 三类资源：只有前两类能自动化

| 类型 | 是什么 | 能不能自动化 | 例子 |
| :--- | :--- | :--- | :--- |
| 可复制的 UI 组件 / 页面区块 | 能直接拿到源码 | 能：按命令安装或复制，再改成项目的 token | shadcn/ui 组件与区块、Magic UI、Origin UI、Float UI，以及 `MI` 里的动效库 |
| 可应用的完整设计系统 / 主题 | 有 token、组件和规则 | 能：一处改 token，全站跟着变 | Tweakcn 主题、shadcn 预设、Material 3、Ant Design、Apple HIG |
| 只有视觉参考的网站 | 只有图，没有代码 | 不能：只能人工提取参数，经过核对后沉淀成新预设 | Awwwards、Dribbble、Apple Design Resources 的 Figma 套件 |

视觉参考网站里的东西，不能写成“已应用某某风格”；提取出来的参数要标明来源和“人工提取”，并像其他预设一样跑验收。

## 四个资源层与风格适配器

| 资源层 | 作用 | 本地已打包 | 线上补充 |
| :--- | :--- | :--- | :--- |
| 风格库 | 选整套视觉语言 | `style-presets/systems/`（Apple、Material 3、Ant Design）、`style-presets/dto/`（V0 的 26 种风格）、`style-presets/themes/tweakcn/`（42 个主题） | [Tweakcn](https://tweakcn.com) 新主题、[shadcn 预设](https://ui.shadcn.com/create)、[Material Theme Builder](https://github.com/material-foundation/material-theme-builder) |
| 设计系统库 | 统一组件、token、交互规则 | 三套系统预设里的组件规则、字阶、圆角阶梯、实现方式 | [shadcn/ui](https://ui.shadcn.com)、[Ant Design](https://ant.design)、[Material 3](https://m3.material.io)、[Apple HIG](https://developer.apple.com/design/human-interface-guidelines) |
| 页面区块库 | 拿页面结构与模板 | `registry.json` 里每个风格族绑定的区块库 | [shadcn Blocks](https://ui.shadcn.com/blocks)、[Magic UI](https://magicui.design)、[Origin UI](https://originui.com)、[Float UI](https://floatui.com)、[Shadcn Studio](https://shadcnstudio.com) 免费部分；[Tailwind Plus](https://tailwindcss.com/plus) 仅限用户已购买许可证 |
| 动效库 | 交互反馈与动态表现 | 风格族绑定的动效库 | 见 `MI` |

**风格适配器**是把这四层串起来的那一步。例如用户说“把当前产品改成苹果风”，流程是：
1. 先从风格库取出苹果设计语言；
2. 再按项目技术栈找对应组件：SwiftUI 用系统组件，Web 用 shadcn 加苹果主题；
3. 最后统一应用 token、组件规则和页面规则。

**技术边界**：
- shadcn/ui 或 Tailwind 项目换主题比较容易，改 CSS 变量即可。
- 已经开发好的 Flutter、SwiftUI 或复杂 React App，不可能只靠复制 CSS 完成全站换肤。必须先清点写死的样式值，再做组件映射和代码改造（见 `DS3`）。

## 本地预设库：先用本地，再去线上补

预设存在 Skill 里，不现查：
- `style-presets/registry.json`：总索引，包含三类资源的定义、12 个风格族、全部预设和线上库清单（含许可证与是否付费）。
- 每个预设文件都是 shadcn 的 `registry:theme` 格式，可以直接 `npx shadcn@latest add ./<文件>.json`。文件的 `meta.dto` 里存着：
  - 字阶、间距、圆角阶梯；
  - 组件规则、导航、动效策略；
  - 适用与不适用场景；
  - 各技术栈的实现方式；
  - 来源和许可证；
  - 可安装资源。
- `scripts/style_preset.py`：
  - `list`：按风格族列出；
  - `show`：查看规格；
  - `export`：导出 CSS、Tailwind v4、shadcn 或 antd token；
  - `apply`：写入项目的全局 CSS，可重复执行。
- `scripts/style_consistency_audit.py`：跨页一致性验收（见 `DS5`）。

**风格族**把同一种观感的本地预设和线上资源归在一起，用户点名的风格名、Agent 推荐的方向都先映射到风格族。现有 13 个：
- 苹果原生
- 安卓原生 / Material
- 企业中后台
- 极简 SaaS
- AI 产品（只用于 AI 对话、生成工具本身；AI 只是交互方式时按行业选）
- 编辑式 / 强排版
- 柔和 Soft UI
- 玻璃拟态
- 科技感 / 未来暗色
- 内容 / 电商信息流
- 大字普惠
- 游戏与互动娱乐
- 旅行与目的地

每个风格族有两类组件来源：
- `recipes`：通用组件配方的标签，见 [component-recipes/](component-recipes/registry.json)。纯 HTML、React、Figma 都能用，组件只引用风格变量，换风格自动跟着变。**所有技术栈先用它当结构、交互和状态的骨架**；页面长相跟 [methods-visual.md](methods-visual.md) `VT` 的目标稿走，拷进来后按目标稿改字体、照片处理、容器和点睛元素。只用配方默认样式拼出来的页面就是模板脸。
- `layout`：React + Tailwind 区块库（shadcn Blocks、Magic UI 等）。只在 React 项目里补配方库没有的零件。它们以后台、官网、表单为主，不提供手机消费产品的页面构图；构图按 `RR` 看同类真实页面，结构用下面的画面级配方。

**画面级配方是必做的，不是「需要时再看」。** 消费级主屏、游戏主界面、内容流，动手前先 `copy` 其中一个，它决定第一眼是什么画面。`field`、`card`、`button`、`chip-group` 只是零件，不许用它们拼出「一行大标题 + 三张小图 + 三张输入卡 + 一颗按钮」。

| 这一屏是什么 | 先 copy 哪个 |
| :--- | :--- |
| 旅行首页 | 先过 `I3` 的首页职责。`destination-hero` 只是首页里的一块主视觉，不是整页。同屏还要有进入自己的行程的入口，以及一个能认出的行程例子。整页只有一个地方、一个名字、「开始这一个」，那是详情页，配方也不许这么拼 |
| 行程长什么样 | `itinerary-preview-card`、`itinerary-timeline` |
| 地图上选地方 | `map-with-sheet` |
| 内容 / 照片流 | `hero-media`、`feed-masonry`、`photo-card` |
| 牌桌、桌游 | `felt-table`。自己的手牌是完整牌面的 `playing-card`（角标加牌心花色，不能只剩一排角标），再配 `hand-fan`、`seat-nameplate` |
| AI 工具本身的输入页 | `prompt-composer`、`ai-result-card` |

拷进来之后仍按 `VT` 的目标稿改字体、照片处理和材质。配方默认样式拼出来的页面是模板脸。

**线上补充**：本地预设定下来之后，仍然去线上库查本地没有的部分：缺的组件和页面区块、Tweakcn 新主题、对应的动效组件。线上拿到的东西按 `DS6` 审过再用，好用的沉淀回 `style-presets/`。

## DS0 识别现状

**触发问题**：项目现在是什么技术栈、已经有什么风格，样式是集中在 token 里，还是散落在每个页面里写死？  
**最低输入**：项目代码或页面文件；没有代码时用截图或 Figma 主稿。  
**跳过**：从零新建、还没有任何页面。

**步骤**
1. 识别技术栈，看依赖和配置文件：
   - `components.json` → shadcn；
   - `antd` → Ant Design；
   - `@mui/material` → MUI；
   - `pubspec.yaml` → Flutter；
   - `.swift` + SwiftUI → 原生 iOS；
   - `build.gradle` + Compose → 原生 Android；
   - 只有 HTML/CSS → 纯网页。
2. 识别现有风格：
   - 读全局 CSS 变量、主题文件、Tailwind 配置或 `ConfigProvider`；
   - 再用 `style_consistency_audit.py`（不带 `--preset`）跑几个代表页，看实际用了多少种颜色、圆角和字体。
3. 清点写死的样式值：搜索页面和组件里直接写的颜色（`#xxxxxx`、`rgb(`）、圆角、字体和阴影，记下数量和位置。写死的值越多，`DS4` 批量应用前要做的改造越多。

**产出**：现状记录，包括技术栈、现有 token 来源、写死值的数量与位置，以及最接近的风格族。  
**完成证据**：写死值的清点有文件位置；一致性检查有实际运行结果。  
**不得替代**：`U0` 分流。有现成页面、用户没要求改版时，仍然走存量延展，不重选风格。

## DS1 选风格：探索和应用分开

**触发问题**：这次是在探索方向，还是要把已定的风格改进代码？  
**最低输入**：`V0` 的语境剪枝结果，或用户点名的风格。  
**跳过**：`U0` 路线 1 的存量延展（沿用现有风格）。

两件事分开做：

1. **风格探索**：生成 3 个不同方向给用户挑，不改项目代码。
   - **什么时候做**：
     - 用户主动说“看看几种风格”“帮我换个风格”；
     - 要给已上线的产品改版；
     - `V0` Step 2 判定方向高度开放。
   - **怎么做**：
     - 从不同风格族各取一个预设（不要 3 个都是同一族的变体）；
     - 用同一个核心代表页、同一份真实内容分别渲染；
     - 三张截图并排给用户看；
     - 用提问工具问一次，每个选项用大白话描述观感，不出现风格编号和内部术语；
     - 推荐项排第一并标 `(Recommended)`。
   - **0→1 新建且用户原话未指定风格时**：在完成并向用户汇报完前置用研、三类竞品调研与具体交互控件方案后，提供 2–3 个视觉风格方向征求用户选择；**在用户选定风格方向之前，严禁提前运行 `style_preset.py` 锁死单一风格！**
2. **风格应用**：把用户选定（或确认）的风格批量写进代码或设计稿（`DS2`–`DS5`）。
   - **改已有产品的代码前，必须先让用户确认**：给出代表页改前改后对比，以及要改的文件范围，用提问工具确认一次，确认后才批量改。不能擅自把成熟产品改得面目全非。

**产出**：选定的预设 ID 与风格族；探索时附 3 个方向的截图和用户选择。  
**完成证据**：改已有产品前有用户确认记录；探索的 3 个方向确实来自不同风格族。  
**不得替代**：`V0` 的语境剪枝与行业底线。高风险行业剔除的风格，探索时也不能拿出来。

## DS2 提取风格规格

**触发问题**：选定的风格落到这个产品上，具体是哪些数值和规则？  
**最低输入**：选定的预设 ID。

**步骤**
1. 运行 `python3 scripts/style_preset.py show <ID>`，读出八类规格。颜色以这份预设的 `cssVars` 和 `meta.dto.palette` 为准，整套用，不另生成一套色板。
   - 字体、圆角、间距、导航、卡片、交互规则、动效同样从这份预设取。
2. 预设没覆盖的项，按以下顺序补：
   - 先从同一风格族的其他本地预设补；
   - 不够再去线上设计系统的官方规范查；
   - 都没有时，从已有参数推出来，并标“推导”。
3. 品牌色只在用户给出了正式品牌色值时，才替换预设主色。没有正式品牌色，禁止运行 `from-brand`，禁止为了对比度或“像某产品”另造一个主色。替换后检查对比度：正文 ≥ 4.5:1，大字和图标 ≥ 3:1。不够就在同一色相里加深这颗按钮或这块字的底，不换一套色。浅色字对比不够时，改底的深浅，字仍用预设的浅色前景。不要把浅色字改成黑色贴在高饱和底上。
4. 把规格写进任务包，作为本轮唯一的风格数据源（与 `V0` Step 5.2 是同一份）。写进 CSS 变量只是开始。页面结构必须跟风格族走，每个组件用上规格里的材质。只换背景色，规格不算落地。

**产出**：风格规格卡：八类规格的具体数值，每项注明来源（本地预设 / 线上规范 / 推导）。  
**完成证据**：每个数值都能对上预设文件或官方链接；没有凭感觉写的值。  
**不得替代**：`V0` Step 3 的材质覆盖要求。规格里每个组件都要有对应的材质参数。

## DS3 组件映射（风格适配器）

**触发问题**：项目里现有的组件，分别对应到目标风格的哪个组件、哪条规则？  
**最低输入**：`DS0` 现状记录与 `DS2` 规格卡。

**按技术栈的应用方式**

| 技术栈 | 怎么应用风格 | 注意 |
| :--- | :--- | :--- |
| shadcn / Tailwind（React） | `style_preset.py apply <ID> --css <全局 CSS>`，或 `npx shadcn@latest add ./style-presets/<文件>.json`；线上 shadcn 预设用 `npx shadcn@latest apply --preset <id> --only theme,font` | shadcn 组件自动跟随；自写组件里写死的值要改成 `var(--…)` |
| 纯 HTML / CSS | 先 `component_recipe.py copy` 画面级配方，再 `style_preset.py export <ID> --format css -o theme.css` 引入 | 导出 CSS 变量只换皮，不构成页面。写死的值改成 `var(--…)`。没有画面级配方的主屏不算做完 |
| Ant Design | `style_preset.py export <ID> --format antd`，放进 `ConfigProvider theme={{ token }}`；暗色加 `theme.darkAlgorithm` | 组件级差异写进 `theme.components` |
| MUI | 按规格卡写 `createTheme({ palette, shape, typography })` | 圆角、字阶对照规格卡 |
| Arco Design / TDesign / Fluent UI | 用各自官方的主题 token 机制（Arco 主题配置、TDesign CSS token、Fluent `createLightTheme` / `createDarkTheme`），数值从规格卡取 | 本地没有它们的预设，按规格卡逐项对照填写 |
| Flutter | `ThemeData(useMaterial3: true, colorScheme: …, textTheme: …)`；Material 风格用 `ColorScheme.fromSeed` | 自定义组件里的 `Color(0x…)` 要改成 `Theme.of(context)` |
| SwiftUI | 苹果原生风格直接用系统组件和语义色；其他风格用 Asset Catalog 颜色加自定义 `ButtonStyle` / `ViewModifier` | 不嵌入 SF Pro 字体文件到 Web 或非苹果平台 |
| Jetpack Compose | `MaterialTheme(colorScheme, typography, shapes)` | 同上，写死的 `Color(0x…)` 要收进主题 |

**组件映射表**：现有组件逐个列出，标明以下四项：
- 对应目标风格的哪个组件或规则，例如：
  - 自写的顶部栏 → 苹果大标题导航栏；
  - 自写的弹窗 → Material 圆角 28 的 Dialog。
- 只换 token 就够，还是要改结构。比如从底部 Tab 改成侧边栏，就属于结构改造。
- 组件从哪里来：先 `python3 scripts/component_recipe.py list --tag <风格族的 recipes 标签>`，用 `copy` 取出纯 HTML/CSS 配方。主屏先 copy 上表的画面级配方，再 copy 零件。这一步不能跳。配方库没有的，React 项目再按风格族绑定的区块库检索（审源码规则同 `MI`），其余技术栈自己按配方格式写。区块库不提供手机消费页面的构图，不能用它代替画面级配方。
- 选风格时可以先看效果：`python3 scripts/component_recipe.py preview --preset <风格编号> --tag <标签> -o <文件.html>`，截图对比两三个候选预设，比读参数表直观。
- 新写的配方放进 `component-recipes/recipes/<id>.html`（元数据注释 + `<style>` + `<!-- demo -->` 结构 + 可选 `<script>`），只读风格变量和 `base.css` 的 `--r-*` 变量，然后运行 `index`。`index` 会检查标签、依赖、图标文件，以及示例里用到的每个类是否有样式来源。
- 改造涉及的文件。

**产出**：组件映射表与改造文件清单。  
**完成证据**：`DS0` 清点出的每个写死值都有去向；每个现有组件都有映射结论。消费级主屏的映射表第一行是画面级配方，不是 `field`。  
**不得替代**：`U4` 的组件功能判断。换风格不改变“用什么控件解决什么任务”。

## DS4 批量应用到整个产品

**触发问题**：怎样一次把风格改到所有页面，而不是逐页手调？  
**最低输入**：`DS3` 映射表；改已有产品时还需要 `DS1` 的用户确认。

**顺序固定**：先 token，再组件，最后页面。
1. **token**：用 `DS3` 的方式写入一个集中位置（全局 CSS、主题文件或 `ConfigProvider`），全产品只有这一处定义颜色、字体、圆角、间距和阴影。
2. **写死值收口**：按 `DS0` 的清点，把页面和组件里写死的值替换成 token 引用。
3. **组件**：按映射表改组件本身，包括结构改造和材质规则；从区块库补进来的组件同样改成用 token。
4. **页面**：只处理页面特有的布局问题。页面里不再出现新的写死样式值；确实需要例外的元素加 `data-style-exempt` 并写明理由，例如品牌 Logo、插画、第三方嵌入。

**不允许**：
- 逐页手调颜色和圆角；
- 同一个组件在不同页面各改一套；
- 改风格的同时顺手改布局、业务逻辑或事件行为。

**产出**：修改文件清单，以及 token 所在位置。  
**完成证据**：搜索写死的颜色和圆角，结果只剩加了豁免的元素。  
**不得替代**：`U3` 的对齐与防碰撞检查。换完风格仍要重跑 `ui_geometry_audit.py`。

## DS5 跨页一致性验收

**触发问题**：所有页面是否都在同一套风格里，没有漏网的旧样式和页面间的差异？  
**最低输入**：应用后的全部页面，至少覆盖每类页面各一个。

**步骤**
1. 运行 `python3 scripts/style_consistency_audit.py <所有页面> --preset <ID>`。
   - 线上或开发服务器页面：用 `--probe-js` 取出探针脚本，在浏览器里执行，把结果存成 JSON，再用 `--from-json` 一起检查。
2. 四类问题必须清零：
   - `OFF_TOKEN_COLOR`：颜色不在色板里；
   - `OFF_SCALE_RADIUS`：圆角不在阶梯里；
   - `OFF_TOKEN_FONT`：字体不在字体栈里；
   - `CROSS_PAGE_DRIFT`：同一类组件在不同页面长得不一样。
3. 每类页面各截一张图并排看，找全产品做得最弱的那个组件，它也必须达到风格参数（与 `V0` Step 3 同一检查）。
4. 不通过就回到 `DS4` 改，改完重跑脚本、重新截图。

**产出**：一致性检查报告与并排截图。  
**完成证据**：脚本 `passed: true`；并排截图里找不到风格不一致的组件。  
**不得替代**：`QA0` 终审。本检查是终审 F 层的一部分。

## DS6 线上补充与沉淀

**触发问题**：本地预设缺的东西怎么补，补到的好东西怎么留下来？  
**最低输入**：`DS2` 规格卡里缺的项，或 `DS3` 映射表里需要补的组件。

**步骤**
1. **检索**：按风格族绑定的资源检索：
   - 组件与区块：
     - `npx shadcn@latest search @magicui -q "<关键词>"`；
     - shadcn Blocks；
     - Origin UI；
     - Float UI。
   - 主题：Tweakcn 新主题、shadcn 预设。
   - 动效：走 `MI`。
2. **审查**，规则同 `MI` 第 4 步：
   - 先读源码和依赖；
   - 不运行未审的安装命令；
   - 付费、需要授权 token 或登录的资源不用；
   - 用户已购买许可证的（如 Tailwind Plus）由用户提供代码。
3. **记来源**：每个拿进来的组件和主题都要记录：
   - 来源 URL；
   - 许可证。
   - Float UI 和 Shadcn Studio 免费部分的限制（不得单独再分发、不得做成模板或建站器）也要写明。
4. **沉淀**：验收通过、可复用的新主题或新风格，存进 `style-presets/`：
   - 主题文件放 `themes/` 或 `dto/`，并在 `registry.json` 登记：
     - 风格族；
     - 来源；
     - 许可证；
     - 适用场景。
   - 只来自视觉参考网站的风格，标“人工提取”。
   - 没在真实项目里验收过的，不进预设库。
5. **找不到**：线上也没有合适资源时，按规格卡自己写，来源记“自写”。不得编造“来自某库”。

**产出**：补充资源清单（来源、许可证、用途）；新沉淀的预设与 `registry.json` 变更。  
**完成证据**：每个外部资源都有可核对的来源和许可证；沉淀的预设有验收记录。  
**不得替代**：`MI` 的动效检索与集成规则。

## 风格引擎验收

- 现状清点：写死值有位置、有去向（`DS0`、`DS3`）。
- 探索和应用分开；改已有产品前有用户确认（`DS1`）。
- 规格卡每个值都有来源（`DS2`）。
- token 只有一处定义；页面里没有新的写死值（`DS4`）。
- `style_consistency_audit.py` 通过，并排截图无不一致（`DS5`）。
- 外部资源来源和许可证齐全，没有付费、未审或编造来源的资源（`DS6`）。
