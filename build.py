#!/usr/bin/env python3
"""Build a static HTML site from an Obsidian vault.

Walks cybersecurity/ and projects/ under VAULT, converts each .md to .html,
resolves [[wikilinks]] and relative .md links, emits a sidebar and a
client-side search index. No framework, no build step beyond running this.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml

VAULT = Path("/Users/lautarodamore/obsidian-vault/ldamore")
OUT = Path(__file__).resolve().parent / "site"
SECTIONS = [
    ("cybersecurity", "Cybersecurity"),
    ("projects", "Projects"),
]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
TAG_RE = re.compile(r"(?<!\w)#([A-Za-z][A-Za-z0-9_\-/]*)")


@dataclass
class Note:
    section: str           # "cybersecurity" | "projects"
    rel_path: Path         # path relative to VAULT, e.g. cybersecurity/networking/foo.md
    title: str
    slug: str              # basename without extension
    body_md: str
    tags: list[str] = field(default_factory=list)
    frontmatter: dict = field(default_factory=dict)

    @property
    def out_path(self) -> Path:
        return OUT / self.rel_path.with_suffix(".html")

    @property
    def url(self) -> str:
        return str(self.rel_path.with_suffix(".html"))


def load_note(section: str, path: Path) -> Note:
    raw = path.read_text(encoding="utf-8")
    fm: dict = {}
    m = FRONTMATTER_RE.match(raw)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            fm = {}
        raw = raw[m.end():]

    # Title: first H1, else frontmatter title, else humanized filename.
    title_match = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    elif isinstance(fm.get("title"), str):
        title = fm["title"]
    else:
        title = path.stem.replace("-", " ").replace("_", " ").title()

    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t) for t in tags]

    rel = path.relative_to(VAULT)
    return Note(
        section=section,
        rel_path=rel,
        title=title,
        slug=path.stem,
        body_md=raw,
        tags=tags,
        frontmatter=fm,
    )


def build_slug_index(notes: list[Note]) -> tuple[dict[str, list[Note]], dict[str, Note]]:
    """Return (slug -> [Notes], full_path_without_ext -> Note).

    The slug map keeps every candidate so we can pick the closest match per
    resolution call. The path map resolves wikilinks that spell out a full path.
    """
    by_slug: dict[str, list[Note]] = {}
    by_path: dict[str, Note] = {}
    collisions: dict[str, list[Note]] = {}
    for n in notes:
        if n.slug in by_slug and n.slug != "index":
            collisions.setdefault(n.slug, list(by_slug[n.slug])).append(n)
        by_slug.setdefault(n.slug, []).append(n)
        by_slug.setdefault(n.slug.lower(), []).append(n)
        key = str(n.rel_path.with_suffix(""))
        by_path[key] = n
        by_path[key.lower()] = n
    # Also index by title-slugified form: "TCP/IP Basics" -> "tcp-ip-basics"
    for n in notes:
        t_slug = re.sub(r"[^a-z0-9]+", "-", n.title.lower()).strip("-")
        if t_slug and t_slug != n.slug.lower():
            by_slug.setdefault(t_slug, []).append(n)
    for slug, members in collisions.items():
        paths = ", ".join(str(m.rel_path) for m in members)
        print(f"[warn] slug collision '{slug}': {paths} (resolver will prefer same-folder)", file=sys.stderr)
    return by_slug, by_path


def rewrite_links(md_text: str, note: Note, by_slug: dict[str, list[Note]], by_path: dict[str, Note]) -> str:
    """Rewrite [[wikilinks]] and relative .md links to generated .html paths."""
    import os
    here = (OUT / note.rel_path).parent
    source_folder = "/".join(note.rel_path.parts[:-1])

    def rel_href(target: Note) -> str:
        return os.path.relpath(OUT / target.rel_path.with_suffix(".html"), here)

    def resolve(raw: str) -> Note | None:
        raw = raw.strip()
        if raw.endswith(".md"):
            raw = raw[:-3]
        # Path-like?
        if "/" in raw:
            key = raw.strip("/")
            return by_path.get(key) or by_path.get(key.lower())
        # Bare slug — try exact, then lowercase, then title-slug.
        candidates = by_slug.get(raw) or by_slug.get(raw.lower())
        if not candidates:
            slugged = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
            candidates = by_slug.get(slugged)
        if not candidates:
            return None
        # Deduplicate while preserving order.
        seen = set()
        unique = []
        for c in candidates:
            k = str(c.rel_path)
            if k not in seen:
                seen.add(k)
                unique.append(c)
        if len(unique) == 1:
            return unique[0]
        # Prefer same folder, then same section, else first.
        for c in unique:
            if "/".join(c.rel_path.parts[:-1]) == source_folder:
                return c
        for c in unique:
            if c.rel_path.parts[0] == note.rel_path.parts[0]:
                return c
        return unique[0]

    def wikilink_sub(m: re.Match) -> str:
        target_raw = m.group(1).strip()
        label = (m.group(2) or target_raw.split("/")[-1]).strip()
        # Drop optional heading anchor "Page#Section"
        target_slug, _, anchor = target_raw.partition("#")
        target = resolve(target_slug)
        if not target:
            return f'<span class="broken-link" title="Unresolved: {html.escape(target_slug)}">{html.escape(label)}</span>'
        href = rel_href(target)
        if anchor:
            href += "#" + anchor.strip().lower().replace(" ", "-")
        return f'<a href="{html.escape(href)}">{html.escape(label)}</a>'

    def mdlink_sub(m: re.Match) -> str:
        label = m.group(1)
        href = m.group(2).strip()
        # Leave external / anchor / already-html links alone.
        if href.startswith(("http://", "https://", "mailto:", "#", "/")):
            return m.group(0)
        # Rewrite relative .md -> .html
        if href.endswith(".md") or ".md#" in href:
            new_href = href.replace(".md#", ".html#").replace(".md", ".html")
            return f"[{label}]({new_href})"
        return m.group(0)

    # Wikilinks first (they're inline so safe before markdown parse; emit raw HTML
    # that markdown will leave alone because it's on a single line).
    md_text = WIKILINK_RE.sub(wikilink_sub, md_text)
    md_text = MD_LINK_RE.sub(mdlink_sub, md_text)
    return md_text


def build_sidebar_tree(notes: list[Note]) -> dict:
    """Return nested dict: {section: {subfolder: [notes], ...}}"""
    tree: dict[str, dict[str, list[Note]]] = {}
    for n in notes:
        parts = n.rel_path.parts  # (section, [sub...], file.md)
        section = parts[0]
        sub = "/".join(parts[1:-1]) or ""
        tree.setdefault(section, {}).setdefault(sub, []).append(n)
    # Stable ordering.
    for section in tree:
        for sub in tree[section]:
            tree[section][sub].sort(key=lambda n: (n.slug != "index", n.title.lower()))
    return tree


def render_sidebar(tree: dict, current: Note | None) -> str:
    """Render sidebar HTML with collapsible subfolders."""
    lines: list[str] = ['<nav class="sidebar">']
    lines.append('<a class="sidebar-home" href="{home}">Home</a>'.format(
        home=relpath_from(current, OUT / "index.html")
    ))
    for section_key, section_label in SECTIONS:
        subs = tree.get(section_key, {})
        if not subs:
            continue
        lines.append(f'<div class="sidebar-section"><h3>{html.escape(section_label)}</h3>')

        # Root-level (no subfolder) notes first.
        root_notes = subs.get("", [])
        for n in root_notes:
            lines.append(render_sidebar_link(n, current))

        for sub in sorted(k for k in subs if k):
            open_attr = ""
            if current and current.rel_path.parts[0] == section_key and "/".join(current.rel_path.parts[1:-1]) == sub:
                open_attr = " open"
            lines.append(f'<details{open_attr}><summary>{html.escape(sub)}</summary>')
            for n in subs[sub]:
                lines.append(render_sidebar_link(n, current))
            lines.append("</details>")
        lines.append("</div>")
    lines.append("</nav>")
    return "\n".join(lines)


def render_sidebar_link(n: Note, current: Note | None) -> str:
    target_html = OUT / n.rel_path.with_suffix(".html")
    here = (OUT / current.rel_path).parent if current else OUT
    import os
    href = os.path.relpath(target_html, here)
    cls = "active" if current and current.rel_path == n.rel_path else ""
    label = n.title if len(n.title) < 60 else n.title[:57] + "…"
    return f'<a class="{cls}" href="{html.escape(href)}">{html.escape(label)}</a>'


def relpath_from(note: Note | None, target: Path) -> str:
    import os
    here = (OUT / note.rel_path).parent if note else OUT
    return os.path.relpath(target, here)


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{css_href}">
<link rel="stylesheet" href="{pygments_href}">
</head>
<body data-root="{root_href}">
<header class="topbar">
  <a class="brand" href="{home_href}">ldamoredev notes</a>
  <input id="search" type="search" placeholder="Search notes…" autocomplete="off">
  <button id="theme-toggle" title="Toggle theme">◐</button>
</header>
<div id="search-results" hidden></div>
<div class="layout">
{sidebar}
<main class="content">
{tag_line}
<article>
{body}
</article>
</main>
</div>
<script src="{search_js_href}"></script>
</body>
</html>
"""


