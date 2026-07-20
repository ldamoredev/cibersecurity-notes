---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Must-Know 30 — The Minimum Viable Security Literacy

The 200+ notes in this atlas are the long form. This is the **short form**: 30 notes that any IT person, developer, or junior security practitioner should be able to explain in 90 seconds each.

If you can do that for all 30, you have a working security model — not a complete one, but a working one. Everything else in the atlas is *depth* on top of this *breadth*.

**How to read this list:**
- The grouping mirrors the Phase 0 → Phase 1 → Phase 2 ordering, but each entry can be read on its own.
- Each entry has one line of *why this matters to everyone* — that line is the point, not the title.
- Notes marked *(future)* are seeded but not yet written; safe to skip on first pass.

---

## Mindset (4)

1. [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|What is cybersecurity (and why not a tool list)]] — fixes the most common newcomer error before the rest of the list lands.
2. [[cia-triad-and-what-it-actually-decides|CIA triad as a decision tool]] — name the property under threat first, before reasoning about controls.
3. [[threat-modeling-quickstart|Threat modeling quickstart]] — the 4 questions + STRIDE pass that takes an hour and changes how you read tickets.
4. [[attacker-defender-duality-as-a-learning-tool|Attacker-defender duality]] — every topic in security is a pair; studying one half plateaus you.

## Networking substrate (6)

1. [[tcp-ip-basics|TCP/IP basics]] — without this, every other networking note is memorization.
2. [[ports-and-services|Ports and services]] — what "open port" actually means, beyond Nmap output.
3. [[dns-resolution|DNS resolution]] — DNS is half of every attack story and half of every fix.
4. [[http-overview|HTTP overview]] — the protocol you debug for the rest of your career.
5. [[tls-https|TLS/HTTPS]] — what TLS actually proves (and what it does not).
6. [[reverse-proxies|Reverse proxies]] — modern apps are mediated; this is where trust gets misplaced.

## Web surface (5)

1. [[broken-access-control|Broken access control]] — the #1 web vulnerability class in every real-world study.
2. [[sql-injection|SQL injection]] — the canonical injection class; understanding it transfers to every other injection.
3. [[ssrf|SSRF]] — the bug that turns "the server fetches a URL for me" into cloud compromise.
4. [[xss|XSS]] — the browser-trust vulnerability everyone has heard of and few have internalized.
5. [[csrf|CSRF]] — taught as "old", still alive in every poorly-designed admin panel.

## Cryptographic correctness (4)

1. [[hashing-vs-encryption-vs-signing|Hashing vs encryption vs signing]] — the distinction that fixes half of all crypto questions.
2. [[password-hashing|Password hashing]] — bcrypt/scrypt/argon2 and why MD5/SHA-256 on passwords is a bug.
3. [[aead-and-nonce-misuse|AEAD and nonce misuse]] — modern encryption gives you confidentiality *and* integrity; understanding why matters.
4. [[jwt-cryptographic-correctness|JWT cryptographic correctness]] — JWTs are right or they are theatre; almost no one validates them correctly on first attempt.

## Offense / defense pair (5 — read each row together)

1. [[host-and-port-discovery|Host and port discovery]] ↔ [[scan-anomaly-detection-and-fingerprint-analysis|Scan anomaly detection]] — the most basic recon move and what it looks like to defenders.
2. [[nmap-scanning|Nmap scanning]] ↔ [[network-telemetry-sources-and-visibility|Network telemetry sources and visibility]] — what an Nmap scan is and where it shows up in your logs.
3. [[active-recon|Active recon]] ↔ [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS and behavioral detection pipelines]] — how attackers enumerate and how defenders catch the pattern, not the payload.
4. [[enumeration|Enumeration]] ↔ [[behavioral-detection-vs-signature-detection|Behavioral vs signature detection]] — the two ways of catching the same activity and why behavioral wins in 2026.
5. [[cloaking-and-security-evasion|Cloaking and security evasion]] ↔ [[detection-evasion-myths-and-modern-limitations|Detection evasion myths]] — what evasion actually buys an attacker and what it does not.

## Practical capability (3)

1. [[threat-modeling-quickstart|Threat modeling quickstart]] *(re-read)* — the only entry that appears twice. It is the single highest-leverage habit on this list.
2. [[exploit-sqli|Playbook: exploit SQLi]] — read one offensive playbook end-to-end to see how concept becomes procedure.
3. [[run-scan-pipeline|Playbook: run scan pipeline]] — the engagement-level recon workflow tying Phase 1-3 together.

## Always-on (3)

1. [[index|Privacy, Anonymity & OPSEC]] *(branch index)* — at minimum the threat-model and account-correlation notes; the rest is depth.
2. [[index|DevSecOps]] *(branch index)* — at minimum the secrets-management and supply-chain notes if you touch CI/CD.
3. [[index|Cloud Security]] *(branch index)* — at minimum the IAM-boundaries and metadata-endpoints notes if your systems run in cloud.

---

## How to use this list

- **As a pre-test.** Before reading anything new, scan the 30 entries and rate yourself "could explain in 90 seconds" / "could not". Your gaps *are* your reading list.
- **As a quarterly refresh.** Senior practitioners drift. Re-rate yourself every quarter; the drift directions are diagnostic.
- **As an interview prep.** Most "junior security engineer" / "AppSec engineer" / "detection engineer" interviews probe a subset of these 30 directly.
- **As a teaching index.** Onboarding a junior teammate? This is the curriculum. Track which of the 30 they have internalized.

This list is **deliberately short**. The hard part of curating it was not picking 30 — it was leaving out the next 30. The atlas is depth on top of these; the next 30 (database security, Kubernetes hardening, AD/Kerberos basics, EDR internals, IR/forensics, malware analysis basics, secure SDLC governance) live in the branches, reachable from here.

---

## Related navigation

- [[start-here|Start Here]] — persona-driven triage page.
- [[index|Cybersecurity Index]] — full branch listing.
- [[index|Foundations]] — Phase 0 entry.
