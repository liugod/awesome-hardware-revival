"use strict";
(() => {
  const english = document.documentElement.lang === "en";
  const t = (zh, en) => english ? en : zh;
  const switchLinks = [...document.querySelectorAll(".language-switch")];
  function syncLanguageLinks() {
    switchLinks.forEach(link => {
      const url = new URL(link.getAttribute("href"), location.href);
      url.search = location.search;
      url.hash = location.hash;
      link.href = url.href;
    });
  }
  function scrollToCurrentHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    const target = document.getElementById(id);
    if (target) requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
  }
  syncLanguageLinks();
  window.addEventListener("hashchange", () => { syncLanguageLinks(); scrollToCurrentHash(); });
  const project = new URLSearchParams(location.search).get("project");
  const context = document.querySelector("#project-context");
  if (context && project && /^[a-zA-Z0-9-]{1,80}$/.test(project)) {
    context.textContent = t("关联项目 ID：", "Related project ID: ") + project;
    context.hidden = false;
    const contribute = document.querySelector("#contribute-link");
    if (contribute) contribute.href += "?project=" + encodeURIComponent(project);
  }
  const leadForm = document.querySelector("#lead-filters");
  if (leadForm) {
    const leadQuery = document.querySelector("#lead-q");
    const leadSource = document.querySelector("#lead-source");
    const leadEvidence = document.querySelector("#lead-evidence");
    const leadCards = [...document.querySelectorAll("#lead-grid .project")];
    const leadCount = document.querySelector("#lead-result-count");
    const leadEmpty = document.querySelector("#lead-empty");
    const readLeadURL = () => {
      const params = new URLSearchParams(location.search);
      leadQuery.value = params.get("q") || "";
      leadSource.value = params.get("source") || "";
      leadEvidence.value = params.get("evidence") || "";
    };
    const applyLeadFilters = (updateURL = true) => {
      const terms = leadQuery.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      leadCards.forEach(card => {
        const match = terms.every(term => card.dataset.search.toLocaleLowerCase().includes(term)) &&
          (!leadSource.value || card.dataset.source === leadSource.value) &&
          (!leadEvidence.value || card.dataset.evidence === leadEvidence.value);
        card.hidden = !match;
        if (match) visible++;
      });
      leadCount.textContent = t(`显示 ${visible} / ${leadCards.length} 条`, `Showing ${visible} / ${leadCards.length}`);
      leadEmpty.hidden = visible !== 0;
      if (updateURL) {
        const url = new URL(location.href);
        [["q", leadQuery], ["source", leadSource], ["evidence", leadEvidence]].forEach(([key, control]) =>
          control.value ? url.searchParams.set(key, control.value) : url.searchParams.delete(key));
        history.replaceState(null, "", url);
        syncLanguageLinks();
      }
    };
    [leadQuery, leadSource, leadEvidence].forEach(control => {
      control.addEventListener("input", applyLeadFilters);
      control.addEventListener("change", applyLeadFilters);
    });
    leadForm.addEventListener("submit", event => event.preventDefault());
    leadForm.addEventListener("reset", () => { leadQuery.value = ""; leadSource.value = ""; leadEvidence.value = ""; applyLeadFilters(); });
    window.addEventListener("popstate", () => { readLeadURL(); applyLeadFilters(false); });
    readLeadURL();
    applyLeadFilters(false);
    scrollToCurrentHash();
  }
  const form = document.querySelector("#filters");
  if (!form) return;
  const keys = ["q", "category", "use", "ai", "difficulty", "evidence"];
  const controls = Object.fromEntries(keys.map(k => [k, document.getElementById(k)]));
  const cards = [...document.querySelectorAll("#project-grid .project")];
  const count = document.querySelector("#result-count");
  function readURL() {
    const params = new URLSearchParams(location.search);
    keys.forEach(k => { controls[k].value = params.get(k) || ""; });
    // Retain old shared links whose use filter contained Chinese labels.
    const legacyUses = {"语音助手":"voice-assistant","Linux终端":"linux-terminal","信息屏":"information-display","副屏":"second-screen","复古游戏":"retro-gaming","媒体中心":"media-center","存储服务器":"storage-server","家庭服务器":"home-server","对话终端":"conversation","应用扩展":"app-extension","摄像头":"camera","智能家居":"smart-home","游戏系统":"gaming-os","离线控制":"offline-control","系统延寿":"os-life-extension","网络设备":"networking","视频分析":"video-analysis","阅读扩展":"reading","音乐播放":"music","驱动修复":"driver-repair"};
    if (legacyUses[params.get("use")]) controls.use.value = legacyUses[params.get("use")];
  }
  function apply(updateURL = true) {
    const terms = controls.q.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.forEach(card => {
      const text = card.dataset.search.toLocaleLowerCase();
      const match = terms.every(t => text.includes(t)) &&
        keys.slice(1).every(k => !controls[k].value || (k === "use"
          ? card.dataset.use.split("|").includes(controls[k].value)
          : card.dataset[k] === controls[k].value));
      card.hidden = !match;
      if (match) visible++;
    });
    count.textContent = t(`显示 ${visible} / ${cards.length} 个条目`, `Showing ${visible} / ${cards.length} entries`);
    document.querySelector("#empty").hidden = visible !== 0;
    if (updateURL) {
      const url = new URL(location.href);
      keys.forEach(k => controls[k].value ? url.searchParams.set(k, controls[k].value) : url.searchParams.delete(k));
      history.replaceState(null, "", url);
    }
    syncLanguageLinks();
  }
  readURL();
  apply(false);
  scrollToCurrentHash();
  form.addEventListener("input", () => apply());
  form.addEventListener("change", () => apply());
  form.addEventListener("submit", e => e.preventDefault());
  form.addEventListener("reset", () => { keys.forEach(k => { controls[k].value = ""; }); apply(); });
  window.addEventListener("popstate", () => { readURL(); apply(false); });
  document.querySelector("#share").addEventListener("click", async () => {
    const target = document.querySelector("#share-status");
    try {
      await navigator.clipboard.writeText(location.href);
      target.textContent = t("已复制当前筛选链接", "Filtered link copied");
    } catch {
      target.textContent = t("请复制浏览器地址栏中的链接，筛选条件已保存在网址中。", "Copy the URL from your browser address bar; it already includes the current filters.");
    }
  });
})();
