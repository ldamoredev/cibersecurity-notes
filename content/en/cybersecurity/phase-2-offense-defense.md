---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Phase 2 — Offense / Defense (Paired)

You have a working substrate model from [[phase-1-substrate|Phase 1]]. Phase 2 is where most cybersecurity learners plateau, because they pick a side — offense *or* defense — and read it alone. This phase exists to prevent that.

**Phase 2 is the one phase in this atlas meant to be read in pairs.** Every offensive note has a corresponding detection-engineering note that teaches what the same activity looks like from the other side. Read them together. The pairing is not decoration; it is the entire pedagogical value of the phase.

See [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] (Phase 0) for the philosophy. This page is the operational version.

---

## How to read a pair (the 4-step ritual)

For every pair below:

1. **Read the offense note** first. State what the attacker actually does at the wire / protocol / code level.
2. **Read the defense note** second. State what telemetry the attack leaves, which invariant it violates, and which control would have prevented it.
3. **State the gap.** What does the offense achieve that the defense does not catch? What does the defense catch that the offense as described does not address?
4. **Place on the Pyramid of Pain.** Is the defense tied to a low-cost indicator (hash, IP, domain — easy to bypass) or a high-cost one (TTP, behavior — expensive to bypass)? Knowing the level is the senior move.

If you cannot complete steps 3 and 4 for a pair, your model is incomplete and you have just discovered what to re-read.

---

## First-pass pairs (6 pairs / 12 notes, ~2-3 weeks)

The minimum set that gives you a working offense+defense model. Read each pair as a unit — the offense, then the defense, then steps 3–4.

### Pair 1 — Reconnaissance mindset ↔ Visibility mindset

- **Offense:** [[recon|Recon]] — how attackers discover surface before touching it.
- **Defense:** [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]] — what defenders can see, and where the blind spots are.
- **Why this pair first:** Both sides start with the same question — *what can be observed about this system?* — from opposite chairs. The pair frames every other Phase 2 pair.

### Pair 2 — Port scanning ↔ Scan anomaly detection

- **Offense:** [[host-and-port-discovery|Host and Port Discovery]] — the entry-level recon move every operator runs.
- **Defense:** [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]] — what a scan looks like in NetFlow, IDS alerts, and TCP fingerprints.
- **Why this pair second:** The most concrete offense/defense pair in the atlas. After reading it, you can run a scan against an authorized target *and* find your own packets in the defender's logs.

### Pair 3 — Enumeration ↔ Behavioral vs signature detection

- **Offense:** [[enumeration|Enumeration]] — the operator pattern of doing many small probes to build a model.
- **Defense:** [[behavioral-detection-vs-signature-detection|Behavioral Detection vs Signature Detection]] — why catching the *pattern* beats catching the *payload* in 2026.
- **Why this pair:** Names the central tension. Signature evasion is cheap; behavioral evasion requires changing what you do, not just how it looks.

### Pair 4 — Cloaking and evasion ↔ Detection evasion myths

- **Offense:** [[cloaking-and-security-evasion|Cloaking and Security Evasion]] — what evasion attempts actually look like.
- **Defense:** [[detection-evasion-myths-and-modern-limitations|Detection Evasion Myths and Modern Limitations]] — why most "stealth" assumptions fail against modern stacks.
- **Why this pair:** Closes the loop on the "I will just bypass detection" half of the duality. Read both sides together or you will believe one of them.

### Pair 5 — Timing/IDS evasion ↔ IDS/IPS pipelines

- **Offense:** [[nmap-timing-and-evasion|Nmap Timing and Evasion]] — the timing/rate/evasion primitives operators actually use.
- **Defense:** [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and Behavioral Detection Pipelines]] — how IDS rules are written, what they catch, and where they fail.
- **Why this pair:** The most surgical pair. Reading these together is how you learn *which evasion primitive defeats which inspection layer* — diagnostic in both directions.

### Pair 6 — Recon handoff ↔ Kill-chain correlation

- **Offense:** [[recon-to-testing-handoff|Recon to Testing Handoff]] — how recon clues become validated test candidates.
- **Defense:** [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation and Kill Chain Observability]] — how defenders connect weak signals across stages into a chain.
- **Why this pair:** Both notes treat security as a *sequence* rather than a moment. The pair teaches the "many small signals chain into one big story" thesis that drives modern detection.

