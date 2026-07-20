---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Foundations Index — Phase 0

## Purpose

This index is the **first thing** a learner should read in the atlas. It exists because every other branch assumes a learner already *thinks security-first*. Phase 0 builds that mindset before any technical branch is opened.

Return to [[index|Cybersecurity Index]] for navigation across branches.

---

## Who this branch is for

- IT person who has never thought about security as a discipline.
- Developer who has been told to "do security" and isn't sure what that means.
- Senior engineer rebuilding the basics deliberately.
- Anyone who has confused "I know Wireshark" with "I understand security."

If you already think in CIA-triad terms, threat-modeling reflexes, and offense/defense pairing, skim this branch and move to [[index|Networking]].

---

## Recommended reading order

### Phase 0 — Orientation

1. [[what-is-cybersecurity-and-why-it-is-not-a-tool-list]]
2. [[cia-triad-and-what-it-actually-decides]]
3. [[threat-modeling-quickstart]]
4. [[attacker-defender-duality-as-a-learning-tool]]
5. [[minimum-viable-cybersecurity-literacy]]
6. [[job-context-specialization]]
7. [[certifications-as-validation-signals]]

After the first four orientation notes, use notes 5-7 when choosing a learning path, specialty track, or certification sequence. Then proceed to Phase 1 — Substrate, starting with [[index|Networking]] (the new Phase 1 order is Networking → Web Security → Cryptography; see [[index]] for the migration trail).

---

## Branch conventions

Phase 0 notes are **framework notes**, not technical notes. They differ from atomic notes in other branches in two ways:

- They teach *how to reason*, not *what a vulnerability is*. So they skip the "Variants and bypasses" and "Practical labs" sections of the atomic-note template, and instead use "Common misconceptions" and "How to apply this".
- They do not need a dedicated `reference-registry-foundations.md`. References are framework documents (NIST CSF, OWASP, Microsoft threat-modeling guidance) and are listed directly in each note's `## References` section.

If the branch grows past ~6 notes, a registry should be added.

---

## Cross-links to other branches

Phase 0 notes are intended to be cross-linked **from** the first note of every branch index (a "Before this branch" entry), giving every learner a reachable path back to the framework.

- [[index|Networking]] — Phase 1, first technical branch
- [[index|Web Security]] — Phase 1, the daily surface
- [[index|Cryptography]] — Phase 1, after TLS is concrete
- [[index|Offensive Security / Recon]] — Phase 2, paired with detection
- [[index|Detection Engineering]] — Phase 2, paired with offense
