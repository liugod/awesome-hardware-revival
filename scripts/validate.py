"""Validate editorial invariants, exports and all generated internal links."""
import collections
import csv
import hashlib
from html.parser import HTMLParser
import json
import math
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

import jsonschema

from scoring import COMPONENTS, HALF_STAR_BUCKETS, WEIGHTS, build_directory_export, directory_csv, export_json_text, project_leads_csv, score_all
from watchlist_merge import load_watchlist

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"docs"
def load(path): return json.loads(path.read_text(encoding="utf-8"))
data=load(ROOT/"data/catalog.json")
config=load(ROOT/"site.config.json")
project_lead_data=load(ROOT/"data/project-leads.json")
project_leads=project_lead_data["projects"]
scoring_evidence=load(ROOT/"data/scoring-evidence.json")
scoring_evidence_items=scoring_evidence["entries"]
if isinstance(scoring_evidence_items,dict):scoring_evidence_items=list(scoring_evidence_items.values())
BASE=config["base_url"].rstrip("/")+"/"
app_javascript=(OUT/"assets/app.js").read_text(encoding="utf-8")
assert 'document.querySelectorAll("#directory-grid .project")' in app_javascript,"Directory filters must target directory cards"
schema=load(ROOT/"data/catalog.schema.json")
jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)
projects=data["projects"]
project_image_data=load(ROOT/"data/project-images.json")
project_images={item["project_id"]:item for item in project_image_data["entries"]}
hardware_tag_data=load(ROOT/"data/hardware-tags.json")
project_hardware_tags=hardware_tag_data["projects"]
lead_hardware_tags=hardware_tag_data["leads"]
assert project_image_data["version"]==config["version"]==data["version"],"Project-image version mismatch"
assert hardware_tag_data["version"]==config["version"],"Hardware-tag version mismatch"
assert len(project_images)==len(project_image_data["entries"]),"Duplicate project-image ID"
assert set(project_images)<=set(p["id"] for p in projects),"Project image points to missing project"
for pid,image in project_images.items():
    assert image["source_kind"] in {"upstream-project-asset","kitagain-project-illustration"},pid
    assert image["fit"] in {"cover","contain"},pid
    assert all(image[key] for key in ["source_file","local_file","source_page","alt_zh","alt_en","caption_zh","caption_en","image_license_status"]),pid
    assert image["source_page"].startswith("https://") and not image["local_file"].startswith("docs/"),pid
    assert (ROOT/image["source_file"]).is_file() and (OUT/image["local_file"]).is_file(),pid
    assert (OUT/image["local_file"]).stat().st_size>5000,pid
    if image["source_kind"]=="upstream-project-asset":
        assert image["source_url"] and image["source_url"].startswith("https://"),pid
        assert image["image_license_status"]=="not-separately-stated",pid
    else:
        assert image["source_url"] is None and image.get("prompt_summary"),pid
        assert "不是实机照片" in image["caption_zh"] and "not an actual device photo" in image["caption_en"],pid
articles=load(ROOT/"data/articles.json")
author_socials=load(ROOT/"data/author-socials.json")
watchlist,watchlist_details=load_watchlist(ROOT/"data")
device_atlas=load(ROOT/"data/device-atlas.json")
device_reviews=load(ROOT/"data/device-reviews.json")
assert scoring_evidence["version"]==config["version"] and scoring_evidence["scoring_model"]=="3.0.0","Scoring-evidence version mismatch"
assert scoring_evidence["policy"]["weights"]==WEIGHTS and scoring_evidence["policy"]["unscored_value"] is None,"Scoring-evidence policy mismatch"
assert scoring_evidence["policy"]["minimum_evidenced_dimensions"]==3 and scoring_evidence["policy"]["renormalize_evidenced_weights"] is True,"Scoring-evidence threshold mismatch"
assert scoring_evidence["policy"]["rounding"]=="nearest-0.5-half-up" and scoring_evidence["policy"]["evidence_grade_independent"] is True,"Scoring-evidence rounding/evidence policy mismatch"
raw_scoring_entries=scoring_evidence["entries"]
if isinstance(raw_scoring_entries,dict):
    scoring_entry_pairs=list(raw_scoring_entries.items())
else:
    scoring_entry_pairs=[(entry["entry_id"],entry) for entry in raw_scoring_entries]
