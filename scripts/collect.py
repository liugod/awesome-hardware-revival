"""Read-only upstream snapshot collector. Requires authenticated gh; never reads tokens."""
import base64, concurrent.futures, datetime, json, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT.parent / "hardware-revival-work" / "upstream"
CACHE.mkdir(parents=True, exist_ok=True)

def api(path):
    for attempt in range(3):
        p = subprocess.run(["gh", "api", path], capture_output=True, encoding="utf-8")
        if p.returncode == 0 or "HTTP 404" in p.stderr:
            break
        time.sleep(1 + attempt)
    if p.returncode:
        return {"error": p.stderr.strip()[:250]}
    return json.loads(p.stdout)

def collect(repo):
    out = {"requested_repo": repo, "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for key, path in [("repo", f"repos/{repo}"), ("readme", f"repos/{repo}/readme"),
                      ("license", f"repos/{repo}/license"), ("releases", f"repos/{repo}/releases?per_page=1")]:
        out[key] = api(path)
    for key in ("readme", "license"):
        if "content" in out[key]:
            out[key]["text"] = base64.b64decode(out[key].pop("content")).decode("utf-8", errors="replace")
    (CACHE / (repo.replace("/", "__") + ".json")).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"repo": repo, "ok": "full_name" in out["repo"], "readme": len(out["readme"].get("text", "")),
            "license": out["license"].get("license", {}).get("spdx_id"), "archived": out["repo"].get("archived")}

if __name__ == "__main__":
    repos = json.loads((ROOT / "data/seeds.json").read_text(encoding="utf-8"))
    selected = sys.argv[1:] or [r["repo"] for r in repos]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(collect, selected):
            print(json.dumps(result, ensure_ascii=False), flush=True)
