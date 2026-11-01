# 真实摄影素材库（Real Image Library）

本文件是素材获取模块，不是新的设计方法。不新开 `V8`。视觉判断仍走 `V5` / `V7`；这里只回答：**真实世界的照片从哪来、怎么搜、怎么合法用到稿上。**

四个条件同时满足才算接入：真实摄影、免费可用、Agent 能自动搜、能拿到适合尺寸的文件并写入设计。只让设计师自己打开网站逛、手动下载的图库，不接入。

**图片免费 ≠ API 可无限调用。** 有的图免费，API 要申请、有额度或必须署名。没有 key 的库自动跳过，不编造成功、不抓网页当 API。

IconScout 继续只管图标、3D、插画、Lottie。人物头像仍走 `V5` 第 7 条（文化匹配 + 同套系），不拿图库里的随机真人脸当用户头像。

## IM0 何时用真实图，何时才生图

**触发问题**：这一处画面需要真实世界，还是虚构视觉？  
**最低输入**：用途（Hero / 卡片 / 背景 / 地点）、主题、构图、比例、当前 UI 冷暖。  
**跳过**：纯图标、3D 道具、矢量插画、Lottie、用户头像圈。

硬规则：

1. **真实场景、人物生活、建筑、自然风景、具体地点** → 先跑本模块。
2. **搜不到合适图，或画面本身必须虚构**（不存在的产品、超现实合成、统一光影的整幅插画）→ 再走 `V7` AI 生图。
3. 禁止：没搜过真实图库，就把「写实摄影 / 氛围背景」直接丢给生图模型。这是 AI 塑料感的主要来源之一。

```
需要画面
  ├─ 图标 / 3D / 插画 / Lottie ──► IconScout（V5）
  ├─ 用户头像圈 ──► IconScout → 文化门 → 不匹配再 AI 成套
  ├─ 真实世界摄影 ──► 本模块 search → 选图 → get → 写入稿
  └─ 虚构或无匹配 ──► V7 AI 生图
```

## IM1 统一 Image Search Adapter

不给每个图库写一套 Skill。只调一个脚本，下面接多个官方 REST API。不依赖社区 MCP。

```
python3 scripts/real_image.py search "桂林山水首页" --role hero --tone cool --json /tmp/photos.json
python3 scripts/real_image.py get wikimedia:Guilin_mifan.jpg --from-json /tmp/photos.json --out ./assets/real-images
```

`--role`：`hero`（横构图、大留白、≥1600） / `card`（主体清楚、≥800） / `portrait` / `background` / `place`  
`--tone`：跟当前 UI 冷暖走，`warm` / `cool` / `neutral` / `dark` / `green`

脚本会把中文主题扩成英文检索词，例如「中国旅游首页」→ `China travel landscape cinematic wide shot no text no watermark`。Pixabay 有 key 时中文可走 `lang=zh`。具体地点保留原名给 Wikimedia。

返回统一结构：`id, source, title, creator, license, license_url, page_url, preview_url, download_url, width, height, attribution`。`get` 下载**适合尺寸的版本**（不是 8MB 原图），并写同名 `.json` 和 `ATTRIBUTION.md`。

选图标准（脚本先打分，Agent 再用 `Read` 看预览）：

| 条件 | Hero | 卡片 | 地点 |
| :--- | :--- | :--- | :--- |
| 构图 | 横图、一侧可叠字 | 主体居中清晰 | 能认出那个地方 |
| 分辨率 | 宽 ≥ 1600 | 宽 ≥ 800 | 宽 ≥ 1200 |
| 授权 | 可商用优先；NC / ND 降权 | 同左 | 记录具体许可证 |
| 色调 | 与 `--tone` / 品牌冷暖同频 | 同左 | 真实光即可 |

禁止把带字、水印、明显摆拍网红脸、或和品牌冷暖打架的图硬塞进 Hero。

## IM2 五个官方来源（v1 优先级）

| 图库 | API | 适合 | v1 |
| :--- | :--- | :--- | :--- |
| **Pixabay** | 免费，默认 100 次/分钟；要 `PIXABAY_API_KEY` | 摄影、背景、插画、视频 | 主库 |
| **Openverse** | 可匿名；有速率限制 | 开放授权摄影、文化、历史 | 主库 |
| **Unsplash** | 已预置 Access Key，开箱即用；环境变量 `UNSPLASH_ACCESS_KEY` 可覆盖。Demo 50 次/小时，生产额度要审批 | 高质量摄影、官网 Hero、生活方式 | 高质量补充 |
| **Pexels** | 200 次/小时、2 万次/月；**目前暂停发新 Key**；`PEXELS_API_KEY` | 人物、商业、产品场景、视频 | 有 key 才启用 |
| **Wikimedia Commons** | 开放、无需 key | 真实地点、地标、历史与文化 | 地点补充 |

检索顺序：

- 一般主题：Pixabay → Openverse → Unsplash → Pexels → Wikimedia
- 具体地点（桂林、故宫、外滩、`--role place`）：Wikimedia 提到最前，再走其余库

Unsplash Access Key 已预置在 `scripts/real_image.py`（和 IconScout Client-ID 一样，给所有使用本 Skill 的人直接调）。环境变量 `UNSPLASH_ACCESS_KEY` 可覆盖。Pixabay / Pexels 仍只读环境变量，没有就跳过。某个库超时或失败记入 `errors`，不整段停工。Openverse 偶发超时是预期，自动落到 Unsplash / Wikimedia。

## IM3 授权与使用边界

每张用上的图必须能指出：来源、作者、许可证、作品页。Openverse 尤其要分清 CC 变体：

- 可默认商用：CC0、PDM、CC BY（署名）、Pixabay License、Unsplash License、Pexels License
- 降权或不用：CC BY-NC、CC BY-ND，以及禁止改作 / 禁止商用的条款
- Wikimedia：按该文件自己的 `LicenseShortName` 写进 sidecar，不假设全是公有领域

**Unsplash 专规**（官方要求，不是建议）：

- 只用 API 返回的 `urls.*`，不要另存成自己的永久图库再对外分发
- 选定使用时必须打 `links.download_location`（脚本 `get` 会做）
- 署名带摄影师和 Unsplash，链接加他们要求的 utm
- Demo key 有额度；生产级使用要按 Unsplash 规则申请

**Pixabay**：决定留用的图要下载到项目本地，不长期热链他们的 CDN。

用户方才有的照片（真实员工、真实客户、未授权实拍）仍按 `SKILL.md` 问人规则向用户要，不从图库找一张「长得像」的代替。

## IM4 写入设计

1. `search` 后用 `Read` 看 2–4 张预览，挑一张符合角色、色调和真实内容要求的。
2. `get` 到项目 `assets/real-images/`（或当前稿的资源目录）。
3. 写入 `V5` 资产 manifest：来源、作者、许可证、本地路径、用途、裁切。
4. Hero 叠字时裁切要给文字留安全区，不要切掉主体脸或地标轮廓。
5. 可复用且用户确认后，按 `AM` 入库；Unsplash 图只记链接与归因，不把原图打包装进 Skill 公共库。
6. 作者和许可证只写在 sidecar 和 manifest。消费界面上不出现 “Photo:”“CC BY” 这类授权句。许可证要求署名时，署名放在关于页或图片信息页，不放在首屏。

**产出**：本地图片文件 + 同名授权 JSON + 资产 manifest 行。  
**完成证据**：稿上每张真实摄影都能指到作者、许可证和文件；没有「来源不详的网图」；该用真实图却直接生图的，本项不过。  
**不得替代**：版权授权；用户方实拍；IconScout 的图标/3D/插画职责。
