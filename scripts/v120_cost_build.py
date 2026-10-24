"""Build the evidence-bounded v1.20 cost ledger for the 95 v1.19 rated entries."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY_PATH = ROOT / "data" / "directory.json"
OUTPUT_PATH = ROOT / "data" / "cost-evidence-v120.json"
CHECKED_AT = "2026-10-24"

# Frozen from the v1.19 rated set. This intentionally does not expand when later
# v1.20 enrichment makes additional entries rated.
EXPECTED_IDS = (
    "project:xiaogpt",
    "project:open-xiaoai",
    "project:mi-gpt",
    "project:onju-voice",
    "project:onju-v2",
    "project:wyoming-satellite",
    "project:linux-voice-assistant",
    "project:lineageos",
    "project:ubports",
    "project:termux",
    "project:droidcam",
    "project:deskreen",
    "project:oclp",
    "project:mrchromebox",
    "project:haos",
    "project:openmediavault",
    "project:dietpi",
    "project:openwrt",
    "project:freshTomato",
    "project:libreelec",
    "project:coreelec",
    "project:armbian-tv",
    "project:webos-homebrew",
    "project:rootmytv",
    "project:koreader",
    "project:kindle-carousel",
    "project:kindle-ha",
    "project:kindle-dashboard",
    "project:kindle-phonekit",
    "project:kindle-whoop",
    "project:winterbreak",
    "project:fbink",
    "project:valetudo",
    "project:wirepod",
    "project:openlumi",
    "project:tasmota",
    "project:openbeken",
    "project:esphome",
    "project:openipc",
    "project:dafang",
    "project:thingino",
    "project:frigate",
    "project:squeezelite",
    "project:lyrion",
    "project:rockbox",
    "project:spotify-ipod",
    "project:gadgetbridge",
    "project:infinitime",
    "project:asteroidos",
    "project:batocera",
    "project:lakka",
    "project:bazzite",
    "project:printer-spl3",
    "lead:kirkwood-nas-debian",
    "lead:eink-display-adapter",
    "lead:six-inch-pi-eink",
    "lead:reuse-sony-reader-with-pico",
    "lead:t95z-plus-nas",
    "lead:atlas-enshi-xiaomi-mi-router-ax3000t",
    "lead:atlas-enshi-xiaomi-redmi-router-ax6s",
    "lead:atlas-enshi-xiaomi-mi-router-4a-gigabit-edition",
    "project-lead:cobalt-kobo-sdk",
    "project-lead:freemarkable",
    "project-lead:kfmon",
    "project-lead:kindle-dash-k4nt",
    "project-lead:kobowriter",
    "project-lead:kindle-kpm",
    "project-lead:nickelmenu",
    "project-lead:okreader",
    "project-lead:plato-kobo-reader",
    "project-lead:quill-kobo-reader",
    "project-lead:rekindle",
    "project-lead:remarkable-entware",
    "project-lead:remarkable-hacks",
    "project-lead:remoteink-pocketbook",
    "project-lead:rmkit",
    "project-lead:toltec",
    "project-lead:ultimate-manga-reader",
    "project-lead:adguard-home",
    "project-lead:asuswrt-merlin-ng",
    "project-lead:casaos",
    "project-lead:cockpit",
    "project-lead:cosmos-server",
    "project-lead:easynas",
    "project-lead:freifunk-gluon",
    "project-lead:libremesh-lime-packages",
    "project-lead:mergerfs",
    "project-lead:nethserver-ns8-core",
    "project-lead:openwisp-controller",
    "project-lead:openzfs",
    "project-lead:opnsense-core",
    "project-lead:pfsense",
    "project-lead:restic",
    "project-lead:rockstor",
    "project-lead:runtipi",
)

GBP_USD = 1.1193 / 0.83728
BROWSER_FALLBACK_URLS = [
    "https://www.ebay.co.uk/shop/google-nest-mini-charcoal?_nkw=google+nest+mini+charcoal",
    "https://www.ebay.co.uk/itm/188937323480",
    "https://www.ebay.com/sch/i.html?_nkw=vector+robot+used&_sop=12",
    "https://www.ebay.co.uk/b/bn_7111075346",
    "https://www.digikey.co.uk/en/products/detail/adafruit-industries-llc/5252/15841478",
    "https://www.ebay.com/itm/234786942156",
    "https://www.ebay.com/itm/203884004553",
    "https://www.ebay.co.uk/itm/188545171108",
    "https://www.ebay.co.uk/itm/116690857672",
]


def price_range(
    low: float,
    high: float,
    currency: str,
    market: str,
    scope_zh: str,
    scope_en: str,
    source_urls: list[str],
    items: list[str] | None = None,
) -> dict:
    result = {
        "low": low,
        "high": high,
        "currency": currency,
        "market": market,
        "scope_zh": scope_zh,
        "scope_en": scope_en,
        "source_urls": source_urls,
    }
    if items is not None:
        result["items"] = items
    return result


def default_record(entry_id: str, upstream_url: str) -> dict:
    reason_zh = (
        "未同时找到可比的设备二手成交/在售价格区间，以及覆盖必要改造零件与工具的完整可靠价格篮子；"
        "不以搜索摘要、单个不完整报价或中性分补位。"
    )
    reason_en = (
        "No comparable used-device price range and complete, reliable basket for the required modding parts/tools "
        "were both available; search snippets, single incomplete quotes, and neutral placeholders were not used."
    )
    return {
        "entry_id": entry_id,
        "checked_at": CHECKED_AT,
        "used_price_range": None,
        "modding_cost_range": None,
        "used_price_sources": [],
        "modding_cost_sources": [],
        "cost_score": None,
        "basis_zh": "仅保留能由可访问精确页面直接支持的成本数据；本条证据链不足。",
        "basis_en": "Only costs directly supported by accessible exact pages are retained; this entry's evidence chain is incomplete.",
        "null_reason_zh": reason_zh,
        "null_reason_en": reason_en,
        "assessment_sources": [upstream_url],
    }


def main() -> None:
    directory = json.loads(DIRECTORY_PATH.read_text(encoding="utf-8"))
    by_id = {entry["entry_id"]: entry for entry in directory["entries"]}
    missing = [entry_id for entry_id in EXPECTED_IDS if entry_id not in by_id]
    if missing:
        raise SystemExit(f"Missing frozen v1.19 entries: {missing}")
    if len(EXPECTED_IDS) != 95 or len(set(EXPECTED_IDS)) != 95:
        raise SystemExit("EXPECTED_IDS must contain exactly 95 unique IDs")

    records = [
        default_record(entry_id, by_id[entry_id]["source_url"])
        for entry_id in EXPECTED_IDS
    ]
    records_by_id = {record["entry_id"]: record for record in records}

    nest_used_sources = [
        "https://www.ebay.co.uk/shop/google-nest-mini-charcoal?_nkw=google+nest+mini+charcoal"
    ]
    onju_mod_sources = [
        "https://community.home-assistant.io/t/onju-voice-pcb-group-buy-in-uk/692514?page=4",
        "https://www.ebay.co.uk/itm/188937323480",
        "https://www.pcbway.com/project/shareproject/Onju_Voice_d33625a1.html",
    ]
    onju_used = price_range(
        21.25,
        30.49,
        "GBP",
        "eBay UK active pre-owned asks",
        "Google Nest Mini 第二代完整/带电源实例的商品价；不含运费、税费。",
        "Item prices for complete/power-supplied Google Nest Mini 2nd-gen examples; shipping and taxes excluded.",
        nest_used_sources,
    )
    onju_mod = price_range(
        25.0,
        44.6,
        "GBP",
        "Home Assistant community offer and eBay UK active ask",
        "一块已组装 Onju Voice 替换板：社区 2026 年未使用板报价为两块 50 英镑，eBay 新板在售价 44.60 英镑；不含运费与可复用宿主机。",
        "One assembled Onju Voice replacement board: a 2026 community offer priced two unused boards at GBP 50, while a current eBay new-board ask is GBP 44.60; shipping and a reusable host are excluded.",
        onju_mod_sources,
        items=["1 assembled Onju Voice replacement PCB"],
    )
    for entry_id, project_url in (
        ("project:onju-voice", "https://github.com/justLV/onju-voice"),
        ("project:onju-v2", "https://github.com/justLV/onju-v2"),
    ):
        record = records_by_id[entry_id]
        record.update(
            {
                "used_price_range": onju_used,
                "modding_cost_range": onju_mod,
                "used_price_sources": nest_used_sources,
                "modding_cost_sources": onju_mod_sources,
                "cost_score": 3,
                "basis_zh": (
                    "上游把同一块 Onju Voice 板定义为 Google Nest Mini 第二代的直插替换板。按区间上限合计 75.09 英镑，"
                    f"依 2026-10-23 ECB 交叉汇率折合约 {75.09 * GBP_USD:.2f} 美元，落入 3 分档。"
                ),
                "basis_en": (
                    "Upstream identifies the same Onju Voice board as a drop-in replacement for a 2nd-gen Google Nest Mini. "
                    f"The GBP 75.09 combined upper bound is about USD {75.09 * GBP_USD:.2f} at the 2026-10-23 ECB cross-rate, placing it in band 3."
                ),
                "null_reason_zh": None,
                "null_reason_en": None,
                "assessment_sources": [project_url, *nest_used_sources, *onju_mod_sources],
            }
        )

    dafang_used_sources = ["https://www.ebay.co.uk/b/bn_7111075346"]
    dafang_mod_sources = [
        "https://github.com/EliasKotlyar/Xiaomi-Dafang-Hacks/blob/master/hacks/install_cfw.md",
        "https://www.digikey.co.uk/en/products/detail/adafruit-industries-llc/5252/15841478",
    ]
    dafang = records_by_id["project:dafang"]
    dafang.update(
        {
            "used_price_range": price_range(
                8.54,
                18.07,
                "GBP",
                "eBay UK active pre-owned listings",
                "明确标为 Xiaomi Dafang 的二手在售/竞拍商品价；不含运费。",
                "Item prices for pre-owned listings explicitly named Xiaomi Dafang; shipping excluded.",
                dafang_used_sources,
            ),
            "modding_cost_range": price_range(
                3.64,
                4.368,
                "GBP",
                "DigiKey UK current unit price",
                "上游安装指南建议 512 MB microSD；价格为一张 512 MB 卡的不含/含英国增值税单价，不含运费。",
                "The upstream install guide recommends a 512 MB microSD; prices are the ex-/incl.-UK-VAT unit prices for one 512 MB card, excluding shipping.",
                dafang_mod_sources,
                items=["1 x 512 MB microSD card"],
            ),
            "used_price_sources": dafang_used_sources,
            "modding_cost_sources": dafang_mod_sources,
            "cost_score": 5,
            "basis_zh": (
                "二手相机与指南要求的存储卡上限合计 22.438 英镑，依 2026-10-23 ECB 交叉汇率折合约 "
                f"{22.438 * GBP_USD:.2f} 美元，落入 5 分档。"
            ),
            "basis_en": (
                "The used camera plus the guide-required card has a GBP 22.438 combined upper bound, about "
                f"USD {22.438 * GBP_USD:.2f} at the 2026-10-23 ECB cross-rate, placing it in band 5."
            ),
            "null_reason_zh": None,
            "null_reason_en": None,
            "assessment_sources": [*dafang_used_sources, *dafang_mod_sources],
        }
    )

    router_used_sources = [
        "https://www.ebay.co.uk/itm/188545171108",
        "https://www.ebay.co.uk/itm/116690857672",
    ]
    router_mod_sources = [
        "https://openwrt.org/toh/xiaomi/xiaomi_mi_router_4a_gigabit_edition"
    ]
    router = records_by_id[
        "lead:atlas-enshi-xiaomi-mi-router-4a-gigabit-edition"
    ]
    router.update(
        {
            "used_price_range": price_range(
                9.99,
                40.0,
                "GBP",
                "eBay UK active used asks",
                "明确标为 Xiaomi Mi Router 4A Gigabit Edition 的两条二手商品价；不含运费/进口费，购买前必须核对硬件修订版。",
                "Two used asks explicitly titled Xiaomi Mi Router 4A Gigabit Edition; shipping/import fees excluded, and the hardware revision must be checked before purchase.",
                router_used_sources,
            ),
            "modding_cost_range": price_range(
                0.0,
                0.0,
                "GBP",
                "OpenWrt documented firmware-exploit route",
                "仅指 OpenWrt 文档明确写明“不需要额外硬件”的固件漏洞路径；假定已有电脑和网线，不计可选串口/编程器恢复工具。",
                "This covers only the firmware-exploit route that OpenWrt explicitly says needs no extra hardware; an existing computer and Ethernet cable are assumed, while optional serial/programmer recovery gear is excluded.",
                router_mod_sources,
                items=[],
            ),
            "used_price_sources": router_used_sources,
            "modding_cost_sources": router_mod_sources,
            "cost_score": 4,
            "basis_zh": (
                "兼容修订版的无额外硬件路径成本上限为 40 英镑，依 2026-10-23 ECB 交叉汇率折合约 "
                f"{40 * GBP_USD:.2f} 美元，落入 4 分档；RD05/v3 不兼容警告仍须单独遵守。"
            ),
            "basis_en": (
                "The no-extra-hardware route has a GBP 40 upper bound, about "
                f"USD {40 * GBP_USD:.2f} at the 2026-10-23 ECB cross-rate, placing it in band 4; the separate RD05/v3 incompatibility warning still applies."
            ),
            "null_reason_zh": None,
            "null_reason_en": None,
            "assessment_sources": [*router_used_sources, *router_mod_sources],
        }
    )

    # Useful partial observations are kept without manufacturing a score: both
    # price classes must be complete before cost_score can be non-null.
    wirepod_used_sources = [
        "https://www.ebay.com/sch/i.html?_nkw=vector+robot+used&_sop=12"
    ]
    wirepod = records_by_id["project:wirepod"]
    wirepod.update(
        {
            "used_price_range": price_range(
                120.0,
                140.0,
                "USD",
                "eBay US active pre-owned asks",
                "带充电座并在实例中带方块/收纳配件的 Vector 二手商品价；不含运费。",
                "Used Vector examples including a charging station and, in the cited examples, cube/case accessories; shipping excluded.",
                wirepod_used_sources,
            ),
            "used_price_sources": wirepod_used_sources,
            "basis_zh": "二手 Vector 区间可核验，但 wire-pod 仍需兼容常驻宿主机；上游只证明软件免费，没有完整宿主机成本篮子。",
            "basis_en": "The used Vector range is verifiable, but wire-pod still needs a compatible always-on host; upstream establishes that the software is free, not a complete host-cost basket.",
            "null_reason_zh": "缺少兼容宿主机的可靠完整成本来源，因此改造成本与 cost_score 保持 null。",
            "null_reason_en": "A reliable complete cost source for the compatible host is missing, so modding cost and cost_score remain null.",
            "assessment_sources": [
                "https://github.com/kercre123/wire-pod",
                *wirepod_used_sources,
            ],
        }
    )

    sony_sources = ["https://hackaday.io/project/203430-reuse-e-reader-with-pico"]
    sony = records_by_id["lead:reuse-sony-reader-with-pico"]
    sony.update(
        {
            "used_price_range": price_range(
                20.0,
                20.0,
                "USD",
                "creator-reported Facebook Marketplace purchase",
                "项目作者报告购入一台 20 美元 Sony PRS-700；这是单个已购样本，不外推市场区间。",
                "The creator reports buying one Sony PRS-700 for USD 20; this is one purchased sample and is not generalized into a broader market range.",
                sony_sources,
            ),
            "used_price_sources": sony_sources,
            "basis_zh": "作者的二手购入价可核验，但项目仍在确定额外元件与更大电池，未给出可复核的完整物料价格。",
            "basis_en": "The creator's used purchase price is verifiable, but the project was still determining extra components and a larger battery and provides no checkable complete priced BOM.",
            "null_reason_zh": "缺少完整、已定型且有价格来源的改造物料篮子，因此改造成本与 cost_score 保持 null。",
            "null_reason_en": "No complete, settled, source-priced modding basket is available, so modding cost and cost_score remain null.",
            "assessment_sources": sony_sources,
        }
    )

    t95_used_sources = [
        "https://www.ebay.com/itm/234786942156",
        "https://www.ebay.com/itm/203884004553",
    ]
    t95 = records_by_id["lead:t95z-plus-nas"]
    t95.update(
        {
            "used_price_range": price_range(
                59.64,
                75.0,
                "USD",
                "eBay US active used asks",
                "明确标为 T95Z Plus 的两条二手商品价；不含运费。",
                "Two used asks explicitly titled T95Z Plus; shipping excluded.",
                t95_used_sources,
            ),
            "used_price_sources": t95_used_sources,
            "basis_zh": "T95Z Plus 二手价可核验，但 NAS 路径还需要 microSD 与 USB 存储；容量未定，无法形成完整可靠的改造成本区间。",
            "basis_en": "The used T95Z Plus prices are verifiable, but the NAS route also needs microSD and USB storage; unspecified capacity prevents a complete, reliable modding-cost range.",
            "null_reason_zh": "缺少已定义容量的 microSD 与 NAS 存储完整价格篮子，因此改造成本与 cost_score 保持 null。",
            "null_reason_en": "A complete price basket for defined-capacity microSD and NAS storage is missing, so modding cost and cost_score remain null.",
            "assessment_sources": [
                "https://forum.armbian.com/topic/53474-t95z-plus-second-one-running-great/",
                *t95_used_sources,
            ],
        }
    )

    filled = sum(record["cost_score"] is not None for record in records)
    lacking_source = len(records) - filled
    used_price_filled = sum(record["used_price_range"] is not None for record in records)
    modding_cost_filled = sum(record["modding_cost_range"] is not None for record in records)
    partial_only = sum(
        record["cost_score"] is None
        and (record["used_price_range"] is not None or record["modding_cost_range"] is not None)
        for record in records
    )

    output = {
        "schema_version": "1.0.0",
        "version": "1.20.0",
        "release": "v1.20.0",
        "checked_at": CHECKED_AT,
        "scope_zh": "v1.19 中已有星级的 95 条目录记录；仅精确、可访问页面可作为成本证据。",
        "scope_en": "The 95 directory entries rated in v1.19; only accessible exact pages qualify as cost evidence.",
        "methodology": {
            "rule_zh": "二手设备区间与必要改造零件/工具区间都可靠时才评分；按两者区间上限合计并折算美元：≤30=5，≤75=4，≤150=3，≤300=2，>300=1。缺一类即为 null。运费、税费与未明确的可选设备按各条 scope 说明处理。",
            "rule_en": "A score is assigned only when both the used-device range and required modding-parts/tools range are reliable. Their combined upper bound is normalized to USD: <=30=5, <=75=4, <=150=3, <=300=2, >300=1. If either class is missing, the score is null. Shipping, taxes, and unspecified optional equipment follow each record's scope.",
            "market_prices": "Active asks unless a record explicitly says creator-reported purchase; asking prices are observations, not guaranteed transaction prices.",
            "fx_reference": {
                "date": "2026-10-23",
                "eur_usd": 1.1193,
                "eur_gbp": 0.83728,
                "gbp_usd_cross": round(GBP_USD, 6),
                "sources": [
                    "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-gbp.en.html",
                    "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-usd.en.html",
                ],
            },
        },
        "source_validation": {
            "checked_at": CHECKED_AT,
            "unique_urls": 107,
            "automated_http_200": 98,
            "browser_fallback_verified": len(BROWSER_FALLBACK_URLS),
            "browser_fallback_urls": BROWSER_FALLBACK_URLS,
            "unverified": 0,
            "note_zh": "9 个市场/零件页拒绝自动化请求（HTTP 403），已在浏览器检索/打开回读中逐页确认标题、状态与价格；其余 98 个唯一 URL 自动请求返回 HTTP 200。",
            "note_en": "Nine marketplace/parts pages rejected the automated client with HTTP 403; each title, condition, and price was read back through browser search/open. The other 98 unique URLs returned HTTP 200 to the automated request.",
        },
        "actual_entries": len(records),
        "filled": filled,
        "lacking_source": lacking_source,
        "used_price_filled": used_price_filled,
        "modding_cost_filled": modding_cost_filled,
        "partial_only": partial_only,
        "entries": records,
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output": str(OUTPUT_PATH),
                "actual_entries": len(records),
                "filled": filled,
                "lacking_source": lacking_source,
                "used_price_filled": used_price_filled,
                "modding_cost_filled": modding_cost_filled,
                "partial_only": partial_only,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
