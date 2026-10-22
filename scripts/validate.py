"""Validate editorial invariants, exports and all generated internal links."""
import collections
import csv
import hashlib
from html.parser import HTMLParser
import json
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

import jsonschema

from watchlist_merge import load_watchlist

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"docs"
def load(path): return json.loads(path.read_text(encoding="utf-8"))
data=load(ROOT/"data/catalog.json")
config=load(ROOT/"site.config.json")
BASE=config["base_url"].rstrip("/")+"/"
schema=load(ROOT/"data/catalog.schema.json")
jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)
projects=data["projects"]
articles=load(ROOT/"data/articles.json")
author_socials=load(ROOT/"data/author-socials.json")
watchlist,watchlist_details=load_watchlist(ROOT/"data")
device_atlas=load(ROOT/"data/device-atlas.json")
assert len(device_atlas["items"])==300 and device_atlas["counts"]["total"]==300, "Device atlas must contain 300 new records"
assert len(projects)+len(watchlist)==400, "Public project/device denominator must equal 400"
assert len({item["slug"] for item in device_atlas["items"]})==300, "Duplicate device-atlas slug"
assert len({item["content_id"] for item in device_atlas["items"]})==300, "Duplicate device-atlas content ID"
assert all(item["source_url"].startswith("https://") and item["device"] and item["model"] and item["source_access"] and item["discovery_channel"] for item in device_atlas["items"]), "Incomplete device-atlas record"
assert articles and len({a["content_id"] for a in articles.values()})==len(articles), "Duplicate article content ID"
for slug,article in articles.items():
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug),slug
    assert article["projects"] and set(article["projects"])<=set(p["id"] for p in projects),slug
    assert article["sources"] and all(s["url"].startswith("https://") and s["label"] for s in article["sources"]),slug
    assert len(article["zh"]["sections"])==len(article["en"]["sections"]),slug
    for lang in ["zh","en"]:
        assert article[lang]["title"] and article[lang]["intro"] and all(title and paragraphs and all(paragraphs) for title,paragraphs in article[lang]["sections"]),slug
    for row in article.get("decision_rows",[]):
        assert row["route"] and all(row[key][lang] for key in ["hardware","result","readiness","stop"] for lang in ["zh","en"]),slug
assert set(author_socials)<=set(p["id"] for p in projects), "Author social points to missing project"
for pid,accounts in author_socials.items():
    assert accounts and all(item["name"] and item["platform"] and item["url"].startswith("https://") and item["source_url"].startswith("https://") and item["verification"] and re.fullmatch(r"\d{4}-\d{2}-\d{2}",item["checked_at"]) and item["zh_role"] and item["en_role"] for item in accounts),pid
assert watchlist and len({lead["content_id"] for lead in watchlist.values()})==len(watchlist), "Duplicate lead content ID"
assert set(watchlist_details)==set(watchlist), "Lead decision-sheet coverage mismatch"
assert not ({a["content_id"] for a in articles.values()} & {lead["content_id"] for lead in watchlist.values()}), "Content ID collision"
for slug,lead in watchlist.items():
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",slug),slug
    assert lead["category"] in data["labels"]["category"],slug
    assert lead["source_url"].startswith("https://"),slug
    assert lead["code_url"] is None or lead["code_url"].startswith("https://"),slug
    assert all(url.startswith("https://") for url in lead["additional_sources"]),slug
    assert re.fullmatch(r"(?:L\d{2,3}|D\d{3})",lead["content_id"]) and lead["status"] and lead["source_platform"],slug
    for lang in ["zh","en"]:
        assert all(lead[lang][key] for key in ["title","summary","gap","next_check","safety"]),slug
        decision=watchlist_details[slug][lang]
        assert all(decision[key] for key in ["stage","usable","works_for","not_for","value","follow"]),slug
        assert all(isinstance(decision[key],list) and decision[key] for key in ["works_for","not_for"]),slug
    resources=watchlist_details[slug]["resources"]
    assert resources and len({item["url"] for item in resources})==len(resources),slug
    assert all(item["url"].startswith("https://") and all(item[key] for key in ["kind","zh_label","en_label","zh_note","en_note"]) for item in resources),slug
    legacy_urls={lead["source_url"],*lead["additional_sources"]}|({lead["code_url"]} if lead["code_url"] else set())
    assert legacy_urls<={item["url"] for item in resources},(slug,"legacy source missing from annotated resources")
ids=[p["id"] for p in projects]
assert len(ids)==len(set(i.lower() for i in ids)), "Duplicate ID"
assert set(p["family"] for p in projects)<=set(ids), "Missing family anchor"
assert set(p["category"] for p in projects)==set(data["labels"]["category"]), "Coverage mismatch"
for p in projects:
    if p["cost"]["status"]=="UNKNOWN":
        assert p["cost"]["amount"] is None and p["cost"]["currency"] is None,p["id"]
    if p["evidence"]["level"]=="E3":
        assert p["evidence"]["independent_reproduction_verified"],p["id"]
    assert p["checked_at"]<=p["editorial_reviewed_at"],p["id"]
    for source in p["sources"]:
        sha=source.get("content_sha256")
        assert sha is None or re.fullmatch(r"[0-9a-f]{64}",sha),p["id"]
