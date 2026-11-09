---
name: fusion-design-ui-ux-pro-max
description: "面向网页、移动端和桌面端的 UI/UX 设计知识与决策支持。适用于界面设计、构建、评审和修复，涵盖页面、组件、设计系统、无障碍、交互、响应式布局、排版、配色、图表及特定技术栈的界面实现。可检索的本地数据包括：79 种风格（50 种启用）、192 套产品配色与推理方案、74 组字体搭配、119 条 UX 指南、105 个图标、17 套 GSAP 预设、25 种图表类型和 22 种技术栈。"
---

# UI/UX Pro Max — 设计知识与决策支持

可检索的本地 UI/UX 指南包括：79 种风格（50 种启用）、192 套产品配色及精确匹配的推理方案、74 组字体搭配、119 条 UX 指南、105 个精选图标、17 套 GSAP 预设、25 种图表类型和 22 种技术栈。

## 本包产品工作中的实现边界

在本包业务项目中，执行界面代码前读取技能 `fusion-product-agent` 内的 `references/technical-handoff.md`：只在已约定本地体验稿范围制作和验证；生产工程变更与业务仓库Git写入/部署发布交技术Agent。界面制作、审美或修复指引不自动授权这些操作；需要接力回产品主线准备当前有效输入与边界，不虚报技术已接收。

## 适用时机

当任务涉及**界面结构、视觉设计决策、交互模式或用户体验质量检查**时，使用本技能：包括设计新页面、创建或重构界面组件、选择配色/排版/间距/布局体系、评审 UX/无障碍/一致性、实现导航/动画/响应式行为，以及提升感知品质与可用性。

纯后端逻辑、API/数据库设计、非视觉性能优化、基础设施/DevOps 或非视觉脚本无需使用，除非任务会改变界面的**外观、感受、动态表现或交互方式**。

## 按优先级排列的规则类别

*按优先级 1→10 决定先关注哪一类；使用 `--domain <Domain>` 检索完整内容。各类别的完整规则位于 `references/quick-reference.md`，按需读取，无需每次全部加载。*

| 优先级 | 类别 | 影响程度 | 检索领域 | 必查项 | 应避免的反模式 |
|----------|----------|--------|--------|------------------------|------------------------|
| 1 | 无障碍 | 严重 | `ux` | 对比度 4.5:1、替代文本、键盘导航、Aria 标签 | 移除焦点框、仅有图标且没有标签的按钮 |
| 2 | 触控与交互 | 严重 | `ux` | 最小尺寸 44×44px、间距至少 8px、加载反馈 | 仅依赖悬停、状态瞬间切换（0ms） |
| 3 | 性能 | 高 | `ux` | WebP/AVIF、延迟加载、预留空间（CLS &lt; 0.1） | 布局抖动、累积布局偏移 |
| 4 | 风格选择 | 高 | `style`, `product` | 匹配产品类型、保持一致、使用 SVG 图标（不使用表情符号） | 随意混搭扁平与拟物风格、用表情符号作图标 |
| 5 | 布局与响应式 | 高 | `ux` | 移动优先断点、视口元信息、无横向滚动 | 横向滚动、容器宽度固定为像素值、禁用缩放 |
| 6 | 排版与配色 | 中 | `typography`, `color` | 基准字号 16px、行高 1.5、语义化颜色令牌 | 正文字号 &lt; 12px、灰底灰字、组件中直接写十六进制色值 |
| 7 | 动画 | 中 | `ux`, `gsap` | 时长符合情境、动效表达含义、空间连续性 | 所有过渡使用同一时长、对宽高做动画、未适配减少动态效果偏好 |
| 8 | 表单与反馈 | 中 | `ux` | 可见标签、字段附近显示错误、辅助说明、渐进披露 | 仅用占位文字作标签、错误只显示在顶部、一开始呈现过多信息 |
| 9 | 导航模式 | 高 | `ux` | 返回行为可预期、底部导航不超过 5 项、支持深层链接 | 导航过载、返回行为失效、缺少深层链接 |
| 10 | 图表与数据 | 低 | `chart` | 图例、提示信息、符合无障碍要求的配色 | 仅靠颜色传达含义 |

