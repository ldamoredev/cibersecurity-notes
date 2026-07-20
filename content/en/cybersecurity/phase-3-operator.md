---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Phase 3 — Operator Surface (Concept → Capability)

You have a substrate model from [[phase-1-substrate|Phase 1]] and you can read offense and defense as pairs from [[phase-2-offense-defense|Phase 2]]. Phase 3 is where that knowledge becomes **operator capability**: workflows you can actually execute against authorized targets, not just reason about.

Phase 3 is the only phase organized around a **workflow**, not a body of theory. The 4 branches form a single end-to-end loop:

> **Mapping the surface → gathering public evidence → walking through a foothold → executing repeatable procedures.**

The 41 atomic notes in those branches collapse into ~12 first-pass notes that give you the working operator loop, then ~12 more that turn the loop into a polished engagement workflow.

---

## The Phase 3 loop

```
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  ▼                                                         │
ATTACK SURFACE MAPPING  →  OSINT  →  LINUX PRIVESC  →  PLAYBOOKS  →
  (what is exposed)      (public      (post-foothold      (repeatable
                          evidence)    boundary failure)   procedures)
```

You can enter the loop at any node depending on engagement context. The first-pass reading order below walks the loop in its natural sequence.

---

## First-pass reading order (12 notes, ~2 weeks)

### Attack Surface Mapping — 3 notes

1. **[[attack-surface-mapping|Attack Surface Mapping]]** — the core mental model: surface as the intersection of reachability, discoverability, and drift.
2. **[[external-attack-surface|External Attack Surface]]** — what is exposed to the public internet, with a discipline for separating intended from actual.
3. **[[exposed-service-triage|Exposed Service Triage]]** — how to rank a hundred discovered services in priority order so you spend time on the right ones.

### OSINT — 3 notes

1. **[[osint|OSINT]]** — public-source evidence gathering, with a discipline for converting clues into validated facts rather than guesses.
2. **[[osint-triage|OSINT Triage]]** — which findings deserve investigation now, which are noise, and how to record the decision.
3. **[[google-dorking|Google Dorking]]** — the most concrete OSINT technique; teaches you what search operators actually do and where indexed data leaks.

### Linux Privilege Escalation — 3 notes

1. **[[linux-privilege-escalation|Linux Privilege Escalation]]** — the core mental model: local privilege boundaries, what fails after a foothold, how enumeration becomes ranked hypotheses.
2. **[[linux-enumeration|Linux Enumeration]]** — the breadth-first inventory that turns "I have a shell" into "I have a ranked list of paths upward".
3. **[[sudo-misconfigurations|Sudo Misconfigurations]]** — by frequency, the #1 real-world Linux privesc path. Teaches the "trust delegation" pattern that recurs everywhere else.

### Security Playbooks — 3 notes

1. **[[index|Security Playbooks Index]]** — read this first to see the playbook template and the catalogue.
2. **[[exploit-idor|Exploit IDOR]]** — read one offense playbook end-to-end to see how concept becomes procedure. IDOR is the right one because it is the most common real-world web finding.
3. **[[run-scan-pipeline|Run External Recon Scan Pipeline]]** — the engagement-level recon playbook that ties Phases 1–3 together. Read this last because it depends on everything else.

**Stop here on first pass.** With these 12 notes you have a working operator loop and can execute a basic external recon engagement on an authorized target end-to-end.

---

## Extended reading (12 more notes, depth on top of first-pass)

Read as need-driven, by branch, when your engagement actually requires it.

### Attack Surface Mapping depth — 4 notes

- **[[endpoint-discovery|Endpoint Discovery]]** — when web/API surface dominates the engagement.
- **[[admin-interface-discovery|Admin Interface Discovery]]** — the high-impact subset of endpoint discovery.
- **[[subdomain-takeover|Subdomain Takeover]]** — the canonical dangling-DNS bug class; high-impact and findable.
- **[[third-party-exposure|Third-Party Exposure]]** — supply-chain attack surface; often the largest unmanaged component of an organization's posture.

### OSINT depth — 3 notes

- **[[company-osint|Company OSINT]]** — organization-level mapping when the engagement is corporate-scoped.
- **[[breach-and-leak-intelligence|Breach and Leak Intelligence]]** — credential exposure as a primary recon source.
- **[[osint-reporting|OSINT Reporting]]** — turning evidence into structured findings that survive review.

### Linux Privesc depth — 3 notes

