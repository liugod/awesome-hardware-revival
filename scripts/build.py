"""Deterministic static site and editorial exports. Python 3.10+, standard library."""
import collections
import html
import json
import pathlib
import shutil
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
config = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
BASE = config["base_url"].rstrip("/") + "/"
REPO = config["repository_url"]
data = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
deep = json.loads((ROOT / "data/deep-dives.json").read_text(encoding="utf-8"))
candidates = json.loads((ROOT / "data/candidates.json").read_text(encoding="utf-8"))
projects = data["projects"]
labels = data["labels"]
DATE = data["compiled_at"][:10]

def h(value):
    return html.escape(str(value if value is not None else "待核实"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")

def link(url, text):
    return f'<a href="{h(url)}">{h(text)}</a>' if url else h(text) + "（无已核验链接）"

def items(values):
    return "<ul>" + "".join(f"<li>{h(v)}</li>" for v in values) + "</ul>"

def page(title, description, body, path="", level=0, script=False):
    prefix = "../" * level
    canonical = BASE + path
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)} · 老硬件复活指南</title><meta name="description" content="{h(description)}">
<link rel="canonical" href="{canonical}"><meta name="theme-color" content="#f5f3eb">
<meta property="og:title" content="{h(title)} · 老硬件复活指南"><meta property="og:description" content="{h(description)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="website">
<link rel="icon" href="{prefix}assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css">
{f'<script src="{prefix}assets/app.js" defer></script>' if script else ''}
</head><body><a class="skip" href="#main">跳到正文</a>
<header class="site-header"><a class="brand" href="{prefix}index.html"><span class="brand-mark">↻</span><span>老硬件复活指南<small>HARDWARE REVIVAL FIELD GUIDE</small></span></a>
<nav aria-label="主导航"><a href="{prefix}index.html#catalog">项目目录</a><a href="{prefix}research.html">研究方法</a><a href="{REPO}">GitHub ↗</a></nav></header>
<main id="main">{body}</main>
<footer><p>让仍能工作的硬件，找到下一份工作。</p><div>资料核查 {DATE} · v{h(data['version'])} · 未进行实机测试<br>
<a href="{prefix}data/catalog.json" download>JSON 数据</a> / <a href="{prefix}data/catalog.csv" download>CSV 数据</a> / <a href="{REPO}/blob/main/README.en.md">English</a> / <a href="{REPO}/issues/new/choose">补充与纠错</a><br>原创文字与目录 CC BY 4.0 · 站点代码 MIT · 第三方项目按各自许可</div></footer>
</body></html>"""

def tags(p):
    values = [labels["category"][p["category"]], labels["ai"][p["ai_relation"]],
              labels["difficulty"][p["difficulty"]], p["evidence"]["level"]]
    return '<div class="tags">' + "".join(f"<span>{h(v)}</span>" for v in values) + "</div>"

def card(p):
    attrs = {"id":p["id"],"category":p["category"],"ai":p["ai_relation"],"difficulty":p["difficulty"],"evidence":p["evidence"]["level"],"use":"|".join(p["use_cases"])}
    search = " ".join([p["name"], p["summary_zh"], p["device_scope"], *p["keywords"], *p["use_cases"]])
    attrtext = " ".join(f'data-{k}="{h(v)}"' for k,v in attrs.items())
    status = labels["maintenance"][p["maintenance"]["status"]]
    special = p["maintenance"]["status"] != "not-archived"
    return f"""<article class="project" {attrtext} data-search="{h(search)}">
{tags(p)}<h3><a href="projects/{p['id']}.html">{h(p['name'])}<span aria-hidden="true"> ↗</span></a></h3>
<p class="summary">{h(p['summary_zh'])}</p><p class="device"><b>适配范围</b> {h(p['device_scope'])}</p>
<p class="limit">{h(p['limitations'][0])}</p>
<div class="card-end"><span class="status {'attention' if special else ''}">{h(status)}</span><span>{h(p['method'])}</span></div>
</article>"""

def options(group):
    return "".join(f'<option value="{h(k)}">{h(v)}</option>' for k,v in group.items())

stats = collections.Counter(p["ai_relation"] for p in projects)
category_counts = collections.Counter(p["category"] for p in projects)
evidence_counts = collections.Counter(p["evidence"]["level"] for p in projects)
featured = ["onju-voice","printer-spl3","kindle-whoop"]
featured_html = ""
for i, pid in enumerate(featured,1):
    p = next(p for p in projects if p["id"] == pid)
    featured_html += f'<a class="feature" href="projects/{pid}.html"><span class="serial">0{i} / 案例拆解</span><h3>{h(p["name"])}</h3><p>{h(deep[pid]["before"])}</p><span class="text-link">阅读设备条件与复现边界 ↗</span></a>'
uses = {u:u for p in projects for u in p["use_cases"]}
body = f"""<section class="hero"><div class="hero-copy"><p class="eyebrow">OPEN HARDWARE, SECOND LIVES / 开源再利用</p>
<h1>旧设备，<br>还可以做点什么<span>？</span></h1>
<p class="intro">从闲置音箱到旧 Kindle，从停服机器人到缺驱动的打印机。<br>按手里的设备找方案，先看适配条件，再决定是否动手。</p>
<a class="primary" href="#catalog">寻找你的设备 <span>↓</span></a><a class="secondary" href="research.html">先看我们如何核查 ↗</a></div>
<aside class="field-note" aria-label="本期资料范围"><span class="eyebrow">FIELD NOTES / 001</span><div class="big-count">{len(projects)}<span>条公开项目与工具</span></div>
<dl><div><dt>设备类别</dt><dd>{len(category_counts)}</dd></div><div><dt>重点案例分析</dt><dd>{len(deep)}</dd></div><div><dt>独立实机复现</dt><dd>0</dd></div></dl><p>这是有来源的研究目录。<br>收录不等于兼容认证或实机测试。</p><small>LAST REVIEWED {DATE}</small></aside></section>
<div class="facts-strip"><span><b>{stats['native']}</b> AI 功能改造</span><span><b>{stats['assisted']}</b> AI 辅助开发 / 配置</span><span><b>{stats['adjacent']}</b> AI 周边用途</span><span><b>{stats['infrastructure']}</b> 传统复活基础设施</span></div>
<section class="featured"><div class="section-heading"><p class="eyebrow">先理解一条完整路径</p><h2>三个值得拆开的案例</h2></div><div class="feature-grid">{featured_html}</div></section>
<section id="catalog" class="catalog"><div class="section-heading"><p class="eyebrow">找到设备的下一份工作</p><h2>项目目录 <span class="muted">/ {len(projects)}</span></h2><p>先按设备缩小范围，再核对型号、固件与恢复路径。平台、前置工具和同家族版本分别标注。</p></div>
<form id="filters" class="filters" role="search"><div class="search-field"><label for="q">搜索设备、型号或项目</label><input id="q" name="q" type="search" placeholder="例如 Kindle、LX06、打印机…" autocomplete="off"></div>
<div class="filter-grid"><label>设备<select id="category" name="category"><option value="">全部设备</option>{options(labels['category'])}</select></label>
<label>用途<select id="use" name="use"><option value="">全部用途</option>{options(dict(sorted(uses.items())))}</select></label>
<label>AI 关系<select id="ai" name="ai"><option value="">全部类型</option>{options(labels['ai'])}</select></label>
<label>难度<select id="difficulty" name="difficulty"><option value="">全部难度</option>{options(labels['difficulty'])}</select></label>
<label>证据<select id="evidence" name="evidence"><option value="">全部证据</option>{options({k:v for k,v in labels['evidence'].items() if k in evidence_counts})}</select></label></div>
<div class="filter-bottom"><p id="result-count" role="status" aria-live="polite">显示 {len(projects)} / {len(projects)} 个条目</p><div><button type="button" id="share">复制筛选链接</button><button type="reset">清除筛选</button></div></div><span id="share-status" role="status"></span></form>
<p class="evidence-note">E1 = 已读源码仓库与部署文档 · E2 = 作者实机陈述或演示 · 本轮没有 E3 独立复现。难度为编辑判断；成本未核价。</p>
<noscript><p>JavaScript 未启用，以下完整目录仍可阅读；可使用浏览器查找。</p></noscript>
<div id="project-grid" class="project-grid">{''.join(card(p) for p in projects)}</div>
<div id="empty" class="empty" hidden><h3>暂时没有匹配条目</h3><p>试试减少一个筛选条件，或在 GitHub 提交你手里的设备线索。</p><a href="{REPO}/issues/new/choose">提交项目线索 ↗</a></div></section>
<section class="closing"><div><p class="eyebrow">KEEP THE EVIDENCE OPEN</p><h2>你成功复活了一台设备？</h2><p>提交准确型号、固件、步骤来源和实测结果。失败条件与恢复经验，同样值得记录。</p></div><a class="primary" href="{REPO}/issues/new/choose">贡献一份复现记录 ↗</a></section>"""
write(OUT/"index.html",page("旧设备还能做什么？53 个开源项目导航","按设备、用途、AI、难度与证据筛选旧硬件再利用项目。核对型号、固件、维护状态、成本与恢复条件。",body,script=True))

req_labels = {"yes":"需要","no":"不需要","UNKNOWN":"待核实","model-dependent":"依具体型号","method-dependent":"依具体方法","recovery-dependent":"仅恢复过程可能需要","storage-dependent":"依存储安装方式","assembly-dependent":"依组装方案","accessory-dependent":"依配件方案","optional":"可选","no-at-runtime":"运行时不需要","no-for-supported-workflows":"文档支持路径不需要","no-in-documented-USB-route":"文档 USB 路径不需要","no-local-server-possible":"可使用本地服务","no-for-core-detection":"核心检测不需要","optional-integrations":"依可选集成","optional-content-services":"依可选内容服务","optional-external-model":"外部模型服务可选","optional-knowledge-provider":"知识服务可选","optional-music-services":"音乐服务可选","optional-game-platforms":"游戏平台可选","optional-sync":"同步服务可选","required-whoop":"需要 WHOOP 服务","required-spotify":"需要 Spotify 服务","required-xiaomi":"需要小米服务","required-xiaomi; optional-model-provider":"需要小米服务；模型云服务可选","depends-on-displayed-services":"依展示的数据服务"}
type_labels={"case":"具体改造路线","platform":"平台 / 多机型工程","prerequisite":"前置工具"}
deep_md = "# 重点案例分析\n\n这些是基于公开文档的分析与建议验收步骤；不是本目录已执行的硬件测试。适用条件以条目来源为准。\n\n"
for p in projects:
    pid = p["id"]
    d = deep.get(pid)
    requirements = "".join(f'<div><dt>{label}</dt><dd>{h(req_labels.get(p["requirements"][k],p["requirements"][k]))}</dd></div>' for k,label in [("disassembly","拆机"),("soldering","焊接"),("cloud_api","云 API / 服务")])
    evidence = p["evidence"]
    source_html = "".join(f'<li>{link(s["url"], s["kind"])} · {h(s["checked_at"][:10])} · 已读内容</li>' for s in p["sources"])
    source_html += "".join(f'<li>{link(s["url"], "X 作者原帖")} · 已读正文，未核验视频画面</li>' for s in p["x_sources"])
    detail = ""
    if d:
        detail = f'<section class="prose"><h2>这台设备发生了什么变化</h2><div class="before-after"><div><h3>原本的限制</h3><p>{h(d["before"])}</p></div><div><h3>新的用途</h3><p>{h(d["after"])}</p></div></div><p>{h(d["analysis"])}</p><h3>适合谁</h3><p>{h(d["fit"])}</p><h3>哪些情况先不要选</h3><p>{h(d["not_fit"])}</p><h3>建议复现验收步骤</h3>{items(d["acceptance"])}<p class="muted">以上是后续实测清单，本目录尚未执行这些硬件步骤。</p></section>'
        deep_md += f"## {p['name']}\n\n**{d['search_intent']}**\n\n{d['before']}\n\n{d['after']}\n\n{d['analysis']}\n\n- 型号：{p['device_scope']}\n- 固件：{p['firmware_requirement'] or '待按具体型号核实'}\n- 方法与难度：{p['method']} / {labels['difficulty'][p['difficulty']]}\n- 拆机 / 焊接 / 云服务：{' / '.join(req_labels.get(p['requirements'][k],p['requirements'][k]) for k in ['disassembly','soldering','cloud_api'])}\n- 额外成本：待核价；{'、'.join(p['cost']['items'])}\n- 证据：{evidence['level']} — {evidence['reason']}\n- 数据风险：{p['risk']['data_loss']}；设备失效风险：{p['risk']['bricking']}（编辑按路径提示，未实测）\n- 恢复：{p['risk']['recovery']}\n- 适合：{d['fit']}\n- 不适合：{d['not_fit']}\n\n建议验收（未执行）：\n\n"+ "".join(f"- {a}\n" for a in d["acceptance"])+f"\n[教程]({p['tutorial_url']}) · [适配范围]({p['compatibility_url']}) · [完整条目]({BASE}projects/{pid}.html)\n\n"
    detail_body = f"""<div class="detail-wrap"><a class="back" href="../index.html#catalog">← 返回项目目录</a><section class="detail-head">{tags(p)}<h1>{h(p['name'])}</h1><p class="intro">{h(p['summary_zh'])}</p>
