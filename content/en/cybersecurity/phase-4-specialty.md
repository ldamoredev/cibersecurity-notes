---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Phase 4 — Specialty Tracks (Pick What Your Job Demands)

Phase 4 is the **only phase you do not read linearly**. By design, it is job-context-chosen: you pick the specialty your role actually requires, learn it deeply enough to be effective, and revisit the others only when your work expands into them.

Generalists who try to read all four Phase 4 branches in parallel produce shallow knowledge of all four and depth in none. The specialist path is the right path here.

Six tracks, each with its own persona, curated path, and entry conditions:

> **API Security · Cloud Security · DevSecOps · Wireless Security · Identity & Active Directory · Binary Exploitation**

Each track assumes you have completed Phases 0–2 first-pass; some assume Phase 3 too. Track entry conditions are stated explicitly. **The Binary Exploitation track has the strongest external prerequisites** (C/C++ literacy, debugger fluency, x86-64 baseline) — see Track F.

---

## Track A — API Security

**Pick this if:** you build, test, or operate APIs (REST, GraphQL, gRPC). Most modern web/mobile/SaaS engineering touches this.

**Entry conditions:**
- Phase 1 first-pass complete (especially [[http-overview|HTTP overview]], [[http-headers|HTTP headers]], [[tls-https|TLS/HTTPS]]).
- [[index|Web Security]] basics complete — APIs inherit most of the web threat model.

**First-pass path (8 of 14 notes):**

1. **[[api-security-top-10|API Security Top 10]]** — the OWASP API canon; the right entry point because it frames every subsequent note.
2. **[[api-inventory-management|API Inventory Management]]** — you cannot secure APIs you do not know about. Inventory is the first capability.
3. **[[broken-object-level-authorization|Broken Object Level Authorization (BOLA)]]** — the #1 API vulnerability class by real-world frequency. IDOR's API-shaped sibling.
4. **[[broken-function-level-authorization|Broken Function Level Authorization]]** — admin/role boundary failures in API routing.
5. **[[broken-object-property-level-authorization|Broken Object Property Level Authorization]]** — fine-grained field-level authorization; closes the gaps the previous two leave open.
6. **[[broken-authentication|Broken Authentication]]** — token issuance, refresh, validation, rotation failures.
7. **[[jwt-attacks|JWT Attacks]]** — the most common token-trust failures, paired with [[jwt-cryptographic-correctness|JWT Cryptographic Correctness]] from Phase 1.
8. **[[excessive-data-exposure|Excessive Data Exposure]]** — APIs that return more than they should; the data-minimization failure.

**Extended (6 more):** [[api-auth-flaws|API auth flaws]], [[api-rate-limiting|API rate limiting]], [[authorization|Authorization]], [[token-lifecycle|Token lifecycle]], [[mass-assignment|Mass assignment]], [[polymorphic-deserialization|Polymorphic deserialization]].

**You are done with first-pass API when:** given any API endpoint, you can walk it through the 8 notes above as a checklist and articulate which of the 8 controls it implements correctly, which it implements weakly, and which it skips.

---

## Track B — Cloud Security

**Pick this if:** your systems run in cloud (AWS, GCP, Azure, multi-cloud) and the security boundaries you care about live in cloud control planes, not on-prem network gear.

**Entry conditions:**
- Phase 1 first-pass complete.
- [[index|Cryptography]] at least through [[hashing-vs-encryption-vs-signing|hashing vs encryption vs signing]] — IAM and keys reasoning depends on it.

**First-pass path (6 of 10 notes):**

1. **[[cloud-security-basics|Cloud Security Basics]]** — shared-responsibility model and what the cloud provider actually guarantees vs what you own.
2. **[[cloud-iam-boundaries|Cloud IAM Boundaries]]** — IAM is the cloud security primary control. Everything else is downstream.
3. **[[cloud-metadata-security|Cloud Metadata Security]]** — the metadata endpoint is the single most-attacked cloud surface; SSRF + cloud metadata = compromise.
4. **[[cloud-network-boundaries|Cloud Network Boundaries]]** — security groups, VPC peering, transit gateways, and how networking trust translates to cloud.
5. **[[cloud-secrets-management|Cloud Secrets Management]]** — short-lived credentials, KMS, secret rotation, why hard-coded keys are the canonical cloud failure.
6. **[[public-cloud-storage-exposure|Public Cloud Storage Exposure]]** — S3-bucket-style misconfiguration, by frequency the most-found public cloud finding.