def render_page(note: Note, html_body: str, sidebar_html: str, tree: dict) -> str:
    import os
    here = note.out_path.parent
    css_href = os.path.relpath(OUT / "assets" / "style.css", here)
    pyg_href = os.path.relpath(OUT / "assets" / "pygments.css", here)
    search_js = os.path.relpath(OUT / "assets" / "search.js", here)
    home_href = os.path.relpath(OUT / "index.html", here)
    root_href = os.path.relpath(OUT, here) or "."

    tag_line = ""
    if note.tags:
        chips = " ".join(f'<span class="tag">#{html.escape(t)}</span>' for t in note.tags)
        tag_line = f'<div class="tags">{chips}</div>'

    return PAGE_TEMPLATE.format(
        title=html.escape(note.title),
        css_href=html.escape(css_href),
        pygments_href=html.escape(pyg_href),
        search_js_href=html.escape(search_js),
        home_href=html.escape(home_href),
        root_href=html.escape(root_href),
        sidebar=sidebar_html,
        tag_line=tag_line,
        body=html_body,
    )


def md_to_html(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",
            "tables",
            "fenced_code",
            "codehilite",
            "sane_lists",
            "toc",
        ],
        extension_configs={
            "codehilite": {"guess_lang": False, "noclasses": False},
            "toc": {"permalink": False},
        },
    )
    return md.convert(md_text)


