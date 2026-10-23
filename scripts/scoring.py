"""Evidence-capped, deterministic scoring for every public KitAgain route.

The score measures review maturity, not popularity, project quality, safety, or
the probability that a user's hardware will work.  Evidence is a hard ceiling:
an E0 lead cannot outrank an E1 source review, and a five is reserved for E3.
"""

from __future__ import annotations

import collections
import csv
import io
import json
from urllib.parse import urljoin


SCORING_VERSION = "1.0.0"
EVIDENCE_SCORE = {"E0": 1, "E1": 3, "E2": 4, "E3": 5}
EVIDENCE_CAP = {"E0": 2, "E1": 3, "E2": 4, "E3": 5}
LOW_ACCESS = {
    "repository-metadata-reviewed",
    "index-confirmed-not-body-reviewed",
    "category-index-reviewed",
}
BODY_ACCESS = {
    "source-page-reviewed",
    "source-body-reviewed",
    "post-text-and-project-read",
}


def _rounded(value: float) -> int:
    """Round positive scores without Python's banker-rounding surprise."""
    return int(value + 0.5)


def _score_record(evidence: str, components: dict[str, int], *, force: int | None = None) -> dict:
    weighted = (
        components["evidence"] * 0.50
        + components["source_specificity"] * 0.20
        + components["recovery_clarity"] * 0.20
        + components["maintenance_visibility"] * 0.10
    )
    score = force if force is not None else _rounded(weighted)
    score = max(1, min(score, EVIDENCE_CAP[evidence]))
    labels = {
        1: ("线索入口", "Discovery lead"),
        2: ("可继续核查", "Ready for deeper review"),
        3: ("资料已读", "Source reviewed"),
        4: ("作者实机证据", "Author hardware evidence"),
        5: ("独立复现已核验", "Independent reproduction verified"),
    }
    zh_label, en_label = labels[score]
    return {
        "score": score,
        "scale": 5,
        "label_zh": zh_label,
        "label_en": en_label,
        "evidence_cap": EVIDENCE_CAP[evidence],
        "components": components,
        "disclaimer_zh": "核查成熟度，不是项目质量、成功率、安全性或用户口碑评分。",
        "disclaimer_en": "Review maturity, not project quality, success probability, safety, or a user rating.",
    }


def score_project(project: dict) -> dict:
    evidence = project["evidence"]["level"]
    model_specific = bool(project.get("model_examples"))
    recovery = project.get("risk", {}).get("recovery") or ""
    recovery_url = project.get("risk", {}).get("recovery_url")
    maintenance = project.get("maintenance", {})
    components = {
        "evidence": EVIDENCE_SCORE[evidence],
        "source_specificity": 5 if model_specific else 4,
        "recovery_clarity": 5 if recovery_url else (4 if recovery else 1),
        # Visibility measures whether the state was recorded with a check date,
        # not whether the project happens to be active. Archived is not worse
        # evidence when its archival state is explicit and dated.
        "maintenance_visibility": 5 if maintenance.get("status") and maintenance.get("checked_at") else 1,
    }
    record = _score_record(evidence, components)
    record["reason_zh"] = (
        f"{evidence} 设定 {record['evidence_cap']} 分证据上限；项目资料含"
        f"{'具体型号示例' if model_specific else '设备范围'}、恢复说明和带日期的维护状态。"
    )
    record["reason_en"] = (
        f"{evidence} sets an evidence ceiling of {record['evidence_cap']}; the record includes "
        f"{'model examples' if model_specific else 'a device scope'}, recovery guidance, and dated maintenance metadata."
    )
    return record


def score_lead(lead: dict, decision: dict) -> dict:
    evidence = lead.get("evidence_level", "E0")
    access = lead.get("source_access")
    exact_model = bool(lead.get("device_model"))
    deep_review = bool(lead.get("deep_review"))
    if deep_review:
        specificity = 5
        recovery = 4
        visibility = 4
    elif exact_model and access in BODY_ACCESS:
        specificity = 4
        recovery = 3
        visibility = 3
    elif exact_model:
        specificity = 3
        recovery = 2
        visibility = 2
    else:
        specificity = 2
        recovery = 3 if decision.get("follow") else 2
        visibility = 3 if access in BODY_ACCESS or access is None else 2
    components = {
        "evidence": EVIDENCE_SCORE[evidence],
        "source_specificity": specificity,
        "recovery_clarity": recovery,
        "maintenance_visibility": visibility,
    }
    force = None
    if evidence == "E0":
        # Metadata/index-only discovery remains level 1 even when the model name
        # itself is exact. A page/body review or curated case sheet can reach 2.
        force = 1 if access in LOW_ACCESS else 2
    record = _score_record(evidence, components, force=force)
    access_note_zh = "只核到索引或仓库元数据" if access in LOW_ACCESS else "已有来源页或判断表"
    access_note_en = "only an index or repository metadata was checked" if access in LOW_ACCESS else "a source page or decision sheet is available"
    record["reason_zh"] = (
        f"{evidence} 设定 {record['evidence_cap']} 分证据上限；{access_note_zh}。"
        "该分数不把设备页存在视为刷机成功。"
    )
    record["reason_en"] = (
        f"{evidence} sets an evidence ceiling of {record['evidence_cap']}; {access_note_en}. "
        "The score does not treat the existence of a device page as a successful build."
    )
    return record