<p class="muted">{h(type_labels[p['entry_type']])} · 家族 {h(p['family'])} · 核查 {h(p['checked_at'][:10])}</p><div class="actions">{link(p['repo_url'],'源码仓库 ↗')}{link(p['tutorial_url'],'原始教程 ↗')}{link(p['compatibility_url'],'型号适配依据 ↗')}</div></section>
<aside class="boundary"><b>先确认边界</b><p>{h(p['device_scope'])}</p>{items(p['limitations'])}<p>固件：{h(p['firmware_requirement'])} · 地区要求：{h(p['region_requirement'])}</p></aside>
{detail}
<section class="prose"><h2>动手需要什么</h2><dl class="spec-grid"><div><dt>改造方式</dt><dd>{h(p['method'])}</dd></div><div><dt>难度</dt><dd>{h(labels['difficulty'][p['difficulty']])}（编辑判断）</dd></div>{requirements}<div><dt>成本金额</dt><dd>待核价 / UNKNOWN</dd></div></dl><h3>可能需要的额外投入</h3>{items(p['cost']['items'])}<p>{h(p['cost']['note'])}</p>
<h2>风险与恢复</h2><p>数据风险：{h(p['risk']['data_loss'])}；设备失效风险：{h(p['risk']['bricking'])}。这是按改造路径给出的风险提示，未作实机验证；不表示每台设备必然发生。</p><p>{h(p['risk']['recovery'])}</p><p>{link(p['risk']['recovery_url'],'恢复资料')}</p>
<h2>证据与维护状态</h2><p><b>{h(evidence['level'])} · {h(labels['evidence'][evidence['level']])}</b></p><p>{h(evidence['reason'])}</p><p>本目录实机测试：未进行。独立复现：未核验。</p>
<dl class="spec-grid"><div><dt>维护状态</dt><dd>{h(labels['maintenance'][p['maintenance']['status']])}</dd></div><div><dt>GitHub 最后 push</dt><dd>{h(p['maintenance']['last_push_at'])}</dd></div><div><dt>仓库许可证</dt><dd>{link(p['license']['url'],p['license']['label'])}</dd></div></dl><p>{h(p['maintenance']['note'])}</p><p>{h(p['license']['scope'])}</p>
<h2>逐项来源</h2><ul class="sources">{source_html}</ul><p>核查为公开资料阅读。型号、服务与固件可能变化，开始操作前请重新核对上游。</p><p>{link(REPO+'/issues/new/choose','补充这条记录或报告错误 ↗')}</p></section></div>"""
    write(OUT/f"projects/{pid}.html",page(p["name"]+"：适配设备与复现条件",p["summary_zh"]+" "+p["device_scope"],detail_body,f"projects/{pid}.html",1))
write(ROOT/"research/DEEP_DIVES.zh-CN.md",deep_md.rstrip()+"\n")

coverage = "\n".join(f"| {labels['category'][k]} | {v} |" for k,v in category_counts.items())
candidate_md = "\n".join(f"- [{c['name']}]({c['url']}) — `{c['status']}`：{c['reason']}" for c in candidates)
report = f"""# 老硬件复活项目研究 · v{data['version']}

