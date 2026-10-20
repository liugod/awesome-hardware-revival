"""Merge editorial review with read-only snapshots; no upstream code is executed."""
import csv, datetime, hashlib, json, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT.parent/"hardware-revival-work"/"upstream"
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def save(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
seeds=load(ROOT/"data/seeds.json")
review=load(ROOT/"data/review.json")
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
labels={
 "category":{"speaker":"音箱与语音","mobile":"手机与平板","computer":"电脑与瘦客户机","network":"路由与 NAS","tv":"电视与盒子","ereader":"电子书与墨水屏","robot":"机器人","smarthome":"智能家居","camera":"摄像头","audio":"播放器与音响","wearable":"手表与可穿戴","gaming":"游戏设备","peripheral":"打印机与外设"},
 "ai":{"native":"AI 功能改造","assisted":"AI 辅助开发/配置","adjacent":"AI 周边用途","infrastructure":"传统复活基础设施"},
 "difficulty":{"easy":"入门","medium":"进阶","high":"高难度"},
 "evidence":{"E0":"候选 / 证据不足","E1":"源码与部署文档","E2":"作者实机陈述 / 演示","E3":"独立复现已核验"},
 "maintenance":{"not-archived":"仓库未归档","archived":"已归档","deprecated":"作者宣布停维护","moved":"已迁移 / 旧镜像归档","historical-patched":"历史方法 / 漏洞已修复","stale":"超过一年无 push（不等于弃用）"}
}
license_overrides={
 "termux":"GPL-3.0-only（含文件例外）","oclp":"BSD 4-clause style / 自定义署名条款",
 "openmediavault":"GPL-3（除另有声明文件）","openwrt":"GPL-2.0-only（含其他组件许可证）",
 "esphome":"MIT + GPL-3.0（按代码类型）","squeezelite":"GPL-3.0-or-later + OpenSSL 例外 / 其他组件",
 "lyrion":"混合：Perl GPL-2.0；固件/资产另有条款",
 "libreelec":"GPL-2.0（README 声明；上游组件分别授权）",
 "coreelec":"GPL-2.0（README 声明；上游组件分别授权）",
 "printer-spl3":"MIT glue + GPL-2.0 SpliX / patches",
 "gadgetbridge":"AGPL-3.0（含 GPL-3.0 / MIT 文件例外）"
}
cases={"xiaogpt","open-xiaoai","onju-voice","onju-v2","kindle-whoop","kindle-ha","oclp","openwrt","haos","valetudo","wirepod","printer-spl3"}
excluded={"postmarketos","libreboot","openwrt-nas","rebble"}
seeds=[s for s in seeds if s["id"] not in excluded]
save(ROOT/"data/seeds.json",seeds)
projects=[]
for s in seeds:
    r=review[s["id"]]; snap=load(CACHE/(s["repo"].replace("/","__")+".json"))
    meta=snap["repo"]; readme=snap["readme"]; lic=snap["license"]
    assert meta.get("full_name"), s["id"]
    assert readme.get("text") or s["id"]=="lineageos",s["id"]
    repo=meta["html_url"]
    source=readme.get("html_url") or r["support_source"]
    maintenance="archived" if meta["archived"] else "not-archived"
    if s["id"]=="onju-voice": maintenance="deprecated"
    pushed=meta.get("pushed_at")
    if maintenance=="not-archived" and pushed and (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(pushed.replace("Z","+00:00"))).days>365: maintenance="stale"
    maintenance=r.get("maintenance_override",maintenance)
    license_name=license_overrides.get(s["id"]) or lic.get("license",{}).get("spdx_id")
    if license_name in (None,"NOASSERTION"): license_name="UNKNOWN"
    level=r.get("evidence_level","E1")
    if s["id"]=="onju-voice": level="E2"
    xlinks=r.get("x",[])
    if s["id"]=="printer-spl3": xlinks=["https://x.com/kuberwastaken/status/2089377982536388964","https://x.com/kuberwastaken/status/2089721130127094071"]
    reason=r["evidence_reason"]
    if s["id"]=="onju-voice": reason+=" 已浏览作者 X 原帖正文、换板解释和视频组件；未逐帧核验视频。"
    if s["id"]=="printer-spl3": reason+=" 已浏览作者 X 主帖及回复，确认作者称使用 Claude 并多轮试错。"
    if s["id"]=="open-xiaoai":
        r["recovery"]="官方 flash.md 说明使用双系统分区，可切回 boot1；该路径取决于原分区完好，本次未实机验证。"
        r["recovery_url"]=r["tutorial"]
        r["disassembly"]="LX06: yes; OH2P: no（按官方教程）"
        r["soldering"]="no-in-documented-USB-route"
    if s["id"]=="lineageos": reason+=" FP2 的 maintainers 列表为空，仅作为历史机型条目，不能推荐为当前维护版本。"
    p={
      "id":s["id"],"name":s["name"],"category":s["category"],"ai_relation":s["ai"],
      "entry_type":r.get("entry_type","case" if s["id"] in cases else "platform"),
      "family":r.get("family",s["id"]), "summary_zh":s["summary"],
      "device_scope":s["devices"],"model_examples":r.get("models",[]),
      "firmware_requirement":r.get("firmware"),"region_requirement":None,
      "compatibility_status":r.get("compatibility_status","follow-upstream-matrix"),
      "use_cases":[s["use"]],"method":r.get("method"),"difficulty":s["difficulty"],
      "difficulty_basis":"编辑按安装、固件、拆装与排障步骤评估，不是作者给出的难度评分。",
      "limitations":[s["limit"]],"repo_url":r.get("canonical_repo",repo),
      "github_snapshot_url":repo,"website_url":r.get("website") or meta.get("homepage") or None,
      "tutorial_url":r.get("tutorial",source),"compatibility_url":r.get("compatibility",r.get("support_source",source)),
      "x_sources":[{"url":u,"status":"original-text-read","video_viewed":False,"checked_at":now,
                    "note":"作者正文通过浏览器读取；未把浏览量或点赞作为成功证据。"} for u in xlinks],
      "evidence":{"level":level,"reason":reason,"hardware_tested_by_catalog":False,
                  "independent_reproduction_verified":False},
      "sources":[{"url":source,"kind":"upstream-document","status":"content-reviewed","checked_at":snap["observed_at"],
                  "readme_blob_sha":readme.get("sha"),"content_sha256":hashlib.sha256(readme.get("text","").encode()).hexdigest() if readme.get("text") else None}],
      "maintenance":{"status":maintenance,"github_archived":meta["archived"],"last_push_at":pushed,"checked_at":snap["observed_at"],
                     "note":"未归档/近期 push 不能证明当前型号无故障，镜像迁移也不等于项目停止维护。"},
      "license":{"label":license_name,"url":lic.get("html_url") or (source if s["id"] in license_overrides else None),
                 "checked_at":snap["observed_at"],"scope":"此仓库根许可证或 README 声明；不代表捆绑固件、模型、品牌或第三方组件同许可。"},
      "requirements":{"disassembly":r.get("disassembly","UNKNOWN"),"soldering":r.get("soldering","UNKNOWN"),"cloud_api":r.get("cloud","UNKNOWN")},
      "cost":{"amount":None,"currency":None,"status":"UNKNOWN","items":r.get("cost_items",["现有设备、电源/存储/连接配件是否足够需逐机检查"]),"note":"未核价；开源许可证不代表硬件、托管、电力和云服务总成本为零。"},
      "risk":{"data_loss":r.get("data_loss","possible"),"bricking":"possible" if s["difficulty"]=="high" and r.get("method") not in ("服务桥接","安装服务","云服务替代") else "workflow-dependent",
              "recovery":r.get("recovery","待具体型号核实恢复流程；本目录未验证救砖，操作前先备份。"),
              "recovery_url":r.get("recovery_url")},
      "keywords":r.get("keywords",[]) + [s["name"],s["category"],s["use"]],
      "checked_at":snap["observed_at"],"editorial_reviewed_at":now
    }
    if r.get("ai_source"):p["sources"].append({"url":r["ai_source"],"kind":"author-process","status":"content-reviewed","checked_at":now})
    if s["id"]=="kindle-whoop":p["sources"].append({"url":r["tutorial"],"kind":"ai-setup-doc","status":"content-reviewed","checked_at":now})
    if s["id"] in {"oclp","haos","valetudo","mrchromebox"}:
        p["sources"].append({"url":r.get("compatibility",r.get("tutorial")),"kind":"official-compatibility-or-install","status":"content-reviewed","checked_at":now})
    release=snap["releases"]
    p["latest_release"]={"tag":release[0]["tag_name"],"url":release[0]["html_url"],"published_at":release[0]["published_at"]} if isinstance(release,list) and release else None
    projects.append(p)
out={"schema_version":"1.0.0","version":json.loads((ROOT/"site.config.json").read_text(encoding="utf-8"))["version"],"compiled_at":now,"timezone":"Asia/Shanghai","labels":labels,"projects":projects}
save(ROOT/"data/catalog.json",out)
with (ROOT/"data/catalog.csv").open("w",encoding="utf-8-sig",newline="") as f:
    fields=["id","name","category","ai_relation","entry_type","device_scope","model_examples","firmware_requirement","region_requirement","use_cases","method","difficulty","evidence_level","evidence_reason","maintenance","license","repo_url","tutorial_url","compatibility_url","x_sources","cost","requirements","risk","checked_at"]
    w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader()
    for p in projects:
        row={k:p.get(k) for k in fields}
        row.update(evidence_level=p["evidence"]["level"],evidence_reason=p["evidence"]["reason"])
        for k,v in row.items():
            if isinstance(v,(dict,list)):row[k]=json.dumps(v,ensure_ascii=False)
        w.writerow(row)
print(f"Curated {len(projects)} projects; no third-party source text redistributed.")
