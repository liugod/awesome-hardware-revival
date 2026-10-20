# 重点案例分析

这些是基于公开文档的分析与建议验收步骤；不是本目录已执行的硬件测试。适用条件以条目来源为准。

## XiaoGPT

**小爱音箱接入大模型，需要刷机吗**

原有音箱的对话能力由厂商服务决定，用户希望保留熟悉的拾音和播放入口。

在外部主机运行桥接服务，把语音请求转给配置的大模型，再由音箱播放结果。

这是一条改造成本主要落在常开主机、接口配置和排障上的路径。README 的 LX06 示例证明有具体配置入口，但并不构成所有小爱型号和账号地区都兼容的证明。小米侧接口变化可能让桥接失效，选择前应先验证账号、型号参数与单次问答，再考虑长期运行。

- 型号：小爱音箱；README 示例 LX06，其他型号须核对 hardware 参数
- 固件：待按具体型号核实
- 方法与难度：服务桥接 / 进阶
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 需要小米服务；模型云服务可选
- 额外成本：待核价；常开主机、按需付费的模型/TTS 服务
- 证据：E1 — README 给出 LX06 启动、配置文件和多模型后端方法，并附作者演示媒体链接；本次未播放媒体。
- 数据风险：possible；设备失效风险：workflow-dependent（编辑按路径提示，未实测）
- 恢复：停止桥接进程可停止转发；本条路径不替换音箱固件。
- 适合：已有对应音箱、能运行 Python 服务，并接受小米云依赖的使用者。
- 不适合：要求完全离线、无需常开主机，或希望修复硬件故障的使用者。

建议验收（未执行）：

- 记录硬件型号和账号地区，完成一次端到端问答
- 断开模型后端，确认能识别失败而不是持续等待
- 停止桥接，检查原有音箱功能

