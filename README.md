# KitAgain · 垃圾佬复活站

**手里有什么设备 → 还能做什么 → 哪个方案有证据 → 动手前核对什么。**

[中文导航站](https://kitagain.com/zh/) · [English website](https://kitagain.com/) · [200 个项目来源](https://kitagain.com/zh/project-sources/) · [全站目录](https://kitagain.com/zh/directory/) · [关于与方法](https://kitagain.com/zh/about/) · [社区论坛](https://community.kitagain.com/) · [English README](README.en.md) · [研究报告](research/REPORT.zh-CN.md) · [提交项目或复现](https://github.com/liugod/awesome-hardware-revival/issues/new/choose)

从小爱音箱和 Nest Mini，到 Kindle、旧电脑、路由器、摄像头、停服机器人和缺驱动的打印机。这个目录把公开代码、作者案例与适配限制放在一起，帮助你判断下一步是否值得尝试。

**v1.19.0 · 统一目录精简 2026-10-24**：本次只调整展示，不删除或缩减目录数据。中英文目录顶部现在只有标题、搜索框，以及设备、最低星级、证据等级三个筛选项；默认始终按星级降序，评分说明由 `ⓘ` 进入[关于页面的评分区](https://kitagain.com/zh/about/#scoring)。全量 JSON/CSV、200 个项目来源和评分方法入口集中在[关于页面](https://kitagain.com/zh/about/)。站点仍有 **200 个按仓库 URL 去重的独立项目来源**、347 条设备与社区路线，以及[全站统一目录](https://kitagain.com/zh/directory/)中的 **547 条公开记录**和 451 个不同主来源 URL。

首页只保留一个标题、一个设备搜索框、一行副标题和热门设备分类；统一目录也删去说明段、提示框、顶部下载链接、条目类型和排序控件。列表卡片只显示名称、可以变成什么、星级或待评分标签，以及独立证据等级。完整适配条件、风险、来源和其他字段仍保留在详情页及 JSON/CSV 下载中。

五项“复活价值”维度仍为：可行性/易上手 25%、低成本 15%、文档与社区 20%、实用价值 20%、低刷坏/安全风险 20%。没有可核验来源的维度保存为 `null`，不再用中性 3 分补位；至少 3 个维度有证据时，才把这些维度的原权重按比例重新归一并计算总分，再四舍五入到最近 0.5 星。当前 **95 / 547 条有星级，452 条显示“待评分 / Not yet rated”**；默认排序为已评分条目按星级降序、待评分条目随后。本版已评分分布为：1 星 1、1.5 星 3、2 星 2、2.5 星 6、3 星 35、3.5 星 8、4 星 35、4.5 星 5、5 星 0。

首批重新研究并评分 **49 条** Kindle/电子书、路由器、旧迷你电脑/NAS 和智能音箱路线，逐维依据与 156 个去重来源 URL 记录在 [`scoring-evidence.json`](data/scoring-evidence.json)。E0–E3 仍是独立证据标签，不参与评分或封顶。147 个仓库发现候选全部保持 E0 和 `needs_review: true` / “待验证”；本批评分取证不会自动升级兼容性证据等级。

设备详情页仍保留独立的硬件名称或型号标签，点击标签即可按同一设备搜索；标签明确区分准确型号、设备家族和硬件平台，未把推测型号当成事实。31 个正式项目已有各自不同的图片：27 张来自项目仓库、作者页面或项目官网的设备实拍、硬件图与界面截图，4 张是在缺少合格原图时制作并明确标注的项目专属示意插图。

详情页用标题和短要点先回答：能变成什么、设备是否对得上、什么情况应该停手、最坏会怎样，以及原始链接能帮什么。资料等级、评分方法与贡献流程由一个小链接统一指向关于页面。

图片来源与说明公开保存在 [`project-images.json`](data/project-images.json)。项目仓库许可证不自动视为图片授权；上游图片保留原页面和文件地址，示意插图明确写明“不是实机照片”。

| AI 关系 | 条目数 | 如何理解 |
| --- | ---: | --- |
| AI 功能改造 | 10 | 增加语音、对话或视觉分析等能力，计算常在外部 |
| AI 辅助开发/配置 | 2 | 有作者过程或 AI 配置文档；二者仍分别说明 |
| AI 周边用途 | 1 | 例如显示 AI 工具用量，不代表设备运行模型 |
| 传统复活基础设施 | 40 | 系统、固件、本地服务和显示工具，不随意贴 AI 标签 |

正式目录证据分布：**E1 50 条、E2 3 条、E3 0 条**；项目发现层 **E0 147 条**；设备图谱另有 **E1 30 条、E0 317 条**。本目录没有实机测试；未取得成本证据时保持 `null`，不以 0 或 3 冒充事实。深审字段见 [JSON](data/catalog.json) / [CSV](data/catalog.csv)，项目发现层见 [JSON](data/project-leads.json) / [CSV](data/project-leads.csv)，547 条统一评分与 URL 见 [JSON](data/directory.json) / [CSV](data/directory.csv)，逐维评分来源见[评分证据台账](data/scoring-evidence.json)。

## 从设备开始

| 设备 | 条目 | 可先看的项目 |
| --- | ---: | --- |
| [音箱与语音](https://kitagain.com/zh/directory/?category=speaker) | 7 | XiaoGPT、Open-XiaoAI、Onju |
| [手机与平板](https://kitagain.com/zh/directory/?category=mobile) | 5 | LineageOS、Termux、Deskreen |
| [电脑与瘦客户机](https://kitagain.com/zh/directory/?category=computer) | 4 | OCLP、MrChromebox、HAOS、DietPi |
| [路由与 NAS](https://kitagain.com/zh/directory/?category=network) | 3 | OpenWrt、FreshTomato、OpenMediaVault |
| [电视与盒子](https://kitagain.com/zh/directory/?category=tv) | 5 | LibreELEC、CoreELEC、webOS Homebrew |
| [电子书与墨水屏](https://kitagain.com/zh/directory/?category=ereader) | 8 | KOReader、Kindle WHOOP、Kindle HA |
| [机器人](https://kitagain.com/zh/directory/?category=robot) | 2 | Valetudo、wire-pod |
| [智能家居](https://kitagain.com/zh/directory/?category=smarthome) | 4 | OpenLumi、Tasmota、OpenBeken、ESPHome |
| [摄像头](https://kitagain.com/zh/directory/?category=camera) | 4 | OpenIPC、Dafang、Thingino、Frigate |
| [播放器与音响](https://kitagain.com/zh/directory/?category=audio) | 4 | Rockbox、Lyrion、Squeezelite、Retro iPod |
| [手表与可穿戴](https://kitagain.com/zh/directory/?category=wearable) | 3 | Gadgetbridge、InfiniTime、AsteroidOS |
| [游戏设备](https://kitagain.com/zh/directory/?category=gaming) | 3 | Batocera、Lakka、Bazzite |
| [打印机与外设](https://kitagain.com/zh/directory/?category=peripheral) | 1 | HP Laser 1008a macOS driver |

也可在[全站目录](https://kitagain.com/zh/directory/)中搜索设备、型号、项目或来源，并按设备类别、[作者实机证据](https://kitagain.com/zh/directory/?evidence=E2)或[最低 4 星](https://kitagain.com/zh/directory/?score=4)筛选。目录固定按星级降序排列，筛选条件保存在网址中。

## 三个代表案例

- **[Onju Voice](https://github.com/justLV/onju-voice)**：复用 Nest Mini 外壳和声学部件，换入 ESP32-S3 主板。原版已停维护；[作者 X 原帖](https://x.com/justLV/status/1681377298308820992) 及后续解释明确是换板，并非纯软件越狱。
- **[HP Laser macOS 驱动](https://github.com/Kuberwastaken/hp-laser-1008a-macos)**：作者公开 Claude 辅助开发过程；[原始帖子](https://x.com/kuberwastaken/status/2089377982536388964)。测试范围是指定 HP Laser 系列、Apple Silicon、macOS 26 与 USB，不推广到 Wi-Fi。
- **[Kindle for WHOOP](https://github.com/kaibuildsai/kindle-for-whoop)**：作者记录 PW2、固件 5.10.3 的显示及唤醒链路，并提供 AI 辅助设置文档；不等于在 Kindle 本地运行 AI，也没有本目录验证的长期续航。

## 证据与未知项

- **E1**：本轮已读源码仓库的部署、适配资料；不代表本目录运行成功。
- **E2**：另有作者具体实机陈述或演示说明；仍是作者证据。
- **E3**：另一个独立使用者的可追溯复现记录已核验；初版没有。
- **E0**：包括 147 个仓库级项目发现候选和 317 条设备/社区线索。前者只核到 GitHub API 与 README 入口；后者中 300 条设备级入口放在[设备图谱](data/device-atlas.json)，其中另有 30 条已经通过[型号资料核查表](data/device-reviews.json)升级为 E1。早期线索放在[社区线索数据](data/watchlist.json)与[扩展研究数据](data/watchlist-expansion.json)，用户判断字段和带说明的链接统一生成到[线索判断表](data/watchlist-details.json)。二手报道或范围不符的内容仍留在[排除区](data/candidates.json)。

逐条记录型号、固件、地区、拆机/焊接/云 API、许可证、归档与迁移、成本未知项、数据损失与恢复。安装应用、替换固件、云服务替代、换板和维修故障分开描述。未归档不表示当前兼容；HTTP 能打开不表示实质验证通过；来源 hash 不表示硬件测试通过。

正式目录读到 4 条 X 原始帖子，涉及 2 个案例家族；设备图谱另收录 1 条可读取并有项目仓库交叉验证的 X 线索。未验证视频画面，也没有把转载、搜索摘要、热度或 star 数当成成功证据。覆盖空白与后续内容栏目见 [完整报告](research/REPORT.zh-CN.md)。

## 数据与构建

硬件名称与型号标签单独维护在 `data/hardware-tags.json`，并在构建时检查 53 个正式项目和 347 条线索是否都有可搜索标签。

主目录为 `data/catalog.json`，147 个 E0 仓库来源位于 `data/project-leads.json`，300 条设备级入口位于 `data/device-atlas.json`，其中 30 条型号级核查位于 `data/device-reviews.json`；`data/scoring-evidence.json` 保存首批 49 条逐维评分取证，`data/directory.json` / CSV 汇总全部 547 条记录的 nullable 总星级、加权平均、五项原始分、有效权重、分项依据与来源、独立证据等级及待验证状态。编辑输入为 `data/seeds.json`、`data/review.json`，重点分析为 `data/deep-dives.json`。英文翻译位于 `data/i18n/`，三个双语专题位于 `data/guides.json`，三篇实用指南位于 `data/articles.json`，公开设备线索由设备图谱、`data/watchlist.json` 和 `data/watchlist-expansion.json` 合并生成。已核实作者社交账号单独维护在 `data/author-socials.json`；构建同时生成覆盖 53 个正式条目的 [`author-identity-coverage.json`](docs/data/author-identity-coverage.json)，仓库所有者入口与个人作者账号分开标注，不把仓库归属写成唯一作者证明。站点有 1124 个规范公开 URL/语言页面、1 个英文根路径首页和 54 个保留的旧 URL，共 1179 个静态 HTML 页面。无后端、无账号、无第三方分析脚本；禁用 JavaScript 仍可阅读完整目录。

英文 [JSON](docs/data/catalog.en.json) / [CSV](docs/data/catalog.en.csv) 可下载。[独立社区论坛](https://community.kitagain.com/)已上线基础服务；其中文界面、版块与管理流程仍在完善，目录纠错继续使用 GitHub Issues。

```sh
python -m pip install -r requirements-dev.txt
python scripts/build.py
python scripts/validate.py
python -m http.server 4185 --bind 127.0.0.1 --directory docs
```

打开 `http://127.0.0.1:4185/`，根路径显示英文搜索首页，可切换中文；完整英文目录位于 `/en/directory/`。GitHub Pages 使用 `main` 分支的 `/docs`。域名、仓库地址、社区地址与产品版本统一配置在 `site.config.json`；改域名后重建 canonical 和 sitemap，并同步 README 的公开链接。详见 [部署与翻译维护](research/BILINGUAL-MAINTENANCE.md)。

`scripts/collect.py` 需要已登录的 GitHub CLI，仅做只读采集，将完整上游快照放在仓库外的同级 `hardware-revival-work/upstream`。`scripts/curate.py` 使用该缓存和编辑输入重新编译 JSON/CSV。**重新采集不是完成内容审核**：先阅读变更、核对来源并更新编辑输入，再运行编译。站点构建与验证不需要缓存或任何账号。

## 贡献、更新与许可

欢迎提交失败复现和恢复路径，而不仅是成功截图。见 [贡献说明](CONTRIBUTING.md)、[更新记录](CHANGELOG.md) 与 [复用研究流程](skills/hardware-revival-research/SKILL.md)。当前不运行定时任务。

原创研究文字与目录编排使用 **CC BY 4.0**，构建代码与原创站点代码使用 **MIT**；详见 [LICENSE](LICENSE) 和 [LICENSE-CODE](LICENSE-CODE)。第三方代码、固件、图片、模型与商标仍属各自权利人。本仓库只提供来源链接与原创摘要，不重新分发第三方固件、完整教程或 X 媒体。项目收录不构成上游背书。
