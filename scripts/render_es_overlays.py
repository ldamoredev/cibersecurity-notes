#!/usr/bin/env python3
"""Render Spanish overlays into the already-generated site/es tree.

The canonical build needs the Obsidian vault, which is not always available on
this mirror machine. This script is a narrow fallback for i18n publishing:

  * read translations/es/<rel>.md
  * render the note body with a small dependency-free Markdown renderer
  * replace only the note body in site/es/<rel>.html
  * preserve build-generated chrome: sidebar, breadcrumbs, prev/next, related
  * refresh site/es/search.json for translated pages

It does not replace build.py. Run the real build on the vault machine whenever
the English source or site structure changes.
"""
from __future__ import annotations

import argparse
import html
import json
import posixpath
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS = ROOT / "translations" / "es"
SITE_ES = ROOT / "site" / "es"

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.S)
ARTICLE_RE = re.compile(r"(<article[^>]*>)(.*?)(</article>)", re.S)
FOOTER_RE = re.compile(r'<nav class="branch-nav"|<section class="related-notes"')
TOC_RE = re.compile(
    r'(<aside class="toc"[^>]*><div class="toc-inner"><h2>.*?</h2>)(.*?)(<a class="back-to-top"[^>]*>.*?</a></div></aside>)',
    re.S,
)
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+(?:#[^\]\|]+)?)(?:\|([^\]]+))?\]\]")
MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ENTRY_LAYER_SLUGS = (
    "start-here",
    "must-know-30",
    "phase-1-substrate",
    "phase-2-offense-defense",
    "phase-3-operator",
    "phase-4-specialty",
)


def slugify(text: str) -> str:
    text = html.unescape(strip_md(text)).lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "section"


def strip_frontmatter(md: str) -> str:
    return FRONTMATTER_RE.sub("", md, count=1).lstrip()


def strip_md(text: str) -> str:
    text = re.sub(r"\[\[([^\]\|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`]+", "", text)
    return text


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def html_text(fragment: str) -> str:
    p = TextExtractor()
    p.feed(fragment)
    return p.text()


class MarkdownRenderer:
    def __init__(self, current_html: Path, slug_index: dict[str, list[Path]]) -> None:
        self.current_html = current_html
        self.current_rel = current_html.relative_to(SITE_ES)
        self.slug_index = slug_index

    def render(self, md: str) -> str:
        lines = strip_frontmatter(md).splitlines()
        return "\n".join(self._render_blocks(lines)).strip() + "\n"

    def _render_blocks(self, lines: list[str]) -> list[str]:
        out: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue

            if line.startswith("```"):
                code: list[str] = []
                i += 1
                while i < len(lines) and not lines[i].startswith("```"):
                    code.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1
                out.append(self._code_block("\n".join(code)))
                continue

            heading = HEADING_RE.match(line)
            if heading:
                level = len(heading.group(1))
                text = heading.group(2).strip()
                out.append(f'<h{level} id="{slugify(text)}">{self.inline(text)}</h{level}>')
                i += 1
                continue

            if re.match(r"^\s*---+\s*$", line):
                out.append("<hr>")
                i += 1
                continue

            if line.startswith(">"):
                block: list[str] = []
                while i < len(lines) and (lines[i].startswith(">") or not lines[i].strip()):
                    if lines[i].startswith(">"):
                        block.append(re.sub(r"^>\s?", "", lines[i]))
                    else:
                        block.append("")
                    i += 1
                inner = "\n".join(self._render_blocks(block))
                out.append(f"<blockquote>\n{inner}\n</blockquote>")
                continue

            if self._is_table_start(lines, i):
                table_lines: list[str] = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                out.append(self._table(table_lines))
                continue

            if LIST_RE.match(line):
                list_lines: list[str] = []
                while i < len(lines):
                    cur = lines[i]
                    if not cur.strip():
                        if i + 1 < len(lines) and LIST_RE.match(lines[i + 1]):
                            i += 1
                            continue
                        break
                    if LIST_RE.match(cur) or cur.startswith((" ", "\t")):
                        list_lines.append(cur)
                        i += 1
                        continue
                    break
                out.append(self._list(list_lines))
                continue

            para: list[str] = [line]
            i += 1
            while i < len(lines) and lines[i].strip():
                nxt = lines[i]
                if (
                    nxt.startswith("```")
                    or HEADING_RE.match(nxt)
                    or nxt.startswith(">")
                    or LIST_RE.match(nxt)
                    or self._is_table_start(lines, i)
                    or re.match(r"^\s*---+\s*$", nxt)
                ):
                    break
                para.append(nxt)
                i += 1
            out.append(f"<p>{self.inline(' '.join(p.strip() for p in para))}</p>")
        return out

    def _code_block(self, code: str) -> str:
        escaped = html.escape(code)
        return f'<div class="codehilite"><pre><span></span><code>{escaped}\n</code></pre></div>'

    def _is_table_start(self, lines: list[str], i: int) -> bool:
        return (
            i + 1 < len(lines)
            and lines[i].strip().startswith("|")
            and re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", lines[i + 1])
            is not None
        )

    def _table(self, lines: list[str]) -> str:
        rows = [self._split_table_row(line) for line in lines]
        if len(rows) < 2:
            return ""
        head = rows[0]
        body = rows[2:]
        out = ["<table>", "<thead>", "<tr>"]
        out.extend(f"<th>{self.inline(cell)}</th>" for cell in head)
        out.extend(["</tr>", "</thead>", "<tbody>"])
        for row in body:
            out.append("<tr>")
            out.extend(f"<td>{self.inline(cell)}</td>" for cell in row)
            out.append("</tr>")
        out.extend(["</tbody>", "</table>"])
        return "\n".join(out)

    def _split_table_row(self, line: str) -> list[str]:
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cells = re.split(r"(?<!\\)\|", line)
        return [cell.replace(r"\|", "|").strip() for cell in cells]

    def _list(self, lines: list[str]) -> str:
        ordered = bool(re.match(r"^\s*\d+\.", lines[0]))
        tag = "ol" if ordered else "ul"
        items: list[list[str]] = []
        for line in lines:
            m = LIST_RE.match(line)
            if m:
                items.append([m.group(3).strip()])
            elif items:
                items[-1].append(line.strip())
        out = [f"<{tag}>"]
        for item_lines in items:
            rendered = "<br>\n".join(self.inline(part) for part in item_lines if part)
            out.append(f"<li>{rendered}</li>")
        out.append(f"</{tag}>")
        return "\n".join(out)

    def inline(self, text: str) -> str:
        held: list[str] = []

        def hold(value: str) -> str:
            held.append(value)
            return f"\u0000{len(held) - 1}\u0000"

        def repl_code(m: re.Match[str]) -> str:
            return hold(f"<code>{html.escape(m.group(1))}</code>")

        def repl_wikilink(m: re.Match[str]) -> str:
            target = m.group(1).replace(r"\|", "|").strip()
            label = (m.group(2) or target.split("#", 1)[0]).replace(r"\|", "|").strip()
            href = self.resolve_wikilink(target)
            label_html = html.escape(label)
            if href:
                return hold(f'<a href="{html.escape(href, quote=True)}">{label_html}</a>')
            return hold(f'<span class="unresolved-link">{label_html}</span>')

        def repl_md_link(m: re.Match[str]) -> str:
            label, href = m.group(1), m.group(2)
            return hold(f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>')

        text = CODE_SPAN_RE.sub(repl_code, text)
        text = WIKILINK_RE.sub(repl_wikilink, text)
        text = MD_LINK_RE.sub(repl_md_link, text)
        text = html.escape(text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)

        for idx, value in enumerate(held):
            text = text.replace(f"\u0000{idx}\u0000", value)
        return text

    def resolve_wikilink(self, target: str) -> str | None:
        path_part, _, anchor_part = target.partition("#")
        anchor = f"#{slugify(anchor_part)}" if anchor_part else ""

        if path_part.startswith("cybersecurity/"):
            rel = Path(path_part + ".html")
        elif "/" in path_part:
            rel = (self.current_rel.parent / f"{path_part}.html")
        else:
            local = self.current_rel.parent / f"{path_part}.html"
            if (SITE_ES / local).exists():
                rel = local
            else:
                matches = self.slug_index.get(path_part, [])
                if not matches:
                    return None
                rel = matches[0]

        try:
            href = posixpath.relpath(rel.as_posix(), self.current_rel.parent.as_posix())
        except ValueError:
            href = rel.as_posix()
        return href + anchor


def build_slug_index() -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for html_path in sorted(SITE_ES.rglob("*.html")):
        rel = html_path.relative_to(SITE_ES)
        index.setdefault(html_path.stem, []).append(rel)
    return index


def overlay_paths(filter_text: str | None = None) -> list[Path]:
    paths = sorted(TRANSLATIONS.rglob("*.md"))
    if filter_text:
        paths = [p for p in paths if filter_text in p.relative_to(TRANSLATIONS).as_posix()]
    return paths


def first_heading(md: str) -> str:
    for line in strip_frontmatter(md).splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return strip_md(m.group(1)).strip()
    return ""


def first_paragraph_text(md: str) -> str:
    in_code = False
    buf: list[str] = []
    for line in strip_frontmatter(md).splitlines():
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.startswith("#") or not line.strip():
            if buf:
                break
            continue
        if line.startswith((">", "|")) or LIST_RE.match(line):
            if buf:
                break
            continue
        buf.append(line.strip())
    return re.sub(r"\s+", " ", strip_md(" ".join(buf))).strip()


def update_metadata(page: str, title: str, description: str, article_html: str) -> str:
    if title:
        def title_with_existing_suffix(current_title: str) -> str:
            current_title = html.unescape(current_title)
            if " | " in current_title:
                return title + current_title[current_title.index(" | ") :]
            if " - " in current_title:
                return title + current_title[current_title.index(" - ") :]
            return title

        page = re.sub(
            r"<title>.*?</title>",
            lambda m: f"<title>{html.escape(title_with_existing_suffix(m.group(0)[7:-8]))}</title>",
            page,
            count=1,
            flags=re.S,
        )
        page = re.sub(
            r'(<meta property="og:title" content=")([^"]*)(">)',
            lambda m: m.group(1) + html.escape(title_with_existing_suffix(m.group(2)), quote=True) + m.group(3),
            page,
            count=1,
        )
        page = re.sub(
            r'(<meta name="twitter:title" content=")([^"]*)(">)',
            lambda m: m.group(1) + html.escape(title_with_existing_suffix(m.group(2)), quote=True) + m.group(3),
            page,
            count=1,
        )
        page = re.sub(
            r'(<nav class="breadcrumbs"[^>]*>.*?<span>)(.*?)(</span></nav>)',
            lambda m: m.group(1) + html.escape(title) + m.group(3),
            page,
            count=1,
            flags=re.S,
        )
    if description:
        desc = html.escape(description[:157] + "..." if len(description) > 160 else description, quote=True)
        page = re.sub(r'(<meta name="description" content=")[^"]*(">)', rf"\1{desc}\2", page, count=1)
        page = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', rf"\1{desc}\2", page, count=1)
        page = re.sub(r'(<meta name="twitter:description" content=")[^"]*(">)', rf"\1{desc}\2", page, count=1)
    return update_json_ld(page, title, description)


def update_json_ld(page: str, title: str, description: str) -> str:
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', page, re.S)
    if not m:
        return page
    try:
        data = json.loads(html.unescape(m.group(2)))
    except json.JSONDecodeError:
        return page
    items = data if isinstance(data, list) else [data]
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("@type") == "TechArticle":
            if title:
                item["headline"] = title
                if "name" in item:
                    current_name = str(item["name"])
                    if " | " in current_name:
                        item["name"] = title + current_name[current_name.index(" | ") :]
                    elif " - " in current_name:
                        item["name"] = title + current_name[current_name.index(" - ") :]
                    else:
                        item["name"] = title
            if description:
                item["description"] = description[:157] + "..." if len(description) > 160 else description
        if item.get("@type") == "BreadcrumbList" and title:
            elems = item.get("itemListElement") or []
            if elems and isinstance(elems[-1], dict):
                elems[-1]["name"] = title
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return page[: m.start(2)] + raw + page[m.end(2) :]


def replace_article_body(page: str, rendered: str) -> str:
    m = ARTICLE_RE.search(page)
    if not m:
        raise ValueError("no <article> found")
    inner = m.group(2)
    footer = FOOTER_RE.search(inner)
    keep = inner[footer.start() :] if footer else ""
    new_article = m.group(1) + "\n" + rendered.strip() + "\n" + keep + m.group(3)
    return page[: m.start()] + new_article + page[m.end() :]


def update_toc(page: str, rendered: str) -> str:
    links: list[str] = []
    for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h[23]>', rendered, re.S):
        level, anchor, label_html = m.group(1), m.group(2), m.group(3)
        label = html_text(label_html)
        links.append(
            f'<a class="toc-level-{level}" href="#{html.escape(anchor, quote=True)}">{html.escape(label)}</a>'
        )
    if not links:
        return page
    return TOC_RE.sub(lambda m: m.group(1) + "\n" + "\n".join(links) + "\n" + m.group(3), page, count=1)


def entry_layer_labels() -> dict[str, str]:
    labels: dict[str, str] = {}
    for slug in ENTRY_LAYER_SLUGS:
        overlay = TRANSLATIONS / "cybersecurity" / f"{slug}.md"
        if not overlay.exists():
            continue
        label = first_heading(overlay.read_text(encoding="utf-8"))
        if label:
            labels[slug] = label
    return labels


def update_entry_sidebar_labels(page: str, labels: dict[str, str]) -> str:
    for slug, label in labels.items():
        label_html = html.escape(label)
        page = re.sub(
            rf'(<a class="sidebar-link kind-concept(?: active)?" href="[^"]*{re.escape(slug)}\.html">)(.*?)(</a>)',
            lambda m: m.group(1) + label_html + m.group(3),
            page,
            flags=re.S,
        )
    return page


def update_entry_related_titles(page: str, labels: dict[str, str]) -> str:
    for slug, label in labels.items():
        page = re.sub(
            rf'(<a class="related-card" href="[^"]*{re.escape(slug)}\.html"><span>.*?</span><strong>)(.*?)(</strong>)',
            lambda m: m.group(1) + html.escape(label) + m.group(3),
            page,
            flags=re.S,
        )
    return page


def update_search_json(updated: dict[str, tuple[str, str, str]]) -> None:
    search_path = SITE_ES / "search.json"
    if not search_path.exists():
        return
    data = json.loads(search_path.read_text(encoding="utf-8"))
    changed = 0
    for entry in data:
        if not isinstance(entry, dict):
            continue
        url = entry.get("url")
        if url in updated:
            title, description, body_text = updated[url]
            if title:
                entry["title"] = title
            if description:
                entry["description"] = description
            entry["text"] = body_text
            changed += 1
    search_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"updated search.json entries: {changed}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("filter", nargs="?", help="optional path substring, e.g. offensive-security")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not SITE_ES.exists():
        sys.exit("error: site/es does not exist")
    slug_index = build_slug_index()
    sidebar_labels = entry_layer_labels()
    updated: dict[str, tuple[str, str, str]] = {}
    count = 0
    missing: list[str] = []

    for overlay in overlay_paths(args.filter):
        rel_md = overlay.relative_to(TRANSLATIONS)
        page_path = SITE_ES / rel_md.with_suffix(".html")
        if not page_path.exists():
            missing.append(rel_md.as_posix())
            continue

        md = overlay.read_text(encoding="utf-8")
        renderer = MarkdownRenderer(page_path, slug_index)
        rendered = renderer.render(md)
        title = first_heading(md)
        description = first_paragraph_text(md)
        page = page_path.read_text(encoding="utf-8")
        page = replace_article_body(page, rendered)
        page = update_toc(page, rendered)
        page = update_metadata(page, title, description, rendered)
        page = update_entry_sidebar_labels(page, sidebar_labels)
        page = update_entry_related_titles(page, sidebar_labels)

        rel_url = page_path.relative_to(SITE_ES).as_posix()
        updated[rel_url] = (title, description, html_text(rendered))
        count += 1
        if not args.dry_run:
            page_path.write_text(page, encoding="utf-8")

    if not args.dry_run:
        update_search_json(updated)
    print(f"rendered overlays: {count}")
    if missing:
        print("missing site pages:")
        for rel in missing:
            print(f"  {rel}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
