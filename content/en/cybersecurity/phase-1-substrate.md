---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Phase 1 — Substrate (How Things Actually Work)

You have finished [[index|Phase 0 — Foundations]] and have the four mental models: *cybersecurity is not a tool list*, *CIA as a decision tool*, *threat modeling as a reflex*, *attacker-defender duality as the meta-frame*. Phase 1 is where those abstractions land in real systems.

The substrate is **3 branches stacked in order**:

> **Networking → Web Security → Cryptography.**

Networking comes first because it is the substrate of everything else. Web Security comes second because it is the daily surface most IT people touch. Cryptography comes third because it is the correctness layer — and it is only meaningful after TLS, sessions, and JWTs are concrete enough to motivate it.

This page is the **curated path** through the 62 atomic notes in those three branches. You do not need to read all 62. You need the right 12 first, then the right 25, then everything else as depth.

---

## First-pass reading order (12 notes, ~2 weeks of casual reading)

The minimum sequence that gives you a working substrate model. Read in order — each note depends on the previous one.

### Networking — 5 notes

1. **[[tcp-ip-basics|TCP/IP basics]]** — Without this, every other networking note is memorization. Names what packets *are* and how they get from A to B.
2. **[[ports-and-services|Ports and services]]** — What "open port" actually means, beyond Nmap output. The first half of every reachability question.
3. **[[dns-resolution|DNS resolution]]** — DNS is half of every attack story and half of every fix. Name resolution is its own trust system layered on top of IP.
4. **[[http-overview|HTTP overview]]** — The protocol you debug for the rest of your career. Everything in Web Security is HTTP at the wire.
5. **[[tls-https|TLS/HTTPS]]** — What TLS actually proves (channel confidentiality + integrity + server authenticity), and what it does *not* (no client-trust, no end-to-end). This note is the bridge into Cryptography.

### Web Security — 4 notes

1. **[[broken-access-control|Broken access control]]** — The #1 web vulnerability class in every real-world study. Most "we got hacked" stories reduce to this.
2. **[[sql-injection|SQL injection]]** — The canonical injection class. Understanding it transfers to command injection, LDAP injection, NoSQL injection, template injection, every other "user input got interpreted as code" bug.
3. **[[xss|XSS]]** — The browser-trust vulnerability everyone has heard of and few have internalized. Teaches you what "context" means in security.
4. **[[ssrf|SSRF]]** — The bug that turns "the server fetches a URL for me" into cloud compromise. Demonstrates how a single trusted boundary failure cascades.

### Cryptography — 3 notes

1. **[[hashing-vs-encryption-vs-signing|Hashing vs encryption vs signing]]** — The distinction that fixes half of all crypto confusion. Maps directly to the CIA triad you learned in Phase 0: hashing for integrity, encryption for confidentiality, signing for integrity + authenticity.
2. **[[password-hashing|Password hashing]]** — bcrypt / scrypt / argon2 and *why* using `MD5` or `SHA-256` on passwords is a bug. Teaches you what a KDF is and why "it's still hashing" misses the point.
3. **[[aead-and-nonce-misuse|AEAD and nonce misuse]]** — Modern encryption gives you confidentiality *and* integrity in one primitive. Closes the loop on the "encryption ≠ security" misconception named in [[cia-triad-and-what-it-actually-decides|CIA Triad]].

**Stop here on first pass.** With these 12 notes you have a working model of the substrate. You can now move to Phase 2 (Offense + Detection paired) and return to Phase 1 for depth as it becomes relevant.

---

## Extended reading (after first pass, before deep Phase 2 work)

The next 13 notes that turn "working model" into "confident operator". Read these as need-driven, not linear.

### Networking depth — 6 notes

- **[[http-headers|HTTP headers]]** — What each header *means at the trust level*, not just "what value to set".
- **[[http-messages|HTTP messages]]** — Request/response structure deeply; necessary for understanding request smuggling, HTTP/2 attacks, header injection.
- **[[cookies-and-sessions|Cookies and sessions]]** — How web state actually persists and where session integrity is won or lost.
- **[[reverse-proxies|Reverse proxies]]** — Modern apps are mediated; this is where trust gets misplaced. Foundational for SSRF, header smuggling, and admin-panel exposure.
- **[[client-ip-trust|Client IP trust]]** — The single most common header-trust failure. Every "we use X-Forwarded-For" production bug lives here.
- **[[firewalls-and-network-boundaries|Firewalls and network boundaries]]** — What firewalls do, what they cannot do, and why "we have a firewall" is not a defense.

