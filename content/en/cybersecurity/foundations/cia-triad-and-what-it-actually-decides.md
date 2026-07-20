---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# CIA Triad — What It Actually Decides

## Definition

The CIA triad — **Confidentiality, Integrity, Availability** — is the three-property model of what information security is trying to preserve. Confidentiality is "who can read". Integrity is "who can change without authorization, and would we detect it". Availability is "does the system work when needed". The triad's value is not as a definition to memorize but as a **decision tool**: naming the property under threat is the first move in any incident, design review, control choice, or vulnerability analysis.

## Why it matters

Every learner is told what the CIA triad is. Almost nobody is taught to use it as a reflex. The result is a generation of practitioners who answer "encrypt it" to questions that have nothing to do with confidentiality, or who treat all incidents as the same "security problem" instead of routing each to the controls that actually apply.

The triad matters because **most controls are aimed at one property, sometimes two, rarely all three**. Encryption is a confidentiality control — it does not, by itself, prevent tampering. Digital signatures are an integrity control — they do not hide anything. Rate limiting is mainly an availability control, sometimes a confidentiality control (preventing enumeration), and almost never an integrity control. If you cannot name which property a control serves, you cannot reason about whether you have the right controls for your threats.

The senior framing is that *threat modeling is fundamentally CIA-triage*: walk the system, name the assets, and for each asset ask which of the three properties matters most. The answer drives the rest of the engineering.

## How it works

The triad is **3 properties, each with its own control family and its own dominant adversary model**:

1.
**Confidentiality — who can read.**
   - Adversary goal: see information they are not authorized to see.
   - Control family: access control (authn + authz), encryption at rest, encryption in transit, key management, channel isolation, side-channel hardening, data minimization.
   - Failure mode: a leak — data is observed by someone who should not have observed it.
   - Detection signal: anomalous read patterns, unexpected egress, leaked credentials in scans.
2.
**Integrity — who can change without authorization, and would we detect it.**
   - Adversary goal: modify data or behavior in a way that is not authorized and goes undetected.
   - Control family: digital signatures, MACs, AEAD (authenticated encryption), version control, immutable storage, audit trails, code-signing, software-supply-chain controls.
   - Failure mode: a *tamper* — data or behavior is changed and the change either goes unnoticed or is attributed to the wrong actor.
   - Detection signal: signature/hash mismatch, unauthorized change to records, integrity-monitoring alerts.
3.
**Availability — does the system work when needed.**
   - Adversary goal: deny legitimate users access to the system or its data.
   - Control family: redundancy, capacity planning, rate limiting, DDoS protection, circuit breakers, graceful degradation, backup and disaster recovery, business-continuity planning.
   - Failure mode: an *outage* — the system is unreachable, slow, or has lost data with no recoverable copy.
   - Detection signal: latency spikes, error-rate spikes, traffic anomalies, backup-failure alerts.

The bug is not "we got hacked"; the bug is *we did not name which property mattered to which asset, so our controls protected the wrong thing*.

## Common misconceptions

### "Confidentiality is the most important of the three."

This is the most common newcomer instinct and it is wrong in many real contexts. The right answer depends on the asset:
- **Patient health records** → C dominates (HIPAA-style threat model).
- **Industrial control firmware / pacemaker firmware** → I dominates. A leaked copy is recoverable; a tampered copy can kill people.
- **Stock-exchange trading platform** → A dominates. Every minute of downtime costs millions; a single transaction leak is small in comparison.
- **Election integrity** → I dominates. Tampering with vote totals is the unrecoverable harm.
Mature security work *ranks the three per asset class*, then designs controls accordingly.

### "Encryption = security."

Encryption is a *confidentiality* control. Plain symmetric encryption (e.g., AES-CBC without a MAC) gives you no integrity — an attacker can flip bits in ciphertext and the decrypted result will be modified plaintext, undetected. This is exactly why modern protocols use [[aead-and-nonce-misuse|AEAD]] (authenticated encryption), which provides C *and* I in one primitive. Saying "we use TLS" tells you the channel is confidential and authenticated, not that the data inside is integrity-protected at rest.

### "The CIA triad is enough — it covers everything."

The triad is the load-bearing core, but extensions exist for good reason:
- **Authenticity** — was this message actually from the claimed sender? (Sometimes folded into integrity, but distinct in practice — digital signatures provide both.)
- **Non-repudiation** — can the sender deny having sent it? (Distinct from integrity; you can detect tampering without being able to prove who sent the original.)
- **AAA** — Authentication, Authorization, Accounting — operational expansion of confidentiality controls.
- **Parkerian Hexad** — adds Possession, Authenticity, Utility on top of CIA.
For most day-to-day work the triad is enough; for cryptographic protocol design or forensic-quality systems, you need the extensions. Knowing they exist is the senior move.

### "Availability isn't really security; it's an SRE / reliability problem."

