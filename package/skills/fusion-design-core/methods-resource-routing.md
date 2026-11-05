# 资源路由与设计资产记忆

方法负责判断怎么设计。外部库和内部资产负责提供真实案例、成熟方案、可复用代码和验证手段。

本文件负责把资源接到已有方法和专业环节，每个资源用 adapter 描述，不为新增一个库另开 U8 / V8。专项方法尚缺时按 [成果、环节与子任务目录](methods-deliverable-routing.md) 补足专业依据；增加资源入口本身不代表补齐方法。

四个登记库已经在 Skill 里，先用它们：
- **Reference**：`resource-adapters/registry.json` 里 `capability=reference|spec`（Mobbin、Page Flows、ARIA APG…）
- **Style**：`style-presets/` + `color-presets/`
- **Component**：shadcn / Magic UI / Origin UI / Figma 套件（风格引擎 + 本文件）
- **Asset**：IconScout（`V5`，图标/3D/插画/Lottie）+ Real Image Library（`IM`，真实摄影）+ SVG Repo 降级

检索顺序固定：

1. 内部资产记忆（`scripts/asset_memory.py search`）
2. 本地预设（风格、配色、字体目录、ARIA APG 索引）
3. 可自动调用的 adapter（CLI / 脚本 / 不需付费的公开接口）
4. 已授权的 MCP（Mobbin、IconScout、Figma、Playwright）
5. 参考链接（打开给用户看，**不抓取**）

```
python3 scripts/resource_router.py list --stage research
python3 scripts/resource_router.py show mobbin
python3 scripts/resource_router.py apg dialog
```

## Adapter 合同

每个资源必须写清，缺一项就不能标「已接入」：

| 字段 | 含义 |
| :--- | :--- |
| mode | `auto` / `mcp` / `cli` / `api` / `reference` |
| search | 怎么检索 |
| returns | 回来的是什么数据 |
| acquire | 怎么用到项目里（复制源码、插 Figma、只作参考） |
| license | 授权与禁止项 |
| fallback | 没权限、没接口、失败时做什么 |

`mode=reference` 或没有公开接口：只给链接和观察记录，**不得假装能自动安装、不得抓取付费内容**。接入库不等于复制网址。

## RR 设计参考智能（接到 CMP，不是新的竞品方法）

**触发问题**：这个任务里的具体场景，真实产品是怎么做的？  
**最低输入**：要支持的设计决定、用户任务、拆好的场景清单。  
**跳过**：依 RT0 判断已有适用且可回查的案例足以支持本轮设计，或本轮问题不需要新增外部样本；写明复用/不展开理由。新界面也先判断已有依据是否充分，不能仅因“从零新建”重复调研，也不能未经判断直接套模板。

重点不是照搬整个竞品，而是按**用户任务和交互问题**检索解法。新的消费级界面还要回答一个构图问题：这类页面第一眼靠什么画面撑起来。

**步骤**
1. 把任务拆成场景，例如拍照搜题：入口 → 相机权限 → 裁剪 → 识别中 → 答案 → 追问。每个场景写要解决的问题，不写产品名。
2. 仅当项目目录已有 `.design-memory/index.json` 沉淀时才跑 `asset_memory.py search <场景>`；0→1 新项目且内部资产库为空时直接跳过此步，不浪费命令调用。
3. 检索外部真实竞品界面：
   - 有 Mobbin 授权（Pro 及以上）：MCP `search_screens` / `search_flows` / `search_sections`。按场景和状态搜，例如「camera permission deny state」，不要搜「像某某 App」。
   - 无授权：自己看公开页面，不停工。用网页搜索找同类产品，打开应用商店页面（App Store、Google Play 的截图区）和产品官网，用浏览器截图或读图，按待回答问题选择同类产品及相关状态，范围由覆盖和新增信息是否改变判断决定。只看公开页面，不登录、不绕过付费墙、不批量抓取。也可以请用户导出 Mobbin / Page Flows 案例，但不等用户才开工。
   - 每个案例写：产品、页面、来源链接；第一眼是什么画面、占屏多大；信息怎么分区；主行动在哪；我们学什么、不学什么。
   - 算数的只有同一种屏幕：手机首页对照手机首页，横屏牌桌对照横屏牌桌。应用商店宣传海报、带下载按钮的落地页、另一种设备的官网首屏，不能替代该任务的交互证据。样本不足以支持判断时写清缺口和下一动作，不许用海报凑数；跨媒介表达参考按 CC4 另记。
   - 流程视频：Page Flows 无公开 API，只作参考链接。
   - 交互行为：`resource_router.py apg <模式>`，对照键盘与角色。
