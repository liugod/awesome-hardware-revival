"""Merge the original detailed watchlist with compact researched expansion records."""
import json


def load_watchlist(data_dir):
    base = json.loads((data_dir / "watchlist.json").read_text(encoding="utf-8"))
    details = json.loads((data_dir / "watchlist-details.json").read_text(encoding="utf-8"))
    expansion = json.loads((data_dir / "watchlist-expansion.json").read_text(encoding="utf-8"))
    for item in expansion:
        slug = item["slug"]
        if slug in base:
            raise ValueError(f"Duplicate watchlist slug: {slug}")
        base[slug] = {
            "content_id": item["content_id"],
            "category": item["category"],
            "source_platform": item["source_platform"],
            "source_url": item["source_url"],
            "code_url": None,
            "additional_sources": [],
            "status": item["status"],
            "reviewed_at": item["reviewed_at"],
            "zh": {key: item["zh"][key] for key in ["title", "summary", "gap", "next_check", "safety"]},
            "en": {key: item["en"][key] for key in ["title", "summary", "gap", "next_check", "safety"]},
        }
        details[slug] = {
            "resources": [{
                "url": item["source_url"],
                "kind": item["resource_kind"],
                "zh_label": item["zh"]["resource_label"],
                "en_label": item["en"]["resource_label"],
                "zh_note": item["zh"]["resource_note"],
                "en_note": item["en"]["resource_note"],
            }],
            "zh": {
                "stage": item["zh"]["summary"],
                "usable": item["zh"]["usable"],
                "works_for": item["zh"]["works_for"],
                "not_for": item["zh"]["not_for"],
                "value": item["zh"]["value"],
                "follow": item["zh"]["follow"],
            },
            "en": {
                "stage": item["en"]["summary"],
                "usable": item["en"]["usable"],
                "works_for": item["en"]["works_for"],
                "not_for": item["en"]["not_for"],
                "value": item["en"]["value"],
                "follow": item["en"]["follow"],
            },
        }
    return base, details