deep=load(ROOT/"data/deep-dives.json")
assert len(deep)>=10
assert set(deep)<=set(ids)
assert not (set(c["id"] for c in load(ROOT/"data/candidates.json")) & set(ids))
for pid,d in deep.items():
    assert all(d.get(k) for k in ["before","after","analysis","fit","not_fit","acceptance","search_intent"]),pid
with (ROOT/"data/catalog.csv").open(encoding="utf-8-sig",newline="") as f:
    rows=list(csv.DictReader(f))
assert [r["id"] for r in rows]==ids
for p,r in zip(projects,rows):
    assert r["name"]==p["name"] and r["evidence_level"]==p["evidence"]["level"],p["id"]
    for key in ["requirements","risk","cost","model_examples","use_cases"]:
        assert json.loads(r[key])==p[key],(p["id"],key)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs=[]; self.ids=set(); self.h1=0; self.canonical=[]; self.has_title=False; self.lang=None
        self.alternates={};self.text=[];self.skip_text=0;self.switch_depth=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html":self.lang=a.get("lang")
        if tag=="h1":self.h1+=1
        if tag=="title":self.has_title=True
        if a.get("id"):self.ids.add(a["id"])
        if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
        if tag=="link" and a.get("rel")=="alternate":self.alternates[a.get("hreflang")]=a.get("href")
        if tag in ("script","style"):self.skip_text+=1
        if tag=="a" and a.get("class")=="language-switch":self.switch_depth+=1
        if tag in ("a","link","script","img"):
            ref=a.get("href") or a.get("src")
            if ref:self.refs.append(ref)
    def handle_endtag(self,tag):
        if tag in ("script","style"):self.skip_text-=1
        if tag=="a" and self.switch_depth:self.switch_depth-=1
    def handle_data(self,text):
        if not self.skip_text and not self.switch_depth:self.text.append(text)

pages={}
for file in OUT.rglob("*.html"):
    parser=Page();parser.feed(file.read_text(encoding="utf-8"));pages[file.resolve()]=parser
    assert parser.h1==1 and parser.has_title and parser.lang in {"zh-CN","en"},file
    assert len(parser.canonical)==1 and parser.canonical[0].startswith(BASE),file
    assert set(parser.alternates)=={"zh-CN","en","x-default"},file
    assert parser.alternates["x-default"]==BASE,file
    if file.is_relative_to(OUT/"en"):
        assert parser.lang=="en" and not re.search(r"[\u4e00-\u9fff]","".join(parser.text)),("Chinese visible text on English page",file)
assert len(pages)==2*(len(projects)+8+len(articles)+len(watchlist))+len(projects)+2
root_page=pages[(OUT/"index.html").resolve()]
english_home=pages[(OUT/"en/index.html").resolve()]
assert root_page.lang=="en" and root_page.canonical==[BASE]
assert english_home.canonical==[BASE]
assert root_page.alternates["en"]==BASE and root_page.alternates["zh-CN"]==BASE+"zh/"
assert "project-grid" in root_page.ids and "filters" in root_page.ids
assert config["community_url"] in root_page.refs
for lang in ["zh","en"]:
    assert config["community_url"] in pages[(OUT/lang/"index.html").resolve()].refs
    assert config["community_url"] in pages[(OUT/lang/"community/index.html").resolve()].refs
    home=pages[(OUT/lang/"index.html").resolve()]
    assert "leads/" in home.refs,(lang,"missing field-leads homepage link")
    leads_index=pages[(OUT/lang/"leads/index.html").resolve()]
    for slug,lead in watchlist.items():
        assert f"{slug}/" in leads_index.refs,(lang,slug,"missing lead index link")
        page=pages[(OUT/lang/"leads"/slug/"index.html").resolve()]
        assert page.canonical==[f"{BASE}{lang}/leads/{slug}/"]
        expected=[item["url"] for item in watchlist_details[slug]["resources"]]
        assert all(url in page.refs for url in expected),(lang,slug,"missing lead source")
    for slug,article in articles.items():
        assert f"articles/{slug}/" in home.refs,(lang,slug,"missing homepage article link")
        page=pages[(OUT/lang/"articles"/slug/"index.html").resolve()]
        assert page.canonical==[f"{BASE}{lang}/articles/{slug}/"]
        assert all(source["url"] in page.refs for source in article["sources"]),(lang,slug,"missing source")
for file,parser in pages.items():
    for url in [*parser.alternates.values(),*parser.canonical]:
        assert url.startswith(BASE),(file,url)
        target=OUT/unquote(url[len(BASE):])
        if target.is_dir():target=target/"index.html"
        assert target.resolve() in pages,(file,url,"language/canonical target missing")
    for ref in parser.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc:continue
        target=(file.parent/unquote(url.path)).resolve() if url.path else file
        if target.is_dir():target=target/"index.html"
        assert target.is_relative_to(OUT.resolve()),(file,ref,"escapes site")
        assert target.exists(),(file,ref,"missing")
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids,(file,ref,"missing anchor")
for name in ["catalog.json","catalog.csv","deep-dives.json","candidates.json","x-research.json","watchlist-expansion.json","device-atlas.json"]:
    assert (OUT/"data"/name).read_bytes()==(ROOT/"data"/name).read_bytes(),name
