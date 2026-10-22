"""Merge the original detailed watchlist with compact researched expansion records."""
import json


def load_watchlist(data_dir):
    base = json.loads((data_dir / "watchlist.json").read_text(encoding="utf-8"))
    details = json.loads((data_dir / "watchlist-details.json").read_text(encoding="utf-8"))
    expansion = json.loads((data_dir / "watchlist-expansion.json").read_text(encoding="utf-8"))
    for item in expansion:
        slug = item["slug"]
        if slug in base:
            raise ValueError(f"Duplicate watchlist slug: {slug}")
        base[slug] = {
            "content_id": item["content_id"],
            "category": item["category"],
            "source_platform": item["source_platform"],
            "source_url": item["source_url"],
            "code_url": None,
            "additional_sources": [],
            "status": item["status"],
            "reviewed_at": item["reviewed_at"],
            "zh": {key: item["zh"][key] for key in ["title", "summary", "gap", "next_check", "safety"]},
            "en": {key: item["en"][key] for key in ["title", "summary", "gap", "next_check", "safety"]},
        }
        details[slug] = {
            "resources": [{
                "url": item["source_url"],
                "kind": item["resource_kind"],
                "zh_label": item["zh"]["resource_label"],
                "en_label": item["en"]["resource_label"],
                "zh_note": item["zh"]["resource_note"],
                "en_note": item["en"]["resource_note"],
            }],
            "zh": {
                "stage": item["zh"]["summary"],
                "usable": item["zh"]["usable"],
                "works_for": item["zh"]["works_for"],
                "not_for": item["zh"]["not_for"],
                "value": item["zh"]["value"],
                "follow": item["zh"]["follow"],
            },
            "en": {
                "stage": item["en"]["summary"],
                "usable": item["en"]["usable"],
                "works_for": item["en"]["works_for"],
                "not_for": item["en"]["not_for"],
                "value": item["en"]["value"],
                "follow": item["en"]["follow"],
            },
        }
    atlas = json.loads((data_dir / "device-atlas.json").read_text(encoding="utf-8"))
    route_copy = {
        "esphome": {
            "zh": {
                "title": "{device}：改成 ESPHome 本地智能设备",
                "summary": "目标很明确：为 {device} 使用 ESPHome 配置，摆脱或减少原厂云依赖，并接入 Home Assistant 等本地系统。",
                "gap": "本轮确认了上游设备库中存在这个型号的配置页，但尚未逐项复核页面里的芯片、PCB 修订、刷写方式和全部功能。",
                "next_check": "打开型号页核对主控芯片、引脚、硬件版本和刷写入口；再找同版 PCB 的成功记录与恢复路径。",
                "safety": "涉及市电的设备必须断电操作，不能在外壳打开时带电调试；型号名相同也可能换芯，先确认 PCB。",
                "usable": "可作为准确型号的配置入口；在核对芯片和硬件修订前，不能把它当成即刷即用固件。",
                "works_for": ["准确型号为 {model} 的设备", "愿意核对芯片、PCB 和刷写方式的 ESPHome 用户"],
                "not_for": ["只有外壳相似、无法确认内部主控的设备", "不具备安全拆机条件的市电设备"],
                "value": "把分散的 ESPHome 设备配置落到具体型号，方便先判断是否值得拆机和继续查证。",
                "follow": "如果型号和芯片完全一致，值得继续；任一硬件修订不明时先停在资料核对阶段。",
                "resource_label": "ESPHome 设备配置页",
                "resource_note": "上游设备库为这个型号保留的配置入口；本轮确认页面存在，未把页面内容视为 KitAgain 实机验证。",
            },
            "en": {
                "title": "{device}: convert it to a local ESPHome device",
                "summary": "The goal is clear: use an ESPHome configuration for {device}, reduce dependence on the vendor cloud and connect it to a local system such as Home Assistant.",
                "gap": "This review confirmed that the upstream device database contains a page for this model, but has not checked every chip, PCB revision, flashing method or feature on that page.",
                "next_check": "Open the model page and verify the controller, pins, hardware revision and flashing access, then find a matching-PCB report and recovery route.",
                "safety": "Disconnect mains-powered devices before opening them and never probe an exposed energized device. Identical product names may hide different chips or PCBs.",
                "usable": "A model-specific configuration starting point, not a flash-ready guarantee until the chip and board revision match.",
                "works_for": ["Devices whose exact model is {model}", "ESPHome users prepared to verify the chip, PCB and flashing route"],
                "not_for": ["Lookalike products whose controller cannot be identified", "Mains devices without a safe disassembly and isolation setup"],
                "value": "Maps a scattered ESPHome configuration to a concrete model so a user can decide whether deeper research and disassembly are worthwhile.",
                "follow": "Continue when the exact model and chip match; stop at research when any hardware revision remains unclear.",
                "resource_label": "ESPHome device configuration page",
                "resource_note": "The upstream device-database entry for this model. Its presence was confirmed; KitAgain has not treated it as hands-on verification.",
            },
        },
        "tasmota": {
            "zh": {
                "title": "{device}：刷 Tasmota，改成本地控制",
                "summary": "目标是按设备模板为 {device} 配置 Tasmota，让开关、灯具、插座或传感器通过本地网页、MQTT 或智能家居系统控制。",
                "gap": "本轮读取了模板仓库的型号元数据，但没有验证当前零售批次是否仍使用相同芯片，也没有在实物上刷写。",
                "next_check": "核对型号、地区规格、芯片和模板页面的刷写说明；确认是否需要拆机、串口或替换模组。",
                "safety": "市电设备必须断电、隔离并由具备相关能力的人操作；不要依据商品外观推断内部芯片。",
                "usable": "模板和型号入口已经存在，可用于判断路线；在确认当前硬件批次前不应直接套用。",
                "works_for": ["准确型号为 {model} 的设备", "能够验证内部芯片与模板版本的 Tasmota 用户"],
                "not_for": ["同品牌但型号或地区规格不同的产品", "无法安全拆机或恢复原固件的设备"],
                "value": "直接给出型号级模板入口，减少在通用刷机教程里猜 GPIO 和设备类型的时间。",
                "follow": "型号、芯片与模板一致时可继续；芯片换代或模板页标记不支持时停止。",
                "resource_label": "Tasmota 设备模板页",
                "resource_note": "模板库提供型号、设备类型和配置入口；收录只表示存在模板资料，不表示 KitAgain 已刷写成功。",
            },
            "en": {
                "title": "{device}: flash Tasmota for local control",
                "summary": "The goal is to configure Tasmota for {device} so its switch, light, plug or sensor can be controlled locally through the web UI, MQTT or a home-automation system.",
                "gap": "Model metadata was read from the template repository, but the current retail revision and controller were not verified and no hardware was flashed.",
                "next_check": "Match the model, regional standard, controller and flashing instructions, including any disassembly, serial access or module replacement.",
                "safety": "Disconnect and isolate mains hardware and use qualified help when needed. Do not infer the internal controller from the enclosure alone.",
                "usable": "A real model/template starting point, but not safe to apply until the current hardware revision is confirmed.",
                "works_for": ["Devices whose exact model is {model}", "Tasmota users able to verify the controller and template revision"],
                "not_for": ["Products with a different model or regional electrical version", "Devices without a safe disassembly or stock-firmware recovery route"],
                "value": "Provides a model-level template entry instead of forcing users to guess GPIO assignments from generic flashing guides.",
                "follow": "Continue when model, chip and template agree; stop for a changed controller or an upstream unsupported warning.",
                "resource_label": "Tasmota device template",
                "resource_note": "The template database provides model and configuration metadata. Inclusion does not mean KitAgain flashed the hardware.",
            },
        },
        "openwrt-cn": {
            "zh": {
                "title": "{device}：刷 OpenWrt 延长路由器寿命",
                "summary": "目标是把 {device} 改成可继续维护的 OpenWrt 路由器，用于拨号、旁路由、无线接入或基础网络服务。",
                "gap": "中文论坛汇总页列出了这个型号，但它不是逐型号安装教程；硬件版本、引导布局、分区和恢复方法仍需回到官方设备页核对。",
                "next_check": "先查 OpenWrt 官方 Table of Hardware、固件选择器和该型号的硬件修订，再核对论坛帖中的固件来源与恢复方式。",
                "safety": "不要混刷 U-Boot 布局与原厂布局镜像；升级前备份分区和校准数据，找不到精确硬件版本时停止。",
                "usable": "可作为中文型号发现入口；尚不足以单独指导刷机。",
                "works_for": ["准确型号为 {model} 的路由器", "能进一步核对官方设备页和分区布局的用户"],
                "not_for": ["仅凭外观判断型号的路由器", "无法备份或没有串口/救援恢复方案的高风险设备"],
                "value": "中文社区一次列出大量具体型号，适合快速判断手里设备是否值得进入下一轮核查。",
                "follow": "官方设备页与硬件修订能对上时继续；只有第三方固件包而没有来源和恢复说明时不要刷。",
                "resource_label": "恩山 OpenWrt 型号汇总帖",
                "resource_note": "帖子列出该型号及相关固件入口；它是发现线索，不替代官方型号页和逐步安装文档。",
            },
            "en": {
                "title": "{device}: extend its life with OpenWrt",
                "summary": "The goal is to turn {device} into a maintainable OpenWrt router for routing, access-point or basic network-service duties.",
                "gap": "A Chinese community roundup lists this model, but it is not a model-specific installation guide. Hardware revision, boot layout, partitions and recovery still need official confirmation.",
                "next_check": "Check the official OpenWrt hardware table and firmware selector, identify the hardware revision, then verify the forum image source and recovery path.",
                "safety": "Never mix stock-layout and OpenWrt-bootloader images. Back up partitions and calibration data; stop when the exact hardware revision is unknown.",
                "usable": "Useful as a Chinese-language model discovery entry, but not sufficient by itself for flashing.",
                "works_for": ["Routers whose exact model is {model}", "Users able to verify the official device page and partition layout"],
                "not_for": ["Routers identified only by enclosure appearance", "High-risk devices without backups or serial/recovery access"],
                "value": "A Chinese community source collects many concrete models and helps decide which owned router deserves deeper verification.",
                "follow": "Continue when the official device page and revision agree. Do not flash an unattributed third-party image without recovery instructions.",
                "resource_label": "Chinese OpenWrt model roundup",
                "resource_note": "The forum post lists the model and firmware entry points. It is a discovery source, not a substitute for the official device page and installation steps.",
            },
        },
        "armbian-cn": {
            "zh": {
                "title": "{device}：把电视盒子改成 Armbian 小服务器",
                "summary": "目标是让 {device} 从安卓电视盒子变成 Armbian 小主机，可承载 Docker、文件服务、Home Assistant 或轻量网络服务。",
                "gap": "维护者设备表列出了型号与芯片系列，但同名盒子可能更换主板、内存、网卡或存储；本轮未验证这台实物。",
                "next_check": "核对 SoC、主板丝印、内存与网卡，先从 USB/TF 启动并验证网络和存储，再考虑写入 eMMC。",
                "safety": "先备份原厂安卓与启动分区；设备树不匹配时可能无显示、无网或无法启动，未验证前不要直接覆盖 eMMC。",
                "usable": "维护者把它列入支持表，可作为选镜像和设备树的起点；实际板型仍需确认。",
                "works_for": ["准确型号为 {model} 且 SoC/主板一致的盒子", "愿意先用 USB/TF 做非破坏性启动验证的用户"],
                "not_for": ["同名但主板、Wi-Fi 或存储芯片未知的盒子", "没有原厂固件备份就准备直接写 eMMC 的设备"],
                "value": "中文维护文档把盒子型号、芯片和镜像系列放在同一张表里，方便先筛掉明显不匹配的路线。",
                "follow": "能从外置介质稳定启动、网络和存储正常后再继续；设备树或恢复包不明时停手。",
                "resource_label": "ophub Armbian 中文支持设备表",
                "resource_note": "维护者文档列出该型号及对应 SoC/镜像系列，并提供备份、外置启动和安装说明。",
            },
            "en": {
                "title": "{device}: turn the TV box into an Armbian server",
                "summary": "The goal is to convert {device} from an Android TV box into a small Armbian host for Docker, file services, Home Assistant or light network services.",
                "gap": "The maintainer device table lists the model and SoC family, but identical product names may hide different boards, memory, Wi-Fi or storage. No unit was tested here.",
                "next_check": "Verify the SoC, board marking, memory and network chip. Boot from USB or microSD and test networking and storage before considering eMMC installation.",
                "safety": "Back up the stock Android and boot partitions. A wrong device tree may lose display, network or boot; do not overwrite eMMC before external-media testing.",
                "usable": "A maintainer-listed starting point for image and device-tree selection; the physical board still needs confirmation.",
                "works_for": ["{model} units with a matching SoC and board", "Users willing to validate non-destructively from USB or microSD first"],
                "not_for": ["Same-name boxes with unknown board, Wi-Fi or storage chips", "Devices headed for direct eMMC installation without a stock backup"],
                "value": "The Chinese maintainer document maps box models to SoC/image families so obvious mismatches can be rejected early.",
                "follow": "Continue only after stable external boot with working network and storage; stop when the device tree or recovery image is unknown.",
                "resource_label": "ophub Armbian supported-device table",
                "resource_note": "The maintainer documentation lists this model and SoC/image family, with backup, external-boot and installation guidance.",
            },
        },
        "postmarketos": {
            "zh": {
                "title": "{device}：尝试运行 postmarketOS Linux",
                "summary": "目标是让 {device} 脱离原厂停更系统，尝试启动 postmarketOS，作为 Linux 终端、测试机或专用控制设备。",
                "gap": "本轮只确认 postmarketOS 设备索引中有这个型号页；尚未读取该页的启动状态、功能矩阵和当前安装步骤。",
                "next_check": "打开精确设备页，核对分类、内核路线、刷写方式、屏幕、触摸、Wi-Fi、音频和蜂窝功能状态。",
                "safety": "解锁和刷写可能清除数据或使设备无法启动；先确认恢复镜像、下载模式和准确代号。",
                "usable": "目前是型号级 Linux 移植入口；在读完设备状态表前不能当作日用系统推荐。",
                "works_for": ["准确型号为 {model} 的设备", "接受部分硬件功能缺失并愿意参与移植测试的用户"],
                "not_for": ["需要相机、通话、GPS 等功能全部可用的主力设备", "无法进入恢复/下载模式或没有数据备份的设备"],
                "value": "先把具体旧设备和上游移植页连起来，用户可以据此快速查看 Linux 启动与功能成熟度。",
                "follow": "设备页显示可启动且关键功能满足用途时继续；仅有占位页或处于 not booting 时先观察。",
                "resource_label": "postmarketOS 设备索引",
                "resource_note": "官方社区 Wiki 的设备索引列出该型号；必须进入设备页查看当前分类和功能状态。",
            },
            "en": {
                "title": "{device}: explore postmarketOS Linux support",
                "summary": "The goal is to move {device} beyond its abandoned vendor OS and try postmarketOS as a Linux terminal, test device or dedicated controller.",
                "gap": "This pass only confirmed a model entry in the postmarketOS device index. Boot status, feature matrix and current installation steps have not yet been read.",
                "next_check": "Open the exact device page and check its category, kernel route, flashing method, display, touch, Wi-Fi, audio and cellular status.",
                "safety": "Unlocking and flashing may erase data or prevent boot. Confirm a recovery image, download mode and exact codename first.",
                "usable": "A model-level Linux porting entry, not a daily-driver recommendation until the device status table is reviewed.",
                "works_for": ["Devices whose exact model is {model}", "Users who accept missing functions and are willing to test a port"],
                "not_for": ["Primary devices requiring full camera, calling, GPS and related functions", "Devices without backups or a known recovery/download mode"],
                "value": "Connects a concrete old device to its upstream porting entry so boot and feature maturity can be checked quickly.",
                "follow": "Continue when the device page boots and its key functions match the intended use; watch and wait for placeholder or not-booting ports.",
                "resource_label": "postmarketOS device index",
                "resource_note": "The official community Wiki index lists this model. Its exact page must be checked for current category and feature status.",
            },
        },
        "x-router": {
            "zh": {
                "title": "{device}：改成授权测试用 Wi-Fi 实验路由器",
                "summary": "目标是把 {device} 改造成用于自有或明确授权网络的 Wi-Fi 实验路由器；X 原帖提供实物线索，GitHub 项目提供构建路线。",
                "gap": "社交帖子是单一作者陈述，项目支持范围仍需按硬件版本核对；本目录没有刷写或执行无线测试。",
                "next_check": "核对 GL-AR300M16-Ext 与相近 AR300M/AR300N 的差异、构建目标、闪存布局、恢复方式和合法测试范围。",
                "safety": "仅用于你拥有或明确获授权的网络；错误固件可能软砖，型号后缀不一致时不要继续。",
                "usable": "有社交原帖和可访问项目文档，可继续做型号与恢复核查；不是现成镜像推荐。",
                "works_for": ["准确型号为 {model} 的路由器", "在自有或授权实验室网络中学习无线安全的用户"],
                "not_for": ["AR300、AR300N 或未确认后缀的相近型号", "没有授权的网络测试或无法承担刷机恢复风险的场景"],
                "value": "展示了 X 可以发现真实改造线索，但必须回到代码和型号文档交叉验证后才值得动手。",
                "follow": "型号、构建目标和恢复路径全部对上时继续；任何一个条件不清楚就停在研究阶段。",
                "resource_label": "X 实物改造帖子",
                "resource_note": "帖子明确提到 GL-AR300M16-Ext 和相应固件构建器；项目文档作为独立可访问佐证。",
            },
            "en": {
                "title": "{device}: an authorized Wi-Fi lab router",
                "summary": "The goal is to convert {device} into a Wi-Fi lab router for networks you own or are explicitly authorized to test. The X post supplies a hardware lead and GitHub supplies the build route.",
                "gap": "The social post is one author's report and support still depends on exact hardware. This catalog did not flash the router or perform wireless testing.",
                "next_check": "Verify differences among GL-AR300M16-Ext, AR300M and AR300N, plus build target, flash layout, recovery and the authorized test scope.",
                "safety": "Use only on networks you own or have explicit permission to test. A wrong image can soft-brick the router; stop when the model suffix differs.",
                "usable": "The original social post and accessible project documentation justify deeper model and recovery research, not a ready-made image recommendation.",
                "works_for": ["Routers whose exact model is {model}", "Users learning wireless security in their own or authorized lab network"],
                "not_for": ["AR300, AR300N or similar models with an unverified suffix", "Unauthorized network testing or cases without a recoverable flashing path"],
                "value": "Shows how X can surface a real build lead while code and model documentation remain necessary before acting.",
                "follow": "Continue only when model, build target and recovery all match; otherwise keep it at research stage.",
                "resource_label": "Original X build post",
                "resource_note": "The post names GL-AR300M16-Ext and the firmware builder; accessible project documentation provides corroboration.",
            },
        },
    }
    assert len(atlas["items"]) == 300, "The 400-entry release requires exactly 300 new device records"
    for item in atlas["items"]:
        slug = item["slug"]
        if slug in base:
            raise ValueError(f"Duplicate device-atlas slug: {slug}")
        copy = route_copy[item["route_type"]]
        localized = {}
        for lang in ["zh", "en"]:
            localized[lang] = {key: value.format(device=item["device"], model=item["model"]) if isinstance(value, str) else [part.format(device=item["device"], model=item["model"]) for part in value] for key, value in copy[lang].items()}
        base[slug] = {
            "content_id": item["content_id"],
            "category": item["category"],
            "source_platform": item["source_platform"],
            "source_url": item["source_url"],
            "code_url": item["extra_sources"][0] if item["extra_sources"] else None,
            "additional_sources": item["extra_sources"][1:] if item["extra_sources"] else [],
            "status": "device-lead-needs-exact-hardware-check",
            "reviewed_at": atlas["reviewed_at"],
            "device_name": item["device"],
            "device_model": item["model"],
            "route_type": item["route_type"],
            "source_language": item["source_language"],
            "source_access": item["source_access"],
            "discovery_channel": item["discovery_channel"],
            "zh": {key: localized["zh"][key] for key in ["title", "summary", "gap", "next_check", "safety"]},
            "en": {key: localized["en"][key] for key in ["title", "summary", "gap", "next_check", "safety"]},
        }
        resources = [{
            "url": item["source_url"],
            "kind": item["source_kind"],
            "zh_label": localized["zh"]["resource_label"],
            "en_label": localized["en"]["resource_label"],
            "zh_note": localized["zh"]["resource_note"],
            "en_note": localized["en"]["resource_note"],
        }]
        for index, url in enumerate(item["extra_sources"], 1):
            resources.append({
                "url": url,
                "kind": "corroborating-project-documentation",
                "zh_label": f"项目佐证 {index}",
                "en_label": f"Project corroboration {index}",
                "zh_note": "用于核对社交帖子中的项目、设备范围与构建方法；仍需按准确硬件版本复核。",
                "en_note": "Used to check the project, device scope and build route mentioned by the social post; exact hardware still requires review.",
            })
        details[slug] = {
            "resources": resources,
            "zh": {key: localized["zh"][key] for key in ["summary", "usable", "works_for", "not_for", "value", "follow"] if key != "summary"} | {"stage": localized["zh"]["summary"]},
            "en": {key: localized["en"][key] for key in ["summary", "usable", "works_for", "not_for", "value", "follow"] if key != "summary"} | {"stage": localized["en"]["summary"]},
        }
    return base, details
