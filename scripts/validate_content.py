#!/usr/bin/env python3
"""Structural, safety-first validation for public Atlas Markdown."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "content" / "en"
ES = ROOT / "content" / "es"
KINDS = {"concept", "mechanism", "attack", "detection", "lab", "playbook", "incident", "standard-guide", "index"}
LEVELS = {"beginner", "intermediate", "advanced"}
STATUSES = {"current", "review-needed", "outdated", "planned", "experimental", "active"}
WIKILINK = re.compile(r"\[\[([^\]|#]+)")
PUBLIC_IP = re.compile(r"(?<![\w.])(?!(?:127|10|192\.168)\.)(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-5])(?:\.\d{1,3}){3}(?![\w.])")

def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    values = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "-")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"\'')
    return values

def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    notes = sorted(EN.rglob("*.md")) if EN.exists() else []
    if not notes:
        errors.append("content/en contains no canonical Markdown")
    path_map = {str(p.relative_to(EN).with_suffix("")): p for p in notes}
    slugs = {p.stem for p in notes}
    for note in notes:
        text = note.read_text(encoding="utf-8")
        fm = frontmatter(text)
        rel = note.relative_to(EN)
        for field, allowed in (("kind", KINDS), ("level", LEVELS), ("status", STATUSES)):
            if field in fm and fm[field] not in allowed:
                errors.append(f"{rel}: invalid {field}={fm[field]!r}")
        if fm.get("kind") == "lab" and fm.get("authorization") != "local-only":
            errors.append(f"{rel}: lab requires authorization: local-only")
        if PUBLIC_IP.search(text):
            warnings.append(f"{rel}: public-looking IP literal requires review")
        for raw in WIKILINK.findall(text):
            target = raw.strip().lstrip("/")
            candidate = target.removesuffix(".md")
            if candidate not in path_map and Path(candidate).name not in slugs:
                errors.append(f"{rel}: unresolved wikilink [[{raw}]]")
        if "## Sources" not in text and "## References" not in text and "migration_source" not in fm:
            warnings.append(f"{rel}: no sources section")
    es_count = len(list(ES.rglob("*.md"))) if ES.exists() else 0
    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    print(f"INFO: canonical={len(notes)} spanish-overlays={es_count} errors={len(errors)} warnings={len(warnings)}")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
