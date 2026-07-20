#!/usr/bin/env python3
"""Generate a repeatable, evidence-bound audit of the public corpus."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
EN, ES = ROOT / "content" / "en", ROOT / "content" / "es"

def score(text: str) -> int:
    signals = ("trust boundary", "attacker", "detection", "telemetry", "evidence", "lab", "sources", "references")
    return min(4, sum(term in text.lower() for term in signals) // 2)

def main() -> None:
    notes = sorted(EN.rglob("*.md"))
    branches = Counter(p.relative_to(EN).parts[1] if len(p.relative_to(EN).parts) > 2 else "root" for p in notes)
    es_paths = {p.relative_to(ES) for p in ES.rglob("*.md")} if ES.exists() else set()
    rows, scores = [], Counter()
    for note in notes:
        rel = note.relative_to(EN)
        text = note.read_text(encoding="utf-8")
        title = next((line[2:] for line in text.splitlines() if line.startswith("# ")), note.stem)
        value = score(text); scores[value] += 1
        action = "DEEPEN" if "migration_source" in text else "CANONICAL"
        rows.append(f"| `{rel}` | {title.replace('|', '/')} | {branches[rel.parts[1]] if len(rel.parts)>2 else 'root'} | {value}/4 | {action} |")
    out = ["# Cybersecurity Atlas audit", "", "## Executive summary", "", "The original build depended on an unavailable private vault and deployed a prebuilt site. The public English snapshot has been recovered into `content/en`; this makes builds reproducible, while its recovered notes remain explicitly review-needed. Spanish overlays are now in `content/es`. No private source was imported.", "", "## Real metrics", "", f"- Canonical English notes: {len(notes)}", f"- Spanish overlays: {len(es_paths)} ({len(es_paths)/len(notes):.1%} of English paths)", f"- Branches: {len(branches)}", f"- Playbooks: {branches.get('security-playbooks', 0)}", f"- Recovered snapshot notes requiring editorial review: {scores[0] + scores[1] + scores[2]}", f"- Score distribution (heuristic, 0–4): {dict(sorted(scores.items()))}", "", "The score is an audit triage signal, not a claim of technical correctness. It is based on visible system-model, attack/defense, evidence, lab, and source markers. Run this script after meaningful editorial changes.", "", "## Branch audit", "", "| Current slug | Notes | Recommended action | Target grouping |", "| --- | ---: | --- | --- |"]
    for branch, count in sorted(branches.items()):
        target = "Detection and response" if branch in {"detection-engineering", "security-playbooks"} else "See CONTENT-PLAN.md"
        out.append(f"| `{branch}` | {count} | KEEP_AND_DEEPEN | {target} |")
    out += ["", "## Note audit", "", "| Current path | Title | Branch | Depth signal | Recommended action |", "| --- | --- | --- | --- | --- |", *rows, "", "## Findings and recommendation", "", "Prioritize the six flagship notes, every branch index, and notes that lack sources, system boundaries, evidence, or stated limits. Preserve public paths until a branch-level redirect and link pass succeeds."]
    (ROOT / "CYBERSECURITY-ATLAS-AUDIT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote audit for {len(notes)} notes")

if __name__ == "__main__":
    main()