def score_project_lead(lead: dict) -> dict:
    """Score an E0 repository discovery record without implying compatibility."""
    evidence = lead.get("evidence_level", "E0")
    assert evidence == "E0", f"Project-source lead {lead.get('id')} must remain E0"
    components = {
        "evidence": EVIDENCE_SCORE[evidence],
        "source_specificity": 3 if lead.get("device_scope_zh") and lead.get("device_scope_en") else 2,
        "recovery_clarity": 1,
        "maintenance_visibility": 4 if lead.get("checked_at") and lead.get("pushed_at") else 1,
    }
    record = _score_record(evidence, components, force=1)
    record["reason_zh"] = (
        "E0 设定 2 分证据上限；目前只核对了 GitHub 仓库元数据与 README 入口，"
        "尚未逐项阅读安装、准确型号兼容与恢复资料，因此保持 1 分。"
    )
    record["reason_en"] = (
        "E0 sets an evidence ceiling of 2. Only GitHub repository metadata and the README entry point "
        "were checked; installation, exact-device compatibility, and recovery material were not "
        "reviewed item by item, so the score remains 1."
    )
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
        "schema_version": "1.0.0",
        "scoring_version": SCORING_VERSION,
        "version": version,
        "generated_at": generated_at,
        "score_name_zh": "核查成熟度",
        "score_name_en": "Review maturity",
        "score_scope_zh": "1–5 分只衡量 KitAgain 对来源、型号边界、恢复与维护信息的核查成熟度；不衡量热度、项目质量、安全性或成功率。",
        "score_scope_en": "The 1–5 score measures only KitAgain review maturity for sources, model boundaries, recovery, and maintenance visibility; it is not popularity, project quality, safety, or success probability.",
        "counts": {
            "entries": len(entries),
            "independent_project_sources": len(projects) + len(project_leads),
            "reviewed_projects": len(projects),
            "project_source_leads": len(project_leads),
            "device_or_community_routes": len(watchlist),
            "unique_primary_source_urls": len({entry["source_url"] for entry in entries}),
            "score_coverage": len(entries),
            "score_distribution": {str(score): distribution.get(score, 0) for score in range(1, 6)},
            "evidence_distribution": dict(sorted(evidence.items())),
            "category_distribution": dict(sorted(categories.items())),
        },
        "rubric": {
            "1": {"zh": "仅核到公开索引或仓库元数据，仍是 E0 发现线索。", "en": "Only a public index or repository metadata was checked; still an E0 discovery lead."},
            "2": {"zh": "来源页或判断表已读，但兼容与部署证据仍不足，保持 E0。", "en": "A source page or decision sheet was read, but compatibility/deployment evidence remains insufficient; still E0."},
            "3": {"zh": "已读部署、配置或准确型号资料，属于 E1；不代表实机成功。", "en": "Deployment, configuration, or exact-model material was read (E1); this is not a hands-on success."},
            "4": {"zh": "在 E1 基础上另有作者具体实机陈述或演示说明，属于 E2。", "en": "E1 plus a specific author hardware claim or demonstration description (E2)."},
            "5": {"zh": "独立使用者的可追溯复现已核验，属于 E3；当前为 0 条。", "en": "A traceable independent reproduction was verified (E3); currently zero entries."},
        },
        "entries": entries,
    }


def directory_csv(export: dict) -> str:
    output = io.StringIO(newline="")
    fields = [
        "entry_id", "content_id", "kind", "title_zh", "title_en", "category",
        "evidence_level", "score", "score_label_zh", "score_label_en",
        "evidence_component", "source_specificity_component",
        "recovery_clarity_component", "maintenance_visibility_component",
        "source_url", "detail_url_zh", "detail_url_en", "reviewed_at",
        "score_reason_zh", "score_reason_en",
    ]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for entry in export["entries"]:
        score = entry["score"]
        components = score["components"]
        writer.writerow({
            **{key: entry[key] for key in ["entry_id", "content_id", "kind", "title_zh", "title_en", "category", "evidence_level", "source_url", "detail_url_zh", "detail_url_en", "reviewed_at"]},
            "score": score["score"],
            "score_label_zh": score["label_zh"],
            "score_label_en": score["label_en"],
            "evidence_component": components["evidence"],
            "source_specificity_component": components["source_specificity"],
            "recovery_clarity_component": components["recovery_clarity"],
            "maintenance_visibility_component": components["maintenance_visibility"],
            "score_reason_zh": score["reason_zh"],
            "score_reason_en": score["reason_en"],
        })
    return "\ufeff" + output.getvalue()


def project_leads_csv(project_leads: list[dict]) -> str:
    """Create a flat, bilingual export for independent E0 project sources."""
    output = io.StringIO(newline="")
    fields = [
        "content_id", "id", "name", "repo_url", "category", "evidence_level",
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
