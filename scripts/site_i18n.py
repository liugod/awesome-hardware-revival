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
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
CONFIG = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
BASE = CONFIG["base_url"].rstrip("/") + "/"
REPO = CONFIG["repository_url"]
assert urlsplit(BASE).scheme == "https" and not urlsplit(BASE).query and not urlsplit(BASE).fragment
DATA = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
DEEP = json.loads((ROOT / "data/deep-dives.json").read_text(encoding="utf-8"))
EN = json.loads((ROOT / "data/i18n/en.json").read_text(encoding="utf-8"))
DEEP_EN = json.loads((ROOT / "data/i18n/deep-dives.en.json").read_text(encoding="utf-8"))
PROJECTS = DATA["projects"]
DATE = DATA["compiled_at"][:10]
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
        canonical = BASE + f"{self.lang}/" + ("" if tail == "index.html" else tail.removesuffix("index.html"))
        other = "en" if self.lang == "zh" else "zh"
        target = f"{other}/{tail}"
        rel = lambda x: self.rel(x, current)
        brand = "KitAgain"
        alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{BASE}{lang}/{"" if tail == "index.html" else tail.removesuffix("index.html")}">' for lang,code in [("zh","zh-CN"),("en","en")])
        alternates += f'<link rel="alternate" hreflang="x-default" href="{BASE}">'
        markup = f"""<!doctype html>
<html lang="{self.t('zh-CN','en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)} · {brand}</title><meta name="description" content="{h(description)}">
<link rel="canonical" href="{h(canonical)}">{alternates}<meta name="theme-color" content="#f5f3eb">
<meta property="og:title" content="{h(title)} · {brand}"><meta property="og:description" content="{h(description)}"><meta property="og:url" content="{h(canonical)}"><meta property="og:type" content="website">
<link rel="icon" href="{rel('assets/mark.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{rel('assets/style.css')}"><script src="{rel('assets/app.js')}" defer></script>
</head><body><a class="skip" href="#main">{self.t('跳到正文','Skip to content')}</a>
<header class="site-header"><a class="brand" href="{rel(self.lang+'/index.html')}"><span class="brand-mark">↻</span><span>{brand}<small>HARDWARE REVIVAL FIELD GUIDE</small></span></a>
<nav aria-label="{self.t('主导航','Main navigation')}"><a href="{rel(self.lang+'/index.html')}#catalog">{self.t('项目目录','Catalog')}</a><a href="{rel(self.lang+'/research/index.html')}">{self.t('研究方法','Method')}</a><a href="{rel(self.lang+'/community/index.html')}">{self.t('参与社区','Community')}</a><a class="language-switch" href="{rel(target)}" lang="{other}" hreflang="{other}">{self.t('English','简体中文')}</a></nav></header>
<main id="main">{body}</main><footer><p>{self.t('让仍能工作的硬件，找到下一份工作。','Give working hardware its next job.')}</p><div>{self.t('资料核查','Sources reviewed')} {DATE} · v{CONFIG['version']} · {self.t('未进行实机测试','No hands-on hardware tests')}<br>
<a href="{rel('data/catalog.json')}" download>{self.t('中文 JSON','Source JSON (Chinese)')}</a> / <a href="{rel('data/catalog.en.json')}" download>English JSON</a> / <a href="{rel('data/catalog'+('.en' if self.lang=='en' else '')+'.csv')}" download>CSV</a> / <a href="{REPO}">GitHub ↗</a><br>{self.t('原创文字与目录 CC BY 4.0 · 站点代码 MIT · 第三方项目按各自许可','Original text & catalog: CC BY 4.0 · Site code: MIT · Third-party projects: their own licenses')}</div></footer></body></html>"""
        write(OUT / current, markup)
        if not legacy:
            PATHS.append(f"{self.lang}/" + ("" if tail == "index.html" else tail.removesuffix("index.html")))

    def link(self, url, text):
        return f'<a href="{h(url)}">{h(text)}</a>' if url else h(text) + self.t("（无已核验链接）"," (no verified link)")

    def tags(self, p):
        return '<div class="tags">' + "".join(f"<span>{h(v)}</span>" for v in [
            self.labels["category"][p["category"]], self.labels["ai"][p["ai_relation"]],
            self.labels["difficulty"][p["difficulty"]], p["evidence"]["level"]]) + "</div>"

    def card(self, p, prefix=""):
        e = localized(p, "en")
        v = localized(p, self.lang)
        attrs = {"id":p["id"],"category":p["category"],"ai":p["ai_relation"],"difficulty":p["difficulty"],"evidence":p["evidence"]["level"],"use":"|".join(USE_IDS[u] for u in p["use_cases"])}
        search = " ".join([p["name"], p["summary_zh"], p["device_scope"], e["summary"], e["device_scope"], *p["keywords"], *p["model_examples"], *p["use_cases"], *(en for uid,zh,en in USES if zh in p["use_cases"])])
        attrs["search"] = search
        attr = " ".join(f'data-{k}="{h(v)}"' for k,v in attrs.items())
        return f"""<article class="project" {attr}>{self.tags(p)}<h3><a href="{prefix}projects/{p['id']}/">{h(p['name'])} ↗</a></h3><p class="summary">{h(v['summary'])}</p><p class="device"><b>{self.t('适配范围','Device scope')}</b>{h(v['device_scope'])}</p><p class="limit">{h(v['limitations'][0])}</p><div class="card-end"><span class="status {'attention' if p['maintenance']['status'] != 'not-archived' else ''}">{h(self.labels['maintenance'][p['maintenance']['status']])}</span><span>{h(v['method'])}</span></div></article>"""

    def home(self):
        t = self.t
        options = lambda group: "".join(f'<option value="{h(k)}">{h(v)}</option>' for k,v in group.items())
        groups = [
            ("category",t("设备","Device"),self.labels["category"]),("use",t("用途","Use"),{uid:t(zh,en) for uid,zh,en in USES}),
            ("ai",t("AI 关系","AI relationship"),self.labels["ai"]),("difficulty",t("难度","Difficulty"),self.labels["difficulty"]),
            ("evidence",t("证据","Evidence"),{k:v for k,v in self.labels["evidence"].items() if k in {"E1","E2"}})]
        filters = "".join(f'<label>{label}<select id="{key}" name="{key}"><option value="">{t("全部","All")}</option>{options(values)}</select></label>' for key,label,values in groups)
        topics = "".join(f'<a class="feature" href="guides/{gid}/"><span class="serial">0{i+1} / {t("路线比较","ROUTE COMPARISON")}</span><h3>{h(g[self.lang]["title"])}</h3><p>{h(g[self.lang]["intro"])}</p><span class="text-link">{t("查看条件与选择依据","Compare requirements and routes")} ↗</span></a>' for i,(gid,g) in enumerate(GUIDES.items()))
        body = f"""<section class="hero"><div class="hero-copy"><p class="eyebrow">OPEN HARDWARE, SECOND LIVES</p><h1>{t('旧设备，<br>还可以做点什么？','Old hardware.<br>A new purpose.')}</h1><p class="intro">{t('从闲置音箱到旧 Kindle，从停服机器人到缺驱动的打印机。按手里的设备找方案，先看适配条件，再决定是否动手。','From idle speakers and old Kindles to service-dependent robots and unsupported printers. Find a route for the device you own, then check compatibility before getting started.')}</p><a class="primary" href="#catalog">{t('寻找你的设备','Find your device')} ↓</a><a class="secondary" href="research/">{t('先看我们如何核查','How we review evidence')} ↗</a></div>
<aside class="field-note"><span class="eyebrow">FIELD NOTES / 001</span><div class="big-count">{len(PROJECTS)}<span>{t('条公开项目与工具','public projects and tools')}</span></div><dl><div><dt>{t('设备类别','Device categories')}</dt><dd>{len(self.labels['category'])}</dd></div><div><dt>{t('重点案例分析','Case analyses')}</dt><dd>{len(DEEP)}</dd></div><div><dt>{t('独立实机复现','Verified independent reproductions')}</dt><dd>0</dd></div></dl><p>{t('这是有来源的研究目录。收录不等于兼容认证或实机测试。','A source-backed research directory. Inclusion is not compatibility certification or hands-on testing.')}</p><small>LAST REVIEWED {DATE}</small></aside></section>
<div class="facts-strip">{''.join(f'<span><b>{sum(p["ai_relation"]==key for p in PROJECTS)}</b>{h(label)}</span>' for key,label in self.labels['ai'].items())}</div>
<section class="featured"><div class="section-heading"><p class="eyebrow">{t('从设备出发','START WITH YOUR DEVICE')}</p><h2>{t('三条值得先了解的路径','Three routes to explore')}</h2></div><div class="feature-grid">{topics}</div></section>
<section id="catalog" class="catalog"><div class="section-heading"><h2>{t('项目目录','Project catalog')} <span class="muted">/ {len(PROJECTS)}</span></h2><p>{t('先按设备缩小范围，再核对型号、固件与恢复路径。','Narrow by device, then check model, firmware and recovery requirements.')}</p></div>
<form id="filters" class="filters" role="search"><div class="search-field"><label for="q">{t('搜索设备、型号或项目（支持中英文）','Search devices, models or projects (Chinese or English)')}</label><input id="q" name="q" type="search" placeholder="{t('例如 Kindle、LX06、打印机…','Try Kindle, LX06, printer…')}" autocomplete="off"></div>
<div class="filter-grid">{filters}</div><div class="filter-bottom"><p id="result-count" role="status" aria-live="polite">{t('显示','Showing')} {len(PROJECTS)} / {len(PROJECTS)}</p><div><button type="button" id="share">{t('复制筛选链接','Copy filtered link')}</button><button type="reset">{t('清除筛选','Clear filters')}</button></div></div><span id="share-status" role="status"></span></form>
<p class="evidence-note">{t('E1 = 已读源码与部署文档 · E2 = 作者实机陈述或演示 · 本轮没有 E3 独立复现。难度为编辑判断；成本未核价。','E1 = source and deployment docs reviewed · E2 = author hardware claim or demonstration · No E3 independent reproduction. Difficulty is editorial judgment; prices are unknown.')}</p>
<noscript><p>{t('JavaScript 未启用；仍可阅读完整目录并使用浏览器查找。','JavaScript is disabled. The full catalog is readable; use your browser’s Find command.')}</p></noscript>
<div id="project-grid" class="project-grid">{''.join(self.card(p) for p in PROJECTS)}</div>
<div id="empty" class="empty" hidden><h3>{t('暂时没有匹配条目','No matching entries')}</h3><p>{t('减少筛选条件，或提交设备线索。','Try fewer filters, or contribute a device lead.')}</p><a href="contribute/">{t('提交线索','Contribute a lead')} ↗</a></div></section>
<section class="closing"><div><p class="eyebrow">KEEP THE EVIDENCE OPEN</p><h2>{t('你成功复活了一台设备？','Brought a device back to use?')}</h2><p>{t('准确型号、固件、失败条件和恢复经验，都值得记录。','Exact models, firmware, failure conditions and recovery experience all matter.')}</p></div><a class="primary" href="contribute/">{t('贡献复现记录','Contribute a report')} ↗</a></section>"""
        self.page(t("旧设备还能做什么？","What can old hardware do next?"),t("按设备、用途、AI、难度与证据筛选旧硬件再利用方案。","Find hardware reuse routes by device, use, AI relationship, difficulty and evidence."),body)

    def detail(self, p, legacy=False):
        t = self.t
        v = localized(p, self.lang)
        d = (DEEP_EN if self.lang == "en" else DEEP).get(p["id"])
        current = f"projects/{p['id']}.html" if legacy else f"{self.lang}/projects/{p['id']}/index.html"
        rel = lambda x: self.rel(x, current)
        extra = ""
        if d:
            extra = f'<section class="prose" id="analysis"><h2>{t("这台设备发生了什么变化","What changes for this device")}</h2><div class="before-after"><div><h3>{t("原本的限制","Before")}</h3><p>{h(d["before"])}</p></div><div><h3>{t("新的用途","After")}</h3><p>{h(d["after"])}</p></div></div><p>{h(d["analysis"])}</p><h3>{t("适合谁","A good fit for")}</h3><p>{h(d["fit"])}</p><h3>{t("哪些情况先不要选","Not a good fit for")}</h3><p>{h(d["not_fit"])}</p><h3>{t("建议复现验收步骤","Proposed reproduction checks")}</h3>{ul(d["acceptance"])}<p class="muted">{t("这些硬件步骤尚未由本目录执行。","These hardware checks have not been performed by this catalog.")}</p></section>'
        specs = [(t("改造方式","Method"),v["method"]), (t("难度（编辑判断）","Difficulty (editorial judgment)"),self.labels["difficulty"][p["difficulty"]])]
        specs += [(t(zh,en), t(*REQS[p["requirements"][key]])) for key,zh,en in [("disassembly","拆机","Disassembly"),("soldering","焊接","Soldering"),("cloud_api","云 API / 服务","Cloud API / service")]]
        specs += [(t("成本金额","Cost amount"),t("待核价 / UNKNOWN","Not priced / UNKNOWN"))]
        sources = "".join(f'<li>{self.link(s["url"],t(*SOURCE_KINDS[s["kind"]]))} · {s["checked_at"][:10]} · {t("已读内容","Content reviewed")}</li>' for s in p["sources"])
        sources += "".join(f'<li>{self.link(s["url"],t("X 作者原帖","Original author X post"))} · {t("已读正文，未核验视频画面","Text read; video frames not verified")}</li>' for s in p["x_sources"])
        license_label = p["license"]["label"] if self.lang=="zh" else LICENSE_EN.get(p["license"]["label"],p["license"]["label"])
        types = {"case":t("具体改造路线","Specific modification route"),"platform":t("平台 / 多机型工程","Platform / multi-device project"),"prerequisite":t("前置工具","Prerequisite tool")}
        body = f"""<div class="detail-wrap"><a class="back" href="{rel(self.lang+'/index.html')}#catalog">← {t('返回项目目录','Back to catalog')}</a><section class="detail-head">{self.tags(p)}<h1>{h(p['name'])}</h1><p class="intro">{h(v['summary'])}</p><p class="muted">{types[p['entry_type']]} · {t('家族','Family')} {h(p['family'])} · {t('核查','Reviewed')} {p['checked_at'][:10]}</p><div class="actions">{self.link(p['repo_url'],t('源码仓库','Source repository')+' ↗')}{self.link(p['tutorial_url'],t('原始教程','Original tutorial')+' ↗')}{self.link(p['compatibility_url'],t('型号适配依据','Compatibility source')+' ↗')}</div></section>
<aside class="boundary"><b>{t('先确认边界','Check the boundaries first')}</b><p>{h(v['device_scope'])}</p>{ul(v['limitations'])}<p>{t('固件','Firmware')}: {h(v['firmware_requirement'] or t('待核实','Unknown'))} · {t('地区要求','Region requirement')}: {h(v['region_requirement'] or t('待核实','Unknown'))}</p></aside>{extra}
<section class="prose"><h2>{t('动手需要什么','What you need')}</h2><dl class="spec-grid">{''.join(f'<div><dt>{h(k)}</dt><dd>{h(val)}</dd></div>' for k,val in specs)}</dl><h3>{t('可能需要的额外投入','Possible additional costs')}</h3>{ul(v['cost_items'])}<p>{t('未核价；开源许可证不代表硬件、托管、电力和云服务总成本为零。','Prices have not been checked. An open-source license does not make hardware, hosting, electricity or cloud services free.')}</p>
<h2>{t('风险与恢复','Risks and recovery')}</h2><p>{t('数据风险','Data-loss risk')}: {h(t(*RISKS[p['risk']['data_loss']]))}; {t('设备失效风险','Bricking risk')}: {h(t(*RISKS[p['risk']['bricking']]))}. {t('按路径给出的提示，未实测，不表示每台设备必然发生。','Route-based guidance, not hardware-tested; these outcomes are not inevitable for every device.')}</p><p>{h(v['recovery'])}</p><p>{self.link(p['risk']['recovery_url'],t('恢复资料','Recovery documentation'))}</p>
<h2>{t('证据与维护状态','Evidence and maintenance')}</h2><p><b>{p['evidence']['level']} · {h(self.labels['evidence'][p['evidence']['level']])}</b></p><p>{h(v['evidence_reason'])}</p><p>{t('本目录实机测试：未进行。独立复现：未核验。','Catalog hands-on testing: not performed. Independent reproduction: not verified.')}</p>
<dl class="spec-grid"><div><dt>{t('维护状态','Maintenance')}</dt><dd>{h(self.labels['maintenance'][p['maintenance']['status']])}</dd></div><div><dt>{t('GitHub 最后 push','Last GitHub push')}</dt><dd>{h(p['maintenance']['last_push_at'] or t('待核实','Unknown'))}</dd></div><div><dt>{t('仓库许可证','Repository license')}</dt><dd>{self.link(p['license']['url'],license_label)}</dd></div></dl>
<p>{t('未归档或近期 push 不能证明型号无故障；镜像迁移也不等于停止维护。','An unarchived repository or recent push does not prove a model works. Mirror migration does not mean development has stopped.')}</p><p>{t('根许可证或 README 声明不代表固件、模型、品牌和第三方组件均采用相同许可。','A root license or README declaration does not establish the same license for firmware, models, brands and third-party components.')}</p>
<h2>{t('逐项来源','Sources')}</h2><ul class="sources">{sources}</ul><p>{t('原始来源可能使用中文或英文。核查为公开资料阅读；操作前请重新核对上游的型号、服务与固件。','Original sources may be in Chinese or English. Review means reading public material; recheck upstream models, services and firmware before acting.')}</p><div class="actions"><a href="{rel(self.lang+'/contribute/index.html')}?project={p['id']}">{t('补充或纠错','Contribute or correct')} ↗</a><a href="{rel(self.lang+'/community/index.html')}?project={p['id']}">{t('讨论与复现入口','Discussion and reproduction')} ↗</a></div></section></div>"""
        self.page(p["name"]+t("：适配设备与复现条件",": compatibility and reproduction"),v["summary"]+" "+v["device_scope"],body,f"projects/{p['id']}/index.html",current if legacy else None)

    def article(self, title, intro, sections, tail):
        body = f'<div class="detail-wrap"><section class="detail-head"><h1>{h(title)}</h1><p class="intro">{h(intro)}</p></section><section class="prose">{sections}</section></div>'
        self.page(title,intro,body,tail)

    def supporting(self):
        t = self.t
        method = f"""<h2>{t('收录意味着什么','What inclusion means')}</h2><p>{t('E1：已读源码与部署文档，50 条。E2：作者实机陈述或演示，3 条。E3：独立复现，0 条。本目录实机测试 0 条。','E1: source and deployment documentation reviewed, 50 entries. E2: author hardware claims or demonstrations, 3. E3: verified independent reproduction, 0. Catalog hands-on hardware tests: 0.')}</p>
<h2>{t('我们如何核查','How we review')}</h2><p>{t('以设备和失效原因寻找原始仓库、安装文档、型号表及作者原帖。保存来源、时间和内容哈希；搜索摘要只作线索。型号、固件、地区未知时保留未知，不把未归档等同持续可用。','We look for original repositories, installation instructions, model tables and author posts by device and failure mode. Source URLs, dates and content hashes are retained; search snippets are leads only. Unknown model, firmware or region requirements stay unknown. An unarchived project is not proof of continued usability.')}</p>
<h2>{t('AI 关系与项目家族','AI relationships and project families')}</h2><p>{t('AI 功能改造、AI 辅助开发/配置、AI 周边用途和传统基础设施分开标注。同家族后继版本不是独立复现，平台与前置工具也不是完成的改造案例。','AI functionality, documented AI-assisted development/setup, AI-adjacent uses and traditional infrastructure are separate categories. Successor versions in one family are not independent reproductions; platforms and prerequisite tools are not completed modification cases.')}</p>
<h2>{t('证据的空白','Evidence gaps')}</h2><p>{t('没有长期耗电、稳定性或恢复实测；成本未核价。难度是编辑判断。X 阅读集中于两个案例家族，不声称穷尽搜索或核验视频。','There are no long-term power, stability or recovery tests, and costs are not priced. Difficulty is editorial judgment. X reading covers two case families; neither exhaustive search nor video verification is claimed.')}</p>
<h2>{t('双语同步','Translation discipline')}</h2><p>{t('两种语言共享稳定 ID 与事实字段。译文记录源内容哈希；源文变动后必须复核，不能把翻译日期当作上游重新核查日期。','Both languages share stable IDs and factual fields. Translations record a source-content hash and must be reviewed when the source changes. Translation dates are not fresh upstream verification dates.')}</p><p><a href="../contribute/">{t('贡献方法与核验流程','Contribution and review process')} ↗</a></p>"""
        self.article(t("先看证据，再谈复活。","Evidence before revival."),t("有来源，也明确记录未知项。","Traceable sources and explicit unknowns."),method,"research/index.html")
        contribute = f"""<h2>{t('提交什么','What to include')}</h2>{ul([t('项目 ID、准确型号、硬件修订、固件与地区','Project ID, exact model, hardware revision, firmware and region'),t('上游版本、操作日期及原始步骤链接','Upstream version, operation date and original instructions'),t('成功与失败功能、恢复结果及可核验材料','Working and failed functions, recovery results and verifiable evidence'),t('不要公开设备唯一序列号、账号、令牌或密钥','Do not publish unique serial numbers, accounts, tokens or secrets')])}
<h2>{t('资料如何进入目录','How reports enter the catalog')}</h2><p>{t('提交后先标为待核验。编辑检查来源与型号条件，再同步中英文；没有独立证据就不升级为 E3。失败记录同样有价值。','Submissions begin as unverified. Editors check sources and exact device conditions, then update both languages. No E3 upgrade without independent evidence. Failure reports are valuable too.')}</p><p id="project-context" class="boundary" hidden></p>
<p>{self.link(REPO+'/issues/new/choose',t('提交项目、纠错或复现记录','Submit a project, correction or reproduction report'))} ↗</p><p>{t('社区仍在准备中，当前提交入口是 GitHub Issues，需要 GitHub 账号。','The community is still being prepared. Current submissions use GitHub Issues and require a GitHub account.')}</p>"""
        self.article(t("贡献一份可靠记录","Contribute a reliable record"),t("成功、失败和不支持条件，都值得保留。","Keep successes, failures and unsupported conditions."),contribute,"contribute/index.html")
        categories = [t("求助与问答","Help & Questions"),t("成功与失败复现","Build Reports"),t("项目发现与改进","Projects & Ideas"),t("公告与社区使用","Announcements & Community")]
        community = f"""<aside class="boundary"><b>{t('社区筹备中','Community in preparation')}</b><p>{t('独立论坛尚未开放。主站可直接阅读，不需要注册。','The independent forum is not open yet. Reading the main site does not require registration.')}</p></aside>
<h2>{t('计划开放的四类讨论','Four planned discussion areas')}</h2>{ul(categories)}
<h2>{t('中文和英文都欢迎','Chinese and English welcome')}</h2><p>{t('使用你熟悉的语言，注明设备与项目 ID。优质经验经复核后可补充双语摘要。机器翻译需标明并保留原文，用户帖子不会自动成为目录认证。','Use the language you know and identify the device and project ID. Reviewed experience may receive a bilingual summary. Machine translations must be labeled with the original retained. User posts do not automatically become catalog certifications.')}</p>
<h2>{t('社区规则','Community rules')}</h2>{ul([t('尊重他人，讨论具体条件，不伪造成功或身份','Respect others; discuss exact conditions; do not fabricate success or identities'),t('保留来源，说明商业关系，避免无关推广','Keep sources, disclose commercial relationships and avoid unrelated promotion'),t('报告失败时记录版本、现象与恢复情况，不发布秘密或个人信息','When reporting failure, record versions, symptoms and recovery without secrets or personal information')])}
<p id="project-context" class="boundary" hidden></p><p><a id="contribute-link" href="../contribute/">{t('现在提交资料或纠错','Contribute or correct information now')} ↗</a></p>"""
        if CONFIG["community_url"]:
            raise ValueError("Community URL activation requires verified forum readiness; update this page deliberately.")
        self.article(t("一起让旧设备继续工作","Keep old devices working together"),t("用可核验的讨论积累经验。","Build experience through verifiable discussion."),community,"community/index.html")

    def guides(self):
        for gid, guide in GUIDES.items():
            g = guide[self.lang]
            sections = "".join(f"<h2>{h(title)}</h2>{ul(lines)}" for title,lines in g["sections"])
            sections += f'<h2>{self.t("对应项目与来源","Projects and sources")}</h2><div class="project-grid">' + "".join(self.card(next(p for p in PROJECTS if p["id"]==pid),"../../") for pid in guide["projects"])+"</div>"
            self.article(g["title"],g["intro"],sections,f"guides/{gid}/index.html")