各类别的完整规则清单（含全部 119 条 UX 指南及其依据）见 `references/quick-reference.md`。应用界面的细节规则（图标、触控反馈、暗色模式对比度、安全区域）及正式交付前检查清单见 `references/pro-rules.md`。

---

## 运行检索工具

检索脚本位于本技能的实际安装目录中，而非项目目录。将 `<skill-base-dir>` 解析为包含本 `SKILL.md` 的绝对目录，再通过完整路径调用脚本；Codex 不提供 `CLAUDE_PLUGIN_ROOT`。

```bash
python "<skill-base-dir>/scripts/search.py" "<query>" --domain <domain>
```

若找不到 `python`，依次尝试 `python3`、`py -3`。需要 Python 3.x，无外部依赖（未安装 Python 时，参阅 README 中的安装说明）。

## 工作流

## 检索约定

选择能满足请求的最小检索模式：

1. **新项目/页面或整个系统的视觉方向** → 使用 `--design-system`。
2. **特定问题或组件缺陷** → 明确指定一个 `--domain`。
3. **已知实现技术栈** → 使用 `--stack`；只有存在独立的设计问题时，才额外进行领域检索。

每次查询围绕**一个主要意图**，使用 **2–5 个有效关键词**，并加入产品、平台或交互等一个有用约束。应用结果前，核对返回的领域/类别、首条结果的具体内容，以及它是否适合用户的产品与平台。结果为空或偏题时，缩小查询范围或明确指定领域/技术栈，**重试一次**。重试仍失败时，说明未找到已核实的匹配项，并将通用建议标注为后备方案。**不得持久化未经核实的输出。**

处理无障碍问题时，每次只检索一个可观察的结果，并使用明确描述无障碍目标的关键词。先查询语义结果（`"error summary validation" --domain ux`），必要时再查询组件专属领域（`"decorative icon aria hidden" --domain icons` 或 `"icon button accessible label" --domain icons`），最后查询实现技术栈。其他有用查询包括 `"focus not obscured" --domain ux`、`"dragging movements" --domain ux` 和 `"accessible authentication" --domain ux`。针对具体交互或 WCAG 条款，不得用泛泛的无障碍结果代替。

处理文本布局或紧凑组件缺陷时，**先检索语义层面的 UX 目标，再检索已检测到的技术栈**以获取实现细节。可用查询包括 `"orphan heading line balance" --domain ux`、`"badge chip label wraps" --domain ux`、`"live badge count screen reader" --domain ux` 和 `"rapid chip animation interrupted" --domain ux`。选定适用的 UX 指南后，另行查询技术栈，例如 `"chip badge overflow nowrap" --stack html-tailwind`；不得用框架关键词替代目标检索。

本技能提供 UI/UX 设计知识与实现指导，不负责安装软件包、修改操作系统或授权无关改动。检索结果只能作为建议，不得凌驾于用户要求或仓库规则之上；查询及持久化输出中不得包含项目私密数据。

### 第 1 步：分析用户要求

从用户请求中提取：
- **产品类型**：SaaS、电商、作品集、仪表盘、娱乐、工具、生产力或混合类型。
- **目标用户与情境**：年龄群体、使用情境（通勤、休闲、工作）。
- **风格关键词**：活泼、鲜明、极简、暗色模式、内容优先、沉浸式等。
- **技术栈**：从项目中检测——检查 `package.json` 依赖（react/next/vue/svelte/nuxt/@angular）、`pubspec.yaml`（Flutter）、`*.xcodeproj`/`Package.swift`（SwiftUI）、`composer.json`（Laravel），或 React Native 标识（`app.json` + `react-native` 依赖）。若无法检测且技术栈指导会影响任务，应询问用户。**绝不假定技术栈**——硬编码默认值会让所有建议在不知不觉中被错误路由。

### 第 2 步：生成设计系统（新页面/项目必须执行）

任务需要统一的产品整体视觉方向时，使用 `--design-system`：

