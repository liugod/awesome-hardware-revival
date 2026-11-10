"""Validate editorial invariants, exports and all generated internal links."""
import collections
import csv
import hashlib
import html
from html.parser import HTMLParser
import json
import math
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

import jsonschema

from scoring import COMPONENTS, HALF_STAR_BUCKETS, WEIGHTS, build_directory_export, directory_csv, export_json_text, project_leads_csv, score_all, tutorial_source_url_allowed
from v120_cost_build import EXPECTED_IDS as V119_RATED_ENTRY_IDS
from watchlist_merge import load_watchlist

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"docs"
def load(path): return json.loads(path.read_text(encoding="utf-8"))
data=load(ROOT/"data/catalog.json")
project_i18n=load(ROOT/"data/i18n/en.json")["projects"]
config=load(ROOT/"site.config.json")
project_lead_data=load(ROOT/"data/project-leads.json")
project_leads=project_lead_data["projects"]
listed_project_leads=[lead for lead in project_leads if lead.get("display_status","listed")=="listed"]
lead_project_upgrade_data=load(ROOT/"data/lead-project-upgrades.json")
lead_project_upgrades=lead_project_upgrade_data["projects"]
lead_project_route_overrides={item["source_entry_id"]:item["id"] for item in lead_project_upgrades}
page_overrides=load(ROOT/"data/project-page-visual.json")
articles=load(ROOT/"data/articles.json")
guides=load(ROOT/"data/guides.json")
xiaomi_router_data=load(ROOT/"data/xiaomi-openwrt-routers.json")
xiaomi_router_slug=xiaomi_router_data["guide_slug"]
xiaomi_router_model_ids=tuple(model for group in xiaomi_router_data["groups"] for model in group["models"])
xiaomi_router_model_id_set=set(xiaomi_router_model_ids)
xiaomi_router_aggregate_canonicals=set(xiaomi_router_data["canonical_to_aggregate"])
xiaomi_router_protected_canonicals=set(xiaomi_router_data["protected_self_canonical"])
tra35_guide_slugs=("tv-box","router","smart-plug")
guide_redirect_slugs=sorted({*guides,"ai-retrofit","nest-mini-local-ai",xiaomi_router_slug})
bare_redirect_targets={
    **{f"guides/{slug}/index.html":f"en/guides/{slug}/" for slug in guide_redirect_slugs},
    **{f"{slug}/index.html":f"en/{slug}/" for slug in ("privacy","terms","contact")},
}
lead_upgrade_redirect_targets={
    f"{lang}/{item['legacy_tail']}index.html":f"{lang}/projects/{item['id']}/"
    for lang in ("zh","en")
    for item in lead_project_upgrades
}
redirect_targets={**bare_redirect_targets,**lead_upgrade_redirect_targets}
scoring_evidence=load(ROOT/"data/scoring-evidence.json")
scoring_evidence_items=scoring_evidence["entries"]
if isinstance(scoring_evidence_items,dict):scoring_evidence_items=list(scoring_evidence_items.values())
cost_evidence=load(ROOT/"data/cost-evidence-v120.json")
cost_evidence_items=cost_evidence["entries"]
if isinstance(cost_evidence_items,dict):cost_evidence_items=list(cost_evidence_items.values())
batch2_evidence=load(ROOT/"data/scoring-evidence-batch2-v120.json")
batch2_items=batch2_evidence["entries"]
if isinstance(batch2_items,dict):batch2_items=list(batch2_items.values())
e0_audit=load(ROOT/"data/e0-audit-v120.json")
e0_audit_items=e0_audit["entries"]
if isinstance(e0_audit_items,dict):e0_audit_items=list(e0_audit_items.values())
BASE=config["base_url"].rstrip("/")+"/"
SITE_URL=urlsplit(BASE)
LOW_INBOUND_THRESHOLD=3
INBOUND_CONTENT_ROOTS={"articles","directory","guides","leads","project-leads","project-sources","projects","research","scoring"}
DIRECTORY_PAGE_SIZE=60
DIRECTORY_CATEGORIES=("audio","camera","computer","ereader","gaming","mobile","network","peripheral","smarthome","speaker","tv")
EN_CATEGORY_LABELS=dict(zip(data["labels"]["category"],["Speakers & voice","Phones & tablets","Computers & thin clients","Routers & NAS","TVs & TV boxes","E-readers & e-ink","Robots","Smart home","Cameras","Music & audio","Watches & wearables","Gaming","Printers & peripherals"]))
APPROVED_ZH_SLOGAN="二手硬件再就业指南"
assert (ROOT/"README.md").read_text(encoding="utf-8").startswith(f"# KitAgain · {APPROVED_ZH_SLOGAN}\n"),"Chinese README brand is locked by TRA-21"
app_javascript=(OUT/"assets/app.js").read_text(encoding="utf-8")
assert 'document.querySelectorAll("#directory-grid .project")' in app_javascript,"Directory filters must target directory cards"
assert "directoryForm.dataset.directoryRoot" in app_javascript and "location.assign(target)" in app_javascript,"Directory categories must navigate to static routes"
schema=load(ROOT/"data/catalog.schema.json")
jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(data)
projects=data["projects"]
expected_lead_upgrade_ids={"vcamdroid","freemarkable","atlas-ophub-hk1-box"}
assert lead_project_upgrade_data["schema_version"]=="1.0.0" and lead_project_upgrade_data["reviewed_at"]=="2026-11-07"
assert {item["id"] for item in lead_project_upgrades}==expected_lead_upgrade_ids and len(lead_project_route_overrides)==3
assert {item["hub_tail"] for item in lead_project_upgrades}=={"directory/camera/","guides/kindle-displays/","guides/tv-box/"}
for item in lead_project_upgrades:
    assert item["legacy_tail"] in {"project-leads/vcamdroid/","project-leads/freemarkable/","leads/atlas-ophub-hk1-box/"},item["id"]
    assert item["source_entry_id"]==f'{item["source_kind"]}:{item["source_id"]}',item["id"]
    assert item["category"] in DIRECTORY_CATEGORIES and len(item["sources"])>=2,item["id"]
    for source in item["sources"]:
        assert source["url"].startswith("https://github.com/") and source["zh_label"] and source["en_label"],item["id"]
        assert source["revision"] is None or re.fullmatch(r"[0-9a-f]{40}",source["revision"]),item["id"]
    for lang in ("zh","en"):
        localized=item[lang]
        required={"title","summary","outcome","applicable_devices","prerequisites","stop_conditions","risks","recovery","good_fit","not_fit","hub_label"}
        assert required<=set(localized), (item["id"],lang,"missing localized field")
        assert all(len(localized[key])>=2 for key in ("applicable_devices","prerequisites","stop_conditions","risks","recovery","good_fit","not_fit")),(item["id"],lang,"thin module")
seo_project_ids={"coreelec","fbink","openbeken","dafang","armbian-tv","webos-homebrew","rootmytv"}
seo_project_lead_ids={"airsane","dorita980","kiosk-satellite","espurna"}
assert seo_project_ids<=set(page_overrides["projects"]),"Missing TRA-26 project SEO override"
assert seo_project_lead_ids<=set(page_overrides["project_leads"]),"Missing TRA-26 project-lead SEO override"
for kind,target_ids in [("projects",seo_project_ids),("project_leads",seo_project_lead_ids)]:
    for target_id in target_ids:
        override=page_overrides[kind][target_id]
        seo=override["seo"]["en"]
        lead=override["content"]["en"]["lead"]
        assert 45<=len(seo["title"])<=60 and seo["title"].endswith(" | KitAgain"),(target_id,"SEO title length/brand")
        assert 120<=len(seo["description"])<=160,(target_id,"meta description length")
        assert len(lead)>=120 and target_id.casefold().replace("-", " ").split()[0] in lead.casefold(),(target_id,"opening lead")
tra31_project_ids={"openbeken","dafang","armbian-tv","webos-homebrew"}
tra31_project_lead_ids={"espurna"}
for kind,target_ids in [("projects",tra31_project_ids),("project_leads",tra31_project_lead_ids)]:
    for target_id in target_ids:
        override=page_overrides[kind][target_id]
        assert set(override["seo"])>={"en","zh"} and set(override["content"])>={"en","zh"},(target_id,"TRA-31 bilingual override")
        assert APPROVED_ZH_SLOGAN in override["seo"]["zh"]["title"],(target_id,"locked Chinese title brand")
        assert len(override["content"]["zh"]["lead"])>=60,(target_id,"Chinese opening lead")
tra38_override=page_overrides["projects"]["rootmytv"]
assert set(tra38_override["seo"])=={"en","zh"} and set(tra38_override["content"])=={"en","zh"},"TRA-38 bilingual RootMyTV override"
assert set(tra38_override["intent_html"])=={"en","zh"},"TRA-38 bilingual rootability answer"
assert "Root My LG TV" in tra38_override["seo"]["en"]["title"] and "Root" in tra38_override["seo"]["zh"]["title"],"TRA-38 title intent"
assert all(term in tra38_override["intent_html"]["en"] for term in ["2016 / 3.4.2","2021 / 6.3.0","Older versions may still fail","Firmware downgrade"]),"TRA-38 English fit and risk boundaries"
assert all(term in tra38_override["intent_html"]["zh"] for term in ["2016 / 3.4.2","2021 / 6.3.0","更旧版本也可能无法使用","无法降级"]),"TRA-38 Chinese fit and risk boundaries"
for kind,target_id,record in [
    ("articles","kindle-model-firmware",articles["kindle-model-firmware"]),
    ("guides","kindle-displays",guides["kindle-displays"]),
]:
    for lang in ["en","zh"]:
        seo=record[lang]["seo"]
        assert seo["title"] and seo["description"],(kind,target_id,lang,"TRA-31 SEO override")
    assert 45<=len(record["en"]["seo"]["title"])<=60 and record["en"]["seo"]["title"].endswith(" | KitAgain"),(kind,target_id,"English SEO title")
    assert 120<=len(record["en"]["seo"]["description"])<=160,(kind,target_id,"English meta description")
    assert APPROVED_ZH_SLOGAN in record["zh"]["seo"]["title"],(kind,target_id,"locked Chinese title brand")
project_image_data=load(ROOT/"data/project-images.json")
directory_images={item["entry_id"]:item for item in project_image_data["entries"]}
project_images={item["project_id"]:item for item in project_image_data["entries"] if item.get("project_id")}
fallback_image_data=load(ROOT/"data/thumbnail-fallbacks.json")
fallback_images={item["entry_id"]:item for item in fallback_image_data["entries"]}
all_directory_images={**fallback_images,**directory_images}
hardware_tag_data=load(ROOT/"data/hardware-tags.json")
project_hardware_tags=hardware_tag_data["projects"]
lead_hardware_tags=hardware_tag_data["leads"]
assert project_image_data["version"]==config["version"]==data["version"],"Project-image version mismatch"
assert hardware_tag_data["version"]==config["version"],"Hardware-tag version mismatch"
assert len(directory_images)==len(project_image_data["entries"]),"Duplicate directory-image entry ID"
assert set(project_images)<=set(p["id"] for p in projects),"Project image points to missing project"
assert not (set(directory_images)&set(fallback_images)),"Fallback duplicates an existing project image"
for entry_id,image in directory_images.items():
    assert image["source_kind"] in {"upstream-project-asset","upstream-source-page-image","kitagain-project-illustration"},entry_id
    assert image["entry_kind"] in {"reviewed-project","project-source-lead","device-or-community-route"},entry_id
    assert image["fit"] in {"cover","contain"},entry_id
    assert all(image[key] for key in ["content_id","source_file","local_file","source_page","alt_zh","alt_en","caption_zh","caption_en","image_license_status","normalized_sha256"]),entry_id
    assert image["source_page"].startswith("https://") and not image["local_file"].startswith("docs/"),entry_id
    source_file=ROOT/image["source_file"]
    output_file=OUT/image["local_file"]
    assert source_file.is_file() and output_file.is_file(),entry_id
    assert output_file.stat().st_size>2000,entry_id
    assert hashlib.sha256(source_file.read_bytes()).hexdigest()==image["normalized_sha256"],entry_id
    if image.get("normalized_source"):
        assert source_file.read_bytes()==output_file.read_bytes(),entry_id
    if image["source_kind"] in {"upstream-project-asset","upstream-source-page-image"}:
        assert image["source_url"] and image["source_url"].startswith("https://"),entry_id
        assert image["image_license_status"]=="not-separately-stated",entry_id
    else:
        assert image["source_url"] is None and image.get("prompt_summary"),entry_id
        assert "不是实机照片" in image["caption_zh"] and "not an actual device photo" in image["caption_en"],entry_id
