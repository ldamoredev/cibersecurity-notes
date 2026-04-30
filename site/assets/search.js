
(function () {
  const root = document.body.dataset.root || ".";
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  const toggle = document.getElementById("theme-toggle");
  const sidebarToggle = document.getElementById("sidebar-toggle");

  // Theme toggle.
  const saved = localStorage.getItem("theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  toggle.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", cur);
    localStorage.setItem("theme", cur);
  });

  sidebarToggle.addEventListener("click", () => {
    document.body.classList.toggle("nav-open");
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
    if (e.key === "Escape") {
      results.hidden = true;
      document.body.classList.remove("nav-open");
      input.blur();
    }
  });

  let index = null;
  async function loadIndex() {
    if (index) return index;
    const res = await fetch(root + "/assets/search.json");
    index = await res.json();
    return index;
  }

  function score(entry, terms) {
    const keywords = (entry.keywords || []).join(" ");
    const description = entry.description || "";
    const title = entry.title.toLowerCase();
    const branch = entry.branch.toLowerCase();
    const tags = entry.tags.join(" ").toLowerCase();
    const hay = (
      entry.title + " " +
      keywords + " " +
      description + " " +
      entry.branch + " " +
      entry.group + " " +
      entry.kind + " " +
      entry.tags.join(" ") + " " +
      entry.text
    ).toLowerCase();
    let s = 0;
    for (const t of terms) {
      if (!t) continue;
      if (title.includes(t)) s += 10;
      if (keywords.toLowerCase().includes(t)) s += 8;
      if (tags.includes(t)) s += 6;
      if (branch.includes(t)) s += 4;
      if (entry.kind.toLowerCase().includes(t)) s += 2;
      const occurrences = hay.split(t).length - 1;
      if (!occurrences) return 0;
      s += occurrences;
    }
    return s;
  }

  let debounce;
  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(runSearch, 120);
  });

  async function runSearch() {
    const q = input.value.trim().toLowerCase();
    if (!q) { results.hidden = true; results.innerHTML = ""; return; }
    const terms = q.split(/\s+/);
    const idx = await loadIndex();
    const hits = idx.map(e => ({ e, s: score(e, terms) }))
                    .filter(x => x.s > 0)
                    .sort((a, b) => b.s - a.s)
                    .slice(0, 20);
    if (!hits.length) {
      results.innerHTML = '<div class="empty">No matches</div>';
    } else {
      results.innerHTML = hits.map(h =>
        `<a class="hit" href="${root}/${h.e.url}"><div class="hit-title">${escapeHtml(h.e.title)}</div><div class="meta">${escapeHtml(h.e.branch)} · ${escapeHtml(h.e.kind)} · ${escapeHtml(h.e.url)}</div><p>${escapeHtml(h.e.description || "")}</p></a>`
      ).join("");
    }
    results.hidden = false;
  }

  document.addEventListener("click", (e) => {
    if (e.target === input) return;
    if (e.target === sidebarToggle) return;
    if (!results.contains(e.target)) results.hidden = true;
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  }
})();
