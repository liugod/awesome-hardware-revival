"""Deterministic five-dimension revival-value scoring for KitAgain.

The 1–5 star score is an editorial comparison across feasibility, expected
cost, documentation/community activity, practical value, and operational
risk. Missing dimensions stay null. A total is published only when at least
three dimensions have source-backed scores; the available weights are then
renormalized. Evidence level (E0–E3) is deliberately separate: it never caps
or enters the arithmetic.
"""

from __future__ import annotations

import collections
import csv
from datetime import datetime
import io
import json
import math
from urllib.parse import urljoin


SCORING_VERSION = "3.0.0"
WEIGHTS = {
    "feasibility": 25,
    "cost": 15,
    "docs_community": 20,
    "practical_value": 20,
    "risk": 20,
}
COMPONENTS = tuple(WEIGHTS)
BODY_ACCESS = {
    "source-page-reviewed",
    "source-body-reviewed",
    "post-text-and-project-read",
}
HALF_STAR_BUCKETS = tuple(step / 2 for step in range(2, 11))


def _round_half(value: float) -> float:
    """Round a positive value to the nearest half, with exact ties upward."""
    return math.floor(value * 2 + 0.5) / 2


def _format_score(value: float) -> str:
    return str(int(value)) if value.is_integer() else f"{value:.1f}"


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _recent(last_push: str | None, checked_at: str | None, days: int = 365) -> bool:
    pushed = _parse_time(last_push)
    checked = _parse_time(checked_at)
    return bool(pushed and checked and 0 <= (checked - pushed).days <= days)


def _score_label(score: float) -> tuple[str, str]:
    if score <= 1.5:
        return "谨慎评估", "Caution"
    if score <= 2.5:
        return "条件较多", "More constraints"
    if score <= 3.5:
        return "值得比较", "Worth comparing"
    if score <= 4.5:
        return "较易落地", "Strong candidate"
    return "综合条件突出", "Excellent fit"


def _score_record(
    components: dict[str, int | None],
    basis: dict[str, str | dict | None],
    *,
    sources: dict[str, list[str]] | None = None,
    provisional: bool = False,
    batch_id: str | None = None,
    checked_at: str | None = None,
) -> dict:
    assert set(components) == set(COMPONENTS)
    assert set(basis) == set(COMPONENTS)
    assert all(value is None or (isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 5) for value in components.values())
    sources = sources or {key: [] for key in COMPONENTS}
    assert set(sources) == set(COMPONENTS)
    for key in COMPONENTS:
        if components[key] is None:
            basis[key] = None
            sources[key] = []
        else:
            assert basis[key], f"Scored dimension {key} requires a basis"
            assert sources[key], f"Scored dimension {key} requires at least one source"
            assert all(isinstance(url, str) and url.startswith("https://") for url in sources[key])

    evidenced = [key for key in COMPONENTS if components[key] is not None]
    available_weight = sum(WEIGHTS[key] for key in evidenced)
    effective_weights = {
        key: (round(WEIGHTS[key] * 100 / available_weight, 3) if key in evidenced else None)
        for key in COMPONENTS
    } if available_weight else {key: None for key in COMPONENTS}
    if len(evidenced) >= 3:
        weighted = sum(components[key] * WEIGHTS[key] for key in evidenced) / available_weight
        score = _round_half(weighted)
        zh_label, en_label = _score_label(score)
    else:
        weighted = None
        score = None
        zh_label, en_label = "尚未评分", "Not yet rated"
    score_sources = list(dict.fromkeys(
        url for key in COMPONENTS for url in sources[key]
    ))
    return {
        "score": score,
        "weighted_average": round(weighted, 3) if weighted is not None else None,
        "scale": 5,
        "rounding": "nearest-0.5",
        "minimum_evidenced_dimensions": 3,
        "evidenced_dimensions": len(evidenced),
        "effective_weights": effective_weights,
        "label_zh": zh_label,
        "label_en": en_label,
        "components": components,
        "component_basis": basis,
        "component_sources": sources,
        "score_sources": score_sources,
        "provisional": provisional,
        "batch_id": batch_id,
        "checked_at": checked_at,
        "disclaimer_zh": "复活价值的相对编辑评分，不是兼容保证或安全证明；E0–E3 证据等级另行标注。",
        "disclaimer_en": "A relative editorial revival-value score, not a compatibility guarantee or safety proof; E0–E3 evidence is shown separately.",
    }


