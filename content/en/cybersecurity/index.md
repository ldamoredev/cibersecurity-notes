---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cybersecurity Index

## Purpose

This is the root navigation page for the cybersecurity atlas.

The goal of this system is to move from:
- learning isolated security concepts

to:
- building a connected security knowledge graph
- understanding exposure, exploitation, and defense as one system
- linking concepts to practical workflows, playbooks, and engineering decisions

This atlas is structured to support:
- security learning
- practical testing
- architecture reasoning
- long-term retrieval and LLM-assisted workflows

---

## How this atlas is organized

The atlas is split into canonical branches.

### Orientation (start here)

The framework everything else assumes — read first.

- [[index|Foundations]] (Phase 0)
- [[start-here|Start Here]] — persona-driven triage page
- [[must-know-30|Must-Know 30]] — minimum viable literacy across branches

### Substrate (how things actually work)

Read in order. Networking is the substrate of everything else, Web Security is the daily surface, Cryptography is the correctness layer.

- [[index|Networking]]
- [[index|Web Security]]
- [[index|Cryptography]]

### Offense / Defense (paired)

Read note-by-note as pairs. Studying one half plateaus you.

- [[index|Offensive Security / Recon]]
- [[index|Detection Engineering]]

### Operator surface

What is actually exposed, where evidence comes from, and how concepts become repeatable procedures.

- [[index|Attack Surface Mapping]]
- [[index|OSINT]]
- [[index|Linux Privilege Escalation]]
- [[index|Security Playbooks]]

### Specialty tracks (job-context choice)

Pick what your job demands. These are not prerequisites for each other.

- [[index|API Security]]
- [[index|Cloud Security]]
- [[index|DevSecOps]]
- [[index|Wireless Security]]
- [[index|Identity and Active Directory]]
- [[index|Binary Exploitation]]

### Always-on (parallel personal discipline)

Not a phase. Read alongside everything else.

- [[index|Privacy, Anonymity & OPSEC]]

---

## Recommended study order

> **Roadmap v2 — landed 2026-05-10.** Reorganized for the IT-person-entering-cyber learner. Phase 0 names the mental models; Phase 1 teaches the substrate (Networking first because it is the substrate of everything else, then Web Security as the daily surface, then Cryptography once TLS/JWTs are concrete enough to motivate it); Phase 2 pairs Offensive Security with Detection Engineering note-by-note; Phase 3 turns concept into operator capability; Phase 4 is specialization chosen by job context, not as a prerequisite. Privacy, Anonymity & OPSEC is reframed as an always-on personal discipline, not a phase. See [[start-here|Start Here]] for the persona-driven triage page.

### Phase 0 — Orientation (start here)

1. [[index|Foundations]] — the mental models every other branch assumes you already hold.

### Phase 1 — Substrate (how things actually work)

> Entry page: [[phase-1-substrate|Phase 1 — Substrate]] — curated first-pass + extended path through Networking + Web Security + Cryptography.
> 1. [[index|Networking]] — the substrate of everything else.
> 2. [[index|Web Security]] — the daily surface most IT people touch.
> 3. [[index|Cryptography]] — the correctness layer; meaningful after TLS and sessions are concrete.

### Phase 2 — Offense / defense paired

> Entry page: [[phase-2-offense-defense|Phase 2 — Offense / Defense (Paired)]] — first-pass pairs + extended pairs, each with the paired-reading ritual.
> 4. [[index|Offensive Security / Recon]] — how attackers discover and validate.
> 5. [[index|Detection Engineering]] — read note-by-note paired with #4.

### Phase 3 — Operator surface

> Entry page: [[phase-3-operator|Phase 3 — Operator Surface]] — the workflow loop across surface mapping, OSINT, privesc, and playbooks, with a curated first-pass path.
> 6. [[index|Attack Surface Mapping]] — what is actually exposed.
> 7. [[index|OSINT]] — public-source evidence handling.
> 8. [[index|Linux Privilege Escalation]] — local boundary failures after a foothold.
> 9. [[index|Security Playbooks]] — concepts as repeatable procedures.

### Phase 4 — Specialty tracks (pick what your job demands)

> Entry page: [[phase-4-specialty|Phase 4 — Specialty Tracks]] — persona-shaped tracks (API / Cloud / DevSecOps / Wireless / Identity & AD / Binary Exploitation), each with its own entry conditions and curated path. Pick one — generalist parallel reading is the wrong move here.
> 10. [[index|API Security]]
> 11. [[index|Cloud Security]]
> 12. [[index|DevSecOps]]
> 13. [[index|Wireless Security]]
> 14. [[index|Identity and Active Directory]]
> 15. [[index|Binary Exploitation]]

### Always-on — Personal discipline (parallel, lifelong)

- [[index|Privacy, Anonymity & OPSEC]] — not a phase. Read alongside everything else, refresh whenever your threat model changes.

## Branch roles

### Foundations (Phase 0)

Explains:
- what cybersecurity actually is (and why it is not a tool list)
- the CIA triad as a *decision tool*, not a definition
- the 4-question / STRIDE threat-modeling reflex
- the attacker-defender duality as the meta-frame every other branch assumes

Phase 0 is the only branch every learner reads regardless of role.

### Networking

Explains:
- transport
- reachability
- HTTP behavior
- proxies
- internal vs external paths

This is the substrate for web, API, SSRF, request smuggling, and attack surface reasoning.

### Web Security

