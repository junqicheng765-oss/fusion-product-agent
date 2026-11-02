# 融合产品锤 0.3.2

2026-11-02版本。产品负责人先澄清用户、场景、目标、范围与关键规则，再交设计；产品领域研究、需求、复杂状态、业务验收和交接沿用融合锤子。设计判断采用同事分支的专家模块；原有Figma执行流程独立随包提供，不再运行旧设计判断方法。本版通过融合锤子独立GitHub仓库分发。

## 设计由谁负责

- [fusion-product-agent](skills/fusion-product-agent/SKILL.md)：产品主线，提供目标、领域依据、规则、范围与验收预期；接回设计结果，核对业务与版本。
- [fusion-design-core](skills/fusion-design-core/SKILL.md)：设计主责，负责设计研究、竞品、信息架构、流程/交互、风格、组件/素材、提示词与QA0终审。
- [fusion-design-ui-ux-pro-max](skills/fusion-design-ui-ux-pro-max/SKILL.md)：按设计任务检索UI/UX方法与实现建议。
- [fusion-figma-workflow](skills/fusion-figma-workflow/SKILL.md)：初始化与复用、工具/文件权限、生成/精修、真实画布证据、Dev Mode到Demo还原及文案/交互复核。
- [fusion-design-impeccable](skills/fusion-design-impeccable/SKILL.md)：按需制作、审视和精修；服务设计主流程，不另立产品规则或覆盖QA0。

旧设计判断方法已撤换；原有Figma配置、目标绑定、生成/精修、Dev Mode还原和专项复核由同包执行模块承接。产品能力模型保留原文，作为产品判断依据；它不与新设计模块争夺设计执行权。详见[替换范围与来源](SOURCE-MAP.md)。

## 当前工作链

产品需求接收与必要澄清 → 用户/场景/目标/产品形态 → 领域研究与规则/范围/路径/业务验收 → [设计交接](skills/fusion-product-agent/references/design-and-demo.md) → 设计专家判断切入点 → 专业设计与QA0 → 产品核对业务/版本与下游交接。

一句话的0到1产品需求先由产品负责人处理会改变方向的选择；设计阶段复用已有产品研究和决定，再按同事入口完成适用的设计研究、交互、风格及制作。存量延展和按正式稿还原走设计模块对应分流。不是所有任务都重新走0到1。

首次设计先按[执行工作流](skills/fusion-figma-workflow/SKILL.md)读取配置、询问未定路线并绑定用户目标。已有本产品Figma主稿或已选Figma时，先在Figma完成设计；旧页Computer Use精修，新增整页按需Figma Agent生成后精修，核验后由同版Dev Mode / MCP还原Demo。缺工具先恢复，不静默改走本地；明确选本地代码时沿用专业组件与素材。HTML转Figma仅为显式且实际可用的可选分支。

## 使用与完整安装

可在新的试验项目让Agent读取本包`skills/fusion-product-agent/SKILL.md`，按当前需求调用同包设计模块。无需把同事的整个JQ产品流程也装进来。

项目级Skill：

```sh
python3 scripts/install.py --project /absolute/path/to/project --mode skill --dry-run
python3 scripts/install.py --project /absolute/path/to/project --mode skill
```

五项Skill完整复制到项目`.agents/skills/`，新会话使用`$fusion-product-agent`。

项目级Subagent：

```sh
python3 scripts/install.py --project /absolute/path/to/project --mode agent --dry-run
python3 scripts/install.py --project /absolute/path/to/project --mode agent
```

五份完整资源复制到项目`.codex/resources/`，注册一个产品主Subagent。子Agent按相邻路径读取设计模块，不注册第二套项目Skill，也不自动启动额外Agent。主任务统一向用户提问。

两种安装方式互斥；任一同名资源已存在时拒绝整个安装，不覆盖本地定制；复制中途失败撤回本次资源。安装记录包含所有资源路径与摘要。既有项目配置保持原样，无配置时按原安装器规则写入最小Agent配置；不改全局设置。

包内插件元数据同时指向五项Skill和IconScout MCP声明。项目安装器仅复制规则/资源，不修改宿主MCP配置。首次安装后新会话加载；文件存在不代表运行已验证。

## 工具条件

自带方法、组件配方、主题/字体数据、真实素材处理和检查脚本，不提供Figma、Computer Use、浏览器、生图服务账号或付费素材权限。按[工具接入](skills/fusion-product-agent/references/figma-adapter.md)检查；已有有效配置复用，不乱建Figma文件。

安装/校验/交付引用辅助脚本使用Python 3.9+标准库；设计脚本依功能还可能依赖Node、Playwright、Pillow、网络或宿主工具，不应沿用旧包“所有脚本只需标准库”的描述。具体见各脚本帮助与实际环境。

## 检查与升级

```sh
python3 scripts/validate_package.py
python3 scripts/test_package.py
```

校验范围见[验证说明](VALIDATION.md)。安装清单`.codex/fusion-product-agent-install.json`包含`resources`及每份资源的摘要；卸载或升级要检查这些资源是否被本地修改，保留项目产物与定制，不整体删除`.agents`或`.codex`。旧版本仍用旧记录处理。

专业设计来源固定为同事分支`6dcc771`，见[设计来源清单](design-source.json)；原JQ 1.1.5的Figma执行层及本地适配见[Figma来源清单](figma-source.json)。明确适配了HTML优先、Figma Agent禁令和仅适合本地CSS的门槛，专业方法与QA0继续保留。脚本、组件和素材未删改。来源的既有许可与权利说明继续适用，本版不添加未经确认的统一开放许可。
