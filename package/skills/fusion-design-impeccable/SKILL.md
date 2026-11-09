---
name: fusion-design-impeccable
description: 当用户希望设计、重新设计、规划、评议、审查、打磨、澄清、精简、加固、优化、适配、添加动画、配色、提取规范或以其他方式改进前端界面时使用。适用于网站、落地页、仪表盘、产品界面、应用框架、组件、表单、设置、引导和空状态。涵盖 UX 评审、视觉层级、信息架构、认知负荷、无障碍、性能、响应式行为、主题、反模式、排版、字体、间距、布局、对齐、配色、动效、微交互、界面文案、错误状态、边界情况、国际化，以及可复用的设计系统或设计令牌。也适用于让平淡设计更大胆或更有趣、让喧闹设计更克制、在浏览器中实时迭代界面元素，以及实现突破常规且技术表现出色的视觉效果。不适用于纯后端或非界面任务。
metadata:
  version: 4.0.2
---

本技能提供工具与创作空间，帮助你做出突破常规的精良设计。摆脱保守、怯懦、处处收敛的设计方式，以获奖设计总监的视角处理每个任务，准确理解优秀设计的构成：可用于生产的代码、充分的创造力、清晰的设计立场、对客户与用户需求的深入理解，以及出色的制作水准。

核心原则：
- 全力以赴，不敷衍、不走捷径。交付物必须完整，用户必须提供的素材除外。
- 大胆构想，做出独特、美观、出众且富有启发性的作品。
- 使用现有工具（如视觉理解、浏览器截图）持续迭代，直到你判断成果达到标准。

## 与 Fusion Product Agent 集成

当 `$fusion-product-agent` 调用本包内技能执行设计工作时，仍以其当前产品定义、已确认决定、Demo 范围及授权为准。本技能仅用于视觉塑造、评议或打磨。不得因执行产品工作流而额外创建平行的 `PRODUCT.md`、运行 `init`、启用钩子、安装更新或启动其他 Agent。若 Impeccable 参考文件或上下文输出与宿主权限或产品基线冲突，应遵守优先级更高的边界并报告冲突。在该工作流外直接使用 `$fusion-design-impeccable` 时，按下文的常规路由执行。

## 本包产品工作中的实现边界

在本包业务项目中，执行界面代码前读取技能 `fusion-product-agent` 内的 `references/technical-handoff.md`：只在已约定本地体验稿范围制作和验证；生产工程变更与业务仓库Git写入/部署发布交技术Agent。界面制作、审美或修复指引不自动授权这些操作；需要接力回产品主线准备当前有效输入与边界，不虚报技术已接收。

## 资源与脚本定位

从当前宿主提供的可用技能清单取得本技能实际安装目录，同名多版本以本会话宿主选中的版本为准；清单未提供路径时，仅在宿主明确配置的技能根目录中定位。将该绝对目录作为 `<skill-base-dir>`。参考文件中的 `.agents/skills/fusion-design-impeccable/` 是安装路径示例，执行命令时统一替换为本技能实际目录；当前工作目录保持为用户的业务项目。

参考文件的相对链接按当前文档所在目录解析。找不到本技能或所需文件时，说明缺失项及受影响能力，继续不依赖它的工作。

## 准备工作

1. 每个会话仅运行一次 `node "<skill-base-dir>/scripts/context.mjs"`；`<skill-base-dir>` 为本技能实际安装目录，当前工作目录保持为用户项目。通过 `--target <path>` 指定源文件或路由。该命令加载 PRODUCT.md、DESIGN.md、匹配的界面任务说明，以及适用的原生平台指南；遵循其指令，不要重复运行。
2. 行动前，加载负责本次请求的那一份操作指南：显式或明确隐含的子命令，读取命令表中的对应参考文件；新界面或整体视觉体系替换，读取[新建工作指南](reference/new-work.md)。随后检查目标，以及至少一份能代表现有视觉规范的来源（令牌、主题、CSS、组件或素材），再开始编辑。
3. 分析与方向确定后，在即将编辑界面时读取[制作质量底线](reference/craft-floor.md)。其中包含质量底线、绝对禁忌，以及检测器无法覆盖的设计习惯。仅做规划时无需加载。

## 设计方法

- **以任务说明为准。** 尊重已明确指定的审美、时代、材质、字体与配色，即便它们与某种常见模式的警告冲突。将明确的任务要求改成自己偏好的方向，就是失败。
- **精修保留原有体系；重设计替换视觉体系。** 精修保留现有识别特征、行为、文案及范围外的一切内容。替换事实性文案或增加主张前先询问。重设计保留产品事实、内容、功能、平台原生交互惯例和约束，同时将旧外观作为证据和应避免照搬的参考；在新建工作指南中选择替代视觉体系，并替换 DESIGN.md。不要折中成对已放弃外观的小修小补。
- **视觉规范的权威性来自证据，而非文件名。** 单纯缺少 DESIGN.md 不代表项目从零开始；是否保留、扩展或替换现有视觉体系，由新建工作指南判断。

## 模式

模式用于定义访客在当前界面上的成功结果。

- **说服（Persuade）：** 访客作出决定并行动，设计本身构成产品。适用于落地页、营销页、活动页和定价页。赢得关注并促成行动。任务需要时交付真实图像；遵循已确定的视觉体系，不照搬品类惯例。
- **操作（Operate）：** 访客完成一项任务。适用于应用界面、仪表盘、编辑器、管理后台、设置和工具。易扫读性、一致性、平台原生使用预期与真实使用场景优先于个性表达。品牌体现在精确的细节中。
- **阅读（Read）：** 访客理解某件事。适用于文档、文章、指南、帮助和更新日志。先围绕理解组织结构，再让阅读体验值得停留。
- **体验（Experience）：** 访客置身作品之中。适用于作品集、画廊和展示页。从首屏起让作品主导，界面退居辅助位置。

