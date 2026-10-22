"""Discover image candidates in upstream GitHub README files without downloading them."""
from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BADGE_MARKERS = (
    "shields.io", "badge", "actions/workflows", "codecov", "coveralls",
    "travis-ci", "github.com/sponsors", "opencollective", "paypal",
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
    args = parser.parse_args()
    catalog = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    wanted = set(args.ids)
    rows = []
    for project in catalog["projects"]:
        if wanted and project["id"] not in wanted:
            continue
        if not project["repo_url"].startswith("https://github.com/"):
            continue
        try:
            rows.append({"id": project["id"], **candidates(project["repo_url"])})
        except subprocess.CalledProcessError as exc:
            rows.append({"id": project["id"], "error": exc.stderr.strip()})
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        (ROOT / args.out).write_text(payload, encoding="utf-8", newline="\n")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
