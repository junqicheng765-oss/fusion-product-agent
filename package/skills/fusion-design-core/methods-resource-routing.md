# 资源路由与设计资产记忆

方法负责判断怎么设计。外部库和内部资产负责提供真实案例、成熟方案、可复用代码和验证手段。

**不再增加设计方法。** 新能力都接到现有环节上，每个资源用 adapter 描述，而不是新开 U8 / V8。

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
**跳过**：本轮不改流程/交互/结构，或已有有效近期案例。**新的消费级界面不跳过**：没看过同类真实页面，不许定视觉主角。

重点不是照搬整个竞品，而是按**用户任务和交互问题**检索解法。新的消费级界面还要回答一个构图问题：这类页面第一眼靠什么画面撑起来。

**步骤**
1. 把任务拆成场景，例如拍照搜题：入口 → 相机权限 → 裁剪 → 识别中 → 答案 → 追问。每个场景写要解决的问题，不写产品名。
2. 仅当项目目录已有 `.design-memory/index.json` 沉淀时才跑 `asset_memory.py search <场景>`；0→1 新项目且内部资产库为空时直接跳过此步，不浪费命令调用。
3. 检索外部真实竞品界面：
   - 有 Mobbin 授权（Pro 及以上）：MCP `search_screens` / `search_flows` / `search_sections`。按场景和状态搜，例如「camera permission deny state」，不要搜「像某某 App」。
   - 无授权：自己看公开页面，不停工。用网页搜索找同类产品，打开应用商店页面（App Store、Google Play 的截图区）和产品官网，用浏览器截图或读图，看 3–5 个同类产品的同类页面。只看公开页面，不登录、不绕过付费墙、不批量抓取。也可以请用户导出 Mobbin / Page Flows 案例，但不等用户才开工。
   - 每个案例写：产品、页面、来源链接；第一眼是什么画面、占屏多大；信息怎么分区；主行动在哪；我们学什么、不学什么。
   - 算数的只有同一种屏幕：手机首页对照手机首页，横屏牌桌对照横屏牌桌。应用商店宣传海报、带下载按钮的落地页、另一种设备的官网首屏，不算这 3–5 张。找不够就写明少了几张，不许用海报凑数。
   - 流程视频：Page Flows 无公开 API，只作参考链接。
   - 交互行为：`resource_router.py apg <模式>`，对照键盘与角色。
4. 每个案例按 [methods-competitive.md](methods-competitive.md) 的样本模板记录。观察到的是事实，解释与假设分开。「别的产品都这样做」只能当候选，不能当完成证据。
5. 不复制品牌资产、文案和独特视觉。

看过的同类截图存进页面目录的 `refs/`（文件名写产品和页面），`VT` 出目标稿时当质感参考，`QA0` 并排对比时当标杆。

Mobbin MCP：`https://api.mobbin.com/mcp`，OAuth，需要付费套餐。有套餐时像 IconScout 一样发起授权，告诉用户点一下。没有套餐或授权失败，走 fallback，不停工。

**产出**：场景 → 案例 → 可复用条件 / 不可复用原因。新的消费级界面另写一句构图结论和视觉主角，进 `design-decisions.md` 第 2 块。  
**完成证据**：每个关键场景至少有一条来源可核对的案例，或写明「未找到，按方法自写」。新的消费级界面至少 3 个同类页面，每个有来源链接。  
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

## 各环节接到哪里

| 现有环节 | 先搜什么 | 已有能力 |
| :--- | :--- | :--- |
| 用研 / 竞品 CMP | 记忆 → Mobbin / Page Flows | CMP1–3 样本纪律 |
| 流程 | 记忆 → Mobbin flows / Page Flows | F1–F3 |
| 交互 | 记忆 → ARIA APG / UI Patterns | I / U4 |
| 风格与配色 | 本地 style-presets / color-presets | DS、CI |
| 字体 | typography_intelligence | V3 |
| 组件与页面 | 记忆 → shadcn / Magic UI / Figma 套件 | U0、DS3、MI |
| 素材 | 图标/3D/插画 → IconScout；真实摄影 → `IM` / `real_image.py`；无匹配或虚构 → 生图 | V5、V7、IM |
| 动效 | MI | methods-motion |
| 验收 | VE + QA0 | methods-close |

九个建议环节里，风格 / 配色 / 组件 / 动效 / IconScout 本来就有。本文件补的是：**真实案例检索、字体自动选型、可执行验收、内部沉淀**，以及一张统一的 adapter 表。真实摄影的细则在 [methods-image.md](methods-image.md)，不在这里再写一套方法。

## IM 真实摄影（接到 V5 / V7，不是新的视觉方法）

**触发问题**：稿上这一处需要真实世界的照片吗？  
**步骤**：按 [methods-image.md](methods-image.md) 运行 `scripts/real_image.py`。主库 Pixabay + Openverse + 已预置 key 的 Unsplash；Pexels 有 key 才开；具体地点优先 Wikimedia。  
**完成证据**：用上的图有作者、许可证、本地文件；该用真图却直接生图的，本项不过。
