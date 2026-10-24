"""Build bilingual static pages from shared facts and revision-checked translations."""
import collections
import csv
import hashlib
import html
import io
import json
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urlsplit

from scoring import WEIGHTS, build_directory_export, directory_csv, export_json_text, project_leads_csv, score_all
from watchlist_merge import load_watchlist

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
CONFIG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
BASE = CONFIG["base_url"].rstrip("/") + "/"
REPO = CONFIG["repository_url"]
assert urlsplit(BASE).scheme == "https" and not urlsplit(BASE).query and not urlsplit(BASE).fragment
DATA = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
PROJECT_LEAD_DATA = json.loads((ROOT / "data/project-leads.json").read_text(encoding="utf-8"))
PROJECT_LEADS = PROJECT_LEAD_DATA["projects"]
SCORING_EVIDENCE_PATH = ROOT / "data/scoring-evidence.json"
SCORING_EVIDENCE = json.loads(SCORING_EVIDENCE_PATH.read_text(encoding="utf-8")) if SCORING_EVIDENCE_PATH.exists() else {}
SCORING_EVIDENCE_ITEMS = SCORING_EVIDENCE.get("entries", {})
if isinstance(SCORING_EVIDENCE_ITEMS, dict):
    SCORING_EVIDENCE_ITEMS = list(SCORING_EVIDENCE_ITEMS.values())