def write_pygments_css(path: Path) -> None:
    from pygments.formatters import HtmlFormatter
    path.write_text(HtmlFormatter().get_style_defs(".codehilite"), encoding="utf-8")


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", " ", s)


def build_home(tree: dict, notes: list[Note]) -> str:
    lines = ["<h1>ldamoredev notes</h1>",
             "<p>Static snapshot of my Obsidian vault. Two sections: <strong>Cybersecurity</strong> (concept notes, playbooks, tooling) and <strong>Projects</strong> (integration work that ties branches together).</p>"]
    for section_key, section_label in SECTIONS:
        subs = tree.get(section_key, {})
        if not subs:
            continue
        lines.append(f'<h2>{html.escape(section_label)}</h2><ul>')
        count = sum(len(v) for v in subs.values())
        lines.append(f"<li><em>{count} notes</em></li>")
        # Prefer an index note if it exists.
        for n in notes:
            if n.rel_path.parts[0] == section_key and n.slug == "index" and len(n.rel_path.parts) == 2:
                lines.append(f'<li><a href="{html.escape(n.url)}">Section index</a></li>')
                break
        # Subfolders.
        for sub in sorted(k for k in subs if k):
            first = subs[sub][0]
            import os
            href = os.path.relpath(OUT / first.rel_path.with_suffix(".html"), OUT)
            lines.append(f'<li><a href="{html.escape(href)}">{html.escape(sub)}</a> — {len(subs[sub])} notes</li>')
        lines.append("</ul>")
    return "\n".join(lines)


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)

    # Load notes.
    notes: list[Note] = []
    for section_key, _ in SECTIONS:
        root = VAULT / section_key
        if not root.exists():
            print(f"[warn] missing: {root}", file=sys.stderr)
            continue
        for p in sorted(root.rglob("*.md")):
            notes.append(load_note(section_key, p))

    print(f"Loaded {len(notes)} notes.")
    by_slug, by_path = build_slug_index(notes)
    tree = build_sidebar_tree(notes)

    # Search index: title + plain body text.
    search_entries: list[dict] = []

    broken_total = 0
    for n in notes:
        rewritten = rewrite_links(n.body_md, n, by_slug, by_path)
        broken_total += rewritten.count('class="broken-link"')
        body_html = md_to_html(rewritten)
        sidebar_html = render_sidebar(tree, n)
        page = render_page(n, body_html, sidebar_html, tree)
        n.out_path.parent.mkdir(parents=True, exist_ok=True)
        n.out_path.write_text(page, encoding="utf-8")

        search_entries.append({
            "title": n.title,
            "url": n.url,
            "section": n.section,
            "tags": n.tags,
            "text": strip_html(body_html)[:2000],
        })

    # Home page.
    home_note = Note(section="", rel_path=Path("index.md"), title="ldamoredev notes", slug="index", body_md="")
    home_body = build_home(tree, notes)
    sidebar_html = render_sidebar(tree, home_note)
    (OUT / "index.html").write_text(
        render_page(home_note, home_body, sidebar_html, tree),
        encoding="utf-8",
    )

    # Search index + assets.
    (OUT / "assets" / "search.json").write_text(
        json.dumps(search_entries, ensure_ascii=False),
        encoding="utf-8",
    )
    write_pygments_css(OUT / "assets" / "pygments.css")
    (OUT / "assets" / "style.css").write_text(STYLE_CSS, encoding="utf-8")
    (OUT / "assets" / "search.js").write_text(SEARCH_JS, encoding="utf-8")

    print(f"Wrote {len(notes) + 1} pages to {OUT} (unresolved wikilinks: {broken_total})")
    return 0


