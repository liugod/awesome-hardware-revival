"use strict";
(() => {
  const form = document.querySelector("#filters");
  if (!form) return;
  const keys = ["q", "category", "use", "ai", "difficulty", "evidence"];
  const controls = Object.fromEntries(keys.map(k => [k, document.getElementById(k)]));
  const cards = [...document.querySelectorAll(".project")];
  const count = document.querySelector("#result-count");
  function readURL() {
    const params = new URLSearchParams(location.search);
    keys.forEach(k => { controls[k].value = params.get(k) || ""; });
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
    count.textContent = `显示 ${visible} / ${cards.length} 个条目`;
    document.querySelector("#empty").hidden = visible !== 0;
    if (updateURL) {
      const url = new URL(location.href);
      keys.forEach(k => controls[k].value ? url.searchParams.set(k, controls[k].value) : url.searchParams.delete(k));
      history.replaceState(null, "", url);
    }
  }
  readURL();
  apply(false);
  form.addEventListener("input", () => apply());
  form.addEventListener("change", () => apply());
  form.addEventListener("submit", e => e.preventDefault());
  form.addEventListener("reset", () => { keys.forEach(k => { controls[k].value = ""; }); apply(); });
  window.addEventListener("popstate", () => { readURL(); apply(false); });
  document.querySelector("#share").addEventListener("click", async () => {
    const target = document.querySelector("#share-status");
    try {
      await navigator.clipboard.writeText(location.href);
      target.textContent = "已复制当前筛选链接";
    } catch {
      target.textContent = "请复制浏览器地址栏中的链接，筛选条件已保存在网址中。";
    }
  });
})();
