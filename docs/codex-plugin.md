# Codex插件 v0.3.6-rc.7（候选）

GitHub主分支提供rc.7整合候选，以下远端安装步骤获取该候选；最新正式Release仍为v0.3.4。维护者本机已通过本地市场安装并启用rc.7。

融合锤子独立GitHub仓库提供Codex市场，入口`.agents/plugins/marketplace.json`指向`package/`。插件标识`fusion-product-agent@fusion-product-agent`。

```sh
codex plugin marketplace add https://github.com/junqicheng765-oss/fusion-product-agent.git
codex plugin add fusion-product-agent@fusion-product-agent
```

已安装时刷新指定市场再安装：

```sh
codex plugin marketplace upgrade fusion-product-agent
codex plugin add fusion-product-agent@fusion-product-agent
```

若当前同名市场指向本地候选目录，需要切回GitHub来源时，先移除 `fusion-product-agent` 市场，再执行上方 `marketplace add` 和 `plugin add`；市场来源为本地时，`marketplace upgrade` 不会获取GitHub代码。

本版提供产品主入口、三项设计Skill及一项Figma执行Skill；插件声明IconScout MCP，仍需实际账号及授权。安装不代表Figma、浏览器、Computer Use、生图服务或付费素材权限已具备。宿主发现、实际调用和设计效果分别验证。

更新后新建聊天。运行中的旧会话不保证切到新版本；菜单未刷新时重新打开Codex。与JQ正式版和设计试用版并存，不替换它们。

不使用插件时可按[项目级安装](../package/README.md)复制全部依赖，选择Skill或Subagent一种方式；已装插件无需重复建立同名入口。
