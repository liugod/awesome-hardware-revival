"""Build bilingual static pages from shared facts and revision-checked translations."""
import collections
import csv
import hashlib
import html
import io
import json
import posixpath
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

from scoring import build_directory_export, directory_csv, export_json_text, project_leads_csv, score_all
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

def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def h(value):
    return html.escape(str(value))

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")

def ul(values):
    return "<ul>" + "".join(f"<li>{h(v)}</li>" for v in values) + "</ul>"

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
        display_brand = self.t("垃圾佬复活站", "KitAgain")
        title_brand = self.t("垃圾佬复活站 · KitAgain", "KitAgain")
        alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{BASE if lang == "en" and tail == "index.html" else BASE+lang+"/"+("" if tail == "index.html" else tail.removesuffix("index.html"))}">' for lang,code in [("zh","zh-CN"),("en","en")])
        alternates += f'<link rel="alternate" hreflang="x-default" href="{BASE}">'
        markup = f"""<!doctype html>
<html lang="{self.t('zh-CN','en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)} · {title_brand}</title><meta name="description" content="{h(description)}">
<link rel="canonical" href="{h(canonical)}">{alternates}<meta name="theme-color" content="#f5f3eb">
<meta property="og:title" content="{h(title)} · {title_brand}"><meta property="og:description" content="{h(description)}"><meta property="og:url" content="{h(canonical)}"><meta property="og:type" content="website">
<link rel="icon" href="{rel('assets/mark.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{rel('assets/style.css')}?v={h(CONFIG['version'])}"><script src="{rel('assets/app.js')}?v={h(CONFIG['version'])}" defer></script>
</head><body><a class="skip" href="#main">{self.t('跳到正文','Skip to content')}</a>
<header class="site-header"><a class="brand" href="{rel(self.lang+'/index.html')}"><span class="brand-mark">↻</span><span>{display_brand}<small>{self.t('KITAGAIN · 旧设备再就业指南','GIVE OLD HARDWARE A NEW JOB')}</small></span></a>
<nav aria-label="{self.t('主导航','Main navigation')}"><a href="{rel(self.lang+'/directory/index.html')}">{self.t('全站目录','All routes')}</a><a href="{rel(self.lang+'/project-sources/index.html')}">{self.t('200 个项目来源','200 project sources')}</a><a href="{rel(self.lang+'/index.html')}#catalog">{self.t('深审项目','Reviewed')}</a><a href="{rel(self.lang+'/research/index.html')}">{self.t('我们怎么查','How we check')}</a><a href="{h(CONFIG['community_url'])}">{self.t('去社区','Community')}</a><a class="language-switch" href="{rel(target)}" lang="{other}" hreflang="{other}">{self.t('English','简体中文')}</a></nav></header>
<main id="main">{body}</main><footer><p>{self.t('让仍能工作的硬件，找到下一份工作。','Give working hardware its next job.')}</p><div>{self.t(f'正式目录核查 {DATE} · 设备图谱核查 {ATLAS_DATE} · 项目来源发现层 {PROJECT_LEAD_DATE}',f'Reviewed catalog {DATE} · device atlas {ATLAS_DATE} · project-source discovery {PROJECT_LEAD_DATE}')} · v{CONFIG['version']} · {self.t('未进行实机测试','No hands-on hardware tests')}<br>
<a href="{rel('data/directory.json')}" download>{self.t('全量 JSON','Full JSON')}</a> / <a href="{rel('data/directory.csv')}" download>{self.t('全量 CSV','Full CSV')}</a> / <a href="{rel('data/catalog'+('.en' if self.lang=='en' else '')+'.csv')}" download>{self.t('深审项目 CSV','Reviewed CSV')}</a> / <a href="{REPO}">GitHub ↗</a><br>{self.t('原创文字与目录 CC BY 4.0 · 站点代码 MIT · 第三方项目按各自许可','Original text & catalog: CC BY 4.0 · Site code: MIT · Third-party projects: their own licenses')}</div></footer></body></html>"""
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
        css = "rating compact" if compact else "rating"
        return f'<div class="{css}" title="{h(disclaimer)}"><span>{self.t("核查成熟度","Review maturity")}</span><strong>{record["score"]}/5</strong><small>{h(label)}</small></div>'

    def rating_detail(self, record, method_href):
        components = record["components"]
        reason = record["reason_zh" if self.lang == "zh" else "reason_en"]
        rows = [
            (self.t("证据强度", "Evidence strength"), components["evidence"]),
            (self.t("来源具体性", "Source specificity"), components["source_specificity"]),
            (self.t("恢复说明", "Recovery clarity"), components["recovery_clarity"]),
            (self.t("维护信息可见度", "Maintenance visibility"), components["maintenance_visibility"]),
        ]
        return f'''<aside class="rating-panel">{self.rating(record, compact=False)}<p>{h(reason)}</p><dl>{''.join(f'<div><dt>{h(label)}</dt><dd>{value}/5</dd></div>' for label,value in rows)}</dl><p class="muted">{h(record["disclaimer_zh" if self.lang == "zh" else "disclaimer_en"])} <a href="{h(method_href)}">{self.t("查看公式与分档","See the rubric and formula")} ↗</a></p></aside>'''

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
        attrs = {"id":p["id"],"category":p["category"],"ai":p["ai_relation"],"difficulty":p["difficulty"],"evidence":p["evidence"]["level"],"score":score["score"],"kind":"reviewed-project","title":p["name"],"use":"|".join(USE_IDS[u] for u in p["use_cases"])}
        hardware_values = [item[self.lang] for item in PROJECT_HARDWARE_TAGS[p["id"]]]
        search = " ".join([p["name"], p["summary_zh"], p["device_scope"], e["summary"], e["device_scope"], *p["keywords"], *p["model_examples"], *hardware_values, *p["use_cases"], *(en for uid,zh,en in USES if zh in p["use_cases"])])
        attrs["search"] = search
        attr = " ".join(f'data-{k}="{h(v)}"' for k,v in attrs.items())
        return f"""<article class="project {'has-image' if p['id'] in PROJECT_IMAGES else ''}" {attr}>{self.card_image(p,prefix)}{self.tags(p)}{self.rating(score)}{self.project_hardware_tags(p,prefix)}<h3><a href="{prefix}projects/{p['id']}/">{h(p['name'])} ↗</a></h3><p class="summary">{h(v['summary'])}</p><p class="device"><b>{self.t('先看你的设备','Check your hardware first')}</b>{h(v['device_scope'])}</p><p class="limit"><b>{self.t('别忽略','Watch out')}</b> {h(v['limitations'][0])}</p><div class="card-end"><span class="status {'attention' if p['maintenance']['status'] != 'not-archived' else ''}">{h(self.labels['maintenance'][p['maintenance']['status']])}</span><span>{h(v['method'])}</span></div></article>"""

    def lead_card(self, slug, lead, prefix="leads/"):
        v = lead[self.lang]
        decision = WATCHLIST_DETAILS[slug][self.lang]
        evidence = lead.get("evidence_level", "E0")
        score = LEAD_SCORES[slug]
        platform = lead["source_platform"]
        if self.lang == "en":
            platform = {"恩山无线论坛":"Enshan Wireless Forum", "ophub 中文项目文档":"ophub Chinese documentation"}.get(platform, platform)
        tags = [self.labels["category"][lead["category"]], platform, evidence]
        search = " ".join([v["title"], v["summary"], lead.get("device_name", ""), lead.get("device_model", ""), *self.lead_hardware_values(slug,lead), platform, lead.get("discovery_channel", "")])
        attrs = f'data-search="{h(search)}" data-title="{h(v["title"])}" data-category="{h(lead["category"])}" data-source="{h(platform)}" data-evidence="{h(evidence)}" data-score="{score["score"]}" data-kind="device-or-community-route" data-channel="{h(lead.get("discovery_channel", "legacy"))}"'
        status = self.t("E1 / 已读具体型号资料", "E1 / exact-model source reviewed") if evidence == "E1" else self.t("E0 / 需核对准确硬件", "E0 / exact hardware check required")
        return f"""<article class="project" {attrs}><div class="tags">{''.join(f'<span>{h(tag)}</span>' for tag in tags)}</div>{self.rating(score)}{self.hardware_tags(self.lead_hardware_values(slug,lead),prefix,'lead-grid')}<h3><a href="{prefix}{slug}/">{h(v['title'])} ↗</a></h3><p class="summary">{h(v['summary'])}</p><p class="device"><b>{self.t('当前可用程度','Practical readiness')}</b>{h(decision['usable'])}</p><p class="limit"><b>{self.t('待核缺口','Review gap')}</b> {h(v['gap'])}</p><div class="card-end"><span class="status {'attention' if evidence == 'E0' else ''}">{status}</span><span>{h(lead['content_id'])}</span></div></article>"""

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
            f'data-score="{score["score"]}" data-kind="project-source-lead"'
        )
        state = self.t("仓库已归档", "Repository archived") if lead["archived"] else self.t("仓库未归档", "Repository not archived")
        return f'''<article class="project" {attrs}><div class="tags"><span>{h(self.labels["category"][lead["category"]])}</span><span>{self.t("独立项目来源","Independent project source")}</span><span>E0</span></div>{self.rating(score)}<h3><a href="{h(prefix+lead['id']+'/')}">{h(lead['name'])} ↗</a></h3><p class="summary">{h(summary)}</p><p class="device"><b>{self.t("可继续核对的设备范围","Hardware scope to review")}</b>{h(device_scope)}</p><p class="limit"><b>{self.t("候选用途","Candidate use")}</b> {h(use_case)}</p><div class="card-end"><span class="status attention">{h(state)} · E0</span><span>{h(lead['content_id'])}</span></div></article>'''

    def home(self):
        t = self.t
        options = lambda group: "".join(f'<option value="{h(k)}">{h(v)}</option>' for k,v in group.items())
        groups = [
            ("category",t("设备","Device"),self.labels["category"]),("use",t("用途","Use"),{uid:t(zh,en) for uid,zh,en in USES}),
            ("ai",t("AI 关系","AI relationship"),self.labels["ai"]),("difficulty",t("难度","Difficulty"),self.labels["difficulty"]),
            ("evidence",t("证据","Evidence"),{k:v for k,v in self.labels["evidence"].items() if k in {"E1","E2"}}),
            ("score",t("最低核查分","Minimum review score"),{str(n):f"≥ {n}/5" for n in range(1,6)}),
            ("sort",t("排序","Sort"),{"score-desc":t("核查分：高到低","Review score: high to low"),"title-asc":t("名称：A–Z","Name: A–Z")})]
        filters = "".join(f'<label>{label}<select id="{key}" name="{key}"><option value="">{t("全部","All")}</option>{options(values)}</select></label>' for key,label,values in groups)
        topics = "".join(f'<a class="feature" href="guides/{gid}/"><span class="serial">0{i+1} / {t("路线比较","ROUTE COMPARISON")}</span><h3>{h(g[self.lang]["title"])}</h3><p>{h(g[self.lang]["intro"])}</p><span class="text-link">{t("查看条件与选择依据","Compare requirements and routes")} ↗</span></a>' for i,(gid,g) in enumerate(GUIDES.items()))
        articles = "".join(f'<a class="feature" href="articles/{slug}/"><span class="serial">{h(a["content_id"])} / {t("实用指南","FIELD GUIDE")}</span><h3>{h(a[self.lang]["title"])}</h3><p>{h(a[self.lang]["intro"])}</p><span class="text-link">{t("阅读核对清单与来源","Read the checklist and sources")} ↗</span></a>' for slug,a in ARTICLES.items())
        reviewed_device_count = sum(lead.get("evidence_level") == "E1" for lead in WATCHLIST.values())
        e0_lead_count = len(WATCHLIST) - reviewed_device_count
        counts = DIRECTORY_EXPORT["counts"]
        project_source_examples = []
        example_categories = set()
        for lead in PROJECT_LEADS:
            if lead["category"] not in example_categories:
                project_source_examples.append(lead)
                example_categories.add(lead["category"])
            if len(project_source_examples) == 4:
                break
        featured = []
        wanted_content_ids = ["D076", "D241", "D127", "D300"]
        for content_id in wanted_content_ids:
            match = next(((slug, lead) for slug, lead in WATCHLIST.items() if lead.get("content_id") == content_id), None)
            if match:
                featured.append(match)
        if len(featured) < 4:
            featured += [(slug, lead) for slug, lead in WATCHLIST.items() if (slug, lead) not in featured][:4-len(featured)]
        leads = "".join(self.lead_card(slug,lead) for slug,lead in featured)
        body = f"""<section class="hero"><div class="hero-copy"><p class="eyebrow">DON'T BIN IT. REBUILD IT.</p><h1>{t('别急着扔。<br>让旧硬件重新上岗。','Don’t bin it.<br>Give it another job.')}</h1><p class="intro">{t('输入设备或型号，看看它能变成信息屏、家庭服务器、媒体播放器，还是本地智能设备。每条路线都告诉你：适不适配、难在哪里、什么时候该停手。','Search a device or model to see whether it can become a display, home server, media player or local smart device. Every route shows what fits, what is difficult and when to stop.')}</p><a class="primary" href="directory/">{t(f'搜索全部 {counts["entries"]} 条公开记录',f'Search all {counts["entries"]} public entries')} →</a><a class="secondary" href="project-sources/">{t('查看 200 个独立项目来源','Browse 200 independent project sources')} →</a></div>
<aside class="field-note"><span class="eyebrow">START HERE</span><div class="big-count">{counts['entries']}<span>{t('条可检索公开记录','searchable public entries')}</span></div><dl><div><dt>{t('独立项目来源','Independent project sources')}</dt><dd>{counts['independent_project_sources']}</dd></div><div><dt>{t('深审项目','Reviewed projects')}</dt><dd>{len(PROJECTS)}</dd></div><div><dt>{t('设备/社区路线','Device/community routes')}</dt><dd>{len(WATCHLIST)}</dd></div></dl><p>{t('项目来源与设备路线分开计数；E0 发现候选不会冒充已完成兼容性核查的项目。','Project sources and device routes use separate denominators; E0 discoveries are never presented as compatibility-reviewed projects.')}</p><small>{t('内容更新','CONTENT UPDATED')} {CONTENT_DATE}</small></aside></section>
<div class="facts-strip"><span><b>✓</b>{t('按手里的设备找方案','Start with the hardware you own')}</span><span><b>✓</b>{t('先看清型号和条件','Check the exact model first')}</span><span><b>✓</b>{t('成功与失败经验都保留','Learn from successes and failures')}</span></div>
<section class="featured"><div class="section-heading"><p class="eyebrow">{t('不知道从哪开始？','NOT SURE WHERE TO START?')}</p><h2>{t('先选你手里的设备','Choose the device you already have')}</h2></div><div class="feature-grid">{topics}</div></section>
<section class="featured"><div class="section-heading"><p class="eyebrow">{t('准备动手？','READY TO TINKER?')}</p><h2>{t('先把关键条件查清楚','Check the important details first')}</h2></div><div class="feature-grid">{articles}</div></section>
<section class="featured"><div class="section-heading"><p class="eyebrow">{t('从中文社区、X 和设备数据库继续找','FOUND ACROSS THE OPEN WEB')}</p><h2>{t(f'{len(WATCHLIST)} 条设备/社区路线里，{reviewed_device_count} 条已完成型号级资料核查',f'{reviewed_device_count} exact-model sources reviewed across {len(WATCHLIST)} device/community routes')}</h2><p>{t('E1 设备页已经写明芯片、刷写入口、可实现功能、版本边界和恢复条件；其余 E0 线索继续保留，方便后续筛选。两种等级都不冒充 KitAgain 实机验证。','E1 device pages now state the chip, installation route, expected functions, revision boundary and recovery conditions. The remaining E0 leads stay searchable for follow-up. Neither level is presented as KitAgain hardware testing.')}</p></div><div class="project-grid">{leads}</div><p><a class="secondary" href="leads/">{t('搜索全部设备与线索','Search all devices and leads')} / {len(WATCHLIST)} ↗</a></p></section>
<section class="featured"><div class="section-heading"><p class="eyebrow">200 INDEPENDENT REPOSITORIES</p><h2>{t('先扩到 200 个项目来源，再逐条升级证据','Start with 200 project sources, then raise evidence item by item')}</h2><p>{t(f'{len(PROJECTS)} 个项目已完成来源深审；新增 {len(PROJECT_LEADS)} 个仓库经 GitHub API 与 README 入口核对后保留为 E0。它们扩展了 NAS、Kindle、手机、摄像头、音频、IoT、机器人、游戏与外设方向，但尚不等于兼容或安装成功。',f'{len(PROJECTS)} projects have source-level reviews. Another {len(PROJECT_LEADS)} repositories were checked through the GitHub API and README entry point and remain E0. They broaden NAS, Kindle, mobile, camera, audio, IoT, robot, gaming, and peripheral coverage without claiming compatibility or installation success.')}</p></div><div class="project-grid">{''.join(self.project_lead_card(lead) for lead in project_source_examples)}</div><p><a class="secondary" href="project-sources/">{t('搜索全部独立项目来源','Search all independent project sources')} / {counts['independent_project_sources']} ↗</a></p></section>
<section id="catalog" class="catalog"><div class="section-heading"><h2>{t('直接搜索你的设备','Search for your device')} <span class="muted">/ {len(PROJECTS)}</span></h2><p>{t('不知道项目名也没关系，输入设备、型号或你想实现的用途。','You do not need to know a project name. Search by device, model or the job you want it to do.')}</p></div>
<form id="filters" class="filters" role="search"><div class="search-field"><label for="q">{t('搜索设备、型号或项目（支持中英文）','Search devices, models or projects (Chinese or English)')}</label><input id="q" name="q" type="search" placeholder="{t('例如 Kindle、LX06、打印机…','Try Kindle, LX06, printer…')}" autocomplete="off"></div>
<div class="filter-grid">{filters}</div><div class="filter-bottom"><p id="result-count" role="status" aria-live="polite">{t('显示','Showing')} {len(PROJECTS)} / {len(PROJECTS)}</p><div><button type="button" id="share">{t('复制筛选链接','Copy filtered link')}</button><button type="reset">{t('清除筛选','Clear filters')}</button></div></div><span id="share-status" role="status"></span></form>
<p class="evidence-note">{t('信息来自项目文档、作者说明和社区原帖；收录不表示你的型号一定可用。核查成熟度受 E0–E3 证据上限约束，不是星级口碑或成功率。','Information comes from project documentation, author notes and original community posts. Inclusion does not guarantee your exact model. Review maturity is capped by E0–E3 evidence and is not a popularity or success rating.')} <a href="scoring/">{t('查看评分方法','Scoring method')} ↗</a></p>
<noscript><p>{t('JavaScript 未启用；仍可阅读完整目录并使用浏览器查找。','JavaScript is disabled. The full catalog is readable; use your browser’s Find command.')}</p></noscript>
<div id="project-grid" class="project-grid">{''.join(self.card(p) for p in PROJECTS)}</div>
<div id="empty" class="empty" hidden><h3>{t('暂时没有匹配条目','No matching entries')}</h3><p>{t('减少筛选条件，或提交设备线索。','Try fewer filters, or contribute a device lead.')}</p><a href="contribute/">{t('提交线索','Contribute a lead')} ↗</a></div></section>
<section class="closing"><div><p class="eyebrow">PASS IT ON</p><h2>{t('你手里的旧设备，也许正缺一条靠谱路线。','Your old device may only need the right route.')}</h2><p>{t('分享准确型号、做成了什么、哪里失败和怎样恢复，下一位垃圾佬就能少走一点弯路。','Share the exact model, the result, the failure point and the recovery. The next builder can start with better information.')}</p></div><a class="primary" href="contribute/">{t('分享一次改造','Share a build')} ↗</a></section>"""
        self.page(t("旧设备别急着扔，让它重新上岗","Give old hardware another job"),t("按设备和型号寻找旧硬件改造路线，快速了解能做什么、适配条件和停止条件。","Find a practical reuse route for old hardware, with clear outcomes, compatibility checks and stop conditions."),body)

    def detail(self, p, legacy=False):
        t = self.t
        v = localized(p, self.lang)
        d = (DEEP_EN if self.lang == "en" else DEEP).get(p["id"])
        current = f"projects/{p['id']}.html" if legacy else f"{self.lang}/projects/{p['id']}/index.html"
        rel = lambda x: self.rel(x, current)
        project_media = self.detail_image(p, current)
        use_labels = [t(zh, en) for uid, zh, en in USES if zh in p["use_cases"]]
        outcome_list = ul(use_labels)
        extra = ""
        if d:
            extra = f'<section class="prose" id="analysis"><h2>{t("从闲置到能用，它改变了什么","How this changes the device")}</h2><div class="before-after"><div><h3>{t("原来卡在哪里","What was holding it back")}</h3><p>{h(d["before"])}</p></div><div><h3>{t("改完能做什么","What it can do afterwards")}</h3><p>{h(d["after"])}</p></div></div><p>{h(d["analysis"])}</p><h3>{t("适合你，如果","A good fit if")}</h3><p>{h(d["fit"])}</p><h3>{t("先别选，如果","Skip this route if")}</h3><p>{h(d["not_fit"])}</p><h3>{t("做完以后这样检查","Checks after the build")}</h3>{ul(d["acceptance"])}<p class="muted">{t("这是给你的验收清单；KitAgain 目前还没有亲手完成这些硬件测试。","Use this as your acceptance checklist; KitAgain has not completed these hardware tests hands-on.")}</p></section>'
        specs = [(t("怎么改","Method"),v["method"]), (t("上手难度","Difficulty"),self.labels["difficulty"][p["difficulty"]])]
        specs += [(t(zh,en), t(*REQS[p["requirements"][key]])) for key,zh,en in [("disassembly","拆机","Disassembly"),("soldering","焊接","Soldering"),("cloud_api","云 API / 服务","Cloud API / service")]]
        specs += [(t("成本金额","Cost amount"),t("待核价 / UNKNOWN","Not priced / UNKNOWN"))]
        source_notes = {
            "upstream-document": t("先用它了解项目能做什么、怎样开始，以及作者写明的限制。", "Use this to understand the outcome, how to start and the limits stated by the project."),
            "official-compatibility-or-install": t("动手前用它核对准确型号、固件版本和安装步骤。", "Use this before starting to check the exact model, firmware and installation steps."),
            "ai-setup-doc": t("这里说明 AI 工具参与了哪些设置步骤，不代表设备在本地运行模型。", "This explains where AI assisted setup; it does not mean the model runs on the device."),
            "author-process": t("作者在这里记录了实际制作过程、取舍或结果。", "The author records the build process, trade-offs or result here."),
        }
        sources = "".join(f'<li><div class="resource-head">{self.link(s["url"],t(*SOURCE_KINDS[s["kind"]])+" ↗")}<span>{s["checked_at"][:10]}</span></div><p>{h(source_notes[s["kind"]])}</p><small>{h(s["url"])}</small></li>' for s in p["sources"])
        sources += "".join(f'<li><div class="resource-head">{self.link(s["url"],t("作者的 X 原帖 ↗","Original author X post ↗"))}<span>X</span></div><p>{t("适合补看作者当时展示的设备和过程；本目录已读正文，但没有把视频画面当成已核验结果。","Useful for the author's device and build context. The text was read, but video frames were not treated as a verified result.")}</p><small>{h(s["url"])}</small></li>' for s in p["x_sources"])
        license_label = p["license"]["label"] if self.lang=="zh" else LICENSE_EN.get(p["license"]["label"],p["license"]["label"])
        types = {"case":t("具体改造路线","Specific modification route"),"platform":t("平台 / 多机型工程","Platform / multi-device project"),"prerequisite":t("前置工具","Prerequisite tool")}
        socials = AUTHOR_SOCIALS.get(p["id"], [])
        repo_owner = repository_owner_account(p["repo_url"])
        identity_links = ""
        if repo_owner:
            identity_links += f'<li>{self.link(repo_owner["url"], repo_owner["name"]+" · "+repo_owner["platform"]+" ↗")}<span class="muted"> — {t("源码仓库所有者账号；不据此推断其为唯一作者","Source-repository owner account; this does not establish sole authorship")}</span></li>'
        identity_links += "".join(f'<li>{self.link(item["url"], item["name"]+" · "+item["platform"]+" ↗")}<span class="muted"> — {h(item[self.lang+"_role"])}</span></li>' for item in socials)
        social_section = f'<h2>{t("项目账号与已核实作者主页","Project identity and verified author profiles")}</h2><ul class="sources">{identity_links}</ul><p class="muted">{t("仓库所有者账号用于追溯项目来源；作者社交账号只有在项目资料、仓库或作者主页能确认归属时才收录。","Repository-owner accounts provide project traceability. Author social profiles are listed only when attribution is confirmed by project materials, the repository or the author profile.")}</p>' if identity_links else ""
        body = f"""<div class="detail-wrap"><a class="back" href="{rel(self.lang+'/index.html')}#catalog">← {t('继续找别的改造方案','Find another reuse route')}</a><section class="detail-head">{self.tags(p)}{self.project_hardware_tags(p,rel(self.lang+'/index.html'))}<h1>{h(p['name'])}</h1><div class="project-purpose"><span>{t('先说人话：它能带来什么','The useful bit first')}</span><p>{h(v['summary'])}</p></div><div class="reader-snapshot"><div><b>{t('做成以后','What you get')}</b>{outcome_list}</div><div><b>{t('你手里的设备要对得上','Your hardware must match')}</b><p>{h(v['device_scope'])}</p></div><div><b>{t('遇到这种情况先停手','Stop here if')}</b><p>{h(v['limitations'][0])}</p></div></div>{project_media}<p class="muted">{t('这是一条','This is a')} {types[p['entry_type']]} · {t('最近核对公开资料','Public sources last checked')} {p['checked_at'][:10]}</p><div class="actions">{self.link(p['repo_url'],t('去项目主页看看','Open the project page')+' ↗')}{self.link(p['tutorial_url'],t('照着原教程动手','Follow the original guide')+' ↗')}{self.link(p['compatibility_url'],t('先确认我的型号','Check my exact model')+' ↗')}</div></section>
{self.rating_detail(PROJECT_SCORES[p['id']],rel(self.lang+'/scoring/index.html'))}<aside class="boundary"><b>{t('动手前，把设备和这几项逐一对上','Before you start, match these details')}</b><p>{h(v['device_scope'])}</p>{ul(v['limitations'])}<p>{t('固件','Firmware')}: {h(v['firmware_requirement'] or t('待核实','Unknown'))} · {t('地区版本','Region')}: {h(v['region_requirement'] or t('待核实','Unknown'))}</p></aside>{extra}
<section class="prose"><h2>{t('你要准备什么','What to prepare')}</h2><dl class="spec-grid">{''.join(f'<div><dt>{h(k)}</dt><dd>{h(val)}</dd></div>' for k,val in specs)}</dl><h3>{t('还可能要花的钱','Things you may still need to buy or run')}</h3>{ul(v['cost_items'])}<p>{t('这些价格还没有核实。软件开源，也可能仍要买转接件、主板、存储，或承担电费和服务费。','Prices have not been checked. Open-source software can still require adapters, boards, storage, electricity or paid services.')}</p>
<h2>{t('最坏会怎样，怎么退回来','What can go wrong, and how to get back')}</h2><p>{t('数据丢失风险','Data-loss risk')}: {h(t(*RISKS[p['risk']['data_loss']]))}; {t('刷坏或无法启动的风险','Bricking / boot-failure risk')}: {h(t(*RISKS[p['risk']['bricking']]))}. {t('这是按操作路线给出的提醒，还没有在每台设备上实测。','This is route-based guidance and has not been tested on every device.')}</p><p>{h(v['recovery'])}</p><p>{self.link(p['risk']['recovery_url'],t('先收藏恢复资料','Save the recovery guide'))}</p>
<h2>{t('这条信息现在可信到哪一步','How far the evidence goes')}</h2><p><b>{p['evidence']['level']} · {h(self.labels['evidence'][p['evidence']['level']])}</b></p><p>{h(v['evidence_reason'])}</p><p>{t('KitAgain 目前没有亲手测试这台设备，也没有把别人的成功截图当成我们的复现。','KitAgain has not tested this device hands-on, and does not present someone else’s success image as our own reproduction.')}</p>
<dl class="spec-grid"><div><dt>{t('维护状态','Maintenance')}</dt><dd>{h(self.labels['maintenance'][p['maintenance']['status']])}</dd></div><div><dt>{t('GitHub 最后 push','Last GitHub push')}</dt><dd>{h(p['maintenance']['last_push_at'] or t('待核实','Unknown'))}</dd></div><div><dt>{t('仓库许可证','Repository license')}</dt><dd>{self.link(p['license']['url'],license_label)}</dd></div></dl>
<p>{t('未归档或近期 push 不能证明型号无故障；镜像迁移也不等于停止维护。','An unarchived repository or recent push does not prove a model works. Mirror migration does not mean development has stopped.')}</p><p>{t('根许可证或 README 声明不代表固件、模型、品牌和第三方组件均采用相同许可。','A root license or README declaration does not establish the same license for firmware, models, brands and third-party components.')}</p>
{social_section}<h2>{t('这些链接分别能帮你做什么','What each link is useful for')}</h2><ul class="resource-list">{sources}</ul><p>{t('原始页面可能使用中文或英文。准备动手时，再按你的准确型号、固件和地区版本核对一次。','Original pages may be in Chinese or English. Before starting, recheck the exact model, firmware and regional variant you own.')}</p><div class="actions"><a href="{rel(self.lang+'/contribute/index.html')}?project={p['id']}">{t('补一条经验或纠错','Add experience or a correction')} ↗</a><a href="{rel(self.lang+'/community/index.html')}?project={p['id']}">{t('带着型号去社区问','Ask the community with your model')} ↗</a></div></section></div>"""
        self.page(p["name"]+t("：适配设备与复现条件",": compatibility and reproduction"),v["summary"]+" "+v["device_scope"],body,f"projects/{p['id']}/index.html",current if legacy else None)

    def article(self, title, intro, sections, tail):
        body = f'<div class="detail-wrap"><section class="detail-head"><h1>{h(title)}</h1><p class="intro">{h(intro)}</p></section><section class="prose">{sections}</section></div>'
        self.page(title,intro,body,tail)

    def supporting(self):
        t = self.t
        method = f"""<h2>{t('收录意味着什么','What inclusion means')}</h2><p>{t(f'E0：公开社区线索 {len(WATCHLIST)} 条。E1：已读源码与部署文档，50 条。E2：作者实机陈述或演示，3 条。E3：独立复现，0 条。本目录实机测试 0 条。',f'E0: {len(WATCHLIST)} public community leads. E1: source and deployment documentation reviewed, 50 entries. E2: author hardware claims or demonstrations, 3. E3: verified independent reproduction, 0. Catalog hands-on hardware tests: 0.')}</p>
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
        rubric_rows = "".join(
            f'<tr><td><b>{score}/5</b></td><td>{h(DIRECTORY_EXPORT["rubric"][str(score)][self.lang])}</td><td>{distribution[str(score)]}</td></tr>'
            for score in range(1,6)
        )
        scoring = f'''<aside class="boundary"><b>{t("分数回答什么","What the score answers")}</b><p>{t("它回答“KitAgain 把这条资料核查到哪一步”，不回答“项目有多好”“一定成功吗”或“操作安全吗”。","It answers how far KitAgain has reviewed the record—not how good the project is, whether it will work, or whether the procedure is safe.")}</p></aside>
<h2>{t("五档证据上限","Five evidence-capped levels")}</h2><table><thead><tr><th>{t("分数","Score")}</th><th>{t("含义","Meaning")}</th><th>{t("当前条数","Current entries")}</th></tr></thead><tbody>{rubric_rows}</tbody></table>
<h2>{t("计算方式","Calculation")}</h2><p>{t("四个可审计分项先按证据强度 50%、来源具体性 20%、恢复说明 20%、维护信息可见度 10% 加权。随后应用硬上限：E0≤2、E1≤3、E2≤4、E3≤5。只有索引或仓库元数据的 E0 固定为 1；已有来源页或完整判断表的 E0 最多为 2。","Four auditable components are weighted: evidence strength 50%, source specificity 20%, recovery clarity 20%, and maintenance visibility 10%. A hard ceiling then applies: E0≤2, E1≤3, E2≤4, E3≤5. An E0 based only on an index or repository metadata is fixed at 1; an E0 with a source page or complete decision sheet can reach at most 2.")}</p>
<h2>{t("不会进入评分的因素","What is deliberately excluded")}</h2>{ul([t("star、点赞、浏览量和搜索热度","Stars, likes, views, and search popularity"),t("未经核实的“成功率”和兼容承诺","Unverified success rates or compatibility promises"),t("项目未归档或最近 push 被当成可用证明","Treating unarchived/recently pushed as proof of usability"),t("重复型号数量被当成多个独立项目","Counting multiple device models as independent projects")])}
<h2>{t("全量覆盖与数据下载","Coverage and downloads")}</h2><p>{t(f"当前 {DIRECTORY_EXPORT['counts']['score_coverage']} / {DIRECTORY_EXPORT['counts']['entries']} 条公开路线有评分，分数、四个分项、理由、证据等级、来源 URL 和中英文详情 URL 均进入统一 JSON/CSV。",f"All {DIRECTORY_EXPORT['counts']['score_coverage']} / {DIRECTORY_EXPORT['counts']['entries']} public routes have a score. The unified JSON/CSV includes the score, four components, rationale, evidence level, source URL, and Chinese/English detail URLs.")}</p><p><a href="../../data/directory.json" download>JSON</a> · <a href="../../data/directory.csv" download>CSV</a> · <a href="../directory/">{t("打开全站目录","Open the full directory")} ↗</a></p>'''
        self.article(t("1–5 分核查成熟度","1–5 review-maturity score"),t("证据封顶、逐条可解释、全量可导出。","Evidence-capped, explainable for every entry, and fully exportable."),scoring,"scoring/index.html")

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
            score = PROJECT_SCORES[project["id"]]["score"]
            all_cards.append((score, project["name"].casefold(), self.card(project, "../")))
        for slug, lead in WATCHLIST.items():
            score = LEAD_SCORES[slug]["score"]
            all_cards.append((score, lead[self.lang]["title"].casefold(), self.lead_card(slug, lead, "../leads/")))
        for lead in PROJECT_LEADS:
            score = PROJECT_LEAD_SCORES[lead["id"]]["score"]
            all_cards.append((score, lead["name"].casefold(), self.project_lead_card(lead, "../project-leads/")))
        all_cards.sort(key=lambda item: (-item[0], item[1]))
        category_options = "".join(f'<option value="{h(key)}">{h(value)}</option>' for key,value in self.labels["category"].items())
        evidence_options = "".join(f'<option value="{level}">{level} · {h(self.labels["evidence"][level])}</option>' for level in ["E0","E1","E2","E3"])
        score_options = "".join(f'<option value="{n}">≥ {n}/5</option>' for n in range(1,6))
        counts = DIRECTORY_EXPORT["counts"]
        body = f'''<div class="detail-wrap wide"><section class="detail-head"><p class="eyebrow">ONE INDEX / CLEAR EVIDENCE</p><h1>{t("全部设备与改造记录","All hardware-revival records")}</h1><p class="intro">{t(f"统一检索 {counts['entries']} 条公开记录，来自 {counts['unique_primary_source_urls']} 个不同主来源 URL。其中 200 个是互不重复的项目仓库来源：53 个深审项目加 147 个 E0 发现候选；另有 347 条设备/社区路线。三个分母分别标注，不把同一上游的不同设备型号冒充独立项目。",f"Search {counts['entries']} public records from {counts['unique_primary_source_urls']} distinct primary-source URLs. Exactly 200 are unique project-repository sources: 53 reviewed projects plus 147 E0 discoveries; another 347 are device/community routes. Each denominator stays explicit, and multiple devices from one upstream are not presented as independent projects.")}</p><div class="actions"><a href="../../data/directory.json" download>{t("下载全量 JSON","Download full JSON")}</a><a href="../../data/directory.csv" download>{t("下载全量 CSV","Download full CSV")}</a><a href="../project-sources/">{t("查看 200 个项目来源","Browse 200 project sources")} ↗</a><a href="../scoring/">{t("评分方法","Scoring method")} ↗</a></div></section>
<aside class="boundary"><b>{t("先理解 1–5 分","Understand the 1–5 score")}</b><p>{t("这是资料核查成熟度，不是热门度、项目质量、安全性或成功概率。E0 最多 2 分，E1 最多 3 分，E2 最多 4 分，只有已核验独立复现的 E3 才可能 5 分。","This is review maturity—not popularity, project quality, safety, or success probability. E0 is capped at 2, E1 at 3, E2 at 4, and only a verified independent reproduction at E3 can reach 5.")}</p></aside>
<form id="directory-filters" class="filters" role="search"><div class="search-field"><label for="directory-q">{t("搜索设备、型号、项目或来源","Search device, model, project, or source")}</label><input id="directory-q" type="search" placeholder="{t('例如 NAS、Kindle、AX3000T、ESPHome…','Try NAS, Kindle, AX3000T, ESPHome…')}" autocomplete="off"></div><div class="filter-grid"><label>{t("设备","Device")}<select id="directory-category"><option value="">{t("全部设备","All devices")}</option>{category_options}</select></label><label>{t("证据","Evidence")}<select id="directory-evidence"><option value="">{t("全部证据","All evidence")}</option>{evidence_options}</select></label><label>{t("最低核查分","Minimum review score")}<select id="directory-score"><option value="">{t("不限","Any score")}</option>{score_options}</select></label><label>{t("条目类型","Entry type")}<select id="directory-kind"><option value="">{t("全部类型","All types")}</option><option value="reviewed-project">{t("深审项目","Reviewed project")}</option><option value="project-source-lead">{t("E0 项目来源","E0 project source")}</option><option value="device-or-community-route">{t("设备或社区路线","Device/community route")}</option></select></label><label>{t("排序","Sort")}<select id="directory-sort"><option value="score-desc">{t("核查分：高到低","Review score: high to low")}</option><option value="title-asc">{t("名称：A–Z","Name: A–Z")}</option></select></label></div><div class="filter-bottom"><p id="directory-result-count" role="status" aria-live="polite">{t("显示","Showing")} {counts['entries']} / {counts['entries']}</p><div><button type="button" id="directory-share">{t("复制筛选链接","Copy filtered link")}</button><button type="reset">{t("清除筛选","Clear filters")}</button></div></div><span id="directory-share-status" role="status"></span></form>
<div id="directory-grid" class="project-grid">{''.join(card for _,_,card in all_cards)}</div><div id="directory-empty" class="empty" hidden><h3>{t("暂时没有匹配路线","No matching route")}</h3><p>{t("减少一个筛选条件，或换一个设备/型号词。","Remove a filter or try another device/model term.")}</p></div></div>'''
        self.page(t(f"全部 {counts['entries']} 条硬件复活记录",f"All {counts['entries']} hardware-revival records"),t("统一搜索设备、型号、项目、来源、证据等级和核查成熟度。","Search every device, model, project, source, evidence level, and review-maturity score."),body,"directory/index.html")

    def project_sources(self):
        t = self.t
        cards = []
        for project in PROJECTS:
            cards.append((PROJECT_SCORES[project["id"]]["score"], project["name"].casefold(), self.card(project, "../")))
        for lead in PROJECT_LEADS:
            cards.append((PROJECT_LEAD_SCORES[lead["id"]]["score"], lead["name"].casefold(), self.project_lead_card(lead, "../project-leads/")))
        cards.sort(key=lambda item: (-item[0], item[1]))
        category_options = "".join(f'<option value="{h(key)}">{h(value)}</option>' for key,value in self.labels["category"].items())
        body = f'''<div class="detail-wrap wide"><section class="detail-head"><p class="eyebrow">200 UNIQUE PROJECT REPOSITORIES</p><h1>{t("200 个独立项目来源","200 independent project sources")}</h1><p class="intro">{t(f"这里按仓库 URL 去重列出 {len(PROJECTS)} 个深审项目与 {len(PROJECT_LEADS)} 个 E0 GitHub 发现候选，合计正好 200 个独立项目来源。E0 只确认仓库存在、非 fork，并读取元数据与 README 入口；不表示具体设备兼容、安装成功或长期稳定。",f"This index deduplicates by repository URL: {len(PROJECTS)} reviewed projects plus {len(PROJECT_LEADS)} E0 GitHub discoveries, exactly 200 independent project sources. E0 confirms that a non-fork repository exists and that its metadata and README entry point were read; it does not establish device compatibility, installation success, or long-term stability.")}</p><div class="actions"><a href="../../data/project-leads.json" download>{t("下载 147 条 E0 JSON","Download 147 E0 JSON")}</a><a href="../../data/project-leads.csv" download>{t("下载 147 条 E0 CSV","Download 147 E0 CSV")}</a><a href="../directory/?kind=project-source-lead">{t("在全站目录只看 E0 项目来源","Show E0 project sources in full directory")} ↗</a></div></section>
<aside class="boundary"><b>{t("两层不能混写","Keep the layers separate")}</b><p>{t("53 个深审项目已读部署或适配来源，证据为 E1/E2；147 个发现候选全部保持 E0。两层都没有 KitAgain 实机测试，E3 仍为 0。","The 53 reviewed projects have deployment or compatibility sources reviewed at E1/E2; all 147 discoveries remain E0. Neither layer has KitAgain hands-on hardware tests, and E3 remains zero.")}</p></aside>
<form id="project-source-filters" class="filters" role="search"><div class="search-field"><label for="project-source-q">{t("搜索项目、设备范围或用途","Search project, hardware scope, or use")}</label><input id="project-source-q" type="search" placeholder="{t('例如 NAS、Kindle、camera、IoT…','Try NAS, Kindle, camera, IoT…')}" autocomplete="off"></div><div class="filter-grid"><label>{t("设备","Device")}<select id="project-source-category"><option value="">{t("全部设备","All devices")}</option>{category_options}</select></label><label>{t("证据","Evidence")}<select id="project-source-evidence"><option value="">{t("全部证据","All evidence")}</option><option value="E0">E0 · {t("发现候选","Discovery")}</option><option value="E1">E1 · {t("资料已读","Source reviewed")}</option><option value="E2">E2 · {t("作者实机证据","Author hardware evidence")}</option></select></label><label>{t("最低核查分","Minimum review score")}<select id="project-source-score"><option value="">{t("不限","Any score")}</option>{''.join(f'<option value="{n}">≥ {n}/5</option>' for n in range(1,6))}</select></label><label>{t("排序","Sort")}<select id="project-source-sort"><option value="score-desc">{t("核查分：高到低","Review score: high to low")}</option><option value="title-asc">{t("名称：A–Z","Name: A–Z")}</option></select></label></div><div class="filter-bottom"><p id="project-source-result-count" role="status" aria-live="polite">{t("显示","Showing")} {len(PROJECTS)+len(PROJECT_LEADS)} / {len(PROJECTS)+len(PROJECT_LEADS)}</p><button type="reset">{t("清除筛选","Clear filters")}</button></div></form>
<noscript><p>{t("JavaScript 未启用；全部 200 个来源仍可阅读并使用浏览器查找。","JavaScript is disabled; all 200 sources remain readable and searchable with browser Find.")}</p></noscript><div id="project-source-grid" class="project-grid">{''.join(card for _,_,card in cards)}</div><div id="project-source-empty" class="empty" hidden><h3>{t("暂时没有匹配项目来源","No matching project source")}</h3><p>{t("减少一个筛选条件，或换一个设备/用途词。","Remove a filter or try another device/use term.")}</p></div></div>'''
        self.page(t("200 个独立项目来源","200 independent project sources"),t("按仓库 URL 去重的硬件复活项目来源，明确区分 E0 发现候选与 E1/E2 深审项目。","Hardware-revival project sources deduplicated by repository URL, with E0 discoveries separated from E1/E2 reviewed projects."),body,"project-sources/index.html")

        for lead in PROJECT_LEADS:
            summary = lead["summary_zh" if self.lang == "zh" else "summary_en"]
            device_scope = lead["device_scope_zh" if self.lang == "zh" else "device_scope_en"]
            use_case = lead["use_case_zh" if self.lang == "zh" else "use_case_en"]
            reason = lead["reason_zh" if self.lang == "zh" else "reason_en"]
            archive_state = t("是；上游仓库已归档", "Yes; the upstream repository is archived") if lead["archived"] else t("否；核查时未归档", "No; not archived when checked")
            license_value = lead["license_spdx"] or t("待核实 / UNKNOWN", "Unknown / UNKNOWN")
            github_description = lead["github_description"] or t("GitHub API 未返回描述；不作补写。", "GitHub API returned no description; none was inferred.")
            sections = f'''<p class="muted">{h(lead["content_id"])} · E0 · {t("GitHub 元数据与 README 入口核查","GitHub metadata and README entry checked")} {h(lead["checked_at"])}</p>{self.rating_detail(PROJECT_LEAD_SCORES[lead["id"]], "../../scoring/")}<aside class="lead-verdict"><p class="eyebrow">E0 / DISCOVERY ONLY</p><div class="decision-grid"><div><b>{t("它可能解决什么","Candidate use")}</b><p>{h(use_case)}</p></div><div><b>{t("先核对哪些设备","Hardware to check")}</b><p>{h(device_scope)}</p></div></div></aside><h2>{t("目前知道什么","What is known")}</h2><p>{h(summary)}</p><p class="muted">{h(github_description)}</p><h2>{t("为什么仍是 E0","Why this remains E0")}</h2><p>{h(reason)}</p><aside class="boundary"><b>{t("动手前的停止条件","Stop condition before building")}</b><p>{t("如果找不到与你的准确型号、硬件修订、固件版本相符的安装与恢复资料，不要仅凭此页面刷写、拆机或购买配件。","Do not flash, disassemble, or buy parts from this page alone if you cannot find installation and recovery material matching your exact model, hardware revision, and firmware.")}</p></aside><h2>{t("仓库快照","Repository snapshot")}</h2><dl class="spec-grid"><div><dt>{t("归档","Archived")}</dt><dd>{h(archive_state)}</dd></div><div><dt>{t("最后 push","Last push")}</dt><dd>{h(lead["pushed_at"])}</dd></div><div><dt>{t("默认分支","Default branch")}</dt><dd>{h(lead["default_branch"])}</dd></div><div><dt>{t("API 许可证标识","API license identifier")}</dt><dd>{h(license_value)}</dd></div></dl><p>{t("许可证字段仅是 GitHub API 快照；不自动覆盖固件、模型、图片、商标或第三方组件。最后 push 与未归档状态也不能证明你的设备兼容。","The license field is only a GitHub API snapshot; it does not automatically cover firmware, models, images, trademarks, or third-party components. A recent push or unarchived state also does not prove compatibility.")}</p><div class="actions">{self.link(lead["repo_url"],t("打开上游仓库","Open upstream repository")+" ↗")}<a href="../../project-sources/">{t("返回 200 个项目来源","Back to 200 project sources")} ↗</a></div>'''
            self.article(lead["name"], summary, sections, f"project-leads/{lead['id']}/index.html")

    def leads(self):
        cards = "".join(self.lead_card(slug,lead,"") for slug,lead in WATCHLIST.items())
        reviewed_count = sum(lead.get("evidence_level") == "E1" for lead in WATCHLIST.values())
        e0_count = len(WATCHLIST) - reviewed_count
        source_names = lambda lead: ({"恩山无线论坛":"Enshan Wireless Forum", "ophub 中文项目文档":"ophub Chinese documentation"}.get(lead["source_platform"], lead["source_platform"]) if self.lang == "en" else lead["source_platform"])
        sources = collections.Counter(source_names(lead) for lead in WATCHLIST.values())
        source_options = "".join(f'<option value="{h(source)}">{h(source)} ({count})</option>' for source,count in sources.most_common())
        intro = self.t(
            f"这里汇集 {len(WATCHLIST)} 条设备与社区路线，来源包括中文论坛、X、作者网站、制作社区以及 ESPHome、Tasmota、postmarketOS 等上游设备库。其中 {reviewed_count} 条已读取具体型号资料并标为 E1，另有 {e0_count} 条 E0 待继续核查；E1 仍不等于 KitAgain 实机验证。",
            f"This section contains {len(WATCHLIST)} device and community routes from Chinese forums, X, author sites, maker communities and upstream databases such as ESPHome, Tasmota and postmarketOS. {reviewed_count} exact-model sources have been read and marked E1; {e0_count} remain E0. E1 still does not mean KitAgain tested the hardware."
        )
        search = f'<form id="lead-filters" class="filters" role="search"><div class="search-field"><label for="lead-q">{self.t("搜索设备、型号或来源","Search device, model or source")}</label><input id="lead-q" type="search" placeholder="{self.t("例如 AX3000T、N1、ESPHome…","Try AX3000T, N1, ESPHome…")}" autocomplete="off"></div><div class="filter-grid"><label>{self.t("来源","Source")}<select id="lead-source"><option value="">{self.t("全部来源","All sources")}</option>{source_options}</select></label><label>{self.t("证据","Evidence")}<select id="lead-evidence"><option value="">{self.t("全部证据","All evidence")}</option><option value="E1">E1 · {self.t("具体型号资料已读","Exact-model source reviewed")}</option><option value="E0">E0 · {self.t("待继续核查","Further review needed")}</option></select></label><label>{self.t("最低核查分","Minimum review score")}<select id="lead-score"><option value="">{self.t("不限","Any score")}</option>{"".join(f"<option value=\"{n}\">≥ {n}/5</option>" for n in range(1,6))}</select></label><label>{self.t("排序","Sort")}<select id="lead-sort"><option value="default">{self.t("默认顺序","Default order")}</option><option value="score-desc">{self.t("核查分：高到低","Review score: high to low")}</option><option value="title-asc">{self.t("名称：A–Z","Name: A–Z")}</option></select></label></div><div class="filter-bottom"><p id="lead-result-count" role="status" aria-live="polite">{self.t("显示","Showing")} {len(WATCHLIST)} / {len(WATCHLIST)}</p><button type="reset">{self.t("清除筛选","Clear filters")}</button></div></form>'
        sections = f'<aside class="boundary"><b>{self.t("先看证据等级","Check the evidence level")}</b><p>{self.t("E1 表示已经读取具体型号的配置或维护记录；E0 表示目前只确认了设备与来源之间的联系。两者都需要在动手前核对准确型号、硬件修订和恢复方式。","E1 means an exact-model configuration or maintainer record was read. E0 means only the device/source connection is established. Both still require exact model, hardware revision and recovery checks before action.")}</p></aside>{search}<div id="lead-grid" class="project-grid">{cards}</div><div id="lead-empty" class="empty" hidden><h3>{self.t("暂时没有匹配设备","No matching device")}</h3><p>{self.t("换一个型号、品牌或来源词试试。","Try another model, brand or source term.")}</p></div>'
        self.article(self.t("设备图谱与社区线索","Device atlas and community leads"),intro,sections,"leads/index.html")
        for slug,lead in WATCHLIST.items():
            v = lead[self.lang]
            details = WATCHLIST_DETAILS[slug]
            decision = details[self.lang]
            evidence = lead.get("evidence_level", "E0")
            sections = self.hardware_tags(self.lead_hardware_values(slug,lead),"../","lead-grid")
            sections += f'<p class="muted">{h(lead["content_id"])} · {evidence} · {self.t("资料核查","Sources reviewed")} {h(lead["reviewed_at"])} · {self.t("未进行实机测试","No hands-on hardware tests")}</p>'
            sections += self.rating_detail(LEAD_SCORES[slug], "../../scoring/")
            if lead.get("deep_review"):
                review = lead["deep_review"][self.lang]
                sections += f'<aside class="lead-verdict"><p class="eyebrow">{self.t("具体型号资料已读","EXACT-MODEL SOURCE REVIEWED")}</p><div class="decision-grid"><div><b>{self.t("硬件确认","Hardware")}</b><p>{h(review["hardware"])}</p></div><div><b>{self.t("改造路线","Installation route")}</b><p>{h(review["route"])}</p></div><div><b>{self.t("可以做到什么","Expected result")}</b><p>{h(review["result"])}</p></div><div><b>{self.t("不能扩大解释的边界","Boundary")}</b><p>{h(review["boundary"])}</p></div></div><p><b>{self.t("恢复与停止条件","Recovery and stop condition")}</b> {h(review["recovery"])}</p><small>{self.t("上游版本","Upstream revision")} {h(lead["upstream_revision"])}</small></aside>'
            sections += f'<aside class="lead-verdict"><p class="eyebrow">{self.t("先判断是否值得继续","DECIDE BEFORE YOU BUILD")}</p><div class="decision-grid"><div><b>{self.t("当前阶段","Current stage")}</b><p>{h(decision["stage"])}</p></div><div><b>{self.t("现在能用到什么程度","Practical readiness")}</b><p>{h(decision["usable"])}</p></div></div></aside>'
            sections += f'<h2>{self.t("适用设备与不能这样用的情况","Device fit and limits")}</h2><div class="before-after"><div><h3>{self.t("已知可参考或可继续核查","Known fit or worth checking")}</h3>{ul(decision["works_for"])}</div><div><h3>{self.t("不能视为已支持","Not established or unsuitable")}</h3>{ul(decision["not_for"])}</div></div>'
            sections += f'<h2>{self.t("对用户有什么价值","Why this lead is useful")}</h2><p>{h(decision["value"])}</p><aside class="boundary"><b>{self.t("是否值得继续跟进","Should you continue?")}</b><p>{h(decision["follow"])}</p></aside>'
            gap_heading = self.t("E1 还没有证明什么", "What E1 still does not prove") if evidence == "E1" else self.t("为什么仍是 E0", "Why it remains E0")
            sections += f'<h2>{gap_heading}</h2><p>{h(v["gap"])}</p>'
            sections += f'<h2>{self.t("下一步核验","Next review step")}</h2><p>{h(v["next_check"])}</p>'
            sections += f'<h2>{self.t("风险与停止条件","Risk and stop condition")}</h2><p>{h(v["safety"])}</p>'
            resources = "".join(f'<li><div class="resource-head">{self.link(item["url"], item[self.lang+"_label"]+" ↗")}<span>{h(item["kind"])}</span></div><p>{h(item[self.lang+"_note"])}</p><small>{h(item["url"])}</small></li>' for item in details["resources"])
            sections += f'<h2>{self.t("链接里分别有什么","What each link contains")}</h2><ul class="resource-list">{resources}</ul>'
            sections += f'<p><a href="../">{self.t("返回全部社区线索","Back to all field leads")} ↗</a></p>'
            self.article(v["title"],v["summary"],sections,f"leads/{slug}/index.html")

GUIDES = json.loads((ROOT / "data/guides.json").read_text(encoding="utf-8"))
ARTICLES = json.loads((ROOT / "data/articles.json").read_text(encoding="utf-8"))
WATCHLIST, WATCHLIST_DETAILS = load_watchlist(ROOT / "data")
AUTHOR_SOCIALS = json.loads((ROOT / "data/author-socials.json").read_text(encoding="utf-8"))
PROJECT_SCORES, LEAD_SCORES, PROJECT_LEAD_SCORES = score_all(PROJECTS, WATCHLIST, WATCHLIST_DETAILS, PROJECT_LEADS)
DIRECTORY_EXPORT = build_directory_export(
    projects=PROJECTS,
    project_leads=PROJECT_LEADS,
    watchlist=WATCHLIST,
    details=WATCHLIST_DETAILS,
    base_url=BASE,
    version=CONFIG["version"],
    generated_at=DATA["compiled_at"],
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
    entry = re.sub(r'(href|src)="([^"]+)"',from_english_home,entry)
    entry = entry.replace('class="brand" href="en/index.html"','class="brand" href="index.html"')
    entry = entry.replace('href="en/index.html#catalog"','href="#catalog"')
    write(OUT/"index.html",entry)
    urls = [""]+[p for p in PATHS if p != "en/"]
    write(OUT/"sitemap.xml",'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f"<url><loc>{h(BASE+p)}</loc></url>" for p in urls)+"\n</urlset>\n")
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