4. 每个案例按 [methods-competitive.md](methods-competitive.md) 的样本模板记录。观察到的是事实，解释与假设分开。「别的产品都这样做」只能当候选，不能当完成证据。
5. 不复制品牌资产、文案和独特视觉。

看过的同类截图存进页面目录的 `refs/`（文件名写产品和页面），`VT` 出目标稿时当质感参考，`QA0` 并排对比时当标杆。

Mobbin MCP：`https://api.mobbin.com/mcp`，OAuth，需要付费套餐。有套餐时像 IconScout 一样发起授权，告诉用户点一下。没有套餐或授权失败，走 fallback，不停工。

**产出**：场景 → 案例 → 可复用条件 / 不可复用原因。新的消费级界面另写一句构图结论和视觉主角，进 `design-decisions.md` 第 2 块。  
**完成证据**：每个关键场景至少有一条来源可核对的案例，或写明「未找到，按方法自写」。结论足以支持本轮判断，重要缺口和证据限制已标明；样本量不设统一下限。后续 QA0 并排审美验收所需参考图仍遵守原验收要求，不因本轮研究复用或不展开而豁免。
**不得替代**：用户研究；不能用案例证明目标用户需要什么。

## TY 智能排版（接到 V3，不是新的视觉方法）

**触发问题**：这套产品用什么字体、字阶和行高，才能覆盖语言和密度？  
**最低输入**：风格族、目标语言、密度（紧凑 / 默认 / 舒展 / 适老）。  
**跳过**：正式品牌字体已锁定。

```
python3 scripts/typography_intelligence.py pick --family editorial --langs zh,en --density relaxed
python3 scripts/typography_intelligence.py pick --family ai-product --langs zh,en --css
```

规则：
- 字体跟风格族走，不凭空挑「高级感字体」。
- 目标语言含中日韩时，正文必须有 CJK 字体。不能只用 Inter / Geist。
- 用 Google Fonts 的 **CSS2 URL** 加载，不需要 API key。完整 2000+ 目录检索才需要用户自己的 key；没有 key 就只用 `resource-adapters/fonts/catalog.json`。
- 不嵌入 SF Pro。苹果风用系统字体栈。
- 字号、行高、字重写入 `V3` 记录，来源写本目录或品牌规范。
- Fontshare 等站点：用户挑选并确认许可后再用。

**产出**：标题 / 正文 / 等宽 / CJK 字族、字阶、CSS 链接。  
**完成证据**：每种目标语言有字形覆盖；`V3` 记录有来源。  
**不得替代**：`V3` 的内容压力测试和窄屏检查。

## VE 验证引擎（接到 QA0，不是新的验收方法）

交付前在现有 QA0 上加三类可执行检查，能跑的必须跑：

| 检查 | 命令 / 工具 | 没有工具时 |
| :--- | :--- | :--- |
| 几何 / 分区 / 图标 | `ui_geometry_audit.py` | 不能交 HTML |
| 跨页风格 | `style_consistency_audit.py` | 单页可跳过跨页项 |
| 对比度 | `color_intelligence.py contrast` | 不能交语义色 |
| 无障碍 | `python3 scripts/a11y_audit.py <页面>`（axe-core） | 键盘走主路径 + 对比度；并写「axe 未跑」 |
| 主路径 | Playwright MCP 或浏览器里实际点一遍，含一个失败分支 | 必须人工点，不能只截静图 |
| 视觉回归 | `npx chromatic`，仅当存在 `CHROMATIC_PROJECT_TOKEN` 且项目有 Storybook | 并排截图；**不写「已做视觉回归」** |

