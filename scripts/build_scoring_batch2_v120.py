"""Build the v1.20 second scoring-enrichment batch.

This ledger is intentionally separate from the canonical scoring file so the
release integrator can review and merge it.  Every scored dimension has a
bilingual basis and one or more HTTPS sources; an entry remains unrated when
fewer than three dimensions are supported.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY_PATH = ROOT / "data" / "directory.json"
OUTPUT_PATH = ROOT / "data" / "scoring-evidence-batch2-v120.json"
CHECKED_AT = "2026-10-24"
COMPONENTS = ("feasibility", "cost", "docs_community", "practical_value", "risk")

OPHUB_README = "https://github.com/ophub/amlogic-s9xxx-armbian/blob/main/README.md"
OPHUB_DOCS = "https://github.com/ophub/amlogic-s9xxx-armbian/tree/main/documents"
OPHUB_RELEASES = "https://github.com/ophub/amlogic-s9xxx-armbian/releases"
OPENWRT_OVERVIEW = "https://downloads.openwrt.org/releases/25.12.6/.overview.json"
OPENWRT_README = "https://github.com/openwrt/openwrt/blob/main/README.md"
OPENWRT_SELECTOR_DOC = "https://github.com/openwrt/firmware-selector-openwrt-org/blob/main/README.md"
ESPHOME_INSTALL = "https://esphome.io/install/getting-started/"
ESPHOME_HOME = "https://esphome.io/"


TV_DEVICES = [
    ("lead:atlas-ophub-khadas-vim3", "Khadas VIM3"),
    ("lead:atlas-ophub-beelink-gt-king", "Beelink GT-King"),
    ("lead:atlas-ophub-beelink-gt-king-pro", "Beelink GT-King Pro"),
    ("lead:atlas-ophub-ugoos-am6-plus", "Ugoos AM6 Plus"),
    ("lead:atlas-ophub-odroid-n2", "ODROID N2"),
    ("lead:atlas-ophub-x88-king", "X88 King"),
    ("lead:atlas-ophub-x96-max-plus", "X96 Max+"),
    ("lead:atlas-ophub-hk1-box", "HK1 Box"),
    ("lead:atlas-ophub-vontar-x3", "Vontar X3"),
    ("lead:atlas-ophub-h96-max-x3", "H96 Max X3"),
    ("lead:atlas-ophub-ugoos-x3", "Ugoos X3"),
    ("lead:atlas-ophub-x96-air", "X96 Air"),
    ("lead:atlas-ophub-a95x-f3-air", "A95X F3 Air"),
    ("lead:atlas-ophub-x88-pro-x3", "X88 Pro X3"),
    ("lead:atlas-ophub-tox1", "TOX1"),
    ("lead:atlas-ophub-khadas-vim3l", "Khadas VIM3L"),
    ("lead:atlas-ophub-mecool-km3-4g", "MECOOL KM3 4G"),
    ("lead:atlas-ophub-tanix-tx5-max", "Tanix TX5 Max"),
    ("lead:atlas-ophub-zte-b860h-v5", "ZTE B860H V5"),
    ("lead:atlas-ophub-cm311-1a-yst", "CM311-1a-YST"),
]


NETWORK_DEVICES = [
    ("lead:atlas-enshi-xiaomi-ax3600", "xiaomi_ax3600", "qualcommax/ipq807x"),
    ("lead:atlas-enshi-xiaomi-ax9000", "xiaomi_ax9000", "qualcommax/ipq807x"),
    ("lead:atlas-enshi-xiaomi-mi-router-wr30u", "xiaomi_mi-router-wr30u-stock", "mediatek/filogic"),
    ("lead:atlas-enshi-xiaomi-redmi-router-ax6000", "xiaomi_redmi-router-ax6000-stock", "mediatek/filogic"),
    ("lead:atlas-enshi-xiaomi-router-ax3200", "xiaomi_redmi-router-ax6s", "mediatek/mt7622"),
    ("lead:atlas-enshi-xiaomi-miwifi-range-extender-ac1200-ra75", "xiaomi_mi-ra75", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-mi-router-3-pro", "xiaomi_mi-router-3-pro", "ramips/mt7621"),
    ("lead:atlas-enshi-xiaomi-mi-router-3g-v2", "xiaomi_mi-router-3g-v2", "ramips/mt7621"),
    ("lead:atlas-enshi-xiaomi-mi-router-3g", "xiaomi_mi-router-3g", "ramips/mt7621"),
    ("lead:atlas-enshi-xiaomi-mi-router-4", "xiaomi_mi-router-4", "ramips/mt7621"),
    ("lead:atlas-enshi-xiaomi-mi-router-4a-100m-international-edition-v2", "xiaomi_mi-router-4a-100m-intl-v2", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-mi-router-4a-100m-international-edition", "xiaomi_mi-router-4a-100m-intl", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-mi-router-4a-100m-edition", "xiaomi_mi-router-4a-100m", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-mi-router-4a-gigabit-edition-v2", "xiaomi_mi-router-4a-gigabit-v2", "ramips/mt7621"),
    ("lead:atlas-enshi-xiaomi-mi-router-4c", "xiaomi_mi-router-4c", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-mi-router-ac2100", "xiaomi_mi-router-ac2100", "ramips/mt7621"),
    ("lead:atlas-enshi-xiaomi-miwifi-3a", "xiaomi_miwifi-3a", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-miwifi-3c", "xiaomi_miwifi-3c", "ramips/mt76x8"),
    ("lead:atlas-enshi-xiaomi-miwifi-mini", "xiaomi_miwifi-mini", "ramips/mt7620"),
    ("lead:atlas-enshi-xiaomi-redmi-router-ac2100", "xiaomi_redmi-router-ac2100", "ramips/mt7621"),
]


SMART_HOME_IDS = [
    "lead:atlas-esphome-4moms-mamaroo-4",
    "lead:atlas-esphome-avatto-s06-ir-remote-no-temp-no-humidity",
    "lead:atlas-esphome-acenx-sop04-us",
    "lead:atlas-esphome-aoycocr-x10s-plug",
    "lead:atlas-esphome-arlec-fl052ha-security-flood-light",
    "lead:atlas-esphome-arlec-grid-connect-smart-led-globe-cwww",
    "lead:atlas-esphome-arlec-pb89ha-plug",
    "lead:atlas-esphome-arthofer-engineering-wifi-fancontroller",
    "lead:atlas-esphome-athom-e27-7w-bulb",
    "lead:atlas-esphome-athom-multi-target-sensor-ps02c3mz",
    "lead:atlas-esphome-athom-smart-plug-pg04v3-uk16a",
    "lead:atlas-esphome-aubess-mini-smart-switch",
    "lead:atlas-esphome-azpen-home-with-usb",
    "lead:atlas-esphome-blitzwolf-bh-ap2501",
    "lead:atlas-esphome-brilliant-lighting-bl20925-power-monitoring-plug",
    "lead:atlas-esphome-brilliant-smart-wi-fi-rgb-garden-light",
    "lead:atlas-esphome-cloudfree-eu-plug-p1eu",
    "lead:atlas-esphome-connected-consumer-fuel-smart-oil-gauge",
    "lead:atlas-esphome-deta-grid-connect-smart-double-touch-power-point-with-dual-usb-6920ha",
    "lead:atlas-esphome-deta-mechanism-switch-6014ha",
    "lead:atlas-esphome-dewenwils-heavy-duty-40a-outdoor-plug-howt01a",
    "lead:atlas-esphome-duux-bora-dxdh02",
    "lead:atlas-esphome-electriq-iqoolsmart12hp-air-conditioner",
    "lead:atlas-esphome-etekcity-voltson-esw01-usa-r6p",
    "lead:atlas-esphome-feit-om100-rgbw-ca-ag",
    "lead:atlas-esphome-feit-dimsmart-3-can",
    "lead:atlas-esphome-girier-switch-4gang",
    "lead:atlas-esphome-geeni-sw003-199-6-outlet-surge-protector",
    "lead:atlas-esphome-ghome-sw5",
    "lead:atlas-esphome-goldair-gpoc2415-smart-heater",
    "lead:atlas-esphome-gosund-sp112",
    "lead:atlas-esphome-gosund-wo1",
    "lead:atlas-esphome-h801-rgbw-led-controller",
    "lead:atlas-esphome-hankerila-ea8",
    "lead:atlas-esphome-holman-4x34mm-spotlight",
    "lead:atlas-esphome-inkbird-pth-9cw",
    "lead:atlas-esphome-king-wall-switch-3gang",
    "lead:atlas-esphome-kogan-smarterhome-smart-plug-with-energy-meter",
    "lead:atlas-esphome-lsc-led-filament-smart-3200074",
]


MOBILE_PROJECTS = {
    "project-lead:ava-pro": ("master", 4, 4, 4),
    "project-lead:freekiosk": ("main", 4, 4, 4),
    "project-lead:kiosk-satellite": ("main", 3, 4, 4),
    "project-lead:kite-aos": ("development", 2, 3, 3),
    "project-lead:linux-deploy": ("master", 3, 4, 4),
    "project-lead:marathon-shell": ("main", 2, 3, 3),
    "project-lead:maru-os": ("master", 2, 3, 4),
    "project-lead:scrcpy": ("master", 5, 5, 5),
    "project-lead:webview-kiosk": ("main", 4, 4, 4),
}


MOBILE_BUILDS = {
    "lead:jelloid-android-jellyfin": (3, 3, 4),
    "lead:old-tablet-ha-panel": (4, 3, 4),
    "lead:original-ipad-cm4": (2, 3, 3),
    "lead:dlt-one-modular-tablet": (2, 3, 3),
    "lead:basic-phone-remote-switch": (3, 3, 3),
    "lead:phoneblox-modular-phone": (2, 3, 3),
    "lead:nokia-n97-cyberdeck": (2, 3, 3),
}


MOBILE_UNRATED = {
    "lead:postmarketos-nura": (
        None,
        "上游下载页能证明 postmarketOS 路线存在，但未单独证明标题中的 Nura 适配；本轮只记录文档与潜在用途，不推断具体型号可安装。",
        "The upstream download page establishes the postmarketOS route but does not independently prove the title's Nura compatibility; this pass records documentation and potential use without inferring model installability.",
    ),
    "lead:atlas-pmos-casio-g-zone-ca201l": (
        "https://wiki.postmarketos.org/wiki/Casio_G%27zOne_%28casio-ca201l%29",
        "设备页明确软件包尚未进入仓库、刷写未测试且多项硬件状态未知；不足以支持实用价值与风险之外的完整评星。",
        "The device page says its package is not in the repositories, flashing is untested, and many hardware states are unknown; that is insufficient for a complete value/risk-backed rating.",
    ),
    "lead:atlas-pmos-chuwi-hi10-plus": (
        "https://wiki.postmarketos.org/wiki/CHUWI_Hi10_Plus_%28chuwi-hi10plus%29",
        "设备页明确该端口已不维护、已移除且标为不能启动；资料足以记录难度与文档状态，但不支持当前可用性评分。",
        "The device page explicitly marks the port unmaintained, removed, and non-booting; it supports difficulty/documentation findings but not a current-utility score.",
    ),
    "lead:atlas-pmos-cmf-by-nothing-phone-1": (
        "https://wiki.postmarketos.org/wiki/CMF_by_Nothing_Phone_1_%28nothing-tetris%29",
        "设备页明确软件包尚未加入仓库，刷写、存储、屏幕、网络等均标为不可用；本轮不把实验记录当成可安装路线。",
        "The device page says no repository package exists and marks flashing, storage, display, and networking broken; this pass does not treat the experiment as an installable route.",
    ),
}


def component(score: int, basis_zh: str, basis_en: str, sources: list[str]) -> dict:
    assert 1 <= score <= 5
    assert sources and all(urlsplit(url).scheme == "https" for url in sources)
    return {
        "score": score,
        "basis_zh": basis_zh,
        "basis_en": basis_en,
        "sources": list(dict.fromkeys(sources)),
    }


def empty_components() -> dict:
    return {key: None for key in COMPONENTS}


def make_entry(record: dict, topic: str, components: dict, note_zh: str, note_en: str) -> dict:
    assert set(components) == set(COMPONENTS)
    urls = sorted({url for value in components.values() if value for url in value["sources"]})
    evidenced = sum(value is not None for value in components.values())
    return {
        "entry_id": record["entry_id"],
        "title_zh": record["title_zh"],
        "title_en": record["title_en"],
        "topic": topic,
        "category": record["category"],
        "checked_at": CHECKED_AT,
        "evidenced_dimensions": evidenced,
        "qualified": evidenced >= 3,
        "note_zh": note_zh,
        "note_en": note_en,
        "components": components,
        "source_checks": [
            {"url": url, "checked_at": CHECKED_AT, "status": "content-reviewed"}
            for url in urls
        ],
    }


def selector_url(profile: str, target: str) -> str:
    return (
        "https://firmware-selector.openwrt.org/"
        f"?version=25.12.6&target={quote(target, safe='')}&id={quote(profile, safe='-_')}"
    )


def build() -> dict:
    directory = json.loads(DIRECTORY_PATH.read_text(encoding="utf-8"))
    records = {item["entry_id"]: item for item in directory["entries"]}
    entries: list[dict] = []

    for entry_id, model in TV_DEVICES:
        record = records[entry_id]
        parts = empty_components()
        parts["feasibility"] = component(
            3,
            f"上游支持表逐名列出 {model}，并提供从 USB/SD 启动及 armbian-install 路径；仍须严格匹配设备树和具体硬件版本。",
            f"The upstream matrix names {model} and documents USB/SD boot plus armbian-install; the exact device tree and hardware revision still have to match.",
            [OPHUB_README, OPHUB_DOCS],
        )
        parts["docs_community"] = component(
            4,
            "上游维护设备矩阵、安装/升级/备份文档和版本化镜像；这些材料可直接核验，但它不是 Armbian 官方 TV 盒支持。",
            "Upstream maintains a device matrix, install/update/backup documentation, and versioned images; these are directly checkable, but this is not official Armbian TV-box support.",
            [OPHUB_README, OPHUB_DOCS, OPHUB_RELEASES],
        )
        parts["practical_value"] = component(
            4,
            "项目把受支持盒子定位为 Debian/Ubuntu 兼容服务器，并记录 Docker、应用服务和软件中心用途。",
            "The project positions supported boxes as Debian/Ubuntu-compatible servers and documents Docker, application services, and its software center.",
            [OPHUB_README],
        )
        parts["risk"] = component(
            2,
            "写入 eMMC 会替换原系统；上游虽提供原 Android 分区备份/恢复和内核回退，仍明确要求先备份且不能消除刷坏风险。",
            "Writing eMMC replaces the stock system; upstream provides Android-partition backup/restore and kernel rollback, but explicitly recommends backup and cannot remove brick risk.",
            [OPHUB_README, OPHUB_DOCS],
        )
        entries.append(make_entry(record, "tv-box", parts, "按上游逐机型矩阵评分；成本未取证。", "Scored against the upstream per-model matrix; cost remains unevidenced."))

    for entry_id, profile, target in NETWORK_DEVICES:
        record = records[entry_id]
        device_selector = selector_url(profile, target)
        parts = empty_components()
        parts["feasibility"] = component(
            3,
            f"OpenWrt 25.12.6 官方发布元数据含配置档 {profile}，固件选择器可定位对应映像；首次安装仍必须遵守该硬件版本的 Info 指引。",
            f"OpenWrt 25.12.6 release metadata contains profile {profile}, and the Firmware Selector resolves its image; first installation still requires the exact hardware revision's Info instructions.",
            [OPENWRT_OVERVIEW, device_selector, OPENWRT_README],
        )
        parts["docs_community"] = component(
            5,
            "官方发布元数据、固件选择器、生成规则和 OpenWrt 主仓库文档形成可复核链路，并指向逐设备安装信息。",
            "Official release metadata, Firmware Selector, its generation rules, and the OpenWrt repository form a checkable chain and point users to per-device installation information.",
            [OPENWRT_OVERVIEW, device_selector, OPENWRT_SELECTOR_DOC, OPENWRT_README],
        )
        parts["practical_value"] = component(
            5,
            "OpenWrt 为该官方配置档提供可写文件系统和软件包管理，可把旧路由器继续用于路由、无线与可扩展网络服务。",
            "OpenWrt gives this official profile a writable filesystem and package management, extending the router for routing, Wi-Fi, and add-on network services.",
            [device_selector, OPENWRT_README],
        )
        entries.append(make_entry(record, "router", parts, "仅按当前官方发布配置档评分；成本和逐机恢复风险未取证。", "Scored only against the current official release profile; cost and model-specific recovery risk remain unevidenced."))

    for entry_id in SMART_HOME_IDS:
        record = records[entry_id]
        device_page = record["source_url"]
        model = record["title_en"].split(":", 1)[0]
        parts = empty_components()
        parts["feasibility"] = component(
            3,
            f"{model} 的逐设备页面给出板型/芯片信息和可复制配置，并由 ESPHome 安装指南覆盖编译与首次写入；实际拆机或接线依型号而定。",
            f"The device-specific page for {model} supplies board/chip information and a usable configuration, while ESPHome's install guide covers compilation and first install; disassembly or wiring remains model-specific.",
            [device_page, ESPHOME_INSTALL],
        )
        parts["docs_community"] = component(
            4,
            "设备目录页保存型号专用配置并链接相关组件，ESPHome 官方站提供持续维护的安装和组件文档。",
            "The device catalog preserves a model-specific configuration and component links, while ESPHome maintains installation and component documentation.",
            [device_page, ESPHOME_INSTALL, ESPHOME_HOME],
        )
        parts["practical_value"] = component(
            4,
            "该型号页面的配置把已列出的开关、灯光或传感功能接入 ESPHome，本地自动化用途具体而可核对。",
            "The model page's configuration exposes its listed switch, light, or sensor functions through ESPHome, giving a concrete and checkable local-automation use.",
            [device_page, ESPHOME_HOME],
        )
        entries.append(make_entry(record, "smart-home", parts, "未用通用假设填补成本或电气/刷写风险。", "Cost and electrical/flashing risk are not filled with generic assumptions."))

    for entry_id, (branch, feasibility, docs, value) in MOBILE_PROJECTS.items():
        record = records[entry_id]
        repo = record["source_url"]
        readme = f"{repo}/blob/{branch}/README.md"
        commits = f"{repo}/commits/{branch}/"
        parts = empty_components()
        parts["feasibility"] = component(
            feasibility,
            "上游 README 给出 Android 端或配套主机的安装、运行与权限前提；分数按步骤完整度与额外系统改动量评定。",
            "The upstream README documents Android-side or companion-host installation, operation, and permission prerequisites; the score reflects step completeness and required system changes.",
            [readme],
        )
        parts["docs_community"] = component(
            docs,
            "项目 README、源码与提交历史可直接核验；文档成熟度按该仓库现有材料而非热度推断。",
            "The project README, source, and commit history are directly checkable; documentation maturity is based on repository material rather than inferred popularity.",
            [repo, readme, commits],
        )
        parts["practical_value"] = component(
            value,
            f"上游明确实现“{record['title_zh']}”所述用途；本轮只评价仓库记录的功能，不扩大到未列出的手机型号。",
            f"Upstream directly implements the use described by “{record['title_en']}”; this pass scores documented functions without extending compatibility to unlisted phone models.",
            [readme],
        )
        entries.append(make_entry(record, "old-phone-tablet", parts, "未找到一致、可比的二手价或逐机恢复资料，成本与风险保留 null。", "No consistent comparable used-price or per-device recovery evidence was found, so cost and risk remain null."))

    for entry_id, (feasibility, docs, value) in MOBILE_BUILDS.items():
        record = records[entry_id]
        source = record["source_url"]
        parts = empty_components()
        parts["feasibility"] = component(
            feasibility,
            "原作者项目页列出主要部件或操作过程；分数反映是否需要换板、焊接、结构加工或持续维护主机。",
            "The creator's project page lists the main parts or procedure; the score reflects board replacement, soldering, enclosure work, or a continuously running host.",
            [source],
        )
        parts["docs_community"] = component(
            docs,
            "来源是原作者教程或项目日志，足以复核设计路径；单一案例不等同广泛型号支持。",
            "The source is the creator's tutorial or project log and is sufficient to review the design path; one build does not establish broad model support.",
            [source],
        )
        parts["practical_value"] = component(
            value,
            f"项目把闲置设备变为“{record['title_zh']}”所述用途，产出明确；评分不把概念演示写成量产方案。",
            f"The project turns idle hardware into the use described by “{record['title_en']}”, a concrete outcome; the score does not present a one-off demonstration as a production recipe.",
            [source],
        )
        entries.append(make_entry(record, "old-phone-tablet", parts, "仅按原作者已公开步骤评分；成本与恢复风险未取得独立证据。", "Scored only from the creator's published process; cost and recovery risk lack independent evidence."))

    for entry_id, (override_url, note_zh, note_en) in MOBILE_UNRATED.items():
        record = records[entry_id]
        source = override_url or record["source_url"]
        parts = empty_components()
        if entry_id == "lead:postmarketos-nura":
            parts["docs_community"] = component(4, "postmarketOS 官方下载页提供设备选择与安装入口，但不能单独证明 Nura 兼容。", "The official postmarketOS download page provides device selection and installation entry points but does not independently establish Nura compatibility.", [source])
            parts["practical_value"] = component(3, "官方路线的目标是让列出的设备运行移动 Linux；标题中的具体组合仍需另证。", "The official route aims to run mobile Linux on listed devices; the title's specific combination still needs separate evidence.", [source])
        else:
            parts["feasibility"] = component(1, note_zh, note_en, [source])
            parts["docs_community"] = component(3, "postmarketOS Wiki 保留逐设备状态、硬件表和贡献者记录，可核对为什么本轮不评星。", "The postmarketOS Wiki preserves per-device status, hardware tables, and contributor records, making the no-rating decision auditable.", [source])
        entries.append(make_entry(record, "old-phone-tablet", parts, note_zh, note_en))

    record = records["project-lead:openepaperlink"]
    source = "https://github.com/OpenEPaperLink/OpenEPaperLink/blob/master/README.md"
    wiki = "https://github.com/OpenEPaperLink/OpenEPaperLink/wiki"
    parts = empty_components()
    parts["feasibility"] = component(3, "上游列出 ESP32、电子价签和 ZBS 刷写器等必需件，并给出接线、AP 与标签固件流程；需要专用硬件和刷写操作。", "Upstream lists the required ESP32, e-paper tags, and ZBS flasher and documents wiring plus AP/tag firmware; dedicated hardware and flashing are required.", [source, wiki])
    parts["docs_community"] = component(5, "仓库提供标签/AP 固件、硬件设计、刷写器、故障排查、Wiki 与自动构建，材料链完整。", "The repository provides tag/AP firmware, hardware designs, flashers, troubleshooting, a wiki, and automated builds, forming a complete documentation chain.", [source, wiki, "https://github.com/OpenEPaperLink/OpenEPaperLink/commits/master/"])
    parts["practical_value"] = component(5, "项目让退役电子货架标签显示自定义内容，并以低功耗接入点管理更新，复用目标明确。", "The project repurposes retired electronic shelf labels for custom content and manages updates through a low-power access point, a clear reuse outcome.", [source])
    parts["risk"] = component(2, "上游说明标签板很小且脆弱、刷写需要专用工具并且不提供保修；错误接线或操作可能造成不可逆硬件损伤。", "Upstream describes the tag boards as tiny and fragile, requires dedicated flashing tools, and offers no warranty; wiring or handling errors can cause irreversible damage.", [source, wiki])
    entries.append(make_entry(record, "e-reader", parts, "唯一剩余未评分的电子纸项目已逐项取证；成本仍缺少可比市场来源。", "The sole remaining unrated e-paper project was reviewed dimension by dimension; cost still lacks comparable marketplace evidence."))

    ids = [entry["entry_id"] for entry in entries]
    assert len(ids) == len(set(ids)) == 100, (len(ids), len(set(ids)))
    for entry in entries:
        current = records[entry["entry_id"]]
        current_score = current["score"]
        assert current_score["score"] is None or current_score.get("batch_id") == "batch-2-v1.20", (
            f"Entry was rated outside this batch: {entry['entry_id']}"
        )
        assert entry["checked_at"] == CHECKED_AT
        assert set(entry["components"]) == set(COMPONENTS)
        for key, value in entry["components"].items():
            if value is None:
                continue
            assert value["basis_zh"] and value["basis_en"] and value["sources"], (entry["entry_id"], key)
            assert all(urlsplit(url).scheme == "https" and urlsplit(url).netloc for url in value["sources"])

    by_category = Counter(entry["category"] for entry in entries)
    qualified_by_category = Counter(entry["category"] for entry in entries if entry["qualified"])
    unrated_by_category = Counter(entry["category"] for entry in entries if not entry["qualified"])
    qualified = sum(entry["qualified"] for entry in entries)
    return {
        "schema_version": "1.0.0",
        "version": "1.20.0",
        "scoring_model": "3.0.0",
        "batch_id": "batch-2-v1.20",
        "checked_at": CHECKED_AT,
        "generated_at": "2026-10-24T00:00:00+08:00",
        "actual_entries": len(entries),
        "qualified_entries": qualified,
        "still_unrated": len(entries) - qualified,
        "scope": ["tv-box", "old-phone-tablet", "smart-home", "e-reader", "router"],
        "counts": {
            "actual_entries": len(entries),
            "qualified_entries": qualified,
            "still_unrated": len(entries) - qualified,
            "by_category": dict(sorted(by_category.items())),
            "qualified_by_category": dict(sorted(qualified_by_category.items())),
            "still_unrated_by_category": dict(sorted(unrated_by_category.items())),
        },
        "policy": {
            "weights": {"feasibility": 25, "cost": 15, "docs_community": 20, "practical_value": 20, "risk": 20},
            "unscored_value": None,
            "minimum_evidenced_dimensions": 3,
            "renormalize_evidenced_weights": True,
            "rounding": "nearest-0.5-half-up",
            "evidence_grade_independent": True,
        },
        "entries": entries,
    }


def fetch_url(url: str) -> tuple[str, int, int]:
    last_error: Exception | None = None
    for attempt in range(3):
        request = Request(url, headers={"User-Agent": "kitagain-source-audit/1.20"})
        try:
            with urlopen(request, timeout=35) as response:
                body = response.read(1_500_000)
                return url, response.status, len(body)
        except Exception as exc:  # pragma: no cover - live network retry
            last_error = exc
            if attempt < 2:
                time.sleep(0.5 * (attempt + 1))
    assert last_error is not None
    raise last_error


def validate_urls(payload: dict) -> None:
    urls = sorted({check["url"] for entry in payload["entries"] for check in entry["source_checks"]})
    failures = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_url, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                _, status, size = future.result()
                if status < 200 or status >= 400 or size == 0:
                    failures.append((url, status, size))
            except Exception as exc:  # pragma: no cover - live network diagnostic
                failures.append((url, type(exc).__name__, str(exc)))
    print(json.dumps({"unique_urls": len(urls), "passed": len(urls) - len(failures), "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-urls", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check_urls:
        validate_urls(payload)
    if not args.validate_only:
        OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
