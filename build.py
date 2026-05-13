#!/usr/bin/env python3
"""Build a static HTML site from an Obsidian vault.

Walks mature cybersecurity branches under VAULT, converts each .md to .html,
resolves [[wikilinks]] and relative .md links, emits a sidebar and a
client-side search index. No framework, no build step beyond running this.
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from datetime import date
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml

VAULT = Path(os.environ.get("VAULT", "/Users/lautarodamore/obsidian-vault/ldamore"))
OUT = Path(__file__).resolve().parent / "site"
STATIC = Path(__file__).resolve().parent / "static"
SECTIONS = [
    ("cybersecurity", "Cybersecurity"),
]

SITE_NAME = "ldamoredev Security Atlas"
SITE_SHORT_NAME = "Security Atlas"
SITE_AUTHOR = "ldamoredev"
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://ldamoredev.github.io/cibersecurity-notes",
).rstrip("/")

SITE_DESCRIPTION = (
    "A personal cybersecurity knowledge base for web security, API security, "
    "cloud security, offensive security, DevSecOps, and practical playbooks."
)

SITE_KEYWORDS = [
    "cybersecurity",
    "web security",
    "API security",
    "cloud security",
    "offensive security",
    "DevSecOps",
    "security playbooks",
]

THEME_COLOR = "#f0a040"

# Only publish mature cybersecurity branches and their reference registries.
# Keep private/project execution notes, templates, tooling experiments, and
# future/unpromoted branches out of the public static mirror.
BRANCHES = {
    "foundations": {
        "label": "Foundations",
        "group": "Orientation",
        "summary": "Phase 0 mental models — what cybersecurity is, the CIA triad as a decision tool, threat-modeling quickstart, and the attacker-defender duality.",
        "accent": "amber",
    },
    "cryptography": {
        "label": "Cryptography",
        "group": "Substrate",
        "summary": "Hashes, encryption, signatures, key exchange, TLS/PKI, password storage, and token correctness.",
        "accent": "emerald",
    },
    "networking": {
        "label": "Networking",
        "group": "Substrate",
        "summary": "Reachability, HTTP, proxies, DNS, TLS, and packet-level observation.",
        "accent": "sky",
    },
    "wireless-security": {
        "label": "Wireless Security",
        "group": "Specialty",
        "summary": "Wi-Fi frames, handshakes, rogue access points, and local-network MITM.",
        "accent": "teal",
    },
    "web-security": {
        "label": "Web Security",
        "group": "Substrate",
        "summary": "Browser behavior, sessions, access control, and server-side exploit patterns.",
        "accent": "blue",
    },
    "api-security": {
        "label": "API Security",
        "group": "Specialty",
        "summary": "Authorization, token trust, inventory drift, and machine-readable abuse.",
        "accent": "indigo",
    },
    "cloud-security": {
        "label": "Cloud Security",
        "group": "Specialty",
        "summary": "IAM, metadata, storage, network boundaries, secrets, and logging controls.",
        "accent": "cyan",
    },
    "attack-surface-mapping": {
        "label": "Attack Surface Mapping",
        "group": "Operator",
        "summary": "What is exposed, reachable, discoverable, and drifting from intended design.",
        "accent": "amber",
    },
    "osint": {
        "label": "OSINT",
        "group": "Operator",
        "summary": "Public-source collection, evidence quality, and ethical handling of clues.",
        "accent": "violet",
    },
    "offensive-security": {
        "label": "Offensive Security / Recon",
        "group": "Paired",
        "summary": "Discovery, validation, and handoff from recon into concrete testing.",
        "accent": "rose",
    },
    "linux-privilege-escalation": {
        "label": "Linux Privilege Escalation",
        "group": "Operator",
        "summary": "Local boundary failures, enumeration, and safe escalation hypothesis testing.",
        "accent": "orange",
    },
    "privacy-anonymity-opsec": {
        "label": "Privacy, Anonymity & OPSEC",
        "group": "Always-on",
        "summary": "VPN threat models, Tor, metadata leakage, compartmentalization, and OPSEC failure modes.",
        "accent": "purple",
    },
    "devsecops": {
        "label": "DevSecOps",
        "group": "Specialty",
        "summary": "Secure delivery, CI/CD hardening, supply chain, secrets, and release trust.",
        "accent": "green",
    },
    "detection-engineering": {
        "label": "Detection Engineering",
        "group": "Paired",
        "summary": "Telemetry, behavioral analytics, correlation, and detection tradeoffs.",
        "accent": "cyan",
    },
    "identity-and-active-directory": {
        "label": "Identity & Active Directory",
        "group": "Specialty",
        "summary": "Kerberos, BloodHound graph analysis, DCSync, and AD attack-path engineering across offense and defense.",
        "accent": "red",
    },
    "binary-exploitation": {
        "label": "Binary Exploitation",
        "group": "Specialty",
        "summary": "Memory corruption, stack and heap overflows, exploit mitigations, reverse engineering, and the modern exploitation arms race at the binary level.",
        "accent": "fuchsia",
    },
    "security-playbooks": {
        "label": "Security Playbooks",
        "group": "Operator",
        "summary": "Repeatable procedures for turning concepts into practical tests.",
        "accent": "slate",
    },
}

BRANCH_GROUPS = ("Orientation", "Substrate", "Paired", "Operator", "Specialty", "Always-on")
MATURE_CYBERSECURITY_BRANCHES = set(BRANCHES)

MATURE_CYBERSECURITY_ROOT_FILES = {
    "index.md",
    "start-here.md",
    "must-know-30.md",
    "phase-1-substrate.md",
    "phase-2-offense-defense.md",
    "phase-3-operator.md",
    "phase-4-specialty.md",
    "reference-registry.md",
    "reference-registry-api-security.md",
    "reference-registry-cryptography.md",
    "reference-registry-attack-surface-mapping.md",
    "reference-registry-cloud-security.md",
    "reference-registry-devsecops.md",
    "reference-registry-detection-engineering.md",
    "reference-registry-identity-and-active-directory.md",
    "reference-registry-binary-exploitation.md",
    "reference-registry-linux-privilege-escalation.md",
    "reference-registry-networking.md",
    "reference-registry-offensive-security.md",
    "reference-registry-osint.md",
    "reference-registry-privacy-anonymity-opsec.md",
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


def branch_notes(subs: dict[str, list[Note]], slug: str) -> list[Note]:
    """Return published notes for a branch, including its overview index page."""
    return subs.get(slug, [])


def branch_note_count(subs: dict[str, list[Note]], slug: str) -> int:
    """Return the published branch count used by sidebar, homepage, and indexes."""
    return len(branch_notes(subs, slug))


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

        # Root-level entry-layer pages: pedagogical order, not alphabetical.
        root_order = {
            "index": 0,
            "start-here": 1,
            "must-know-30": 2,
            "phase-1-substrate": 3,
            "phase-2-offense-defense": 4,
            "phase-3-operator": 5,
            "phase-4-specialty": 6,
        }
        root_notes = [n for n in subs.get("", []) if not n.slug.startswith("reference-registry")]
        root_notes.sort(key=lambda n: (root_order.get(n.slug, 99), n.title.lower()))
        for n in root_notes:
            # Only the actual `index.md` gets the legacy "Cybersecurity Index"
            # label; entry-layer pages use their real title.
            label = "Cybersecurity Index" if n.slug == "index" else None
            lines.append(render_sidebar_link(n, current, label=label))

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
    notes = branch_notes(subs, sub)
    index_note = next((n for n in notes if n.slug == "index"), None)
    summary = branch_summary(sub)
    accent = branch_accent(sub)
    lines.append(
        f'<details class="branch branch-{html.escape(accent)}"{open_attr}>'
        f'<summary><span>{html.escape(branch_label(sub))}</span><small>{branch_note_count(subs, sub)}</small></summary>'
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


def reading_time_minutes(note: Note) -> int:
    if page_kind(note) in {"index", "registry"}:
        return 0
    text = FRONTMATTER_RE.sub("", note.body_md, count=1)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1).split("/")[-1], text)
    words = len(re.findall(r"\w+", text))
    return max(1, round(words / 220))


def format_lastmod_human(iso_date: str) -> str:
    try:
        d = date.fromisoformat(iso_date)
    except ValueError:
        return iso_date
    return d.strftime("%b %d, %Y")


def page_meta_html(note: Note) -> str:
    branch = branch_slug(note)
    chips = [f'<span class="meta-chip">{html.escape(page_kind(note))}</span>']
    if branch:
        chips.append(f'<span class="meta-chip accent-{html.escape(branch_accent(branch))}">{html.escape(branch_label(branch))}</span>')
    minutes = reading_time_minutes(note)
    if minutes:
        chips.append(f'<span class="meta-chip meta-time" title="Estimated reading time">~{minutes} min read</span>')
    if page_kind(note) in {"concept", "playbook"}:
        updated = format_lastmod_human(note_last_modified(note))
        chips.append(f'<span class="meta-chip meta-updated" title="Last updated">Updated {html.escape(updated)}</span>')
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


def root_asset(root_href: str, path: str) -> str:
    base = root_href if root_href else "."
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def absolute_site_url(path: str) -> str:
    return f"{SITE_URL}/{path.lstrip('/')}"


def note_last_modified(note: Note) -> str:
    source = VAULT / note.rel_path
    try:
        ts = source.stat().st_mtime
    except OSError:
        ts = date.today()
        return ts.isoformat()
    return date.fromtimestamp(ts).isoformat()


def canonical_url(note: Note) -> str:
    if note.section == "" and note.rel_path == Path("index.md"):
        return SITE_URL + "/"
    return absolute_site_url(note.url)


def page_title(note: Note) -> str:
    label = note_label(note)
    branch = branch_slug(note)

    if note.section == "" and note.rel_path == Path("index.md"):
        return f"Cybersecurity Notes Index | {SITE_NAME}"
    if page_kind(note) == "index" and branch:
        return f"{branch_label(branch)} Notes | {SITE_NAME}"
    if page_kind(note) == "registry":
        return f"{label} | {SITE_NAME}"
    if branch:
        return f"{label} - {branch_label(branch)} | {SITE_NAME}"
    return f"{label} | {SITE_NAME}"


def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def first_content_paragraph(md_text: str) -> str:
    cleaned = FRONTMATTER_RE.sub("", md_text, count=1)
    cleaned = re.sub(r"```.*?```", " ", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", cleaned)
    cleaned = WIKILINK_RE.sub(
        lambda m: m.group(2) or m.group(1).split("/")[-1],
        cleaned,
    )
    cleaned = re.sub(r"^#{1,6}\s+.*$", "", cleaned, flags=re.MULTILINE)

    for block in re.split(r"\n\s*\n", cleaned):
        block = normalize_ws(block)
        if not block or block.startswith("#") or block.startswith("---"):
            continue
        block = re.sub(r"^[-*+]\s+", "", block)
        block = re.sub(r"^>\s*", "", block)
        block = TAG_RE.sub(r"\1", block)
        block = normalize_ws(block)
        if len(block) >= 40:
            return block
    return ""


def truncate_description(value: str, limit: int = 165) -> str:
    value = normalize_ws(strip_html(value))
    if len(value) <= limit:
        return value
    clipped = value[: limit - 1]
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped.rstrip(".,;:-") + "..."


def note_description(note: Note) -> str:
    fm_description = note.frontmatter.get("description") or note.frontmatter.get("summary")
    if isinstance(fm_description, str) and fm_description.strip():
        return truncate_description(fm_description)
    if note.section == "" and note.rel_path == Path("index.md"):
        return SITE_DESCRIPTION

    branch = branch_slug(note)
    if page_kind(note) == "index" and branch:
        return truncate_description(f"{branch_label(branch)} notes: {branch_summary(branch)}")

    para = first_content_paragraph(note.body_md)
    if para:
        return truncate_description(para)
    if branch:
        return truncate_description(
            f"{note_label(note)} in the {branch_label(branch)} branch of the ldamoredev cybersecurity knowledge base."
        )
    return SITE_DESCRIPTION


def page_keywords(note: Note) -> list[str]:
    keywords = list(SITE_KEYWORDS)
    branch = branch_slug(note)
    if branch:
        keywords.append(branch_label(branch))
    keywords.append(note_label(note))
    keywords.extend(note.tags)

    seen: set[str] = set()
    result: list[str] = []
    for k in keywords:
        k = str(k).strip().lstrip("#")
        key = k.lower()
        if k and key not in seen:
            seen.add(key)
            result.append(k)
    return result[:14]


def breadcrumb_items(note: Note) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = [("Home", absolute_site_url("index.html"))]
    if note.rel_path.parts and note.rel_path.parts[0] == "cybersecurity":
        items.append(("Cybersecurity", absolute_site_url("cybersecurity/index.html")))
    branch = branch_slug(note)
    if branch:
        items.append((branch_label(branch), absolute_site_url(f"cybersecurity/{branch}/index.html")))
    if not (note.section == "" and note.rel_path == Path("index.md")):
        items.append((note_label(note), canonical_url(note)))
    return items


def json_ld_for(note: Note) -> str:
    description = note_description(note)
    canonical = canonical_url(note)
    title = page_title(note)
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": url,
            }
            for i, (name, url) in enumerate(breadcrumb_items(note))
        ],
    }

    site_ref = {"@type": "WebSite", "@id": SITE_URL + "/#website", "name": SITE_NAME, "url": SITE_URL + "/"}
    author_ref = {"@type": "Person", "@id": SITE_URL + "/#author", "name": SITE_AUTHOR}
    if note.section == "" and note.rel_path == Path("index.md"):
        page = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "name": SITE_NAME,
            "url": SITE_URL + "/",
            "description": SITE_DESCRIPTION,
            "inLanguage": "en",
            "author": author_ref,
        }
    elif page_kind(note) == "index":
        last_modified = note_last_modified(note)
        page = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "@id": canonical + "#page",
            "name": title,
            "headline": note_label(note),
            "description": description,
            "url": canonical,
            "inLanguage": "en",
            "dateModified": last_modified,
            "isPartOf": site_ref,
            "author": author_ref,
        }
    else:
        last_modified = note_last_modified(note)
        page = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": canonical + "#article",
            "name": title,
            "headline": note_label(note),
            "description": description,
            "url": canonical,
            "inLanguage": "en",
            "datePublished": last_modified,
            "dateModified": last_modified,
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "isPartOf": site_ref,
            "author": author_ref,
            "keywords": page_keywords(note),
        }
    return json.dumps([page, breadcrumb], ensure_ascii=False, separators=(",", ":"))


def seo_head(note: Note, root_href: str) -> str:
    title = page_title(note)
    description = note_description(note)
    canonical = canonical_url(note)
    og_image = absolute_site_url("assets/og-image.png")
    kind = "article" if page_kind(note) in {"concept", "playbook", "registry"} else "website"
    lines = [
        f'<title>{html.escape(title)}</title>',
        f'<meta name="description" content="{html.escape(description)}">',
        f'<meta name="author" content="{html.escape(SITE_AUTHOR)}">',
        f'<meta name="keywords" content="{html.escape(", ".join(page_keywords(note)))}">',
        f'<meta name="theme-color" content="{THEME_COLOR}">',
        '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">',
        '<meta name="googlebot" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">',
        f'<link rel="canonical" href="{html.escape(canonical)}">',
        f'<link rel="icon" href="{html.escape(root_asset(root_href, "favicon.ico"))}" sizes="any">',
        f'<link rel="icon" href="{html.escape(root_asset(root_href, "favicon.svg"))}" type="image/svg+xml">',
        f'<link rel="apple-touch-icon" href="{html.escape(root_asset(root_href, "apple-touch-icon.png"))}">',
        f'<link rel="manifest" href="{html.escape(root_asset(root_href, "site.webmanifest"))}">',
        f'<meta property="og:site_name" content="{html.escape(SITE_NAME)}">',
        '<meta property="og:locale" content="en_US">',
        f'<meta property="og:type" content="{kind}">',
        f'<meta property="og:title" content="{html.escape(title)}">',
        f'<meta property="og:description" content="{html.escape(description)}">',
        f'<meta property="og:url" content="{html.escape(canonical)}">',
        f'<meta property="og:image" content="{html.escape(og_image)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{html.escape(SITE_NAME)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(title)}">',
        f'<meta name="twitter:description" content="{html.escape(description)}">',
        f'<meta name="twitter:image" content="{html.escape(og_image)}">',
        f'<script type="application/ld+json">{json_ld_for(note).replace("</", "<\\/")}</script>',
    ]
    branch = branch_slug(note)
    if branch:
        lines.insert(12, f'<meta property="article:section" content="{html.escape(branch_label(branch))}">')
    return "\n".join(lines)


def branch_nav_html(note: Note, all_notes: list[Note]) -> str:
    if page_kind(note) not in {"concept", "playbook"}:
        return ""
    branch = branch_slug(note)
    if not branch:
        return ""
    here = note.out_path.parent

    siblings = sorted(
        [
            n for n in all_notes
            if branch_slug(n) == branch and page_kind(n) in {"concept", "playbook"}
        ],
        key=lambda n: n.title.lower(),
    )
    try:
        idx = next(i for i, n in enumerate(siblings) if n.rel_path == note.rel_path)
    except StopIteration:
        return ""

    prev_note = siblings[idx - 1] if idx > 0 else None
    next_note = siblings[idx + 1] if idx + 1 < len(siblings) else None
    if not prev_note and not next_note:
        return ""

    parts = ['<nav class="branch-nav" aria-label="Within this branch">']
    if prev_note:
        href = os.path.relpath(prev_note.out_path, here)
        parts.append(
            f'<a class="branch-nav-link prev" href="{html.escape(href)}">'
            '<span class="nav-dir">← Previous</span>'
            f'<strong>{html.escape(note_label(prev_note))}</strong>'
            '</a>'
        )
    else:
        parts.append('<span class="branch-nav-spacer"></span>')
    if next_note:
        href = os.path.relpath(next_note.out_path, here)
        parts.append(
            f'<a class="branch-nav-link next" href="{html.escape(href)}">'
            '<span class="nav-dir">Next →</span>'
            f'<strong>{html.escape(note_label(next_note))}</strong>'
            '</a>'
        )
    parts.append('</nav>')
    return "".join(parts)


def related_notes_html(note: Note, all_notes: list[Note]) -> str:
    if page_kind(note) not in {"concept", "playbook"}:
        return ""

    branch = branch_slug(note)
    here = note.out_path.parent
    note_tags = set(t.lower() for t in note.tags)
    candidates: list[tuple[int, str, Note]] = []

    for other in all_notes:
        if other.rel_path == note.rel_path or page_kind(other) in {"index", "registry"}:
            continue
        score = 0
        if branch and branch_slug(other) == branch:
            score += 5
        if branch and branch_group(branch_slug(other)) == branch_group(branch):
            score += 1
        shared_tags = note_tags.intersection(t.lower() for t in other.tags)
        score += len(shared_tags) * 3
        if score:
            candidates.append((score, other.title.lower(), other))
    if not candidates:
        return ""

    lines = [
        '<section class="related-notes" aria-label="Explore nearby notes">',
        "<h2>Explore nearby notes</h2>",
        '<div class="related-grid">',
    ]
    for _, _, other in sorted(candidates, key=lambda x: (-x[0], x[1]))[:6]:
        href = os.path.relpath(other.out_path, here)
        branch_name = branch_label(branch_slug(other)) if branch_slug(other) else "Cybersecurity"
        desc = note_description(other)
        lines.append(
            f'<a class="related-card" href="{html.escape(href)}">'
            f'<span>{html.escape(branch_name)}</span>'
            f'<strong>{html.escape(note_label(other))}</strong>'
            f'<small>{html.escape(desc)}</small>'
            "</a>"
        )
    lines.append("</div></section>")
    return "\n".join(lines)


def xml_escape(value: str) -> str:
    return html.escape(value, quote=True)


def write_sitemap(notes: list[Note]) -> None:
    today = date.today().isoformat()
    entries: dict[str, str] = {absolute_site_url("index.html"): today}
    for n in notes:
        entries[canonical_url(n)] = note_last_modified(n)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in sorted(entries):
        lines.append("  <url>")
        lines.append(f"    <loc>{xml_escape(url)}</loc>")
        lines.append(f"    <lastmod>{entries[url]}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>\n")
    (OUT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def write_robots() -> None:
    (OUT / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {absolute_site_url('sitemap.xml')}\n",
        encoding="utf-8",
    )


def write_manifest() -> None:
    manifest = {
        "name": SITE_NAME,
        "short_name": SITE_SHORT_NAME,
        "description": SITE_DESCRIPTION,
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#111416",
        "theme_color": THEME_COLOR,
        "icons": [
            {"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    (OUT / "site.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def copy_static_assets() -> None:
    if not STATIC.exists():
        return
    for path in STATIC.rglob("*"):
        if path.is_dir():
            continue
        target = OUT / path.relative_to(STATIC)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{seo_head}
<script>(function(){{try{{var t=localStorage.getItem('theme');if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();</script>
<link rel="stylesheet" href="{css_href}">
<link rel="stylesheet" href="{pygments_href}">
</head>
<body id="top" data-root="{root_href}">
<header class="topbar">
  <a class="brand" href="{home_href}"><span class="brand-mark">⌬</span><span>ldamoredev<span class="brand-slash">/</span><span class="brand-sub">atlas</span></span></a>
  <div class="topbar-search search-shell">
    <svg class="search-ico" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l3 3"/></svg>
    <input id="search" type="search" placeholder="Search notes, jump anywhere..." autocomplete="off">
    <kbd>/</kbd>
  </div>
  <div class="topbar-actions">
    <button id="sidebar-toggle" class="icon-btn menu-toggle" title="Toggle navigation" aria-label="Toggle navigation"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h12"/></svg></button>
    <button id="theme-toggle" class="icon-btn" title="Toggle theme" aria-label="Toggle theme"><svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 1a7 7 0 100 14V1z"/></svg></button>
    <a class="icon-btn github-link" href="https://github.com/ldamoredev/cibersecurity-notes" target="_blank" rel="noopener" aria-label="GitHub"><svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8a8 8 0 005.47 7.59c.4.07.55-.17.55-.38v-1.32C3.73 14.37 3.26 13 3.26 13c-.36-.92-.88-1.16-.88-1.16-.72-.49.06-.48.06-.48.79.06 1.21.81 1.21.81.71 1.21 1.86.86 2.31.66.07-.51.28-.86.5-1.06-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.35-1.02.08-2.13 0 0 .67-.21 2.2.82a7.6 7.6 0 014 0c1.53-1.03 2.2-.82 2.2-.82.43 1.11.16 1.93.08 2.13.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48v2.2c0 .21.15.46.55.38A8 8 0 0016 8c0-4.42-3.58-8-8-8z"/></svg></a>
  </div>
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


def render_page(
    note: Note,
    html_body: str,
    sidebar_html: str,
    tree: dict,
    all_notes: list[Note] | None = None,
) -> str:
    here = note.out_path.parent
    css_href = os.path.relpath(OUT / "assets" / "style.css", here)
    pyg_href = os.path.relpath(OUT / "assets" / "pygments.css", here)
    search_js = os.path.relpath(OUT / "assets" / "search.js", here)
    home_href = os.path.relpath(OUT / "index.html", here)
    root_href = os.path.relpath(OUT, here) or "."

    toc_html = "" if note.section == "" else render_toc(html_body)
    nav_html = branch_nav_html(note, all_notes or [])
    related_html = related_notes_html(note, all_notes or [])
    article_body = html_body
    if nav_html:
        article_body += "\n" + nav_html
    if related_html:
        article_body += "\n" + related_html
    return PAGE_TEMPLATE.format(
        seo_head=seo_head(note, root_href),
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
        body=article_body,
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
    playbook_count = branch_note_count(subs, "security-playbooks") if "security-playbooks" in subs else 0
    repo_url = "https://github.com/ldamoredev/cibersecurity-notes"
    lines = [
        '<section class="hero home-hero">',
        '<div class="hero-kicker">PERSONAL CYBERSECURITY REFERENCE · v2026.05</div>',
        '<h1>Notes from the <br class="mobile-break"><em>actual practice</em><br>of attacking and<br class="mobile-break"> defending systems.</h1>',
        f'<p class="lede">An atomic, retrievable knowledge base — <strong>{published_notes} notes across {len(BRANCHES)} branches</strong>, structured around the path from <em>substrate</em> to <em>specialty</em>. Each entry is a single concept, with attacker/defender duality, references, and links to playbooks that turn it into action.</p>',
        '<div class="hero-stats">',
        f'<div class="hero-stat"><div class="v">{published_notes}</div><div class="l">Atomic notes</div></div>',
        f'<div class="hero-stat"><div class="v">{len(BRANCHES)}</div><div class="l">Branches</div></div>',
        f'<div class="hero-stat"><div class="v">{playbook_count}</div><div class="l">Playbooks</div></div>',
        '<div class="hero-stat"><div class="v">5<small>phases</small></div><div class="l">Learning path</div></div>',
        f'<div class="hero-stat"><div class="v">{registry_count}</div><div class="l">Registries</div></div>',
        '</div>',
        '</section>',
        '<a class="continue" href="cybersecurity/web-security/xss.html">',
        '<div class="continue-meta"><div class="continue-eyebrow"><span class="pulse"></span>Featured note · Web Security</div><div class="continue-title">Cross-Site Scripting (XSS)</div><div class="continue-progress"><span>Operational note</span><span class="bar"><i style="width:62%"></i></span><span>Contexts, payloads, defenses</span></div></div>',
        '<span class="continue-action">Open →</span>',
        '</a>',
        '<section class="path-section" id="start-here">',
        '<div class="section-head"><div><div class="section-eyebrow">START → CAPABLE</div><h2>The five-phase learning path</h2><p>Do not read folder-by-folder. Read in phases: each one is a prerequisite layer for the next. Pick where you are, then walk forward.</p></div><a href="cybersecurity/start-here.html" class="section-head-action">Open Start Here →</a></div>',
        '<div class="phase-grid">',
        '<a class="phase-card" href="cybersecurity/foundations/index.html"><span>00</span><strong>Orientation</strong><small>Mental models, CIA tradeoffs, and threat modeling.</small></a>',
        '<a class="phase-card" href="cybersecurity/phase-1-substrate.html"><span>01</span><strong>Substrate</strong><small>Networking, cryptography, browser trust, and system behavior.</small></a>',
        '<a class="phase-card" href="cybersecurity/phase-2-offense-defense.html"><span>02</span><strong>Offense / Defense</strong><small>Paired attack and detection thinking.</small></a>',
        '<a class="phase-card" href="cybersecurity/phase-3-operator.html"><span>03</span><strong>Operator Surface</strong><small>Recon, exposure, and practical execution workflows.</small></a>',
        '<a class="phase-card" href="cybersecurity/phase-4-specialty.html"><span>04</span><strong>Specialty Tracks</strong><small>Cloud, identity, DevSecOps, wireless, and binary exploitation.</small></a>',
        '</div></section>',
    ]
    for group in BRANCH_GROUPS:
        group_slugs = [slug for slug in BRANCHES if slug in subs and branch_group(slug) == group]
        if not group_slugs:
            continue
        lines.append(f'<section class="branch-section"><div class="section-head compact"><div><div class="section-eyebrow">{html.escape(group)}</div><h2>{html.escape(group)} branches</h2></div></div><div class="branch-grid">')
        for slug in group_slugs:
            notes_for_branch = branch_notes(subs, slug)
            index_note = next((n for n in notes_for_branch if n.slug == "index"), notes_for_branch[0])
            href = index_note.url
            accent = branch_accent(slug)
            published_count = branch_note_count(subs, slug)
            lines.append(f'<a class="branch-card accent-{html.escape(accent)}" href="{html.escape(href)}"><span class="card-kicker">{html.escape(group)}</span><h3>{html.escape(branch_label(slug))}</h3><p>{html.escape(branch_summary(slug))}</p><span class="card-meta">{published_count} notes</span></a>')
        lines.append('</div></section>')
    registry_notes = [n for n in subs.get("", []) if n.slug.startswith("reference-registry")]
    if registry_notes:
        lines.append('<section class="reference-panel" id="registries"><div class="section-eyebrow">Reference system</div><h2>Reference registries</h2><p>The registries keep citations normalized behind the learning branches, so atomic notes stay compact and high-signal.</p><div class="reference-list">')
        for n in registry_notes:
            lines.append(f'<a href="{html.escape(n.url)}">{html.escape(note_label(n))}</a>')
        lines.append('</div></section>')
    lines.extend(['<footer class="home-footer"><div class="footer-about"><strong>ldamoredev/atlas</strong><p>A personal cybersecurity knowledge base, published from an Obsidian vault as a static operator reference.</p></div><div class="footer-links">', f'<a href="{repo_url}" rel="noopener" target="_blank">GitHub</a>', '<a href="cybersecurity/start-here.html">Start Here</a>', '<a href="cybersecurity/index.html">Full index</a>', '</div></footer>'])
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
        page = render_page(n, body_html, sidebar_html, tree, notes)
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
            "description": note_description(n),
            "keywords": page_keywords(n),
            "text": strip_html(body_html)[:2000],
        })

    # Home page.
    home_note = Note(section="", rel_path=Path("index.md"), title="ldamoredev notes", slug="index", body_md="")
    home_body = build_home(tree, notes)
    sidebar_html = render_sidebar(tree, home_note)
    (OUT / "index.html").write_text(
        render_page(home_note, home_body, sidebar_html, tree, notes),
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
    copy_static_assets()
    write_manifest()
    write_sitemap(notes)
    write_robots()

    print(f"Wrote {len(notes) + 1} pages to {OUT} (unresolved wikilinks: {broken_total})")
    return 0


STYLE_CSS = r"""
@import url("atlas.css");