[教程](https://github.com/yihong0618/xiaogpt/blob/main/README.md) · [适配范围](https://github.com/yihong0618/xiaogpt/blob/main/README.md) · [完整条目](https://kitagain.com/projects/xiaogpt.html)

## Open-XiaoAI

**小爱 LX06 OH2P 固件改造有什么区别**

希望接管小爱音箱的音频链路，而不只通过云端问答记录实现桥接。

在特定音箱上使用补丁固件及客户端，把音频送到外部服务处理。

项目文档明确区分 LX06 与 OH2P。LX06 路径涉及拆机和 Micro USB，OH2P 文档使用 Type-C，不能把一种机型的接线或镜像套到另一种。官方文档提到双系统分区的恢复思路，但只有原分区完好时才可能有用。仓库已归档，应把它视为需要自己维护依赖的历史工程。

- 型号：小爱音箱 Pro LX06 / 小米智能音箱 Pro OH2P；按型号刷机文档
- 固件：待按具体型号核实
- 方法与难度：补丁固件 / 高难度
- 拆机 / 焊接 / 云服务：LX06: yes; OH2P: no（按官方教程） / 文档 USB 路径不需要 / 可选
- 额外成本：待核价；主机、按配置选用模型/API 服务
- 证据：E1 — README 明确限定两款 Pro 音箱，提供固件、客户端、服务端三步入口；仓库已归档，仍有历史可复现材料。
- 数据风险：possible；设备失效风险：possible（编辑按路径提示，未实测）
- 恢复：官方 flash.md 说明使用双系统分区，可切回 boot1；该路径取决于原分区完好，本次未实机验证。
- 适合：能核对准确型号、理解固件分区并准备恢复材料的实验者。
- 不适合：家中唯一日用音箱、不能接受停机，或无法确认固件与型号的使用者。

建议验收（未执行）：

- 刷写前记录型号和固件、确认原分区备份与恢复路径
- 先验证音频采集和播放，再连接 AI 服务
- 重启后检查连接恢复；保存可回退的配置

[教程](https://github.com/idootop/open-xiaoai/blob/main/docs/flash.md) · [适配范围](https://github.com/idootop/open-xiaoai/blob/main/README.md) · [完整条目](https://kitagain.com/projects/open-xiaoai.html)

## Onju Voice

**Nest Mini 改 ChatGPT 音箱是不是只改软件**

Google Nest Mini 的原厂主板与服务限制了自定义语音链路。

保留外壳和部分声学部件，换入 ESP32-S3 定制主板，连接外部语音与模型服务。

作者 2023 年 X 原帖及后续说明确认了换板路线。原帖展示的是语音代理场景，不是让 Nest Mini 自身运行大模型。原版已宣布停止维护，应把它作为硬件复用案例阅读。Onju v2 是同一项目家族的后续设计，旧视频不能自动证明 v2 的每个功能。

- 型号：Google Nest Mini 第二代外壳与外围部件
- 固件：待按具体型号核实
- 方法与难度：替换主板 / 高难度
- 拆机 / 焊接 / 云服务：需要 / 依组装方案 / 可选
- 额外成本：待核价；Onju PCBA、拆装工具、主机、可选云语音/API
- 证据：E2 — 作者提供 PCB、固件及服务器安装说明；README 声明不再积极维护，后继为 onju-v2。独立制作者视频说明确认其进行了改装演示，但本轮未播放视频，未升级为独立实测等级。 已浏览作者 X 原帖正文、换板解释和视频组件；未逐帧核验视频。
- 数据风险：possible；设备失效风险：possible（编辑按路径提示，未实测）
- 恢复：保留原主板可提供硬件回退选项；拆装损伤不可由软件恢复。
- 适合：愿意购买或制作 PCB、拆装设备并维护外部语音服务的人。
- 不适合：期待下载一个程序便完成原机越狱，或要求所有推理都在音箱内部的人。

建议验收（未执行）：

- 核对 Nest Mini 代际、PCB 版本和部件清单
- 分开验证拾音、扬声器、网络与服务端
- 测试完整对话和断网后的行为；保留原主板

[教程](https://github.com/justLV/onju-voice/blob/master/README.md) · [适配范围](https://github.com/justLV/onju-voice/blob/master/README.md) · [完整条目](https://kitagain.com/projects/onju-voice.html)

## OpenCore Legacy Patcher

**旧 Intel Mac 升级 macOS 前要核对什么**

部分 Intel Mac 硬件仍能工作，但已不在某些 macOS 版本的官方支持范围。

通过 OpenCore 启动与机型相关补丁，尝试运行原先不受支持的 macOS。

兼容性不能只看年份。官方列表按机型标识区分支持和图形、无线等补丁条件；不覆盖 Apple Silicon 或 PowerPC。系统更新可能需要重新应用补丁，操作系统能启动也不代表全部外设和图形加速正常。应先完成可恢复备份并准备另一启动介质，再评估是否适合作为日用系统。

- 型号：官方支持表内的 Intel Mac
- 固件：待按具体型号核实
- 方法与难度：引导与系统补丁 / 高难度
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 不需要
- 额外成本：待核价；安装 U 盘、备份盘、可选内存/SSD
- 证据：E1 — README 提供版本范围，官方支持矩阵逐列说明 Intel Mac 型号及 GPU/USB 限制；不支持 PowerPC 或 Apple Silicon。
- 数据风险：possible；设备失效风险：possible（编辑按路径提示，未实测）
- 恢复：保留备份与可启动安装介质，按照官方卸载/恢复文档回退；本次未测试设备恢复。
- 适合：能确认 Intel Mac 机型标识、备份数据并自行处理系统更新的人。
- 不适合：仅有一台工作电脑、依赖无中断使用，或把 Apple Silicon 当成同一路线的人。

建议验收（未执行）：

- 核对机型标识、目标 macOS 和补丁需求
- 逐项检查显卡加速、Wi-Fi、睡眠、外接显示和常用软件
- 验证备份可读取，并保留原系统恢复入口

[教程](https://dortania.github.io/OpenCore-Legacy-Patcher/) · [适配范围](https://dortania.github.io/OpenCore-Legacy-Patcher/MODELS.html) · [完整条目](https://kitagain.com/projects/oclp.html)

## Home Assistant OS

**闲置小主机安装 Home Assistant OS 条件**

闲置小型 x86 电脑可以继续运行，却缺少一个明确、低维护的家庭用途。

安装 Home Assistant OS，作为家庭自动化主机，按需连接语音或其他扩展。

官方 Generic x86-64 路径要求 UEFI，需关闭 Secure Boot；目标存储写入会覆盖数据。文档区分 512n/512e 与不支持的 4Kn，老电脑不能仅凭有 64 位 CPU 就判定兼容。安装 HAOS 本身不等于具备本地大模型推理能力，应另算语音模型、加速器与内存需求。

- 型号：官方安装文档支持的 Generic x86-64 / 单板机
- 固件：待按具体型号核实
- 方法与难度：替换系统 / 进阶
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 依可选集成
- 额外成本：待核价；启动 U 盘、健康的系统盘、可选 Zigbee/Thread USB 适配器
- 证据：E1 — 官方 Generic x86-64 文档给出 UEFI、关闭 Secure Boot、512 字节逻辑扇区要求与实际安装步骤。
- 数据风险：expected；设备失效风险：workflow-dependent（编辑按路径提示，未实测）
- 恢复：映像写入会覆盖目标磁盘；先保存全盘镜像，后续用原系统安装介质恢复。
- 适合：有可专用的 x86-64 UEFI 小主机，希望集中管理已有设备的人。
- 不适合：需要保留原磁盘系统、只支持传统 BIOS，或期待低配机器自动获得强 AI 算力的人。

建议验收（未执行）：

- 检查 UEFI、存储扇区和网络条件
- 备份磁盘，安装后确认重启能持续启动
- 连接一个真实设备并完成备份导出和恢复演练

[教程](https://www.home-assistant.io/installation/generic-x86-64/) · [适配范围](https://github.com/home-assistant/operating-system/blob/dev/README.md) · [完整条目](https://kitagain.com/projects/haos.html)

## OpenWrt

**旧路由器能刷 OpenWrt 吗 硬件版本怎么查**

旧路由器的厂商系统可能缺少所需功能或已不再更新。

在受支持的准确硬件版本上安装 OpenWrt，作为路由、接入点或其他网络节点。

项目成熟不代表某个旧型号仍有当前版本支持。品牌、外观和同一销售名称都不足以选择镜像，必须确认硬件版本、闪存和内存限制。首次安装镜像与后续升级镜像可能不同。恢复能力取决于引导程序、串口或厂商恢复模式；没有确认恢复路径时，不应拿家庭唯一出口做试验。

- 型号：Table of Hardware 中对应硬件 revision 的路由器
- 固件：待按具体型号核实
- 方法与难度：替换固件 / 高难度
- 拆机 / 焊接 / 云服务：依具体型号 / 依具体型号 / 不需要
- 额外成本：待核价；网线、可能需要 UART/编程器
- 证据：E1 — README 提供 Firmware Selector 与安装信息链接；可复现范围必须细化到对应型号和硬件修订。
- 数据风险：expected；设备失效风险：possible（编辑按路径提示，未实测）
- 恢复：failsafe 仅适用于仍可启动的情况；无法启动时需具体型号的 TFTP/UART/编程器恢复，不应把恢复出厂设置当作通用救砖。
- 适合：有备用网络、可以核对设备版本和恢复文档的使用者。
- 不适合：极小闪存设备、找不到精确型号条目，或不能接受暂时断网的人。

建议验收（未执行）：

- 先核对精确设备页、硬件版本、镜像类型和校验值
- 备份原配置及设备特有分区，确认恢复工具
- 验证 WAN/LAN、无线与重启，不用一次联网代替稳定性验证

[教程](https://openwrt.org/toh/start) · [适配范围](https://firmware-selector.openwrt.org/) · [完整条目](https://kitagain.com/projects/openwrt.html)

## HA Lovelace Kindle Screensaver

**Kindle 4 变 Home Assistant 墨水屏看板**

闲置 Kindle 屏幕适合低频信息，但不能直接按现代平板方式展示所有网页。

由服务端生成 Home Assistant 仪表板图像，再由 Kindle 更新显示。

项目作者以 Kindle 4 为实例。渲染发生在外部服务，设备主要承担显示任务，因此应分别排查 Home Assistant 页面权限、截图生成和设备拉取。刷新频率越高，不一定越实用：墨水屏延迟、残影与耗电必须在自己的设备上测量。它适合状态看板，不适合视频或高频交互。

- 型号：能运行截图显示脚本的 jailbroken Kindle
- 固件：待按具体型号核实
- 方法与难度：安装脚本 / 进阶
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 可使用本地服务
- 额外成本：待核价；Home Assistant 与截图服务器
- 证据：E1 — README 提供 HA 截图服务、online screensaver 和作者 Kindle 4 设置入口。
- 数据风险：possible；设备失效风险：workflow-dependent（编辑按路径提示，未实测）
- 恢复：删除定时下载/显示脚本，撤销 HA 访问令牌；原阅读用途保留情况依赖安装方式。
- 适合：已有 Home Assistant，希望把少量状态长期放在墙面或桌面的使用者。
- 不适合：要求实时动画、复杂触控控制或无需任何服务端的使用者。

建议验收（未执行）：

- 先生成一张正确尺寸的截图，再检查设备显示
- 测试认证失效与网络中断，避免静默展示过期信息
- 测量刷新间隔与实际耗电，显示数据更新时间

[教程](https://github.com/sibbl/hass-lovelace-kindle-4) · [适配范围](https://github.com/sibbl/hass-lovelace-kindle-screensaver/blob/main/README.md) · [完整条目](https://kitagain.com/projects/kindle-ha.html)

## Kindle for WHOOP

**旧 Kindle 显示 WHOOP 数据和 AI 辅助配置**

旧 Kindle 的墨水屏仍可用，但阅读之外的实时信息展示受到原系统限制。

将 WHOOP 数据渲染为图像，通过越狱后的设备显示，并尝试定时唤醒和休眠。

作者记录的实机边界是 Kindle Paperwhite 2、固件 5.10.3，以及一次唤醒、联网、更新和休眠链路验证。项目提供 AI 辅助配置文档，可用于让 Codex 或 Claude 协助部署；这不等于 AI 在 Kindle 上本地运行，也不证明全部代码由 AI 编写。一次周期成功不能推导数周续航。

- 型号：项目配置支持的 jailbroken Kindle
- 固件：5.10.3（作者唯一已验证范围）
- 方法与难度：安装脚本 / 高难度
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 需要 WHOOP 服务
- 额外成本：待核价；WHOOP 账号/服务、数据服务主机
- 证据：E2 — 作者 README 明确实机验证 Paperwhite 2 / 5.10.3 的手动刷新与一次 RTC 唤醒、联网刷新、再休眠完整周期；未找到独立复现。
- 数据风险：possible；设备失效风险：possible（编辑按路径提示，未实测）
- 恢复：先停用自动唤醒刷新、移除客户端配置并撤销不再需要的 API 授权；保留原设备文件备份。
- 适合：已有匹配旧 Kindle、WHOOP 数据来源，愿意处理 KUAL/linkss 和服务配置的人。
- 不适合：使用未确认可越狱固件、要求长续航已经被充分测量，或不愿维护外部数据服务的人。

建议验收（未执行）：

- 核对 PW2 和固件，不将示例推广到任意 Kindle
- 先手动刷新，再测试定时唤醒和休眠
- 持续记录耗电、失败重试和联网行为，补充多日复现

[教程](https://github.com/kaibuildsai/kindle-for-whoop/blob/main/docs/ai-assisted-setup.md) · [适配范围](https://github.com/kaibuildsai/kindle-for-whoop/blob/main/README.md) · [完整条目](https://kitagain.com/projects/kindle-whoop.html)

## Valetudo

**扫地机器人脱离云服务 Valetudo 支持哪些型号**

部分扫地机器人依赖厂商云控制，而机械与传感器仍可工作。

在受支持且能取得相应权限的设备上，用本地服务接替云端接口。

Valetudo 明确不是通用替换固件。支持列表是穷尽清单，不在列表上就不应推测可用。同名 Xiaomi 1C 也存在不同硬件修订，文档只支持指定内部型号；Xiaomi V1 的生产时间还会改变是否需要拆机。原厂地图或硬件能力缺失不会因为去云就自动补齐。

- 型号：Valetudo 支持列表中的具体扫地机器人型号
- 固件：待按具体型号核实
- 方法与难度：云服务替代 / 高难度
- 拆机 / 焊接 / 云服务：依具体型号 / 依具体型号 / 不需要
- 额外成本：待核价；按型号的刷写/连接工具
- 证据：E1 — README 明确是运行在厂商固件上的本地云替代层，官方提供支持机器人列表和逐机型安装方法。
- 数据风险：possible；设备失效风险：workflow-dependent（编辑按路径提示，未实测）
- 恢复：必须按对应机器人的 rooting 方法备份；本次未验证任何型号的救砖。
- 适合：精确型号在支持列表中、愿意按机型准备工具和恢复方法的人。
- 不适合：型号不在列表上，或希望借此修复电池、电机等物理故障的人。

建议验收（未执行）：

- 核对内部型号、生产批次与对应 root 文档
- 断开互联网后测试清扫和本地控制
- 检查地图、充电回座、配置持久化和恢复条件

[教程](https://valetudo.cloud/) · [适配范围](https://valetudo.cloud/pages/general/supported-robots/) · [完整条目](https://kitagain.com/projects/valetudo.html)

## wire-pod

**Vector 机器人停服后 wire-pod 怎么继续使用**

Vector 机器人部分语音能力依赖外部服务，云端可用性影响持续使用。

使用自己运行的 wire-pod 服务接收语音并处理请求，可配置知识服务。

它把服务依赖转移到自己维护的主机，不能修复机器人电池、显示屏或网络硬件。Vector 1.0/2.0 的部署入口应跟随当前官方说明，服务端证书、网络和设备配置均是验收点。选择云模型还是其他后端会改变隐私、费用和离线能力，不能把‘自建服务’等同于全链路离线。

- 型号：Anki / Digital Dream Labs Vector 机器人，按 setup 支持范围
- 固件：待按具体型号核实
- 方法与难度：云服务替代 / 高难度
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 知识服务可选
- 额外成本：待核价；常开服务器
- 证据：E1 — README 明确 Vector 1.0/2.0 与生产机器人支持，提供安装 wiki 与故障排查入口。
- 数据风险：possible；设备失效风险：workflow-dependent（编辑按路径提示，未实测）
- 恢复：保留配对与固件信息；仅重新部署服务端不保证解决固件或硬件故障。
- 适合：已有可用 Vector，并能长期运行及维护局域网服务的人。
- 不适合：机器人本体无法开机，或不愿维护任何常开主机的人。

建议验收（未执行）：

- 记录设备版本，检查服务端与机器人网络连通性
- 验证本地语音命令及可选知识问答
- 重启服务端与设备后重测，记录外网依赖

[教程](https://github.com/kercre123/wire-pod/wiki/Installation) · [适配范围](https://github.com/kercre123/wire-pod/blob/main/README.md) · [完整条目](https://kitagain.com/projects/wirepod.html)

## OpenLumi

**旧小米 Aqara 网关 OpenLumi 型号与备份**

旧款小米或 Aqara 网关仍有可用的 Zigbee 等硬件，但用途受原厂软件限制。

在限定型号上改装系统，将网关纳入自己维护的本地智能家居服务。

项目列出的 DGNWG05LM、mieu01 EU 和 ZHWG11LM 不能推广到名字相近的 DGNWG02LM。原始 rootfs 备份包含设备特有内容，其他人的镜像不能替代自己的备份。这个案例体现了复活项目常见的真正门槛：不是找到一个仓库，而是准确识别版本并保住不可再生的设备数据。

- 型号：OpenLumi 文档支持的小米网关硬件版本
- 固件：待按具体型号核实
- 方法与难度：替换固件 / 高难度
- 拆机 / 焊接 / 云服务：依具体方法 / 依具体方法 / 不需要
- 额外成本：待核价；现有设备、电源/存储/连接配件是否足够需逐机检查
- 证据：E1 — README 限定硬件版本，提供 backup、OTA failure recovery、return to stock firmware 段落。
- 数据风险：possible；设备失效风险：possible（编辑按路径提示，未实测）
- 恢复：必须保留本机 rootfs tar.gz 备份，不能用他人的通用备份代替设备唯一数据。
- 适合：型号准确匹配，能按文档备份、接线和检查系统的人。
- 不适合：只凭外壳识别型号、没有设备原始备份，或希望直接套用他人镜像的人。

建议验收（未执行）：

- 对照铭牌与文档核对型号、地区和硬件版本
- 离线保存并检查本机备份完整性
- 验证设备加入、控制、重启和恢复路径

[教程](https://github.com/openlumi/openlumi.github.io/blob/master/README.md) · [适配范围](https://github.com/openlumi/openlumi.github.io/blob/master/README.md) · [完整条目](https://kitagain.com/projects/openlumi.html)

## HP Laser 1008a macOS driver

**HP Laser 1008a Apple Silicon macOS USB 开源驱动**

作者在 Apple Silicon Mac 上遇到 HP Laser 1008a 驱动不可用的问题，打印机硬件仍可工作。

通过 SpliX 衍生转换与原生 CUPS/IOKit 连接，恢复特定 HP Laser 系列的 USB 打印。

作者在 X 表示使用 Claude 并经过约 30–40 次提示与试错，公开过程与代码。README 的作者验证范围为 Apple Silicon、macOS 26 与 HP Laser 1003/1006/1008 a/w 的 USB 路径。不能据此推断 Wi-Fi、所有 HP 型号或 Intel Mac 都可用。安装涉及管理员级系统配置，卸载脚本与许可拆分同样需要阅读。

- 型号：HP Laser 1003/1006/1008 a/w USB + Apple Silicon macOS 26（作者测试范围）
- 固件：待按具体型号核实
- 方法与难度：安装驱动 / 进阶
- 拆机 / 焊接 / 云服务：不需要 / 不需要 / 运行时不需要
- 额外成本：待核价；USB 数据线、兼容 Mac
- 证据：E2 — 作者 README 声明 Apple Silicon macOS 26 经 USB 测试，给出安装、卸载和打印链路分析；作者自托管 Claude 会话页支持 AI 辅助开发归类。X 原文另行记录访问状态。 已浏览作者 X 主帖及回复，确认作者称使用 Claude 并多轮试错。
- 数据风险：possible；设备失效风险：workflow-dependent（编辑按路径提示，未实测）
- 恢复：仓库提供 uninstall.sh，README 解释如何撤销对 ippusbd 的更改；安装器需要管理员权限。
- 适合：设备和系统版本匹配，能检查安装脚本并处理 CUPS 打印队列的人。
- 不适合：只用 Wi-Fi 打印、设备不在作者测试范围，或无法接受系统配置变动的人。

建议验收（未执行）：

- 记录 macOS、CPU、USB 设备身份和驱动版本
- 测试真实文档、多页任务、重启后打印与错误恢复
- 检查卸载路径；不把打印成功推导为所有设备功能受支持

[教程](https://github.com/Kuberwastaken/hp-laser-1008a-macos/blob/main/README.md) · [适配范围](https://github.com/Kuberwastaken/hp-laser-1008a-macos/blob/main/README.md) · [完整条目](https://kitagain.com/projects/printer-spl3.html)