scoring_entry_ids=[entry_id for entry_id,_ in scoring_entry_pairs]
valid_scoring_entry_ids={f"project:{p['id']}" for p in projects}|{f"lead:{slug}" for slug in watchlist}|{f"project-lead:{lead['id']}" for lead in project_leads}
assert len(scoring_entry_ids)==len(set(scoring_entry_ids)) and set(scoring_entry_ids)<=valid_scoring_entry_ids,"Invalid or duplicate scoring-evidence entry_id"
declared_actual=scoring_evidence.get("actual_entries",scoring_evidence.get("counts",{}).get("actual_entries"))
assert declared_actual==len(scoring_entry_pairs),"Scoring-evidence actual_entries mismatch"
allowed_scoring_topics={"kindle-ereader","router","old-mini-pc-nas","smart-speaker"}
assert set(scoring_evidence["scope"])==allowed_scoring_topics,"Scoring-evidence scope mismatch"
batch_scoring_date=scoring_evidence["checked_at"][:10]
assert re.fullmatch(r"\d{4}-\d{2}-\d{2}",batch_scoring_date),"Invalid scoring-evidence check date"
for entry_id,entry in scoring_entry_pairs:
    assert entry.get("entry_id",entry_id)==entry_id and entry["topic"] in allowed_scoring_topics,entry_id
    assert entry["checked_at"][:10]==batch_scoring_date,(entry_id,"Scoring-evidence check date")
    assert set(entry["components"])==set(COMPONENTS),entry_id
    scored_components=0
    for key,component in entry["components"].items():
        if component is None:
            continue
        assert isinstance(component,dict) and set(component)>={"score","basis_zh","basis_en","sources"},(entry_id,key)
        value=component["score"]
        assert isinstance(value,int) and not isinstance(value,bool) and 1<=value<=5,(entry_id,key)
        scored_components+=1
        assert component["basis_zh"] and component["basis_en"] and component["sources"],(entry_id,key,"Scored dimension needs bilingual basis and sources")
        for url in component["sources"]:
            parsed=urlsplit(url)
            assert parsed.scheme=="https" and parsed.netloc,(entry_id,key,"Score source must be HTTPS")
            assert not ("search" in parsed.path.casefold() and parsed.query),(entry_id,key,"Search-result URL is not a scoring source")
    assert scored_components>=3,(entry_id,"Enrichment entry requires at least three evidenced dimensions")
    serialized=json.dumps(entry,ensure_ascii=False).casefold()
    assert "unknown-neutral" not in serialized and "unreviewed-neutral" not in serialized,entry_id
