#!/usr/bin/env python3
"""Build a static HTML site from an Obsidian vault.

Walks mature cybersecurity branches under VAULT, converts each .md to .html,
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
]

# Only publish mature cybersecurity branches and their reference registries.
# Keep private/project execution notes, templates, tooling experiments, and
# future/unpromoted branches out of the public static mirror.
BRANCHES = {
    "networking": {
        "label": "Networking",
        "group": "Foundations",
        "summary": "Reachability, HTTP, proxies, DNS, TLS, and packet-level observation.",
        "accent": "sky",
    },
    "wireless-security": {
        "label": "Wireless Security",
        "group": "Foundations",
        "summary": "Wi-Fi frames, handshakes, rogue access points, and local-network MITM.",
        "accent": "teal",
    },
    "web-security": {
        "label": "Web Security",
        "group": "Foundations",
        "summary": "Browser behavior, sessions, access control, and server-side exploit patterns.",
        "accent": "blue",
    },
    "api-security": {
        "label": "API Security",
        "group": "Foundations",
        "summary": "Authorization, token trust, inventory drift, and machine-readable abuse.",
        "accent": "indigo",
    },
    "cloud-security": {
        "label": "Cloud Security",
        "group": "Foundations",
        "summary": "IAM, metadata, storage, network boundaries, secrets, and logging controls.",
        "accent": "cyan",
    },
    "attack-surface-mapping": {
        "label": "Attack Surface Mapping",
        "group": "Exposure",
        "summary": "What is exposed, reachable, discoverable, and drifting from intended design.",
        "accent": "amber",
    },
    "osint": {
        "label": "OSINT",
        "group": "Exposure",
        "summary": "Public-source collection, evidence quality, and ethical handling of clues.",
        "accent": "violet",
    },
    "offensive-security": {
        "label": "Offensive Security / Recon",
        "group": "Exposure",
        "summary": "Discovery, validation, and handoff from recon into concrete testing.",
        "accent": "rose",
    },
    "linux-privilege-escalation": {
        "label": "Linux Privilege Escalation",
        "group": "Exposure",
        "summary": "Local boundary failures, enumeration, and safe escalation hypothesis testing.",
        "accent": "orange",
    },
    "devsecops": {
        "label": "DevSecOps",
        "group": "Engineering",
        "summary": "Secure delivery, CI/CD hardening, supply chain, secrets, and release trust.",
        "accent": "green",
    },
    "security-playbooks": {
        "label": "Security Playbooks",
        "group": "Execution",
        "summary": "Repeatable procedures for turning concepts into practical tests.",
        "accent": "slate",
    },
}

BRANCH_GROUPS = ("Foundations", "Exposure", "Engineering", "Execution")
MATURE_CYBERSECURITY_BRANCHES = set(BRANCHES)

MATURE_CYBERSECURITY_ROOT_FILES = {
    "index.md",
    "reference-registry.md",
    "reference-registry-api-security.md",
    "reference-registry-attack-surface-mapping.md",
    "reference-registry-cloud-security.md",
    "reference-registry-devsecops.md",
    "reference-registry-linux-privilege-escalation.md",
    "reference-registry-networking.md",
    "reference-registry-offensive-security.md",
    "reference-registry-osint.md",
    "reference-registry-playbooks.md",
    "reference-registry-web-security.md",
    "reference-registry-wireless-security.md",
}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
TAG_RE = re.compile(r"(?<!\w)#([A-Za-z][A-Za-z0-9_\-/]*)")


@dataclass
class Note:
    section: str           # "cybersecurity"
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


def branch_slug(note: Note) -> str:
    if len(note.rel_path.parts) >= 3 and note.rel_path.parts[0] == "cybersecurity":
        return note.rel_path.parts[1]
    return ""


def page_kind(note: Note) -> str:
    if note.slug.startswith("reference-registry"):
        return "registry"
    if note.rel_path.name == "index.md":
        return "index"
    if branch_slug(note) == "security-playbooks":
        return "playbook"
    return "concept"


def note_label(note: Note) -> str:
    return note.title.replace(" Seed", "")


def branch_label(slug: str) -> str:
    return BRANCHES.get(slug, {}).get("label", slug.replace("-", " ").title())


def branch_group(slug: str) -> str:
    return BRANCHES.get(slug, {}).get("group", "Other")


def branch_summary(slug: str) -> str:
    return BRANCHES.get(slug, {}).get("summary", "")


def branch_accent(slug: str) -> str:
    return BRANCHES.get(slug, {}).get("accent", "blue")


def should_publish(section: str, path: Path) -> bool:
    """Return whether a vault markdown file should be published."""
    rel = path.relative_to(VAULT)
    if section != "cybersecurity":
        return True
    if len(rel.parts) == 2:
        return rel.name in MATURE_CYBERSECURITY_ROOT_FILES
    branch = rel.parts[1]
    return branch in MATURE_CYBERSECURITY_BRANCHES


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
    if path.name.startswith("reference-registry"):
        raw = re.sub(r"^# (.+?) Seed$", r"# \1", raw, count=1, flags=re.MULTILINE)

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
            return f'<span class="unresolved-link" title="Unpublished or unresolved: {html.escape(target_slug)}">{html.escape(label)}</span>'
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
    lines.append('<a class="sidebar-home" href="{home}">Atlas Home</a>'.format(
        home=relpath_from(current, OUT / "index.html")
    ))
    for section_key, section_label in SECTIONS:
        subs = tree.get(section_key, {})
        if not subs:
            continue
        lines.append(f'<div class="sidebar-section"><h3>{html.escape(section_label)}</h3>')

        root_notes = [n for n in subs.get("", []) if not n.slug.startswith("reference-registry")]
        for n in root_notes:
            lines.append(render_sidebar_link(n, current, label="Cybersecurity Index"))

        for group in BRANCH_GROUPS:
            group_subs = [s for s in BRANCHES if s in subs and branch_group(s) == group]
            if not group_subs:
                continue
            lines.append(f'<div class="sidebar-group-label">{html.escape(group)}</div>')
            for sub in group_subs:
                lines.append(render_branch_details(subs, sub, current))

        other_subs = sorted(k for k in subs if k and k not in BRANCHES)
        if other_subs:
            lines.append('<div class="sidebar-group-label">Other</div>')
        for sub in other_subs:
            lines.append(render_branch_details(subs, sub, current))

        registry_notes = [n for n in subs.get("", []) if n.slug.startswith("reference-registry")]
        if registry_notes:
            open_attr = " open" if current and page_kind(current) == "registry" else ""
            lines.append(f'<details class="registry-group"{open_attr}><summary>Reference System <span>{len(registry_notes)}</span></summary>')
            for n in registry_notes:
                lines.append(render_sidebar_link(n, current))
            lines.append("</details>")
        lines.append("</div>")
    lines.append("</nav>")
    return "\n".join(lines)


def render_branch_details(subs: dict[str, list[Note]], sub: str, current: Note | None) -> str:
    lines: list[str] = []
    open_attr = ""
    if current and current.rel_path.parts[0] == "cybersecurity" and branch_slug(current) == sub:
        open_attr = " open"
    notes = subs[sub]
    index_note = next((n for n in notes if n.slug == "index"), None)
    summary = branch_summary(sub)
    accent = branch_accent(sub)
    lines.append(
        f'<details class="branch branch-{html.escape(accent)}"{open_attr}>'
        f'<summary><span>{html.escape(branch_label(sub))}</span><small>{len(notes)}</small></summary>'
    )
    if summary:
        lines.append(f'<p class="sidebar-summary">{html.escape(summary)}</p>')
    if index_note:
        lines.append(render_sidebar_link(index_note, current, label="Overview"))
    for n in notes:
        if n.slug == "index":
            continue
        lines.append(render_sidebar_link(n, current))
    lines.append("</details>")
    return "\n".join(lines)


def render_sidebar_link(n: Note, current: Note | None, label: str | None = None) -> str:
    target_html = OUT / n.rel_path.with_suffix(".html")
    here = (OUT / current.rel_path).parent if current else OUT
    import os
    href = os.path.relpath(target_html, here)
    classes = ["sidebar-link", f"kind-{page_kind(n)}"]
    if current and current.rel_path == n.rel_path:
        classes.append("active")
    visible_label = label or note_label(n)
    visible_label = visible_label if len(visible_label) < 60 else visible_label[:57] + "..."
    return f'<a class="{" ".join(classes)}" href="{html.escape(href)}">{html.escape(visible_label)}</a>'


def relpath_from(note: Note | None, target: Path) -> str:
    import os
    here = (OUT / note.rel_path).parent if note else OUT
    return os.path.relpath(target, here)


def breadcrumb_html(note: Note) -> str:
    parts = [f'<a href="{html.escape(relpath_from(note, OUT / "index.html"))}">Home</a>']
    if note.rel_path.parts and note.rel_path.parts[0] == "cybersecurity":
        cyber_index = OUT / "cybersecurity" / "index.html"
        parts.append(f'<a href="{html.escape(relpath_from(note, cyber_index))}">Cybersecurity</a>')
    branch = branch_slug(note)
    if branch:
        branch_index = OUT / "cybersecurity" / branch / "index.html"
        parts.append(f'<a href="{html.escape(relpath_from(note, branch_index))}">{html.escape(branch_label(branch))}</a>')
    parts.append(f'<span>{html.escape(note_label(note))}</span>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + "<span>/</span>".join(parts) + "</nav>"


def page_meta_html(note: Note) -> str:
    branch = branch_slug(note)
    chips = [f'<span class="meta-chip">{html.escape(page_kind(note))}</span>']
    if branch:
        chips.append(f'<span class="meta-chip accent-{html.escape(branch_accent(branch))}">{html.escape(branch_label(branch))}</span>')
    if note.tags:
        chips.extend(f'<span class="meta-chip tag">#{html.escape(t)}</span>' for t in note.tags)
    return f'<div class="page-meta">{"".join(chips)}</div>'


def extract_toc(html_body: str) -> list[tuple[int, str, str]]:
    headings: list[tuple[int, str, str]] = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>', html_body, re.DOTALL):
        level = int(m.group(1))
        anchor = m.group(2)
        label = strip_html(m.group(3)).strip()
        if label:
            headings.append((level, anchor, html.unescape(label)))
    return headings


def render_toc(html_body: str) -> str:
    headings = extract_toc(html_body)
    if not headings:
        return ""
    lines = ['<aside class="toc" aria-label="On this page"><div class="toc-inner"><h2>On This Page</h2>']
    for level, anchor, label in headings[:18]:
        lines.append(f'<a class="toc-level-{level}" href="#{html.escape(anchor)}">{html.escape(label)}</a>')
    lines.append('<a class="back-to-top" href="#top">Back to top</a></div></aside>')
    return "\n".join(lines)


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="{css_href}">
<link rel="stylesheet" href="{pygments_href}">
</head>
<body id="top" data-root="{root_href}">
<header class="topbar">
  <button id="sidebar-toggle" title="Toggle navigation" aria-label="Toggle navigation">☰</button>
  <a class="brand" href="{home_href}"><span>ldamoredev</span><small>security atlas</small></a>
  <div class="search-shell">
    <input id="search" type="search" placeholder="Search notes..." autocomplete="off">
    <kbd>/</kbd>
  </div>
  <button id="theme-toggle" title="Toggle theme" aria-label="Toggle theme">◐</button>
</header>
<div id="search-results" hidden></div>
<div class="layout {layout_class}">
{sidebar}
<main class="content">
{breadcrumbs}
<header class="page-hero">
{page_meta}
</header>
<article class="{article_class}">
{body}
</article>
</main>
{toc}
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

    toc_html = render_toc(html_body)
    return PAGE_TEMPLATE.format(
        title=html.escape(note.title),
        css_href=html.escape(css_href),
        pygments_href=html.escape(pyg_href),
        search_js_href=html.escape(search_js),
        home_href=html.escape(home_href),
        root_href=html.escape(root_href),
        sidebar=sidebar_html,
        layout_class="no-toc" if not toc_html else "with-toc",
        breadcrumbs=breadcrumb_html(note),
        page_meta=page_meta_html(note),
        article_class="article-home" if note.rel_path == Path("index.md") else "article-note",
        body=html_body,
        toc=toc_html,
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
    subs = tree.get("cybersecurity", {})
    published_notes = sum(len(v) for v in subs.values())
    registry_count = len([n for n in subs.get("", []) if n.slug.startswith("reference-registry")])
    lines = [
        '<section class="home-hero">',
        '<p class="eyebrow">Personal security knowledge base</p>',
        '<h1>ldamoredev security atlas</h1>',
        '<p class="lede">A static snapshot of mature cybersecurity notes from the Obsidian vault: learning paths, atomic concepts, reference policy, and practical playbooks shaped for fast retrieval.</p>',
        '<div class="stat-row">',
        f'<span><strong>{published_notes}</strong> published notes</span>',
        f'<span><strong>{len(BRANCHES)}</strong> branches</span>',
        f'<span><strong>{registry_count}</strong> reference registries</span>',
        '</div>',
        '</section>',
    ]
    cyber_index = next((n for n in subs.get("", []) if n.slug == "index"), None)
    if cyber_index:
        lines.append(f'<p class="home-index-link"><a href="{html.escape(cyber_index.url)}">Open the full cybersecurity index</a></p>')

    for group in BRANCH_GROUPS:
        group_slugs = [slug for slug in BRANCHES if slug in subs and branch_group(slug) == group]
        if not group_slugs:
            continue
        lines.append(f'<section class="branch-section"><h2>{html.escape(group)}</h2><div class="branch-grid">')
        for slug in group_slugs:
            notes_for_branch = subs[slug]
            index_note = next((n for n in notes_for_branch if n.slug == "index"), notes_for_branch[0])
            href = index_note.url
            accent = branch_accent(slug)
            concept_count = len([n for n in notes_for_branch if n.slug != "index"])
            lines.append(
                f'<a class="branch-card accent-{html.escape(accent)}" href="{html.escape(href)}">'
                f'<span class="card-kicker">{html.escape(group)}</span>'
                f'<h3>{html.escape(branch_label(slug))}</h3>'
                f'<p>{html.escape(branch_summary(slug))}</p>'
                f'<span class="card-meta">{concept_count} notes</span>'
                '</a>'
            )
        lines.append('</div></section>')

    registry_notes = [n for n in subs.get("", []) if n.slug.startswith("reference-registry")]
    if registry_notes:
        lines.append('<section class="reference-panel"><h2>Reference System</h2>')
        lines.append('<p>Reference registries stay published, but they sit behind the learning branches instead of competing with them in the primary path.</p>')
        lines.append('<div class="reference-list">')
        for n in registry_notes:
            lines.append(f'<a href="{html.escape(n.url)}">{html.escape(note_label(n))}</a>')
        lines.append('</div></section>')
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
            if not should_publish(section_key, p):
                continue
            notes.append(load_note(section_key, p))

    print(f"Loaded {len(notes)} notes.")
    by_slug, by_path = build_slug_index(notes)
    tree = build_sidebar_tree(notes)

    # Search index: title + plain body text.
    search_entries: list[dict] = []

    broken_total = 0
    for n in notes:
        rewritten = rewrite_links(n.body_md, n, by_slug, by_path)
        broken_total += rewritten.count('class="unresolved-link"')
        body_html = md_to_html(rewritten)
        sidebar_html = render_sidebar(tree, n)
        page = render_page(n, body_html, sidebar_html, tree)
        n.out_path.parent.mkdir(parents=True, exist_ok=True)
        n.out_path.write_text(page, encoding="utf-8")

        search_entries.append({
            "title": note_label(n),
            "url": n.url,
            "section": n.section,
            "branch": branch_label(branch_slug(n)) if branch_slug(n) else "Cybersecurity",
            "group": branch_group(branch_slug(n)) if branch_slug(n) else "Reference",
            "kind": page_kind(n),
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
  --bg: #fbfbf8;
  --surface: #ffffff;
  --surface-soft: #f4f6f3;
  --fg: #151817;
  --muted: #67706b;
  --muted-2: #8a928e;
  --accent: #256d85;
  --accent-soft: #e5f3f5;
  --border: #dde3dd;
  --border-strong: #c6d0c8;
  --code-bg: #eef2ef;
  --shadow: 0 18px 50px rgba(30, 45, 40, 0.08);
  --topbar-h: 64px;
  --sidebar-w: 312px;
  --toc-w: 236px;
}
html[data-theme="dark"] {
  --bg: #111416;
  --surface: #171b1d;
  --surface-soft: #1d2423;
  --fg: #e8ece8;
  --muted: #a3ada8;
  --muted-2: #7e8985;
  --accent: #70c0d8;
  --accent-soft: #143039;
  --border: #2b3433;
  --border-strong: #3a4745;
  --code-bg: #202828;
  --shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); }
body { font: 16px/1.68 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif; text-rendering: optimizeLegibility; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.topbar {
  display: grid;
  grid-template-columns: var(--sidebar-w) minmax(280px, 520px) auto;
  align-items: center;
  gap: 0.9rem;
  min-height: var(--topbar-h);
  padding: 0.75rem clamp(1rem, 2vw, 1.5rem);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: color-mix(in srgb, var(--bg) 88%, transparent);
  backdrop-filter: blur(16px);
  z-index: 30;
}
.brand { color: var(--fg); display: flex; flex-direction: column; line-height: 1.05; min-width: 0; }
.brand span { font-weight: 740; letter-spacing: 0; }
.brand small { margin-top: 0.18rem; color: var(--muted); font-size: 0.74rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.brand:hover { text-decoration: none; }
#sidebar-toggle, #theme-toggle {
  width: 38px;
  height: 38px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--fg);
  cursor: pointer;
  box-shadow: none;
}
#sidebar-toggle { display: none; }
.search-shell { position: relative; width: min(100%, 520px); }
.search-shell input {
  width: 100%;
  height: 42px;
  padding: 0 3rem 0 0.9rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--fg);
  font: inherit;
  box-shadow: 0 1px 0 rgba(20, 30, 28, 0.03);
}
.search-shell input:focus { outline: 2px solid var(--accent-soft); border-color: var(--accent); }
.search-shell kbd {
  position: absolute;
  right: 0.55rem;
  top: 50%;
  transform: translateY(-50%);
  min-width: 24px;
  padding: 0.05rem 0.38rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--muted);
  background: var(--surface-soft);
  font: 0.78rem ui-monospace, SFMono-Regular, Menlo, monospace;
  text-align: center;
}

#search-results {
  position: fixed;
  top: calc(var(--topbar-h) + 10px);
  left: 50%;
  transform: translateX(-50%);
  width: min(680px, calc(100vw - 2rem));
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  max-height: 68vh;
  overflow: auto;
  padding: 0.45rem;
  z-index: 50;
  box-shadow: var(--shadow);
}
#search-results .hit { display: block; padding: 0.75rem 0.85rem; border-radius: 8px; color: var(--fg); }
#search-results .hit:hover { background: var(--surface-soft); text-decoration: none; }
#search-results .hit-title { font-weight: 700; }
#search-results .meta { color: var(--muted); font-size: 0.84rem; margin-top: 0.12rem; }
#search-results .empty { padding: 0.8rem; color: var(--muted); }

.layout {
  display: grid;
  grid-template-columns: var(--sidebar-w) minmax(0, 1fr) var(--toc-w);
  min-height: calc(100vh - var(--topbar-h));
}
.layout.no-toc { grid-template-columns: var(--sidebar-w) minmax(0, 1fr); }
.sidebar {
  background: var(--surface-soft);
  border-right: 1px solid var(--border);
  padding: 1.15rem 0.9rem 1.6rem;
  overflow-y: auto;
  max-height: calc(100vh - var(--topbar-h));
  position: sticky;
  top: var(--topbar-h);
  font-size: 0.92rem;
}
.sidebar-home {
  display: block;
  margin: 0 0 1rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  color: var(--fg);
  font-weight: 740;
}
.sidebar-home:hover { text-decoration: none; border-color: var(--border-strong); }
.sidebar-section h3, .sidebar-group-label {
  margin: 1rem 0 0.35rem;
  padding: 0 0.55rem;
  color: var(--muted-2);
  font-size: 0.74rem;
  font-weight: 760;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.sidebar-section h3 { margin-top: 0; }
.sidebar details { margin: 0.18rem 0; border-radius: 8px; }
.sidebar summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  cursor: pointer;
  padding: 0.42rem 0.55rem;
  border-radius: 8px;
  color: var(--fg);
  font-weight: 680;
}
.sidebar summary:hover { background: var(--surface); }
.sidebar summary small, .sidebar summary span:last-child {
  color: var(--muted-2);
  font-size: 0.75rem;
  font-weight: 700;
}
.sidebar-summary {
  margin: 0.1rem 0.55rem 0.45rem;
  color: var(--muted);
  font-size: 0.82rem;
  line-height: 1.4;
}
.sidebar-link {
  display: block;
  margin: 0.05rem 0 0.05rem 0.8rem;
  padding: 0.3rem 0.55rem;
  border-radius: 7px;
  color: var(--fg);
  line-height: 1.35;
}
.sidebar-link:hover { background: var(--surface); text-decoration: none; }
.sidebar-link.active {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 740;
}
.kind-registry { color: var(--muted); }
.registry-group { margin-top: 1.2rem; border-top: 1px solid var(--border); padding-top: 0.75rem; }

.content {
  min-width: 0;
  padding: 2.3rem clamp(1.25rem, 4vw, 4rem) 4rem;
}
.article-note, .page-hero, .breadcrumbs { max-width: 76ch; }
.article-home { max-width: 1120px; }
.breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  align-items: center;
  margin-bottom: 0.8rem;
  color: var(--muted);
  font-size: 0.84rem;
}
.breadcrumbs a { color: var(--muted); }
.breadcrumbs span:last-child { color: var(--fg); }
.page-hero { margin-bottom: 0.65rem; }
.page-meta { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.meta-chip {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0.12rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--muted);
  background: var(--surface);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: capitalize;
}
.meta-chip.tag { text-transform: none; color: var(--accent); background: var(--accent-soft); border-color: transparent; }
.content h1 { margin: 0.35rem 0 1rem; font-size: clamp(2rem, 3vw, 3rem); line-height: 1.08; letter-spacing: 0; }
.content h2 { margin-top: 2.35rem; padding-bottom: 0.32rem; border-bottom: 1px solid var(--border); font-size: 1.45rem; line-height: 1.25; }
.content h3 { margin-top: 1.55rem; font-size: 1.05rem; }
.content p, .content li { color: var(--fg); }
.content p { margin: 1rem 0; }
.content ul, .content ol { padding-left: 1.35rem; }
.content li + li { margin-top: 0.2rem; }
.content blockquote {
  border-left: 4px solid var(--accent);
  margin: 1.25rem 0;
  padding: 0.75rem 1rem;
  color: var(--muted);
  background: var(--surface-soft);
  border-radius: 0 8px 8px 0;
}
.content code {
  background: var(--code-bg);
  padding: 0.1rem 0.36rem;
  border-radius: 5px;
  font-size: 0.9em;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.content pre {
  background: var(--code-bg);
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.88em;
}
.content pre code { background: transparent; padding: 0; }
.content table { border-collapse: collapse; margin: 1.2rem 0; width: 100%; font-size: 0.94rem; }
.content th, .content td { border: 1px solid var(--border); padding: 0.48rem 0.7rem; text-align: left; vertical-align: top; }
.content th { background: var(--surface-soft); }
.content hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }

.toc {
  padding: 2.3rem 1.2rem 2rem 0;
}
.toc-inner {
  position: sticky;
  top: calc(var(--topbar-h) + 1.2rem);
  max-height: calc(100vh - var(--topbar-h) - 2rem);
  overflow: auto;
  border-left: 1px solid var(--border);
  padding-left: 1rem;
}
.toc h2 { margin: 0 0 0.65rem; color: var(--muted-2); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.08em; }
.toc a { display: block; padding: 0.18rem 0; color: var(--muted); font-size: 0.84rem; line-height: 1.35; }
.toc a:hover { color: var(--accent); text-decoration: none; }
.toc .toc-level-3 { padding-left: 0.75rem; }
.back-to-top { margin-top: 0.7rem; font-weight: 700; }

.home-hero {
  max-width: none;
  padding: clamp(1.5rem, 4vw, 3rem);
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  box-shadow: var(--shadow);
}
.eyebrow, .card-kicker {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.lede { color: var(--muted); font-size: 1.08rem; max-width: 68ch; }
.stat-row { display: flex; flex-wrap: wrap; gap: 0.8rem; margin-top: 1.4rem; }
.stat-row span {
  display: inline-flex;
  gap: 0.35rem;
  align-items: baseline;
  padding: 0.36rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--muted);
  background: var(--surface-soft);
}
.stat-row strong { color: var(--fg); }
.home-index-link { font-weight: 720; }
.branch-section { margin-top: 2.2rem; }
.branch-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 0.95rem; max-width: none; }
.branch-card {
  min-height: 190px;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border: 1px solid var(--border);
  border-top: 4px solid var(--accent);
  border-radius: 8px;
  background: var(--surface);
  color: var(--fg);
  box-shadow: 0 1px 0 rgba(20, 30, 28, 0.03);
}
.branch-card:hover { transform: translateY(-1px); border-color: var(--border-strong); text-decoration: none; box-shadow: var(--shadow); }
.branch-card h3 { margin: 0.35rem 0; font-size: 1.12rem; }
.branch-card p { margin: 0; color: var(--muted); line-height: 1.45; }
.card-meta { margin-top: auto; padding-top: 1rem; color: var(--muted-2); font-size: 0.84rem; font-weight: 700; }
.reference-panel {
  max-width: 980px;
  margin-top: 2.5rem;
  padding: 1.2rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-soft);
}
.reference-list { display: flex; flex-wrap: wrap; gap: 0.45rem; }
.reference-list a {
  padding: 0.3rem 0.55rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  color: var(--fg);
  font-size: 0.88rem;
}
.reference-list a:hover { color: var(--accent); text-decoration: none; }

.accent-sky, .branch-sky { --accent: #27799a; }
.accent-teal, .branch-teal { --accent: #17826d; }
.accent-blue, .branch-blue { --accent: #2d68b2; }
.accent-indigo, .branch-indigo { --accent: #5865b4; }
.accent-cyan, .branch-cyan { --accent: #1f8690; }
.accent-amber, .branch-amber { --accent: #9a6a16; }
.accent-violet, .branch-violet { --accent: #7a5ab5; }
.accent-rose, .branch-rose { --accent: #b25067; }
.accent-orange, .branch-orange { --accent: #ad6432; }
.accent-green, .branch-green { --accent: #2f7b4d; }
.accent-slate, .branch-slate { --accent: #607080; }

.unresolved-link {
  color: #a85d20;
  border-bottom: 1px dashed #a85d20;
  cursor: help;
  background: color-mix(in srgb, #a85d20 10%, transparent);
  border-radius: 4px;
  padding: 0 0.12rem;
}
html[data-theme="dark"] .unresolved-link { color: #ffb072; border-bottom-color: #ffb072; }

@media (max-width: 1120px) {
  .layout { grid-template-columns: var(--sidebar-w) minmax(0, 1fr); }
  .toc { display: none; }
}
@media (max-width: 780px) {
  :root { --topbar-h: 58px; }
  .topbar { grid-template-columns: auto minmax(110px, 1fr) auto; gap: 0.65rem; }
  #sidebar-toggle { display: inline-grid; place-items: center; }
  #theme-toggle { grid-column: 3; grid-row: 1; }
  .search-shell { grid-column: 1 / -1; grid-row: 2; width: 100%; }
  .layout { display: block; }
  .sidebar {
    display: none;
    position: static;
    width: 100%;
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }
  body.nav-open .sidebar { display: block; }
  .content { padding: 1.25rem 1rem 3rem; }
  .home-hero { padding: 1.2rem; }
  .content h1 { font-size: 2rem; }
}
"""

SEARCH_JS = r"""
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
    const hay = (entry.title + " " + entry.branch + " " + entry.group + " " + entry.kind + " " + entry.tags.join(" ") + " " + entry.text).toLowerCase();
    let s = 0;
    for (const t of terms) {
      if (!t) continue;
      if (entry.title.toLowerCase().includes(t)) s += 5;
      if (entry.branch.toLowerCase().includes(t)) s += 3;
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
        `<a class="hit" href="${root}/${h.e.url}"><div class="hit-title">${escapeHtml(h.e.title)}</div><div class="meta">${escapeHtml(h.e.branch)} · ${escapeHtml(h.e.kind)} · ${escapeHtml(h.e.url)}</div></a>`
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
"""


if __name__ == "__main__":
    sys.exit(main())