DEVICE_ATLAS = json.loads((ROOT / "data/device-atlas.json").read_text(encoding="utf-8"))
PROJECT_IMAGE_DATA = json.loads((ROOT / "data/project-images.json").read_text(encoding="utf-8"))
PROJECT_IMAGES = {item["project_id"]: item for item in PROJECT_IMAGE_DATA["entries"]}
HARDWARE_TAG_DATA = json.loads((ROOT / "data/hardware-tags.json").read_text(encoding="utf-8"))
PROJECT_HARDWARE_TAGS = HARDWARE_TAG_DATA["projects"]
LEAD_HARDWARE_TAGS = HARDWARE_TAG_DATA["leads"]
DEEP = json.loads((ROOT / "data/deep-dives.json").read_text(encoding="utf-8"))
EN = json.loads((ROOT / "data/i18n/en.json").read_text(encoding="utf-8"))
DEEP_EN = json.loads((ROOT / "data/i18n/deep-dives.en.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
DATE = DATA["compiled_at"][:10]
ATLAS_DATE = DEVICE_ATLAS["reviewed_at"][:10]
CONTENT_DATE = max(DATE, ATLAS_DATE)
PROJECT_LEAD_DATE = PROJECT_LEAD_DATA["published_at"]
CONTENT_DATE = max(CONTENT_DATE, PROJECT_LEAD_DATE)
SCORING_DATES = [
    value[:10]
    for value in [
        SCORING_EVIDENCE.get("checked_at"),
        *(entry.get("checked_at") for entry in SCORING_EVIDENCE_ITEMS),
    ]
    if value
]
SCORING_DATE = max(SCORING_DATES) if SCORING_DATES else CONTENT_DATE
CONTENT_DATE = max(CONTENT_DATE, SCORING_DATE)
LABELS_EN = {
    "category": dict(zip(DATA["labels"]["category"], ["Speakers & voice","Phones & tablets","Computers & thin clients","Routers & NAS","TVs & TV boxes","E-readers & e-ink","Robots","Smart home","Cameras","Music & audio","Watches & wearables","Gaming","Printers & peripherals"])),
    "ai": {"native":"AI functionality","assisted":"AI-assisted development/setup","adjacent":"AI-adjacent uses","infrastructure":"Traditional reuse infrastructure"},
    "difficulty": {"easy":"Beginner","medium":"Intermediate","high":"Advanced"},
    "evidence": {"E0":"Candidate / insufficient evidence","E1":"Source code & deployment docs","E2":"Author hardware claim / demonstration","E3":"Independent reproduction verified"},
    "maintenance": {"not-archived":"Repository not archived","archived":"Archived","deprecated":"Maintenance ended by author","moved":"Moved / old mirror archived","historical-patched":"Historical / vulnerability patched","stale":"No push for over a year (not proof of abandonment)"},
}
USES = [
    ("voice-assistant","语音助手","Voice assistant"),("linux-terminal","Linux终端","Linux terminal"),
    ("information-display","信息屏","Information display"),("second-screen","副屏","Second screen"),
    ("retro-gaming","复古游戏","Retro gaming"),("media-center","媒体中心","Media center"),
    ("storage-server","存储服务器","Storage server"),("home-server","家庭服务器","Home server"),
    ("conversation","对话终端","Conversation endpoint"),("app-extension","应用扩展","App extension"),
    ("camera","摄像头","Camera"),("smart-home","智能家居","Smart home"),
    ("gaming-os","游戏系统","Gaming OS"),("offline-control","离线控制","Offline control"),
    ("os-life-extension","系统延寿","OS life extension"),("networking","网络设备","Networking"),
    ("video-analysis","视频分析","Video analysis"),("reading","阅读扩展","Reading"),
    ("music","音乐播放","Music playback"),("driver-repair","驱动修复","Driver repair"),
]
USE_IDS = {zh: uid for uid, zh, en in USES}

def repository_owner_account(repo_url):
    """Return the repository owner page without claiming that it is a sole-author profile."""
    parsed = urlsplit(repo_url or "")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    host = parsed.netloc.lower()
    if host == "github.com":
        platform = "GitHub"
    elif host == "codeberg.org":
        platform = "Codeberg"
    else:
        return None
    owner = parts[0]
    return {
        "name": owner,
        "platform": platform,
        "url": f"{parsed.scheme}://{parsed.netloc}/{owner}",
    }
REQS = {
    "yes":("需要","Required"),"no":("不需要","Not required"),"UNKNOWN":("待核实","Unknown"),
    "model-dependent":("依具体型号","Model-dependent"),"method-dependent":("依具体方法","Method-dependent"),
    "recovery-dependent":("仅恢复过程可能需要","May be needed for recovery"),
    "storage-dependent":("依存储安装方式","Depends on storage installation"),
    "assembly-dependent":("依组装方案","Depends on assembly"),
    "accessory-dependent":("依配件方案","Depends on accessories"),
    "optional":("可选","Optional"),"no-at-runtime":("运行时不需要","Not required at runtime"),
    "no-for-supported-workflows":("文档支持路径不需要","Not required for documented supported workflows"),
    "no-in-documented-USB-route":("文档 USB 路径不需要","Not required in the documented USB route"),
    "no-local-server-possible":("可使用本地服务","Local server is possible"),
    "no-for-core-detection":("核心检测不需要","Not required for core detection"),
    "optional-integrations":("依可选集成","Depends on optional integrations"),
    "optional-content-services":("依可选内容服务","Depends on optional content services"),
    "optional-external-model":("外部模型服务可选","External model service optional"),
    "optional-knowledge-provider":("知识服务可选","Knowledge service optional"),
    "optional-music-services":("音乐服务可选","Music services optional"),
    "optional-game-platforms":("游戏平台可选","Game platforms optional"),
    "optional-sync":("同步服务可选","Sync optional"),
    "required-whoop":("需要 WHOOP 服务","WHOOP service required"),
    "required-spotify":("需要 Spotify 服务","Spotify service required"),
    "required-xiaomi":("需要小米服务","Xiaomi service required"),
    "required-xiaomi; optional-model-provider":("需要小米服务；模型云服务可选","Xiaomi service required; model cloud service optional"),
    "depends-on-displayed-services":("依展示的数据服务","Depends on the displayed data services"),
    "LX06: yes; OH2P: no（按官方教程）":("LX06：需要；OH2P：不需要（按官方教程）","LX06: required; OH2P: not required (official instructions)"),
}
LICENSE_EN = {
    "AGPL-3.0（含 GPL-3.0 / MIT 文件例外）":"AGPL-3.0 (GPL-3.0 / MIT file exceptions)",
    "BSD 4-clause style / 自定义署名条款":"BSD 4-clause style / custom attribution terms",
    "GPL-2.0-only（含其他组件许可证）":"GPL-2.0-only (other component licenses also apply)",
    "GPL-2.0（README 声明；上游组件分别授权）":"GPL-2.0 (README declaration; upstream components separately licensed)",
    "GPL-3.0-only（含文件例外）":"GPL-3.0-only (file exceptions)",
    "GPL-3.0-or-later + OpenSSL 例外 / 其他组件":"GPL-3.0-or-later + OpenSSL exception / other components",
    "GPL-3（除另有声明文件）":"GPL-3 (except files stating otherwise)",
    "MIT + GPL-3.0（按代码类型）":"MIT + GPL-3.0 (by code type)",
    "混合：Perl GPL-2.0；固件/资产另有条款":"Mixed: Perl GPL-2.0; firmware/assets have separate terms",
}
RISKS = {"possible":("可能发生","Possible"),"expected":("预计会发生","Expected"),
         "not-expected":("按此路径预计不会发生","Not expected for this route"),
         "workflow-dependent":("依操作路径","Workflow-dependent")}
SOURCE_KINDS = {
    "upstream-document":("上游项目文档","Upstream documentation"),
    "official-compatibility-or-install":("官方适配或安装文档","Official compatibility / installation"),
    "ai-setup-doc":("AI 辅助设置文档","AI-assisted setup documentation"),
    "author-process":("作者过程记录","Author process record")}
PATHS = []
SCORE_FILTER_VALUES = [step / 2 for step in range(2, 11)]


def score_text(value):
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def score_filter_options():
    return "".join(f'<option value="{score_text(value)}">≥ {score_text(value)}/5</option>' for value in SCORE_FILTER_VALUES)


def score_sort_key(record, title):
    """Rated entries first, descending; unrated entries last, then title."""
    value = record["score"]
    return (value is None, -(value or 0), title.casefold())


def score_data_value(record):
    return "" if record["score"] is None else score_text(record["score"])

def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def h(value):
    return html.escape(str(value))

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def ul(values, css_class=""):
    attr = f' class="{h(css_class)}"' if css_class else ""
    return f"<ul{attr}>" + "".join(f"<li>{h(v)}</li>" for v in values) + "</ul>"

def localized(p, lang):
    if lang == "en":
        return EN["projects"][p["id"]]
    return dict(summary=p["summary_zh"], device_scope=p["device_scope"], limitations=p["limitations"],
                evidence_reason=p["evidence"]["reason"], recovery=p["risk"]["recovery"],
                cost_items=p["cost"]["items"], method=p["method"],
                firmware_requirement=p["firmware_requirement"], region_requirement=p["region_requirement"])

class Site:
    def __init__(self, lang):
        self.lang = lang
        self.labels = LABELS_EN if lang == "en" else DATA["labels"]

    def t(self, zh, en):
        return zh if self.lang == "zh" else en

    def rel(self, target, current):
        return posixpath.relpath(target, posixpath.dirname(current) or ".")

    def page(self, title, description, body, tail="index.html", legacy=None):
        current = legacy or f"{self.lang}/{tail}"
        canonical = BASE if self.lang == "en" and tail == "index.html" else BASE + f"{self.lang}/" + ("" if tail == "index.html" else tail.removesuffix("index.html"))
        other = "en" if self.lang == "zh" else "zh"
        target = f"{other}/{tail}"
        rel = lambda x: self.rel(x, current)
        footer_about = rel(self.lang + "/about/index.html")
        display_brand = self.t("垃圾佬复活站", "KitAgain")
        title_brand = self.t("垃圾佬复活站 · KitAgain", "KitAgain")
        alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{BASE if lang == "en" and tail == "index.html" else BASE+lang+"/"+("" if tail == "index.html" else tail.removesuffix("index.html"))}">' for lang,code in [("zh","zh-CN"),("en","en")])
        alternates += f'<link rel="alternate" hreflang="x-default" href="{BASE}">'
        markup = f"""<!doctype html>
<html lang="{self.t('zh-CN','en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)} · {title_brand}</title><meta name="description" content="{h(description)}">
<link rel="canonical" href="{h(canonical)}">{alternates}<meta name="theme-color" content="#f7f7f5">
<meta property="og:title" content="{h(title)} · {title_brand}"><meta property="og:description" content="{h(description)}"><meta property="og:url" content="{h(canonical)}"><meta property="og:type" content="website">
<link rel="icon" href="{rel('assets/mark.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{rel('assets/style.css')}?v={h(CONFIG['version'])}"><script src="{rel('assets/app.js')}?v={h(CONFIG['version'])}" defer></script>
</head><body><a class="skip" href="#main">{self.t('跳到正文','Skip to content')}</a>
<header class="site-header"><a class="brand" href="{rel(self.lang+'/index.html')}"><span class="brand-mark">↻</span><span>{display_brand}</span></a>
<nav aria-label="{self.t('主导航','Main navigation')}"><a href="{rel(self.lang+'/directory/index.html')}">{self.t('全部路线','All routes')}</a><a href="{rel(self.lang+'/about/index.html')}">{self.t('关于','About')}</a><a href="{h(CONFIG['community_url'])}">{self.t('社区','Community')}</a><a class="language-switch" href="{rel(target)}" lang="{other}" hreflang="{other}">{self.t('English','简体中文')}</a></nav></header>
<main id="main">{body}</main><footer><nav class="footer-links" aria-label="{self.t('页脚链接','Footer links')}"><a href="{footer_about}">{self.t('关于','About')}</a><span aria-hidden="true"> · </span><a href="{footer_about}#downloads">{self.t('数据下载','Data download')}</a><span aria-hidden="true"> · </span><a href="{REPO}">GitHub</a><span aria-hidden="true"> · </span><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></nav></footer></body></html>"""
        write(OUT / current, markup)
        if not legacy:
            PATHS.append(f"{self.lang}/" + ("" if tail == "index.html" else tail.removesuffix("index.html")))

    def link(self, url, text):
        return f'<a href="{h(url)}">{h(text)}</a>' if url else h(text) + self.t("（无已核验链接）"," (no verified link)")

    def tags(self, p):
        return '<div class="tags">' + "".join(f"<span>{h(v)}</span>" for v in [
            self.labels["category"][p["category"]], self.labels["ai"][p["ai_relation"]],
            self.labels["difficulty"][p["difficulty"]], p["evidence"]["level"]]) + "</div>"

    def rating(self, record, compact=True):
        label = record["label_zh" if self.lang == "zh" else "label_en"]
        disclaimer = record["disclaimer_zh" if self.lang == "zh" else "disclaimer_en"]
        css = "card-rating" if compact else "detail-rating"
        if record["score"] is None:
            marker = self.t("待评分", "Not yet rated")
            accessible = self.t(f"复活星级：{marker}", f"Revival stars: {marker}")
            return f'<div class="{css} unrated" title="{h(disclaimer)}" aria-label="{h(accessible)}"><strong>{h(marker)}</strong></div>'
        return f'<div class="{css}" title="{h(disclaimer)}" aria-label="{h(self.t("复活星级", "Revival stars"))}: {score_text(record["score"])} / 5"><strong>★ {score_text(record["score"])}/5</strong>{f"<small>{h(label)}</small>" if not compact else ""}</div>'

    def rating_detail(self, record, method_href=None):
        reason = record["reason_zh" if self.lang == "zh" else "reason_en"]
        evidence_count = self.t(
            f'{record["evidenced_dimensions"]}/5 个维度有可核验来源',
            f'{record["evidenced_dimensions"]}/5 dimensions have verifiable sources',
        )
        provisional = f'<span class="needs-review">{self.t("待验证", "To verify")}</span>' if record["provisional"] else ""
        return f'''<section class="detail-score" aria-label="{self.t('复活星级','Revival stars')}">{provisional}{self.rating(record, compact=False)}<ul><li>{h(evidence_count)}</li><li>{h(reason)}</li></ul></section>'''

    def evidence_tag(self, level, needs_review=False):
        suffix = f' · {self.t("待验证", "To verify")}' if needs_review else ""
        label = self.labels["evidence"].get(level, level)
        return f'<span class="evidence-tag" title="{h(label)}">{h(level + suffix)}</span>'

    def hardware_tags(self, values, base, anchor):
        label = self.t("适配硬件", "Hardware")
        links = "".join(
            f'<a class="hardware-tag" href="{h(base)}?q={quote(value, safe="")}#{h(anchor)}">{h(value)}</a>'
            for value in values
        )
        return f'<div class="hardware-tags" aria-label="{label}"><span>{label}</span>{links}</div>'

    def project_hardware_tags(self, p, base, anchor="catalog"):
        values = [item[self.lang] for item in PROJECT_HARDWARE_TAGS[p["id"]]]
        return self.hardware_tags(values, base, anchor)

    def lead_hardware_values(self, slug, lead):
        if slug in LEAD_HARDWARE_TAGS:
            return [item[self.lang] for item in LEAD_HARDWARE_TAGS[slug]]
        values = []
        for value in [lead.get("device_model"), lead.get("device_name")]:
            if value and value not in values:
                values.append(value)
        return values

    def card_image(self, p, prefix=""):
        image = PROJECT_IMAGES.get(p["id"])
        if not image:
            return ""
        alt = image["alt_zh" if self.lang == "zh" else "alt_en"]
        src = f'{prefix}../{image["local_file"]}'
        return f'<a class="project-thumb {h(image["fit"])}" href="{prefix}projects/{p["id"]}/"><img src="{h(src)}" alt="{h(alt)}" loading="lazy" decoding="async"></a>'

    def detail_image(self, p, current):
        image = PROJECT_IMAGES.get(p["id"])
        if not image:
            return ""
        alt = image["alt_zh" if self.lang == "zh" else "alt_en"]
        caption = image["caption_zh" if self.lang == "zh" else "caption_en"]
        source_label = self.t("查看图片来源", "View image source")
        return f'''<figure class="project-media {h(image["fit"])}"><img src="{h(self.rel(image["local_file"], current))}" alt="{h(alt)}" decoding="async"><figcaption>{h(caption)} <a href="{h(image["source_page"])}">{source_label} ↗</a></figcaption></figure>'''

    def card(self, p, prefix=""):
        e = localized(p, "en")
        v = localized(p, self.lang)
        score = PROJECT_SCORES[p["id"]]
        attrs = {"id":p["id"],"category":p["category"],"ai":p["ai_relation"],"difficulty":p["difficulty"],"evidence":p["evidence"]["level"],"score":score_data_value(score),"rated":str(score["score"] is not None).lower(),"kind":"reviewed-project","title":p["name"],"use":"|".join(USE_IDS[u] for u in p["use_cases"])}
        hardware_values = [item[self.lang] for item in PROJECT_HARDWARE_TAGS[p["id"]]]
        search = " ".join([p["name"], p["summary_zh"], p["device_scope"], e["summary"], e["device_scope"], *p["keywords"], *p["model_examples"], *hardware_values, *p["use_cases"], *(en for uid,zh,en in USES if zh in p["use_cases"])])
        attrs["search"] = search
        attr = " ".join(f'data-{k}="{h(v)}"' for k,v in attrs.items())
        return f"""<article class="project" {attr}><h3><a href="{prefix}projects/{p['id']}/">{h(p['name'])}</a></h3><p class="card-outcome" title="{h(v['summary'])}">{h(v['summary'])}</p><div class="card-meta">{self.rating(score)}{self.evidence_tag(p['evidence']['level'])}</div></article>"""

    def lead_card(self, slug, lead, prefix="leads/"):
        v = lead[self.lang]
        decision = WATCHLIST_DETAILS[slug][self.lang]
        evidence = lead.get("evidence_level", "E0")
        score = LEAD_SCORES[slug]
        platform = lead["source_platform"]
        if self.lang == "en":
            platform = {"恩山无线论坛":"Enshan Wireless Forum", "ophub 中文项目文档":"ophub Chinese documentation"}.get(platform, platform)
        search = " ".join([v["title"], v["summary"], lead.get("device_name", ""), lead.get("device_model", ""), *self.lead_hardware_values(slug,lead), platform, lead.get("discovery_channel", "")])
        attrs = f'data-search="{h(search)}" data-title="{h(v["title"])}" data-category="{h(lead["category"])}" data-source="{h(platform)}" data-evidence="{h(evidence)}" data-score="{score_data_value(score)}" data-rated="{str(score["score"] is not None).lower()}" data-kind="device-or-community-route" data-channel="{h(lead.get("discovery_channel", "legacy"))}"'
        return f"""<article class="project" {attrs}><h3><a href="{prefix}{slug}/">{h(v['title'])}</a></h3><p class="card-outcome" title="{h(v['summary'])}">{h(v['summary'])}</p><div class="card-meta">{self.rating(score)}{self.evidence_tag(evidence)}</div></article>"""

    def project_lead_card(self, lead, prefix="project-leads/"):
        score = PROJECT_LEAD_SCORES[lead["id"]]
        summary = lead["summary_zh" if self.lang == "zh" else "summary_en"]
        device_scope = lead["device_scope_zh" if self.lang == "zh" else "device_scope_en"]
        use_case = lead["use_case_zh" if self.lang == "zh" else "use_case_en"]
        search = " ".join([
            lead["name"], lead["github_description"] or "", lead["summary_zh"], lead["summary_en"],
            lead["device_scope_zh"], lead["device_scope_en"], lead["use_case_zh"], lead["use_case_en"],
        ])
        attrs = (
            f'data-search="{h(search)}" data-title="{h(lead["name"])}" '
            f'data-category="{h(lead["category"])}" data-evidence="E0" '
            f'data-score="{score_data_value(score)}" data-rated="{str(score["score"] is not None).lower()}" data-kind="project-source-lead" data-needs-review="true"'
        )
        return f'''<article class="project" {attrs}><h3><a href="{h(prefix+lead['id']+'/')}">{h(lead['name'])}</a></h3><p class="card-outcome" title="{h(use_case)}">{h(use_case)}</p><div class="card-meta">{self.rating(score)}{self.evidence_tag("E0", needs_review=True)}</div></article>'''

    def home(self):
        t = self.t
        categories = [
            ("ereader", "▤", t("电子书", "E-readers")),
            ("network", "∿", t("路由器", "Routers")),
            ("computer", "▣", t("小电脑", "Mini PCs")),
            ("speaker", "◉", t("智能音箱", "Speakers")),
            ("tv", "▰", t("电视盒", "TV boxes")),
            ("smarthome", "⌂", t("智能家居", "Smart home")),
        ]
        category_links = "".join(
            f'<a class="category-entry" href="directory/?category={key}"><span class="category-icon" aria-hidden="true">{icon}</span><span>{h(label)}</span></a>'
            for key, icon, label in categories
        )
        body = f'''<section class="home-hero"><h1>{t("让旧设备重新上岗", "Give old hardware another job")}</h1><p class="home-subtitle">{t("输入设备，找到它的下一份工作。", "Find its next practical job.")}</p><form id="home-search" class="home-search" action="directory/" method="get" role="search"><label class="visually-hidden" for="home-q">{t("搜索设备", "Search devices")}</label><input id="home-q" name="q" type="search" placeholder="{t("输入你的设备", "Enter your device")}" autocomplete="off"><button type="submit">{t("搜索", "Search")}</button></form><nav class="popular-categories" aria-label="{t('热门分类','Popular categories')}">{category_links}</nav></section>'''
        self.page(t("旧设备别急着扔，让它重新上岗","Give old hardware another job"),t("按设备和型号寻找旧硬件改造路线，快速了解能做什么、适配条件和停止条件。","Find a practical reuse route for old hardware, with clear outcomes, compatibility checks and stop conditions."),body)

    def detail(self, p, legacy=False):
        t = self.t
        v = localized(p, self.lang)
        d = (DEEP_EN if self.lang == "en" else DEEP).get(p["id"])
        current = f"projects/{p['id']}.html" if legacy else f"{self.lang}/projects/{p['id']}/index.html"
        rel = lambda x: self.rel(x, current)
        project_media = self.detail_image(p, current)
        use_labels = [t(zh, en) for uid, zh, en in USES if zh in p["use_cases"]]
        outcome_list = ul(use_labels, "detail-list")
        extra = ""
        if d:
            extra = f'''<section id="analysis"><h2>{t("实际选择依据","Practical decision notes")}</h2><ul class="detail-list"><li><b>{t("原来卡在哪里","What was holding it back")}</b> {h(d["before"])}</li><li><b>{t("改完能做什么","What it can do afterwards")}</b> {h(d["after"])}</li><li><b>{t("判断依据","Assessment")}</b> {h(d["analysis"])}</li><li><b>{t("适合你，如果","A good fit if")}</b> {h(d["fit"])}</li><li><b>{t("先别选，如果","Skip this route if")}</b> {h(d["not_fit"])}</li></ul><h3>{t("完成后检查","Checks after the build")}</h3>{ul(d["acceptance"], "detail-list")}</section>'''
        source_notes = {
            "upstream-document": t("先用它了解项目能做什么、怎样开始，以及作者写明的限制。", "Use this to understand the outcome, how to start and the limits stated by the project."),
            "official-compatibility-or-install": t("动手前用它核对准确型号、固件版本和安装步骤。", "Use this before starting to check the exact model, firmware and installation steps."),
            "ai-setup-doc": t("这里说明 AI 工具参与了哪些设置步骤，不代表设备在本地运行模型。", "This explains where AI assisted setup; it does not mean the model runs on the device."),
            "author-process": t("作者在这里记录了实际制作过程、取舍或结果。", "The author records the build process, trade-offs or result here."),
        }
        sources = "".join(f'<li><div class="resource-head">{self.link(s["url"],t(*SOURCE_KINDS[s["kind"]])+" ↗")}<span>{s["checked_at"][:10]}</span></div><span class="resource-note">{h(source_notes[s["kind"]])}</span><small>{h(s["url"])}</small></li>' for s in p["sources"])
        sources += "".join(f'<li><div class="resource-head">{self.link(s["url"],t("作者的 X 原帖 ↗","Original author X post ↗"))}<span>X</span></div><span class="resource-note">{t("用于补看作者展示的设备和过程；视频画面未当作已核验结果。","Useful for the device and process shown by the author; video frames were not treated as verified results.")}</span><small>{h(s["url"])}</small></li>' for s in p["x_sources"])
        license_label = p["license"]["label"] if self.lang=="zh" else LICENSE_EN.get(p["license"]["label"],p["license"]["label"])
        types = {"case":t("具体改造路线","Specific modification route"),"platform":t("平台 / 多机型工程","Platform / multi-device project"),"prerequisite":t("前置工具","Prerequisite tool")}
        socials = AUTHOR_SOCIALS.get(p["id"], [])
        repo_owner = repository_owner_account(p["repo_url"])
        identity_links = ""
        if repo_owner:
            identity_links += f'<li>{self.link(repo_owner["url"], repo_owner["name"]+" · "+repo_owner["platform"]+" ↗")}<span class="muted"> — {t("源码仓库所有者账号；不据此推断其为唯一作者","Source-repository owner account; this does not establish sole authorship")}</span></li>'
        identity_links += "".join(f'<li>{self.link(item["url"], item["name"]+" · "+item["platform"]+" ↗")}<span class="muted"> — {h(item[self.lang+"_role"])}</span></li>' for item in socials)
        social_section = f'<section><h2>{t("项目账号与已核实作者主页","Project identity and verified author profiles")}</h2><ul class="sources detail-list">{identity_links}</ul></section>' if identity_links else ""
        requirements = [
            (t("改造方法", "Method"), v["method"]),
            (t("上手难度", "Difficulty"), self.labels["difficulty"][p["difficulty"]]),
            (t("拆机", "Disassembly"), t(*REQS[p["requirements"]["disassembly"]])),
            (t("焊接", "Soldering"), t(*REQS[p["requirements"]["soldering"]])),
            (t("云 API / 服务", "Cloud API / service"), t(*REQS[p["requirements"]["cloud_api"]])),
            (t("成本", "Cost"), t("待核价 / UNKNOWN", "Not priced / UNKNOWN")),
        ]
        requirement_items = "".join(f'<li><b>{h(label)}</b> {h(value)}</li>' for label, value in requirements)
        limitation_items = "".join(f'<li><b>{t("停止条件", "Stop condition")}</b> {h(value)}</li>' for value in v["limitations"])
        cost_items = "".join(f'<li><b>{t("可能成本", "Possible cost")}</b> {h(value)}</li>' for value in v["cost_items"])
        body = f"""<div class="detail-wrap record-detail"><a class="back" href="{rel(self.lang+'/directory/index.html')}">← {t('返回全部路线','Back to all routes')}</a><section class="detail-head"><h1>{h(p['name'])}</h1><ul class="detail-list detail-intro"><li>{h(v['summary'])}</li></ul><div class="detail-meta-row">{self.evidence_tag(p['evidence']['level'])}<a class="about-link" href="{rel(self.lang+'/about/index.html')}">{t('了解证据与评分','About evidence and scoring')} ↗</a></div>{self.rating_detail(PROJECT_SCORES[p['id']])}{project_media}</section>
<section><h2>{t('它能变成什么','What it can become')}</h2>{outcome_list}<ul class="detail-list"><li><b>{t('设备范围','Hardware scope')}</b> {h(v['device_scope'])}</li><li><b>{t('设备类别','Category')}</b> {h(self.labels['category'][p['category']])}</li><li><b>{t('AI 关系','AI relationship')}</b> {h(self.labels['ai'][p['ai_relation']])}</li><li><b>{t('路线类型','Route type')}</b> {h(types[p['entry_type']])}</li><li><b>{t('资料最近核对','Sources last checked')}</b> {p['checked_at'][:10]}</li></ul>{self.project_hardware_tags(p,rel(self.lang+'/directory/index.html'),'directory-grid')}</section>
<section><h2>{t('动手前','Before you start')}</h2><ul class="detail-list">{requirement_items}{limitation_items}<li><b>{t('固件','Firmware')}</b> {h(v['firmware_requirement'] or t('待核实','Unknown'))}</li><li><b>{t('地区版本','Region')}</b> {h(v['region_requirement'] or t('待核实','Unknown'))}</li>{cost_items}</ul><ul class="detail-links"><li>{self.link(p['repo_url'],t('项目主页','Project page')+' ↗')}</li><li>{self.link(p['tutorial_url'],t('原始教程','Original guide')+' ↗')}</li><li>{self.link(p['compatibility_url'],t('型号兼容资料','Compatibility source')+' ↗')}</li></ul></section>
<section><h2>{t('风险与恢复','Risk and recovery')}</h2><ul class="detail-list"><li><b>{t('数据丢失风险','Data-loss risk')}</b> {h(t(*RISKS[p['risk']['data_loss']]))}</li><li><b>{t('刷坏 / 无法启动风险','Bricking / boot-failure risk')}</b> {h(t(*RISKS[p['risk']['bricking']]))}</li><li><b>{t('恢复路线','Recovery route')}</b> {h(v['recovery'])}</li><li>{self.link(p['risk']['recovery_url'],t('恢复资料','Recovery guide')+' ↗')}</li></ul></section>{extra}
<section><h2>{t('证据、维护与来源','Evidence, maintenance, and sources')}</h2><ul class="detail-list"><li><b>{p['evidence']['level']} · {h(self.labels['evidence'][p['evidence']['level']])}</b> {h(v['evidence_reason'])}</li><li><b>{t('实机状态','Hands-on status')}</b> {t('KitAgain 未对此设备进行实机测试。','KitAgain has not tested this device hands-on.')}</li><li><b>{t('维护状态','Maintenance')}</b> {h(self.labels['maintenance'][p['maintenance']['status']])}</li><li><b>{t('GitHub 最后 push','Last GitHub push')}</b> {h(p['maintenance']['last_push_at'] or t('待核实','Unknown'))}</li><li><b>{t('仓库许可证','Repository license')}</b> {self.link(p['license']['url'],license_label)}</li><li>{t('近期 push 不证明型号可用；根许可证也不自动覆盖固件、模型、品牌或第三方组件。','A recent push does not prove model compatibility, and a root license does not automatically cover firmware, models, brands, or third-party components.')}</li></ul><ul class="resource-list">{sources}</ul></section>{social_section}</div>"""
        self.page(p["name"]+t("：适配设备与复现条件",": compatibility and reproduction"),v["summary"]+" "+v["device_scope"],body,f"projects/{p['id']}/index.html",current if legacy else None)

    def article(self, title, intro, sections, tail, record=False):
        classes = "detail-wrap record-detail" if record else "detail-wrap"
        intro_markup = f'<ul class="detail-list detail-intro"><li>{h(intro)}</li></ul>' if record else f'<p class="intro">{h(intro)}</p>'
        body = f'<div class="{classes}"><section class="detail-head"><h1>{h(title)}</h1>{intro_markup}</section><section class="prose">{sections}</section></div>'
        self.page(title,intro,body,tail)

    def supporting(self):
        t = self.t
        evidence_counts = DIRECTORY_EXPORT["counts"]["evidence_distribution"]
        about_dimension_rows = "".join(
            f'<tr><td><b>{h(item[self.lang])}</b></td><td>{item["weight"]}%</td></tr>'
            for item in DIRECTORY_EXPORT["dimensions"].values()
        )
        reviewed_catalog_json = "catalog.en.json" if self.lang == "en" else "catalog.json"
        reviewed_catalog_csv = "catalog.en.csv" if self.lang == "en" else "catalog.csv"
        about = f'''<section id="release"><h2>{t("版本与核查状态", "Release and review status")}</h2><ul class="detail-list"><li><b>{t("当前版本", "Current version")}</b> v{CONFIG["version"]}</li><li><b>{t("核查日期", "Review dates")}</b> {t(f"正式目录 {DATE}；设备图谱 {ATLAS_DATE}；项目来源发现层 {PROJECT_LEAD_DATE}。", f"Reviewed catalog {DATE}; device atlas {ATLAS_DATE}; project-source discovery {PROJECT_LEAD_DATE}.")}</li><li><b>{t("实机状态", "Hands-on status")}</b> {t("未进行实机测试。条目收录不等于兼容认证、安全认证或成功保证。", "No hands-on hardware tests. Inclusion is not a compatibility certification, safety certification, or success guarantee.")}</li></ul></section>
<section id="evidence"><h2>{t("证据等级", "Evidence levels")}</h2><ul class="detail-list"><li><b>E0</b> {t("只确认条目和来源的关联，还要核对准确型号、安装与恢复。", "Discovery only; exact model, installation, and recovery still need review.")}</li><li><b>E1</b> {t("已读源码、部署文档或设备兼容资料。", "Source, deployment, or device-compatibility documentation reviewed.")}</li><li><b>E2</b> {t("有作者的实机陈述或演示。", "Author hardware claim or demonstration available.")}</li><li><b>E3</b> {t("有已核验的独立复现。", "Verified independent reproduction available.")}</li></ul><p>{t("证据等级与复活星级独立；它不参与加权，也不限制星级上限。", "Evidence levels are independent of revival stars: they neither enter the weighted score nor cap it.")}</p></section>
<section id="scoring"><h2>{t("复活星级", "Revival stars")}</h2><table class="scoring-weights"><thead><tr><th>{t("维度", "Dimension")}</th><th>{t("权重", "Weight")}</th></tr></thead><tbody>{about_dimension_rows}</tbody></table><ul class="detail-list"><li>{t("每个有可核验来源的维度给 1–5 分；没有证据时保存为 null，不用中性 3 分补位。", "Each source-backed dimension receives 1–5 points; an unevidenced dimension is stored as null, never replaced by a neutral 3.")}</li><li>{t("只在已取证维度之间把原权重按比例重新归一到 100%。", "Only evidenced dimensions have their original weights proportionally renormalized to 100%.")}</li><li>{t("至少 3 个维度有证据才计算总分；否则显示“待评分”，并排在已评分条目之后。", "A total requires at least 3 evidenced dimensions; otherwise it displays ‘Not yet rated’ and sorts after every rated entry.")}</li><li>{t("加权平均四舍五入到最近的 0.5 星，正好落在中点时向上取整。", "The weighted average is rounded to the nearest 0.5 star, with exact ties rounded upward.")}</li></ul></section>
<section id="contribute"><h2>{t("贡献指南", "Contribution guide")}</h2>{ul([t("写明项目 ID、准确型号、硬件修订、固件和地区。", "Include project ID, exact model, hardware revision, firmware, and region."),t("附上源版本、操作日期和原始步骤链接。", "Include upstream revision, operation date, and original instruction links."),t("保留成功、失败、恢复结果和可核验材料。", "Keep successes, failures, recovery outcomes, and verifiable evidence."),t("不要公开唯一序列号、账号、令牌或密钥。", "Do not publish unique serial numbers, accounts, tokens, or secrets.")], "detail-list")}<p><a href="{REPO}/issues/new/choose">{t("提交项目、纠错或复现记录", "Submit a project, correction, or reproduction report")} ↗</a></p></section>
<section id="downloads"><h2>{t("数据下载", "Data download")}</h2><ul class="detail-list"><li><b>{t("全站统一目录", "Full directory")}</b> <a href="../../data/directory.json" download>JSON</a> · <a href="../../data/directory.csv" download>CSV</a></li><li><b>{t("深审项目目录", "Reviewed catalog")}</b> <a href="../../data/{reviewed_catalog_json}" download>JSON</a> · <a href="../../data/{reviewed_catalog_csv}" download>CSV</a></li><li><b>{t("E0 项目来源", "E0 project sources")}</b> <a href="../../data/project-leads.json" download>JSON</a> · <a href="../../data/project-leads.csv" download>CSV</a></li><li><b>{t("评分取证台账", "Scoring evidence ledger")}</b> <a href="../../data/scoring-evidence.json" download>JSON</a></li></ul></section>'''
        self.article(t("关于 KitAgain", "About KitAgain"),t("版本、证据、评分、贡献与数据下载放在一处。", "Release status, evidence, scoring, contribution, and downloads in one place."),about,"about/index.html")
        method = f"""<h2>{t('收录意味着什么','What inclusion means')}</h2><p>{t(f'E0：公开发现条目 {evidence_counts.get("E0", 0)} 条。E1：已读源码、部署文档或设备兼容资料，{evidence_counts.get("E1", 0)} 条。E2：作者实机陈述或演示，{evidence_counts.get("E2", 0)} 条。E3：独立复现，{evidence_counts.get("E3", 0)} 条。本目录实机测试 0 条。',f'E0: {evidence_counts.get("E0", 0)} public discovery entries. E1: source, deployment, or device-compatibility documentation reviewed, {evidence_counts.get("E1", 0)} entries. E2: author hardware claims or demonstrations, {evidence_counts.get("E2", 0)}. E3: verified independent reproduction, {evidence_counts.get("E3", 0)}. Catalog hands-on hardware tests: 0.')}</p>
<h2>{t('我们如何核查','How we review')}</h2><p>{t('以设备和失效原因寻找原始仓库、项目论坛、作者网站、Codeberg、GitLab、Hackaday、Instructables、安装文档、型号表及社交平台原帖。保存来源和核查时间；搜索摘要与转载只作线索。型号、固件、地区未知时保留未知，不把未归档等同持续可用。','We search original repositories, project forums, author sites, Codeberg, GitLab, Hackaday, Instructables, install documentation, model tables and original social posts by device and failure mode. Source URLs and review dates are retained; search snippets and reposts are leads only. Unknown model, firmware or region requirements stay unknown. An unarchived project is not proof of continued usability.')}</p>
<h2>{t('AI 关系与项目家族','AI relationships and project families')}</h2><p>{t('AI 功能改造、AI 辅助开发/配置、AI 周边用途和传统基础设施分开标注。同家族后继版本不是独立复现，平台与前置工具也不是完成的改造案例。','AI functionality, documented AI-assisted development/setup, AI-adjacent uses and traditional infrastructure are separate categories. Successor versions in one family are not independent reproductions; platforms and prerequisite tools are not completed modification cases.')}</p>
<h2>{t('证据的空白','Evidence gaps')}</h2><p>{t('没有长期耗电、稳定性或恢复实测；成本未核价。难度是编辑判断。X 阅读集中于两个案例家族，不声称穷尽搜索或核验视频。','There are no long-term power, stability or recovery tests, and costs are not priced. Difficulty is editorial judgment. X reading covers two case families; neither exhaustive search nor video verification is claimed.')}</p>
<h2>{t('双语同步','Translation discipline')}</h2><p>{t('两种语言共享稳定 ID 与事实字段。译文记录源内容哈希；源文变动后必须复核，不能把翻译日期当作上游重新核查日期。','Both languages share stable IDs and factual fields. Translations record a source-content hash and must be reviewed when the source changes. Translation dates are not fresh upstream verification dates.')}</p><p><a href="../contribute/">{t('贡献方法与核验流程','Contribution and review process')} ↗</a></p>"""
        self.article(t("先看证据，再谈复活。","Evidence before revival."),t("有来源，也明确记录未知项。","Traceable sources and explicit unknowns."),method,"research/index.html")
        contribute = f"""<h2>{t('提交什么','What to include')}</h2>{ul([t('项目 ID、准确型号、硬件修订、固件与地区','Project ID, exact model, hardware revision, firmware and region'),t('上游版本、操作日期及原始步骤链接','Upstream version, operation date and original instructions'),t('成功与失败功能、恢复结果及可核验材料','Working and failed functions, recovery results and verifiable evidence'),t('不要公开设备唯一序列号、账号、令牌或密钥','Do not publish unique serial numbers, accounts, tokens or secrets')])}
<h2>{t('资料如何进入目录','How reports enter the catalog')}</h2><p>{t('提交后先标为待核验。编辑检查来源与型号条件，再同步中英文；没有独立证据就不升级为 E3。失败记录同样有价值。','Submissions begin as unverified. Editors check sources and exact device conditions, then update both languages. No E3 upgrade without independent evidence. Failure reports are valuable too.')}</p><p id="project-context" class="boundary" hidden></p>
<p>{self.link(REPO+'/issues/new/choose',t('向目录提交项目、纠错或复现记录','Submit a project, correction or reproduction report to the catalog'))} ↗</p><p>{self.link(CONFIG['community_url'],t('前往社区论坛交流','Visit the community forum'))} ↗</p><p>{t('论坛已上线，但语言界面、管理流程和发帖功能仍在完善；正式目录纠错继续使用 GitHub Issues。','The forum is online, while interface localization, moderation and posting checks are still in progress. Use GitHub Issues for formal catalog corrections.')}</p>"""
        self.article(t("贡献一份可靠记录","Contribute a reliable record"),t("成功、失败和不支持条件，都值得保留。","Keep successes, failures and unsupported conditions."),contribute,"contribute/index.html")
        categories = [t("求助与问答","Help & Questions"),t("成功与失败复现","Build Reports"),t("项目发现与改进","Projects & Ideas"),t("公告与社区使用","Announcements & Community")]
        community = f"""<aside class="boundary"><b>{t('社区论坛已上线','Community forum is online')}</b><p>{t('论坛目前使用英文界面，版块、审核和发帖流程仍在完善。主站目录可直接阅读，不需要注册。','The forum currently has an English interface; categories, moderation and posting workflows are still being prepared. The catalog remains readable without registration.')}</p><p>{self.link(CONFIG['community_url'],t('进入 KitAgain 社区论坛','Open the KitAgain community forum'))} ↗</p></aside>
<h2>{t('计划建设的四类讨论','Four discussion areas being prepared')}</h2>{ul(categories)}
<h2>{t('中文和英文都欢迎','Chinese and English welcome')}</h2><p>{t('使用你熟悉的语言，注明设备与项目 ID。优质经验经复核后可补充双语摘要。机器翻译需标明并保留原文，用户帖子不会自动成为目录认证。','Use the language you know and identify the device and project ID. Reviewed experience may receive a bilingual summary. Machine translations must be labeled with the original retained. User posts do not automatically become catalog certifications.')}</p>
<h2>{t('社区规则','Community rules')}</h2>{ul([t('尊重他人，讨论具体条件，不伪造成功或身份','Respect others; discuss exact conditions; do not fabricate success or identities'),t('保留来源，说明商业关系，避免无关推广','Keep sources, disclose commercial relationships and avoid unrelated promotion'),t('报告失败时记录版本、现象与恢复情况，不发布秘密或个人信息','When reporting failure, record versions, symptoms and recovery without secrets or personal information')])}
<p id="project-context" class="boundary" hidden></p><p><a id="contribute-link" href="../contribute/">{t('现在提交资料或纠错','Contribute or correct information now')} ↗</a></p>"""
        self.article(t("一起让旧设备继续工作","Keep old devices working together"),t("用可核验的讨论积累经验。","Build experience through verifiable discussion."),community,"community/index.html")
        distribution = DIRECTORY_EXPORT["counts"]["score_distribution"]
        distribution_rows = "".join(
            f'<tr><td><b>{bucket}/5</b></td><td>{distribution[bucket]}</td></tr>'
            for bucket in distribution
        )
        distribution_rows += f'<tr><td><b>{t("待评分", "Not yet rated")}</b></td><td>{DIRECTORY_EXPORT["counts"]["not_yet_rated"]}</td></tr>'
        dimension_rows = "".join(
            f'<tr><td><b>{h(item[self.lang])}</b></td><td>{item["weight"]}%</td></tr>'
            for item in DIRECTORY_EXPORT["dimensions"].values()
        )
        scoring = f'''<aside class="boundary"><b>{t("星级回答什么","What the stars answer")}</b><p>{t("它用于比较一条复活路线的落地条件，不是兼容保证、安全认证或成功率。E0–E3 单独表示来源证据深度，不参与星级加权，也不设置上限。","It compares the conditions for putting a revival route into practice. It is not a compatibility guarantee, safety certification, or success rate. E0–E3 separately describes evidence depth and neither enters nor caps the stars.")}</p></aside>
<h2>{t("五个维度与权重","Five dimensions and weights")}</h2><table><thead><tr><th>{t("维度","Dimension")}</th><th>{t("权重","Weight")}</th></tr></thead><tbody>{dimension_rows}</tbody></table>
<h2>{t("计算方式","Calculation")}</h2><p>{t("每个有可核验来源的维度给 1–5 分。仅将已取证维度的原权重按比例重新归一到 100%，再求加权平均；四舍五入到最近的 0.5 星，正好落在中点时向上取整。","Each source-backed dimension receives 1–5 points. Only the original weights of evidenced dimensions are proportionally renormalized to 100% before averaging. The result is rounded to the nearest 0.5 star, with exact ties rounded upward.")}</p>
<h2>{t("未知项怎样处理","How unknowns are handled")}</h2><p>{t("缺少证据的维度保留为 null，不再用 3 分占位，也不进入分母。少于 3 个维度有证据时，总分和加权平均均为 null，页面显示“待评分”，并排在所有已评分条目之后。","Unevidenced dimensions remain null: no neutral 3 is imputed and their weights do not enter the denominator. With fewer than three evidenced dimensions, both the total and weighted average are null; the page shows “Not yet rated” and sorts the entry after every rated item.")}</p>
<h2>{t("当前半星分布","Current half-star distribution")}</h2><table><thead><tr><th>{t("星级","Stars")}</th><th>{t("当前条数","Current entries")}</th></tr></thead><tbody>{distribution_rows}</tbody></table>
<h2>{t("不会进入评分的因素","What is deliberately excluded")}</h2>{ul([t("E0–E3 证据等级本身","The E0–E3 evidence grade itself"),t("star、点赞、浏览量和搜索热度","Repository stars, likes, views, and search popularity"),t("未经核实的成功率或兼容承诺","Unverified success rates or compatibility promises"),t("把最近 push 直接当成设备可用证明","Treating a recent push as proof that hardware works")])}
<h2>{t("全量覆盖与数据下载","Coverage and downloads")}</h2><p>{t(f"当前 {DIRECTORY_EXPORT['counts']['rated']} / {DIRECTORY_EXPORT['counts']['entries']} 条有星级，{DIRECTORY_EXPORT['counts']['not_yet_rated']} 条待评分。统一 JSON/CSV 保存 nullable 的总分与五项原始分、有效权重、分项依据与来源 URL，以及独立证据等级。",f"{DIRECTORY_EXPORT['counts']['rated']} / {DIRECTORY_EXPORT['counts']['entries']} entries currently have stars; {DIRECTORY_EXPORT['counts']['not_yet_rated']} are not yet rated. Unified JSON/CSV stores nullable totals and raw dimensions, effective weights, per-dimension basis and source URLs, plus the independent evidence grade.")}</p><p><a href="../../data/directory.json" download>JSON</a> · <a href="../../data/directory.csv" download>CSV</a> · <a href="../../data/scoring-evidence.json" download>{t("评分取证台账","Scoring evidence ledger")}</a> · <a href="../directory/">{t("打开全站目录","Open the full directory")} ↗</a></p>'''
        self.article(t("1–5 星复活价值评分","1–5 revival-value stars"),t("只计有证据维度、权重重新归一、证据等级独立。","Source-backed dimensions only, renormalized weights, and independent evidence grades."),scoring,"scoring/index.html")

    def guides(self):
        for gid, guide in GUIDES.items():
            g = guide[self.lang]
            sections = "".join(f"<h2>{h(title)}</h2>{ul(lines)}" for title,lines in g["sections"])
            sections += f'<h2>{self.t("对应项目与来源","Projects and sources")}</h2><div class="project-grid">' + "".join(self.card(next(p for p in PROJECTS if p["id"]==pid),"../../") for pid in guide["projects"])+"</div>"
            self.article(g["title"],g["intro"],sections,f"guides/{gid}/index.html")

    def articles(self):
        for slug, article in ARTICLES.items():
            a = article[self.lang]
            sections = f'<p class="muted">{h(article["content_id"])} · {self.t("资料核查","Sources reviewed")} {h(article["reviewed_at"])} · {self.t("未进行实机测试","No hands-on hardware tests")}</p>'
            if article.get("decision_rows"):
                rows = "".join(
                    f'<tr><td><b>{h(row["hardware"][self.lang])}</b></td><td>{h(row["result"][self.lang])}</td><td>{h(row["route"])}</td><td>{h(row["readiness"][self.lang])}</td><td>{h(row["stop"][self.lang])}</td></tr>'
                    for row in article["decision_rows"]
                )
                sections += f'<h2>{self.t("先用这张表选方向","Choose a route at a glance")}</h2><div class="table-scroll"><table class="decision-table"><thead><tr><th>{self.t("手里的硬件","Hardware")}</th><th>{self.t("可以变成","New job")}</th><th>{self.t("实现路线","Route")}</th><th>{self.t("成熟度","Readiness")}</th><th>{self.t("先停手的情况","Stop when")}</th></tr></thead><tbody>{rows}</tbody></table></div>'
            sections += "".join(f"<h2>{h(title)}</h2>" + "".join(f"<p>{h(paragraph)}</p>" for paragraph in paragraphs) for title,paragraphs in a["sections"])
            sections += f'<h2>{self.t("原始来源","Primary sources")}</h2><ul class="sources">' + "".join(f'<li>{self.link(source["url"],source["label"])}</li>' for source in article["sources"]) + "</ul>"
            sections += f'<h2>{self.t("相关项目","Related projects")}</h2><div class="project-grid">' + "".join(self.card(next(p for p in PROJECTS if p["id"] == pid),"../../") for pid in article["projects"]) + "</div>"
            self.article(a["title"],a["intro"],sections,f"articles/{slug}/index.html")

    def directory(self):
        t = self.t
        all_cards = []
        for project in PROJECTS:
            record = PROJECT_SCORES[project["id"]]
            all_cards.append((*score_sort_key(record, project["name"]), self.card(project, "../")))
        for slug, lead in WATCHLIST.items():
            record = LEAD_SCORES[slug]
            all_cards.append((*score_sort_key(record, lead[self.lang]["title"]), self.lead_card(slug, lead, "../leads/")))
        for lead in PROJECT_LEADS:
            record = PROJECT_LEAD_SCORES[lead["id"]]
            all_cards.append((*score_sort_key(record, lead["name"]), self.project_lead_card(lead, "../project-leads/")))
        all_cards.sort(key=lambda item: item[:3])
        category_options = "".join(f'<option value="{h(key)}">{h(value)}</option>' for key,value in self.labels["category"].items())
        evidence_options = "".join(f'<option value="{level}">{level} · {h(self.labels["evidence"][level])}</option>' for level in ["E0","E1","E2","E3"])
        score_options = score_filter_options()
        counts = DIRECTORY_EXPORT["counts"]
        body = f'''<div class="detail-wrap wide"><section class="detail-head"><p class="eyebrow">ONE INDEX / CLEAR EVIDENCE</p><h1>{t("全部设备与改造记录","All hardware-revival records")}</h1><p class="intro">{t(f"统一检索 {counts['entries']} 条公开记录，来自 {counts['unique_primary_source_urls']} 个不同主来源 URL。其中 200 个是互不重复的项目仓库来源：53 个深审项目加 147 个 E0 发现候选；另有 347 条设备/社区路线。三个分母分别标注，不把同一上游的不同设备型号冒充独立项目。",f"Search {counts['entries']} public records from {counts['unique_primary_source_urls']} distinct primary-source URLs. Exactly 200 are unique project-repository sources: 53 reviewed projects plus 147 E0 discoveries; another 347 are device/community routes. Each denominator stays explicit, and multiple devices from one upstream are not presented as independent projects.")}</p><div class="actions"><a href="../../data/directory.json" download>{t("下载全量 JSON","Download full JSON")}</a><a href="../../data/directory.csv" download>{t("下载全量 CSV","Download full CSV")}</a><a href="../project-sources/">{t("查看 200 个项目来源","Browse 200 project sources")} ↗</a><a href="../about/#scoring">{t("评分方法","Scoring method")} ↗</a></div></section>
<aside class="boundary"><b>{t("星级与证据分开看","Read stars and evidence separately")}</b><p>{t("只对有可核验来源的维度计分，已取证权重重新归一；少于 3 个维度时显示“待评分”并排在已评分条目之后。E0–E3 仍是独立证据标签。","Only source-backed dimensions are scored and their weights are renormalized. Fewer than three dimensions displays “Not yet rated” and sorts after rated entries. E0–E3 remains an independent evidence tag.")}</p></aside>
<form id="directory-filters" class="filters" role="search"><div class="search-field"><label for="directory-q">{t("搜索设备、型号、项目或来源","Search device, model, project, or source")}</label><input id="directory-q" type="search" placeholder="{t('例如 NAS、Kindle、AX3000T、ESPHome…','Try NAS, Kindle, AX3000T, ESPHome…')}" autocomplete="off"></div><div class="filter-grid"><label>{t("设备","Device")}<select id="directory-category"><option value="">{t("全部设备","All devices")}</option>{category_options}</select></label><label>{t("证据","Evidence")}<select id="directory-evidence"><option value="">{t("全部证据","All evidence")}</option>{evidence_options}</select></label><label>{t("最低星级","Minimum stars")}<select id="directory-score"><option value="">{t("不限","Any score")}</option>{score_options}</select></label><label>{t("条目类型","Entry type")}<select id="directory-kind"><option value="">{t("全部类型","All types")}</option><option value="reviewed-project">{t("深审项目","Reviewed project")}</option><option value="project-source-lead">{t("E0 项目来源","E0 project source")}</option><option value="device-or-community-route">{t("设备或社区路线","Device/community route")}</option></select></label><label>{t("排序","Sort")}<select id="directory-sort"><option value="score-desc">{t("星级：高到低","Stars: high to low")}</option><option value="title-asc">{t("名称：A–Z","Name: A–Z")}</option></select></label></div><div class="filter-bottom"><p id="directory-result-count" role="status" aria-live="polite">{t("显示","Showing")} {counts['entries']} / {counts['entries']}</p><div><button type="button" id="directory-share">{t("复制筛选链接","Copy filtered link")}</button><button type="reset">{t("清除筛选","Clear filters")}</button></div></div><span id="directory-share-status" role="status"></span></form>
<div id="directory-grid" class="project-grid">{''.join(item[-1] for item in all_cards)}</div><div id="directory-empty" class="empty" hidden><h3>{t("暂时没有匹配路线","No matching route")}</h3><p>{t("减少一个筛选条件，或换一个设备/型号词。","Remove a filter or try another device/model term.")}</p></div></div>'''
        self.page(t(f"全部 {counts['entries']} 条硬件复活记录",f"All {counts['entries']} hardware-revival records"),t("统一搜索设备、型号、项目、来源、复活星级和独立证据等级。","Search every device, model, project, source, revival-star score, and independent evidence grade."),body,"directory/index.html")

    def project_sources(self):
        t = self.t
        cards = []
        for project in PROJECTS:
            record = PROJECT_SCORES[project["id"]]
            cards.append((*score_sort_key(record, project["name"]), self.card(project, "../")))
        for lead in PROJECT_LEADS:
            record = PROJECT_LEAD_SCORES[lead["id"]]
            cards.append((*score_sort_key(record, lead["name"]), self.project_lead_card(lead, "../project-leads/")))
        cards.sort(key=lambda item: item[:3])
        category_options = "".join(f'<option value="{h(key)}">{h(value)}</option>' for key,value in self.labels["category"].items())
        body = f'''<div class="detail-wrap wide"><section class="detail-head"><p class="eyebrow">200 UNIQUE PROJECT REPOSITORIES</p><h1>{t("200 个独立项目来源","200 independent project sources")}</h1><p class="intro">{t(f"这里按仓库 URL 去重列出 {len(PROJECTS)} 个深审项目与 {len(PROJECT_LEADS)} 个 E0 GitHub 发现候选，合计正好 200 个独立项目来源。E0 只确认仓库存在、非 fork，并读取元数据与 README 入口；不表示具体设备兼容、安装成功或长期稳定。",f"This index deduplicates by repository URL: {len(PROJECTS)} reviewed projects plus {len(PROJECT_LEADS)} E0 GitHub discoveries, exactly 200 independent project sources. E0 confirms that a non-fork repository exists and that its metadata and README entry point were read; it does not establish device compatibility, installation success, or long-term stability.")}</p><div class="actions"><a href="../../data/project-leads.json" download>{t("下载 147 条 E0 JSON","Download 147 E0 JSON")}</a><a href="../../data/project-leads.csv" download>{t("下载 147 条 E0 CSV","Download 147 E0 CSV")}</a><a href="../directory/?kind=project-source-lead">{t("在全站目录只看 E0 项目来源","Show E0 project sources in full directory")} ↗</a></div></section>
<aside class="boundary"><b>{t("两层不能混写","Keep the layers separate")}</b><p>{t("53 个深审项目已读部署或适配来源，证据为 E1/E2；147 个发现候选全部保持 E0。两层都没有 KitAgain 实机测试，E3 仍为 0。","The 53 reviewed projects have deployment or compatibility sources reviewed at E1/E2; all 147 discoveries remain E0. Neither layer has KitAgain hands-on hardware tests, and E3 remains zero.")}</p></aside>
<form id="project-source-filters" class="filters" role="search"><div class="search-field"><label for="project-source-q">{t("搜索项目、设备范围或用途","Search project, hardware scope, or use")}</label><input id="project-source-q" type="search" placeholder="{t('例如 NAS、Kindle、camera、IoT…','Try NAS, Kindle, camera, IoT…')}" autocomplete="off"></div><div class="filter-grid"><label>{t("设备","Device")}<select id="project-source-category"><option value="">{t("全部设备","All devices")}</option>{category_options}</select></label><label>{t("证据","Evidence")}<select id="project-source-evidence"><option value="">{t("全部证据","All evidence")}</option><option value="E0">E0 · {t("发现候选","Discovery")}</option><option value="E1">E1 · {t("资料已读","Source reviewed")}</option><option value="E2">E2 · {t("作者实机证据","Author hardware evidence")}</option></select></label><label>{t("最低星级","Minimum stars")}<select id="project-source-score"><option value="">{t("不限","Any score")}</option>{score_filter_options()}</select></label><label>{t("排序","Sort")}<select id="project-source-sort"><option value="score-desc">{t("星级：高到低","Stars: high to low")}</option><option value="title-asc">{t("名称：A–Z","Name: A–Z")}</option></select></label></div><div class="filter-bottom"><p id="project-source-result-count" role="status" aria-live="polite">{t("显示","Showing")} {len(PROJECTS)+len(PROJECT_LEADS)} / {len(PROJECTS)+len(PROJECT_LEADS)}</p><button type="reset">{t("清除筛选","Clear filters")}</button></div></form>
<noscript><p>{t("JavaScript 未启用；全部 200 个来源仍可阅读并使用浏览器查找。","JavaScript is disabled; all 200 sources remain readable and searchable with browser Find.")}</p></noscript><div id="project-source-grid" class="project-grid">{''.join(item[-1] for item in cards)}</div><div id="project-source-empty" class="empty" hidden><h3>{t("暂时没有匹配项目来源","No matching project source")}</h3><p>{t("减少一个筛选条件，或换一个设备/用途词。","Remove a filter or try another device/use term.")}</p></div></div>'''
        self.page(t("200 个独立项目来源","200 independent project sources"),t("按仓库 URL 去重的硬件复活项目来源，明确区分 E0 发现候选与 E1/E2 深审项目。","Hardware-revival project sources deduplicated by repository URL, with E0 discoveries separated from E1/E2 reviewed projects."),body,"project-sources/index.html")

        for lead in PROJECT_LEADS:
            summary = lead["summary_zh" if self.lang == "zh" else "summary_en"]
            device_scope = lead["device_scope_zh" if self.lang == "zh" else "device_scope_en"]
            use_case = lead["use_case_zh" if self.lang == "zh" else "use_case_en"]
            reason = lead["reason_zh" if self.lang == "zh" else "reason_en"]
            archive_state = t("是；上游仓库已归档", "Yes; the upstream repository is archived") if lead["archived"] else t("否；核查时未归档", "No; not archived when checked")
            license_value = lead["license_spdx"] or t("待核实 / UNKNOWN", "Unknown / UNKNOWN")
            github_description = lead["github_description"] or t("GitHub API 未返回描述；不作补写。", "GitHub API returned no description; none was inferred.")
            sections = f'''<div class="detail-meta-row">{self.evidence_tag("E0", needs_review=True)}<a class="about-link" href="../../about/">{t("了解证据与评分", "About evidence and scoring")} ↗</a></div>{self.rating_detail(PROJECT_LEAD_SCORES[lead["id"]])}<h2>{t("候选路线","Candidate route")}</h2><ul class="detail-list"><li><b>{t("可能用途","Candidate use")}</b> {h(use_case)}</li><li><b>{t("设备范围","Hardware scope")}</b> {h(device_scope)}</li><li><b>{t("目前已知","What is known")}</b> {h(summary)}</li><li><b>GitHub</b> {h(github_description)}</li><li><b>{t("为什么仍是 E0","Why this remains E0")}</b> {h(reason)}</li><li><b>{t("核查记录","Review record")}</b> {h(lead["content_id"])} · {h(lead["checked_at"])}</li></ul><h2>{t("动手前","Before you start")}</h2><ul class="detail-list"><li>{t("如果找不到与准确型号、硬件修订和固件相符的安装与恢复资料，不要刷写、拆机或购买配件。","Do not flash, disassemble, or buy parts without installation and recovery material for the exact model, hardware revision, and firmware.")}</li></ul><h2>{t("仓库快照","Repository snapshot")}</h2><ul class="detail-list"><li><b>{t("归档","Archived")}</b> {h(archive_state)}</li><li><b>{t("最后 push","Last push")}</b> {h(lead["pushed_at"])}</li><li><b>{t("默认分支","Default branch")}</b> {h(lead["default_branch"])}</li><li><b>{t("API 许可证标识","API license identifier")}</b> {h(license_value)}</li><li>{t("许可证快照不自动覆盖固件、模型、图片、商标或第三方组件；最后 push 也不证明设备兼容。","The license snapshot does not automatically cover firmware, models, images, trademarks, or third-party components; a recent push does not prove compatibility.")}</li></ul><ul class="detail-links"><li>{self.link(lead["repo_url"],t("打开上游仓库","Open upstream repository")+" ↗")}</li><li><a href="../../project-sources/">{t("返回 200 个项目来源","Back to 200 project sources")} ↗</a></li></ul>'''
            self.article(lead["name"], summary, sections, f"project-leads/{lead['id']}/index.html", record=True)

    def leads(self):
        ordered_leads = sorted(WATCHLIST.items(), key=lambda item: score_sort_key(LEAD_SCORES[item[0]], item[1][self.lang]["title"]))
        cards = "".join(self.lead_card(slug,lead,"") for slug,lead in ordered_leads)
        reviewed_count = sum(lead.get("evidence_level") == "E1" for lead in WATCHLIST.values())
        e0_count = len(WATCHLIST) - reviewed_count
        source_names = lambda lead: ({"恩山无线论坛":"Enshan Wireless Forum", "ophub 中文项目文档":"ophub Chinese documentation"}.get(lead["source_platform"], lead["source_platform"]) if self.lang == "en" else lead["source_platform"])
        sources = collections.Counter(source_names(lead) for lead in WATCHLIST.values())
        source_options = "".join(f'<option value="{h(source)}">{h(source)} ({count})</option>' for source,count in sources.most_common())
        intro = self.t(
            f"这里汇集 {len(WATCHLIST)} 条设备与社区路线，来源包括中文论坛、X、作者网站、制作社区以及 ESPHome、Tasmota、postmarketOS 等上游设备库。其中 {reviewed_count} 条已读取具体型号资料并标为 E1，另有 {e0_count} 条 E0 待继续核查；E1 仍不等于 KitAgain 实机验证。",
            f"This section contains {len(WATCHLIST)} device and community routes from Chinese forums, X, author sites, maker communities and upstream databases such as ESPHome, Tasmota and postmarketOS. {reviewed_count} exact-model sources have been read and marked E1; {e0_count} remain E0. E1 still does not mean KitAgain tested the hardware."
        )
        search = f'<form id="lead-filters" class="filters" role="search"><div class="search-field"><label for="lead-q">{self.t("搜索设备、型号或来源","Search device, model or source")}</label><input id="lead-q" type="search" placeholder="{self.t("例如 AX3000T、N1、ESPHome…","Try AX3000T, N1, ESPHome…")}" autocomplete="off"></div><div class="filter-grid"><label>{self.t("来源","Source")}<select id="lead-source"><option value="">{self.t("全部来源","All sources")}</option>{source_options}</select></label><label>{self.t("证据","Evidence")}<select id="lead-evidence"><option value="">{self.t("全部证据","All evidence")}</option><option value="E1">E1 · {self.t("具体型号资料已读","Exact-model source reviewed")}</option><option value="E0">E0 · {self.t("待继续核查","Further review needed")}</option></select></label><label>{self.t("最低星级","Minimum stars")}<select id="lead-score"><option value="">{self.t("不限","Any score")}</option>{score_filter_options()}</select></label><label>{self.t("排序","Sort")}<select id="lead-sort"><option value="score-desc">{self.t("星级：高到低","Stars: high to low")}</option><option value="title-asc">{self.t("名称：A–Z","Name: A–Z")}</option></select></label></div><div class="filter-bottom"><p id="lead-result-count" role="status" aria-live="polite">{self.t("显示","Showing")} {len(WATCHLIST)} / {len(WATCHLIST)}</p><button type="reset">{self.t("清除筛选","Clear filters")}</button></div></form>'
        sections = f'<aside class="boundary"><b>{self.t("先看证据等级","Check the evidence level")}</b><p>{self.t("E1 表示已经读取具体型号的配置或维护记录；E0 表示目前只确认了设备与来源之间的联系。两者都需要在动手前核对准确型号、硬件修订和恢复方式。","E1 means an exact-model configuration or maintainer record was read. E0 means only the device/source connection is established. Both still require exact model, hardware revision and recovery checks before action.")}</p></aside>{search}<div id="lead-grid" class="project-grid">{cards}</div><div id="lead-empty" class="empty" hidden><h3>{self.t("暂时没有匹配设备","No matching device")}</h3><p>{self.t("换一个型号、品牌或来源词试试。","Try another model, brand or source term.")}</p></div>'
        self.article(self.t("设备图谱与社区线索","Device atlas and community leads"),intro,sections,"leads/index.html")
        for slug,lead in WATCHLIST.items():
            v = lead[self.lang]
            details = WATCHLIST_DETAILS[slug]
            decision = details[self.lang]
            evidence = lead.get("evidence_level", "E0")
            sections = f'<div class="detail-meta-row">{self.evidence_tag(evidence)}<a class="about-link" href="../../about/">{self.t("了解证据与评分", "About evidence and scoring")} ↗</a></div>'
            sections += self.hardware_tags(self.lead_hardware_values(slug,lead),"../../directory/","directory-grid")
            sections += f'<ul class="detail-list"><li><b>{self.t("记录", "Record")}</b> {h(lead["content_id"])}</li><li><b>{self.t("资料核查", "Sources reviewed")}</b> {h(lead["reviewed_at"])}</li><li><b>{self.t("实机状态", "Hands-on status")}</b> {self.t("KitAgain 未进行实机测试", "No KitAgain hands-on hardware test")}</li></ul>'
            sections += self.rating_detail(LEAD_SCORES[slug])
            if lead.get("deep_review"):
                review = lead["deep_review"][self.lang]
                sections += f'<h2>{self.t("具体型号核查", "Exact-model review")}</h2><ul class="detail-list"><li><b>{self.t("硬件确认", "Hardware")}</b> {h(review["hardware"])}</li><li><b>{self.t("改造路线", "Installation route")}</b> {h(review["route"])}</li><li><b>{self.t("可以做到什么", "Expected result")}</b> {h(review["result"])}</li><li><b>{self.t("不能扩大解释的边界", "Boundary")}</b> {h(review["boundary"])}</li><li><b>{self.t("恢复与停止条件", "Recovery and stop condition")}</b> {h(review["recovery"])}</li><li><b>{self.t("上游版本", "Upstream revision")}</b> {h(lead["upstream_revision"])}</li></ul>'
            sections += f'<h2>{self.t("是否值得继续", "Decide before you build")}</h2><ul class="detail-list"><li><b>{self.t("当前阶段", "Current stage")}</b> {h(decision["stage"])}</li><li><b>{self.t("现在能用到什么程度", "Practical readiness")}</b> {h(decision["usable"])}</li><li><b>{self.t("用户价值", "User value")}</b> {h(decision["value"])}</li><li><b>{self.t("继续跟进建议", "Follow-up recommendation")}</b> {h(decision["follow"])}</li></ul><h2>{self.t("适用设备与限制", "Device fit and limits")}</h2><h3>{self.t("已知可参考或可继续核查", "Known fit or worth checking")}</h3>{ul(decision["works_for"], "detail-list")}<h3>{self.t("不能视为已支持", "Not established or unsuitable")}</h3>{ul(decision["not_for"], "detail-list")}'
            gap_heading = self.t("E1 还没有证明什么", "What E1 still does not prove") if evidence == "E1" else self.t("为什么仍是 E0", "Why it remains E0")
            sections += f'<h2>{self.t("缺口、下一步与风险", "Gaps, next step, and risk")}</h2><ul class="detail-list"><li><b>{gap_heading}</b> {h(v["gap"])}</li><li><b>{self.t("下一步核验", "Next review step")}</b> {h(v["next_check"])}</li><li><b>{self.t("风险与停止条件", "Risk and stop condition")}</b> {h(v["safety"])}</li></ul>'
            resources = "".join(f'<li><div class="resource-head">{self.link(item["url"], item[self.lang+"_label"]+" ↗")}<span>{h(item["kind"])}</span></div><span class="resource-note">{h(item[self.lang+"_note"])}</span><small>{h(item["url"])}</small></li>' for item in details["resources"])
            sections += f'<h2>{self.t("链接里分别有什么","What each link contains")}</h2><ul class="resource-list">{resources}</ul><a class="back" href="../">← {self.t("返回全部社区线索","Back to all field leads")}</a>'
            self.article(v["title"],v["summary"],sections,f"leads/{slug}/index.html", record=True)

GUIDES = json.loads((ROOT / "data/guides.json").read_text(encoding="utf-8"))
ARTICLES = json.loads((ROOT / "data/articles.json").read_text(encoding="utf-8"))
WATCHLIST, WATCHLIST_DETAILS = load_watchlist(ROOT / "data")
AUTHOR_SOCIALS = json.loads((ROOT / "data/author-socials.json").read_text(encoding="utf-8"))
PROJECT_SCORES, LEAD_SCORES, PROJECT_LEAD_SCORES = score_all(PROJECTS, WATCHLIST, WATCHLIST_DETAILS, PROJECT_LEADS, SCORING_EVIDENCE)
DIRECTORY_EXPORT = build_directory_export(
    projects=PROJECTS,
    project_leads=PROJECT_LEADS,
    watchlist=WATCHLIST,
    details=WATCHLIST_DETAILS,
    base_url=BASE,
    version=CONFIG["version"],
    generated_at=SCORING_EVIDENCE.get("generated_at", DATA["compiled_at"]),
    scoring_evidence=SCORING_EVIDENCE,
)

def build():
    assert CONFIG["version"] == DATA["version"], "Product versions differ"
    for p in PROJECTS:
        record = EN["projects"][p["id"]]
        assert record["source_sha256"] == digest(p) and record["status"] == "reviewed", ("Translation stale",p["id"])
    manifest = json.loads((ROOT / "data/i18n/revisions.json").read_text(encoding="utf-8"))
    assert manifest["deep_source_sha256"] == digest(DEEP), "Deep-dive translations stale"
    assert manifest["deep_translation_sha256"] == digest(DEEP_EN), "Deep-dive translations changed without review"
    for lang in ["zh","en"]:
        s=Site(lang)
        s.home();s.supporting();s.guides();s.articles();s.leads();s.directory();s.project_sources()
        for p in PROJECTS:
            s.detail(p)
            if lang=="zh":s.detail(p,legacy=True)
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    (OUT / "data/watchlist.json").write_text(json.dumps(WATCHLIST, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (OUT / "data/watchlist-details.json").write_text(json.dumps(WATCHLIST_DETAILS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write(OUT/"data/directory.json",export_json_text(DIRECTORY_EXPORT))
    write(OUT/"data/directory.csv",directory_csv(DIRECTORY_EXPORT))
    write(OUT/"data/project-leads.json",json.dumps(PROJECT_LEAD_DATA,ensure_ascii=False,indent=2)+"\n")
    write(OUT/"data/project-leads.csv",project_leads_csv(PROJECT_LEADS))
    shutil.copyfile(SCORING_EVIDENCE_PATH, OUT/"data/scoring-evidence.json")
    identity_coverage = []
    for p in PROJECTS:
        owner = repository_owner_account(p["repo_url"])
        profiles = AUTHOR_SOCIALS.get(p["id"], [])
        identity_coverage.append({
            "project_id": p["id"],
            "project_name": p["name"],
            "repository_owner": owner,
            "verified_author_profiles": profiles,
            "coverage_status": "repository-owner-and-author-profile" if profiles else "repository-owner-only",
            "note": "Repository ownership is a traceability link and does not establish sole authorship. Social profiles require explicit attribution evidence."
        })
    write(OUT/"data/author-identity-coverage.json",json.dumps({
        "generated_from": ["data/catalog.json", "data/author-socials.json"],
        "catalog_entries": len(PROJECTS),
        "repository_owner_covered": sum(bool(row["repository_owner"]) for row in identity_coverage),
        "projects_with_verified_author_profiles": sum(bool(row["verified_author_profiles"]) for row in identity_coverage),
        "entries": identity_coverage
    },ensure_ascii=False,indent=2)+"\n")
    # Preserve historical method URL with complete localized content, not a fake HTTP 301.
    old = (OUT/"zh/research/index.html").read_text(encoding="utf-8")
    def rewrite_reference(match):
        attr, ref = match.groups()
        if urlsplit(ref).scheme or ref.startswith(("#","//")):
            return match.group(0)
        new = posixpath.normpath(posixpath.join("zh/research",ref))
        if ref.endswith("/"):
            new += "/"
        return f'{attr}="{new}"'
    old = re.sub(r'(href|src)="([^"]+)"',rewrite_reference,old)
    write(OUT/"research.html",old)
    # Serve the complete English catalog at /; retain /en/ for existing links.
    entry = (OUT/"en/index.html").read_text(encoding="utf-8")
    def from_english_home(match):
        attr, ref = match.groups()
        parts = urlsplit(ref)
        if parts.scheme or parts.netloc or not parts.path or ref.startswith("//"):
            return match.group(0)
        path = posixpath.normpath(posixpath.join("en",parts.path))
        if parts.path.endswith("/"):
            path += "/"
        suffix = ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")
        return f'{attr}="{path}{suffix}"'
    entry = re.sub(r'(href|src|action)="([^"]+)"',from_english_home,entry)
    entry = entry.replace('class="brand" href="en/index.html"','class="brand" href="index.html"')
    write(OUT/"index.html",entry)
    urls = [""]+[p for p in PATHS if p != "en/"]
    write(OUT/"sitemap.xml",'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f"<url><loc>{h(BASE+p)}</loc><lastmod>{CONTENT_DATE}</lastmod></url>" for p in urls)+"\n</urlset>\n")
    migrations = {"note":"Historical URLs remain readable HTML with canonical links; these are not HTTP 301 redirects.",
                  "mappings":{f"projects/{p['id']}.html":f"zh/projects/{p['id']}/" for p in PROJECTS}}
    write(OUT/"data/url-mapping.json",json.dumps(migrations,ensure_ascii=False,indent=2)+"\n")
    # Public English export keeps shared machine-readable facts while localizing editorial fields.
    english = json.loads(json.dumps(DATA))
    english["language"]="en";english["labels"]=LABELS_EN
    for p in english["projects"]:
        v = EN["projects"][p["id"]]
        p["summary"]=v["summary"];del p["summary_zh"]
        for k in ["device_scope","method","limitations","firmware_requirement","region_requirement"]:p[k]=v[k]
        p["cost"]["items"]=v["cost_items"]
        p["cost"]["note"]="Not priced; open source does not imply zero hardware, hosting, electricity or cloud cost."
        p["evidence"]["reason"]=v["evidence_reason"];p["risk"]["recovery"]=v["recovery"]
        p["maintenance"]["note"]="Unarchived/recent push is not proof a model works; mirror migration is not the end of development."
        p["license"]["label"]=LICENSE_EN.get(p["license"]["label"],p["license"]["label"])
        p["license"]["scope"]="Root license/README declaration only; firmware, models, brands and third-party components may have different licenses."
        p["difficulty_basis"]="Editorial assessment of installation, firmware, assembly and troubleshooting; not an author-provided score."
        p["use_cases"]=[USE_IDS[u] for u in p["use_cases"]]
        p["requirements"]={k:REQS[val][1] if re.search(r"[\u4e00-\u9fff]",val) else val for k,val in p["requirements"].items()}
        p["translation"]={k:v[k] for k in ["source_sha256","status","reviewed_at","review_scope"]}
    write(OUT/"data/catalog.en.json",json.dumps(english,ensure_ascii=False,indent=2)+"\n")
    output=io.StringIO(newline="")
    fields=["id","name","category","summary","device_scope","method","limitations","evidence","requirements","cost","risk","checked_at","translation"]
    writer=csv.DictWriter(output,fieldnames=fields,lineterminator="\n");writer.writeheader()
    for p in english["projects"]:
        writer.writerow({k:json.dumps(p[k],ensure_ascii=False) if isinstance(p[k],(list,dict)) else p[k] for k in fields})
    write(OUT/"data/catalog.en.csv","\ufeff"+output.getvalue())
    write(OUT/"data/deep-dives.en.json",json.dumps(DEEP_EN,ensure_ascii=False,indent=2)+"\n")
    print(f"Bilingual build: {len(PATHS)} localized pages + complete English root + 54 historical URLs.")