assert device_atlas["version"]==device_reviews["version"]==config["version"],"Device-data version mismatch"
assert project_lead_data["version"]==config["version"],"Project-source version mismatch"
assert len(device_atlas["items"])==300 and device_atlas["counts"]["total"]==300, "Device atlas must contain 300 new records"
assert len(projects)+len(watchlist)==400, "Reviewed-project/device-route denominator must equal 400"
assert len(projects)+len(project_leads)==200, "Independent project-source denominator must equal 200"
assert len(projects)+len(project_leads)+len(watchlist)==547, "Unified public-entry denominator must equal 547"
assert len(project_leads)==project_lead_data["counts"]["total"]==147,"Expected 147 E0 project-source leads"
assert len({lead["id"] for lead in project_leads})==len(project_leads),"Duplicate project-source ID"
assert len({lead["content_id"] for lead in project_leads})==len(project_leads),"Duplicate project-source content ID"
assert len({lead["repo_url"].casefold() for lead in project_leads})==len(project_leads),"Duplicate project-source repository"
assert not ({lead["repo_url"].casefold() for lead in project_leads}&{project["repo_url"].casefold() for project in projects}),"Project-source lead duplicates reviewed catalog"
project_lead_fields={"content_id","id","name","repo_url","category","evidence_level","needs_review","summary_zh","summary_en","device_scope_zh","device_scope_en","use_case_zh","use_case_en","github_description","archived","pushed_at","license_spdx","default_branch","checked_at","source_access","readme_access","reason_zh","reason_en","fork"}
for lead in project_leads:
    assert project_lead_fields<=set(lead),lead.get("id")
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*",lead["id"]),lead["id"]
    assert lead["content_id"]==f"PS-{lead['id']}" and lead["category"] in data["labels"]["category"],lead["id"]
    assert lead["repo_url"].startswith("https://github.com/") and lead["repo_url"].count("/")==4,lead["id"]
    assert lead["evidence_level"]=="E0" and lead["needs_review"] is True and lead["source_access"]=="repository-metadata-reviewed" and lead["readme_access"]=="opening-section-read",lead["id"]
    assert lead["fork"] is False and isinstance(lead["archived"],bool),lead["id"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",lead["checked_at"]),lead["id"]
    assert all(lead[key] for key in ["name","summary_zh","summary_en","device_scope_zh","device_scope_en","use_case_zh","use_case_en","pushed_at","default_branch","reason_zh","reason_en"]),lead["id"]
    assert lead["github_description"] is None or isinstance(lead["github_description"],str),lead["id"]
assert project_lead_data["counts"]["evidence"]=={"E0":147,"E1":0,"E2":0,"E3":0}
assert project_lead_data["counts"]["needs_review"]==147
assert project_lead_data["counts"]["categories"]==dict(sorted(collections.Counter(lead["category"] for lead in project_leads).items()))
assert set(project_hardware_tags)=={p["id"] for p in projects},"Reviewed-project hardware-tag coverage mismatch"
assert set(lead_hardware_tags)<=set(watchlist),"Hardware tags point to missing leads"
allowed_tag_kinds={"exact-model","device-family","hardware-platform"}
for owner,entries in [*project_hardware_tags.items(),*lead_hardware_tags.items()]:
    assert entries and all(set(item)=={"zh","en","kind"} and item["zh"] and item["en"] and item["kind"] in allowed_tag_kinds for item in entries),owner
    for lang in ["zh","en"]:
        assert len({item[lang].casefold() for item in entries})==len(entries),(owner,lang,"duplicate hardware tag")
def lead_tag_values(slug,lead,lang):
    if slug in lead_hardware_tags:
        return [item[lang] for item in lead_hardware_tags[slug]]
    values=[]
    for value in [lead.get("device_model"),lead.get("device_name")]:
        if value and value not in values: values.append(value)
    return values
assert all(lead_tag_values(slug,lead,"zh") and lead_tag_values(slug,lead,"en") for slug,lead in watchlist.items()),"Every lead needs a hardware model/name tag"
assert len({item["slug"] for item in device_atlas["items"]})==300, "Duplicate device-atlas slug"
assert len({item["content_id"] for item in device_atlas["items"]})==300, "Duplicate device-atlas content ID"
assert all(item["source_url"].startswith("https://") and item["device"] and item["model"] and item["source_access"] and item["discovery_channel"] for item in device_atlas["items"]), "Incomplete device-atlas record"
assert len(device_reviews["items"])==30, "Expected 30 exact-model source reviews"
assert len({item["content_id"] for item in device_reviews["items"]})==30, "Duplicate device-review content ID"
assert {item["content_id"] for item in device_reviews["items"]}<={item["content_id"] for item in device_atlas["items"]}, "Device review points outside atlas"
assert all(re.fullmatch(r"[0-9a-f]{40}",item["upstream_revision"]) and item["source_url"].startswith("https://") for item in device_reviews["items"]), "Invalid device-review source revision"
for item in device_reviews["items"]:
    for lang in ["zh","en"]:
        assert all(item[lang][key] for key in ["hardware","route","result","boundary","recovery"]),item["content_id"]
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
    if lead.get("evidence_level")=="E1":
        assert lead["status"]=="source-body-reviewed-exact-model" and lead["source_access"]=="source-body-reviewed",slug
        assert re.fullmatch(r"[0-9a-f]{40}",lead["upstream_revision"]),slug
        for lang in ["zh","en"]:
            assert all(lead["deep_review"][lang][key] for key in ["hardware","route","result","boundary","recovery"]),slug
assert sum(lead.get("evidence_level")=="E1" for lead in watchlist.values())==30,"Merged E1 device-review count"
project_scores,lead_scores,project_lead_scores=score_all(projects,watchlist,watchlist_details,project_leads,scoring_evidence)
all_scores=[*project_scores.values(),*lead_scores.values(),*project_lead_scores.values()]
assert len(all_scores)==len(projects)+len(watchlist)+len(project_leads),"Score coverage mismatch"
assert sum(WEIGHTS.values())==100 and set(WEIGHTS)==set(COMPONENTS),"Score weights must total 100"
for item in all_scores:
    assert set(item["components"])==set(COMPONENTS) and set(item["component_basis"])==set(COMPONENTS),"Five score dimensions required"
    assert set(item["component_sources"])==set(COMPONENTS) and set(item["effective_weights"])==set(COMPONENTS),"Score evidence fields incomplete"
    assert all(value is None or (isinstance(value,int) and not isinstance(value,bool) and 1<=value<=5) for value in item["components"].values()),"Raw score out of range"
    evidenced=[key for key in COMPONENTS if item["components"][key] is not None]
    assert item["evidenced_dimensions"]==len(evidenced),"Evidenced-dimension count mismatch"
    assert set(item["score_sources"])=={url for key in COMPONENTS for url in item["component_sources"][key]},"Score-source union mismatch"
    for key in COMPONENTS:
        if item["components"][key] is None:
            assert item["component_basis"][key] is None and item["component_sources"][key]==[] and item["effective_weights"][key] is None,"Unscored dimension must be empty"
        else:
            assert item["component_basis"][key] and item["component_sources"][key],"Scored dimension requires basis and sources"
            assert all(url.startswith("https://") for url in item["component_sources"][key]),"Score sources must be HTTPS"
    if len(evidenced)<3:
        assert item["score"] is None and item["weighted_average"] is None,"Fewer than three evidenced dimensions must be unrated"
    else:
        denominator=sum(WEIGHTS[key] for key in evidenced)
        weighted=sum(item["components"][key]*WEIGHTS[key] for key in evidenced)/denominator
        rounded=math.floor(weighted*2+0.5)/2
        assert item["weighted_average"]==round(weighted,3) and item["score"]==rounded,"Renormalized score arithmetic mismatch"
        assert isinstance(item["score"],(int,float)) and 1<=item["score"]<=5 and float(item["score"]*2).is_integer(),"Score must use half-star steps"
        assert abs(sum(item["effective_weights"][key] for key in evidenced)-100)<0.01,"Effective weights must renormalize to 100%"
    assert "unknown-neutral" not in json.dumps(item,ensure_ascii=False).casefold() and "unreviewed-neutral" not in json.dumps(item,ensure_ascii=False).casefold(),"Neutral placeholder basis is forbidden"
    assert "evidence_cap" not in item,"Evidence must not cap revival stars"
assert all(project_lead_scores[lead["id"]]["provisional"] is True for lead in project_leads),"E0 project-source scores must remain provisional"
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
        if tag in ("a","link","script","img","form"):
            ref=a.get("href") or a.get("src") or a.get("action")
            if ref:self.refs.append(ref)
    def handle_endtag(self,tag):
        if tag in ("script","style"):self.skip_text-=1
        if tag=="a" and self.switch_depth:self.switch_depth-=1
    def handle_data(self,text):
        if not self.skip_text and not self.switch_depth:self.text.append(text)

class FooterAudit(HTMLParser):
    """Require the same compact four-link footer on every generated page."""
    def __init__(self):
        super().__init__()
        self.in_footer=False;self.footer_count=0;self.text=[];self.anchors=[];self.current_anchor=None;self.forbidden=[]
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=="footer":
            assert not self.in_footer,"Nested footer"
            self.in_footer=True;self.footer_count+=1
            return
        if not self.in_footer:return
        if tag in {"p","div","br"}:self.forbidden.append(tag)
        if tag=="a":
            assert self.current_anchor is None,"Nested footer link"
            self.current_anchor={"href":values.get("href", ""),"text":[]}
    def handle_endtag(self,tag):
        if tag=="a" and self.current_anchor is not None:
            self.anchors.append((self.current_anchor["href"]," ".join("".join(self.current_anchor["text"]).split())))
            self.current_anchor=None
        elif tag=="footer":
            self.in_footer=False
    def handle_data(self,text):
        if not self.in_footer:return
        self.text.append(text)
        if self.current_anchor is not None:self.current_anchor["text"].append(text)

def audit_footer(markup,lang,label):
    parser=FooterAudit();parser.feed(markup)
    expected_labels=["关于","数据下载","GitHub","CC BY 4.0"] if lang=="zh-CN" else ["About","Data download","GitHub","CC BY 4.0"]
    expected_text=" · ".join(expected_labels)
    normalized=" ".join("".join(parser.text).split())
    assert parser.footer_count==1 and not parser.forbidden,(label,"footer structure",parser.footer_count,parser.forbidden)
    assert normalized==expected_text,(label,"footer text",normalized)
    assert [text for _,text in parser.anchors]==expected_labels,(label,"footer link labels",parser.anchors)
    hrefs=[href for href,_ in parser.anchors]
    about_target=(OUT/("zh" if lang=="zh-CN" else "en")/"about/index.html").resolve()
    about_ref=urlsplit(hrefs[0]);download_ref=urlsplit(hrefs[1])
    about_resolved=(label.parent/unquote(about_ref.path)).resolve()
    download_resolved=(label.parent/unquote(download_ref.path)).resolve()
    assert about_resolved==download_resolved==about_target and not about_ref.fragment and download_ref.fragment=="downloads",(label,"localized footer routes",hrefs[:2])
    assert hrefs[2]==config["repository_url"] and hrefs[3]=="https://creativecommons.org/licenses/by/4.0/",(label,"external footer routes",hrefs[2:])
    assert not re.search(r"v\d+\.\d+\.\d+|\d{4}-\d{2}-\d{2}|未进行实机测试|No hands-on hardware tests|not physically tested",normalized,re.I),(label,"footer metadata must live on About")

class ProjectCardAudit(HTMLParser):
    """Audit the visible contract of every generated list card."""
    def __init__(self):
        super().__init__()
        self.current=None
        self.cards=[]
        self.void_tags={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        classes=set(a.get("class","").split())
        if tag=="article" and "project" in classes:
            assert self.current is None,"Nested project card"
            self.current={"direct":[],"depth":0,"classes":collections.Counter(),"tags":collections.Counter()}
            return
        if self.current is None:return
        self.current["depth"]+=1
        self.current["tags"][tag]+=1
        self.current["classes"].update(classes)
        if self.current["depth"]==1:
            self.current["direct"].append((tag,classes))
        if tag in self.void_tags:self.current["depth"]-=1
    def handle_startendtag(self,tag,attrs):
        if self.current is None:return
        a=dict(attrs);classes=set(a.get("class","").split())
        self.current["tags"][tag]+=1;self.current["classes"].update(classes)
        if self.current["depth"]==0:self.current["direct"].append((tag,classes))
    def handle_endtag(self,tag):
        if self.current is None:return
        if tag=="article" and self.current["depth"]==0:
            self.cards.append(self.current);self.current=None;return
        self.current["depth"]-=1
        assert self.current["depth"]>=0,"Malformed project card"

def audit_project_cards(markup,label):
    parser=ProjectCardAudit();parser.feed(markup)
    assert parser.cards,(label,"no project cards")
    forbidden={"tags","hardware-tags","device","limit","card-end","project-thumb","rating-panel"}
    for index,card in enumerate(parser.cards):
        direct=card["direct"]
        assert len(direct)==3,(label,index,"card must have exactly three direct visible groups",direct)
        assert direct[0][0]=="h3" and direct[1][0]=="p" and "card-outcome" in direct[1][1],(label,index,"card title/outcome structure")
        assert direct[2][0]=="div" and "card-meta" in direct[2][1],(label,index,"card metadata structure")
        assert card["classes"]["card-rating"]==1 and card["classes"]["evidence-tag"]==1,(label,index,"rating/evidence coverage")
        assert not (forbidden&set(card["classes"])),(label,index,"legacy card field remains",forbidden&set(card["classes"]))
        assert card["tags"]["img"]==0,(label,index,"list cards must not show images")
    return len(parser.cards)

pages={}
card_page_count=0
generated_card_count=0
for file in OUT.rglob("*.html"):
    markup=file.read_text(encoding="utf-8")
    parser=Page();parser.feed(markup);pages[file.resolve()]=parser
    assert parser.h1==1 and parser.has_title and parser.lang in {"zh-CN","en"},file
    assert len(parser.canonical)==1 and parser.canonical[0].startswith(BASE),file
    assert set(parser.alternates)=={"zh-CN","en","x-default"},file
    assert parser.alternates["x-default"]==BASE,file
    audit_footer(markup,parser.lang,file)
    if '<article class="project"' in markup:
        generated_card_count+=audit_project_cards(markup,("all generated cards",file))
        card_page_count+=1
    if file.is_relative_to(OUT/"en"):
        assert parser.lang=="en" and not re.search(r"[\u4e00-\u9fff]","".join(parser.text)),("Chinese visible text on English page",file)
assert card_page_count==18 and generated_card_count==2240,("complete generated card audit",card_page_count,generated_card_count)
assert len(pages)==2*(len(projects)+12+len(articles)+len(watchlist)+len(project_leads))+len(projects)+2
root_page=pages[(OUT/"index.html").resolve()]
english_home=pages[(OUT/"en/index.html").resolve()]
assert root_page.lang=="en" and root_page.canonical==[BASE]
assert english_home.canonical==[BASE]
assert root_page.alternates["en"]==BASE and root_page.alternates["zh-CN"]==BASE+"zh/"
assert "home-search" in root_page.ids and "home-q" in root_page.ids
assert config["community_url"] in root_page.refs
for lang in ["zh","en"]:
    assert config["community_url"] in pages[(OUT/lang/"index.html").resolve()].refs
    assert config["community_url"] in pages[(OUT/lang/"community/index.html").resolve()].refs
    directory_page=pages[(OUT/lang/"directory/index.html").resolve()]
    assert "directory-grid" in directory_page.ids and "directory-filters" in directory_page.ids
    assert "directory.json" in " ".join(directory_page.refs) and "directory.csv" in " ".join(directory_page.refs)
    directory_markup=(OUT/lang/"directory/index.html").read_text(encoding="utf-8")
    audit_project_cards(directory_markup,(lang,"directory"))
    assert directory_markup.count('data-needs-review="true"')==147,(lang,"directory needs-review markers")
    assert '<select id="directory-sort"><option value="score-desc">' in directory_markup,(lang,"directory default star sort")
    project_source_index=pages[(OUT/lang/"project-sources/index.html").resolve()]
    assert "project-source-grid" in project_source_index.ids and "project-source-filters" in project_source_index.ids
    assert "project-leads.json" in " ".join(project_source_index.refs) and "project-leads.csv" in " ".join(project_source_index.refs)
    project_source_markup=(OUT/lang/"project-sources/index.html").read_text(encoding="utf-8")
    audit_project_cards(project_source_markup,(lang,"project sources"))
    assert project_source_markup.count('data-needs-review="true"')==147,(lang,"project-source needs-review markers")
    assert '<select id="project-source-sort"><option value="score-desc">' in project_source_markup,(lang,"project-source default star sort")
    for project in projects:
        assert f"../projects/{project['id']}/" in project_source_index.refs,(lang,project["id"],"missing reviewed project-source link")
    for lead in project_leads:
        assert f"../project-leads/{lead['id']}/" in project_source_index.refs,(lang,lead["id"],"missing E0 project-source link")
        source_page=pages[(OUT/lang/"project-leads"/lead["id"]/"index.html").resolve()]
        assert source_page.canonical==[f"{BASE}{lang}/project-leads/{lead['id']}/"]
        assert lead["repo_url"] in source_page.refs,(lang,lead["id"],"missing upstream repository link")
        source_markup=(OUT/lang/"project-leads"/lead["id"]/"index.html").read_text(encoding="utf-8")
        assert source_markup.count('class="needs-review"')==1,(lang,lead["id"],"missing compact review marker")
        assert 'class="detail-wrap record-detail"' in source_markup and source_markup.count('class="about-link"')==1,(lang,lead["id"],"simplified project-source detail")
        assert '<ul' in source_markup,(lang,lead["id"],"project-source detail bullets")
        assert 'class="detail-score"' in source_markup and 'class="detail-rating' in source_markup and 'class="rating-panel"' not in source_markup,(lang,lead["id"],"simplified project-source score")
    home=pages[(OUT/lang/"index.html").resolve()]
    home_markup=(OUT/lang/"index.html").read_text(encoding="utf-8")
    expected_placeholder="输入你的设备" if lang=="zh" else "Enter your device"
    assert "home-search" in home.ids and "home-q" in home.ids,(lang,"homepage search")
    assert f'placeholder="{expected_placeholder}"' in home_markup,(lang,"homepage search placeholder")
    assert home_markup.count('class="home-subtitle"')==1,(lang,"homepage subtitle")
    assert home_markup.count('class="category-entry"')>=4,(lang,"homepage popular categories")
    assert all(token not in home_markup for token in ['id="filters"','id="project-grid"','class="field-note"','class="facts-strip"','class="featured"','class="closing"']),(lang,"legacy homepage section remains")
    leads_index=pages[(OUT/lang/"leads/index.html").resolve()]
    audit_project_cards((OUT/lang/"leads/index.html").read_text(encoding="utf-8"),(lang,"device leads"))
    assert '<select id="lead-sort"><option value="score-desc">' in (OUT/lang/"leads/index.html").read_text(encoding="utf-8"),(lang,"lead default star sort")
    about=pages[(OUT/lang/"about/index.html").resolve()]
    about_markup=(OUT/lang/"about/index.html").read_text(encoding="utf-8")
    assert about.canonical==[f"{BASE}{lang}/about/"] and {"release","evidence","scoring","contribute","downloads"}<=about.ids,(lang,"About anchors")
    assert 'class="scoring-weights"' in about_markup,(lang,"About scoring table")
    assert all(f">{weight}%<" in about_markup for weight in WEIGHTS.values()),(lang,"About score weights missing")
    assert ">E0<" in about_markup and ">E3<" in about_markup and "0.5" in about_markup,(lang,"About evidence levels or half-star explanation missing")
    assert "null" in about_markup,(lang,"About nullable scoring explanation missing")
    assert ("待评分" if lang=="zh" else "Not yet rated") in about_markup,(lang,"About unrated explanation missing")
    assert f"v{config['version']}" in about_markup and all(date in about_markup for date in [data["compiled_at"][:10],device_atlas["reviewed_at"][:10],project_lead_data["published_at"]]),(lang,"About release status")
    assert ("未进行实机测试" if lang=="zh" else "No hands-on hardware tests") in about_markup,(lang,"About hands-on boundary")
    expected_catalog="catalog.en" if lang=="en" else "catalog"
    expected_downloads=["directory.json","directory.csv",f"{expected_catalog}.json",f"{expected_catalog}.csv","project-leads.json","project-leads.csv","scoring-evidence.json"]
    assert all(name in " ".join(about.refs) for name in expected_downloads),(lang,"About data downloads")
    assert config["repository_url"]+"/issues/new/choose" in about.refs,(lang,"About contribution link")
    for slug,lead in watchlist.items():
        assert f"{slug}/" in leads_index.refs,(lang,slug,"missing lead index link")
        page=pages[(OUT/lang/"leads"/slug/"index.html").resolve()]
        assert page.canonical==[f"{BASE}{lang}/leads/{slug}/"]
        assert 'class="hardware-tag"' in (OUT/lang/"leads"/slug/"index.html").read_text(encoding="utf-8"),(lang,slug,"missing hardware tag")
        lead_markup=(OUT/lang/"leads"/slug/"index.html").read_text(encoding="utf-8")
        assert 'class="detail-wrap record-detail"' in lead_markup and lead_markup.count('class="about-link"')==1,(lang,slug,"simplified lead detail")
        assert '<ul' in lead_markup,(lang,slug,"lead detail bullets")
        assert 'class="detail-score"' in lead_markup and 'class="detail-rating' in lead_markup and 'class="rating-panel"' not in lead_markup,(lang,slug,"simplified lead score")
        expected=[item["url"] for item in watchlist_details[slug]["resources"]]
        assert all(url in page.refs for url in expected),(lang,slug,"missing lead source")
    for slug,article in articles.items():
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
for name in ["catalog.json","catalog.csv","directory.json","directory.csv","project-leads.json","project-leads.csv","deep-dives.json","candidates.json","x-research.json","watchlist-expansion.json","device-atlas.json","device-reviews.json","project-images.json","hardware-tags.json","scoring-evidence.json"]:
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
        markup=(OUT/lang/"projects"/pid/"index.html").read_text(encoding="utf-8")
        assert 'class="hardware-tag"' in markup,(lang,pid,"missing hardware tag")
        assert 'class="detail-wrap record-detail"' in markup and markup.count('class="about-link"')==1,(lang,pid,"simplified project detail")
        assert '<ul' in markup,(lang,pid,"project detail bullets")
        assert 'class="detail-score"' in markup and 'class="detail-rating' in markup and 'class="rating-panel"' not in markup,(lang,pid,"simplified project score")
        assert parser.canonical==[f"{BASE}{lang}/projects/{pid}/"]
        assert parser.alternates["en"]==f"{BASE}en/projects/{pid}/"
        assert parser.alternates["zh-CN"]==f"{BASE}zh/projects/{pid}/"
        repo=urlsplit(next(p["repo_url"] for p in projects if p["id"]==pid))
        owner_parts=[part for part in repo.path.split("/") if part]
        if repo.netloc in {"github.com","codeberg.org"} and len(owner_parts)>=2:
            assert f"{repo.scheme}://{repo.netloc}/{owner_parts[0]}" in parser.refs,(lang,pid,"missing repository owner identity")
        if pid in project_images:
            image=project_images[pid]
            expected="../../../"+image["local_file"]
            assert expected in parser.refs,(lang,pid,"missing project detail image")
            assert image["source_page"] in parser.refs,(lang,pid,"missing image attribution link")
            assert "project-media" in markup and image["caption_zh" if lang=="zh" else "caption_en"] in markup,(lang,pid,"missing image caption")
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
directory=load(ROOT/"data/directory.json")
expected_directory=build_directory_export(projects=projects,project_leads=project_leads,watchlist=watchlist,details=watchlist_details,base_url=BASE,version=config["version"],generated_at=scoring_evidence.get("generated_at",data["compiled_at"]),scoring_evidence=scoring_evidence)
assert directory==expected_directory,"Unified directory JSON is stale"
assert (ROOT/"data/directory.csv").read_text(encoding="utf-8-sig")==directory_csv(directory).removeprefix("\ufeff"),"Unified directory CSV is stale"
assert directory["counts"]["entries"]==len(projects)+len(project_leads)+len(watchlist)
assert directory["counts"]["independent_project_sources"]==200
assert directory["counts"]["project_source_leads"]==147
assert directory["schema_version"]==directory["scoring_version"]=="3.0.0"
assert directory["counts"]["score_coverage"]==directory["counts"]["rated"]
assert directory["counts"]["rated"]+directory["counts"]["not_yet_rated"]==directory["counts"]["entries"]
assert directory["weights"]==WEIGHTS and directory["counts"]["needs_review"]==147
expected_buckets={str(int(value)) if value.is_integer() else f"{value:.1f}" for value in HALF_STAR_BUCKETS}
assert set(directory["counts"]["score_distribution"])==expected_buckets
assert sum(directory["counts"]["score_distribution"].values())==directory["counts"]["rated"]
assert sum(entry["needs_review"] for entry in directory["entries"])==147
assert all(entry["needs_review"]==(entry["kind"]=="project-source-lead") for entry in directory["entries"])
assert directory["counts"]["unique_primary_source_urls"]>=200,"Fewer than 200 distinct primary-source URLs"
for entry in directory["entries"]:
    if entry["score"]["score"] is None:
        assert entry["score"]["label_zh"]=="待评分",(entry["entry_id"],"Chinese unrated label mismatch")
        assert entry["score"]["label_en"]=="Not yet rated",(entry["entry_id"],"English unrated label mismatch")
with (ROOT/"data/directory.csv").open(encoding="utf-8-sig",newline="") as f:
    directory_rows=list(csv.DictReader(f))
assert [row["entry_id"] for row in directory_rows]==[entry["entry_id"] for entry in directory["entries"]],"Unified JSON/CSV entry mismatch"
for row,entry in zip(directory_rows,directory["entries"]):
    expected_score=entry["score"]["score"]
    expected_average=entry["score"]["weighted_average"]
    assert (row["score"]=="" if expected_score is None else float(row["score"])==expected_score),(entry["entry_id"],"CSV total score mismatch")
    assert (row["weighted_average"]=="" if expected_average is None else float(row["weighted_average"])==expected_average),(entry["entry_id"],"CSV weighted average mismatch")
    assert row["needs_review"].lower()==str(entry["needs_review"]).lower() and row["source_url"]==entry["source_url"],(entry["entry_id"],"Unified JSON/CSV facts mismatch")
    assert all((row[key]=="" if entry["score"]["components"][key] is None else int(row[key])==entry["score"]["components"][key]) for key in COMPONENTS),(entry["entry_id"],"Raw score CSV mismatch")
    assert json.loads(row["component_basis"])==entry["score"]["component_basis"],(entry["entry_id"],"Score basis CSV mismatch")
    assert json.loads(row["component_sources"])==entry["score"]["component_sources"],(entry["entry_id"],"Score sources CSV mismatch")
    assert json.loads(row["score_sources"])==entry["score"]["score_sources"],(entry["entry_id"],"Score-source union CSV mismatch")
    assert json.loads(row["effective_weights"])==entry["score"]["effective_weights"],(entry["entry_id"],"Effective-weight CSV mismatch")
    assert int(row["evidenced_dimensions"])==entry["score"]["evidenced_dimensions"],(entry["entry_id"],"Evidenced-dimension CSV mismatch")
with (ROOT/"data/project-leads.csv").open(encoding="utf-8-sig",newline="") as f:
    project_lead_rows=list(csv.DictReader(f))
assert [row["id"] for row in project_lead_rows]==[lead["id"] for lead in project_leads],"Project-source JSON/CSV entry mismatch"
assert all(row["needs_review"].lower()=="true" for row in project_lead_rows),"Project-source CSV needs_review mismatch"
assert (ROOT/"data/project-leads.csv").read_text(encoding="utf-8-sig")==project_leads_csv(project_leads).removeprefix("\ufeff"),"Project-source CSV is stale"
mapping=load(OUT/"data/url-mapping.json")["mappings"]
assert len(mapping)==len(projects)
for source,target in mapping.items():
    assert pages[(OUT/source).resolve()].canonical==[BASE+target]
import xml.etree.ElementTree as ET
urls=[node.text for node in ET.parse(OUT/"sitemap.xml").findall(".//{*}loc")]
assert len(urls)==len(set(urls))==2*(len(projects)+12+len(articles)+len(watchlist)+len(project_leads))
lastmods=[node.text for node in ET.parse(OUT/"sitemap.xml").findall(".//{*}lastmod")]
scoring_dates=[value[:10] for value in [scoring_evidence.get("checked_at"),*(entry.get("checked_at") for entry in scoring_evidence_items)] if value]
expected_lastmod=max(data["compiled_at"][:10],device_atlas["reviewed_at"][:10],project_lead_data["published_at"],*scoring_dates)
assert len(lastmods)==len(urls) and set(lastmods)=={expected_lastmod},"Sitemap lastmod mismatch"
assert BASE in urls and BASE+"en/" not in urls
assert BASE+"zh/about/" in urls and BASE+"en/about/" in urls
for url in urls:
    assert url.startswith(BASE)
    target=OUT/url[len(BASE):]
    if target.is_dir():target=target/"index.html"
    assert target.resolve() in pages
# Block credentials and private machine paths, not harmless public repository names.
secret_patterns=[r"gh[pousr]_[A-Za-z0-9]{25,}",r"github_pat_[A-Za-z0-9_]{30,}",r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}",r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----",r"C:\\\\Users\\\\",r"C:\\\\work\\\\\.secrets"]
retired_unrated_label="".join(chr(value) for value in (0x5c1a,0x672a,0x8bc4,0x5206))
placeholder_artifact="?"*3
for file in ROOT.rglob("*"):
    if not file.is_file() or ".git" in file.parts or "__pycache__" in file.parts:continue
    if file.suffix not in {".json",".csv",".md",".html",".js",".css",".yml",".py",".txt"}:continue
    text=file.read_text(encoding="utf-8-sig")
    assert "\ufffd" not in text,("UTF8 replacement character",file)
    assert retired_unrated_label not in text,("Retired unrated label",file)
    assert placeholder_artifact not in text,("Placeholder artifact",file)
    for pattern in secret_patterns:
        assert not re.search(pattern,text),("Potential sensitive content",file)
print(json.dumps({"schema":"PASS","unique_ids":len(ids),"families":len(set(p["family"] for p in projects)),"categories":len(set(p["category"] for p in projects)),"deep_dives":len(deep),"independent_project_sources":len(projects)+len(project_leads),"project_source_leads":len(project_leads),"device_source_reviews":len(device_reviews["items"]),"remaining_e0_leads":len(watchlist)-len(device_reviews["items"]),"scoring_batch_entries":len(scoring_entry_pairs),"directory_entries":directory["counts"]["entries"],"distinct_primary_source_urls":directory["counts"]["unique_primary_source_urls"],"rated":directory["counts"]["rated"],"not_yet_rated":directory["counts"]["not_yet_rated"],"score_weights":directory["weights"],"score_distribution":directory["counts"]["score_distribution"],"needs_review":directory["counts"]["needs_review"],"html_pages_and_internal_links":"PASS","csv_json_parity":"PASS","public_file_scan":"PASS","catalog_evidence":dict(collections.Counter(p["evidence"]["level"] for p in projects))},ensure_ascii=False,indent=2))