assert load(OUT/"data/watchlist.json")==watchlist,"merged watchlist export"
assert load(OUT/"data/watchlist-details.json")==watchlist_details,"merged watchlist details export"
identity_coverage=load(OUT/"data/author-identity-coverage.json")
assert identity_coverage["catalog_entries"]==len(projects)
assert identity_coverage["repository_owner_covered"]==len(projects)
assert identity_coverage["projects_with_verified_author_profiles"]==len(author_socials)
assert [row["project_id"] for row in identity_coverage["entries"]]==ids
assert set(ids)=={p.stem for p in (OUT/"projects").glob("*.html")}
for lang in ["zh","en"]:
    assert set(ids)=={p.name for p in (OUT/lang/"projects").iterdir() if p.is_dir()}
    for pid in ids:
        parser=pages[(OUT/lang/"projects"/pid/"index.html").resolve()]
        assert parser.canonical==[f"{BASE}{lang}/projects/{pid}/"]
        assert parser.alternates["en"]==f"{BASE}en/projects/{pid}/"
        assert parser.alternates["zh-CN"]==f"{BASE}zh/projects/{pid}/"
        repo=urlsplit(next(p["repo_url"] for p in projects if p["id"]==pid))
        owner_parts=[part for part in repo.path.split("/") if part]
        if repo.netloc in {"github.com","codeberg.org"} and len(owner_parts)>=2:
            assert f"{repo.scheme}://{repo.netloc}/{owner_parts[0]}" in parser.refs,(lang,pid,"missing repository owner identity")
english=load(OUT/"data/catalog.en.json")
assert [p["id"] for p in english["projects"]]==ids
for p,e in zip(projects,english["projects"]):
    for key in ["id","family","category","ai_relation","entry_type","repo_url","tutorial_url","compatibility_url","sources","checked_at","model_examples"]:
        assert p[key]==e[key],(p["id"],"Changed shared fact",key)
    assert p["evidence"]["level"]==e["evidence"]["level"]
    assert p["cost"]["amount"]==e["cost"]["amount"] is None
    assert p["risk"]["data_loss"]==e["risk"]["data_loss"]
    assert p["risk"]["bricking"]==e["risk"]["bricking"]
with (OUT/"data/catalog.en.csv").open(encoding="utf-8-sig",newline="") as f:
    enrows=list(csv.DictReader(f))
assert [p["id"] for p in enrows]==ids
for p,row in zip(english["projects"],enrows):
    for key in ["summary","device_scope","method"]:assert p[key]==row[key]
    for key in ["requirements","cost","risk","evidence","limitations","translation"]:assert p[key]==json.loads(row[key])
assert set(load(OUT/"data/deep-dives.en.json"))==set(deep)
mapping=load(OUT/"data/url-mapping.json")["mappings"]
assert len(mapping)==len(projects)
for source,target in mapping.items():
    assert pages[(OUT/source).resolve()].canonical==[BASE+target]
import xml.etree.ElementTree as ET
urls=[node.text for node in ET.parse(OUT/"sitemap.xml").findall(".//{*}loc")]
assert len(urls)==len(set(urls))==2*(len(projects)+8+len(articles)+len(watchlist))
assert BASE in urls and BASE+"en/" not in urls
for url in urls:
    assert url.startswith(BASE)
    target=OUT/url[len(BASE):]
    if target.is_dir():target=target/"index.html"
    assert target.resolve() in pages
# Block credentials and private machine paths, not harmless public repository names.
secret_patterns=[r"gh[pousr]_[A-Za-z0-9]{25,}",r"github_pat_[A-Za-z0-9_]{30,}",r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}",r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----",r"C:\\\\Users\\\\",r"C:\\\\work\\\\\.secrets"]
for file in ROOT.rglob("*"):
    if not file.is_file() or ".git" in file.parts or "__pycache__" in file.parts:continue
    if file.suffix not in {".json",".csv",".md",".html",".js",".css",".yml",".py",".txt"}:continue
    text=file.read_text(encoding="utf-8-sig")
    assert "\ufffd" not in text,("UTF8 replacement character",file)
    for pattern in secret_patterns:
        assert not re.search(pattern,text),("Potential sensitive content",file)
print(json.dumps({"schema":"PASS","unique_ids":len(ids),"families":len(set(p["family"] for p in projects)),"categories":len(set(p["category"] for p in projects)),"deep_dives":len(deep),"html_pages_and_internal_links":"PASS","csv_json_parity":"PASS","public_file_scan":"PASS","evidence":dict(collections.Counter(p["evidence"]["level"] for p in projects))},ensure_ascii=False,indent=2))