核查日期：{DATE}（条目保留 UTC 原始时间；本报告按 Asia/Shanghai 阅读）。

## 结论与适用范围

初版收录 {len(projects)} 条公开项目、平台和前置工具，覆盖 {len(category_counts)} 类设备，归并为 {len(set(p['family'] for p in projects))} 个项目家族。另有 {len(candidates)} 条候选或排除记录。它们不是 53 次成功实机改造：E1 文档与代码证据 {evidence_counts['E1']} 条，E2 作者实机陈述/演示 {evidence_counts['E2']} 条，E3 独立复现 0 条，本目录亲手测试 0 条。

AI 功能改造 {stats['native']} 条；有明确 AI 辅助开发/配置材料 {stats['assisted']} 条；AI 周边用途 {stats['adjacent']} 条；传统开源复活基础设施 {stats['infrastructure']} 条。不能因为项目可以与大模型结合就把它称为 AI 项目。AI 辅助配置与 AI 编写底层驱动也不是同一种证据。

主要发现：

1. 复用设备常由外部计算机完成新工作。音箱作为音频端点、Kindle 作为显示端点，与在设备内部运行大模型有实质区别。
2. 真正的兼容单位通常是型号、硬件修订、固件、地区的组合。销售名称只适合发现线索。
3. 云替代、系统更新、增加应用、换板与修复物理故障应分开。软件项目不会自动解决电池或存储失效。
4. 旧项目值得保留，但归档、停止维护、镜像迁移与漏洞已修复必须直接展示；未归档不代表每个设备当前仍能部署。
5. 具体问题比泛泛“AI 复活万物”更适合作为内容入口：用户需要知道手里的这台设备是否值得动手。

