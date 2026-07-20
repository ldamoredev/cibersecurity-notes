---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Detect BloodHound Collection

> *Playbook structure (Goal / Assumptions / Prerequisites / Detection steps / Validation clues / Mitigation / Logging / Operational safety), matching the trio siblings [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] and [[detect-dcsync-and-ntdsdit-access|Detect DCSync and NTDS.dit Access]] — not the 11-section atomic-note template. This is the third of the three-note AD-detection trio.*

## Goal

Detect Active Directory enumeration by BloodHound-family collectors ([[bloodhound-attack-path-analysis|SharpHound / BloodHound-CE]] and successors like SOAPHound) early enough to identify the **source host, source principal, and collection method** before the operator converts the resulting attack graph into a Kerberoast → DCSync → Domain Admin chain — and with enough fidelity to survive the realistic 2026 evasions (paged/throttled LDAP, DCOnly collection, AD Web Services abuse, custom in-memory collectors).

## Assumptions

- you collect Domain Controller telemetry (Windows Security events and/or Microsoft Defender for Identity sensor data) into a SIEM with ≥ 30 days retention
- you can deploy at least one honeytoken object (a decoy user or computer with attractive-looking ACLs that no legitimate process ever reads)
- the goal is **detect, contain, investigate** — collection is reconnaissance, not exploitation; you are racing the operator's *next* step, not patching a bug
- BloodHound collection is frequently a *legitimate* blue-team / IAM activity in your environment — so detection must distinguish authorized inventory runs from adversary recon, which means an allowlist of sanctioned collector hosts/accounts is mandatory

## Prerequisites

