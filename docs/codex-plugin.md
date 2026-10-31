# 融合产品锤：Codex插件

插件及能力包版本：0.2.0。市场分发配置新增日期：2026-10-31。

## 安装

```sh
codex plugin marketplace add https://github.com/junqicheng765-oss/fusion-product-agent.git
codex plugin add fusion-product-agent@fusion-product-agent
```

仓库公开可见，可直接访问和安装。也可在Codex的插件界面添加同一仓库作为市场，再安装“融合产品锤”。使用仓库地址，不填写单个JSON的网页地址。

## 使用

新开Codex聊天，选择“融合产品锤”，或输入：

> 使用 $fusion-product-agent。我可能不懂产品和业务领域，请围绕我的想法和业务目标交互，主动研究并补齐领域需求、边界及上下游交接。本次任务范围是……

入口是 [主Skill](../package/skills/fusion-product-agent/SKILL.md)。流程见 [完整工作流程](workflow.md)。

旧聊天不保证热加载。插件列表没有刷新时，退出并重新打开应用。无需再安装包内项目级Skill或Subagent。插件的主Skill负责本次任务；是否委派其他Agent仍受宿主及用户授权约束。

## 分发结构

```text
.agents/plugins/marketplace.json   独立市场入口
package/.codex-plugin/plugin.json  原生Codex兼容插件元数据
package/skills/fusion-product-agent/
                                 主Skill、参考规则、完整知识和辅助脚本
```

市场以 `./package` 为插件来源，路径相对于仓库根目录解析。原有能力包未因注册市场而改写，ZIP和完整性清单继续适用。注册方式参考 [OpenAI官方插件打包文档](https://developers.openai.com/plugins/build/plugins)。

插件标识为 `fusion-product-agent@fusion-product-agent`；原JQ产品锤标识为 `tc-product-agent@tc-product-agent`。两个插件使用独立市场和缓存，可同时安装与启用。任务开始时明确选择需要使用的一套。

## 查询、更新和卸载

```sh
codex plugin list --marketplace fusion-product-agent --json
codex plugin marketplace upgrade fusion-product-agent
codex plugin add fusion-product-agent@fusion-product-agent
codex plugin remove fusion-product-agent@fusion-product-agent
```

更新前保留项目自己的成果与定制；插件缓存中的改动不应当作项目成果保存。卸载仅针对这个插件标识。不要删除原JQ插件、其他市场或整个Codex配置目录。

## 验证边界

包结构和辅助脚本检查：

```sh
python3 package/scripts/validate_package.py
python3 package/scripts/test_package.py
```

插件发现、installed/enabled状态、缓存内容一致性及原插件保护需在目标机器实际核对。它们与真实业务试验、生产接入、财税适用性及收益验证分别成立。

插件提供工作规则和知识文件。Figma、浏览器、Computer Use及企业系统账号、工具和权限仍取决于宿主环境。