Explains:
- classic web vulnerability classes
- browser behavior
- sessions
- access control
- server-side exploit patterns

### Cryptography

Explains:
- hashes, encryption, MACs, signatures, key exchange, and CSPRNGs
- TLS/PKI, JWT signing, password hashing, and KDF correctness
- how nonce reuse, weak modes, algorithm confusion, and roll-your-own designs fail

This is the correctness layer under TLS, sessions, JWTs, MFA/passkeys, secrets management, and privacy tooling. Sits after Networking in the new study order because crypto is most meaningful once TLS and sessions are concrete.

### Wireless Security

Explains:
- Wi-Fi as radio, frame, association, and authentication behavior
- monitor-mode observation and packet capture
- WEP, WPA/WPA2 handshakes, and passphrase risk
- deauthentication, rogue access points, and local-network MITM

Specialty track in the new ordering — read when your job demands Wi-Fi-specific work.

### API Security

Explains:
- object-, function-, and property-level authorization
- token trust
- inventory drift
- machine-readable abuse patterns

### Cloud Security

Explains:
- cloud shared responsibility, identity, and safe lab boundaries
- IAM, metadata, storage, network, DNS/TLS, secrets, and logging controls
- how cloud misconfiguration becomes attack surface

### Attack Surface Mapping

Explains:
- what is actually exposed
- what is reachable
- what is discoverable
- what has drifted from intended design

### Offensive Security / Recon

Explains:
- how attackers discover
- how findings are validated
- how recon turns into testing

### Linux Privilege Escalation

Explains:
- how local Linux privilege boundaries fail after an authorized foothold
- how enumeration turns host clues into ranked escalation hypotheses
- how sudo, SUID/SGID, capabilities, scheduled jobs, PATH, kernel, and LinPEAS findings should be verified safely

### Privacy, Anonymity & OPSEC

Explains:
- how privacy tools change observer visibility and trust
- why VPNs are privacy-routing tools, not anonymity guarantees
- how metadata, accounts, browser state, files, and behavior leak identity
- how Tor, compartmentalized systems, encrypted communication, and secure deletion fit into a threat model

### OSINT

Explains:
- how public-source information is collected and evaluated
- how public clues become evidence instead of guesses
- how people, company, media, breach, and search data should be handled ethically

### DevSecOps

Explains:
- secure development workflow
- software supply chain
- CI/CD hardening
- release trust
- secrets, containers, and artifacts

### Detection Engineering

Explains:
- telemetry sources and visibility limits
- network observability, IDS/IPS pipelines, and behavioral correlation
- Zeek, Suricata, NetFlow/IPFIX, EDR, cloud, and endpoint-network joins
- why modern defense is behavioral and correlational rather than signature-only

### Security Playbooks

Explains:
- how to operationalize concepts
- how to test specific classes of weakness
- how to move from theory to repeatable procedure

## Reference registries

These are the source-of-truth notes for references in each branch.

- [[reference-registry-cryptography|Reference Registry — Cryptography]]
- [[reference-registry-networking|Reference Registry — Networking]]
- [[reference-registry-wireless-security|Reference Registry — Wireless Security]]
- [[reference-registry-web-security|Reference Registry — Web Security]]
- [[reference-registry-api-security|Reference Registry — API Security]]
- [[reference-registry-cloud-security|Reference Registry — Cloud Security]]
- [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]]
- [[reference-registry-osint|Reference Registry — OSINT]]
- [[reference-registry-devsecops|Reference Registry — DevSecOps]]
- [[reference-registry-detection-engineering|Reference Registry — Detection Engineering]]
- [[reference-registry-binary-exploitation|Reference Registry — Binary Exploitation]]
- [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]]
- [[reference-registry-offensive-security|Reference Registry — Offensive Security]]
- [[reference-registry-linux-privilege-escalation|Reference Registry — Linux Privilege Escalation]]
- [[reference-registry-privacy-anonymity-opsec|Reference Registry — Privacy, Anonymity & OPSEC]]
- [[reference-registry-playbooks|Reference Registry — Playbooks]]

---

## Working rules for the atlas

### Canonical notes

Each branch should use:
- one canonical `index.md`
- atomic notes with clear scope
- strong related-note links
- references aligned to the branch registry

### Playbooks

Playbooks should:
- operationalize concepts
- connect to the relevant canonical notes
- stay procedural, not conceptual

### Cross-branch links

Cross-branch links should:
- be meaningful
- explain mechanisms, trust boundaries, exploit flow, or control design
- stay selective rather than exhaustive

### Cleanup rule

When overlapping notes exist:
- preserve the canonical note
- archive weaker or older duplicates
- merge unique insights instead of losing them

---

## Current focus

The current mature branches, listed in the new study order:

- [[index|Foundations]] (Phase 0)
- [[index|Networking]]
- [[index|Web Security]]
- [[index|Cryptography]]
- [[index|Offensive Security / Recon]]
- [[index|Detection Engineering]]
- [[index|Attack Surface Mapping]]
- [[index|OSINT]]
- [[index|Linux Privilege Escalation]]
- [[index|Privacy, Anonymity & OPSEC]]
- [[index|Security Playbooks]]

This root index should remain a navigation and system note, not a giant summary note.

---

## Suggested future additions

Potential future branches:
- mobile-security
- reverse-engineering
- social-engineering
- ai-security / agent-security

These should only be added once their branch structure and reference registry are mature enough.