Availability becomes a security problem the moment an adversary can *cause* the outage. A network outage from a misconfigured router is reliability; the same outage caused by a DDoS or a ransomware encryption event is security. The boundary is "is there an adversary?". Many modern attacks (ransomware, wiper malware, supply-chain sabotage) are pure-A attacks dressed up as something else.

### "Confidentiality and integrity are independent."

They are not. Encryption without integrity (the "MAC-then-encrypt vs encrypt-then-MAC" debates, the ECB-mode tampering attacks, the padding-oracle attacks against CBC) shows that a confidentiality-only control without integrity can *leak data anyway* because the attacker tampers with the ciphertext to force a side channel. This is why AEAD exists. See [[aead-and-nonce-misuse|AEAD and nonce misuse]].

## How to apply this

The triad turns into **4 reflexes** a learner should build:

1.
**Name the property first — before any other analysis.**
   When you read about an incident or vulnerability, force yourself to state explicitly: "this is a C breach" / "this is an I breach" / "this is an A breach" *before* reading the technical details. The discipline pays off across every branch of the atlas.

2.
**Tag every control with its property.**
   When you design or review a control, write next to it which of C/I/A it serves. If a control claims to serve all three, suspect it — most do not. The exercise reveals controls that are doing nothing for the property under threat.

3.
**Rank C/I/A per asset class, not globally.**
   For each asset (database, log stream, firmware, credential store), ask which of the three matters most. The answer drives the control budget. A control plan that treats every asset as "C-dominant" is a control plan that misallocates attention.

4.
**In incidents, the triage question is "which property is breached?".**
   That single question routes the response: a C breach goes to credential rotation, key revocation, leak containment. An I breach goes to verification of records, rollback to known-good state, attribution. An A breach goes to restoration, failover, root-cause analysis of the outage mechanism.

## Practical examples

- **SQL injection that leaks user rows** → C breach. Response: identify what leaked, notify, rotate any leaked credentials, fix the injection sink.
- **SQL injection that updates `is_admin=1` on another user's row** → I breach. Response: audit recent changes, roll back unauthorized writes, fix the sink, *and* check whether the integrity of any downstream system was contaminated.
- **SQL injection that runs `DROP TABLE users`** → A breach (and an I breach to backups). Response: restore from backup, fix the sink, audit what else used that account.
- **Stolen long-lived API token** → C breach (the attacker can read everything the token can read) + potentially I (if the token has write scopes). The C-vs-I split decides whether read-access logs alone tell the story.
- **Ransomware encrypting a fileserver** → A breach primarily (files unavailable) + C breach secondarily (attackers often exfiltrate before encrypting). Response is dominated by A: backups, restoration, business-continuity. C response is forensic: what was exfiltrated, who needs to be notified.
- **Tampering with signed log entries** → I breach. Often the *real* attack hiding behind something else — an attacker who can rewrite logs has already compromised the integrity of every downstream investigation that relies on those logs.
- **TLS certificate not validated by the client (skip-verify)** → C breach (eavesdropping possible) *and* I breach (MITM can inject content). Both, because the cert validation underpins both properties of the channel.
- **DDoS against a payment gateway during Black Friday** → pure A breach. Cost is measured in revenue, not data. A defense that focuses on "the data is encrypted" misses the entire threat.

## Related notes

- [[what-is-cybersecurity-and-why-it-is-not-a-tool-list]] — the framework this note sits inside.
- [[threat-modeling-quickstart]] *(future)* — uses the triad as the first triage question.
- [[attacker-defender-duality-as-a-learning-tool]] *(future)* — each property has its own offense/defense pair.
- [[hashing-vs-encryption-vs-signing|Hashing vs Encryption vs Signing]] — concrete C/I/authenticity distinction in primitives.
- [[aead-and-nonce-misuse|AEAD and nonce misuse]] — why modern protocols give C and I together.
- [[digital-signatures|Digital Signatures]] — the canonical I + authenticity control.
- [[mac-and-hmac|MAC and HMAC]] — integrity primitive.
- [[broken-access-control|Broken Access Control]] — most C breaches in web apps reduce to this.
- [[index|Detection Engineering]] — each property has its own detection telemetry.

### Suggested future atomic notes

- parkerian-hexad-and-when-the-triad-is-not-enough
- aaa-authentication-authorization-accounting
- non-repudiation-and-when-it-actually-matters
- ranking-cia-per-asset-class

## References

- **Foundational:** NIST SP 800-12 — An Introduction to Information Security (defines CIA as the organizing model) — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-12r1.pdf
- **Foundational:** ISO/IEC 27000:2018 — Information security management systems overview (canonical CIA definition in international standards) — https://www.iso.org/standard/73906.html
- **Research / Deep Dive:** Donn B. Parker — Toward a New Framework for Information Security (Parkerian Hexad, the standard critique of the triad's limits) — https://onlinelibrary.wiley.com/doi/10.1002/9780470051986.j0027