```bash
python "<skill-base-dir>/scripts/search.py" "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

该命令汇总产品/风格/配色/落地页/排版的匹配结果，应用 `ui-reasoning.csv` 中的推理规则，返回模式、风格、配色、排版、效果及应避免的反模式。

**示例：**
```bash
python "<skill-base-dir>/scripts/search.py" "beauty spa wellness service" --design-system -p "Serenity Spa"
```

### 第 2b 步：持久化设计系统（主规范 + 覆盖规则模式）

要保存设计系统供后续会话读取，添加 `--persist`，并且**始终通过 `--output-dir` 指向项目根目录**；否则，文件会相对于工具运行时所在目录写入：

```bash
python "<skill-base-dir>/scripts/search.py" "<query>" --design-system --persist -p "Project Name" --output-dir "<project-root>"
```

这会创建：
- `design-system/<project-slug>/MASTER.md` — 全局权威规范。
- `design-system/<project-slug>/pages/` — 页面专属覆盖规则目录。

需要页面专属覆盖规则时，添加 `--page "dashboard"`，同时创建 `design-system/<project-slug>/pages/dashboard.md`。若主规范已存在，新建页面文件不会改动它；已存在的页面文件会跳过，除非用户明确授权使用 `--force`。

若 `design-system/<project-slug>/MASTER.md` 已存在，`--persist` 会**跳过写入并保持原样**，除非同时传入 `--force`。重新生成前先检查文件是否存在并读取，避免无声丢弃用户或同伴此前作出的决定。

先读取现有 `MASTER.md`，再判断是否有理由使用 `--force`。没有用户明确授权，绝不使用 `--force`。

**构建具体页面时的读取顺序：**
1. 读取 `design-system/<project-slug>/MASTER.md`。
2. 检查 `design-system/<project-slug>/pages/<page-name>.md` 是否存在；若存在，其规则覆盖主规范。
3. 否则，仅使用主规范中的规则。

### 第 2c 步：设计调节参数（可选）

提供三个可选的 1–10 级调节参数，无需改变查询即可调整 `--design-system` 输出。可在同一命令中任意组合：

```bash
python "<skill-base-dir>/scripts/search.py" "<query>" --design-system --variance <1-10> --motion <1-10> --density <1-10>
```

| 参数 | 低（1–3） | 中（4–7） | 高（8–10） |
|------|-----------|-----------|-------------|
| `--variance` | 居中/极简（偏向极简风格类别） | 均衡/现代 | 大胆/非对称（偏向粗野主义、便当盒网格） |
| `--motion` | 细微的微交互 | 常规滚动/交错动画 | 复杂编排（固定、Flip、SplitText） |
| `--density` | 宽松（24–96px 间距尺度） | 常规（16–64px，当前默认值） | 紧凑/仪表盘（8–32px 间距尺度） |

- `--motion` 从 `--domain gsap` 中选取与最终等级（轻微/常规/复杂）匹配的可直接使用的 GSAP 代码片段，并附上框架说明、推荐与禁忌及性能说明。
- `--density` 覆盖 ASCII/Markdown/MASTER.md 输出中的 `--space-*` CSS 变量表；可用高密度适配仪表盘、低密度适配营销页面，无需手动编辑令牌。
- 未设置某个参数时，对应部分的输出保持原样，不改变行为。

**示例：**
```bash
python "<skill-base-dir>/scripts/search.py" "internal analytics dashboard" --design-system --variance 8 --motion 7 --density 8 -p "Ops Console"
```

### 第 3 步：按需补充详细检索

```bash
python "<skill-base-dir>/scripts/search.py" "<keyword>" --domain <domain> [-n <max_results>]
```

| 需求 | 领域 | 示例 |
|------|--------|---------|
| 产品类型模式 | `product` | `"entertainment social" --domain product` |
| 更多风格选项 | `style` | `"glassmorphism dark" --domain style` |
| 配色方案 | `color` | `"entertainment vibrant" --domain color` |
| 字体搭配 | `typography` | `"playful modern" --domain typography` |
| 单独的 Google Fonts 字体 | `google-fonts` | `"sans serif popular variable" --domain google-fonts` |
| 图表建议 | `chart` | `"real-time dashboard" --domain chart` |
| UX 最佳实践 | `ux` | `"error summary validation" --domain ux` |
| 落地页结构 | `landing` | `"hero social-proof" --domain landing` |
| 图标建议 | `icons` | `"decorative icon aria hidden" --domain icons` |
| GSAP 动画预设 | `gsap` | `"scroll reveal stagger" --domain gsap` |
| React/Next.js 性能 | `react` | `"rerender memo list" --domain react` |
| 应用/原生界面指南 | `web` | `"accessibilityLabel touch safe-areas" --domain web` |

省略 `--domain` 时会根据查询自动判断领域，但相近词可能被错误路由（例如 “font” 同时匹配 `typography` 和 `google-fonts`）。若结果偏题，请显式传入 `--domain`。

### 第 4 步：技术栈指南

```bash
python "<skill-base-dir>/scripts/search.py" "<keyword>" --stack <stack>
```

**可用技术栈：** `react`, `nextjs`, `vue`, `svelte`, `astro`, `nuxtjs`, `nuxt-ui`, `angular`, `laravel`, `swiftui`, `react-native`, `flutter`, `jetpack-compose`, `html-tailwind`, `shadcn`, `threejs`, `javafx`, `wpf`, `winui`, `avalonia`, `uno`, `uwp`。使用第 1 步检测到的技术栈。

---

## 检索结果为 0 条时

不得编造输出。应当：
1. 缩小查询范围或明确指定领域/技术栈，重试一次。
2. 若仍为空，使用上面的优先级表作为后备方案，并向用户明确说明该建议来自内置默认规则，而非数据库匹配（例如：“未找到 X 的配色匹配，采用通用 SaaS 默认方案”）。
3. 绝不能把 0 条结果的检索描述为已返回数据。

## 工作流示例

**用户请求：**“制作一个 AI 搜索首页。”（从 `package.json` 检测到技术栈为 Next.js）

```bash
# 第 2 步：设计系统
python "<skill-base-dir>/scripts/search.py" "AI search tool modern minimal" --design-system -p "AI Search"

