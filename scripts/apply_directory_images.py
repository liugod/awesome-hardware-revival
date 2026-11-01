"""Merge validated TRA-19 acquisitions into the canonical public image ledger."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/project-images.json"
ACQUISITION = ROOT / "research/tra-19-directory-image-acquisition.json"
MISSING = ROOT / "research/tra-19-directory-image-missing.json"


def main() -> None:
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    audit = json.loads(ACQUISITION.read_text(encoding="utf-8"))
    acquired = {entry["entry_id"]: entry for entry in audit["ledger_entries"]}
    retained = []
    blocked_source_markers = (
        "ko-fi", "kofi", "buymeacoffee", "support_me_on",
        "templates.blakadder.com/assets/images/logo",
        "forum.armbian.com/uploads/monthly_2026_01/logo9",
    )
    for entry in ledger["entries"]:
        normalized = dict(entry)
        if "entry_id" not in normalized:
            normalized["entry_id"] = f"project:{entry['project_id']}"
        if "content_id" not in normalized:
            normalized["content_id"] = entry["project_id"]
        normalized.setdefault("entry_kind", "reviewed-project")
        replacement = acquired.pop(normalized["entry_id"], None)
        if replacement:
            retained.append(replacement)
        elif not any(marker in (normalized.get("source_url") or "").lower() for marker in blocked_source_markers):
            retained.append(normalized)
    retained.extend(acquired.values())
    retained.sort(key=lambda entry: (entry["entry_kind"], entry["entry_id"]))
    for entry in retained:
        source = ROOT / entry["source_file"]
        if not source.is_file():
            raise FileNotFoundError(source)
        entry.setdefault("normalized_sha256", hashlib.sha256(source.read_bytes()).hexdigest())
    source_backed = sum(entry["source_kind"] != "kitagain-project-illustration" for entry in retained)
    ledger["coverage"] = {
        "listed_directory_entries": audit["counts"]["listed"],
        "source_backed_images": source_backed,
        "kitagain_illustrations": sum(entry["source_kind"] == "kitagain-project-illustration" for entry in retained),
        "pending_review_placeholders": audit["counts"]["listed"] - len(retained),
    }
    ledger["entries"] = retained
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    final_ids = {entry["entry_id"] for entry in retained}
    missing = []
    for record in audit["records"]:
        if record["entry_id"] in final_ids:
            continue
        status = record["status"]
        if status == "no-candidate":
            reason = "source-page-unavailable-and-no-candidate" if record.get("page_error") else "no-representative-candidate"
        elif status == "all-candidates-rejected":
            reason = "all-candidates-failed-download-or-image-validation"
        elif status == "duplicate-image-rejected":
            reason = "candidate-duplicates-another-accepted-image"
        else:
            raise ValueError(f"Unexpected missing-image status for {record['entry_id']}: {status}")
        item = {
            "entry_id": record["entry_id"],
            "content_id": record["content_id"],
            "entry_kind": record["entry_kind"],
            "title_zh": record["title_zh"],
            "title_en": record["title_en"],
            "source_page": record["source_page"],
            "reason": reason,
            "pipeline_status": status,
            "candidate_count": len(record.get("candidates", [])),
        }
        if record.get("page_error"):
            item["page_error"] = record["page_error"]
        if record.get("attempts"):
            item["rejection_reasons"] = [attempt["error"] for attempt in record["attempts"]]
        if record.get("duplicate_of"):
            item["duplicate_of"] = record["duplicate_of"]
        missing.append(item)
    missing.sort(key=lambda entry: (entry["entry_kind"], entry["entry_id"]))
    reason_counts = {}
    for item in missing:
        reason_counts[item["reason"]] = reason_counts.get(item["reason"], 0) + 1
    assert len(missing) == ledger["coverage"]["pending_review_placeholders"]
    MISSING.write_text(json.dumps({
        "schema_version": "1.0",
        "purpose": "Current TRA-19 placeholder list derived from the final image ledger after acquisition and visual review.",
        "counts": {"missing": len(missing), "by_reason": reason_counts},
        "entries": missing,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"entries": len(retained), **ledger["coverage"], "missing_report": str(MISSING.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