author_socials=load(ROOT/"data/author-socials.json")
watchlist,watchlist_details=load_watchlist(ROOT/"data")
project_leads_by_id={lead["id"]:lead for lead in project_leads}
for item in lead_project_upgrades:
    if item["source_kind"]=="project-lead":
        assert item["source_id"] in project_leads_by_id and project_leads_by_id[item["source_id"]].get("display_status","listed")=="listed",item["id"]
    else:
        assert item["source_kind"]=="lead" and item["source_id"] in watchlist,item["id"]
directory_category_counts=collections.Counter(project["category"] for project in projects)
directory_category_counts.update(lead["category"] for lead in watchlist.values())
directory_category_counts.update(lead["category"] for lead in listed_project_leads)
assert all(directory_category_counts[category]>0 for category in DIRECTORY_CATEGORIES),"Every static directory category must be non-empty"
static_category_entry_count=sum(directory_category_counts[category] for category in DIRECTORY_CATEGORIES)
static_category_page_count=sum(math.ceil(directory_category_counts[category]/DIRECTORY_PAGE_SIZE) for category in DIRECTORY_CATEGORIES)
project_ids={project["id"] for project in projects}
project_lead_ids={lead["id"] for lead in listed_project_leads}
for slug in tra35_guide_slugs:
    guide=guides[slug]
    assert len(guide["entries"])>=6,(slug,"TRA-35 guide entry count")
    entry_keys=[(entry["kind"],entry["id"]) for entry in guide["entries"]]
    assert len(entry_keys)==len(set(entry_keys)),(slug,"duplicate guide entry")
    for entry in guide["entries"]:
        kind,item_id=entry["kind"],entry["id"]
        assert ((kind=="project" and item_id in project_ids) or
                (kind=="lead" and item_id in watchlist) or
                (kind=="project-lead" and item_id in project_lead_ids)),(slug,kind,item_id,"unknown guide entry")
        assert entry["zh_anchor"] and entry["en_anchor"],(slug,kind,item_id,"device-action anchor")
    for lang in ("en","zh"):
        seo=guide[lang]["seo"]
        assert seo["title"] and seo["description"] and guide[lang]["title"] and guide[lang]["intro"],(slug,lang,"guide copy")
    assert 45<=len(guide["en"]["seo"]["title"])<=60 and guide["en"]["seo"]["title"].endswith(" | KitAgain"),(slug,"English SEO title")
    assert 120<=len(guide["en"]["seo"]["description"])<=160,(slug,"English meta description")
    assert APPROVED_ZH_SLOGAN in guide["zh"]["seo"]["title"],(slug,"locked Chinese title brand")
listed_image_ids={f'project:{project["id"]}' for project in projects}
listed_image_ids|={f'project-lead:{lead["id"]}' for lead in project_leads if lead.get("display_status","listed")=="listed"}
listed_image_ids|={f"lead:{slug}" for slug in watchlist}
assert set(directory_images)<=listed_image_ids,"Directory image points to a missing or delisted entry"
assert project_image_data["coverage"]=={
    "listed_directory_entries":len(listed_image_ids),
    "source_backed_images":sum(image["source_kind"]!="kitagain-project-illustration" for image in directory_images.values()),
    "kitagain_illustrations":sum(image["source_kind"]=="kitagain-project-illustration" for image in directory_images.values()),
    "pending_review_placeholders":len(listed_image_ids)-len(directory_images),
},"Directory-image coverage summary mismatch"
missing_image_data=load(ROOT/"research/tra-19-directory-image-missing.json")
missing_image_ids={item["entry_id"] for item in missing_image_data["entries"]}
assert len(missing_image_ids)==len(missing_image_data["entries"])==191,"TRA-19 missing-image baseline drift"
assert set(fallback_images)==missing_image_ids==listed_image_ids-set(directory_images),"Fallback coverage must exactly match the TRA-19 gap"
assert set(all_directory_images)==listed_image_ids and len(all_directory_images)==543,"Every listed entry needs one image"
assert fallback_image_data["version"]==config["version"] and fallback_image_data["counts"]=={
    "originally_missing":191,
    "resolved":191,
    "unresolved":0,
    "by_source_kind":{kind:collections.Counter(image["source_kind"] for image in fallback_images.values()).get(kind,0) for kind in ["hardware-photo","brand-logo","category-illustration"]},
},"Fallback ledger coverage summary mismatch"
for entry_id,image in fallback_images.items():
    assert image["source_kind"] in {"hardware-photo","brand-logo","category-illustration"},entry_id
    assert image["fit"] in {"cover","contain"} and image["fallback_image"]==image["local_file"],entry_id
    assert image["source_url"].startswith("https://") and image["license"]["name"] and image["license"]["url"].startswith("https://"),entry_id
    assert all(image[key] for key in ["content_id","entry_kind","alt_zh","alt_en","caption_zh","caption_en","asset_sha256","inference","original_missing_reason"]),entry_id
    assert "备用" in image["alt_zh"] and "Fallback" in image["alt_en"],entry_id
    asset=OUT/image["local_file"]
    assert asset.is_file() and asset.suffix==".svg" and 200<asset.stat().st_size<128000,entry_id
    assert hashlib.sha256(asset.read_bytes()).hexdigest()==image["asset_sha256"],entry_id
device_atlas=load(ROOT/"data/device-atlas.json")
device_atlas_by_slug={item["slug"]:item for item in device_atlas["items"]}
assert xiaomi_router_data["schema_version"]=="1.0.0" and xiaomi_router_data["reviewed_at"]=="2026-11-10"
assert xiaomi_router_slug=="xiaomi-openwrt-routers"
assert len(xiaomi_router_model_ids)==len(xiaomi_router_model_id_set)>=8
assert xiaomi_router_model_id_set<=set(watchlist) and xiaomi_router_model_id_set<=set(device_atlas_by_slug)
assert all(device_atlas_by_slug[slug]["category"]=="network" for slug in xiaomi_router_model_ids)
assert xiaomi_router_aggregate_canonicals<=xiaomi_router_model_id_set
assert xiaomi_router_protected_canonicals<=xiaomi_router_model_id_set
assert xiaomi_router_aggregate_canonicals.isdisjoint(xiaomi_router_protected_canonicals)
assert xiaomi_router_aggregate_canonicals=={
    "atlas-enshi-xiaomi-ax1800",
    "atlas-enshi-xiaomi-ax3600",
    "atlas-enshi-xiaomi-ax6000",
    "atlas-enshi-xiaomi-mi-router-3g-v2",
    "atlas-enshi-xiaomi-mi-router-4",
    "atlas-enshi-xiaomi-mi-router-4c",
},"Canonical consolidation must remain a narrow explicit allowlist"
assert {
    "atlas-enshi-xiaomi-ax9000",
    "atlas-enshi-xiaomi-mi-router-ac2100",
    "atlas-enshi-xiaomi-redmi-router-ac2100",
    "atlas-enshi-xiaomi-mi-router-3g",
    "atlas-enshi-xiaomi-mi-router-3-pro",
    "atlas-enshi-xiaomi-mi-router-ax3000t",
}<=xiaomi_router_protected_canonicals,"Clicked, ambiguous, or strongly ranking Xiaomi pages must remain self-canonical"
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
allowed_scoring_topics=set(scoring_evidence["scope"])
assert {"kindle-ereader","router","old-mini-pc-nas","smart-speaker","tv-box","old-phone-tablet","smart-home","e-reader"}<=allowed_scoring_topics,"Scoring-evidence scope mismatch"
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
    if "qualified" in entry:
        assert entry["qualified"]==(scored_components>=3),(entry_id,"Batch qualification mismatch")
    else:
        assert scored_components>=3,(entry_id,"Published batch-1 entry requires at least three evidenced dimensions")
    serialized=json.dumps(entry,ensure_ascii=False).casefold()
    assert "unknown-neutral" not in serialized and "unreviewed-neutral" not in serialized,entry_id

# v1.20 research ledgers are release inputs, not informal notes. Validate their
# frozen scopes and source-bounded null policy before comparing generated output.
assert cost_evidence["version"]==batch2_evidence["version"]==e0_audit["version"]==config["version"],"v1.20 ledger version mismatch"
assert len(cost_evidence_items)==cost_evidence["actual_entries"]==95,"Cost ledger must cover the frozen 95-entry v1.19 rated set"
assert {item["entry_id"] for item in cost_evidence_items}==set(V119_RATED_ENTRY_IDS),"Cost ledger scope drifted from the v1.19 rated set"
assert len({item["entry_id"] for item in cost_evidence_items})==95,"Duplicate cost-ledger entry"
for item in cost_evidence_items:
    assert item["checked_at"]==cost_evidence["checked_at"] and re.fullmatch(r"\d{4}-\d{2}-\d{2}",item["checked_at"]),item["entry_id"]
    assert item["assessment_sources"] and all(url.startswith("https://") for url in item["assessment_sources"]),item["entry_id"]
    for range_key,sources_key in [("used_price_range","used_price_sources"),("modding_cost_range","modding_cost_sources")]:
        value=item[range_key]
        sources=item[sources_key]
        assert bool(value)==bool(sources),(item["entry_id"],range_key,"range/source mismatch")
        if value:
            assert 0<=value["low"]<=value["high"] and value["currency"] and value["market"],(item["entry_id"],range_key)
            assert value["scope_zh"] and value["scope_en"] and value["source_urls"]==sources,(item["entry_id"],range_key)
            assert all(url.startswith("https://") for url in sources),(item["entry_id"],range_key)
    complete=bool(item["used_price_range"] and item["modding_cost_range"])
    assert complete==(item["cost_score"] is not None),(item["entry_id"],"Cost score requires both evidence classes")
    if complete:
        assert isinstance(item["cost_score"],int) and 1<=item["cost_score"]<=5 and item["null_reason_zh"] is None and item["null_reason_en"] is None,item["entry_id"]
    else:
        assert item["cost_score"] is None and item["null_reason_zh"] and item["null_reason_en"],item["entry_id"]
    assert item["basis_zh"] and item["basis_en"],item["entry_id"]
cost_filled=sum(item["cost_score"] is not None for item in cost_evidence_items)
used_price_filled=sum(item["used_price_range"] is not None for item in cost_evidence_items)
modding_cost_filled=sum(item["modding_cost_range"] is not None for item in cost_evidence_items)
assert (cost_filled,used_price_filled,modding_cost_filled)==(cost_evidence["filled"],cost_evidence["used_price_filled"],cost_evidence["modding_cost_filled"])
assert cost_evidence["lacking_source"]==95-cost_filled and cost_evidence["partial_only"]==sum((item["used_price_range"] is None)!=(item["modding_cost_range"] is None) for item in cost_evidence_items)
cost_urls={url for item in cost_evidence_items for key in ["used_price_sources","modding_cost_sources","assessment_sources"] for url in item[key]}|set(cost_evidence["methodology"]["fx_reference"]["sources"])
assert cost_evidence["source_validation"]["unique_urls"]==len(cost_urls) and set(cost_evidence["source_validation"]["browser_fallback_urls"])<=cost_urls,"Cost source-validation inventory mismatch"