def _ledger_entries(scoring_evidence: dict | None) -> dict[str, dict]:
    """Return an entry-id mapping from the canonical scoring-evidence ledger."""
    if not scoring_evidence:
        return {}
    entries = scoring_evidence.get("entries", scoring_evidence)
    if isinstance(entries, list):
        return {item["entry_id"]: item for item in entries}
    assert isinstance(entries, dict), "Scoring evidence entries must be keyed by entry_id"
    return entries


def _record_from_ledger(entry_id: str, scoring_evidence: dict | None, *, provisional: bool) -> dict | None:
    entry = _ledger_entries(scoring_evidence).get(entry_id)
    if entry is None:
        return None
    raw_components = entry.get("components", entry.get("dimensions"))
    assert isinstance(raw_components, dict) and set(raw_components) == set(COMPONENTS), entry_id
    top_basis = entry.get("component_basis", {})
    top_sources = entry.get("component_sources", entry.get("sources", {}))
    if not isinstance(top_basis, dict):
        top_basis = {}
    if not isinstance(top_sources, dict):
        top_sources = {}
    components: dict[str, int | None] = {}
    basis: dict[str, str | dict | None] = {}
    sources: dict[str, list[str]] = {}
    for key in COMPONENTS:
        raw = raw_components[key]
        if isinstance(raw, dict):
            value = raw.get("score")
            component_basis = raw.get("basis")
            if component_basis is None and (raw.get("basis_zh") or raw.get("basis_en")):
                component_basis = {"zh": raw.get("basis_zh"), "en": raw.get("basis_en")}
            component_sources = raw.get("sources", [])
        else:
            value = raw
            component_basis = top_basis.get(key)
            component_sources = top_sources.get(key, [])
        components[key] = value
        basis[key] = component_basis
        sources[key] = list(dict.fromkeys(component_sources or []))
    record = _score_record(
        components,
        basis,
        sources=sources,
        provisional=provisional,
        batch_id=entry.get("batch_id", scoring_evidence.get("batch_id") if scoring_evidence else None),
        checked_at=entry.get("checked_at", scoring_evidence.get("checked_at") if scoring_evidence else None),
    )
    record["reason_zh"] = entry.get("reason_zh") or (
        "仅用有可核验来源的维度计算；未取证维度保留为 null，不用中性分补位。"
    )
    record["reason_en"] = entry.get("reason_en") or (
        "Only dimensions backed by verifiable sources are included; unevidenced dimensions remain null rather than receiving a neutral placeholder."
    )
    return record


def score_project(project: dict, scoring_evidence: dict | None = None) -> dict:
    ledger_record = _record_from_ledger(f"project:{project['id']}", scoring_evidence, provisional=False)
    if ledger_record is not None:
        return ledger_record

    feasibility = {"easy": 5, "medium": 3, "high": 1}[project["difficulty"]]
    # UNKNOWN monetary cost is not evidence and must stay unscored.
    cost = None

    source_urls = {
        url
        for url in [
            project.get("repo_url"),
            project.get("tutorial_url"),
            project.get("compatibility_url"),
            *(source.get("url") for source in project.get("sources", [])),
        ]
        if url
    }
    maintenance = project.get("maintenance", {})
    active = maintenance.get("status") == "not-archived" and _recent(
        maintenance.get("last_push_at"), maintenance.get("checked_at")
    )
    if len(source_urls) >= 2 and active:
        docs_community = 5
        docs_basis = f"reviewed-urls:{len(source_urls)};recent-non-archived"
    elif len(source_urls) >= 2:
        docs_community = 4
        docs_basis = f"reviewed-urls:{len(source_urls)};activity-not-assumed"
    elif source_urls:
        docs_community = 3
        docs_basis = "one-reviewed-url"
    else:
        docs_community = None
        docs_basis = None

    practical_value = 3 if project["entry_type"] == "prerequisite" else 4

    # Existing catalog risk fields do not independently assess security, so the
    # combined bricking/security dimension remains unscored without a ledger
    # record that cites suitable sources.
    risk = None
    components = {
        "feasibility": feasibility,
        "cost": cost,
        "docs_community": docs_community,
        "practical_value": practical_value,
        "risk": risk,
    }
    basis = {
        "feasibility": f"catalog-difficulty:{project['difficulty']}",
        "cost": None,
        "docs_community": docs_basis,
        "practical_value": f"reviewed-entry-type:{project['entry_type']}",
        "risk": None,
    }
    source_list = sorted(source_urls)
    sources = {
        "feasibility": source_list,
        "cost": [],
        "docs_community": source_list,
        "practical_value": source_list,
        "risk": [],
    }
    record = _score_record(components, basis, sources=sources)
    record["reason_zh"] = "使用已读来源支持的难度、文档/社区与实用价值维度；未核价的成本及未完整评估的刷坏/安全风险保留为 null。"
    record["reason_en"] = "Uses source-backed feasibility, docs/community, and practical-value dimensions; unpriced cost and incompletely assessed bricking/security risk remain null."
    return record


