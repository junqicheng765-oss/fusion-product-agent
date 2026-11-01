# 融合产品锤 0.3.0

2026-11-01版本。产品领域研究、需求与规则、复杂状态、业务验收和交接沿用融合锤子；设计部分整体替换为同事分支的设计专家模块，不再运行旧设计方法。本版通过融合锤子独立GitHub仓库分发。

## 设计由谁负责

- [fusion-product-agent](skills/fusion-product-agent/SKILL.md)：产品主线，提供目标、领域依据、规则、范围与验收预期；接回设计结果，核对业务与版本。
- [fusion-design-core](skills/fusion-design-core/SKILL.md)：设计主责，负责设计研究、竞品、信息架构、流程/交互、风格、组件/素材、Figma/代码与QA0终审。
- [fusion-design-ui-ux-pro-max](skills/fusion-design-ui-ux-pro-max/SKILL.md)：按设计任务检索UI/UX方法与实现建议。
- [fusion-design-impeccable](skills/fusion-design-impeccable/SKILL.md)：按需制作、审视和精修；服务设计主流程，不另立产品规则或覆盖QA0。

原融合版的设计分层、风格选择办法、Figma优先路线、视觉/交互制作清单已撤换。产品能力模型保留原文，作为产品判断依据；它不与新设计模块争夺设计执行权。详见[替换范围与来源](SOURCE-MAP.md)。

## 当前工作链

产品理解与领域研究 → 规则/范围/场景与业务验收 → [设计交接](skills/fusion-product-agent/references/design-and-demo.md) → 设计专家判断切入点 → 专业设计与QA0 → 产品核对业务/版本与下游交接。

0到1设计按同事入口先完成并汇报研究、竞品、流程和具体交互，再原生提问确认风格等事项，随后调组件、主题、字体与真实素材制作。存量延展和按正式稿还原走设计模块对应分流。不是所有任务都重新走0到1。

同事最新版的新建UI路线为本地高保真组件页面优先，需要Figma时再按实际可用能力转换。若用户指定已有Figma主稿或交付格式，按任务合同与相应分流处理，不能暗换路线。Figma云端Agents不是本版新建页面的默认生成路径。

## 使用与完整安装

可在新的试验项目让Agent读取本包`skills/fusion-product-agent/SKILL.md`，按当前需求调用同包设计模块。无需把同事的整个JQ产品流程也装进来。

项目级Skill：

```sh
python3 scripts/install.py --project /absolute/path/to/project --mode skill --dry-run
python3 scripts/install.py --project /absolute/path/to/project --mode skill
```

四项Skill完整复制到项目`.agents/skills/`，新会话使用`$fusion-product-agent`。

项目级Subagent：

```sh
python3 scripts/install.py --project /absolute/path/to/project --mode agent --dry-run
python3 scripts/install.py --project /absolute/path/to/project --mode agent
```

四份完整资源复制到项目`.codex/resources/`，注册一个产品主Subagent。子Agent按相邻路径读取设计模块，不注册第二套项目Skill，也不自动启动额外Agent。主任务统一向用户提问。

两种安装方式互斥；任一同名资源已存在时拒绝整个安装，不覆盖本地定制；复制中途失败撤回本次资源。安装记录包含所有资源路径与摘要。既有项目配置保持原样，无配置时按原安装器规则写入最小Agent配置；不改全局设置。

包内插件元数据同时指向四项Skill和IconScout MCP声明。项目安装器仅复制规则/资源，不修改宿主MCP配置。首次安装后新会话加载；文件存在不代表运行已验证。

## 工具条件

自带方法、组件配方、主题/字体数据、真实素材处理和检查脚本，不提供Figma、Computer Use、浏览器、生图服务账号或付费素材权限。按[工具接入](skills/fusion-product-agent/references/figma-adapter.md)检查；已有有效配置复用，不乱建Figma文件。

安装/校验/交付引用辅助脚本使用Python 3.9+标准库；设计脚本依功能还可能依赖Node、Playwright、Pillow、网络或宿主工具，不应沿用旧包“所有脚本只需标准库”的描述。具体见各脚本帮助与实际环境。

## 检查与升级

```sh
python3 scripts/validate_package.py
python3 scripts/test_package.py
```

校验范围见[验证说明](VALIDATION.md)。安装清单`.codex/fusion-product-agent-install.json`包含`resources`及每份资源的摘要；卸载或升级要检查这些资源是否被本地修改，保留项目产物与定制，不整体删除`.agents`或`.codex`。旧版本仍用旧记录处理。

来源固定为同事分支`6dcc771`；完整文件及适配前后摘要见[设计来源清单](design-source.json)。仅做隔离标识、宿主/父流程接入，以及按作者最新入口澄清两处遗留Figma概括。脚本、组件和素材未删改。来源的既有许可与权利说明继续适用，本版不添加未经确认的统一开放许可。