axe 报出的 `critical` / `serious` 必须修好再交。Chromatic 没 token 不是失败，是不适用。

## AM 设计资产记忆（闭环，长期价值最高）

每次做完：设计执行 → 自动验收 → **用户确认** → 入库 → 下一次优先复用。

```
python3 scripts/asset_memory.py search 相机权限
python3 scripts/asset_memory.py deposit --type pattern --title "权限被拒可重试" \
  --conditions "系统权限、必须有设置入口" --files permission.html \
  --validation a11y.json --confirm
```

可入库的类型：交互模式及适用条件、页面模板及组件映射、风格 / 配色 / 字体预设、动效代码及参数、已通过验收的组件及测试记录。

规则：
- 没跑验收、验收未通过、用户没确认，都不能入库。
- 默认写入当前项目的 `.design-memory/`。可复用到其他项目的，再拷进 Skill 的 `asset-memory/`。
- 检索时两个目录都搜。
- 命中内部资产后，仍要用当前任务的约束核对适用条件，不能无条件套用。

**产出**：`index.json` 中的一条资产。  
**完成证据**：有验收记录和确认标记。  
**不得替代**：本轮仍要按方法做判断；记忆是输入，不是答案。

## 环节—方法—资源对应表

由 [成果、环节与子任务目录](methods-deliverable-routing.md) 和 RT0 先判断本轮需要解决什么，再查下表。它不是所有任务必须跑完的检索清单；独立委托与嵌入任务使用同一方法入口，区别在范围和下游用途。已有材料足够时复用并写依据，无需为每个子成果重新取证。

| 本轮要解决的判断 | 已有方法入口 | 何时查哪些库或资料 | 应进入下游的结果与检查 |
| :--- | :--- | :--- | :--- |
| 用户、情境、问题与价值是否成立 | CT/BR；R0/R0.1、R1–R8，按未知选用 | 先审查已有研究、数据、反馈和真实记录；需要背景再查公开资料。NN/g 等为方法参考，Mobbin 等为产品案例，不充当用户经历 | 有来源的问题/情境、假设及方向判断；按所选方法的完成证据区分事实、解释和未验证内容 |
| 是否需要比较行业方案、操作原理或用户已有习惯 | CMP1–CMP3 + RR | 已有有效案例不足时按具体决定查 Mobbin、Page Flows、公开产品；能否访问及样本适用性分别核对 | 场景、来源、可复用条件、反例和适用限制；进入相应决定，不以案例证明用户需求 |
| 流程及服务接力怎样完成、怎样恢复 | F1–F5；需要时 R6、CT3/CT4/CT8 | 先查项目流程、运行事实和有效内部记忆；有比较问题再查 Mobbin flows / Page Flows | 任务、角色、主路径、分支及恢复；执行原流程评审，不能只交页面跳转 |
| 内容怎样分类、找到、理解和表达 | CT6、I2/I3/I4、适用 U1/U2/U6 | 项目内容、术语、现有结构与真实查找问题；必要的外部案例按 CMP/RR 取证，不凭组件库决定内容职责 | 分类/命名、页面或章节职责、信息主次和实际文案；检查完整性、查找和理解，不将排版当内容验收 |
| 动作、控件、状态和异常怎样成立 | I1–I6、U4/U5；需要验证时 PROTO/VAL | 现有交互模式不足时查 ARIA APG、UI Patterns、同包 Pro Max 对应 UX 指导及必要操作案例 | 具体规则、反馈、失败出口与适用原型；核对状态和操作。真实用户结论仍需真实测试 |
| 概念、信息主次及构图怎样服务目标 | CC；CT6/CT7，适用的 V 方法 | 按主题、机制或图文关系找有来源的表达参考；跨媒介参考按 CC4 说明学什么、哪些不能移用 | 概念候选与选择、信息/构图依据；F4/CC2 共用记录，进入相应子成果，不能用风格预设替代概念推导 |
| 视觉语言、字体和配色怎样落地 | V、DS、CI；TY 接 V3 | 已有品牌/正式稿先复核；需要新方向再查 style-presets、color-presets/Radix、字体目录及同包 Pro Max 的相关建议 | 风格规格、字形覆盖、字阶、语义色和对比度实测；实际渲染后按适用视觉标准校正 |
| 组件怎样复用或形成系统 | CT3、U4/U5、DS3–DS5 | 项目组件优先；适用时查 component-recipes、shadcn、Magic UI、Figma 套件，或同包 Impeccable 系统提炼参考 | 组件映射、状态/变体和真实应用；检查与项目语义、风格和跨页行为一致，不因有配方就直接套整页 |
| 图像、图标、插画或角色用什么、怎样落位 | V5/V7、IM 及原资产合同 | 按用途查 IconScout、真实摄影入口，必要时走已确认的生成工具路线；来源与使用条件按各资源核对 | 真实文件、来源/许可、尺寸/格式和实际落位；资产可以独立委托，不自动扩展为品牌定位 |
| 图表或信息图怎样解释内容/数据 | CT6、内容层级、同包 Pro Max 图表指导；补专项依据 | 已有内容/数据来源先核实，按要解释的关系查图表选型；图表建议库不替代数据口径和编码审查 | 来源、口径、关系/编码、标注及理解检查；放回页面、海报、报告或视频时复核，交互版另接 I/M |
| 交互或品牌运动怎样实现 | M1–M3 / MI，各自适用；TR5 | 运动目的和必要输入已成立后，查 React Bits、Motion Primitives 等源码、IconScout 动态素材或 Pro Max GSAP 建议 | 起止/中间状态、时序、正式实现及动态证据；UI 动效检查打断/恢复，线性视频用其叙事与播放标准 |
| 成果是否完成、是否适合展示与交接 | 各已用方法的完成证据、适用 QA0/VE 或 VAL | 按已定载体运行几何/一致性/对比度、Playwright、axe 等适用检查；Impeccable 可提供界面 critique/audit/polish 参考 | 方法结果、版本、实际操作/看图、修正和复核证据；脚本通过不单独构成审美通过，AI 自检不称用户验证 |