**Extended (4 more):** [[cloud-logging-and-detection|Cloud logging and detection]], [[cloud-dns-and-certbot|Cloud DNS and Certbot]], [[ssh-access-to-cloud-hosts|SSH access to cloud hosts]], [[cloud-lab-infrastructure|Cloud lab infrastructure]].

**You are done with first-pass Cloud when:** for any cloud workload, you can walk its IAM role / network exposure / metadata reachability / secret-handling / storage exposure and assess each in under 10 minutes against the 6 notes above.

---

## Track C — DevSecOps

**Pick this if:** you own (or contribute to) a CI/CD pipeline, release process, container build, or supply-chain control. This track is increasingly non-optional for backend / platform / SRE roles.

**Entry conditions:**
- Phase 1 first-pass complete (especially [[digital-signatures|Digital signatures]] for artifact integrity reasoning).
- Phase 2 first-pass helpful but not strictly required.

**First-pass path (7 of 12 notes):**

1. **[[secure-by-design|Secure by Design]]** — the philosophy that drives every other note; without it the rest become checklists.
2. **[[ci-cd-hardening|CI/CD Hardening]]** — the build pipeline is part of the attack surface. This note names what to harden first.
3. **[[secrets-management|Secrets Management]]** — the canonical CI/CD failure. Hard-coded keys, exposed logs, leaked tokens.
4. **[[supply-chain-security|Supply Chain Security]]** — the threat model that motivates SBOM, signing, and provenance.
5. **[[sbom-and-provenance|SBOM and Provenance]]** — how to know what you are actually shipping. SLSA, Sigstore, in-toto.
6. **[[dependency-risk|Dependency Risk]]** — the open-source dependency surface as a first-class threat.
7. **[[container-security|Container Security]]** — image, runtime, and orchestration layer threats.

**Extended (5 more):** [[artifact-integrity|Artifact integrity]], [[image-scanning|Image scanning]], [[branch-protection-and-release-controls|Branch protection and release controls]], [[nist-ssdf|NIST SSDF]], [[asvs-as-dev-process-input|ASVS as dev process input]].

**You are done with first-pass DevSecOps when:** you can [[threat-modeling-quickstart|threat-model]] your own CI/CD pipeline end-to-end and name the controls that protect each stage (commit → build → test → publish → deploy).

---

## Track E — Identity and Active Directory

**Pick this if:** you do red-team / pentest work in AD environments, you administer AD, you respond to identity-based incidents, or you work on identity-platform engineering (AD, Entra ID, hybrid). High-frequency relevance for enterprise security roles.

**Entry conditions:**
- Phase 1 first-pass complete (especially [[password-hashing|password hashing]] and [[symmetric-encryption-modes|symmetric encryption modes]] — AD credential attacks are KDF/encryption-economics problems).
- Phase 2 first-pass complete — AD attacks have *no* useful signature-based detection; behavioral framing is mandatory.

**First-pass path (4 notes, read in order):**

1. **[[bloodhound-attack-path-analysis|BloodHound and Attack Path Analysis]]** — the visibility layer. Tells you which AD attacks are worth doing and which defensive ACLs to fix first.
2. **[[as-rep-roasting|AS-REP Roasting]]** — the *pre-foothold* attack that requires no credentials, only usernames.
3. **[[kerberoasting|Kerberoasting]]** — the *post-foothold* attack against accounts with SPNs.
4. **[[dcsync-and-ntdsdit-extraction|DCSync and ntds.dit Extraction]]** — the endgame: recover every hash including `krbtgt`, enabling Golden Tickets and permanent domain compromise.

