# 融合产品锤 v0.2.0

方向调整试用版，构建日期2026-10-31。基于0.1.0融合包及本次用户转述的老板输入更新运行规则；继承来源未重新查询上游版本。融合强子产品Agent 2026.09.30.2、俊琦JQ Product Agent 1.1.5和Peter Matrix-AI v0.26的已核对方法。版本标识对应本次本地来源，不声称是各上游最新发布。

**默认没有专家补位，由锤子主动研究并构建领域需求、边界与上下游交接，与人持续校准创意和业务目标。** 一套主线、一处规则来源、按任务风险加载深度；不要求原三套同时安装。

## 本次方向调整

领域构建成为常规迭代/完整设计的必需工作，按任务风险确定深度。产品能力模型提供产品判断方法，业务领域知识需另行研究与验证。人的“不知道”不会被当作研究工作的终点。

以从想法到变现为服务目标，当前包仍是产品锤：主动构建后续研发、上线、采用和收益验证所需输入，在用户授权范围内衔接工作；生成文件不代表整条链路已跑通。

评测优先看目标理解、领域需求补齐、边界构建、上下游承接及真实任务/价值证据；Token、篇幅、流程和轮数只作诊断。详见 [领域方法](skills/fusion-product-agent/references/domain-and-value.md) 与 [新测评口径](skills/fusion-product-agent/references/nonexpert-evaluation.md)。本轮仅验证包格式、引用、完整性和继承的安装脚本行为，尚未完成新口径业务实测。

## 这版有什么

- 咨询/清单、局部迭代、完整产品设计与复杂任务的统一路由。
- 渐进澄清、已有决定与委托复用；内部检查不变成逐步人工放行。
- 业务正文优先，历史与确认可回查；设计/研发/QA共用同一规则来源。
- 设计准备前置，代表链路→模块/状态→实际文案、交互和视觉检查。
- 对象、权限、资金、异步、结果未知、恢复与关键变更方法。
- 七类48项产品能力原文按需参考；正式基线/交接筛适用性，局部任务只查受影响项。
- 设计、Demo、规则与验收的语义/版本对应；可选机器引用检查。
- 项目级Skill或Subagent两种安装方式，互斥选择；没有全局安装副作用。

运行规则是融合后重写的执行合同，未把三套入口或审批串起来。具体取舍见 [融合来源与取舍](SOURCE-MAP.md)。

## 从这里使用

无需安装即可在一个新项目聊天中提供本包入口的绝对路径，请Agent读取：

> 请读取这个包的 `skills/fusion-product-agent/SKILL.md`，用融合产品锤处理下面的需求。我可能不懂产品和业务领域，请围绕我的想法与目标交互，主动研究并构建领域需求、边界及上下游交接。本次做到开发前，说明后续如何验证采用与收益。

这种方式验证的是读取并使用包内规则，不代表已注册为宿主Skill。要在项目中按名称发现，使用下述安装方式。

### 方式一：项目级Skill

在本包目录运行，替换为你真实项目的绝对路径：

```sh
python3 scripts/install.py --project /absolute/path/to/project --mode skill --dry-run
python3 scripts/install.py --project /absolute/path/to/project --mode skill
```

生成项目内 `.agents/skills/fusion-product-agent/`。在该项目新开聊天，输入：

> 使用 $fusion-product-agent，先理解我的需求，按本次范围完成产品方案与交付。

### 方式二：仅项目级Subagent

```sh
python3 scripts/install.py --project /absolute/path/to/project --mode agent --dry-run
python3 scripts/install.py --project /absolute/path/to/project --mode agent
```

生成 `.codex/agents/fusion-product-agent.toml` 和 `.codex/resources/fusion-product-agent/`，不注册项目Skill。项目无config时创建最小Agent启用配置；已有config完整保留，若其禁用自定义Agent，需由项目使用者按宿主要求启用。新开该项目聊天后输入：

> 请调用本项目的 fusion-product-agent Subagent，完成下面的产品任务。由你统一向我提问和汇总。

首次安装后需新聊天加载；文件存在、宿主发现和实际运行分别验证。移动项目后重装到新位置以更新Subagent规则绝对路径；Skill引用采用相对路径。安装器默认拒绝覆盖旧安装，不合并现有AGENTS.md、不改变模型/Provider、不触及全局配置。

## 环境与边界

主Skill是Markdown规则，可由具备文件读取能力的Agent使用。附带脚本使用Python 3.9+标准库，不需pip安装。Figma、浏览器和Computer Use依赖宿主实际提供与授权，是可选适配，不随包附带账号或工具。

包内 `.codex-plugin/plugin.json` 提供插件元数据；本地项目Skill/Subagent是本版实际试装路径。本版未发布市场、不声称市场导入已通过。

## 检查与试用

```sh
python3 scripts/validate_package.py
python3 scripts/test_package.py
```

第一个检查文件清单、相对引用和入口，第二个在临时目录验证两种安装及覆盖保护、路径边界和交付引用失败场景。它们不证明产品判断效果。真实试用结果与范围见 [验证说明](VALIDATION.md)。

多载体交接需要机械校对时，可按 [清单示例](skills/fusion-product-agent/assets/delivery.example.json) 记录实际引用，用 `skills/fusion-product-agent/scripts/check_delivery.py` 检查。它只查声明过的内容；建议在规则记录 `source_sha256`、产物记录 `sha256` 绑定实际内容，不改哈希让旧结果通过。自动检查不审查业务语义或批准真实性。

## 卸载与升级

安装记录在项目 `.codex/fusion-product-agent-install.json`。卸载前检查是否有项目新增内容；只删除记录对应的Skill目录或Agent预设/资源及该记录。安装器创建的config只有在确认仍是原始最小配置且项目不再需要时才可移除，不整体删除`.codex`。

升级时先保留旧版与项目产物，核对记录和本地改动；在新隔离目录试装新包，不用强制覆盖来丢弃项目定制。本包版本独立于各来源版本。

## 来源与使用范围

本版供用户本地融合试用。来源、复制范围及校验见 [SOURCE-MAP.md](SOURCE-MAP.md) 和 [provenance.json](provenance.json)。本地来源包未提供可据此授予整个融合包公开再分发的统一许可，因此本版不添加开放许可、不宣称获得上游官方背书；公开再分发前应核对来源权利。未包含业务样本、历史会话、凭据或来源项目产物。
