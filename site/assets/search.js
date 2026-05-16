
(function () {
  const root = document.body.dataset.root || ".";
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  const toggle = document.getElementById("theme-toggle");
  const sidebarToggle = document.getElementById("sidebar-toggle");

  // Theme toggle — null-guarded so a missing button can't kill the rest of the script.
  const saved = localStorage.getItem("theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  if (toggle) {
    toggle.addEventListener("click", () => {
      const cur = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", cur);
      localStorage.setItem("theme", cur);
    });
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
    });
    // Tap any nav link on mobile → close the drawer so the user lands on the page.
    document.querySelectorAll(".sidebar a").forEach(a => {
      a.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 780px)").matches) {
          document.body.classList.remove("nav-open");
        }
      });
    });
  }

  // Scroll the current page's nav row into view if it's offscreen.
  const activeLink = document.querySelector(
    ".sidebar .nav-leaf.active, .sidebar .nav-child.active, .sidebar .sidebar-link.active"
  );
  if (activeLink) {
    const rect = activeLink.getBoundingClientRect();
    if (rect.top < 80 || rect.bottom > window.innerHeight - 40) {
      activeLink.scrollIntoView({ block: "center" });
    }
  }

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
  let activeIndex = -1;
  let currentHits = [];

  input.addEventListener("focus", () => { loadIndex(); });
  input.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(runSearch, 120);
  });
  input.addEventListener("keydown", (e) => {
    if (results.hidden || !currentHits.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      activeIndex = (activeIndex + 1) % currentHits.length;
      updateActive();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + currentHits.length) % currentHits.length;
      updateActive();
    } else if (e.key === "Enter" && activeIndex >= 0) {
      const nodes = results.querySelectorAll(".hit");
      if (nodes[activeIndex]) {
        e.preventDefault();
        window.location.href = nodes[activeIndex].href;
      }
    }
  });

  function updateActive() {
    const nodes = results.querySelectorAll(".hit");
    nodes.forEach((n, i) => n.classList.toggle("active", i === activeIndex));
    if (activeIndex >= 0 && nodes[activeIndex]) {
      nodes[activeIndex].scrollIntoView({ block: "nearest" });
    }
  }

  async function runSearch() {
    const q = input.value.trim().toLowerCase();
    if (!q) { results.hidden = true; results.innerHTML = ""; currentHits = []; activeIndex = -1; return; }
    const terms = q.split(/\s+/).filter(Boolean);
    const idx = await loadIndex();
    const hits = idx.map(e => ({ e, s: score(e, terms) }))
                    .filter(x => x.s > 0)
                    .sort((a, b) => b.s - a.s)
                    .slice(0, 20);
    currentHits = hits;
    activeIndex = hits.length ? 0 : -1;
    if (!hits.length) {
      results.innerHTML = '<div class="empty">No matches for "' + escapeHtml(q) + '"</div>';
    } else {
      const count = `<div class="results-meta">${hits.length} result${hits.length === 1 ? "" : "s"} · ↑↓ to navigate · ↵ to open</div>`;
      results.innerHTML = count + hits.map((h, i) =>
        `<a class="hit${i === 0 ? " active" : ""}" href="${root}/${h.e.url}"><div class="hit-title">${highlight(h.e.title, terms)}</div><div class="meta">${escapeHtml(h.e.branch)} · ${escapeHtml(h.e.kind)}</div><p>${highlight(h.e.description || "", terms)}</p></a>`
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

  function highlight(text, terms) {
    const safe = escapeHtml(text);
    const pattern = terms
      .map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
      .filter(Boolean)
      .join("|");
    if (!pattern) return safe;
    return safe.replace(new RegExp("(" + pattern + ")", "gi"), "<mark>$1</mark>");
  }

})();