def score_lead(lead: dict, decision: dict, *, entry_id: str | None = None, scoring_evidence: dict | None = None) -> dict:
    if entry_id:
        ledger_record = _record_from_ledger(entry_id, scoring_evidence, provisional=False)
        if ledger_record is not None:
            return ledger_record
    access = lead.get("source_access")
    deep_review = bool(lead.get("deep_review"))
    if deep_review:
        docs_community = 4
        docs_basis = "exact-model-source-body-reviewed"
    elif access in BODY_ACCESS:
        docs_community = 3
        docs_basis = f"source-access:{access}"
    else:
        docs_community = None
        docs_basis = None
    source_urls = list(dict.fromkeys([
        lead.get("source_url"),
        lead.get("code_url"),
        *lead.get("additional_sources", []),
    ]))
    source_urls = [url for url in source_urls if url]
    # The device/community ledger does not contain comparable structured cost,
    # ease, value, or security measurements. Those dimensions stay null.
    components = {
        "feasibility": None,
        "cost": None,
        "docs_community": docs_community,
        "practical_value": None,
        "risk": None,
    }
    basis = {
        "feasibility": None,
        "cost": None,
        "docs_community": docs_basis,
        "practical_value": None,
        "risk": None,
    }
    sources = {
        key: (source_urls if key == "docs_community" and docs_community is not None else [])
        for key in COMPONENTS
    }
    record = _score_record(components, basis, sources=sources)
    record["reason_zh"] = "现有核查状态只能支持文档与社区维度；其余维度未取证并保留为 null，因不足 3 个有证据维度而暂不评星。"
    record["reason_en"] = "The current review supports only docs/community. Other dimensions remain null, so fewer than three evidenced dimensions means this route is not yet rated."
    return record


def score_project_lead(lead: dict, scoring_evidence: dict | None = None) -> dict:
    """Represent an E0 repository discovery without implying a deep review."""
    assert lead.get("evidence_level", "E0") == "E0", f"Project-source lead {lead.get('id')} must remain E0"
    ledger_record = _record_from_ledger(f"project-lead:{lead['id']}", scoring_evidence, provisional=True)
    if ledger_record is not None:
        return ledger_record
    if lead.get("archived"):
        docs_community = 1
        docs_basis = "repository-archived"
    elif _recent(lead.get("pushed_at"), lead.get("checked_at")):
        docs_community = 3
        docs_basis = "repository-metadata;push-within-365-days"
    else:
        docs_community = 2
        docs_basis = "repository-metadata;activity-not-assumed"
    components = {
        "feasibility": None,
        "cost": None,
        "docs_community": docs_community,
        "practical_value": None,
        "risk": None,
    }
    basis = {
        "feasibility": None,
        "cost": None,
        "docs_community": docs_basis,
        "practical_value": None,
        "risk": None,
    }
    sources = {key: ([lead["repo_url"]] if key == "docs_community" else []) for key in COMPONENTS}
    record = _score_record(components, basis, sources=sources, provisional=True)
    record["reason_zh"] = "仓库元数据只支持文档/社区维度；其余维度未深审并保留为 null，当前标记为待验证且暂不评星。"
    record["reason_en"] = "Repository metadata supports only docs/community. Other dimensions remain null, so this discovery stays To verify and is not yet rated."
    return record