assert len(batch2_items)==batch2_evidence["actual_entries"]==100,"Batch-2 attempt count mismatch"
assert len({item["entry_id"] for item in batch2_items})==100 and {item["entry_id"] for item in batch2_items}<=valid_scoring_entry_ids,"Invalid batch-2 entry IDs"
qualified=sum(sum(component is not None for component in item["components"].values())>=3 for item in batch2_items)
assert qualified==batch2_evidence["qualified_entries"]==96 and batch2_evidence["still_unrated"]==4,"Batch-2 qualification counts mismatch"
assert batch2_evidence["counts"]["actual_entries"]==100 and batch2_evidence["counts"]["qualified_entries"]==96 and batch2_evidence["counts"]["still_unrated"]==4,"Batch-2 declared counts mismatch"
canonical_scoring={entry_id:entry for entry_id,entry in scoring_entry_pairs}
for item in batch2_items:
    assert item["checked_at"]==batch2_evidence["checked_at"] and item["qualified"]==(sum(component is not None for component in item["components"].values())>=3),item["entry_id"]
    assert canonical_scoring[item["entry_id"]]["components"]==item["components"],(item["entry_id"],"Canonical scoring differs from batch-2 evidence")
    assert item["source_checks"] and all(check["url"].startswith("https://") and check["checked_at"]==batch2_evidence["checked_at"] for check in item["source_checks"]),item["entry_id"]

assert len(e0_audit_items)==e0_audit["counts"]["audited"]==30,"E0 audit size mismatch"
assert len({item["project_id"] for item in e0_audit_items})==30,"Duplicate E0 audit target"
audit_outcome_to_level={"upgraded-e1":"E1","upgraded-e2":"E2","stays-e0":"E0","rejected-delisted":"E0"}
audit_outcomes=collections.Counter(item["outcome"] for item in e0_audit_items)
assert audit_outcomes==collections.Counter({"upgraded-e1":18,"upgraded-e2":7,"stays-e0":1,"rejected-delisted":4}),"E0 audit outcome mismatch"
lead_by_id={lead["id"]:lead for lead in project_leads}
audit_urls=set()
for item in e0_audit_items:
    assert item["entry_id"]==f"project-lead:{item['project_id']}" and item["project_id"] in lead_by_id,item["project_id"]
    assert item["resulting_evidence_level"]==audit_outcome_to_level[item["outcome"]] and item["checked_at"]==e0_audit["checked_at"],item["project_id"]
    assert item["rationale_zh"] and item["rationale_en"] and item["evidence_sources"],item["project_id"]
    for source in item["evidence_sources"]:
        assert source["title"] and source["publisher"] and source["url"].startswith("https://") and source["accessed_at"]==e0_audit["checked_at"],item["project_id"]
        audit_urls.add(source["url"])
    for key in ["installation","compatibility","recovery"]:
        block=item[key]
        assert block["status"] and block["zh"] and block["en"] and block["source_urls"],(item["project_id"],key)
        assert all(url.startswith("https://") for url in block["source_urls"]),(item["project_id"],key)
        audit_urls.update(block["source_urls"])
    audit_urls.update(item["tutorial_sources"])
    for block in (item.get("action_guide") or {}).values():
        audit_urls.update(block["source_urls"])
    lead=lead_by_id[item["project_id"]]
    assert lead["audit_outcome"]==item["outcome"] and lead["evidence_level"]==item["resulting_evidence_level"],item["project_id"]
    assert lead["display_status"]==("delisted" if item["outcome"]=="rejected-delisted" else "listed"),item["project_id"]
