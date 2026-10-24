"""Merge the reviewed v1.20 research ledgers into canonical KitAgain data."""

from __future__ import annotations

import collections
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERSION = "1.20.0"
COMPONENTS = {"feasibility", "cost", "docs_community", "practical_value", "risk"}


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def entries(value: dict) -> list[dict]:
    raw = value.get("entries", [])
    return list(raw.values()) if isinstance(raw, dict) else list(raw)


def source_urls(audit: dict) -> list[str]:
    urls: list[str] = []
    for source in audit.get("evidence_sources", []):
        url = source.get("url") if isinstance(source, dict) else source
        if url:
            urls.append(url)
    urls.extend(audit.get("sources", []))
    urls.extend(audit.get("tutorial_sources", []))
    for key in ("installation", "compatibility", "recovery"):
        urls.extend((audit.get(key) or {}).get("source_urls", []))
    for item in (audit.get("action_guide") or {}).values():
        urls.extend(item.get("source_urls", item.get("sources", [])))
    return list(dict.fromkeys(urls))


def validate_scoring_entry(entry: dict) -> None:
    assert set(entry["components"]) == COMPONENTS, entry["entry_id"]
    for component in entry["components"].values():
        if component is None:
            continue
        assert 1 <= component["score"] <= 5
        assert component["basis_zh"] and component["basis_en"] and component["sources"]
        assert all(url.startswith("https://") for url in component["sources"])


def merge_scoring() -> dict:
    canonical = load("scoring-evidence.json")
    batch2 = load("scoring-evidence-batch2-v120.json")
    current = entries(canonical)
    additions = entries(batch2)
    addition_ids = {entry["entry_id"] for entry in additions}
    baseline = [entry for entry in current if entry["entry_id"] not in addition_ids]
    assert len(additions) == batch2["actual_entries"] == 100
    assert len(baseline) == 49, f"Expected 49 batch-1 entries, found {len(baseline)}"
    assert batch2["qualified_entries"] == sum(
        sum(component is not None for component in entry["components"].values()) >= 3
        for entry in additions
    )
    assert batch2["still_unrated"] == len(additions) - batch2["qualified_entries"]
    for entry in additions:
        validate_scoring_entry(entry)
        entry["batch_id"] = batch2["batch_id"]
    by_id = {entry["entry_id"]: entry for entry in baseline}
    by_id.update({entry["entry_id"]: entry for entry in additions})
    canonical["version"] = VERSION
    canonical["batch_id"] = "batch-1+batch-2"
    canonical["checked_at"] = max(canonical["checked_at"], batch2["checked_at"])
    canonical["generated_at"] = batch2.get("generated_at", canonical["generated_at"])
    canonical["actual_entries"] = len(by_id)
    canonical["scope"] = list(dict.fromkeys([*canonical["scope"], *batch2["scope"]]))
    canonical["counts"] = {
        "batch_1_entries": len(baseline),
        "batch_2_attempted": len(additions),
        "batch_2_qualified": batch2["qualified_entries"],
        "batch_2_still_unrated": batch2["still_unrated"],
        "actual_entries": len(by_id),
    }
    canonical["entries"] = list(by_id.values())
    write(DATA / "scoring-evidence.json", canonical)
    return canonical


