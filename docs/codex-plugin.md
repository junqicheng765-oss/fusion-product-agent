# Codex插件 v0.3.0

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

本版提供产品主入口与三项设计Skill；插件声明IconScout MCP，仍需实际账号及授权。安装不代表Figma、浏览器、Computer Use、生图服务或付费素材权限已具备。宿主发现、实际调用和设计效果分别验证。

更新后新建聊天。运行中的旧会话不保证切到新版本；菜单未刷新时重新打开Codex。与JQ正式版和设计试用版并存，不替换它们。

不使用插件时可按[项目级安装](../package/README.md)复制全部依赖，选择Skill或Subagent一种方式；已装插件无需重复建立同名入口。