def score_all(
    projects: list[dict],
    watchlist: dict[str, dict],
    details: dict[str, dict],
    project_leads: list[dict] | None = None,
    scoring_evidence: dict | None = None,
) -> tuple[dict, dict, dict]:
    project_scores = {project["id"]: score_project(project, scoring_evidence) for project in projects}
    lead_scores = {
        slug: score_lead(
            lead,
            details[slug]["zh"],
            entry_id=f"lead:{slug}",
            scoring_evidence=scoring_evidence,
        )
        for slug, lead in watchlist.items()
    }
    project_lead_scores = {
        lead["id"]: score_project_lead(lead, scoring_evidence)
        for lead in (project_leads or [])
    }
    return project_scores, lead_scores, project_lead_scores


def build_directory_export(
    *,
    projects: list[dict],
    project_leads: list[dict],
    watchlist: dict[str, dict],
    details: dict[str, dict],
    base_url: str,
    version: str,
    generated_at: str,
    scoring_evidence: dict | None = None,
) -> dict:
    base = base_url.rstrip("/") + "/"
    project_scores, lead_scores, project_lead_scores = score_all(
        projects, watchlist, details, project_leads, scoring_evidence
    )
    entries = []
    for project in projects:
        pid = project["id"]
        entries.append({
            "entry_id": f"project:{pid}",
            "content_id": pid,
            "kind": "reviewed-project",
            "title_zh": project["name"],
            "title_en": project["name"],
            "category": project["category"],
            "evidence_level": project["evidence"]["level"],
            "needs_review": False,
            "score": project_scores[pid],
            "source_url": project["repo_url"],
            "detail_url_zh": urljoin(base, f"zh/projects/{pid}/"),
            "detail_url_en": urljoin(base, f"en/projects/{pid}/"),
            "reviewed_at": project["editorial_reviewed_at"],
        })
    for slug, lead in watchlist.items():
        entries.append({
            "entry_id": f"lead:{slug}",
            "content_id": lead["content_id"],
            "kind": "device-or-community-route",
            "title_zh": lead["zh"]["title"],
            "title_en": lead["en"]["title"],
            "category": lead["category"],
            "evidence_level": lead.get("evidence_level", "E0"),
            "needs_review": False,
            "score": lead_scores[slug],
            "source_url": lead["source_url"],
            "detail_url_zh": urljoin(base, f"zh/leads/{slug}/"),
            "detail_url_en": urljoin(base, f"en/leads/{slug}/"),
            "reviewed_at": lead["reviewed_at"],
        })
    for lead in project_leads:
        lead_id = lead["id"]
        entries.append({
            "entry_id": f"project-lead:{lead_id}",
            "content_id": lead["content_id"],
            "kind": "project-source-lead",
            "title_zh": lead["name"],
            "title_en": lead["name"],
            "category": lead["category"],
            "evidence_level": lead["evidence_level"],
            "needs_review": lead["needs_review"],
            "score": project_lead_scores[lead_id],
            "source_url": lead["repo_url"],
            "detail_url_zh": urljoin(base, f"zh/project-leads/{lead_id}/"),
            "detail_url_en": urljoin(base, f"en/project-leads/{lead_id}/"),
            "reviewed_at": lead["checked_at"],
        })
    distribution = collections.Counter(
        entry["score"]["score"] for entry in entries if entry["score"]["score"] is not None
    )
    rated = sum(entry["score"]["score"] is not None for entry in entries)
    evidence = collections.Counter(entry["evidence_level"] for entry in entries)
    categories = collections.Counter(entry["category"] for entry in entries)
    return {
        "schema_version": "3.0.0",
        "scoring_version": SCORING_VERSION,
        "version": version,
        "generated_at": generated_at,
        "score_name_zh": "复活价值综合星级",
        "score_name_en": "Revival value stars",
        "score_scope_zh": "五维相对编辑评分，缺少证据的维度为 null；至少 3 个维度有证据才按已取证权重比例重新归一、计算并按 0.5 星取整。E0–E3 独立标注。",
        "score_scope_en": "A relative five-dimension editorial score. Unevidenced dimensions are null. With at least three evidenced dimensions, only their weights are proportionally renormalized before rounding to 0.5 stars. E0–E3 remains independent.",
        "weights": WEIGHTS,
        "counts": {
            "entries": len(entries),
            "independent_project_sources": len(projects) + len(project_leads),
            "reviewed_projects": len(projects),
            "project_source_leads": len(project_leads),
            "device_or_community_routes": len(watchlist),
            "unique_primary_source_urls": len({entry["source_url"] for entry in entries}),
            "score_coverage": rated,
            "rated": rated,
            "not_yet_rated": len(entries) - rated,
            "needs_review": sum(entry["needs_review"] for entry in entries),
            "score_distribution": {_format_score(score): distribution.get(score, 0) for score in HALF_STAR_BUCKETS},
            "evidence_distribution": dict(sorted(evidence.items())),
            "category_distribution": dict(sorted(categories.items())),
        },
        "dimensions": {
            "feasibility": {"weight": WEIGHTS["feasibility"], "zh": "可行性 / 上手难度（越容易分越高）", "en": "Feasibility / ease (easier is higher)"},
            "cost": {"weight": WEIGHTS["cost"], "zh": "成本（越低分越高）", "en": "Cost (lower is higher)"},
            "docs_community": {"weight": WEIGHTS["docs_community"], "zh": "文档与社区活跃度", "en": "Documentation and community activity"},
            "practical_value": {"weight": WEIGHTS["practical_value"], "zh": "实用价值", "en": "Practical value"},
            "risk": {"weight": WEIGHTS["risk"], "zh": "刷坏与安全风险（风险越低分越高）", "en": "Bricking and security risk (lower risk is higher)"},
        },
        "entries": entries,
    }


