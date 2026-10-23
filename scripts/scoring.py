"""Deterministic five-dimension revival-value scoring for KitAgain.

The 1–5 star score is an editorial comparison across feasibility, expected
cost, documentation/community activity, practical value, and operational
risk. Evidence level (E0–E3) is deliberately separate: it never caps or enters
the arithmetic. Repository-discovery rows remain clearly provisional.
"""

from __future__ import annotations

import collections
import csv
from datetime import datetime
import io
import json
import math
from urllib.parse import urljoin


SCORING_VERSION = "2.0.0"
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
    components: dict[str, int],
    basis: dict[str, str],
    *,
    provisional: bool = False,
) -> dict:
    assert set(components) == set(COMPONENTS)
    assert set(basis) == set(COMPONENTS)
    assert all(isinstance(value, int) and 1 <= value <= 5 for value in components.values())
    weighted = sum(components[key] * WEIGHTS[key] for key in COMPONENTS) / 100
    score = _round_half(weighted)
    zh_label, en_label = _score_label(score)
    return {
        "score": score,
        "weighted_average": round(weighted, 3),
        "scale": 5,
        "rounding": "nearest-0.5",
        "label_zh": zh_label,
        "label_en": en_label,
        "components": components,
        "component_basis": basis,
        "provisional": provisional,
        "disclaimer_zh": "复活价值的相对编辑评分，不是兼容保证或安全证明；E0–E3 证据等级另行标注。",
        "disclaimer_en": "A relative editorial revival-value score, not a compatibility guarantee or safety proof; E0–E3 evidence is shown separately.",
    }


def score_project(project: dict) -> dict:
    feasibility = {"easy": 5, "medium": 3, "high": 1}[project["difficulty"]]
    # Every reviewed project currently has UNKNOWN monetary cost. Neutral 3 is
    # explicit imputation; item counts are not treated as price evidence.
    cost = 3

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
        docs_community = 1
        docs_basis = "no-reviewed-url"

    practical_value = 3 if project["entry_type"] == "prerequisite" else 4

    data_loss_score = {"not-expected": 5, "possible": 3, "expected": 1}.get(
        project.get("risk", {}).get("data_loss"), 3
    )
    bricking_score = {"not-expected": 5, "workflow-dependent": 3, "possible": 2, "expected": 1}.get(
        project.get("risk", {}).get("bricking"), 3
    )
    # Security has not been assessed independently, so even a low-bricking
    # software route cannot exceed neutral 3 on the combined risk dimension.
    risk = min(data_loss_score, bricking_score, 3)
    components = {
        "feasibility": feasibility,
        "cost": cost,
        "docs_community": docs_community,
        "practical_value": practical_value,
        "risk": risk,
    }
    basis = {
        "feasibility": f"catalog-difficulty:{project['difficulty']}",
        "cost": "unknown-neutral",
        "docs_community": docs_basis,
        "practical_value": f"reviewed-entry-type:{project['entry_type']}",
        "risk": f"structured-data-loss:{project['risk']['data_loss']};bricking:{project['risk']['bricking']};security-unreviewed",
    }
    record = _score_record(components, basis)
    record["reason_zh"] = "按现有难度、未知成本、已读资料、复活用途与结构化风险字段计算；证据等级不参与加权或封顶。"
    record["reason_en"] = "Calculated from existing difficulty, unknown cost, reviewed documentation, revival use, and structured risk fields; evidence level neither enters nor caps the score."
    return record


