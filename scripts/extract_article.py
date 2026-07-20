#!/usr/bin/env python3
"""Extract a single note's body from rendered English HTML as clean Markdown.

The English `.md` sources live in the (absent) Obsidian vault, so the only
on-repo source of truth for a note's text is its rendered page under
`site/en/<rel>.html`. That page is 70-80 KB, but the actual note body is only
~4-15 KB — the rest is the sidebar nav repeated on every page. This script
isolates the `<article>` body (everything before the build-generated
`branch-nav` / related-notes footer) and converts it back to translation-ready
Markdown:

  * code blocks lose their Pygments span noise (big token saver)
  * wikilinks are recovered from anchor hrefs as `[[slug]]` / `[[slug|label]]`
  * unresolved links become `[[slug]]`
  * headings/lists/tables/blockquotes/bold/inline-code are preserved

It is a translation aid, not a byte-perfect round-trip — minor list-continuation
indentation may differ, which the translator can fix.

Usage:
    python3 scripts/extract_article.py cybersecurity/web-security/csrf
    python3 scripts/extract_article.py site/en/cybersecurity/web-security/csrf.html
    python3 scripts/extract_article.py --list web-security      # list pending notes in a branch
    python3 scripts/extract_article.py --export-canonical       # recover public snapshot into content/en
"""
from __future__ import annotations

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN_ROOT = ROOT / "site" / "en"
ES_ROOT = ROOT / "translations" / "es"

# Everything from these tags onward inside <article> is build-generated chrome.
FOOTER_RE = re.compile(r'<nav class="branch-nav"|<section class="related-notes"')


def resolve_html(arg: str) -> Path:
    """Accept a slug-ish rel path, a 'cybersecurity/...' path, or a full html path."""
    p = Path(arg)
    if p.suffix == ".html" and p.exists():
        return p
    rel = arg
    if rel.endswith(".md"):
        rel = rel[:-3]
    if rel.endswith(".html"):
        rel = rel[:-5]
    if not rel.startswith("cybersecurity/") and not (EN_ROOT / f"{rel}.html").exists():
        # bare slug or path under cybersecurity/
        rel = f"cybersecurity/{rel}"
    cand = EN_ROOT / f"{rel}.html"
    if not cand.exists():
        sys.exit(f"error: no rendered page at {cand.relative_to(ROOT)}")
    return cand


def article_body_html(page_html: str) -> str:
    m = re.search(r"<article[^>]*>(.*?)</article>", page_html, re.S)
    if not m:
        sys.exit("error: no <article> found")
    body = m.group(1)
    cut = FOOTER_RE.search(body)
    return body[: cut.start()] if cut else body


