"""Discover image candidates in upstream GitHub README files without downloading them.

By default this covers the reviewed catalog. ``--include-project-leads`` adds the
listed GitHub discovery records so TRA-19 can measure image availability across
the complete directory without silently promoting their evidence level.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BADGE_MARKERS = (
    "shields.io", "badge", "actions/workflows", "codecov", "coveralls",
    "travis-ci", "github.com/sponsors", "opencollective", "paypal",
    "ko-fi", "kofi", "buymeacoffee", "support_me_on",
)


def gh_json(path: str) -> dict:
    result = subprocess.run(
        ["gh", "api", path], check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return json.loads(result.stdout)


def candidates(repo_url: str) -> dict:
    parts = [p for p in urlsplit(repo_url).path.split("/") if p]
    owner, repo = parts[:2]
    repo_info = gh_json(f"repos/{owner}/{repo}")
    readme = gh_json(f"repos/{owner}/{repo}/readme")
    content = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
    refs = re.findall(r"!\[[^\]]*\]\((?:<)?([^)>\s]+)", content)
    refs += re.findall(r"<img[^>]+src=[\"']([^\"']+)", content, flags=re.I)
    refs += re.findall(r"<source[^>]+srcset=[\"']([^\"'\s,]+)", content, flags=re.I)
    base = f"https://raw.githubusercontent.com/{owner}/{repo}/{repo_info['default_branch']}/"
    resolved = []
    for ref in refs:
        ref = ref.replace("&amp;", "&").strip()
        if ref.startswith(("data:", "#")):
            continue
        url = ref if ref.startswith(("http://", "https://")) else urljoin(base, ref.lstrip("./"))
        if any(marker in url.lower() for marker in BADGE_MARKERS):
            continue
        if url not in resolved:
            resolved.append(url)
    if len(resolved) < 2:
        try:
            tree = gh_json(f"repos/{owner}/{repo}/git/trees/{repo_info['default_branch']}?recursive=1")
            ranked = []
            for item in tree.get("tree", []):
                path = item.get("path", "")
                lowered = path.lower()
                if item.get("type") != "blob" or not lowered.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                    continue
                if any(marker in lowered for marker in ("node_modules/", "vendor/", "fixture", "testdata", "favicon", "badge", "/icons/", "icon-", "logo")):
                    continue
                size = int(item.get("size") or 0)
                if size < 5000 or size > 20_000_000:
                    continue
                preferred = sum(marker in lowered for marker in ("screenshot", "screen", "demo", "device", "photo", "hardware", "render", "docs/image", "assets/image", "media/"))
                ranked.append((preferred, min(size, 2_000_000), path))
            for _, _, image_path in sorted(ranked, reverse=True)[:12]:
                url = f"https://raw.githubusercontent.com/{owner}/{repo}/{repo_info['default_branch']}/{quote(image_path)}"
                if url not in resolved:
                    resolved.append(url)
        except subprocess.CalledProcessError:
            pass
    license_info = repo_info.get("license") or {}
    return {
        "repository": f"{owner}/{repo}",
        "default_branch": repo_info["default_branch"],
        "license": license_info.get("spdx_id") or "UNKNOWN",
        "readme_url": readme.get("html_url"),
        "candidates": resolved,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", nargs="*")
    parser.add_argument("--out")
    parser.add_argument("--include-project-leads", action="store_true")
    args = parser.parse_args()
    catalog = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    wanted = set(args.ids)
    jobs = []
    for project in catalog["projects"]:
        if wanted and project["id"] not in wanted:
            continue
        if not project["repo_url"].startswith("https://github.com/"):
            continue
        jobs.append((project["id"], None, project["repo_url"]))
    if args.include_project_leads:
        leads = json.loads((ROOT / "data/project-leads.json").read_text(encoding="utf-8"))["projects"]
        for lead in leads:
            if lead.get("display_status", "listed") != "listed":
                continue
            if wanted and lead["id"] not in wanted:
                continue
            if not lead["repo_url"].startswith("https://github.com/"):
                continue
            jobs.append((lead["id"], "project-source-lead", lead["repo_url"]))

    def discover(job: tuple[str, str | None, str]) -> dict:
        item_id, entry_kind, repo_url = job
        prefix = {"id": item_id}
        if entry_kind:
            prefix["entry_kind"] = entry_kind
        try:
            return {**prefix, **candidates(repo_url)}
        except subprocess.CalledProcessError as exc:
            return {**prefix, "error": exc.stderr.strip()}

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        rows = list(executor.map(discover, jobs))
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        (ROOT / args.out).write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
