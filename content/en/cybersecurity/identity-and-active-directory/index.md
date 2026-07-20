---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Identity and Active Directory Index

## Purpose

This branch covers identity-system attacks and defenses centered on **Active Directory**, **Kerberos**, and **graph-based attack-path analysis**. AD is the single most-attacked authoritative identity system in enterprise environments because (a) a fully compromised AD is total enterprise compromise, and (b) the protocols that make AD usable also expose attackable structure (replication rights, password-derived encryption keys, transitive group membership, delegated ACEs).

Use [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[index|Networking]] — Kerberos runs on UDP/TCP 88 and LDAP on 389/636; protocol context matters.
> - [[index|Cryptography]] — every AD credential attack reduces to KDF strength + symmetric encryption choice (RC4 vs AES). Read [[password-hashing|password hashing]] and [[symmetric-encryption-modes|symmetric encryption modes]] before this branch.
> - **Pair every note with its [[index|Detection Engineering]] counterpart.** AD attacks have *no* signature; only behavioral detection works.

---

## Branch positioning

This branch sits in Phase 4 — **Specialty tracks** — by roadmap-v2 classification: read it when AD is part of your job context (red-team operator, AD admin, IR analyst, identity-platform engineer). But it is also a deep Phase 2 case study because every note in this branch *is* an offense/defense pair. See [[phase-4-specialty|Phase 4 — Specialty Tracks]] for context.

---

## Recommended learning order

### First-pass core (11 notes)

1. [[bloodhound-attack-path-analysis]] — the visibility layer. Read first because it tells you which AD attacks are worth doing, which accounts are worth attacking, and which defensive paths to remediate first. The cleanest single-tool example of offense/defense duality in the entire atlas.
2. [[as-rep-roasting]] — the *pre-foothold* attack. No credentials needed; only usernames and a single account with pre-authentication disabled. Often the first attack on a domain.
3. [[kerberoasting]] — the *post-foothold* attack. Requires any domain credential; targets accounts with SPNs. Frequently yields a service account with onward path to DCSync.
4. [[dcsync-and-ntdsdit-extraction]] — the endgame. Recovers every hash in the domain including `krbtgt`. Enables Golden Tickets and total persistent domain compromise.
5. [[pass-the-hash-and-ntlm-credential-reuse]] — what you do with the bulk NTLM hashes DCSync produces. Closes the credential-extraction → reuse loop and explains why NTLM disablement is the long-term direction.
   - Sibling: [[windows-privilege-escalation]] — the local-host primitive that yields the LSASS access where Pass-the-Hash credentials come from. Read whenever the chain reaches a Windows host that needs elevation before AD attacks continue.
6. [[golden-ticket-and-krbtgt-compromise]] — the trust-root abuse step after `krbtgt` material is compromised. Read this after PtH so the domain-wide vs targeted-host distinction is concrete.
7. [[silver-ticket-and-service-account-persistence]] — service-scoped TGS forgery from service-account key material. Read this after Golden Ticket to keep the domain-wide vs service-scoped distinction sharp.
8. [[gmsa-and-modern-service-account-hardening]] — the defensive service-account design pattern. Read after Silver Ticket so hardening decisions map to concrete abuse paths.
9. [[tier-zero-administration-and-paw]] — the **structural** defense that makes the entire chain above impossible. Every prior offense note references this as "the answer"; reading it here grounds the references.
10. [[krbtgt-rotation-and-tier-zero-recovery]] — the Tier 0 recovery operation after suspected `krbtgt` compromise. Read last because the procedure only makes sense after the trust-root abuse model is clear.

Read in this order: the first note teaches you to *see* the graph; the next two teach you the most common ways to traverse edges; the fourth reaches the credential-extraction endgame; the fifth explains what bulk NTLM hash material enables; the sixth explains why `krbtgt` compromise is not "another password" but domain authentication-root compromise; the seventh shows how service-account key compromise creates narrower but often quieter persistence; the eighth turns that offensive model into service-account engineering; the ninth gives the structural defense; the tenth closes the loop with trust restoration.

### Suggested future atomic notes (seeded across the branch)

- dcshadow-and-rogue-dc-attacks — the stealthy DCSync sibling.
- exchange-ad-permission-legacy-issues — the recurring source of misconfigured replication rights.
- username-enumeration-against-kerberos — the prerequisite step for AS-REP Roasting.
- kerberos-preauth-and-encryption-types — why `DONT_REQ_PREAUTH` is structurally dangerous.
- useraccountcontrol-flags-as-attack-surface — every dangerous bit in `userAccountControl`.
- dcsync-and-genericall-acl-abuse (alt of writedacl-and-genericall-acl-abuse) — high-leverage edge types in BloodHound.
- shadow-credentials-and-kerberos-pkinit — modern AD-CS-based persistence path.
- [[detect-bloodhound-collection]] — defender-side playbook for catching the enumeration phase.
- [[detect-dcsync-and-ntdsdit-access]] — defender-side playbook for the endgame attack.

---

## Cross-links to other branches

- [[index|Offensive Security / Recon]] — the AD attacks here use the same operator mindset as the offensive-security branch; the AD-specific notes were originally there and were promoted here once the cluster reached critical mass.
- [[password-hashing|Password hashing]] — the load-bearing economics of all AD credential attacks.
- [[symmetric-encryption-modes|Symmetric encryption modes]] — RC4 vs AES in the Kerberos context.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — the right framing for AD attack telemetry.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — the defensive counterpart to BloodHound's graph thinking.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — this branch is the cleanest concrete example of the duality concept.

---

## Branch maintenance notes

- Every note in this branch follows the 11-section atomic-note template.
- AD attacks have *no* useful signature-based detection. The default detection framing here is always behavioral. Avoid drafting any "detect by IoC X" content; route detection narrative through Event-ID + behavior pairs.
- The branch was promoted from `cybersecurity/offensive-security/` once it reached 4 mature notes (Kerberoasting + AS-REP Roasting + BloodHound + DCSync) on 2026-05-10. New AD-specific notes should land directly here.
- Future expansion: a sibling `cybersecurity/entra-id-and-cloud-identity/` branch may eventually split off once Entra ID / AAD content reaches similar mass.