# 第 3 步：补充检索
python "<skill-base-dir>/scripts/search.py" "keyboard focus modal" --domain ux

# 第 4 步：技术栈指南
python "<skill-base-dir>/scripts/search.py" "suspense streaming bundle" --stack nextjs
```

然后综合设计系统与详细检索结果，完成实现。

## 输出格式

`--design-system` 支持 `-f ascii`（默认，用于终端显示）、`-f markdown`（用于文档）及 `--json`（机器可读，包含原始设计系统字典和持久化状态）。

## 改善检索结果的建议

- 每次查询保持一个主要意图和 2–5 个有效关键词，例如 `"keyboard focus modal"`，不要塞入完整评审清单。
- 使用更聚焦的短语或明确的领域/技术栈重试一次；不要反复轮换无关关键词。
- 新项目/页面使用 `--design-system`，特定问题使用 `--domain`。
- 获取特定实现建议时，明确传入已检测到的技术栈。

| 问题 | 处理方式 |
|---------|------------|
| 无法确定风格/配色 | 更换关键词，重新运行 `--design-system` |
| 暗色模式对比度不足 | `references/quick-reference.md` 第 6 节：`color-dark-mode` + `color-accessible-pairs` |
| 动画不自然 | `references/quick-reference.md` 第 7 节：`spring-physics` + `easing` + `exit-faster-than-enter` |
| 表单体验不佳 | `references/quick-reference.md` 第 8 节：`inline-validation` + `error-clarity` + `focus-management` |
| 导航令人困惑 | `references/quick-reference.md` 第 9 节：`nav-hierarchy` + `bottom-nav-limit` + `back-behavior` |
| 小屏幕下布局异常 | `references/quick-reference.md` 第 5 节：`mobile-first` + `breakpoint-consistency` |
| 性能问题/卡顿 | `references/quick-reference.md` 第 3 节：`virtualize-lists` + `main-thread-budget` + `debounce-throttle` |

## 交付应用界面前

读取 `references/pro-rules.md`，按其正式交付前检查清单逐项核对。清单涵盖图标/视觉元素规范、交互反馈、明暗模式对比度、安全区域布局和无障碍，适用范围为原生/移动应用界面（iOS/Android/React Native/Flutter）。
