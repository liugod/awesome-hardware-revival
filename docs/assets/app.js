"use strict";
(() => {
  const english = document.documentElement.lang === "en";
  const t = (zh, en) => english ? en : zh;
  const cardScore = card => {
    const raw = card.dataset.score;
    if (raw === undefined || raw === "") return null;
    const value = Number(raw);
    return Number.isFinite(value) ? value : null;
  };
  const sortCards = (grid, cards, mode) => {
    if (!grid) return;
    const sorted = [...cards].sort((a, b) => {
      if (mode === "score-desc") {
        const aScore = cardScore(a);
        const bScore = cardScore(b);
        if (aScore === null && bScore !== null) return 1;
        if (aScore !== null && bScore === null) return -1;
        if (aScore !== null && bScore !== null && aScore !== bScore) return bScore - aScore;
        return a.dataset.title.localeCompare(b.dataset.title, document.documentElement.lang);
      }
      if (mode === "title-asc") return a.dataset.title.localeCompare(b.dataset.title, document.documentElement.lang);
      return Number(a.dataset.order) - Number(b.dataset.order);
    });
    sorted.forEach(card => grid.append(card));
  };
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
  const directoryForm = document.querySelector("#directory-filters");
  if (directoryForm) {
    const controls = {
      q: document.querySelector("#directory-q"),
      category: document.querySelector("#directory-category"),
      evidence: document.querySelector("#directory-evidence"),
      score: document.querySelector("#directory-score")
    };
    const cards = [...document.querySelectorAll("#directory-grid .project")];
    cards.forEach((card, index) => { card.dataset.order = index; });
    const grid = document.querySelector("#directory-grid");
    const count = document.querySelector("#directory-result-count");
    const empty = document.querySelector("#directory-empty");
    const keys = Object.keys(controls);
    const readURL = () => {
      const params = new URLSearchParams(location.search);
      keys.forEach(key => { controls[key].value = params.get(key) || ""; });
    };
    const apply = (updateURL = true) => {
      const terms = controls.q.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      cards.forEach(card => {
        const match = terms.every(term => card.dataset.search.toLocaleLowerCase().includes(term)) &&
          (!controls.category.value || card.dataset.category === controls.category.value) &&
          (!controls.evidence.value || card.dataset.evidence === controls.evidence.value) &&
          (!controls.score.value || (cardScore(card) !== null && cardScore(card) >= Number(controls.score.value)));
        card.hidden = !match;
        if (match) visible++;
      });
      sortCards(grid, cards, "score-desc");
      count.textContent = t(`显示 ${visible} / ${cards.length} 条`, `Showing ${visible} / ${cards.length}`);
      empty.hidden = visible !== 0;
      if (updateURL) {
        const url = new URL(location.href);
        keys.forEach(key => {
          const value = controls[key].value;
          value ? url.searchParams.set(key, value) : url.searchParams.delete(key);
        });
        url.searchParams.delete("kind");
        url.searchParams.delete("sort");
        history.replaceState(null, "", url);
        syncLanguageLinks();
      }
    };
    Object.values(controls).forEach(control => {
      control.addEventListener("input", apply);
      control.addEventListener("change", apply);
    });
    directoryForm.addEventListener("submit", event => event.preventDefault());
    directoryForm.addEventListener("reset", () => {
      Object.values(controls).forEach(control => { control.value = ""; });
      apply();
    });
    window.addEventListener("popstate", () => { readURL(); apply(); });
    readURL();
    apply();
    scrollToCurrentHash();
  }
  const sourceForm = document.querySelector("#project-source-filters");
  if (sourceForm) {
    const controls = {
      q: document.querySelector("#project-source-q"),
      category: document.querySelector("#project-source-category"),
      evidence: document.querySelector("#project-source-evidence"),
      score: document.querySelector("#project-source-score"),
      sort: document.querySelector("#project-source-sort")
    };
    const cards = [...document.querySelectorAll("#project-source-grid .project")];
    cards.forEach((card, index) => { card.dataset.order = index; });
    const grid = document.querySelector("#project-source-grid");
    const count = document.querySelector("#project-source-result-count");
    const empty = document.querySelector("#project-source-empty");
    const keys = Object.keys(controls);
    const readURL = () => {
      const params = new URLSearchParams(location.search);
      keys.forEach(key => { controls[key].value = params.get(key) || (key === "sort" ? "score-desc" : ""); });
    };
    const apply = (updateURL = true) => {
      const terms = controls.q.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      cards.forEach(card => {
        const match = terms.every(term => card.dataset.search.toLocaleLowerCase().includes(term)) &&
          (!controls.category.value || card.dataset.category === controls.category.value) &&
          (!controls.evidence.value || card.dataset.evidence === controls.evidence.value) &&
          (!controls.score.value || (cardScore(card) !== null && cardScore(card) >= Number(controls.score.value)));
        card.hidden = !match;
        if (match) visible++;
      });
      sortCards(grid, cards, controls.sort.value);
      count.textContent = t(`显示 ${visible} / ${cards.length} 条`, `Showing ${visible} / ${cards.length}`);
      empty.hidden = visible !== 0;
      if (updateURL) {
        const url = new URL(location.href);
        keys.forEach(key => {
          const value = controls[key].value;
          const isDefault = key === "sort" && value === "score-desc";
          value && !isDefault ? url.searchParams.set(key, value) : url.searchParams.delete(key);
        });
        history.replaceState(null, "", url);
        syncLanguageLinks();
      }
    };
    Object.values(controls).forEach(control => {
      control.addEventListener("input", apply);
      control.addEventListener("change", apply);
    });
    sourceForm.addEventListener("submit", event => event.preventDefault());
    sourceForm.addEventListener("reset", () => {
      Object.entries(controls).forEach(([key, control]) => { control.value = key === "sort" ? "score-desc" : ""; });
      apply();
    });
    window.addEventListener("popstate", () => { readURL(); apply(false); });
    readURL();
    apply(false);
    scrollToCurrentHash();
  }
  const leadForm = document.querySelector("#lead-filters");
  if (leadForm) {
    const leadQuery = document.querySelector("#lead-q");
    const leadSource = document.querySelector("#lead-source");
    const leadEvidence = document.querySelector("#lead-evidence");
    const leadScore = document.querySelector("#lead-score");
    const leadSort = document.querySelector("#lead-sort");
    const leadCards = [...document.querySelectorAll("#lead-grid .project")];
    leadCards.forEach((card, index) => { card.dataset.order = index; });
    const leadGrid = document.querySelector("#lead-grid");
    const leadCount = document.querySelector("#lead-result-count");
    const leadEmpty = document.querySelector("#lead-empty");
    const readLeadURL = () => {
      const params = new URLSearchParams(location.search);
      leadQuery.value = params.get("q") || "";
      leadSource.value = params.get("source") || "";
      leadEvidence.value = params.get("evidence") || "";
      leadScore.value = params.get("score") || "";
      leadSort.value = params.get("sort") || "score-desc";
    };
    const applyLeadFilters = (updateURL = true) => {
      const terms = leadQuery.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      leadCards.forEach(card => {
        const match = terms.every(term => card.dataset.search.toLocaleLowerCase().includes(term)) &&
          (!leadSource.value || card.dataset.source === leadSource.value) &&
          (!leadEvidence.value || card.dataset.evidence === leadEvidence.value) &&
          (!leadScore.value || (cardScore(card) !== null && cardScore(card) >= Number(leadScore.value)));
        card.hidden = !match;
        if (match) visible++;
      });
      leadCount.textContent = t(`显示 ${visible} / ${leadCards.length} 条`, `Showing ${visible} / ${leadCards.length}`);
      leadEmpty.hidden = visible !== 0;
      sortCards(leadGrid, leadCards, leadSort.value);
      if (updateURL) {
        const url = new URL(location.href);
        [["q", leadQuery], ["source", leadSource], ["evidence", leadEvidence], ["score", leadScore], ["sort", leadSort]].forEach(([key, control]) => {
          const isDefault = key === "sort" && control.value === "score-desc";
          control.value && !isDefault ? url.searchParams.set(key, control.value) : url.searchParams.delete(key);
        });
        history.replaceState(null, "", url);
        syncLanguageLinks();
      }
    };
    [leadQuery, leadSource, leadEvidence, leadScore, leadSort].forEach(control => {
      control.addEventListener("input", applyLeadFilters);
      control.addEventListener("change", applyLeadFilters);
    });
    leadForm.addEventListener("submit", event => event.preventDefault());
    leadForm.addEventListener("reset", event => { event.preventDefault(); leadQuery.value = ""; leadSource.value = ""; leadEvidence.value = ""; leadScore.value = ""; leadSort.value = "score-desc"; applyLeadFilters(); });
    window.addEventListener("popstate", () => { readLeadURL(); applyLeadFilters(false); });
    readLeadURL();
    applyLeadFilters(false);
    scrollToCurrentHash();
  }
  const form = document.querySelector("#filters");
  if (!form) return;
  const keys = ["q", "category", "use", "ai", "difficulty", "evidence", "score", "sort"];
  const controls = Object.fromEntries(keys.map(k => [k, document.getElementById(k)]));
  const cards = [...document.querySelectorAll("#project-grid .project")];
  cards.forEach((card, index) => { card.dataset.order = index; });
  const grid = document.querySelector("#project-grid");
  const count = document.querySelector("#result-count");
  function readURL() {
    const params = new URLSearchParams(location.search);
    keys.forEach(k => { controls[k].value = params.get(k) || (k === "sort" ? "score-desc" : ""); });
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
        ["category", "use", "ai", "difficulty", "evidence"].every(k => !controls[k].value || (k === "use"
          ? card.dataset.use.split("|").includes(controls[k].value)
          : card.dataset[k] === controls[k].value)) &&
        (!controls.score.value || (cardScore(card) !== null && cardScore(card) >= Number(controls.score.value)));
      card.hidden = !match;
      if (match) visible++;
    });
    count.textContent = t(`显示 ${visible} / ${cards.length} 个条目`, `Showing ${visible} / ${cards.length} entries`);
    document.querySelector("#empty").hidden = visible !== 0;
    sortCards(grid, cards, controls.sort.value);
    if (updateURL) {
      const url = new URL(location.href);
      keys.forEach(k => {
        const value = controls[k].value;
        const isDefault = k === "sort" && value === "score-desc";
        value && !isDefault ? url.searchParams.set(k, value) : url.searchParams.delete(k);
      });
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
  form.addEventListener("reset", event => { event.preventDefault(); keys.forEach(k => { controls[k].value = k === "sort" ? "score-desc" : ""; }); apply(); });
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