- **[[suid-sgid-misconfigurations|SUID/SGID Misconfigurations]]** — the second most common privesc class in real-world findings.
- **[[linux-capabilities|Linux Capabilities]]** — the modern replacement for SUID and a common source of subtle privesc.
- **[[linpeas-workflow|LinPEAS Workflow]]** — the practical tooling layer that converts theory into a 60-second enumeration pass.

### Playbooks depth — 2 notes

- **[[exploit-sqli|Exploit SQL Injection]]** — the canonical injection playbook; transfers to command injection, NoSQL injection, etc.
- **[[investigate-ssrf|Investigate SSRF]]** — the most-impactful cloud-era web finding; the playbook teaches the metadata-endpoint chain that turns SSRF into compromise.

---

## How Phase 3 connects back to Phase 0 / 1 / 2

Phase 3 is where the earlier phases pay off. Use them as lenses:

- **From Phase 0:** Every operator finding gets named with its [[cia-triad-and-what-it-actually-decides|CIA property]] before reporting. Every workflow gets a [[threat-modeling-quickstart|threat-model]] pass before execution. Every offensive move is paired with its [[attacker-defender-duality-as-a-learning-tool|defensive counterpart]] before claiming it succeeded.
- **From Phase 1:** Networking and Web Security substrate is what makes attack-surface mapping intelligible; Cryptography correctness is what makes "the JWT validates" claims credible.
- **From Phase 2:** Every Phase 3 playbook has a Phase 2 detection counterpart. The senior operator runs the offensive playbook *and* knows what the SOC saw.

---

## What to skip on first pass

Phase 3 has 41 notes; the first-pass 12 + extended 12 = 24. The other 17 are depth:

- **OSINT specialty notes** (email-and-phone-osint, image-and-location-osint, social-media-osint, historical-internet-artifacts) — workflow-specific; return when the engagement type demands them.
- **Attack Surface Mapping specialty** (deprecated-api-versions, exposed-storage, internal-attack-surface) — return when the engagement has those surface types.
- **Linux Privesc specialty** (path-hijacking, kernel-exploit-triage, cron-and-timer-abuse) — return after sudo and SUID basics are reflex.
- **Niche playbooks** (test-client-ip-spoofing, test-cors-behavior, test-path-traversal, inspect-session-handling, etc.) — return when the engagement scope includes them.

This list is not a value judgment. It is operator-prioritization for someone who wants to execute one authorized engagement end-to-end before specializing.

---

## What "first-pass complete" means in Phase 3

You have completed first-pass Phase 3 when you can:

1. **Walk the loop** from attack surface mapping → OSINT → privesc-after-foothold → playbook execution against an authorized target without an external recipe.
2. **Triage findings** — given 100 services, name which 10 deserve immediate attention and why.
3. **Execute one playbook from memory** — pick one of [[exploit-idor]], [[run-scan-pipeline]], or [[exploit-sqli]] and run it from start to "validated finding or negative result" without reading the page.
4. **Write the report** — turn the run into a finding with reproduction steps, CIA property, blast radius, and remediation, in under a page.

These four steps are the unit of operator capability. Phase 4 specialization is built on top of this unit.

---

## What's next

After Phase 3 first-pass, you choose Phase 4 specialty tracks based on your job:

- **API Security** if you build or test APIs.
- **Cloud Security** if your systems run in cloud.
- **DevSecOps** if you own a build/release pipeline.
- **Wireless Security** if you work with Wi-Fi networks.

A future `phase-4-specialty.md` will surface the right starting notes for each. Until then, the [[index|API Security]], [[index|Cloud Security]], [[index|DevSecOps]], and [[index|Wireless Security]] indexes carry their own ordered reading lists.

The Always-on parallel discipline of [[index|Privacy, Anonymity & OPSEC]] becomes professionally relevant in Phase 3 — every engagement leaves operator-side artifacts that need OPSEC discipline.

---

## Related navigation

- [[start-here|Start Here]] — persona-driven triage page.
- [[phase-1-substrate|Phase 1 — Substrate]] — previous phase entry.
- [[phase-2-offense-defense|Phase 2 — Offense / Defense]] — previous phase entry.
- [[index|Phase 0 — Foundations]] — the mental models Phase 3 operationalizes.
- [[index|Attack Surface Mapping Index]] — full branch.
- [[index|OSINT Index]] — full branch.
- [[index|Linux Privilege Escalation Index]] — full branch.
- [[index|Security Playbooks Index]] — full branch.
- [[must-know-30|Must-Know 30]] — cross-branch must-know list.
- [[index|Cybersecurity Index]] — full atlas roadmap.
