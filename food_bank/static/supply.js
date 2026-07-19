(function () {
  const LEVEL_CLASS = {
    critically_low: "level-critically-low",
    low: "level-low",
    ok: "level-ok",
    high: "level-high",
    full: "level-full",
  };

  function initSupplySlider(root) {
    const hidden = root.querySelector("[data-supply-value]");
    const range = root.querySelector("[data-supply-range]");
    const label = root.querySelector("[data-supply-label]");
    const ticks = root.querySelectorAll(".supply-tick");
    const levels = JSON.parse(root.dataset.levels || "[]");
    const labels = JSON.parse(root.dataset.labels || "[]");

    function applyLevel(index) {
      const idx = Math.max(0, Math.min(levels.length - 1, Number(index)));
      const level = levels[idx];
      hidden.value = level;
      range.value = String(idx);
      range.setAttribute("aria-valuenow", String(idx));
      label.textContent = labels[idx];
      root.dataset.level = level;
      root.classList.remove(...Object.values(LEVEL_CLASS));
      root.classList.add(LEVEL_CLASS[level] || "level-ok");
      ticks.forEach((tick, tickIndex) => {
        tick.classList.toggle("active", tickIndex === idx);
      });
    }

    range.addEventListener("input", () => applyLevel(range.value));
    ticks.forEach((tick) => {
      tick.addEventListener("click", () => applyLevel(tick.dataset.tickIndex));
    });

    const startIndex = levels.indexOf(root.dataset.currentLevel);
    applyLevel(startIndex >= 0 ? startIndex : 2);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-supply-slider]").forEach(initSupplySlider);
  });
})();