### 资源身份与实际可用性

- `style-presets/`、`color-presets/`、字体目录、组件配方，以及同包 [Pro Max](../fusion-design-ui-ux-pro-max/SKILL.md) 的 UX/字体/图表等数据是本地资源；同包 [Impeccable](../fusion-design-impeccable/SKILL.md) 是可按需调用的界面方法参考。两项辅助 Skill 不接管主流程、产品事实或原确认规则。
- Mobbin、IconScout、Figma 等是外部入口；参考链接、可自动调用资源和需授权工具按 adapter 合同区别记录。登记存在不代表已连接、已有付费权限或已取得素材。
- 内部记忆仅在对应目录有真实条目时检索；随包的空索引只是机制，不可报告为已命中历史资产。确认并通过验收后再按 AM 沉淀。
- 品牌、服务蓝图、视频叙事/声音、文稿出版和印刷生产的完整专项仍有缺口；上表部分方法或素材可支持它们，不能据此宣称专项已齐备。按目录补足实际专业依据，不为补一个库另开平行流程。
- 查询结果需在实际成果中采用、说明不适用，或形成明确设计判断；只运行搜索或列库名不构成方法完成。每一步的具体输入、停止和交接仍以原方法及 N5 合同为准。

真实摄影的细则保留在 [methods-image.md](methods-image.md)，本文件只负责接入，不另写一套方法。

## IM 真实摄影（接到 V5 / V7，不是新的视觉方法）

**触发问题**：稿上这一处需要真实世界的照片吗？  
**步骤**：按 [methods-image.md](methods-image.md) 运行 `scripts/real_image.py`。主库 Pixabay + Openverse + 已预置 key 的 Unsplash；Pexels 有 key 才开；具体地点优先 Wikimedia。  
**完成证据**：用上的图有作者、许可证、本地文件；该用真图却直接生图的，本项不过。