**Stop here on first pass.** After these 6 pairs you have a working offense+defense model and can intelligently pick which depth pairs matter for your job.

---

## Extended pairs (3 pairs / 6 notes, depth on top of first-pass)

Read these as need-driven, not linear. Each unlocks a specific operator capability.

### Pair 7 — Internet-scale scanning ↔ NetFlow/Zeek/Suricata

- **Offense:** [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]] — async stateless scanning for breadth jobs.
- **Defense:** [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]] — the flow-analytics layer that catches scale before deep packet inspection sees it.
- **Why:** At internet scale, fan-out flow patterns dominate signature inspection. Defenders catch Masscan before IDS does.

### Pair 8 — Tech-stack fingerprinting ↔ Encrypted traffic analysis

- **Offense:** [[tech-stack-fingerprinting|Tech-Stack Fingerprinting]] — how attackers identify what is running, often despite TLS.
- **Defense:** [[encrypted-traffic-analysis-and-metadata-leakage|Encrypted Traffic Analysis and Metadata Leakage]] — JA3/JA4, flow shape, timing, SNI — TLS does not hide as much as people think.
- **Why:** The pair that dismantles "TLS makes traffic invisible". Same metadata leaks both sides exploit.

### Pair 9 — Active recon depth ↔ EDR + process correlation

- **Offense:** [[active-recon|Active Recon]] — engagement-level active discovery.
- **Defense:** [[edr-network-observability-and-process-correlation|EDR Network Observability and Process Correlation]] — the host-side join that ties network behavior to specific processes, users, and parents.
- **Why:** Modern detection's killer feature is tying *which process* made *which connection*. This is where "we saw the scanner" becomes "we identified the operator account".

---

## Cross-cutting detection notes (no single offensive pair)

Some detection-engineering notes are about the discipline itself, not a specific attack. Read these after the first-pass 6 pairs — they apply across all pairs.

- **[[false-positives-false-negatives-and-detection-tradeoffs|False positives, false negatives, and detection tradeoffs]]** — the precision/recall economics that decide whether a rule survives in production.
- **[[telemetry-normalization-correlation-and-enrichment|Telemetry normalization, correlation, and enrichment]]** — ECS/OpenTelemetry, entity resolution, why "we have the logs" is not the same as "we can correlate them".

These two are read *after* you have 6 pairs of concrete examples — they make far more sense once you have something to apply them to.

---

## What "first-pass complete" means in Phase 2

You have completed first-pass Phase 2 when, for any one of the 6 pairs, you can:

1. Explain the offense at the protocol/wire level.
2. Explain the defense's telemetry source and detection logic.
3. State at least one bypass class for the defense.
4. State at least one detection that catches the bypass.
5. Place the defense on the Pyramid of Pain (low → trivial bypass / high → expensive bypass).

If you can do this for one pair, you can do it for all six with the same template. That fluency *is* what Phase 2 teaches.

---

## What's next

After Phase 2 first-pass, you can move to:

- **[[index|Security Playbooks]]** — turn concept into procedure. Specifically [[run-scan-pipeline|Run External Recon Scan Pipeline]] uses three Phase 2 pairs as its operational substrate.
- **Phase 3 — Operator surface** (Attack Surface Mapping, OSINT, Linux Privilege Escalation, Security Playbooks).
- **Phase 4 — Specialty tracks** (API / Cloud / DevSecOps / Wireless) when your job context demands them.

Future entry pages `phase-3-operator.md` and `phase-4-specialty.md` will curate those phases the same way this page curates Phase 2.

---

## Why this page exists

Most security education teaches offense and defense as separate curricula taught by separate people in separate rooms. The cost is the half-practitioner archetype — skilled at one side, dangerous when forced to reason about the other. This atlas is structured to make pairing cheap, and this page is the operational artifact that makes pairing the default reading mode rather than an aspiration.

If you read only one half of these pairs, you have learned half of Phase 2.

---

## Related navigation

- [[start-here|Start Here]] — persona-driven triage page.
- [[phase-1-substrate|Phase 1 — Substrate]] — the previous phase's curated path.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the Phase 0 note this phase operationalizes.
- [[index|Offensive Security / Recon Index]] — full offensive branch listing.
- [[index|Detection Engineering Index]] — full defensive branch listing.
- [[must-know-30|Must-Know 30]] — cross-branch must-know list (Pair 2 from this page is on it).
- [[index|Cybersecurity Index]] — full atlas roadmap.
