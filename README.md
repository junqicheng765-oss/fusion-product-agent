# 融合产品锤 · Fusion Product Agent

独立融合版 **v0.2.0**，构建日期 **2026-10-31**。

帮助有业务想法、但缺乏产品与业务领域知识的使用者，将想法推进为有依据的领域需求、产品规则、系统边界、可操作体验及上下游交接。

本仓库与原有 `jq-product-agent` 仓库独立，使用 `fusion-product-agent` 名称。Codex插件通过独立市场安装；包内辅助安装器提供项目级Skill或Subagent安装方式。两条安装路径都独立于原锤子。

## 先看这里

- [完整工作流程：各场景输入、输出及什么时候需要使用者参与](docs/workflow.md)
- [Codex插件安装、使用及验证边界](docs/codex-plugin.md)
- [详细使用与安装说明](package/README.md)
- [主Skill入口](package/skills/fusion-product-agent/SKILL.md)
- [领域构建与价值路径](package/skills/fusion-product-agent/references/domain-and-value.md)
- [非专家任务测评方法](package/skills/fusion-product-agent/references/nonexpert-evaluation.md)
- [来源与融合取舍](package/SOURCE-MAP.md)
- [验证结果与边界](package/VALIDATION.md)

## 下载完整能力包

- [融合产品锤 v0.2.0 ZIP](downloads/fusion-product-agent-v0.2.0.zip)
- [ZIP的SHA-256校验值](downloads/fusion-product-agent-v0.2.0.zip.sha256)

GitHub的 **Code → Download ZIP** 会下载整个仓库，包含文档和完整能力包。上面的能力包ZIP仅包含可独立使用的v0.2.0包。

## 作为Codex插件安装（推荐）

本仓库提供独立的Codex插件市场，插件标识为 `fusion-product-agent@fusion-product-agent`，能力包版本为 **0.2.0**。市场入口为 `.agents/plugins/marketplace.json`，指向原有完整 `package/`，能力文件与下载ZIP保持一致。

在本机终端执行：

```sh
codex plugin marketplace add https://github.com/junqicheng765-oss/fusion-product-agent.git
codex plugin add fusion-product-agent@fusion-product-agent
```

仓库为私有，安装和后续更新需要当前Git环境具备该仓库的读取权限。安装后新开Codex聊天，明确选择“融合产品锤”插件或输入：

> 使用 $fusion-product-agent。我可能不懂产品和业务领域，请先理解下面的想法与业务目标，主动研究并构建领域需求、系统边界及上下游交接，按本次范围推进。

插件与原来的 `tc-product-agent@tc-product-agent` 可以共存。每次任务明确选择需要使用的一套。当前聊天不保证热加载；界面列表若未刷新，退出并重新打开应用。

插件安装会由Codex添加相应市场和启用配置，不修改模型、Provider或原插件配置。无需再执行项目级安装器。

## 直接读取或项目级安装

下载或克隆后，在一个新项目聊天中，让Agent读取仓库中的 `package/skills/fusion-product-agent/SKILL.md`，再输入业务需求，例如：

> 请读取融合产品锤的SKILL.md。我可能不懂产品和业务领域，请围绕我的想法与业务目标交互，主动研究并构建领域需求、边界和上下游交接。本次做到开发前，并说明后续如何验证采用与收益。

若不使用上面的插件方式，可选择下面一种项目级安装方式。

### 方式一：项目级Skill

在仓库根目录运行，将目标路径换成一个新的试用项目目录：

```sh
python3 package/scripts/install.py --project /absolute/path/to/new-project --mode skill --dry-run
python3 package/scripts/install.py --project /absolute/path/to/new-project --mode skill
```

在该项目新开聊天，输入：

> 使用 $fusion-product-agent，按本次范围完成下面的产品任务。

### 方式二：项目级Subagent

```sh
python3 package/scripts/install.py --project /absolute/path/to/new-project --mode agent --dry-run
python3 package/scripts/install.py --project /absolute/path/to/new-project --mode agent
```

然后在该项目新开聊天，请主Agent调用项目内的 `fusion-product-agent`。

项目级Skill和Subagent两种方式互斥。安装器拒绝覆盖已有同名安装，保留既有项目配置，不修改全局设置。已经安装Codex插件时直接使用插件，避免额外建立同名入口。

## 核心工作方式

1. 持续理解并校准创意、业务目标与现场约束。
2. 主动研究任务所需领域知识，补出使用者没有想到的必需需求。
3. 构建对象、规则、状态、责任及上下游边界。
4. 用代表体验检验方案，再展开约定核心任务与适用状态。
5. 核对规则、设计、Demo与验收的一致性，形成可承接交付。
6. 为后续交付、上线、采用和收益验证构建具体任务与接收条件。

专业知识由锤子优先研究；组织事实从原始材料取证；经营取舍提供推荐并在有效委托内推进。Token、流程长度、篇幅和问答轮数仅作诊断，不作为核心能力得分。

## 检查能力包

```sh
python3 package/scripts/validate_package.py
python3 package/scripts/test_package.py
```

包内辅助脚本使用Python 3.9+标准库。浏览器、Figma、Computer Use及企业系统访问取决于宿主和实际授权，不随仓库提供账号或工具。

## 当前验证边界

已完成格式、引用、完整性及安装/引用脚本行为检查。v0.2.0尚未按新口径完成非专家真实业务试验、真实团队接手、生产接入或收益验证。规则已经写入，不代表专业任务、上线和变现已经被实证。

`package/`与2026-10-31构建的v0.2.0能力包逐文件一致；仓库根说明与工作流程文档位于包外，不改变能力包的完整性清单。

## 来源与使用范围

继承强子产品Agent、JQ Product Agent及Peter Matrix-AI的固定本地版本与方法；具体版本、原文保留范围及hash见包内来源说明。版本标识不表示各上游当前最新版本。本仓库作为私有工作副本保存，不宣称取得整个融合包的开放再分发许可，也不附加未经确认的开放许可。