def directory_csv(export: dict) -> str:
    output = io.StringIO(newline="")
    fields = [
        "entry_id", "content_id", "kind", "title_zh", "title_en", "category",
        "evidence_level", "needs_review", "score", "weighted_average",
        "score_label_zh", "score_label_en", "feasibility", "cost",
        "docs_community", "practical_value", "risk", "evidenced_dimensions",
        "effective_weights", "component_basis", "component_sources", "score_sources",
        "scoring_batch_id", "scoring_checked_at",
        "source_url", "detail_url_zh", "detail_url_en", "reviewed_at",
        "score_reason_zh", "score_reason_en",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for entry in export["entries"]:
        score = entry["score"]
        components = score["components"]
        writer.writerow({
            **{key: entry[key] for key in ["entry_id", "content_id", "kind", "title_zh", "title_en", "category", "evidence_level", "needs_review", "source_url", "detail_url_zh", "detail_url_en", "reviewed_at"]},
            "score": "" if score["score"] is None else score["score"],
            "weighted_average": "" if score["weighted_average"] is None else score["weighted_average"],
            "score_label_zh": score["label_zh"],
            "score_label_en": score["label_en"],
            **{key: "" if components[key] is None else components[key] for key in COMPONENTS},
            "evidenced_dimensions": score["evidenced_dimensions"],
            "effective_weights": json.dumps(score["effective_weights"], ensure_ascii=False, separators=(",", ":")),
            "component_basis": json.dumps(score["component_basis"], ensure_ascii=False, separators=(",", ":")),
            "component_sources": json.dumps(score["component_sources"], ensure_ascii=False, separators=(",", ":")),
            "score_sources": json.dumps(score["score_sources"], ensure_ascii=False, separators=(",", ":")),
            "scoring_batch_id": score["batch_id"] or "",
            "scoring_checked_at": score["checked_at"] or "",
            "score_reason_zh": score["reason_zh"],
            "score_reason_en": score["reason_en"],
        })
    return "\ufeff" + output.getvalue()


def project_leads_csv(project_leads: list[dict]) -> str:
    """Create a flat, bilingual export for independent E0 project sources."""
    output = io.StringIO(newline="")
    fields = [
        "content_id", "id", "name", "repo_url", "category", "evidence_level", "needs_review",
        "summary_zh", "summary_en", "device_scope_zh", "device_scope_en",
        "use_case_zh", "use_case_en", "github_description", "archived",
        "pushed_at", "license_spdx", "default_branch", "checked_at",
        "source_access", "readme_access", "reason_zh", "reason_en",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for lead in project_leads:
        writer.writerow({key: lead.get(key) for key in fields})
    return "\ufeff" + output.getvalue()


def export_json_text(export: dict) -> str:
    return json.dumps(export, ensure_ascii=False, indent=2) + "\n"