def merge_audits() -> dict:
    lead_data = load("project-leads.json")
    audit_data = load("e0-audit-v120.json")
    audits = entries(audit_data)
    assert len(audits) == 30, f"Expected 30 E0 audits, found {len(audits)}"
    leads = {lead["id"]: lead for lead in lead_data["projects"]}
    expected_outcomes = {"upgraded-e1", "upgraded-e2", "stays-e0", "rejected-delisted"}
    assert len({audit["project_id"] for audit in audits}) == 30
    for audit in audits:
        assert audit["outcome"] in expected_outcomes, audit
        lead = leads[audit["project_id"]]
        urls = source_urls(audit)
        assert urls and all(url.startswith("https://") for url in urls), audit["project_id"]
        outcome = audit["outcome"]
        level = audit.get("resulting_evidence_level") or {
            "upgraded-e1": "E1",
            "upgraded-e2": "E2",
            "stays-e0": "E0",
            "rejected-delisted": "E0",
        }[outcome]
        assert level == {"upgraded-e1": "E1", "upgraded-e2": "E2", "stays-e0": "E0", "rejected-delisted": "E0"}[outcome]
        lead.update({
            "evidence_level": level,
            "needs_review": outcome == "stays-e0",
            "display_status": "delisted" if outcome == "rejected-delisted" else "listed",
            "audit_outcome": outcome,
            "audit_checked_at": audit["checked_at"],
            "audit_reason_zh": audit["rationale_zh"],
            "audit_reason_en": audit["rationale_en"],
            "audit_sources": urls,
            "audit_installation": audit.get("installation"),
            "audit_compatibility": audit.get("compatibility"),
            "audit_recovery": audit.get("recovery"),
            "action_guide": audit.get("action_guide"),
        })
    for lead in leads.values():
        lead.setdefault("display_status", "listed")
    evidence_counts = collections.Counter(lead["evidence_level"] for lead in leads.values())
    outcome_counts = collections.Counter(lead.get("audit_outcome", "not-audited") for lead in leads.values())
    lead_data["schema_version"] = "1.2.0"
    lead_data["version"] = VERSION
    lead_data["published_at"] = audit_data["checked_at"]
    lead_data["evidence_boundary_zh"] = "仓库发现层保留全部 147 条记录；30 条已深审并记录升级、保留 E0 或下架判定，未审条目仍是 E0 待验证。"
    lead_data["evidence_boundary_en"] = "All 147 repository discoveries remain in data; 30 have deep-audit upgrade, E0-retention, or delisting decisions, while unaudited entries remain E0 and to verify."
    lead_data["audit"] = {
        "batch_id": audit_data["batch_id"],
        "checked_at": audit_data["checked_at"],
        "audited": len(audits),
        "outcomes": dict(sorted(collections.Counter(audit["outcome"] for audit in audits).items())),
        "source": "data/e0-audit-v120.json",
    }
    lead_data["counts"] = {
        "total": len(leads),
        "listed": sum(lead["display_status"] == "listed" for lead in leads.values()),
        "delisted": sum(lead["display_status"] == "delisted" for lead in leads.values()),
        "needs_review": sum(lead["needs_review"] for lead in leads.values()),
        "evidence": {level: evidence_counts.get(level, 0) for level in ("E0", "E1", "E2", "E3")},
        "audit_outcomes": dict(sorted(outcome_counts.items())),
        "categories": dict(sorted(collections.Counter(lead["category"] for lead in leads.values()).items())),
    }
    write(DATA / "project-leads.json", lead_data)
    return lead_data


def bump_versions() -> None:
    targets = [ROOT / "site.config.json", *DATA.glob("*.json")]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        updated = text.replace('"version": "1.19.0"', f'"version": "{VERSION}"')
        updated = updated.replace('"version":  "1.19.0"', f'"version":  "{VERSION}"')
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")


def main() -> None:
    batch = load("scoring-evidence-batch2-v120.json")
    cost = load("cost-evidence-v120.json")
    audit = load("e0-audit-v120.json")
    cost_version = cost.get("version") or str(cost.get("release", "")).removeprefix("v")
    assert batch["version"] == cost_version == audit["version"] == VERSION
    assert len(entries(cost)) == 95, "Cost ledger must cover the 95 baseline-rated entries"
    merge_scoring()
    merge_audits()
    bump_versions()
    print(json.dumps({
        "version": VERSION,
        "batch2_attempted": len(entries(batch)),
        "batch2_qualified": batch["qualified_entries"],
        "cost_entries": len(entries(cost)),
        "e0_audits": len(entries(audit)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