## 检索与核查方法

以设备和失效原因组合检索 GitHub、官方网站与 X。检索词包括 old hardware reuse、Nest Mini LLM PCB、Kindle dashboard jailbreak、Vector wire-pod、HP Laser macOS Claude driver、router firmware、IP camera local firmware，以及对应中文设备名。

使用 GitHub 只读 API 取得仓库元数据、README、根许可证与最近 release 列表。逐项阅读 README 的适配和部署片段；重点项目继续读官方安装/型号表与作者过程。保留来源 URL、核查时间、README blob SHA 和内容哈希，不重新发布上游教程全文。不存在的旧路径、镜像或跳转不自动视为项目失效，放入候选区继续核实。

维护状态来自带时间的 API 快照和作者说明。许可证字段优先实际根文件；没有确认的标 UNKNOWN，混合许可不压成一个宽松标签。难度为编辑判断，成本未核价，恢复描述是文档路径而非救砖保证。地区、固件缺少明确材料时保留 null。

X 通过浏览器读取 4 条原始帖子正文，涉及 Onju 与 HP 驱动 2 个案例家族。部分搜索/抓取入口受限；不把转载或搜索摘要当作原帖核验。视频组件出现不等于看过或验证视频。本轮未记录点赞、浏览量作为成功证据。详见 [X 来源记录](../data/x-research.json)。