assert e0_audit["source_validation"]["unique_urls"]==len(audit_urls) and e0_audit["source_validation"]["verified_total"]==len(audit_urls) and e0_audit["source_validation"]["unresolved"]==0,"E0 audit source-validation inventory mismatch"
assert set(e0_audit["source_validation"]["browser_fallback_urls"])<=audit_urls,"E0 audit fallback URL is not cited"
assert device_atlas["version"]==device_reviews["version"]==config["version"],"Device-data version mismatch"
assert project_lead_data["version"]==config["version"],"Project-source version mismatch"
assert len(device_atlas["items"])==300 and device_atlas["counts"]["total"]==300, "Device atlas must contain 300 new records"
assert len(projects)+len(watchlist)==400, "Reviewed-project/device-route denominator must equal 400"
assert len(projects)+len(project_leads)==200, "Independent project-source denominator must equal 200"
assert len(projects)+len(project_leads)+len(watchlist)==547, "Unified public-entry denominator must equal 547"
assert len(project_leads)==project_lead_data["counts"]["total"]==147,"Expected 147 retained project-source leads"
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
    assert lead["evidence_level"] in {"E0","E1","E2"} and lead["source_access"]=="repository-metadata-reviewed" and lead["readme_access"]=="opening-section-read",lead["id"]
    assert lead.get("display_status","listed") in {"listed","delisted"},lead["id"]
    if lead.get("audit_outcome"):
        assert lead["audit_outcome"] in {"upgraded-e1","upgraded-e2","stays-e0","rejected-delisted"},lead["id"]
        assert lead["audit_reason_zh"] and lead["audit_reason_en"] and lead["audit_sources"],lead["id"]
        assert all(url.startswith("https://") for url in lead["audit_sources"]),lead["id"]
    else:
        assert lead["evidence_level"]=="E0" and lead["needs_review"] is True and lead["display_status"]=="listed",lead["id"]
    assert lead["fork"] is False and isinstance(lead["archived"],bool),lead["id"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",lead["checked_at"]),lead["id"]
    assert all(lead[key] for key in ["name","summary_zh","summary_en","device_scope_zh","device_scope_en","use_case_zh","use_case_en","pushed_at","default_branch","reason_zh","reason_en"]),lead["id"]
    assert lead["github_description"] is None or isinstance(lead["github_description"],str),lead["id"]
assert project_lead_data["counts"]["evidence"]=={level:sum(lead["evidence_level"]==level for lead in project_leads) for level in ["E0","E1","E2","E3"]}
assert project_lead_data["counts"]["needs_review"]==sum(lead["needs_review"] for lead in project_leads)
assert project_lead_data["counts"]["listed"]==len(listed_project_leads) and project_lead_data["counts"]["delisted"]==len(project_leads)-len(listed_project_leads)
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
project_scores,lead_scores,project_lead_scores=score_all(projects,watchlist,watchlist_details,project_leads,scoring_evidence,cost_evidence)
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
assert all(project_lead_scores[lead["id"]]["provisional"] is lead["needs_review"] for lead in project_leads),"Project-source provisional flag mismatch"
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
        self.refs=[]; self.anchor_hrefs=[]; self.ids=set(); self.h1=0; self.canonical=[]; self.has_title=False; self.lang=None
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
        if tag=="a" and a.get("href"):self.anchor_hrefs.append(a["href"])
        if tag in ("a","link","script","img","form"):
            ref=a.get("href") or a.get("src") or a.get("action")
            if ref:self.refs.append(ref)
    def handle_endtag(self,tag):
        if tag in ("script","style"):self.skip_text-=1
        if tag=="a" and self.switch_depth:self.switch_depth-=1
    def handle_data(self,text):
        if not self.skip_text and not self.switch_depth:self.text.append(text)

def resolve_internal_ref(source_file,ref):
    """Resolve one generated-site reference, or return None for an external URL."""
    url=urlsplit(ref)
    if url.scheme or url.netloc:
        if (url.scheme and url.scheme not in {"http","https"}) or url.netloc.casefold()!=SITE_URL.netloc.casefold():
            return None
        site_path=unquote(SITE_URL.path)
        ref_path=unquote(url.path)
        if site_path!="/" and not ref_path.startswith(site_path):
            return None
        target=(OUT/ref_path[len(site_path):].lstrip("/")).resolve()
    elif url.path.startswith("/"):
        target=(OUT/unquote(url.path).lstrip("/")).resolve()
    else:
        target=(source_file.parent/unquote(url.path)).resolve() if url.path else source_file
    if target.is_dir():target=target/"index.html"
    return target,url

def public_route(file):
    relative=file.relative_to(OUT.resolve()).as_posix()
    if relative=="index.html":return "/"
    if relative.endswith("/index.html"):return "/"+relative.removesuffix("index.html")
    return "/"+relative

def is_inbound_content_page(file):
    relative=file.relative_to(OUT.resolve())
    if relative.as_posix()=="index.html":return True
    return len(relative.parts)>=2 and relative.parts[0] in {"en","zh"} and (
        relative.parts[1]=="index.html" or relative.parts[1] in INBOUND_CONTENT_ROOTS
    )

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
            self.current={"direct":[],"depth":0,"classes":collections.Counter(),"tags":collections.Counter(),"article_classes":classes}
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
    forbidden={"tags","hardware-tags","device","limit","card-end","rating-panel"}
    for index,card in enumerate(parser.cards):
        direct=card["direct"]
        has_media="has-media" in card["article_classes"]
        has_image="has-image" in card["article_classes"]
        has_placeholder="has-placeholder" in card["article_classes"]
        content_offset=1 if has_media else 0
        assert has_media and has_image and not has_placeholder,(label,index,"every list card must have an image")
        assert len(direct)==3+content_offset,(label,index,"card visible group count",direct)
        if has_image:
            assert direct[0][0]=="a" and "project-thumb" in direct[0][1],(label,index,"card thumbnail structure")
            assert card["classes"]["project-thumb"]==1 and card["tags"]["img"]==1,(label,index,"card thumbnail coverage")
        assert direct[content_offset][0]=="h3" and direct[content_offset+1][0]=="p" and "card-outcome" in direct[content_offset+1][1],(label,index,"card title/outcome structure")
        assert direct[content_offset+2][0]=="div" and "card-meta" in direct[content_offset+2][1],(label,index,"card metadata structure")
        assert card["classes"]["card-rating"]==1 and card["classes"]["evidence-tag"]==1,(label,index,"rating/evidence coverage")
        assert not (forbidden&set(card["classes"])),(label,index,"legacy card field remains",forbidden&set(card["classes"]))
    return len(parser.cards)

def audit_detail_navigation(file,markup,lang,category,title,current_url,label):
    breadcrumb_match=re.findall(r'<nav class="breadcrumbs"[^>]*>(.*?)</nav>',markup,re.S)
    schema_match=re.findall(r'<script type="application/ld\+json" class="breadcrumb-schema">(.*?)</script>',markup,re.S)
    assert len(breadcrumb_match)==len(schema_match)==1,(label,"breadcrumb/schema count")
    breadcrumb=breadcrumb_match[0]
    schema=json.loads(schema_match[0])
    assert schema["@context"]=="https://schema.org" and schema["@type"]=="BreadcrumbList",(label,"BreadcrumbList type")
    items=schema["itemListElement"]
    assert len(items)==3 and [item["position"] for item in items]==[1,2,3],(label,"breadcrumb positions")
    home_url=BASE if lang=="en" else BASE+"zh/"
    category_url=(
        f"{BASE}{lang}/directory/{category}/"
        if category in DIRECTORY_CATEGORIES
        else f"{BASE}{lang}/directory/"
    )
    expected_names=["Home" if lang=="en" else "首页",(EN_CATEGORY_LABELS if lang=="en" else data["labels"]["category"])[category],title]
    assert [item["name"] for item in items]==expected_names,(label,"breadcrumb names")
    assert [item["item"] for item in items]==[home_url,category_url,current_url],(label,"breadcrumb URLs")
    assert f'href="{home_url}"' in breadcrumb and 'aria-current="page"' in breadcrumb,(label,"visible home/current breadcrumb")
    assert html.escape(expected_names[1],quote=True) in breadcrumb and html.escape(title,quote=True) in breadcrumb,(label,"visible breadcrumb labels")
    related_match=re.findall(r'<section class="related-projects"[^>]*>(.*?)</section>',markup,re.S)
    assert len(related_match)==1,(label,"related-project block count")
    related_links=re.findall(r'<a class="related-project-link" href="([^"]+)">([^<]+)</a>',related_match[0])
    assert 3<=len(related_links)<=6 and len(related_links)==4,(label,"related-project count")
    assert len({href for href,_ in related_links})==len(related_links),(label,"duplicate related target")
    assert all(" — " in html.unescape(anchor) for _,anchor in related_links),(label,"action-style related anchor")
    normalized=[]
    for href,_ in related_links:
        target=(file.parent/unquote(urlsplit(href).path)).resolve()
        assert target.is_relative_to(OUT.resolve()) and target.exists(),(label,href,"related target missing")
        parts=target.relative_to(OUT.resolve()).parts
        assert parts[0]==lang and parts[-1]=="index.html",(label,href,"related target language")
        normalized.append("/".join(parts[1:]))
    return tuple(normalized)

def audit_guide_navigation(markup,lang,title,current_url,label):
    breadcrumb_match=re.findall(r'<nav class="breadcrumbs"[^>]*>(.*?)</nav>',markup,re.S)
    schema_match=re.findall(r'<script type="application/ld\+json" class="breadcrumb-schema">(.*?)</script>',markup,re.S)
    assert len(breadcrumb_match)==len(schema_match)==1,(label,"breadcrumb/schema count")
    schema=json.loads(schema_match[0])
    assert schema["@context"]=="https://schema.org" and schema["@type"]=="BreadcrumbList",(label,"BreadcrumbList type")
    items=schema["itemListElement"]
    home_url=BASE if lang=="en" else BASE+"zh/"
    expected_names=["Home" if lang=="en" else "首页","Device guides" if lang=="en" else "设备指南",title]
    assert len(items)==3 and [item["position"] for item in items]==[1,2,3],(label,"breadcrumb positions")
    assert [item["name"] for item in items]==expected_names,(label,"breadcrumb names")
    assert [item["item"] for item in items]==[home_url,home_url+"#device-guides",current_url],(label,"breadcrumb URLs")
    assert 'aria-current="page"' in breadcrumb_match[0] and html.escape(title,quote=True) in breadcrumb_match[0],(label,"visible breadcrumb")

pages={}
card_page_count=0
generated_card_count=0
for file in OUT.rglob("*.html"):
    markup=file.read_text(encoding="utf-8")
    parser=Page();parser.feed(markup);pages[file.resolve()]=parser
    assert parser.h1==1 and parser.has_title and parser.lang in {"zh-CN","en"},file
    assert len(parser.canonical)==1 and parser.canonical[0].startswith(BASE),file
    assert set(parser.alternates)=={"zh-CN","en","x-default"},file
    assert parser.alternates["x-default"]==parser.alternates["en"],file
    audit_footer(markup,parser.lang,file)
    if re.search(r'<article class="project(?:\s|")',markup):
        generated_card_count+=audit_project_cards(markup,("all generated cards",file))
        card_page_count+=1
    if file.is_relative_to(OUT/"en"):
        assert parser.lang=="en" and not re.search(r"[\u4e00-\u9fff]","".join(parser.text)),("Chinese visible text on English page",file)
delisted_count=len(project_leads)-len(listed_project_leads)
directory_page_count=math.ceil((len(projects)+len(watchlist)+len(listed_project_leads))/DIRECTORY_PAGE_SIZE)
tra35_guide_card_count=sum(len(guides[slug]["entries"]) for slug in tra35_guide_slugs)
assert card_page_count==18+2*len(tra35_guide_slugs)+2*(directory_page_count-1)+2*static_category_page_count and generated_card_count==2240+2*tra35_guide_card_count-4*delisted_count+2*static_category_entry_count,("complete generated card audit",card_page_count,generated_card_count)
assert len(pages)==2*(len(projects)+12+len(guides)+len(articles)+len(watchlist)+len(listed_project_leads))+len(projects)+2+4+2*(directory_page_count-1)+2*static_category_page_count+len(redirect_targets)+2
root_page=pages[(OUT/"index.html").resolve()]
english_home=pages[(OUT/"en/index.html").resolve()]
for kind,target_ids,route in [
    ("projects",seo_project_ids,"projects"),
    ("project_leads",seo_project_lead_ids,"project-leads"),
]:
    for target_id in target_ids:
        override=page_overrides[kind][target_id]
        seo=override["seo"]["en"]
        lead=override["content"]["en"]["lead"]
        markup=(OUT/"en"/route/target_id/"index.html").read_text(encoding="utf-8")
        escaped_title=html.escape(seo["title"],quote=True)
        escaped_description=html.escape(seo["description"],quote=True)
        assert f"<title>{escaped_title}</title>" in markup,(target_id,"rendered title")
        assert f'<meta name="description" content="{escaped_description}">' in markup,(target_id,"rendered description")
        assert f'<meta property="og:title" content="{escaped_title}">' in markup,(target_id,"rendered OG title")
        assert f'<meta property="og:description" content="{escaped_description}">' in markup,(target_id,"rendered OG description")
        assert html.escape(lead,quote=True) in markup,(target_id,"rendered opening lead")
for lang in ["en","zh"]:
    tra31_rendered=[]
    for target_id in tra31_project_ids:
        tra31_rendered.append(("projects",target_id,page_overrides["projects"][target_id]["seo"][lang],page_overrides["projects"][target_id]["content"][lang]["lead"]))
    for target_id in tra31_project_lead_ids:
        tra31_rendered.append(("project-leads",target_id,page_overrides["project_leads"][target_id]["seo"][lang],page_overrides["project_leads"][target_id]["content"][lang]["lead"]))
    tra31_rendered.extend([
        ("articles","kindle-model-firmware",articles["kindle-model-firmware"][lang]["seo"],None),
        ("guides","kindle-displays",guides["kindle-displays"][lang]["seo"],None),
    ])
    for route,target_id,seo,lead in tra31_rendered:
        markup=(OUT/lang/route/target_id/"index.html").read_text(encoding="utf-8")
        escaped_title=html.escape(seo["title"],quote=True)
        escaped_description=html.escape(seo["description"],quote=True)
        assert f"<title>{escaped_title}</title>" in markup,(lang,target_id,"TRA-31 rendered title")
        assert f'<meta name="description" content="{escaped_description}">' in markup,(lang,target_id,"TRA-31 rendered description")
        assert f'<meta property="og:title" content="{escaped_title}">' in markup,(lang,target_id,"TRA-31 rendered OG title")
        assert f'<meta property="og:description" content="{escaped_description}">' in markup,(lang,target_id,"TRA-31 rendered OG description")
        if lead:
            assert html.escape(lead,quote=True) in markup,(lang,target_id,"TRA-31 rendered opening lead")
    rootmytv_markup=(OUT/lang/"projects/rootmytv/index.html").read_text(encoding="utf-8")
    rootmytv_seo=tra38_override["seo"][lang]
    rootmytv_lead=tra38_override["content"][lang]["lead"]
    assert f'<title>{html.escape(rootmytv_seo["title"],quote=True)}</title>' in rootmytv_markup,(lang,"TRA-38 rendered title")
    assert f'<meta name="description" content="{html.escape(rootmytv_seo["description"],quote=True)}">' in rootmytv_markup,(lang,"TRA-38 rendered description")
    assert html.escape(rootmytv_lead,quote=True) in rootmytv_markup,(lang,"TRA-38 rendered opening answer")
    assert tra38_override["intent_html"][lang] in rootmytv_markup,(lang,"TRA-38 rendered fit and risk section")
    assert all(link in rootmytv_markup for link in ["../../guides/tv-box/index.html","../webos-homebrew/index.html"]),(lang,"TRA-38 visible intent links")
    webos_homebrew_markup=(OUT/lang/"projects/webos-homebrew/index.html").read_text(encoding="utf-8")
    assert '../rootmytv/index.html' in webos_homebrew_markup,(lang,"TRA-38 Homebrew reciprocal link")
zh_home_markup=(OUT/"zh/index.html").read_text(encoding="utf-8")
assert zh_home_markup.count(f"<h1>{APPROVED_ZH_SLOGAN}</h1>")==1,"Chinese homepage slogan is locked by TRA-21"
assert zh_home_markup.count(f'<p class="ai-kicker">KitAgain · {APPROVED_ZH_SLOGAN}</p>')==1,"Chinese homepage kicker is locked by TRA-21"
assert re.search(fr"<title>[^<]+ · {APPROVED_ZH_SLOGAN} · KitAgain</title>",zh_home_markup),"Chinese title brand is locked by TRA-21"
assert re.search(fr'<meta property="og:title" content="[^"]+ · {APPROVED_ZH_SLOGAN} · KitAgain">',zh_home_markup),"Chinese og:title brand is locked by TRA-21"
assert re.search(fr'<a class="brand"[^>]*><span class="brand-mark">↻</span><span>{APPROVED_ZH_SLOGAN}</span></a>',zh_home_markup),"Chinese header brand is locked by TRA-21"
assert root_page.lang=="en" and root_page.canonical==[BASE]
assert english_home.canonical==[BASE]
assert root_page.alternates["en"]==BASE and root_page.alternates["zh-CN"]==BASE+"zh/"
assert "home-search" in root_page.ids and "home-q" in root_page.ids
assert config["community_url"] in root_page.refs
homepage_user_copy={
    "en": [
        "Give your old hardware a useful second life.",
        "See what your device can do next.",
        "See what it can do",
        "See the outcome first",
        "No proof, no promise",
        "Find by device",
        "Open the matching guide, then verify your exact model.",
    ],
    "zh": [
        APPROVED_ZH_SLOGAN,
        "输入设备或型号，看看它还能做什么。",
        "看看能做什么",
        "先看能做什么",
        "没证据，就不下结论",
        "按设备找",
        "先打开对应指南，再核对你的准确型号。",
    ],
}
root_home_markup=(OUT/"index.html").read_text(encoding="utf-8")
assert all(text in root_home_markup for text in homepage_user_copy["en"]),"Root homepage user-copy contract"
related_target_sets={}
for lang in ["zh","en"]:
    assert config["community_url"] in pages[(OUT/lang/"index.html").resolve()].refs
    assert config["community_url"] in pages[(OUT/lang/"community/index.html").resolve()].refs
    directory_page=pages[(OUT/lang/"directory/index.html").resolve()]
    assert "directory-grid" in directory_page.ids and "directory-filters" in directory_page.ids
    directory_markup=(OUT/lang/"directory/index.html").read_text(encoding="utf-8")
    parameter_seo_marker='<script data-query-param-seo>'
    assert directory_markup.count(parameter_seo_marker)==1,(lang,"directory query-parameter SEO guard")
    assert 'p.has("q")||p.has("category")' in directory_markup,(lang,"directory filter parameters covered")
    assert 'r.content="noindex,follow"' in directory_markup,(lang,"directory filtered views noindex")
    assert f'||"{BASE}{lang}/directory/"' in directory_markup,(lang,"directory filtered-view clean canonical")
    for category in DIRECTORY_CATEGORIES:
        assert f'"{category}":"{BASE}{lang}/directory/{category}/"' in directory_markup,(lang,category,"parameter category canonical")
    audit_project_cards(directory_markup,(lang,"directory"))
    directory_markups=[directory_markup]
    for page_number in range(2,directory_page_count+1):
        paged_file=OUT/lang/"directory"/"page"/str(page_number)/"index.html"
        paged=pages[paged_file.resolve()]
        assert "directory-grid" in paged.ids and "directory-filters" in paged.ids,(lang,page_number,"paged directory shell")
        assert paged.canonical==[f"{BASE}{lang}/directory/page/{page_number}/"],(lang,page_number,"paged directory canonical")
        paged_markup=paged_file.read_text(encoding="utf-8")
        assert paged_markup.count(parameter_seo_marker)==1,(lang,page_number,"paged query-parameter SEO guard")
        assert f'||"{BASE}{lang}/directory/"' in paged_markup,(lang,page_number,"paged filtered-view clean canonical")
        directory_markups.append(paged_markup)
    combined_directory_markup="".join(directory_markups)
    assert sum(audit_project_cards(markup,(lang,"directory page",index)) for index,markup in enumerate(directory_markups,1))==len(projects)+len(watchlist)+len(listed_project_leads),(lang,"paged directory coverage")
    assert combined_directory_markup.count('<a class="project-thumb ')==len(all_directory_images),(lang,"complete directory thumbnail coverage")
    assert 'project-thumb-placeholder' not in combined_directory_markup and 'Image pending review' not in combined_directory_markup and '图片待核' not in combined_directory_markup,(lang,"placeholder must be absent")
    for source_kind,count in fallback_image_data["counts"]["by_source_kind"].items():
        assert combined_directory_markup.count(f'data-image-kind="{source_kind}"')==count,(lang,source_kind,"fallback source-kind count")
    assert combined_directory_markup.count(' has-media ')==len(projects)+len(watchlist)+len(listed_project_leads),(lang,"directory media coverage")
    assert combined_directory_markup.count('data-ai="native"')==10,(lang,"reviewed AI-function route count")
    listed_needs_review=sum(lead["needs_review"] for lead in listed_project_leads)
    assert combined_directory_markup.count('data-needs-review="true"')==listed_needs_review,(lang,"directory needs-review markers")
    assert 'class="detail-head directory-head"><h1>' in directory_markup,(lang,"directory heading")
    assert all(token not in directory_markup for token in ['class="eyebrow"','class="intro"','class="actions"','class="boundary"','id="directory-share"','id="directory-share-status"']),(lang,"directory top must stay minimal")
    assert directory_markup.count("<select")==4,(lang,"directory visible filter count")
    assert all(f'id="directory-{control}"' in directory_markup for control in ["q","category","ai","score","evidence"]),(lang,"directory search/filter controls")
    assert '<option value="native">' in directory_markup,(lang,"reviewed AI-function filter")
    assert 'id="directory-kind"' not in directory_markup and 'id="directory-sort"' not in directory_markup,(lang,"directory removed secondary controls")
    assert 'class="directory-info"' in directory_markup and '>ⓘ</a>' in directory_markup and '../about/#scoring' in directory_markup,(lang,"directory scoring info link")
    assert "directory.json" not in " ".join(directory_page.refs) and "directory.csv" not in " ".join(directory_page.refs),(lang,"directory downloads must live on About")
    generated_category_dirs={path.name for path in (OUT/lang/"directory").iterdir() if path.is_dir() and path.name!="page"}
    assert generated_category_dirs==set(DIRECTORY_CATEGORIES),(lang,"static directory category set",generated_category_dirs)
    for category in DIRECTORY_CATEGORIES:
        category_count=directory_category_counts[category]
        category_page_count=math.ceil(category_count/DIRECTORY_PAGE_SIZE)
        category_markups=[]
        for page_number in range(1,category_page_count+1):
            category_file=(
                OUT/lang/"directory"/category/"index.html"
                if page_number==1
                else OUT/lang/"directory"/category/"page"/str(page_number)/"index.html"
            )
            category_page=pages[category_file.resolve()]
            expected_canonical=f"{BASE}{lang}/directory/{category}/" + ("" if page_number==1 else f"page/{page_number}/")
            assert category_page.canonical==[expected_canonical],(lang,category,page_number,"static category canonical")
            category_markup=category_file.read_text(encoding="utf-8")
            assert '<meta name="robots" content="noindex' not in category_markup,(lang,category,page_number,"clean static category indexability")
            assert category_markup.count(parameter_seo_marker)==1,(lang,category,page_number,"category query guard")
            assert f'||"{BASE}{lang}/directory/{category}/"' in category_markup,(lang,category,page_number,"category filtered canonical")
            assert f'data-category="{category}"' in category_markup,(lang,category,page_number,"category route state")
            category_markups.append(category_markup)
        combined_category_markup="".join(category_markups)
        assert sum(audit_project_cards(markup,(lang,category,index)) for index,markup in enumerate(category_markups,1))==category_count,(lang,category,"static category coverage")
        assert set(re.findall(r'<article class="project[^>]*data-category="([^"]+)"',combined_category_markup))=={category},(lang,category,"static category purity")
    for slug in ["ai-retrofit","nest-mini-local-ai"]:
        guide=pages[(OUT/lang/"guides"/slug/"index.html").resolve()]
        assert guide.canonical==[f"{BASE}{lang}/guides/{slug}/"],(lang,slug,"guide canonical")
    for slug in tra35_guide_slugs:
        guide_file=OUT/lang/"guides"/slug/"index.html"
        guide_page=pages[guide_file.resolve()]
        guide_markup=guide_file.read_text(encoding="utf-8")
        localized=guides[slug][lang]
        assert guide_page.canonical==[f"{BASE}{lang}/guides/{slug}/"],(lang,slug,"TRA-35 guide canonical")
        assert guide_markup.count("<h1>")==1 and f'<h1>{html.escape(localized["title"])}</h1>' in guide_markup,(lang,slug,"TRA-35 guide H1")
        assert '<meta name="robots" content="noindex' not in guide_markup,(lang,slug,"TRA-35 guide indexability")
        assert audit_project_cards(guide_markup,(lang,slug,"TRA-35 guide cards"))>=6
        audit_guide_navigation(guide_markup,lang,localized["title"],f"{BASE}{lang}/guides/{slug}/",(lang,slug,"TRA-35 guide breadcrumb"))
        seo=localized["seo"]
        assert f'<title>{html.escape(seo["title"])}</title>' in guide_markup,(lang,slug,"TRA-35 guide title")
        assert f'<meta name="description" content="{html.escape(seo["description"],quote=True)}">' in guide_markup,(lang,slug,"TRA-35 guide description")
        for entry in guides[slug]["entries"]:
            upgrade_id=lead_project_route_overrides.get(f'{entry["kind"]}:{entry["id"]}')
            route=f"projects/{upgrade_id}" if upgrade_id else f'{ {"project":"projects","lead":"leads","project-lead":"project-leads"}[entry["kind"]]}/{entry["id"]}'
            assert f'href="../../{route}/"' in guide_markup,(lang,slug,entry["kind"],entry["id"],"guide route")
            assert html.escape(entry[f"{lang}_anchor"]) in guide_markup,(lang,slug,entry["id"],"localized device-action anchor")
    aggregate_file=OUT/lang/"guides"/xiaomi_router_slug/"index.html"
    aggregate_page=pages[aggregate_file.resolve()]
    aggregate_markup=aggregate_file.read_text(encoding="utf-8")
    aggregate_url=f"{BASE}{lang}/guides/{xiaomi_router_slug}/"
    assert aggregate_page.canonical==[aggregate_url],(lang,"Xiaomi aggregate self-canonical")
    assert '<meta name="robots" content="noindex' not in aggregate_markup,(lang,"Xiaomi aggregate indexability")
    assert aggregate_markup.count("<h1>")==1 and len(xiaomi_router_model_ids)>=8,(lang,"Xiaomi aggregate H1/model count")
    assert all(f'href="../../leads/{slug}/"' in aggregate_markup for slug in xiaomi_router_model_ids),(lang,"Xiaomi aggregate model coverage")
    assert '../router/' in aggregate_markup and '../../directory/network/' in aggregate_markup,(lang,"Xiaomi aggregate return links")
    assert f'../{xiaomi_router_slug}/' in (OUT/lang/"guides/router/index.html").read_text(encoding="utf-8"),(lang,"router hub Xiaomi aggregate link")
    assert f'../../guides/{xiaomi_router_slug}/' in (OUT/lang/"directory/network/index.html").read_text(encoding="utf-8"),(lang,"network directory Xiaomi aggregate link")
    audit_guide_navigation(aggregate_markup,lang,
        "Xiaomi & Redmi OpenWrt router model atlas" if lang=="en" else "Xiaomi / Redmi 路由器 OpenWrt 型号聚合",
        aggregate_url,(lang,"Xiaomi aggregate breadcrumb"))
    ai_guide_markup=(OUT/lang/"guides/ai-retrofit/index.html").read_text(encoding="utf-8")
    assert '../../directory/?ai=native' in ai_guide_markup and '../../directory/?q=AI' not in ai_guide_markup,(lang,"guide structured AI filter link")
    assert '../nest-mini-local-ai/' in ai_guide_markup,(lang,"AI retrofit hub links to Nest Mini guide")
    assert all(link in ai_guide_markup for link in ['../speaker-voice/','../../projects/onju-v2/','../../projects/onju-voice/','../../projects/openbeken/']),(lang,"AI retrofit topical links")
    speaker_guide_markup=(OUT/lang/"guides/speaker-voice/index.html").read_text(encoding="utf-8")
    assert all(link in speaker_guide_markup for link in ['../nest-mini-local-ai/','../ai-retrofit/','../../projects/onju-v2/','../../projects/onju-voice/']),(lang,"speaker hub topical links")
    nest_markup=(OUT/lang/"guides/nest-mini-local-ai/index.html").read_text(encoding="utf-8")
    assert all(term in nest_markup for term in ["Onju v2","ESPHome","Home Assistant","Ollama","I2S"]),(lang,"Nest Mini decision coverage")
    assert all(link in nest_markup for link in ['../ai-retrofit/','../speaker-voice/','../../projects/onju-v2/','../../projects/onju-voice/']),(lang,"Nest Mini guide topical links")
    for project_id in ["onju-voice","onju-v2"]:
        project_markup=(OUT/lang/"projects"/project_id/"index.html").read_text(encoding="utf-8")
        other_project="onju-v2" if project_id=="onju-voice" else "onju-voice"
        assert all(link in project_markup for link in ['../../guides/nest-mini-local-ai/index.html','../../guides/speaker-voice/index.html','../../guides/ai-retrofit/index.html',f'../{other_project}/index.html']),(lang,project_id,"Onju project topical links")
    openbeken_markup=(OUT/lang/"projects/openbeken/index.html").read_text(encoding="utf-8")
    assert '../../guides/ai-retrofit/index.html' in openbeken_markup,(lang,"OpenBeken AI retrofit link")
    reciprocal_routes={
        "tv-box":[("projects/rootmytv","../../guides/tv-box/index.html"),("projects/atlas-ophub-hk1-box","../../guides/tv-box/index.html")],
        "router":[("leads/atlas-enshi-xiaomi-ax9000","../../guides/router/index.html")],
        "smart-plug":[("projects/openbeken","../../guides/smart-plug/index.html"),("leads/atlas-esphome-sonoff-s31","../../guides/smart-plug/index.html")],
    }
    for slug,targets in reciprocal_routes.items():
        hub_markup=(OUT/lang/"guides"/slug/"index.html").read_text(encoding="utf-8")
        for route,back_link in targets:
            target_markup=(OUT/lang/route/"index.html").read_text(encoding="utf-8")
            assert "../../"+route+"/" in hub_markup,(lang,slug,route,"hub forward link")
            assert back_link in target_markup,(lang,slug,route,"detail back link")
    project_source_index=pages[(OUT/lang/"project-sources/index.html").resolve()]
    assert "project-source-grid" in project_source_index.ids and "project-source-filters" in project_source_index.ids
    assert "project-leads.json" in " ".join(project_source_index.refs) and "project-leads.csv" in " ".join(project_source_index.refs)
    project_source_markup=(OUT/lang/"project-sources/index.html").read_text(encoding="utf-8")
    audit_project_cards(project_source_markup,(lang,"project sources"))
    assert project_source_markup.count('data-needs-review="true"')==listed_needs_review,(lang,"project-source needs-review markers")
    assert '<select id="project-source-sort"><option value="score-desc">' in project_source_markup,(lang,"project-source default star sort")
    for project in projects:
        assert f"../projects/{project['id']}/" in project_source_index.refs,(lang,project["id"],"missing reviewed project-source link")
    for lead in project_leads:
        expected_file=OUT/lang/"project-leads"/lead["id"]/"index.html"
        if lead.get("display_status","listed")=="delisted":
            assert f"../project-leads/{lead['id']}/" not in project_source_index.refs and not expected_file.exists(),(lang,lead["id"],"delisted source still displayed")
            continue
        upgrade=next((item for item in lead_project_upgrades if item["source_entry_id"]==f'project-lead:{lead["id"]}'),None)
        if upgrade:
            assert f"../projects/{upgrade['id']}/" in project_source_index.refs,(lang,lead["id"],"missing upgraded project-source link")
            continue
        assert f"../project-leads/{lead['id']}/" in project_source_index.refs,(lang,lead["id"],"missing project-source link")
        source_page=pages[(OUT/lang/"project-leads"/lead["id"]/"index.html").resolve()]
        assert source_page.canonical==[f"{BASE}{lang}/project-leads/{lead['id']}/"]
        assert lead["repo_url"] in source_page.refs,(lang,lead["id"],"missing upstream repository link")
        source_markup=(OUT/lang/"project-leads"/lead["id"]/"index.html").read_text(encoding="utf-8")
        assert source_markup.count('class="needs-review"')==int(lead["needs_review"]),(lang,lead["id"],"compact review marker mismatch")
        assert 'class="detail-wrap record-detail"' in source_markup and source_markup.count('class="about-link"')==1,(lang,lead["id"],"simplified project-source detail")
        entry_image=all_directory_images[f'project-lead:{lead["id"]}']
        assert "../../../"+entry_image["local_file"] in source_page.refs and 'class="project-media ' in source_markup,(lang,lead["id"],"project-source hero image")
        assert '<ul' in source_markup,(lang,lead["id"],"project-source detail bullets")
        assert 'class="detail-score"' in source_markup and 'class="detail-rating' in source_markup and 'class="rating-panel"' not in source_markup,(lang,lead["id"],"simplified project-source score")
        expected_guide=project_lead_scores[lead["id"]]["score"] is not None and project_lead_scores[lead["id"]]["score"]>=4
        assert ('class="action-guide"' in source_markup)==expected_guide,(lang,lead["id"],"action-guide threshold")
        related_target_sets[("project-lead",lead["id"],lang)]=audit_detail_navigation(
            expected_file,source_markup,lang,lead["category"],lead["name"],f"{BASE}{lang}/project-leads/{lead['id']}/",(lang,"project-lead",lead["id"])
        )
    for upgrade in lead_project_upgrades:
        upgraded_file=OUT/lang/"projects"/upgrade["id"]/"index.html"
        upgraded_page=pages[upgraded_file.resolve()]
        upgraded_markup=upgraded_file.read_text(encoding="utf-8")
        localized=upgrade[lang]
        assert upgraded_page.canonical==[f"{BASE}{lang}/projects/{upgrade['id']}/"],(lang,upgrade["id"],"upgraded canonical")
        required_headings=(
            ("项目概述","Project overview"),("适用设备","Applicable devices"),("动手前","Before you start"),
            ("风险与恢复","Risk and recovery"),("停止条件","STOP CONDITIONS"),("相关项目","Related projects"),
        )
        assert all((zh if lang=="zh" else en) in upgraded_markup for zh,en in required_headings),(lang,upgrade["id"],"complete project modules")
        assert f'../../{upgrade["hub_tail"]}index.html' in upgraded_markup,(lang,upgrade["id"],"topic backlink")
        assert all(source["url"] in upgraded_page.refs for source in upgrade["sources"]),(lang,upgrade["id"],"source ledger")
        assert "KitAgain 已测试" not in upgraded_markup and "KitAgain tested" not in upgraded_markup,(lang,upgrade["id"],"unsupported hands-on claim")
        entry_image=all_directory_images[upgrade["source_entry_id"]]
        assert "../../../"+entry_image["local_file"] in upgraded_page.refs and 'class="project-media ' in upgraded_markup,(lang,upgrade["id"],"upgraded hero image")
        if upgrade["source_kind"]=="project-lead":
            related_source=project_leads_by_id[upgrade["source_id"]]
        else:
            related_source=watchlist[upgrade["source_id"]]
        related_target_sets[("upgrade",upgrade["id"],lang)]=audit_detail_navigation(
            upgraded_file,upgraded_markup,lang,upgrade["category"],localized["title"],f"{BASE}{lang}/projects/{upgrade['id']}/",(lang,"upgrade",upgrade["id"])
        )
    home=pages[(OUT/lang/"index.html").resolve()]
    home_markup=(OUT/lang/"index.html").read_text(encoding="utf-8")
    expected_placeholder="输入设备或型号" if lang=="zh" else "Enter a device or model"
    assert "home-search" in home.ids and "home-q" in home.ids,(lang,"homepage search")
    assert f'placeholder="{expected_placeholder}"' in home_markup,(lang,"homepage search placeholder")
    assert 'directory/?ai=native' in home_markup and 'directory/?q=AI' not in home_markup,(lang,"homepage structured AI filter link")
    assert home_markup.count('class="home-subtitle"')==1,(lang,"homepage subtitle")
    assert home_markup.count('class="ai-route-thumb ')==3,(lang,"homepage reviewed-route thumbnail coverage")
    homepage_categories=("ereader","network","computer","speaker","tv","smarthome")
    assert all(f'href="directory/{category}/"' in home_markup for category in homepage_categories),(lang,"homepage static category links")
    assert 'href="directory/?category=' not in home_markup,(lang,"homepage parameter category link remains")
    expected_home_guides=["speaker-voice","kindle-displays","home-computers","tv-box","router","smart-plug","ai-retrofit","nest-mini-local-ai"]
    assert all(f'href="guides/{slug}/"' in home_markup for slug in expected_home_guides),(lang,"homepage device guide links")
    expected_action_anchors=["旧电视与电视盒：比较","旧路由器：核对","智能插座：核对"] if lang=="zh" else ["Old TVs and TV boxes: compare","Old routers: check","Smart plugs: check"]
    assert 'id="device-guides"' in home_markup and all(text in home_markup for text in expected_action_anchors),(lang,"TRA-35 homepage action anchors")
    assert home_markup.count('class="popular-categories home-guide-links"')==1,(lang,"single homepage device-guide hub")
    assert all(token not in home_markup for token in ['id="filters"','id="project-grid"','class="field-note"','class="facts-strip"','class="featured"','class="closing"']),(lang,"legacy homepage section remains")
    assert all(text in home_markup for text in homepage_user_copy[lang]),(lang,"homepage user-copy contract")
    onju_markup=(OUT/lang/"projects/onju-v2/index.html").read_text(encoding="utf-8")
    assert ("适合你，如果" if lang=="zh" else "A good fit if") in onju_markup,(lang,"Onju fit guidance")
    assert ("无法确认设备是第二代 Nest Mini" if lang=="zh" else "cannot confirm a second-generation Nest Mini") in onju_markup,(lang,"Onju executable stop condition")
    assert ("断电后装回原主板" if lang=="zh" else "power off and reinstall the original board") in onju_markup,(lang,"Onju rollback guidance")
    assert "Recovery guide" not in onju_markup and "恢复资料" not in onju_markup,(lang,"Onju must not show an unlinked recovery guide")
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
    expected_downloads=["directory.json","directory.csv",f"{expected_catalog}.json",f"{expected_catalog}.csv","project-leads.json","project-leads.csv","scoring-evidence.json","scoring-evidence-batch2-v120.json","cost-evidence-v120.json","action-guides-v120.json","e0-audit-v120.json"]
    assert all(name in " ".join(about.refs) for name in expected_downloads),(lang,"About data downloads")
    assert any("project-sources" in ref for ref in about.refs) and "#scoring" in about.refs,(lang,"About directory links")
    for slug in ("privacy","terms","contact"):
        utility=pages[(OUT/lang/slug/"index.html").resolve()]
        utility_markup=(OUT/lang/slug/"index.html").read_text(encoding="utf-8")
        assert utility.canonical==[f"{BASE}{lang}/{slug}/"],(lang,slug,"utility canonical")
        assert utility.alternates["en"]==f"{BASE}en/{slug}/" and utility.alternates["zh-CN"]==f"{BASE}zh/{slug}/",(lang,slug,"utility alternates")
        assert 'data-client-redirect' not in utility_markup and 'http-equiv="refresh"' not in utility_markup,(lang,slug,"localized utility must be real content")
    contact_markup=(OUT/lang/"contact/index.html").read_text(encoding="utf-8")
    assert config["repository_url"]+"/issues/new/choose" in contact_markup,(lang,"contact route")
    assert config["repository_url"]+"/issues/new/choose" in about.refs,(lang,"About contribution link")
    for slug,lead in watchlist.items():
        upgrade=next((item for item in lead_project_upgrades if item["source_entry_id"]==f"lead:{slug}"),None)
        if upgrade:
            assert f"../projects/{upgrade['id']}/" in leads_index.refs,(lang,slug,"missing upgraded lead index link")
            continue
        assert f"{slug}/" in leads_index.refs,(lang,slug,"missing lead index link")
        page=pages[(OUT/lang/"leads"/slug/"index.html").resolve()]
        expected_canonical=(
            f"{BASE}{lang}/guides/{xiaomi_router_slug}/"
            if slug in xiaomi_router_aggregate_canonicals
            else f"{BASE}{lang}/leads/{slug}/"
        )
        assert page.canonical==[expected_canonical]
        assert 'class="hardware-tag"' in (OUT/lang/"leads"/slug/"index.html").read_text(encoding="utf-8"),(lang,slug,"missing hardware tag")
        lead_markup=(OUT/lang/"leads"/slug/"index.html").read_text(encoding="utf-8")
        assert '<meta name="robots" content="noindex' not in lead_markup,(lang,slug,"lead indexability")
        if slug in xiaomi_router_model_id_set:
            assert f'../../guides/{xiaomi_router_slug}/' in lead_markup,(lang,slug,"Xiaomi series entry")
            assert 'class="lead-verdict xiaomi-series-entry"' in lead_markup,(lang,slug,"prominent Xiaomi series entry")
        if slug in xiaomi_router_protected_canonicals:
            assert page.canonical==[f"{BASE}{lang}/leads/{slug}/"],(lang,slug,"protected self-canonical")
        assert 'class="detail-wrap record-detail"' in lead_markup and lead_markup.count('class="about-link"')==1,(lang,slug,"simplified lead detail")
        entry_image=all_directory_images[f"lead:{slug}"]
        assert "../../../"+entry_image["local_file"] in page.refs and 'class="project-media ' in lead_markup,(lang,slug,"lead hero image")
        assert '<ul' in lead_markup,(lang,slug,"lead detail bullets")
        assert 'class="detail-score"' in lead_markup and 'class="detail-rating' in lead_markup and 'class="rating-panel"' not in lead_markup,(lang,slug,"simplified lead score")
        expected_guide=lead_scores[slug]["score"] is not None and lead_scores[slug]["score"]>=4
        assert ('class="action-guide"' in lead_markup)==expected_guide,(lang,slug,"action-guide threshold")
        expected=[item["url"] for item in watchlist_details[slug]["resources"]]
        assert all(url in page.refs for url in expected),(lang,slug,"missing lead source")
        related_target_sets[("lead",slug,lang)]=audit_detail_navigation(
            OUT/lang/"leads"/slug/"index.html",lead_markup,lang,lead["category"],lead[lang]["title"],f"{BASE}{lang}/leads/{slug}/",(lang,"lead",slug)
        )
    for slug,article in articles.items():
        page=pages[(OUT/lang/"articles"/slug/"index.html").resolve()]
        assert page.canonical==[f"{BASE}{lang}/articles/{slug}/"]
        assert all(source["url"] in page.refs for source in article["sources"]),(lang,slug,"missing source")
broken_internal_refs=[]
internal_ref_count=0
for file,parser in pages.items():
    for url in [*parser.alternates.values(),*parser.canonical]:
        assert url.startswith(BASE),(file,url)
        target=OUT/unquote(url[len(BASE):])
        if target.is_dir():target=target/"index.html"
        assert target.resolve() in pages,(file,url,"language/canonical target missing")
    for ref in parser.refs:
        resolved=resolve_internal_ref(file,ref)
        if resolved is None:continue
        internal_ref_count+=1
        target,url=resolved
        if not target.is_relative_to(OUT.resolve()):
            broken_internal_refs.append((public_route(file),ref,"escapes generated site"))
        elif not target.exists():
            broken_internal_refs.append((public_route(file),ref,"target missing"))
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            broken_internal_refs.append((public_route(file),ref,"fragment missing"))
if broken_internal_refs:
    print(f"Broken internal references ({len(broken_internal_refs)}):",file=sys.stderr)
    for source,ref,reason in broken_internal_refs:
        print(f"  {source} -> {ref} [{reason}]",file=sys.stderr)
    raise AssertionError(f"{len(broken_internal_refs)} broken internal reference(s)")

redirect_stub_files={(OUT/source).resolve() for source in redirect_targets}
inbound_sources={file:set() for file in pages if is_inbound_content_page(file)}
for source,parser in pages.items():
    if source in redirect_stub_files:continue
    for href in parser.anchor_hrefs:
        resolved=resolve_internal_ref(source,href)
        if resolved is None:continue
        target,_=resolved
        if target in inbound_sources and target!=source:
            inbound_sources[target].add(source)
low_inbound=sorted(
    (len(sources),public_route(file))
    for file,sources in inbound_sources.items()
    if len(sources)<LOW_INBOUND_THRESHOLD
)
print(f"Internal link health: PASS ({internal_ref_count} generated internal references checked)")
print(f"Low-inbound content pages (<{LOW_INBOUND_THRESHOLD} distinct source pages; report only): {len(low_inbound)}")
for count,route in low_inbound:
    print(f"  {count}\t{route}")
for name in ["catalog.json","catalog.csv","directory.json","directory.csv","project-leads.json","project-leads.csv","lead-project-upgrades.json","deep-dives.json","candidates.json","x-research.json","watchlist-expansion.json","device-atlas.json","device-reviews.json","project-images.json","thumbnail-fallbacks.json","hardware-tags.json","scoring-evidence.json","scoring-evidence-batch2-v120.json","cost-evidence-v120.json","action-guides-v120.json","e0-audit-v120.json"]:
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
    assert set(ids)|expected_lead_upgrade_ids=={p.name for p in (OUT/lang/"projects").iterdir() if p.is_dir()}
    for pid in ids:
        parser=pages[(OUT/lang/"projects"/pid/"index.html").resolve()]
        markup=(OUT/lang/"projects"/pid/"index.html").read_text(encoding="utf-8")
        assert 'class="hardware-tag"' in markup,(lang,pid,"missing hardware tag")
        assert 'class="detail-wrap record-detail"' in markup and markup.count('class="about-link"')==1,(lang,pid,"simplified project detail")
        assert '<ul' in markup,(lang,pid,"project detail bullets")
        assert 'class="detail-score"' in markup and 'class="detail-rating' in markup and 'class="rating-panel"' not in markup,(lang,pid,"simplified project score")
        expected_guide=project_scores[pid]["score"] is not None and project_scores[pid]["score"]>=4
        assert ('class="action-guide"' in markup)==expected_guide,(lang,pid,"action-guide threshold")
        assert parser.canonical==[f"{BASE}{lang}/projects/{pid}/"]
        assert parser.alternates["en"]==f"{BASE}en/projects/{pid}/"
        assert parser.alternates["zh-CN"]==f"{BASE}zh/projects/{pid}/"
        repo=urlsplit(next(p["repo_url"] for p in projects if p["id"]==pid))
        owner_parts=[part for part in repo.path.split("/") if part]
        if repo.netloc in {"github.com","codeberg.org"} and len(owner_parts)>=2:
            assert f"{repo.scheme}://{repo.netloc}/{owner_parts[0]}" in parser.refs,(lang,pid,"missing repository owner identity")
        entry_id=f"project:{pid}"
        image=all_directory_images[entry_id]
        expected="../../../"+image["local_file"]
        assert expected in parser.refs,(lang,pid,"missing project detail image")
        image_source=image["source_url"] if entry_id in fallback_images else image["source_page"]
        assert image_source in parser.refs,(lang,pid,"missing image attribution link")
        assert "project-media" in markup and html.escape(image["caption_zh" if lang=="zh" else "caption_en"]) in markup,(lang,pid,"missing image caption")
        project=next(item for item in projects if item["id"]==pid)
        related_target_sets[("project",pid,lang)]=audit_detail_navigation(
            OUT/lang/"projects"/pid/"index.html",markup,lang,project["category"],project["name"],f"{BASE}{lang}/projects/{pid}/",(lang,"project",pid)
        )
for kind,entries in [("project",projects),("project-lead",listed_project_leads),("lead",[{"id":slug} for slug in watchlist])]:
    for entry in entries:
        if f"{kind}:{entry['id']}" in lead_project_route_overrides:
            continue
        assert related_target_sets[(kind,entry["id"],"zh")]==related_target_sets[(kind,entry["id"],"en")],(kind,entry["id"],"bilingual related-project symmetry")
for upgrade in lead_project_upgrades:
    assert related_target_sets[("upgrade",upgrade["id"],"zh")]==related_target_sets[("upgrade",upgrade["id"],"en")],("upgrade",upgrade["id"],"bilingual related-project symmetry")
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
expected_directory=build_directory_export(projects=projects,project_leads=project_leads,watchlist=watchlist,details=watchlist_details,base_url=BASE,version=config["version"],generated_at=scoring_evidence.get("generated_at",data["compiled_at"]),project_i18n=project_i18n,scoring_evidence=scoring_evidence,cost_evidence=cost_evidence,project_route_overrides=lead_project_route_overrides)
assert directory==expected_directory,"Unified directory JSON is stale"
directory_by_entry={entry["entry_id"]:entry for entry in directory["entries"]}
for item in lead_project_upgrades:
    entry=directory_by_entry[item["source_entry_id"]]
    assert entry["detail_url_en"]==f"{BASE}en/projects/{item['id']}/" and entry["detail_url_zh"]==f"{BASE}zh/projects/{item['id']}/",(item["id"],"directory canonical route")
assert (ROOT/"data/directory.csv").read_text(encoding="utf-8-sig")==directory_csv(directory).removeprefix("\ufeff"),"Unified directory CSV is stale"
assert directory["counts"]["entries"]==len(projects)+len(project_leads)+len(watchlist)
assert directory["counts"]["independent_project_sources"]==200
assert directory["counts"]["project_source_leads"]==147
assert directory["schema_version"]==directory["scoring_version"]=="3.0.0"
assert directory["counts"]["score_coverage"]==directory["counts"]["rated"]
assert directory["counts"]["rated"]+directory["counts"]["not_yet_rated"]==directory["counts"]["entries"]
assert directory["weights"]==WEIGHTS and directory["counts"]["needs_review"]==sum(lead["needs_review"] for lead in project_leads)
assert directory["counts"]["listed_entries"]==len(projects)+len(watchlist)+len(listed_project_leads)
assert directory["counts"]["delisted_entries"]==len(project_leads)-len(listed_project_leads)
expected_buckets={str(int(value)) if value.is_integer() else f"{value:.1f}" for value in HALF_STAR_BUCKETS}
assert set(directory["counts"]["score_distribution"])==expected_buckets
assert sum(directory["counts"]["score_distribution"].values())==directory["counts"]["rated"]
assert sum(entry["needs_review"] for entry in directory["entries"])==sum(lead["needs_review"] for lead in project_leads)
assert all(entry["display_status"] in {"listed","delisted"} for entry in directory["entries"])
assert directory["counts"]["unique_primary_source_urls"]>=200,"Fewer than 200 distinct primary-source URLs"
guide_entries=[]
old_boilerplate={
    "先确认准确型号、硬件修订与当前固件，并准备上游教程要求的访问、备份和恢复工具。",
    "按链接教程核对兼容范围，先备份，再逐步安装或配置；每一步只验证教程明确写出的结果。",
    "型号或固件不在文档范围、无法建立可用备份/恢复路径，或现场步骤与教程不符时停止。",
    "Confirm the exact model, hardware revision and current firmware, then prepare the access, backup and recovery tools required by the upstream guide.",
    "Check compatibility in the linked guide, back up first, then install or configure one step at a time and verify only the documented outcomes.",
    "Stop when the model or firmware is outside the documented scope, no usable backup/recovery path exists, or the observed steps diverge from the guide.",
}
unsupported_guide_claims={
    "Never mix stock-layout and OpenWrt-bootloader images.",
    "Back up partitions and calibration data",
    "不要混刷 U-Boot 布局与原厂布局镜像",
    "备份分区和校准数据",
}
for entry in directory["entries"]:
    if entry["score"]["score"] is None:
        assert entry["score"]["label_zh"]=="待评分",(entry["entry_id"],"Chinese unrated label mismatch")
        assert entry["score"]["label_en"]=="Not yet rated",(entry["entry_id"],"English unrated label mismatch")
    if entry["display_status"]=="delisted":
        assert entry["detail_url_zh"] is None and entry["detail_url_en"] is None,entry["entry_id"]
    expected_guide=entry["display_status"]=="listed" and entry["score"]["score"] is not None and entry["score"]["score"]>=4
    assert (entry["action_guide"] is not None)==expected_guide,(entry["entry_id"],"Action-guide threshold mismatch")
    if entry["action_guide"]:
        assert set(entry["action_guide"])=={"what_you_need","rough_steps","when_to_stop"},entry["entry_id"]
        assert all(item["zh"] and item["en"] and item["sources"] and all(tutorial_source_url_allowed(url) for url in item["sources"]) for item in entry["action_guide"].values()),entry["entry_id"]
        assert all(item["zh"] not in old_boilerplate and item["en"] not in old_boilerplate for item in entry["action_guide"].values()),(entry["entry_id"],"Generic action-guide boilerplate")
        assert not any(claim in item[lang] for item in entry["action_guide"].values() for lang in ("zh","en") for claim in unsupported_guide_claims),(entry["entry_id"],"Unsupported action-guide claim")
        assert all(len(item["zh"])<=280 and len(item["en"])<=440 for item in entry["action_guide"].values()),(entry["entry_id"],"Action guide is not concise")
        guide_entries.append(entry)
assert len(guide_entries)==directory["counts"]["action_guides"]
for key in ("what_you_need","rough_steps","when_to_stop"):
    for lang in ("zh","en"):
        values=[entry["action_guide"][key][lang] for entry in guide_entries]
        assert len(values)==len(set(values)),(key,lang,"Identical action-guide blocks")
def normalized_action_block(entry,key,lang):
    text=entry["action_guide"][key][lang]
    for title in (entry["title_zh"],entry["title_en"]):
        text=re.sub(re.escape(title),"<title>",text,flags=re.IGNORECASE)
    return re.sub(r"\s+"," ",text.casefold()).strip()
for key in ("what_you_need","rough_steps","when_to_stop"):
    for lang in ("zh","en"):
        normalized=[normalized_action_block(entry,key,lang) for entry in guide_entries]
        assert len(normalized)==len(set(normalized)),(key,lang,"Title-only action-guide blocks")
def normalized_guide(entry,lang):
    text=" ".join(entry["action_guide"][key][lang] for key in ("what_you_need","rough_steps","when_to_stop"))
    for title in (entry["title_zh"],entry["title_en"]):
        text=re.sub(re.escape(title),"<title>",text,flags=re.IGNORECASE)
    return re.sub(r"\s+"," ",text.casefold()).strip()
for lang in ("zh","en"):
    normalized=[normalized_guide(entry,lang) for entry in guide_entries]
    assert len(normalized)==len(set(normalized)),(lang,"Title-only action-guide boilerplate")
with (ROOT/"data/directory.csv").open(encoding="utf-8-sig",newline="") as f:
    directory_rows=list(csv.DictReader(f))
assert [row["entry_id"] for row in directory_rows]==[entry["entry_id"] for entry in directory["entries"]],"Unified JSON/CSV entry mismatch"
for row,entry in zip(directory_rows,directory["entries"]):
    expected_score=entry["score"]["score"]
    expected_average=entry["score"]["weighted_average"]
    assert (row["score"]=="" if expected_score is None else float(row["score"])==expected_score),(entry["entry_id"],"CSV total score mismatch")
    assert (row["weighted_average"]=="" if expected_average is None else float(row["weighted_average"])==expected_average),(entry["entry_id"],"CSV weighted average mismatch")
    assert row["needs_review"].lower()==str(entry["needs_review"]).lower() and row["source_url"]==entry["source_url"] and row["display_status"]==entry["display_status"],(entry["entry_id"],"Unified JSON/CSV facts mismatch")
    assert all((row[key]=="" if entry["score"]["components"][key] is None else int(row[key])==entry["score"]["components"][key]) for key in COMPONENTS),(entry["entry_id"],"Raw score CSV mismatch")
    assert json.loads(row["component_basis"])==entry["score"]["component_basis"],(entry["entry_id"],"Score basis CSV mismatch")
    assert json.loads(row["component_sources"])==entry["score"]["component_sources"],(entry["entry_id"],"Score sources CSV mismatch")
    assert json.loads(row["score_sources"])==entry["score"]["score_sources"],(entry["entry_id"],"Score-source union CSV mismatch")
    assert json.loads(row["effective_weights"])==entry["score"]["effective_weights"],(entry["entry_id"],"Effective-weight CSV mismatch")
    assert int(row["evidenced_dimensions"])==entry["score"]["evidenced_dimensions"],(entry["entry_id"],"Evidenced-dimension CSV mismatch")
    assert (row["cost_evidence"]=="")== (entry["score"].get("cost_evidence") is None),(entry["entry_id"],"Cost evidence CSV null mismatch")
    assert (row["action_guide"]=="")== (entry["action_guide"] is None),(entry["entry_id"],"Action guide CSV null mismatch")
    if row["cost_evidence"]: assert json.loads(row["cost_evidence"])==entry["score"]["cost_evidence"]
    if row["action_guide"]: assert json.loads(row["action_guide"])==entry["action_guide"]
with (ROOT/"data/project-leads.csv").open(encoding="utf-8-sig",newline="") as f:
    project_lead_rows=list(csv.DictReader(f))
assert [row["id"] for row in project_lead_rows]==[lead["id"] for lead in project_leads],"Project-source JSON/CSV entry mismatch"
assert [row["needs_review"].lower() for row in project_lead_rows]==[str(lead["needs_review"]).lower() for lead in project_leads],"Project-source CSV needs_review mismatch"
assert (ROOT/"data/project-leads.csv").read_text(encoding="utf-8-sig")==project_leads_csv(project_leads).removeprefix("\ufeff"),"Project-source CSV is stale"
mapping=load(OUT/"data/url-mapping.json")["mappings"]
assert len(mapping)==len(projects)+len(redirect_targets)
assert {source:mapping[source] for source in bare_redirect_targets}==bare_redirect_targets
assert {source:mapping[source] for source in lead_upgrade_redirect_targets}==lead_upgrade_redirect_targets
for source,target in mapping.items():
    assert pages[(OUT/source).resolve()].canonical==[BASE+target]
for source,target in redirect_targets.items():
    markup=(OUT/source).read_text(encoding="utf-8")
    target_path="/"+target
    assert '<meta name="robots" content="noindex,follow">' in markup,(source,"redirect robots")
    assert f'<meta http-equiv="refresh" content="0;url={target_path}">' in markup,(source,"meta redirect")
    assert f'window.location.replace({json.dumps(target_path)}+window.location.search+window.location.hash);' in markup,(source,"JavaScript redirect")
    assert f'href="{target_path}"' in markup,(source,"redirect fallback link")
import xml.etree.ElementTree as ET
urls=[node.text for node in ET.parse(OUT/"sitemap.xml").findall(".//{*}loc")]
assert len(urls)==len(set(urls))==2*(len(projects)+12+len(guides)+len(articles)+len(watchlist)+len(listed_project_leads))+4+2*(directory_page_count-1)+2*static_category_page_count+2-2*len(xiaomi_router_aggregate_canonicals)
lastmods=[node.text for node in ET.parse(OUT/"sitemap.xml").findall(".//{*}lastmod")]
scoring_dates=[value[:10] for value in [scoring_evidence.get("checked_at"),*(entry.get("checked_at") for entry in scoring_evidence_items)] if value]
expected_lastmod=max(data["compiled_at"][:10],device_atlas["reviewed_at"][:10],project_lead_data["published_at"],*scoring_dates)
assert len(lastmods)==len(urls),"Sitemap lastmod count mismatch"
sitemap_lastmods=dict(zip(urls,lastmods))
upgraded_project_urls={BASE+f"{lang}/projects/{upgrade['id']}/" for lang in ("zh","en") for upgrade in lead_project_upgrades}
assert all(sitemap_lastmods[url]==lead_project_upgrade_data["reviewed_at"] for url in upgraded_project_urls),"Upgraded project sitemap lastmod mismatch"
assert all(lastmod==expected_lastmod for url,lastmod in sitemap_lastmods.items() if url not in upgraded_project_urls),"Existing sitemap lastmod mismatch"
assert BASE in urls and BASE+"en/" not in urls
assert BASE+"zh/about/" in urls and BASE+"en/about/" in urls
for lang in ("en","zh"):
    for category in DIRECTORY_CATEGORIES:
        category_page_count=math.ceil(directory_category_counts[category]/DIRECTORY_PAGE_SIZE)
        assert BASE+f"{lang}/directory/{category}/" in urls,(lang,category,"static category missing from sitemap")
        for page_number in range(2,category_page_count+1):
            assert BASE+f"{lang}/directory/{category}/page/{page_number}/" in urls,(lang,category,page_number,"static category pagination missing from sitemap")
    for slug in ("tv-box","router","smart-plug"):
        assert BASE+f"{lang}/guides/{slug}/" in urls,(lang,slug,"device hub missing from sitemap")
    aggregate_url=BASE+f"{lang}/guides/{xiaomi_router_slug}/"
    assert aggregate_url in urls,(lang,"Xiaomi aggregate missing from sitemap")
    for slug in xiaomi_router_aggregate_canonicals:
        assert BASE+f"{lang}/leads/{slug}/" not in urls,(lang,slug,"canonicalized Xiaomi leaf must stay out of sitemap")
    for slug in xiaomi_router_protected_canonicals:
        assert BASE+f"{lang}/leads/{slug}/" in urls,(lang,slug,"protected Xiaomi leaf missing from sitemap")
for source,target in redirect_targets.items():
    assert BASE+source.removesuffix("index.html") not in urls,(source,"thin redirect must stay out of sitemap")
    assert BASE+target in urls,(target,"canonical redirect target missing from sitemap")
for url in urls:
    assert url.startswith(BASE)
    target=OUT/url[len(BASE):]
    if target.is_dir():target=target/"index.html"
    assert target.resolve() in pages
# Block credentials and private machine paths, not harmless public repository names.
secret_patterns=[r"gh[pousr]_[A-Za-z0-9]{25,}",r"github_pat_[A-Za-z0-9_]{30,}",r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}",r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----",r"C:\\\\Users\\\\",r"C:\\\\work\\\\\.secrets"]
retired_unrated_label="".join(chr(value) for value in (0x5c1a,0x672a,0x8bc4,0x5206))
retired_zh_brand="".join(chr(value) for value in (0x5783,0x573e,0x4f6c,0x590d,0x6d3b,0x7ad9))
retired_zh_tagline="".join(chr(value) for value in (0x786c,0x4ef6,0x590d,0x6d3b,0x91ce,0x5916,0x6307,0x5357))
placeholder_artifact="?"*3
for file in ROOT.rglob("*"):
    if not file.is_file() or ".git" in file.parts or "__pycache__" in file.parts:continue
    if file.suffix not in {".json",".csv",".md",".html",".js",".css",".yml",".py",".txt"}:continue
    text=file.read_text(encoding="utf-8-sig")
    assert "\ufffd" not in text,("UTF8 replacement character",file)
    assert retired_unrated_label not in text,("Retired unrated label",file)
    if file.is_relative_to(OUT) or file.is_relative_to(ROOT/"scripts"):
        assert retired_zh_brand not in text,("Retired Chinese brand",file)
        assert retired_zh_tagline not in text,("Retired Chinese tagline",file)
    assert placeholder_artifact not in text,("Placeholder artifact",file)
    for pattern in secret_patterns:
        assert not re.search(pattern,text),("Potential sensitive content",file)
print(json.dumps({"schema":"PASS","unique_ids":len(ids),"families":len(set(p["family"] for p in projects)),"categories":len(set(p["category"] for p in projects)),"deep_dives":len(deep),"independent_project_sources":len(projects)+len(project_leads),"project_source_leads":len(project_leads),"device_source_reviews":len(device_reviews["items"]),"remaining_e0_leads":len(watchlist)-len(device_reviews["items"]),"scoring_batch_entries":len(scoring_entry_pairs),"directory_entries":directory["counts"]["entries"],"listed_directory_images":len(all_directory_images),"fallback_source_kinds":fallback_image_data["counts"]["by_source_kind"],"empty_or_placeholder_images":0,"distinct_primary_source_urls":directory["counts"]["unique_primary_source_urls"],"rated":directory["counts"]["rated"],"not_yet_rated":directory["counts"]["not_yet_rated"],"score_weights":directory["weights"],"score_distribution":directory["counts"]["score_distribution"],"needs_review":directory["counts"]["needs_review"],"html_pages_and_internal_links":"PASS","csv_json_parity":"PASS","public_file_scan":"PASS","catalog_evidence":dict(collections.Counter(p["evidence"]["level"] for p in projects))},ensure_ascii=False,indent=2))
