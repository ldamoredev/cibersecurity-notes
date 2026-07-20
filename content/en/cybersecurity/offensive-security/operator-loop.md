---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# The Operator Loop

## Definition

The operator loop is the repeatable decision cycle a red-team operator (or a real intruder) runs from outside the perimeter to objective: **recon → initial access → enumerate → privilege-escalation → lateral movement → persistence → actions-on-objectives**, with the middle stages *looping* on every newly acquired host or identity. It is the methodology spine that the branch's individual technique notes (recon, enumeration, privilege escalation, the detection playbooks) are *stages of*. Under 2026 EDR/identity-telemetry pressure the loop is governed less by "can I do this?" and more by **"what does this cost me in telemetry, and can I undo it?"**

## Why it matters

Individual techniques — Kerberoasting, SUID abuse, an SSRF to the metadata endpoint — are *moves*. The operator loop is the *game*. Operators who only collect techniques get caught sequencing them badly. Three transferable lessons:

- **The loop is a sequence of priced bets, not a checklist.** Every stage is a choice weighed on two axes: **reversible ↔ irreversible** (can I undo the footprint?) and **quiet ↔ loud** (what telemetry does this emit?). A failed password spray is reversible and cheap; dumping LSASS or dropping an implant is irreversible and loud. Senior tradecraft front-loads reversible, quiet actions and defers irreversible ones until the objective forces them.
- **Telemetry collapses the decision space.** In a well-instrumented 2026 enterprise, EDR process lineage, identity logs (LDAP recon, anomalous auth), and network metadata turn "many ways forward" into "a few quiet ways forward." The defender's visibility *is* the operator's constraint — which is why this note pairs tightly to the [[attack-path-correlation-and-kill-chain-observability|detection-engineering branch]].
- **It transfers across targets.** The same seven-beat loop runs on Windows-AD, macOS, and cloud — but the *mechanics* of each stage differ completely (Kerberos vs TCC vs IAM). Holding the loop as the invariant lets you port the skill instead of relearning it per platform.

This note is the offensive half of the [[attacker-defender-duality-as-a-learning-tool|attacker-defender duality]]; the defender reads it as the kill chain to disrupt.

## How it works

The loop runs in **7 stages**, where stages 3–5 repeat on every new foothold:

1. **Recon (external).** OSINT + attack-surface mapping. Usually reversible and near-invisible to the target. → [[passive-recon]], [[active-recon]].
2. **Initial access.** Phish, exploit, or valid credentials. The first meaningfully *loud* step — it produces an auth event or a payload execution.
3. **Enumerate.** Situational awareness from the foothold: local privileges, domain/cloud structure, reachable hosts and identities. High value, frequently the *noisiest* step (LDAP recon, cloud API enumeration). → [[enumeration]].
4. **Privilege escalation.** Local user → admin/root/SYSTEM, or low-priv identity → high-priv role. → [[windows-privilege-escalation|Windows privesc]], the Linux privesc branch.
5. **Lateral movement.** To the next host or identity using harvested credentials, tickets, or tokens.
6. **Persistence.** Survive reboot and credential rotation — a deliberately *deferred, irreversible* artifact, taken only when the foothold is worth keeping.
7. **Actions on objectives.** Collection, exfiltration, or impact — the goal, and the point of maximum risk.

**The loop, not the line:** stages 3→4→5 re-run on each acquired host/identity (enumerate the new context, escalate within it, move again), and internal recon re-seeds stage 1 from inside.

A decision-branch at a fresh foothold makes the two axes concrete:

```
Foothold: user shell on a Windows workstation, EDR present, AD domain-joined
Need: domain situational awareness before any credential action
├─ Option A  SharpHound, full collection ....... LOUD (LDAP-recon alert) · reversible
├─ Option B  targeted LDAP, paged + throttled .. quieter · slower · reversible
├─ Option C  dump LSASS for credentials ........ LOUD + IRREVERSIBLE (LSASS-access
│                                                 telemetry + a credential artifact)
└─ Operator rule: exhaust reversible+quiet enumeration (A/B) before any
                  irreversible credential action (C). Spend irreversibility late.
```

The loop is not a checklist; it is an ordering problem. The skill is *sequencing* moves to reach the objective while spending as little telemetry and irreversibility as possible.

> Section adaptation: this is a methodology note. *How it works* describes a decision cycle rather than a single mechanism; *Variants and bypasses* below carries the per-target-world view; *Practical labs* are mapping/reasoning exercises plus one runnable range.

## Techniques / patterns

How top operators actually run the loop:

- **Model the defender's view before each action.** Ask "what does this look like in EDR / identity / network telemetry?" *before* doing it. The [[network-security-monitoring-discipline|monitoring discipline]] note is the mirror of this question.
- **Front-load reversible and quiet; defer irreversible and loud.** Recon and enumeration first; credential dumping and persistence last and only as needed. Irreversibility is a budget you spend, not a default.
- **Live off the land.** Prefer built-in tooling whose telemetry blends with normal admin activity over noisy custom tools that trip behavioral detection.
- **Hold multiple independent footholds/identities.** One burned access should not reset the engagement; redundancy is what makes a single loud mistake survivable.
- **Branch on telemetry, not habit.** If a quiet path to the same outcome exists, take it; treat the loud path as a last resort, not the default.
- **Stay inside scope and time-box (authorized engagements).** The loop runs under rules of engagement — [[scope-validation]] and [[recon-to-testing-handoff]] gate where it may go.

## Variants and bypasses

The same loop, three target worlds — Q2's core comparison. The invariant is the seven stages; the *stage mechanics and telemetry* differ.

### 1. Windows + Active Directory

The canonical loop. Initial access → AD enumeration ([[bloodhound-attack-path-analysis|BloodHound]]) → Kerberos/credential attacks (Kerberoast, AS-REP) → lateral via pass-the-hash / tickets → DCSync / Golden Ticket → Domain Admin. **Telemetry:** Windows event logs, EDR, Defender for Identity — the [[detect-bloodhound-collection|AD-detection trio]] lives here. The richest detection surface of the three.

### 2. macOS

Initial access (phish/installer) → TCC and keychain enumeration → privesc via TCC bypass or local misconfig → lateral often via SSH or MDM → persistence via LaunchAgents/Daemons. **Telemetry:** Endpoint Security Framework (ESF) and Unified Logs. Fewer graph-style identity attacks; the loop is endpoint- and MDM-centric.

### 3. Cloud-native

Initial access via leaked keys, OAuth abuse, or SSRF-to-metadata → IAM enumeration → privesc via role/policy abuse (`iam:PassRole`, privilege-escalation policy paths) → lateral via assumed roles / cross-account trust → persistence via IAM users, access keys, or serverless triggers. **Telemetry:** CloudTrail / Azure Activity / GCP audit logs. The loop is *identity- and API-shaped*, not host-shaped — "lateral movement" is an `AssumeRole`, not an SMB session.

**Hybrid is the 2026 reality:** real loops chain on-prem AD → Entra ID → SaaS, crossing all three worlds in one engagement — the natural extension tracked in [[identity-attack-paths-across-idps]].

## Impact

For a methodology note, "impact" is what loop *execution quality* produces:

- **Objective reached without detection (mature operator)** vs **early burn (sloppy sequencing).** The difference is almost never technique knowledge — it is ordering and telemetry awareness.
- **Dwell time and blast radius.** A patient loop yields weeks of undetected access and broad reach; a rushed one trips a stage-level detection and resets.
- **For the defender, the loop is the kill chain to break.** Every stage the operator *must* pass through is a detection and disruption opportunity; stall any stage and the loop cannot close.

## Detection and defense

The defender's pairing — how to break the loop. Ordered by effectiveness:

1.
**Raise the cost of every stage (defense-in-depth).**
   Each mandatory stage is a detection opportunity. The goal is not a single wall but enough friction that the operator must take a loud or irreversible action — which you are watching for.

2.
**Collapse the decision space with broad telemetry.**
   EDR (process lineage, LSASS access), identity (LDAP recon, anomalous auth), and network (lateral auth, C2 beaconing) together remove the operator's quiet options. The richer and more correlated the telemetry, the fewer ways forward stay invisible — see [[attack-path-correlation-and-kill-chain-observability|attack-path correlation]].

3.
**Instrument the irreversible stages hardest.**
   Credential dumping, persistence installation, and privileged lateral auth leave durable artifacts and distinctive telemetry. Concentrate detection where the operator is forced to spend irreversibility.

4.
**Segment identity and protect Tier 0.**
   If privilege escalation and lateral movement structurally cannot reach the crown jewels, even a successful inner loop yields little — shrink the attack graph ([[tier-zero-administration-and-paw|Tier 0]]).

5.
**Assume breach and hunt the inner loop.**
   Detection must target stages 3–7, not just initial access. Perimeter prevention alone concedes the entire loop the moment one foothold lands.

### What does not work as a primary defense