class MdWriter(HTMLParser):
    """Convert the article-body HTML fragment to Markdown."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.inline: list[str] = []
        self.list_stack: list[dict] = []  # {"type": ul|ol, "n": int}
        self.in_pre = False
        self.pre_buf: list[str] = []
        self.in_a = False
        self.a_href = ""
        self.a_text: list[str] = []
        self.in_unresolved = False
        self.bq = 0
        # table state
        self.in_table = False
        self.rows: list[list[str]] = []
        self.cur_row: list[str] = []
        self.in_cell = False
        self.cell: list[str] = []

    # --- sink helpers ----------------------------------------------------
    def emit(self, s: str) -> None:
        if self.in_a:
            self.a_text.append(s)
        elif self.in_cell:
            self.cell.append(s)
        else:
            self.inline.append(s)

    def flush_block(self, prefix: str = "") -> None:
        text = "".join(self.inline).strip()
        self.inline = []
        if not text:
            return
        if self.bq:
            text = "\n".join(("> " + ln).rstrip() for ln in text.split("\n"))
        if prefix:
            text = prefix + text
        self.parts.append(text)

    # --- tags ------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.in_pre and tag != "pre":
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.flush_block()
            self.inline.append("#" * int(tag[1]) + " ")
        elif tag == "p":
            if not self.list_stack:
                self.flush_block()
        elif tag in ("ul", "ol"):
            self.flush_block()
            self.list_stack.append({"type": tag, "n": 0})
        elif tag == "li":
            self.flush_block()
            lvl = len(self.list_stack) - 1
            indent = "  " * max(lvl, 0)
            top = self.list_stack[-1] if self.list_stack else {"type": "ul", "n": 0}
            if top["type"] == "ol":
                top["n"] += 1
                self.inline.append(f"{indent}{top['n']}. ")
            else:
                self.inline.append(f"{indent}- ")
        elif tag in ("strong", "b"):
            self.emit("**")
        elif tag in ("em", "i"):
            self.emit("*")
        elif tag == "code" and not self.in_pre:
            self.emit("`")
        elif tag == "pre":
            self.flush_block()
            self.in_pre = True
            self.pre_buf = []
        elif tag == "a":
            self.in_a = True
            self.a_href = a.get("href", "")
            self.a_text = []
        elif tag == "span" and "unresolved-link" in a.get("class", ""):
            self.in_unresolved = True
        elif tag == "br":
            self.emit("\n")
        elif tag == "hr":
            self.flush_block()
            self.parts.append("---")
        elif tag == "blockquote":
            self.flush_block()
            self.bq += 1
        elif tag == "table":
            self.flush_block()
            self.in_table = True
            self.rows = []
        elif tag == "tr":
            self.cur_row = []
        elif tag in ("td", "th"):
            self.in_cell = True
            self.cell = []

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False
            code = "".join(self.pre_buf).strip("\n")
            self.parts.append(f"```\n{code}\n```")
            return
        if self.in_pre:
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.flush_block()
        elif tag == "p":
            if self.list_stack:
                # continuation inside a list item: keep inline, add newline
                self.inline.append("\n")
            else:
                self.flush_block()
        elif tag in ("ul", "ol"):
            self.flush_block()
            if self.list_stack:
                self.list_stack.pop()
        elif tag == "li":
            self.flush_block()
        elif tag in ("strong", "b"):
            self.emit("**")
        elif tag in ("em", "i"):
            self.emit("*")
        elif tag == "code" and not self.in_pre:
            self.emit("`")
        elif tag == "a":
            self.in_a = False
            text = "".join(self.a_text).strip()
            href = self.a_href
            if href.endswith(".html"):
                slug = Path(href).name[:-5]
                if text and text != slug:
                    self.emit(f"[[{slug}|{text}]]")
                else:
                    self.emit(f"[[{slug}]]")
            elif href.startswith(("http://", "https://")):
                self.emit(f"[{text}]({href})")
            else:
                self.emit(text)
        elif tag == "span" and self.in_unresolved:
            self.in_unresolved = False
        elif tag == "blockquote":
            if self.bq:
                self.bq -= 1
        elif tag in ("td", "th"):
            self.in_cell = False
            self.cur_row.append("".join(self.cell).strip())
        elif tag == "tr":
            if self.cur_row:
                self.rows.append(self.cur_row)
            self.cur_row = []
        elif tag == "table":
            self.in_table = False
            self.parts.append(self._render_table())

    def handle_data(self, data):
        if self.in_pre:
            self.pre_buf.append(data)
        else:
            self.emit(data)

    def _render_table(self) -> str:
        if not self.rows:
            return ""
        head = self.rows[0]
        out = ["| " + " | ".join(head) + " |",
               "| " + " | ".join("---" for _ in head) + " |"]
        for row in self.rows[1:]:
            out.append("| " + " | ".join(row) + " |")
        return "\n".join(out)

    def markdown(self) -> str:
        self.flush_block()
        text = "\n\n".join(p for p in self.parts if p.strip())
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = _tighten_lists(text)
        text = "\n".join(ln.rstrip() for ln in text.split("\n"))
        return text.strip() + "\n"


_LI_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s")


def _tighten_lists(text: str) -> str:
    """Drop blank lines that sit between two consecutive list items."""
    lines = text.split("\n")
    out: list[str] = []
    for i, ln in enumerate(lines):
        if ln == "" and out and _LI_RE.match(out[-1]):
            j = i + 1
            while j < len(lines) and lines[j] == "":
                j += 1
            if j < len(lines) and _LI_RE.match(lines[j]):
                continue
        out.append(ln)
    return "\n".join(out)


def to_markdown(page_html: str) -> str:
    w = MdWriter()
    w.feed(article_body_html(page_html))
    return w.markdown()


def list_pending(branch: str | None) -> None:
    canon = {p.relative_to(EN_ROOT).with_suffix("")
             for p in EN_ROOT.rglob("*.html")}
    done = {p.relative_to(ES_ROOT).with_suffix("")
            for p in ES_ROOT.rglob("*.md")}
    pending = sorted(str(p) for p in (canon - done))
    if branch:
        pending = [p for p in pending if f"/{branch}/" in p or p.endswith(f"/{branch}")
                   or branch in p]
    for p in pending:
        print(p)
    print(f"\n# {len(pending)} pending", file=sys.stderr)


def export_canonical() -> None:
    """Recover the *published* English snapshot into repository content.

    This is intentionally a migration bridge, not a Markdown round-trip claim:
    the private Obsidian vault is absent and the renderer's public HTML is the
    only complete English corpus tracked by Git.  Bodies are recovered without
    inventing material; frontmatter is added only where it can state the
    recovery provenance.  Editorial normalization happens later, note by note.
    """
    target_root = ROOT / "content" / "en"
    written = 0
    for page in sorted(EN_ROOT.rglob("*.html")):
        rel = page.relative_to(EN_ROOT)
        if rel.name == "index.html" and rel.parent == EN_ROOT:
            continue
        target = target_root / rel.with_suffix(".md")
        target.parent.mkdir(parents=True, exist_ok=True)
        body = to_markdown(page.read_text(encoding="utf-8"))
        target.write_text(
            "---\n"
            "migration_source: published-html-snapshot\n"
            "migration_status: needs-editorial-review\n"
            "---\n\n" + body,
            encoding="utf-8",
        )
        written += 1
    print(f"Recovered {written} public English notes into {target_root.relative_to(ROOT)}")


def main(argv: list[str]) -> None:
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "--list":
        list_pending(argv[1] if len(argv) > 1 else None)
        return
    if argv[0] == "--export-canonical":
        export_canonical()
        return
    html_path = resolve_html(argv[0])
    rel = html_path.relative_to(EN_ROOT).with_suffix(".md")
    overlay = ES_ROOT / rel
    print(f"# SOURCE: {html_path.relative_to(ROOT)}")
    print(f"# OVERLAY (write Spanish here): translations/es/{rel}")
    print(f"# ALREADY TRANSLATED: {overlay.exists()}")
    print("# " + "-" * 68)
    print(to_markdown(html_path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    main(sys.argv[1:])
