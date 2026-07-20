---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Start Here — Cybersecurity Atlas Guide

You have landed on a cybersecurity atlas organized by phases, branches, and playbooks. This guide routes you to the right path based on **who you are right now**.

If you are not sure which persona fits, default to **"New to cybersecurity"** — the path costs nothing extra and the foundations apply to everyone.

---

## "I am new to cybersecurity"

You have used computers, you may work in IT, but you have never thought security-first as a discipline.

**Your path (4-8 weeks of casual reading):**

1. **Read [[index|Foundations]] (Phase 0) end-to-end.** This is the framework everything else assumes.
2. **Read [[phase-1-substrate|Phase 1 — Substrate]]** for the curated first-pass path through Networking → Web Security → Cryptography. Skip notes that go deeper than you need on first pass; you can return.
3. **Read the [[must-know-30|Must-Know 30]]** list to see where you are vs where you want to be.
4. **Open [[phase-2-offense-defense|Phase 2 — Offense / Defense (Paired)]] and read its first-pass pairs.** This is where the *real skill* starts compounding. The page makes the pairing operational so you actually read both sides instead of one.
5. **Stop trying to learn everything.** Specialize when you have a job context that demands it.

---

## "I am an IT admin / sysadmin / infrastructure engineer"

You run systems. You want to harden what you have and reason confidently about risk.

**Your path:**

1. **Phase 0 — [[index|Foundations]]** — non-negotiable.
2. **Networking first, in full:** [[index|Networking]] — most of it will be familiar, but the security framing of things you already know is the point.
3. **[[index|Attack Surface Mapping]]** — what is actually exposed from where.
4. **[[index|Offensive Security / Recon]]** — how attackers see your systems.
5. **[[index|Detection Engineering]]** — the half that makes you employable for security work, not just IT work.
6. **[[index|Linux Privilege Escalation]]** — if you run Linux servers, this is non-optional.
7. **Pick your specialty:** [[index|Cloud]] if you run cloud, [[index|Wireless]] if you run office networks, [[index|DevSecOps]] if you own a build pipeline.

---

## "I am a software developer"

You write code. You want to ship features that do not become headlines.

**Your path:**

1. **Phase 0 — [[index|Foundations]]** — the threat-modeling note in particular changes how you read tickets.
2. **[[index|Web Security]]** in full. If you build web/mobile apps, this is your daily surface.
3. **[[index|API Security]]** — likely your second daily surface.
4. **[[index|Cryptography]]** focused on the application-correctness notes: [[password-hashing|password hashing]], [[jwt-cryptographic-correctness|JWT correctness]], [[aead-and-nonce-misuse|AEAD]], [[certificate-validation-and-pinning|cert validation]].
5. **[[index|DevSecOps]]** — your build pipeline is part of the threat surface.
6. **Phase 2 pair — Offensive + Detection** — even one read-through changes how you write code.
7. **Reach into [[index|Security Playbooks]]** for the testing procedures you can actually run on your own code.

---

## "I am rebuilding fundamentals deliberately"

You have been in security or adjacent for a while and want to clean up your model rather than learn the next tool.

**Your path:**

1. **Phase 0 — [[index|Foundations]]** — yes, even if you "know it". The reflexes named there are what stop senior practitioners from plateauing.
2. **Phase 1 in full**, but reading for the *connections between notes* rather than the content of each note.
3. **Phase 2 read in pairs** — [[index|Offensive]] and [[index|Detection Engineering]] note-by-note. This is the senior move that most "experienced" practitioners have never actually done.
4. **Audit your own [[must-know-30|Must-Know 30]] gaps.** If you cannot explain any of the 30 in 90 seconds, that is your next reading.
5. **Read [[index|Cryptography]] for correctness, not for memorization.** Most "I know crypto" claims fail at AEAD, KDFs, or [[random-and-csprng-pitfalls|CSPRNG pitfalls]].
6. **Walk one real system you own** through [[threat-modeling-quickstart|Threat Modeling Quickstart]]. The exercise reveals which branch you should refresh next.

---

## "I want to break into security as a career"

You want a job in security and you are working backward from there.

**Your path:**

1. Read all four personas above. Your real path is a mix of "new to cybersecurity" (foundations) + the persona closest to your current job (IT admin / developer) + the rebuilder discipline.
2. **Phase 0 + Phase 1 + Phase 2** is the minimum portfolio of *understanding*. Without it you will be a button-pusher for any tool stack.
3. **[[index|Security Playbooks]]** is where understanding becomes capability. Pick three playbooks and execute them on owned/authorized targets until you can run them from memory.
4. **[[phase-4-specialty|Phase 4 — Specialty Tracks]]** — pick *one* track (API / Cloud / DevSecOps / Wireless) based on your job context. Generalists are valuable; "I am applying to every cyber job" candidates are not.
5. **[[index|Privacy, Anonymity & OPSEC]]** is professionally useful too — every offensive engagement, every IR investigation, every threat-intel job has OPSEC requirements.

---

## "I just want to read one thing"

Read [[what-is-cybersecurity-and-why-it-is-not-a-tool-list|What Is Cybersecurity, and Why It Is Not a Tool List]]. That note alone is worth more than most "Intro to cybersecurity" courses.

---

## Related navigation

- [[index|Cybersecurity Index]] — full branch listing and study order.
- [[index|Foundations]] — Phase 0 entry.
- [[must-know-30|Must-Know 30]] — the 30-note diagonal must-know cut across branches.
- [[index|Security Playbooks]] — concept into procedure.