## 证据等级

| 等级 | 本目录含义 | 条数 |
| --- | --- | ---: |
| E0 | 概念、线索或证据未完成；留在候选区 | 不计主目录 |
| E1 | 已读项目源码仓库说明与部署/适配文档；未验证实机 | {evidence_counts['E1']} |
| E2 | 在 E1 基础上，有本轮读到的作者具体实机陈述或演示说明 | {evidence_counts['E2']} |
| E3 | 有另一个独立使用者的可追溯复现记录且本轮已核验 | 0 |

E1 不表示项目从未被别人成功使用，只表示本轮核查停留在此层级。E2 也不是本目录亲测。厂商或维护者在文档中说“支持”是来源声明，不自动等于本目录完成独立复现。

## 覆盖矩阵

| 设备类别 | 主目录条目数 |
| --- | ---: |
{coverage}

条目类型包括具体路线、跨机型平台与前置工具。Onju v1/v2、旧 Wyoming satellite/后继 Linux Voice Assistant 有家族关联；版本数不当作独立成功设备数。越狱工具和显示库本身不是完整用途案例。

## 重点案例

[12 篇完整分析](DEEP_DIVES.zh-CN.md) 包括 XiaoGPT、Open-XiaoAI、Onju、Kindle WHOOP、Kindle Home Assistant、OCLP、HAOS、OpenWrt、Valetudo、wire-pod、HP 打印驱动、OpenLumi。每篇提供原限制、新用途、适配前提、费用未知项、拆装要求、风险与恢复、适合/不适合人群及未执行的验收清单。

## 待核验与排除

{candidate_md}

## 明确的空白

- 没有实物硬件与长期稳定性测试；耗电、端到端延迟和可恢复性没有自测数据。
- X 覆盖集中于 2 个案例，未形成广泛作者样本；没有声称检索穷尽。
- 旧手机的逐型号当前镜像、旧 NAS 的启动加载器恢复、停服穿戴服务和区域差异仍需补全。
- 没有把智能锁、他人账号绑定解除或防盗激活锁绕过当作普通再利用指南。
- 金额全为未知；没有本地采购价、云账单或长期总成本估计。
- 项目未归档和最新 release 不是部署通过证明；第三方服务可能改变。

## 作为流量入口的下一步

