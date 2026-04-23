
(function () {
  const root = document.body.dataset.root || ".";
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  const toggle = document.getElementById("theme-toggle");

  // Theme toggle.
  const saved = localStorage.getItem("theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  toggle.addEventListener("click", () => {
    const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", cur);
    localStorage.setItem("theme", cur);
  });

  let index = null;
  async function loadIndex() {
    if (index) return index;
    const res = await fetch(root + "/assets/search.json");
    index = await res.json();
    return index;
  }

  function score(entry, terms) {
    const hay = (entry.title + " " + entry.tags.join(" ") + " " + entry.text).toLowerCase();
    let s = 0;
    for (const t of terms) {
      if (!t) continue;
      if (entry.title.toLowerCase().includes(t)) s += 5;
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
      results.innerHTML = '<div class="hit"><em>No matches</em></div>';
    } else {
      results.innerHTML = hits.map(h =>
        `<a class="hit" href="${root}/${h.e.url}"><div>${escapeHtml(h.e.title)}</div><div class="meta">${escapeHtml(h.e.section)} · ${escapeHtml(h.e.url)}</div></a>`
      ).join("");
    }
    results.hidden = false;
  }

  document.addEventListener("click", (e) => {
    if (e.target === input) return;
    if (!results.contains(e.target)) results.hidden = true;
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  }
})();
