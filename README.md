# 融合产品锤 · Fusion Product Agent

**v0.3.1 · 2026-11-01**

帮助有业务想法、但缺乏产品与领域知识的使用者，完成领域研究、产品规则、范围、专业设计、可操作体验及上下游交接。支持产品领域能力校验；首期可在Codex下运行，也可由具备文件读取能力的Agent按入口使用。

本版采用设计同事的专业方法与QA0，同时保留原有Figma执行工作流：初始化并复用配置，在指定Figma生成或精修设计，再按同版Dev Mode / MCP还原Demo。产品主线维护业务目标、领域依据、规则及交接。

## 安装使用

```sh
codex plugin marketplace add https://github.com/junqicheng765-oss/fusion-product-agent.git
codex plugin add fusion-product-agent@fusion-product-agent
```

安装后新建聊天，选择“融合产品锤”或输入：

> 使用 $fusion-product-agent。请理解我的想法与业务目标，主动研究领域需求和边界，按本次范围完成方案、设计与交接。

已有GitHub来源安装，可先执行`codex plugin marketplace upgrade fusion-product-agent`，再执行上面的`codex plugin add`更新插件。当前运行中的旧会话不保证热加载；菜单没有刷新时重新打开Codex。

独立插件名与市场仍为`fusion-product-agent`，可与JQ正式版、设计试用版并存。安装本包不需要同时安装原来的三套产品锤子。

## 完整能力包与工作方式

- [v0.3.1完整能力包](downloads/fusion-product-agent-v0.3.1.zip) · [SHA-256](downloads/fusion-product-agent-v0.3.1.zip.sha256)
- [详细使用、五项Skill与项目级Skill/Subagent安装](package/README.md)
- [完整工作流程](docs/workflow.md)
- [产品主入口](package/skills/fusion-product-agent/SKILL.md) · [设计专家入口](package/skills/fusion-design-core/SKILL.md) · [Figma执行入口](package/skills/fusion-figma-workflow/SKILL.md)
- [设计替换范围及固定来源](package/SOURCE-MAP.md) · [版本记录](CHANGELOG.md)
- [检查结果与能力边界](package/VALIDATION.md)

产品输入 → 设计专家判断切入点 → 研究/流程/交互 → 风格确认 → 组件与素材制作 → QA0及实际验证 → 产品核对业务与版本 → 下游交接。存量延展、已有稿还原和从0到1按设计专家规则分流。

已有本产品Figma主稿或已选Figma时，先在指定Figma完成设计：旧页Computer Use精修，新整页按需Figma Agent生成后精修，再由Dev Mode / MCP还原Demo。明确选择本地代码时才走本地组件路线；HTML转Figma为实际可用且显式选择的可选分支。

包内包含设计主模块、UI/UX Pro Max、Impeccable、Figma执行工作流及完整资源。方法和资源不附带Figma、素材、生图或浏览器账号与权限，需检查宿主实际能力和授权。

## 验证

```sh
python3 package/scripts/validate_package.py
python3 package/scripts/test_package.py
```

已通过结构、来源摘要与离线安装/交付引用检查，并验证部分设计工具路径。尚未完成本版整条设计流程的真实业务试用；这些检查不证明实际设计质量、Agent遵循率或生产能力。

来源的许可与权利说明继续适用；本包不添加未经确认的统一开放许可。历史[0.2.0 ZIP](downloads/fusion-product-agent-v0.2.0.zip)保留供回查，与本版内容不同。