**Extended (seeded future notes):** Golden Ticket forgery, Silver Ticket persistence, Pass-the-Hash, DCShadow, krbtgt rotation, Exchange permission legacy, UAC flags, shadow credentials / PKINIT, Tier 0 administration / PAW.

**You are done with first-pass Identity & AD when:** given any AD environment, you can collect with BloodHound, identify the shortest path from any unprivileged user to Domain Admin, name the cheapest two ACE edges defenders should remove, and execute one offensive chain end-to-end against an authorized lab.

---

## Track D — Wireless Security

**Pick this if:** you work with Wi-Fi networks at any depth — corporate Wi-Fi assessment, branch-office security, wireless penetration testing, or building wireless products. Pick this *last* if your role is web/cloud/API; wireless is genuinely a specialty track.

**Entry conditions:**
- Phase 1 first-pass complete (especially [[tcp-ip-basics|TCP/IP basics]] and [[ports-and-services|Ports and services]] — Wi-Fi is L1/L2 underneath the same TCP/IP).
- Hardware: a Wi-Fi adapter that supports monitor mode is required for the labs in this track to be useful.

**First-pass path (5 of 10 notes):**

1. **[[wireless-security|Wireless Security]]** — the branch-level mental model: Wi-Fi as radio + frames + association + authentication.
2. **[[wifi-monitor-mode|Wi-Fi Monitor Mode]]** — the foundational capability; without monitor-mode capture the rest is theory.
3. **[[wpa-wpa2-handshakes|WPA/WPA2 Handshakes]]** — the canonical capture-and-crack target.
4. **[[wifi-deauthentication|Wi-Fi Deauthentication]]** — the move that turns "wait for a client to connect" into "force one to reconnect now". Foundational to handshake capture and evil-twin attacks.
5. **[[evil-twin-access-points|Evil Twin Access Points]]** — the rogue-AP attack that converts wireless surface into credential / session compromise.

**Extended (5 more):** [[wifi-wordlist-attacks|Wi-Fi wordlist attacks]], [[wep-security|WEP security]], [[mitm-on-local-networks|MITM on local networks]], [[arp-poisoning|ARP poisoning]], [[bettercap-workflows|Bettercap workflows]].

**You are done with first-pass Wireless when:** you can capture a WPA2 handshake from an authorized test network, crack it against a controlled wordlist, and articulate why your corporate Wi-Fi *is or is not* vulnerable to the same workflow.

---

## Track F — Binary Exploitation

**Pick this if:** you do vulnerability research, exploit development, security engineering for low-level systems software (OS kernels, hypervisors, browsers, language runtimes), CTF pwn-category competition, security-tooling authorship, or you maintain memory-unsafe code in any production context. **Strongest external prerequisites of any track** — this is the deepest technical specialty in the atlas by ladder distance from source code.