def score_lead(lead: dict, decision: dict) -> dict:
    access = lead.get("source_access")
    deep_review = bool(lead.get("deep_review"))
    if deep_review:
        docs_community = 4
        docs_basis = "exact-model-source-body-reviewed"
    elif access in BODY_ACCESS:
        docs_community = 3
        docs_basis = f"source-access:{access}"
    else:
        docs_community = 2
        docs_basis = f"source-access:{access or 'unspecified'}"
    # The device/community ledger does not contain comparable structured cost,
    # ease, value, or security measurements. Use a disclosed neutral value
    # instead of extracting numbers from prose.
    components = {
        "feasibility": 3,
        "cost": 3,
        "docs_community": docs_community,
        "practical_value": 3,
        "risk": 3,
    }
    basis = {
        "feasibility": "unknown-neutral",
        "cost": "unknown-neutral",
        "docs_community": docs_basis,
        "practical_value": "unknown-neutral",
        "risk": "unknown-neutral;security-unreviewed",
    }
    record = _score_record(components, basis)
    record["reason_zh"] = "设备/社区路线仅对资料与社区维度使用现有核查状态；其余不可比较字段以 3 分中性值计入，并不表示已验证为中等。"
    record["reason_en"] = "Only the documentation/community dimension uses the current review state; other non-comparable fields use a neutral 3, which does not mean they were verified as average."
    return record


def score_project_lead(lead: dict) -> dict:
    """Score an E0 repository discovery without implying a deep review."""
    assert lead.get("evidence_level", "E0") == "E0", f"Project-source lead {lead.get('id')} must remain E0"
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
        "feasibility": 3,
        "cost": 3,
        "docs_community": docs_community,
        "practical_value": 3,
        "risk": 3,
    }
    basis = {
        "feasibility": "unreviewed-neutral",
        "cost": "unreviewed-neutral",
        "docs_community": docs_basis,
        "practical_value": "unreviewed-neutral",
        "risk": "unreviewed-neutral;security-unreviewed",
    }
    record = _score_record(components, basis, provisional=True)
    record["reason_zh"] = "仅依据仓库元数据给出暂定比较分；可行性、成本、实用价值、刷坏/安全风险均未深审，以 3 分中性占位并标记待验证。"
    record["reason_en"] = "A provisional comparison based only on repository metadata; feasibility, cost, practical value, and bricking/security risk were not deeply reviewed, use a neutral 3, and remain marked for verification."
    return record


def score_all(
    projects: list[dict],
    watchlist: dict[str, dict],
    details: dict[str, dict],
    project_leads: list[dict] | None = None,
) -> tuple[dict, dict, dict]:
    project_scores = {project["id"]: score_project(project) for project in projects}
    lead_scores = {slug: score_lead(lead, details[slug]["zh"]) for slug, lead in watchlist.items()}
    project_lead_scores = {lead["id"]: score_project_lead(lead) for lead in (project_leads or [])}
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
) -> dict:
    base = base_url.rstrip("/") + "/"
    project_scores, lead_scores, project_lead_scores = score_all(projects, watchlist, details, project_leads)
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
    distribution = collections.Counter(entry["score"]["score"] for entry in entries)
    evidence = collections.Counter(entry["evidence_level"] for entry in entries)
    categories = collections.Counter(entry["category"] for entry in entries)
    return {
        "schema_version": "2.0.0",
        "scoring_version": SCORING_VERSION,
        "version": version,
        "generated_at": generated_at,
        "score_name_zh": "复活价值综合星级",
        "score_name_en": "Revival value stars",
        "score_scope_zh": "五维相对编辑评分，按 0.5 星取整；E0–E3 是独立证据等级，不参与加权或封顶。缺少可比较事实时使用明确标注的 3 分中性值，不代表已核验为中等。",
        "score_scope_en": "A relative five-dimension editorial score rounded to 0.5 stars. E0–E3 is an independent evidence grade and neither enters nor caps the score. A disclosed neutral 3 is used when comparable facts are unavailable; it does not mean verified average performance.",
        "weights": WEIGHTS,
        "counts": {
            "entries": len(entries),
            "independent_project_sources": len(projects) + len(project_leads),
            "reviewed_projects": len(projects),
            "project_source_leads": len(project_leads),
            "device_or_community_routes": len(watchlist),
            "unique_primary_source_urls": len({entry["source_url"] for entry in entries}),
            "score_coverage": len(entries),
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
        "docs_community", "practical_value", "risk", "component_basis",
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
            "score": score["score"],
            "weighted_average": score["weighted_average"],
            "score_label_zh": score["label_zh"],
            "score_label_en": score["label_en"],
            **{key: components[key] for key in COMPONENTS},
            "component_basis": json.dumps(score["component_basis"], ensure_ascii=False, separators=(",", ":")),
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
