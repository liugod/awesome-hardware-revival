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

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"docs"
def load(path): return json.loads(path.read_text(encoding="utf-8"))
data=load(ROOT/"data/catalog.json")
schema=load(ROOT/"data/catalog.schema.json")
jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)
projects=data["projects"]
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
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="html":self.lang=a.get("lang")
        if tag=="h1":self.h1+=1
        if tag=="title":self.has_title=True
        if a.get("id"):self.ids.add(a["id"])
        if tag=="link" and a.get("rel")=="canonical":self.canonical.append(a.get("href"))
        if tag in ("a","link","script","img"):
            ref=a.get("href") or a.get("src")
            if ref:self.refs.append(ref)

pages={}
for file in OUT.rglob("*.html"):
    parser=Page();parser.feed(file.read_text(encoding="utf-8"));pages[file.resolve()]=parser
    assert parser.h1==1 and parser.has_title and parser.lang=="zh-CN",file
    assert len(parser.canonical)==1 and parser.canonical[0].startswith("https://liugod.github.io/awesome-hardware-revival/"),file
assert len(pages)==len(projects)+2
for file,parser in pages.items():
    for ref in parser.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc:continue
        target=(file.parent/unquote(url.path)).resolve() if url.path else file
        if target.is_dir():target=target/"index.html"
        assert target.is_relative_to(OUT.resolve()),(file,ref,"escapes site")
        assert target.exists(),(file,ref,"missing")
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids,(file,ref,"missing anchor")
for name in ["catalog.json","catalog.csv","deep-dives.json","candidates.json","x-research.json"]:
    assert (OUT/"data"/name).read_bytes()==(ROOT/"data"/name).read_bytes(),name
assert set(ids)=={p.stem for p in (OUT/"projects").glob("*.html")}
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