首屏按“设备 → 用途 → 适配条件”组织，所有条目都有可索引静态详情页。搜索词来自实际设备问题，不生成没有内容的关键词页。

建议先补三类内容：型号对照（如 LX06/OH2P、Kindle 固件边界）；路线比较（桥接/换板/替换系统）；失败与恢复记录（先备份什么，什么条件应停止）。把每篇文章关联到稳定条目 ID 与原始来源。

贡献者通过 issue 提交准确型号、固件、地区、日期、版本、操作来源、成功/失败功能和恢复结果。维护者复核后更新 JSON，重建页面并在变更日志写明证据变化。没有新增证据就不升级等级。仅修改元数据不要刷新“内容核查”日期。

建议人工每月优先检查归档状态、文档迁移和热门条目的服务依赖；每季度审查候选与长期失效链接。这是建议节奏，本项目没有创建定时任务。上线后可以观察搜索收录、issue 质量与用户实际复现；初版没有流量、转化或增长承诺。
"""
write(ROOT/"research/REPORT.zh-CN.md",report)
research_body = f'<div class="detail-wrap"><section class="detail-head"><p class="eyebrow">METHOD & COVERAGE</p><h1>先看证据，<br>再谈复活。</h1><p class="intro">{len(projects)} 条资料，{len(category_counts)} 类设备。所有结论都保留来源与未知项。</p></section><section class="prose"><h2>收录意味着什么</h2><p>E1：已读项目说明和部署文档，共 {evidence_counts["E1"]} 条。E2：作者具体实机陈述或演示说明，共 {evidence_counts["E2"]} 条。E3：独立复现，本轮 0 条。本目录实物测试 0 条。</p><p>项目、跨机型平台与前置工具分别标注。53 条归并为 51 个家族，同家族后续版本不算独立成功设备。</p><h2>怎么核查</h2><p>读取 GitHub 元数据、README、许可证及版本信息，重点检查官方型号和安装文档。X 已读 4 条原始帖子，涉及 2 个案例；未播放验证视频，不以互动数据判断成功。</p><p>维护状态与核查时间逐条保留。难度是编辑判断，金额未知写 UNKNOWN，缺失固件/地区条件保留 null。不会将历史教程或文档可访问说成今天已经实测成功。</p><h2>12 篇案例分析</h2><ul>'+"".join(f'<li><a href="projects/{pid}.html">{h(next(p["name"] for p in projects if p["id"]==pid))}</a>：{h(d["search_intent"])}</li>' for pid,d in deep.items())+'</ul><h2>设备覆盖</h2><table><thead><tr><th>类别</th><th>条目</th></tr></thead><tbody>'+"".join(f'<tr><td>{h(labels["category"][k])}</td><td>{n}</td></tr>' for k,n in category_counts.items())+'</tbody></table><h2>候选与空白</h2><ul>'+"".join(f'<li>{link(c["url"],c["name"])} — {h(c["reason"])}</li>' for c in candidates)+f'</ul><p>本轮缺少长期稳定性、能耗、实际费用与独立硬件复现；旧 NAS、当前手机镜像与停服穿戴服务需继续补全。未声称覆盖全网。</p><h2>阅读完整研究</h2><p>{link(REPO+"/blob/main/research/REPORT.zh-CN.md","研究报告 ↗")} · {link(REPO+"/blob/main/research/DEEP_DIVES.zh-CN.md","案例合辑 ↗")} · {link(REPO+"/blob/main/CONTRIBUTING.md","贡献方法 ↗")}</p></section></div>'
write(OUT/"research.html",page("研究方法、证据分级与覆盖矩阵","公开项目入选方法、证据边界、13 类设备覆盖、12 篇重点案例与待核验空白。",research_body,"research.html"))
write(OUT/".nojekyll","")
for name in ["catalog.json","catalog.csv","candidates.json","deep-dives.json","x-research.json"]:
    (OUT/"data").mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/"data"/name,OUT/"data"/name)
paths = ["","research.html"]+[f"projects/{p['id']}.html" for p in projects]
write(OUT/"sitemap.xml",'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f"<url><loc>{BASE}{p}</loc><lastmod>{DATE}</lastmod></url>" for p in paths)+"\n</urlset>\n")
print(f"Built {len(paths)} HTML pages; {len(deep)} deep dives; deterministic data date {DATE}.")
from site_i18n import build as build_bilingual
build_bilingual()