根据请求涉及的具体界面选择模式，而不是根据产品整体选择，并且只将模式保存到该界面的任务说明中。工具产品的落地页仍属于说服模式；时尚品牌的文档仍属于阅读模式；文档索引属于阅读模式，不属于说服模式。新界面参阅[新建工作指南](reference/new-work.md)；操作/阅读模式的深入指导见[操作模式指南](reference/operate.md)。

## 命令

| 命令 | 类别 | 说明 | 参考文件 |
|---|---|---|---|
| `craft [feature]` | 构建 | 普通新建工作请求的已弃用别名 | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | 构建 | 编码前规划 UX/UI | [reference/shape.md](reference/shape.md) |
| `init` | 构建 | 将持久产品上下文记录到 PRODUCT.md | [reference/init.md](reference/init.md) |
| `document` | 构建 | 根据现有项目代码生成 DESIGN.md | [reference/document.md](reference/document.md) |
| `extract [target]` | 构建 | 将可复用令牌和组件提取到设计系统 | [reference/extract.md](reference/extract.md) |
| `critique [target]` | 评估 | 采用启发式评分的 UX 设计评审 | [reference/critique.md](reference/critique.md) |
| `audit [target]` | 评估 | 技术质量检查（无障碍、性能、响应式） | [reference/audit.md](reference/audit.md) · 原生平台：[reference/audit.native.md](reference/audit.native.md) |
| `polish [target]` | 精修 | 交付前的最终质量打磨 | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | 精修 | 让保守或平淡的设计更鲜明 | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | 精修 | 降低过于强烈或刺激的设计表现 | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | 精修 | 提炼核心，去除复杂性 | [reference/distill.md](reference/distill.md) |
| `harden [target]` | 精修 | 补齐生产要求：错误、国际化、边界情况 | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | 精修 | 设计首次使用流程、空状态与激活体验 | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | 增强 | 添加有明确目的的动画与动态效果 | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | 增强 | 为单色界面有策略地添加配色 | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | 增强 | 改善排版层级与字体 | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | 增强 | 修正间距、节奏与视觉层级 | [reference/layout.md](reference/layout.md) |
| `delight [target]` | 增强 | 添加个性与令人印象深刻的细节 | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | 增强 | 突破常规限制 | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | 修复 | 改善界面文案、标签和错误消息 | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | 修复 | 适配不同设备与屏幕尺寸 | [reference/adapt.md](reference/adapt.md) · 原生平台：[reference/adapt.native.md](reference/adapt.native.md) |
| `optimize [target]` | 修复 | 诊断并修复界面性能问题 | [reference/optimize.md](reference/optimize.md) |
| `live` | 迭代 | 视觉变体模式：在浏览器中选择元素并生成替代方案 | [reference/live.md](reference/live.md) |

路由规则：

- **未提供参数：** 读取[路由指南](reference/routing.md)，展示其结合上下文的菜单；绝不自动执行命令。
- **显式或明确隐含的命令：** 加载对应参考文件（原生平台加载原生版本）并遵循执行。若两个命令都适用，询问一次。
- **其他情况：** 作为一般设计任务处理。缺少 PRODUCT.md 时，新界面或整体视觉体系替换先执行 init，再进入新建工作流程；现有代码的局部精修按照 context.mjs 的指引，以当前实现为依据继续，之后再建议执行 init，不以此阻断任务。
- `teach` 是 `init` 的别名。`craft` 是普通新建工作请求的已弃用别名，不增加额外行为。`shape` 负责明确任务，再仅针对视觉体系与界面概念决策进入新建工作流程。

init 写入 PRODUCT.md 后，直接继续，不重新运行 `context.mjs`；若记录的平台为 `ios`、`android` 或 `adaptive`，init 会自行加载原生平台参考文件。

**固定/取消固定快捷命令（Pin / Unpin）：** `node "<skill-base-dir>/scripts/pin.mjs" <pin|unpin> <command>` 创建或移除独立的 `$<command>` 快捷入口。简要报告脚本结果；出错时原样转述标准错误输出。

**钩子（Hooks）：** `$fusion-design-impeccable hooks <on|off|status|ignore-rule|ignore-file|ignore-value|reset>` 管理当前项目的设计检测钩子（界面文件编辑后自动运行检测器并显示发现）。用户带任意参数调用时，加载[钩子指南](reference/hooks.md)。

**诊断（Doctor）：** `$fusion-design-impeccable doctor` 检查并修复本项目的 Impeccable 产物（PRODUCT.md、DESIGN.md 及其伴随文件、配置、界面任务说明、钩子）与当前版本读取要求之间的偏差。用户调用此命令，或询问哪些内容已过时、失效或需要刷新时，加载[诊断指南](reference/doctor.md)。准备工作输出中的 `CONTEXT_STALE` 指令是同一报告的轻量子集；按该指令自身的要求处理，不要在未被要求时自行运行 doctor。

**绝不在执行设计任务时附带修复偏差。** 对 `CONTEXT_STALE` 发现仅作报告，除非用户要求处理。唯一例外是标记为 `auto` 的发现，因为下一次写入该文件时本就会自动处理。