- **Perimeter-only / prevent-initial-access.** The loop *assumes* breach. If your only control is stopping stage 2, stages 3–7 run unobserved once anyone gets in.
- **Detecting tools instead of behaviors.** Operators rename, recompile, and reimplement tooling. The loop's *stages* persist; tool signatures do not.
- **Treating stages in isolation.** A lone enumeration event looks benign; the kill chain is the *correlation* across stages. Single-stage rules miss the loop.

## Practical labs

This is a methodology note, so the labs are mapping/reasoning exercises plus one runnable range. Run any hands-on work only against owned labs or authorized engagements.

### Map an engagement onto the loop and its axes

```
For your last authorized engagement (or a public APT report), fill the table:
Stage                | Action taken            | Reversible? | Telemetry emitted
initial-access       | ...                     | y/n         | ...
enumerate            | ...                     | y/n         | ...
privilege-escalation | ...                     | y/n         | ...
lateral-movement     | ...                     | y/n         | ...
The irreversible+loud rows are where the defender had the best shot.
```

### Overlay the loop on MITRE ATT&CK

```
Open the ATT&CK Navigator (https://mitre-attack.github.io/attack-navigator/)
and color the tactics your loop touched: Reconnaissance, Initial Access,
Discovery, Privilege Escalation, Lateral Movement, Persistence, Collection,
Exfiltration, Impact. The colored path IS the operator loop for that engagement.
```

### Run one stage in a lab and watch the telemetry

```
# Stand up Game of Active Directory (GOAD) or DetectionLab, run BloodHound from a
# foothold, and read what the defender sees (Windows 4662/4661, Defender for
# Identity LDAP-recon alert). Owned lab only.
# GOAD: https://github.com/Orange-Cyberdefense/GOAD
```

The lesson is the *telemetry cost* of a single stage — the input to every branch decision above.

### Build a reversible-vs-irreversible decision tree

```
For one foothold, enumerate the options to reach the next stage, label each
reversible/irreversible and quiet/loud, and order them. Practicing the ordering
is the methodology; the individual techniques are elsewhere in the branch.
```

## Practical examples

- **Quiet-first AD engagement.** Phish → SharpHound (paced) → Kerberoast → offline crack → pass-the-hash lateral → DCSync → Domain Admin, with LSASS dumping deferred until a specific credential was required. Objective reached; few irreversible actions spent.
- **Patient real-world intrusion.** An APT runs the identical loop over *weeks*, pacing enumeration and lateral movement to stay under behavioral thresholds — the same stages, optimized for dwell time over speed.
- **Cloud loop.** A leaked CI/CD key → IAM enumeration → `iam:PassRole` privesc to an admin role → cross-account `AssumeRole` → S3 exfiltration. No host shells anywhere; the whole loop is API calls in CloudTrail.
- **macOS loop.** Phished installer → TCC/keychain enumeration → keychain credential theft → MDM-assisted lateral movement → LaunchAgent persistence.
- **Where the loop stalled.** An operator dumped LSASS in the first hour to "save time," tripped the EDR LSASS-access detection, and lost the foothold — a textbook case of spending irreversibility and loudness too early.

## Related notes

- [[recon]] — stage 1; the external-recon entry to the loop.
- [[enumeration]] — stage 3; the situational-awareness engine that re-runs each iteration.
- [[recon-to-testing-handoff]] — the engagement-discipline boundary the loop runs inside.
- [[scope-validation]] — the rules-of-engagement gate on where the loop may go.
- [[bloodhound-attack-path-analysis|BloodHound Attack Path Analysis]] — the AD-world enumeration stage.
- [[tier-zero-administration-and-paw|Tier 0 Administration]] — the structural defense that starves stages 4–5.
- [[detect-bloodhound-collection|Detect BloodHound Collection]] — the defender pair for the AD enumeration stage.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — the defender stitching loop stages into one kill chain.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the meta-frame; the loop is the offensive half.

### Suggested future atomic notes

- living-off-the-land-and-edr-evasion
- c2-and-command-and-control-tradecraft
- initial-access-techniques
- [[identity-attack-paths-across-idps]]
- detect-the-operator-loop

> Future atomic notes are listed as `<span class="unresolved-link" title="Unpublished or unresolved: wikilinks">wikilinks</span>` even when the target file does not exist yet, so they register as forward-links in Obsidian.

## References

- **Foundational:** MITRE ATT&CK Enterprise Matrix (the tactic sequence underpinning the loop) — https://attack.mitre.org/matrices/enterprise/
- **Research / Deep Dive:** Paul Pols — The Unified Kill Chain (end-to-end attack-phase synthesis) — https://www.unifiedkillchain.com/
- **Foundational:** Lockheed Martin — Cyber Kill Chain — https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html