### Web Security depth — 5 notes

- **[[csrf|CSRF]]** — Often taught as "old", still alive in every poorly-designed admin panel. Teaches you what *cross-site request* trust actually means.
- **[[command-injection|Command injection]]** — The variant of SQLi where the interpreter is the operating system. Same mental model, different sink.
- **[[xxe|XXE]]** — XML external entity injection. Often forgotten, still common in legacy APIs and SAML flows.
- **[[open-redirect|Open redirect]]** — Looks trivial, chains into account takeover via OAuth state and phishing.
- **[[content-security-policy|Content Security Policy]]** — The browser-side defense that closes most XSS variants in modern apps.

### Cryptography depth — 2 notes

- **[[jwt-cryptographic-correctness|JWT cryptographic correctness]]** — JWTs are right or they are theatre. Almost no one validates them correctly on first attempt. Covers `alg:none`, algorithm confusion, missing `aud`/`iss` checks, key rotation.
- **[[certificate-validation-and-pinning|Certificate validation and pinning]]** — What TLS clients actually do (and skip) when they validate a cert. The bridge from "TLS works" to "TLS works against this threat model".

---

## How to read Phase 1 alongside Phase 0

Phase 0's mental models are not memorize-once-and-move-on. They are *lenses* you apply note by note.

For every Phase 1 note you read, force yourself to do the four Phase 0 reflexes:

1. **Name the CIA property under threat.** Is this a confidentiality, integrity, or availability problem? (Most Web Security notes are C+I; most TLS/crypto notes are channel C+I; most DNS/availability notes are A.)
2. **Walk the trust boundary.** Where does data leave one trusted component and enter another? That edge is where the bug lives.
3. **State the threat → control pair.** For each vulnerability, who is the adversary and what control would prevent the violation?
4. **Articulate both sides.** If you can name the attack but not the detection, your model of that note is incomplete and you have just discovered the next thing to read.

The notes will *feel* different than they did before Phase 0. That feeling is the point.

---

## What you can skip on first pass

Phase 1 has 62 notes; the first-pass 12 plus extended 13 = 25. The other 37 are depth — they are *not* less important, they are *more specialized*. Skip on first pass:

- **Wireshark / packet-analysis workflows** — tactical, not foundational. Return when you have a packet capture to analyze.
- **HTTP-header-trust-in-Node-Express** — language-specific. Return when you write Node code.
- **NAT and private networks** — useful, but unless you build network infrastructure, not first-pass.
- **Dangling DNS records, caching and security, packet analysis** — return when you do attack-surface mapping (Phase 3).
- **Most variant-XSS notes (DOM XSS, mutation XSS, etc.)** — depth on top of base XSS. Return when you do AppSec engagements.
- **Crypto deep dives** (`asymmetric-encryption-and-key-exchange`, `mac-and-hmac`, `digital-signatures`, `kdf-and-key-stretching`, `random-and-csprng-pitfalls`, `roll-your-own-crypto-failures`, `post-quantum-awareness`) — read once you have a real protocol or design to reason about.

This list is not a value judgment. It is a *first-pass prioritization* for the IT-person-entering-cyber learner. Senior practitioners eventually need most of these; nobody needs all of them at once.

---

## What's next

After the first-pass 12 (or the extended 25), you are ready for [[index|Phase 2 — Offense / Defense paired]]. Phase 2 is unique in this atlas: it is meant to be read **in pairs**, not as two separate branches. Every offensive note has a corresponding [[index|Detection Engineering]] note that teaches what the attack looks like from the other side. Read them together.

A future `cybersecurity/phase-2-offense-defense.md` entry-page will curate the paired reading order — until then, the [[index|offensive-security index]] and [[index|detection-engineering index]] are the right pair to read note-by-note.

---

## Related navigation

- [[start-here|Start Here]] — persona-driven triage page (some personas have a different Phase 1 emphasis).
- [[index|Phase 0 — Foundations]] — the orientation that this phase assumes.
- [[must-know-30|Must-Know 30]] — the cross-branch must-know list that overlaps with Phase 1 first-pass.
- [[index|Cybersecurity Index]] — full branch listing and roadmap.
