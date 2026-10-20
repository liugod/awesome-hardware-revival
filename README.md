# 老硬件复活指南 · Hardware Revival Field Guide

**手里有什么设备 → 还能做什么 → 哪个方案有证据 → 动手前核对什么。**

[打开可搜索导航站](https://liugod.github.io/awesome-hardware-revival/) · [English](README.en.md) · [研究报告](research/REPORT.zh-CN.md) · [12 篇案例分析](research/DEEP_DIVES.zh-CN.md) · [提交项目或复现](https://github.com/liugod/awesome-hardware-revival/issues/new/choose)

从小爱音箱和 Nest Mini，到 Kindle、旧电脑、路由器、摄像头、停服机器人和缺驱动的打印机。这个目录把公开代码、作者案例与适配限制放在一起，帮助你判断下一步是否值得尝试。

**v1.0.0 · 核查 2026-10-20**：53 条项目/平台/工具，13 类设备，51 个项目家族。不是“53 台亲测成功设备”。

| AI 关系 | 条目数 | 如何理解 |
| --- | ---: | --- |
| AI 功能改造 | 10 | 增加语音、对话或视觉分析等能力，计算常在外部 |
| AI 辅助开发/配置 | 2 | 有作者过程或 AI 配置文档；二者仍分别说明 |
| AI 周边用途 | 1 | 例如显示 AI 工具用量，不代表设备运行模型 |
| 传统复活基础设施 | 40 | 系统、固件、本地服务和显示工具，不随意贴 AI 标签 |

证据分布：**E1 50 条、E2 3 条、E3 0 条**。本目录没有实机测试；所有金额未知，不以 0 冒充免费。完整字段见 [JSON](data/catalog.json) / [CSV（UTF-8 BOM）](data/catalog.csv)。

## 从设备开始

| 设备 | 条目 | 可先看的项目 |
| --- | ---: | --- |
| [音箱与语音](https://liugod.github.io/awesome-hardware-revival/?category=speaker#catalog) | 7 | XiaoGPT、Open-XiaoAI、Onju |
| [手机与平板](https://liugod.github.io/awesome-hardware-revival/?category=mobile#catalog) | 5 | LineageOS、Termux、Deskreen |
| [电脑与瘦客户机](https://liugod.github.io/awesome-hardware-revival/?category=computer#catalog) | 4 | OCLP、MrChromebox、HAOS、DietPi |
| [路由与 NAS](https://liugod.github.io/awesome-hardware-revival/?category=network#catalog) | 3 | OpenWrt、FreshTomato、OpenMediaVault |
| [电视与盒子](https://liugod.github.io/awesome-hardware-revival/?category=tv#catalog) | 5 | LibreELEC、CoreELEC、webOS Homebrew |
| [电子书与墨水屏](https://liugod.github.io/awesome-hardware-revival/?category=ereader#catalog) | 8 | KOReader、Kindle WHOOP、Kindle HA |
| [机器人](https://liugod.github.io/awesome-hardware-revival/?category=robot#catalog) | 2 | Valetudo、wire-pod |
| [智能家居](https://liugod.github.io/awesome-hardware-revival/?category=smarthome#catalog) | 4 | OpenLumi、Tasmota、OpenBeken、ESPHome |
| [摄像头](https://liugod.github.io/awesome-hardware-revival/?category=camera#catalog) | 4 | OpenIPC、Dafang、Thingino、Frigate |
| [播放器与音响](https://liugod.github.io/awesome-hardware-revival/?category=audio#catalog) | 4 | Rockbox、Lyrion、Squeezelite、Retro iPod |
| [手表与可穿戴](https://liugod.github.io/awesome-hardware-revival/?category=wearable#catalog) | 3 | Gadgetbridge、InfiniTime、AsteroidOS |
| [游戏设备](https://liugod.github.io/awesome-hardware-revival/?category=gaming#catalog) | 3 | Batocera、Lakka、Bazzite |
| [打印机与外设](https://liugod.github.io/awesome-hardware-revival/?category=peripheral#catalog) | 1 | HP Laser 1008a macOS driver |

也可按 [语音助手](https://liugod.github.io/awesome-hardware-revival/?use=%E8%AF%AD%E9%9F%B3%E5%8A%A9%E6%89%8B#catalog)、[信息屏](https://liugod.github.io/awesome-hardware-revival/?use=%E4%BF%A1%E6%81%AF%E5%B1%8F#catalog)、[入门难度](https://liugod.github.io/awesome-hardware-revival/?difficulty=easy#catalog) 或 [作者实机证据](https://liugod.github.io/awesome-hardware-revival/?evidence=E2#catalog) 查找。筛选条件保存在网址中，可直接分享。

## 三个代表案例

- **[Onju Voice](https://github.com/justLV/onju-voice)**：复用 Nest Mini 外壳和声学部件，换入 ESP32-S3 主板。原版已停维护；[作者 X 原帖](https://x.com/justLV/status/1681377298308820992) 及后续解释明确是换板，并非纯软件越狱。
- **[HP Laser macOS 驱动](https://github.com/Kuberwastaken/hp-laser-1008a-macos)**：作者公开 Claude 辅助开发过程；[原始帖子](https://x.com/kuberwastaken/status/2089377982536388964)。测试范围是指定 HP Laser 系列、Apple Silicon、macOS 26 与 USB，不推广到 Wi-Fi。
- **[Kindle for WHOOP](https://github.com/kaibuildsai/kindle-for-whoop)**：作者记录 PW2、固件 5.10.3 的显示及唤醒链路，并提供 AI 辅助设置文档；不等于在 Kindle 本地运行 AI，也没有本目录验证的长期续航。

## 证据与未知项

- **E1**：本轮已读源码仓库的部署、适配资料；不代表本目录运行成功。
- **E2**：另有作者具体实机陈述或演示说明；仍是作者证据。
- **E3**：另一个独立使用者的可追溯复现记录已核验；初版没有。
- **E0**：线索或材料未完成，放在 [候选/排除区](data/candidates.json)，不计入 53 条。

逐条记录型号、固件、地区、拆机/焊接/云 API、许可证、归档与迁移、成本未知项、数据损失与恢复。安装应用、替换固件、云服务替代、换板和维修故障分开描述。未归档不表示当前兼容；HTTP 能打开不表示实质验证通过；来源 hash 不表示硬件测试通过。

X 本轮读到 4 条原始帖子，涉及 2 个案例家族；未验证视频画面。没有把转载、热度或 star 数当成成功证据。覆盖空白与后续内容栏目见 [完整报告](research/REPORT.zh-CN.md)。

## 数据与构建

主目录为 `data/catalog.json`，编辑输入为 `data/seeds.json`、`data/review.json`，重点分析为 `data/deep-dives.json`。站点 55 个静态 HTML 页面，无后端、无账号、无第三方分析脚本。禁用 JavaScript 仍可阅读完整目录。

```sh
python -m pip install -r requirements-dev.txt
python scripts/build.py
python scripts/validate.py
python -m http.server 4185 --bind 127.0.0.1 --directory docs
```

打开 `http://127.0.0.1:4185/`。GitHub Pages 使用 `main` 分支的 `/docs`。改仓库地址时同步修改 `scripts/build.py` 中的 BASE/REPO 与本 README；重建 canonical 和 sitemap。

`scripts/collect.py` 需要已登录的 GitHub CLI，仅做只读采集，将完整上游快照放在仓库外的同级 `hardware-revival-work/upstream`。`scripts/curate.py` 使用该缓存和编辑输入重新编译 JSON/CSV。**重新采集不是完成内容审核**：先阅读变更、核对来源并更新编辑输入，再运行编译。站点构建与验证不需要缓存或任何账号。

## 贡献、更新与许可

欢迎提交失败复现和恢复路径，而不仅是成功截图。见 [贡献说明](CONTRIBUTING.md)、[更新记录](CHANGELOG.md) 与 [复用研究流程](skills/hardware-revival-research/SKILL.md)。当前不运行定时任务。

原创研究文字与目录编排使用 **CC BY 4.0**，构建代码与原创站点代码使用 **MIT**；详见 [LICENSE](LICENSE) 和 [LICENSE-CODE](LICENSE-CODE)。第三方代码、固件、图片、模型与商标仍属各自权利人。本仓库只提供来源链接与原创摘要，不重新分发第三方固件、完整教程或 X 媒体。项目收录不构成上游背书。