STYLE_CSS = r"""
:root {
  --bg: #fdfdfc;
  --fg: #1b1b1b;
  --muted: #666;
  --accent: #2a5db0;
  --border: #e3e3e0;
  --code-bg: #f5f5f3;
  --sidebar-bg: #f8f8f6;
  --tag-bg: #eef2f9;
}
html[data-theme="dark"] {
  --bg: #15171a;
  --fg: #e4e4e1;
  --muted: #9aa0a6;
  --accent: #8ab4f8;
  --border: #2a2d31;
  --code-bg: #1e2024;
  --sidebar-bg: #1a1c1f;
  --tag-bg: #23272e;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); }
body { font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.topbar {
  display: flex; align-items: center; gap: 1rem;
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; background: var(--bg); z-index: 10;
}
.topbar .brand { font-weight: 600; color: var(--fg); }
.topbar #search {
  flex: 1; max-width: 400px;
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); color: var(--fg);
}
#theme-toggle { background: transparent; border: 1px solid var(--border); color: var(--fg); border-radius: 6px; padding: 0.3rem 0.6rem; cursor: pointer; }

#search-results {
  position: absolute; top: 52px; left: 0; right: 0; margin: 0 auto; max-width: 600px;
  background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  max-height: 60vh; overflow: auto; padding: 0.5rem; z-index: 20;
}
#search-results .hit { padding: 0.4rem 0.6rem; border-radius: 4px; }
#search-results .hit:hover { background: var(--sidebar-bg); }
#search-results .hit .meta { color: var(--muted); font-size: 0.85em; }

.layout { display: flex; min-height: calc(100vh - 52px); }
.sidebar {
  width: 280px; flex-shrink: 0;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  padding: 1rem;
  overflow-y: auto; max-height: calc(100vh - 52px); position: sticky; top: 52px;
  font-size: 0.92em;
}
.sidebar a { display: block; padding: 0.2rem 0.4rem; border-radius: 4px; color: var(--fg); }
.sidebar a:hover { background: var(--tag-bg); text-decoration: none; }
.sidebar a.active { background: var(--tag-bg); color: var(--accent); font-weight: 600; }
.sidebar .sidebar-home { font-weight: 600; margin-bottom: 0.5rem; }
.sidebar-section h3 { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); margin: 1rem 0 0.3rem; }
.sidebar details { margin: 0.15rem 0; }
.sidebar summary { cursor: pointer; padding: 0.2rem 0.4rem; color: var(--muted); font-weight: 500; }
.sidebar summary:hover { color: var(--fg); }

.content { flex: 1; padding: 2rem clamp(1rem, 4vw, 3rem); max-width: 900px; }
.content article { max-width: 72ch; }
.content h1 { margin-top: 0; font-size: 1.9rem; line-height: 1.25; }
.content h2 { margin-top: 2rem; padding-bottom: 0.2rem; border-bottom: 1px solid var(--border); }
.content h3 { margin-top: 1.5rem; }
.content p, .content li { color: var(--fg); }
.content blockquote { border-left: 3px solid var(--accent); padding: 0.2rem 1rem; color: var(--muted); background: var(--sidebar-bg); border-radius: 0 4px 4px 0; }
.content code { background: var(--code-bg); padding: 0.1rem 0.35rem; border-radius: 3px; font-size: 0.9em; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
.content pre { background: var(--code-bg); padding: 0.9rem; border-radius: 6px; overflow-x: auto; font-size: 0.88em; }
.content pre code { background: transparent; padding: 0; }
.content table { border-collapse: collapse; margin: 1rem 0; }
.content th, .content td { border: 1px solid var(--border); padding: 0.4rem 0.7rem; text-align: left; }
.content th { background: var(--sidebar-bg); }
.content hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }

.tags { margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.3rem; }
.tag { background: var(--tag-bg); color: var(--accent); padding: 0.1rem 0.5rem; border-radius: 999px; font-size: 0.82em; }
.broken-link { color: #b00; border-bottom: 1px dashed #b00; cursor: help; }
html[data-theme="dark"] .broken-link { color: #ff8a80; border-bottom-color: #ff8a80; }

@media (max-width: 780px) {
  .layout { flex-direction: column; }
  .sidebar { position: static; width: 100%; max-height: none; border-right: 0; border-bottom: 1px solid var(--border); }
  .content { padding: 1.2rem; }
}
"""

SEARCH_JS = r"""
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
"""


if __name__ == "__main__":
    sys.exit(main())