- **LDAP query visibility.** Either Defender for Identity (which models LDAP reconnaissance natively) or Directory Service diagnostic LDAP logging (Event **1644**, gated behind the `Field Engineering` / `15 Field Engineering` registry diagnostic and the `Expensive/Inefficient` thresholds) on DCs. Raw 1644 is high-volume — prefer Defender for Identity or ETW where available.
- **SAMR / SRVSVC visibility.** Event **4661** (a handle was requested to a SAM/DS object) with the right SACL, plus **5145** (network share / named-pipe `\srvsvc`, `\samr` access) for session/local-group enumeration. See [[windows-event-logs|Windows Event Logs]] for the audit-policy preconditions.
- **Endpoint telemetry.** [[edr-network-observability-and-process-correlation|EDR / Sysmon]] for process lineage, .NET assembly load (SharpHound is C#), and **outbound connection fan-out** (Session/LoggedOn collection hits many hosts).
- **AD Web Services (ADWS) visibility.** Connection logging to TCP **9389** on DCs — the SOAPHound evasion path that bypasses port-389 LDAP detection.
- **A baseline** of who legitimately performs directory-wide reads (IAM tooling, vuln scanners, the blue team's own BloodHound runs) and from which hosts.

## Detection steps

> *This playbook is the defender pair for [[bloodhound-attack-path-analysis|BloodHound Attack Path Analysis]]. Read offense + defense together per the [[attacker-defender-duality-as-a-learning-tool|paired-reading discipline]]. BloodHound collection is the **recon** that precedes the [[detect-kerberoasting-and-as-rep-roasting|roasting]] and [[detect-dcsync-and-ntdsdit-access|DCSync]] stages — correlate across all three.*

### Phase 0 — Baseline and decoys (do once, refresh quarterly)

1. **Allowlist sanctioned collectors.** Record the hosts/accounts that legitimately enumerate the directory (IAM, scanners, blue-team BloodHound). Everything off this list reading the whole directory is suspect.
2. **Plant honeytoken objects.** Create a decoy user and computer that *look* privileged (attractive group membership, a juicy-looking ACL, an SPN) but are used by nobody. SharpHound's ACL/Default collection reads every object's `ntSecurityDescriptor` — so any read of the decoy's security descriptor, or any TGS/auth against it, is adversary activity by construction. This is the highest-fidelity, near-zero-FP signal in the playbook.
3. **Baseline LDAP query shape per principal.** Normal apps query *narrow* slices (a few objects, specific attributes). BloodHound queries *broad* slices: all `user`/`computer`/`group` objects with the ACL-relevant attribute set (`ntSecurityDescriptor`, `member`, `memberOf`, `servicePrincipalName`, `userAccountControl`, `msDS-AllowedToActOnBehalfOfOtherIdentity`).

### Phase 1 — Detect the collection signature

Operator signature: **one source principal reads a large, ACL-heavy cross-section of the directory in a short window, often followed by SAMR/SRVSVC fan-out to many hosts.**

1. **Honeytoken read / auth (highest fidelity).** Any LDAP read of the decoy object's security descriptor, or any authentication to the decoy account, is immediate high severity. No false positives by design.
2. **Defender for Identity reconnaissance alerts.** Surface and tune *Security principal reconnaissance (LDAP)*, *User and Group membership reconnaissance (SAMR)*, and *Network mapping / user-and-IP reconnaissance (SMB)*. These are purpose-built and far lower-FP than raw event rules.
3. **Broad-LDAP behavioral rule.** Alert when one principal/source pulls ACL-relevant attributes across ≥ N object classes within a short window, where the source is not on the Phase 0 allowlist. Tune N to your baseline.
4. **SAMR + SRVSVC fan-out rule.** Alert when one non-admin workstation enumerates local group membership (SAMR) or sessions (`NetSessionEnum` via `\srvsvc`) against many hosts — the Session/LoggedOn collection signature. Event 4661/5145 clustering by source.
5. **In-memory .NET collector signal.** Sysmon DLL/CLR load of `System.DirectoryServices` / ADWS assemblies from an unusual process, or AMSI/.NET ETW telemetry, catches renamed or fileless SharpHound that leaves no `SharpHound.exe` on disk.

### Phase 2 — Detect the evasions (the 2026 reality)

The default tool is the easy case. The realistic operator evades:

1. **Paged / throttled / jittered LDAP (`--Throttle`, `--Jitter`, small page size).** Defeats volumetric thresholds. **Counter:** rely on *diversity* (how much of the directory was touched, cumulatively) and honeytoken reads, not events-per-minute. Low-and-slow still eventually reads the decoy.
2. **DCOnly collection.** Skips host touch entirely — only LDAP + SAMR to the DC, no Session/SRVSVC fan-out. Removes the Phase 1 rule-4 signal. **Counter:** Phase 1 rules 1–3 (honeytoken, Defender for Identity LDAP, broad-LDAP behavioral) still fire because the directory read still happens.
3. **SOAPHound / AD Web Services abuse.** Collects via **ADWS (TCP 9389)** instead of LDAP/389, bypassing Event 1644 and LDAP-port-focused detection. **Counter:** monitor ADWS connections to DCs from non-admin/non-management hosts; the honeytoken read fires regardless of transport.
4. **Custom collectors / BOFs / `ldapsearch` + offline parsing (e.g., bofhound).** No BloodHound binary at all. **Counter:** the detection must key on the *directory-access behavior and the honeytoken*, never on the tool name or hash — block-listing `SharpHound.exe` is defeated by a rename.

### Phase 3 — Investigation and response

1. **Identify the source.** Pull source host/IP and principal from the triggering event (Defender for Identity entity, 4661/5145 `SubjectUserName`/`IpAddress`, or ADWS connection log).
2. **Build the timeline.** Pull all directory-access events from that source in the last 24–72h. Determine the collection method (DCOnly vs Session vs ACL vs ADWS) from which signals fired.
3. **Look downstream for the next stage.** If the same source subsequently performs [[detect-kerberoasting-and-as-rep-roasting|Kerberoasting / AS-REP roasting]] or touches replication rights ([[detect-dcsync-and-ntdsdit-access|DCSync]]), you have a confirmed recon→escalation kill chain, not isolated noise.
4. **Scope what was learned.** Assume the operator now holds the full attack graph: every path to Tier 0 visible from the collecting principal is now known to them. Prioritize closing the *shortest* paths the graph would have revealed.
5. **Contain.** Disable/contain the source principal and host pending investigation; if a sanctioned collector account was compromised, treat its credentials as burned.

## Validation clues

- **Honeytoken fired:** any read of the decoy's security descriptor or auth to the decoy account — confirmed adversary, investigate immediately.
- **High-confidence collection:** one off-allowlist principal reads ACL attributes across users+computers+groups+GPOs+trusts in one window.
- **DCOnly signature:** broad LDAP + SAMR to the DC with *no* corresponding host-session fan-out.
- **SOAPHound signature:** ADWS (9389) connection from a workstation that has no management role, with directory-wide read volume.
- **Kill-chain confirmation:** the collecting source later roasts service accounts or requests replication — recon followed by credential access from the same origin.

## Mitigation / remediation

Durable controls, ordered by effectiveness:

- **Honeytokens as a standing control.** Decoy objects are the cheapest near-zero-FP detection for ACL-based enumeration and should be permanent, not incident-only.
- **Reduce the attack graph itself.** The most durable defense is having fewer dangerous paths to find: remove excessive ACLs, collapse nested group sprawl, and enforce [[tier-zero-administration-and-paw|Tier 0 separation]] so that even a complete collection reveals no short path to Domain Admin. Detecting collection matters less if the graph is clean.
- **Enable and tune Defender for Identity** (or equivalent) reconnaissance alerts rather than building raw 1644 rules from scratch.
- **Restrict ADWS exposure.** Limit which hosts may reach DC port 9389; it is a management interface, not a workstation need.
- **LDAP query auditing on Tier 0** where Defender for Identity is unavailable, accepting the volume cost.

### What does not work as a primary defense

- **Block-listing `SharpHound.exe` / known hashes.** Renamed, recompiled, in-memory, BOF, and `ldapsearch`-based collection all defeat it. The directory-read behavior is the surface, not the binary.
- **Blocking LDAP.** LDAP *is* how AD works; you cannot block it. (And SOAPHound doesn't use port 389 anyway.)
- **Volumetric-only thresholds.** Throttled/jittered/low-and-slow collection slips under any rate limit; diversity-of-objects-read and honeytokens are the durable signals.
- **Trusting that "BloodHound needs admin".** It does not — any authenticated domain user can run most collection methods. "Only admins can enumerate" is false.
- **Preventing collection at all.** Any authenticated principal can read most of the directory by design. The realistic posture is *detect collection + shrink the graph*, not *prevent reads*.

## Logging / forensics

- **Retain DC directory-access and Defender for Identity data ≥ 90 days.** Collection → graph analysis → escalation chains often span days/weeks.
- **Tag every alert with:** source host/principal, collection method inferred (DCOnly/Session/ACL/ADWS), allowlist status, and whether a honeytoken was touched.
- **Capture the ADWS/LDAP connection metadata** (source, duration, byte volume) — useful for distinguishing a sanctioned full inventory run from adversary recon.
- **Correlate across the trio** via [[attack-path-correlation-and-kill-chain-observability|attack-path correlation]]: collection from host X, then roasting from host X hours later, then a cracked service account authenticating from host Y is one kill chain, not three alerts.

## Operational safety

- **always** maintain the sanctioned-collector allowlist — without it, every legitimate IAM/blue-team BloodHound run is a false positive and the rule gets disabled.
- **always** validate honeytoken detections end-to-end in a lab before relying on them; a decoy nobody monitors is worthless.
- **never** treat "no SharpHound.exe found" as "no collection occurred" — assume fileless/custom collection and pivot to behavior + honeytoken evidence.
- **always** test detections against the Phase 2 evasions (DCOnly, throttled, SOAPHound) on an authorized internal lab — a rule that only catches default SharpHound is theater against a real operator.
- **never** rely on a single rule; honeytoken + Defender-for-Identity recon alert + broad-LDAP behavioral together produce far higher fidelity than any one alone.

## Related notes

- [[bloodhound-attack-path-analysis|BloodHound Attack Path Analysis]] — the offense half this playbook detects.
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] — trio sibling; the credential-access stage that usually follows collection.
- [[detect-dcsync-and-ntdsdit-access|Detect DCSync and NTDS.dit Access]] — trio sibling; the endgame after the graph reveals a path to replication rights.
- [[tier-zero-administration-and-paw|Tier 0 Administration and PAW]] — the structural defense that makes a complete collection low-value.
- [[windows-event-logs|Windows Event Logs]] — the 1644/4661/5145 audit-policy preconditions.
- [[edr-network-observability-and-process-correlation|EDR / Process Correlation]] — host-side process and fan-out telemetry for in-memory collectors.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — stitching collection → roasting → DCSync into one chain.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the meta-principle behind the offense/defense pairing.

## References

- **Foundational:** MITRE ATT&CK T1087 — Account Discovery (with T1069 Permission Groups Discovery and T1482 Domain Trust Discovery) — https://attack.mitre.org/techniques/T1087/
- **Official Tool Docs:** BloodHound Community Edition documentation (SpecterOps) — https://bloodhound.specterops.io/
- **Research / Deep Dive:** Robbins, Schroeder, Vazarkar — An ACE Up The Sleeve (Black Hat USA 2017) — https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf
- **Telemetry / Detection:** Microsoft Defender for Identity — Reconnaissance and discovery alerts — https://learn.microsoft.com/en-us/defender-for-identity/reconnaissance-discovery-alerts
- **Official Tool Docs:** Microsoft Sysinternals — Sysmon — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
