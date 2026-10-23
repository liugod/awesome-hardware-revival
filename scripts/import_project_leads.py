"""Normalize verified GitHub discovery batches into the public E0 source ledger.

Input files are arrays produced by a separate read-only research pass. The
result is deterministic, excludes the reviewed catalog, and selects across
categories in rounds so one high-volume topic cannot consume the whole target.
"""

from __future__ import annotations

import argparse
import collections
from datetime import datetime, timedelta, timezone
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "id", "name", "repo_url", "category", "summary_zh", "summary_en",
    "device_scope_zh", "device_scope_en", "use_case_zh", "use_case_en",
    "github_description", "archived", "pushed_at", "license_spdx",
    "default_branch", "checked_at", "reason_zh", "reason_en",
}


def canonical_repo(url: str, *, github_only: bool = True) -> str:
    parsed = urlsplit(url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if parsed.scheme != "https" or len(parts) != 2 or (github_only and parsed.netloc.lower() != "github.com"):
        raise ValueError(f"Not a canonical GitHub repository URL: {url}")
    return f"https://{parsed.netloc.lower()}/{parts[0]}/{parts[1].removesuffix('.git')}".casefold()


def unique_id(raw: str, repo_url: str, used: set[str]) -> str:
    candidate = re.sub(r"[^a-z0-9]+", "-", raw.casefold()).strip("-")
    if candidate not in used:
        used.add(candidate)
        return candidate
    owner = [part for part in urlsplit(repo_url).path.split("/") if part][0]
    candidate = re.sub(r"[^a-z0-9]+", "-", f"{owner}-{raw}".casefold()).strip("-")
    if candidate in used:
        raise ValueError(f"Unresolvable project-lead ID collision: {repo_url}")
    used.add(candidate)
    return candidate


def select_round_robin(items: list[dict], target: int) -> list[dict]:
    groups: dict[str, list[dict]] = collections.defaultdict(list)
    for item in items:
        groups[item["category"]].append(item)
    for values in groups.values():
        values.sort(key=lambda item: (item["name"].casefold(), item["repo_url"].casefold()))
    selected = []
    categories = sorted(groups)
    while len(selected) < target:
        progressed = False
        for category in categories:
            if groups[category] and len(selected) < target:
                selected.append(groups[category].pop(0))
                progressed = True
        if not progressed:
            break
    if len(selected) != target:
        raise ValueError(f"Only {len(selected)} unique candidates available for target {target}")
    return sorted(selected, key=lambda item: (item["category"], item["name"].casefold()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--target", type=int, default=147)
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "project-leads.json")
    args = parser.parse_args()

    config = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
    catalog = json.loads((ROOT / "data" / "catalog.json").read_text(encoding="utf-8"))
    allowed_categories = set(catalog["labels"]["category"])
    reviewed_urls = {canonical_repo(project["repo_url"], github_only=False) for project in catalog["projects"]}
    pool = []
    seen_urls = set()
    for input_path in args.inputs:
        batch = json.loads(input_path.read_text(encoding="utf-8-sig"))
        if not isinstance(batch, list):
            raise ValueError(f"Expected an array: {input_path}")
        for item in batch:
            missing = REQUIRED - set(item)
            if missing or any(item[key] in (None, "") for key in REQUIRED - {"license_spdx", "github_description"}):
                raise ValueError(f"Incomplete candidate {item.get('id')}: {sorted(missing)}")
            if item["category"] not in allowed_categories:
                raise ValueError(f"Unknown category: {item['category']}")
            repo = canonical_repo(item["repo_url"])
            if repo in reviewed_urls or repo in seen_urls:
                continue
            seen_urls.add(repo)
            pool.append(dict(item))

    selected = select_round_robin(pool, args.target)
    used_ids: set[str] = set()
    for item in selected:
        item["id"] = unique_id(item["id"], item["repo_url"], used_ids)
        item["content_id"] = f"PS-{item['id']}"
        item["repo_url"] = item["repo_url"].rstrip("/")
        item["evidence_level"] = "E0"
        item["source_access"] = "repository-metadata-reviewed"
        item["readme_access"] = "opening-section-read"
        item["fork"] = False
        item["needs_review"] = True

    generated_at = max(item["checked_at"] for item in selected)
    payload = {
        "schema_version": "1.1.0",
        "version": config["version"],
        "generated_at": generated_at,
        "published_at": datetime.fromisoformat(generated_at.replace("Z", "+00:00")).astimezone(timezone(timedelta(hours=8))).date().isoformat(),
        "selection_method": "Verified non-fork GitHub repositories, deduplicated against the reviewed catalog and selected in category rounds.",
        "evidence_boundary_zh": "这些是独立仓库级 E0 发现来源，不是已完成兼容性、安装或实机核验的正式项目条目。",
        "evidence_boundary_en": "These are repository-level E0 discovery sources, not reviewed compatibility, installation, or hands-on project entries.",
        "counts": {
            "total": len(selected),
            "needs_review": len(selected),
            "evidence": {"E0": len(selected), "E1": 0, "E2": 0, "E3": 0},
            "categories": dict(sorted(collections.Counter(item["category"] for item in selected).items())),
        },
        "projects": selected,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(payload["counts"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
