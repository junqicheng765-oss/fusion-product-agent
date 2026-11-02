# 当前来源与设计职责

本版 `0.3.3` 明确产品主线先于设计，保留同事的专业设计方法及原 JQ 的 Figma 执行工作流。设计作为产品锤中的环节承接有效产品输入。

| 范围 | 当前责任 |
| --- | --- |
| 领域研究、业务目标、需求/对象/规则、范围、复杂状态、业务验收与交接 | fusion-product-agent 维护事实与唯一产品正文 |
| 研究/竞品、信息架构、页面职责、交互与文案、风格、颜色/字体、组件/素材、QA0 | 同事的 fusion-design-core 及两项辅助 Skill |
| Figma 初始化与配置复用、用户目标/权限、Agent生成、Computer Use精修、Dev Mode/MCP还原Demo、文案与交互复核 | 原 JQ 执行层适配为同包 fusion-figma-workflow |
| 产品模型 | 84份原文及48项定义保持原摘要；用于产品判断，不另立设计方法 |

## 同事专业设计来源

固定来源 `https://github.com/savvydd/jq-product-agent` 的 `feat/design-handoff-contract` 提交 `6dcc771bb7b5d0c5f4d2ca25fc13994af12c73a1`。完整导入 design-thinking-os 234份、impeccable 127份、ui-ux-pro-max 73份，共434份；不导入另一套产品主线或阶段包装。

[design-source.json](design-source.json)逐文件记录原始与适配摘要；仓库 `tools/import_design_core.py`、`tools/design_execution_adapter.py`及`tools/product_stage_adapter.py`可重建。35份文本适配、399份字节不变；脚本、组件、主题和素材保持源字节。

除名称/父入口接入外，明确适配主入口、UI分流、工具路由、视觉工具表和QA0中的执行约束：移除无条件HTML优先及Figma Agent禁令，CSS检查限于适用代码路线；Figma原生稿以实际组件/变量/素材及画布证据核验。研究、风格判断和QA0专业目标继续使用同事方法，不能称作者分支原封不动的包。

0.3.2在设计主入口、分诊与路由加入产品启动依赖，并收窄候选假设推进的适用范围。相对0.3.1仅修改上述三份设计集成文本，其余431份同事模块文件保持字节不变。Figma仅修改执行入口增加产品输入先决条件，六份执行手册保持不变；不改变专业方法或素材来解决主流程衔接问题。

## 原 Figma 执行来源

来源为 JQ Product Agent `1.1.5`，完整保留原执行入口、生成/精修手册、Dev Mode到Demo手册、初始化/复用、执行前核对卡、文案与交互复核；从原设计交付文档摘取设计任务包章节。七份文件均以包内路径适配，不依赖作者全局Skill或账号。

[figma-source.json](figma-source.json)记录源路径、原始文件摘要、摘取标识和适配摘要，仓库 `tools/import_figma_workflow.py --source-plugin-root <原插件目录>` 可重建。产品事实归融合主线，设计判断与QA0归同事模块；只恢复执行能力，不恢复旧设计判断或A–F产品阶段。

已有本产品Figma主稿或已选Figma时，先完成主稿再按同版设计还原Demo；旧页直接精修，新整页按需Agent生成后精修。配置、目标与权限分别验证。HTML转Figma为显式且有实际工具的可选分支，不声称已集成验证。

## 产品底座沿革与边界

继承强子产品Agent `2026.09.30.2`、JQ `1.1.5`、Peter Matrix-AI `v0.26` 的固定来源，详见[provenance.json](provenance.json)。本轮未重新获取其他上游版本。包提供方法和资源；工具、账号、目标编辑权及真实设计效果需在使用项目验证。来源许可继续适用，不添加未经确认的统一许可。

0.3.3恢复每条成果回复首行的产品六阶段、设计四步骤导航及下一步引导。设计和Figma入口回传相同位置，安装生成的Subagent入口保留导航。只增加集成约束，保留专业方法和来源文件的可重建适配。