GUIDES = json.loads((ROOT / "data/guides.json").read_text(encoding="utf-8"))

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
        s.home();s.supporting();s.guides()
        for p in PROJECTS:
            s.detail(p)
            if lang=="zh":s.detail(p,legacy=True)
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
    entry = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KitAgain · 旧设备的新用途 · Hardware Revival Field Guide</title><meta name="description" content="探索旧设备的新用途。Explore new uses for old hardware."><link rel="canonical" href="{BASE}"><link rel="alternate" hreflang="zh-CN" href="{BASE}zh/"><link rel="alternate" hreflang="en" href="{BASE}en/"><link rel="alternate" hreflang="x-default" href="{BASE}"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head><body><main id="main"><section class="hero"><div><p class="eyebrow">KITAGAIN / HARDWARE REVIVAL FIELD GUIDE / v{CONFIG['version']}</p><h1>旧设备，新的用途。<br><span lang="en">Old hardware.<br>A new purpose.</span></h1><p class="intro">53 条项目，12 篇分析，保留来源与适配边界。<br><span lang="en">53 projects, 12 case analyses, with sources and compatibility boundaries.</span></p><div class="actions"><a class="primary language-switch" href="zh/">简体中文 →</a><a class="primary language-switch" href="en/" lang="en">English →</a></div><p class="evidence-note">没有实机测试 / <span lang="en">No hands-on hardware testing.</span></p></div><aside class="field-note"><span class="brand-mark">↻</span><h2>让仍能工作的硬件，找到下一份工作。</h2><p lang="en">Give working hardware its next job.</p><a href="{REPO}">GitHub ↗</a></aside></section></main></body></html>"""
    write(OUT/"index.html",entry)
    urls = [""]+PATHS
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
    print(f"Bilingual build: {len(PATHS)} localized pages + language entry + 54 historical URLs.")