/* Compatibility layer for generated Obsidian pages using the Atlas design. */
.search-shell { position: relative; }
.mobile-break { display: none; }
.search-shell input { width: 100%; height: 36px; padding: 0 3rem 0 2.25rem; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); color: var(--fg); font: inherit; outline: none; }
.search-shell input::placeholder { color: var(--muted); }
.search-shell input:focus { border-color: var(--accent-line); box-shadow: 0 0 0 3px var(--accent-soft); }
.search-ico { position: absolute; left: .85rem; top: 50%; transform: translateY(-50%); color: var(--muted-2); pointer-events: none; }
.search-shell kbd { position: absolute; right: .55rem; top: 50%; transform: translateY(-50%); font-family: var(--font-mono); font-size: .72rem; color: var(--muted); background: var(--panel-2); border: 1px solid var(--border); border-radius: 4px; padding: 1px 6px; }
#sidebar-toggle { display: none; }
.github-link:hover { text-decoration: none; }
.article-home { max-width: 1180px; }
.article-note, .page-hero, .breadcrumbs { max-width: 78ch; }
.breadcrumbs { display: flex; flex-wrap: wrap; gap: .35rem; align-items: center; margin-bottom: .85rem; color: var(--muted); font: .8rem/1.4 var(--font-mono); }
.breadcrumbs a { color: var(--muted); }
.breadcrumbs span:last-child { color: var(--fg-soft); }
.page-hero { margin-bottom: .8rem; }
.page-meta { display: flex; flex-wrap: wrap; gap: .4rem; }
.meta-chip { display: inline-flex; align-items: center; min-height: 24px; padding: .12rem .55rem; border: 1px solid var(--border); border-radius: 999px; color: var(--muted); background: var(--panel); font: 600 .74rem/1.3 var(--font-mono); text-transform: capitalize; }
.meta-chip.tag, .meta-chip[class*="accent-"] { color: var(--accent); background: var(--accent-soft); border-color: transparent; }
.content h1 { margin: .35rem 0 1rem; font-size: clamp(2rem, 3.2vw, 3.15rem); line-height: 1.08; letter-spacing: 0; }
.content h2 { margin-top: 2.35rem; padding-bottom: .32rem; border-bottom: 1px solid var(--border); font-size: 1.42rem; line-height: 1.25; }
.content h3 { margin-top: 1.55rem; font-size: 1.06rem; }
.content p { margin: 1rem 0; }
.content p, .content li { color: var(--fg-soft); }
.content ul, .content ol { padding-left: 1.35rem; }
.content blockquote { border-left: 4px solid var(--accent); margin: 1.25rem 0; padding: .75rem 1rem; color: var(--muted); background: var(--panel-2); border-radius: 0 8px 8px 0; }
.content code { background: var(--panel-2); padding: .1rem .36rem; border-radius: 5px; font-size: .9em; font-family: var(--font-mono); }
.content pre { background: var(--panel-2); padding: 1rem; border: 1px solid var(--border); border-radius: 8px; overflow-x: auto; font-size: .88em; }
.content pre code { background: transparent; padding: 0; }
.content table { border-collapse: collapse; margin: 1.2rem 0; width: 100%; font-size: .94rem; }
.content th, .content td { border: 1px solid var(--border); padding: .48rem .7rem; text-align: left; vertical-align: top; }
.content th { background: var(--panel-2); color: var(--fg); }
.sidebar-home { display: block; margin: 0 0 .55rem; padding: .45rem .55rem; border-radius: 7px; background: var(--panel-2); border: 1px solid var(--border); color: var(--fg); font-family: var(--font-mono); font-size: .78rem; font-weight: 600; }
.sidebar-section h3, .sidebar-group-label { margin: .95rem 0 .35rem; padding: .4rem .55rem; color: var(--muted-2); font: 600 .68rem/1.2 var(--font-mono); text-transform: uppercase; letter-spacing: .1em; }
.sidebar-section h3 { margin-top: 0; border-bottom: 1px solid var(--border); }
.sidebar details.branch > summary { border-left: 3px solid var(--accent); }
.sidebar summary { list-style: none; }
.sidebar summary::-webkit-details-marker { display: none; }
.sidebar-summary { margin: .2rem .55rem .45rem .75rem; color: var(--muted); font-size: .8rem; line-height: 1.4; }
.sidebar-link { display: block; margin: .05rem 0 .05rem .78rem; padding: .31rem .55rem; border-radius: 6px; color: var(--muted); line-height: 1.35; }
.sidebar-link:hover { background: var(--panel); color: var(--fg); text-decoration: none; }
.sidebar-link.active { background: var(--accent-soft); color: var(--accent); font-weight: 700; box-shadow: inset 2px 0 0 var(--accent); }
.toc { padding: 2.4rem 1.2rem 2rem 0; }
.toc-inner { position: sticky; top: calc(var(--topbar-h) + 1.2rem); max-height: calc(100vh - var(--topbar-h) - 2rem); overflow: auto; border-left: 1px solid var(--border); padding-left: 1rem; }
.toc h2 { margin: 0 0 .65rem; color: var(--muted-2); font: 600 .72rem/1.2 var(--font-mono); text-transform: uppercase; letter-spacing: .1em; }
.toc a { display: block; padding: .18rem 0; color: var(--muted); font-size: .84rem; line-height: 1.35; }
.toc a:hover { color: var(--accent); text-decoration: none; }
.path-section, .branch-section, .reference-panel { margin-top: 2.4rem; }
.section-head { display: flex; justify-content: space-between; align-items: end; gap: 1.5rem; margin-bottom: 1rem; }
.section-head.compact { margin-bottom: .75rem; }
.phase-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .75rem; }
.phase-card { display: grid; grid-template-rows: auto auto 1fr; gap: .4rem; min-height: 170px; padding: 1rem; border: 1px solid var(--border); border-radius: 8px; background: var(--panel); color: var(--fg); }
.phase-card:hover { text-decoration: none; border-color: var(--border-strong); transform: translateY(-1px); box-shadow: var(--shadow-1); }
.phase-card span { color: var(--accent); font: 700 .82rem/1 var(--font-mono); }
.phase-card small { color: var(--muted); line-height: 1.45; }
.continue-action { font-family: var(--font-mono); color: var(--accent); font-size: .85rem; white-space: nowrap; }
.branch-card { transition: transform 100ms ease, border-color 120ms ease, box-shadow 140ms ease; }
.related-notes { margin-top: 3rem; padding-top: 1.4rem; border-top: 1px solid var(--border); }
.related-grid, .branch-nav { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .85rem; }
.related-card, .branch-nav-link { border: 1px solid var(--border); border-radius: 8px; background: var(--panel); color: var(--fg); padding: .95rem 1rem; }
.related-card:hover, .branch-nav-link:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow-1); }
.branch-nav { margin-top: 3rem; padding-top: 1.4rem; border-top: 1px solid var(--border); }
.branch-nav-link { display: flex; flex-direction: column; gap: .25rem; line-height: 1.35; }
.branch-nav-link.next { text-align: right; align-items: flex-end; }
.nav-dir, .related-card span { color: var(--accent); font: 700 .72rem/1.2 var(--font-mono); text-transform: uppercase; letter-spacing: .08em; }
.unresolved-link { color: var(--crit); border-bottom: 1px dashed var(--crit); cursor: help; background: var(--crit-soft); border-radius: 4px; padding: 0 .12rem; }
#search-results {
  position: fixed;
  top: calc(var(--topbar-h) + 10px);
  left: 50%;
  transform: translateX(-50%);
  width: min(720px, calc(100vw - 2rem));
  max-height: min(68vh, 760px);
  overflow: auto;
  padding: .45rem;
  z-index: 60;
  background: var(--panel);
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  box-shadow: var(--shadow-2);
}
#search-results[hidden] { display: none !important; }
#search-results .results-meta {
  padding: .45rem .85rem .6rem;
  margin-bottom: .25rem;
  border-bottom: 1px solid var(--border);
  color: var(--muted-2);
  font: 600 .74rem/1.2 var(--font-mono);
}
#search-results .hit {
  display: block;
  padding: .75rem .85rem;
  border-radius: 8px;
  color: var(--fg);
}
#search-results .hit:hover,
#search-results .hit.active {
  background: var(--panel-2);
  text-decoration: none;
}
#search-results .hit.active { outline: 1px solid var(--accent-line); }
#search-results .hit-title { color: var(--fg); font-weight: 700; }
#search-results .meta { margin-top: .12rem; color: var(--muted); font-size: .82rem; }
#search-results .empty { padding: .8rem; color: var(--muted); }
#search-results mark {
  background: var(--accent-soft);
  color: var(--fg);
  border-radius: 2px;
  padding: 0 1px;
}
#search-results .hit p { margin: .25rem 0 0; color: var(--muted); font-size: .86rem; line-height: 1.45; }
@media (max-width: 780px) {
  #search-results { top: 96px; width: calc(100vw - 1.5rem); max-height: 70vh; }
}
@media (max-width: 1180px) { .phase-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 860px) { .section-head { display: block; } .github-link { display: none; } .related-grid, .branch-nav { grid-template-columns: 1fr; } .branch-nav-link.next { text-align: left; align-items: flex-start; } }
@media (max-width: 780px) { html, body { overflow-x: hidden; max-width: 100vw; } .topbar { grid-template-columns: auto minmax(0, 1fr) auto; height: auto; min-height: 56px; padding: .55rem .75rem; } #sidebar-toggle { display: grid; grid-column: 1; grid-row: 1; } .brand { grid-column: 2; grid-row: 1; min-width: 0; overflow: hidden; } .brand-sub { display: none; } .topbar-actions { grid-column: 3; grid-row: 1; } .topbar-search { grid-column: 1 / -1; grid-row: 2; width: 100%; } .layout { display: block; } .sidebar { display: none; position: static; height: auto; max-height: none; border-right: 0; border-bottom: 1px solid var(--border); } body.nav-open .sidebar { display: block; } .layout, .content, .article-home, .hero, .home-hero { max-width: 100vw !important; } .content { width: 100vw; padding: 1.25rem 1rem 3rem; overflow: visible; } .hero, .home-hero { padding-top: 1.1rem; } .hero h1, .home-hero h1 { width: 22rem !important; max-width: calc(100vw - 2rem) !important; font-size: 1.75rem; overflow-wrap: break-word; word-break: normal; } .mobile-break { display: block; } .hero .lede, .lede { width: 22rem; max-width: calc(100vw - 2rem) !important; overflow-wrap: break-word; } .hero-stats { grid-template-columns: 1fr; } .continue { align-items: flex-start; flex-direction: column; } .phase-grid { grid-template-columns: 1fr; } }
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

  const activeLink = document.querySelector(".sidebar .sidebar-link.active");
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
"""


if __name__ == "__main__":
    sys.exit(main())
