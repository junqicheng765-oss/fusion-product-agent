# Figma 执行接入

设计判断由同包 [设计专家](../../fusion-design-core/SKILL.md)负责；实际工具初始化、目标绑定、Figma Agent 生成、Computer Use 精修、Dev Mode / MCP 读取及 Demo 还原，统一执行同包 [fusion-figma-workflow](../../fusion-figma-workflow/SKILL.md)。必须实际读取相关手册，不以本摘要代替执行。

首次设计读取[初始化与复用](../../fusion-figma-workflow/references/initialization.md)。尚无路线时，用原生 Question 询问是否使用 Figma，并按缺口引导配置。已有本产品 Figma 主稿或已明确选择 Figma 时，先在指定 Figma 完成本次设计，再按同版节点还原 Demo；仅作竞品/灵感参考的链接不触发此默认。已有配置、有效选择和授权不重复收集。

已有页直接 Computer Use 精修，新增整页需要生成时才要求实际可用的 Figma Agent，然后精修。Figma MCP、Agent、Computer Use、账号与文件读写权分别验证；缺少 Agent 不阻断条件齐备的旧页编辑。已选 Figma 缺工具时先恢复，不静默换为本地独立设计。

用户指定归属、文件/Frame、允许动作及保护范围；没有目标时请用户提供或明确授权代建，不随机新建团队、项目或文件。普通节点链接能定位则复用，不强制再复制 Dev Mode 链接。用户明确选择本地路线时，沿用专业组件、素材与 QA0；HTML 转 Figma 仅为显式选择且有实际工具的可选路线，不承诺已经实现或验证。

IconScout MCP 声明在包根目录 `.mcp.json`，不代表服务已认证。项目级安装只复制完整规则与资源，不改宿主 MCP 设置，也不携带账号、令牌或编辑权限。具体配置指引按当前宿主及官方说明核实。

回传实际使用工具、文件/节点/版本、输入输出对应、画布/截图/代码与运行证据、未覆盖和恢复动作。服务返回、可编辑图层、静态检查、动态体验和用户确认分别表达。
