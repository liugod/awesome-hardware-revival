"""Build a provenance-first image-candidate audit for every listed directory row.

This script does not change the public image ledger. It reads GitHub README
candidate output plus each route's public source page, then emits ranked URLs
for the acquisition/format-validation step.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Mozilla/5.0 (compatible; KitAgainImageResearch/1.0; +https://kitagain.com/)"
BAD_MARKERS = (
    "badge", "shields.io", "actions/workflows", "codecov", "coveralls",
    "travis", "favicon", "sprite", "emoji", "avatar", "tracking", "pixel",
    "spacer", "icon-", "/icons/", "logo-small", "github.com/sponsors",
    "social-card", ".within.website", "/anubis/",
    "ko-fi", "kofi", "buymeacoffee", "support_me_on",
    "templates.blakadder.com/assets/images/logo", "forum.armbian.com/uploads/monthly_2026_01/logo9",
)
GOOD_MARKERS = (
    "device", "photo", "screenshot", "screen", "demo", "render", "hardware",
    "board", "product", "cover", "header", "hero", "gallery", "media",
)


class Images(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: list[tuple[str, str]] = []
        self.images: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "meta":
            name = (values.get("property") or values.get("name") or "").lower()
            if name in {"og:image", "og:image:url", "twitter:image", "twitter:image:src"}:
                self.meta.append((name, values.get("content", "")))
        elif tag.lower() == "img":
            src = values.get("src") or values.get("data-src") or values.get("data-original")
            if src:
                self.images.append((src, " ".join((values.get("alt", ""), values.get("title", ""))).strip()))
        elif tag.lower() == "source":
            srcset = values.get("srcset", "").split(",", 1)[0].strip().split(" ", 1)[0]
            if srcset:
                self.images.append((srcset, ""))


def allowed(url: str) -> bool:
    lowered = url.lower()
    return (
        url.startswith(("https://", "http://"))
        and not any(marker in lowered for marker in BAD_MARKERS)
        and not lowered.startswith("https://opengraph.githubassets.com/")
        and not lowered.endswith((".ico", ".js", ".css"))
    )


def score(url: str, origin: str, label: str = "") -> int:
    value = f"{url} {label}".lower()
    base = {"og:image": 100, "twitter:image": 95, "readme": 80, "page-img": 35}.get(origin, 20)
    base += 12 * sum(marker in value for marker in GOOD_MARKERS)
    base -= 25 * sum(marker in value for marker in ("logo", "wordmark", "donate", "sponsor"))
    return base


def fetch_page(url: str) -> dict:
    try:
        response = requests.get(url, timeout=(10, 25), headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        if "html" not in response.headers.get("content-type", "").lower():
            return {"status": response.status_code, "final_url": response.url, "candidates": []}
        parser = Images()
        parser.feed(response.text)
        candidates = []
        for name, value in parser.meta:
            resolved = urljoin(response.url, value)
            if allowed(resolved):
                origin = "og:image" if name.startswith("og:") else "twitter:image"
                candidates.append({"url": resolved, "origin": origin, "score": score(resolved, origin)})
        for value, label in parser.images:
            resolved = urljoin(response.url, value)
            if allowed(resolved):
                candidates.append({"url": resolved, "origin": "page-img", "score": score(resolved, "page-img", label), "label": label})
        return {"status": response.status_code, "final_url": response.url, "candidates": candidates}
    except Exception as exc:  # keep every failed row visible in the audit
        return {"error": f"{type(exc).__name__}: {exc}", "candidates": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-candidates", default="research/tra-19-github-image-candidates.json")
    parser.add_argument("--out", default="research/tra-19-directory-image-candidates.json")
    args = parser.parse_args()

    directory = json.loads((ROOT / "data/directory.json").read_text(encoding="utf-8"))
    listed = [entry for entry in directory["entries"] if entry["display_status"] == "listed"]
    github_rows = json.loads((ROOT / args.github_candidates).read_text(encoding="utf-8"))
    github = {}
    for row in github_rows:
        kind = row.get("entry_kind", "reviewed-project")
        github[(kind, row["id"])] = row

    urls = sorted({entry["source_url"] for entry in listed})
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        fetched = dict(zip(urls, executor.map(fetch_page, urls)))

    records = []
    for entry in listed:
        candidates = []
        github_id = entry["entry_id"].split(":", 1)[1]
        github_row = github.get((entry["kind"], github_id))
        if github_row:
            for index, url in enumerate(github_row.get("candidates", [])):
                if allowed(url):
                    candidates.append({"url": url, "origin": "readme", "score": score(url, "readme") - min(index, 20)})
        page = fetched[entry["source_url"]]
        page_candidates = page.get("candidates", [])
        if urlsplit(entry["source_url"]).netloc == "github.com":
            page_candidates = [item for item in page_candidates if item["url"].startswith("https://repository-images.githubusercontent.com/")]
        candidates.extend(page_candidates)
        unique = {}
        for candidate in candidates:
            key = candidate["url"].replace("&amp;", "&")
            candidate["url"] = key
            if key not in unique or candidate["score"] > unique[key]["score"]:
                unique[key] = candidate
        ranked = sorted(unique.values(), key=lambda item: (-item["score"], item["url"]))[:12]
        records.append({
            "entry_id": entry["entry_id"],
            "content_id": entry["content_id"],
            "entry_kind": entry["kind"],
            "title_zh": entry["title_zh"],
            "title_en": entry["title_en"],
            "source_page": entry["source_url"],
            "page_status": page.get("status"),
            "page_final_url": page.get("final_url"),
            "page_error": page.get("error"),
            "candidates": ranked,
        })

    payload = {
        "schema_version": "1.0",
        "purpose": "TRA-19 image candidate audit; candidates are not approved until format, dimensions, duplicate and visual-source checks pass.",
        "listed_entries": len(listed),
        "records": records,
    }
    (ROOT / args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    counts = {
        "listed": len(records),
        "with_candidates": sum(bool(record["candidates"]) for record in records),
        "without_candidates": sum(not record["candidates"] for record in records),
        "page_errors": sum(bool(record["page_error"]) for record in records),
    }
    print(json.dumps(counts, ensure_ascii=False))


if __name__ == "__main__":
    main()