**Entry conditions:**
- Phase 1 first-pass complete.
- **C/C++ programming literacy** — the branch assumes you can read C, have a working mental model of stack frames and heap allocation, and are comfortable with a debugger (`gdb` / `lldb` / WinDbg). If not, work through *Practical Binary Analysis* or OpenSecurityTraining x86 / OS-internals first.
- **Linux + x86-64 baseline.** Most labs target Linux on x86-64. aarch64, macOS, and Windows specifics are called out per-note as they come up.
- Phase 2 first-pass useful but not strictly required (exploit detection lives mostly inside the branch's own mitigation notes plus the [[edr-network-observability-and-process-correlation|EDR / process correlation]] cross-link).

**First-pass path (2 notes, read in order):**

1. **[[memory-corruption|Memory Corruption]]** — the root concept, the 6-class taxonomy (stack overflow / heap overflow / use-after-free / double-free / out-of-bounds read / integer overflow), and the chain from bug to exploit primitive to code execution.
2. **[[stack-buffer-overflow|Stack Buffer Overflow]]** — the canonical worked example of class 1. The deep-dive that introduces stack layout, return-address control, the mitigation chain (canary → ASLR → DEP → CET → MTE → PAC), ROP-style reasoning, and the pwntools-shaped exploit-development workflow.

**Extended (seeded future notes):** Heap exploitation, use-after-free, double-free, info-leak primitives, ROP / ret2libc, ASLR / PIE leak chains, format-string bugs, exploit mitigations (the full landscape), stack canaries / shadow stacks / PAC, ARM MTE, CFI, ELF format, reverse-engineering loop, fuzzing with libFuzzer / AFL++, sanitizers (ASAN / MSAN / UBSan), symbolic execution with angr.

**You are done with first-pass Binary Exploitation when:** given a vulnerable C program, you can identify the bug class, locate the saved return address (or equivalent control-flow primitive), build a working exploit against an unmitigated build, articulate which mitigations defeat that simple exploit, and name at least two primitives you would chain to defeat them. The pwntools-shaped exploit script for a basic stack-overflow CTF challenge should be a 20-line task, not an afternoon.

---

## How Phase 4 connects back to earlier phases

| Phase 4 track | Strongest Phase 0–3 dependencies |
| --- | --- |
| API Security | Web Security (Phase 1), JWT correctness (Phase 1 Crypto), Broken Access Control + IDOR playbook (Phase 3) |
| Cloud Security | Networking + Crypto (Phase 1), SSRF + metadata endpoints (Phase 1 Web), Investigate-SSRF playbook (Phase 3) |
| DevSecOps | Crypto digital signatures + AEAD (Phase 1), threat-modeling (Phase 0), every Phase 2 pair for "is my pipeline detectable" thinking |
| Wireless Security | Networking L1/L2/L3 (Phase 1), evasion and detection pairing (Phase 2) |
| Identity & Active Directory | Password hashing + symmetric encryption modes (Phase 1 Crypto), behavioral-vs-signature detection (Phase 2), attacker-defender duality (Phase 0) |
| Binary Exploitation | **C/C++ literacy + debugger fluency + x86-64 baseline (external prerequisites)**, threat-modeling at the systems-software layer (Phase 0), EDR-side detection telemetry (Phase 2) |

Pick the track whose dependencies you have already covered; that is the most efficient path.

---

## Picking more than one track

The Always-on parallel discipline of [[index|Privacy, Anonymity & OPSEC]] is your fifth track in spirit — it runs alongside every other one and never stops being relevant.

If your role demands two specialties (e.g., API + Cloud is common in modern backend engineering), do them **sequentially, not in parallel**. Finish first-pass on one, then start first-pass on the other. Parallel reading produces shallower retention in both.

---

## What's after Phase 4

There is no Phase 5 in this atlas. After Phase 4 specialty first-pass, you are operating as a specialist with full breadth across Phases 0–3 and depth in one (or two, sequentially) specialty area. The next learning move is **outside this atlas**:

- **Real engagements** under authorization — bug bounty programs, internal red/purple-team exercises, IR drills.
- **Defending a real system** that uses your specialty — building or operating one is the highest-leverage learning context.
- **The suggested future branches** in [[index|Cybersecurity Index]] (mobile, reverse-engineering, social-engineering, AI/agent-security) — open when they become job-relevant.

The atlas structure ends here. Everything else is depth.

---

## Related navigation

- [[start-here|Start Here]] — persona-driven triage page (the personas there map onto the four tracks here).
- [[phase-1-substrate|Phase 1 — Substrate]] · [[phase-2-offense-defense|Phase 2 — Offense / Defense]] · [[phase-3-operator|Phase 3 — Operator surface]] — prior phase entry pages.
- [[index|Phase 0 — Foundations]] — mental models all four tracks assume.
- [[index|API Security Index]] · [[index|Cloud Security Index]] · [[index|DevSecOps Index]] · [[index|Wireless Security Index]] — full branch listings.
- [[index|Privacy, Anonymity & OPSEC]] — the parallel always-on discipline.
- [[must-know-30|Must-Know 30]] — cross-branch must-know list.
- [[index|Cybersecurity Index]] — full atlas roadmap.
