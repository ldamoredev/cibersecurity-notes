---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Identity and Active Directory

## Purpose

This note standardizes references for the identity-and-active-directory branch.

Use it to:
- keep AD/Kerberos notes tied to canonical primary sources
- avoid stale or low-signal blog posts when MITRE / Microsoft / SpecterOps cover the same topic
- keep this branch centered on AD, Kerberos, and graph-based attack-path analysis while leaving room for Entra ID / hybrid identity content later

## Source of truth rule

For identity-and-active-directory notes, this registry is the primary source of truth.

Use it together with:
- `<a href="identity-and-active-directory/index.html">Identity and Active Directory Index</a>`
- `<a href="reference-registry-offensive-security.html">Reference Registry — Offensive Security</a>` when AD notes cross into recon / enumeration territory
- `<a href="reference-registry-detection-engineering.html">Reference Registry — Detection Engineering</a>` when AD notes reach into telemetry / behavioral-detection content

---

## Reference selection policy

### Source priority

1. **Foundational** taxonomies (MITRE ATT&CK, Microsoft documentation)
2. **Research / Deep Dive** primary sources (SpecterOps / harmj0y / Sean Metcalf canonical posts and conference talks)
3. **Tool docs** (BloodHound CE, Impacket, Mimikatz)
4. **Secondary** sources only when they add clear value (rare for this branch — primary sources are abundant)

### Per-note target

- minimum 2 references
- ideal 3 references

### Labeling

Use:
- **Foundational**
- **Research / Deep Dive**
- **Official Tool Docs**

---

# Identity / AD topic map

## kerberoasting

Preferred references:
- **Foundational:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Cracking Kerberos TGS Tickets — https://adsecurity.org/?p=2293
- **Research / Deep Dive:** Tim Medin — Attacking Microsoft Kerberos (DerbyCon 2014, original talk) — https://www.youtube.com/watch?v=PUyhlN-E5MU

## as-rep-roasting

Preferred references:
- **Foundational:** MITRE ATT&CK T1558.004 — AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Research / Deep Dive:** Will Schroeder (harmj0y) — Roasting AS-REPs — https://blog.harmj0y.net/activedirectory/roasting-as-reps/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458

## bloodhound-attack-path-analysis

Preferred references:
- **Official Tool Docs:** BloodHound Community Edition documentation (SpecterOps) — https://bloodhound.specterops.io/
- **Research / Deep Dive:** Robbins, Schroeder, Vazarkar — An ACE Up The Sleeve (Black Hat USA 2017) — https://www.specterops.io/assets/resources/an_ace_up_the_sleeve.pdf
- **Research / Deep Dive:** Robbins & Schroeder — Six Degrees of Domain Admin (DEF CON 24) — https://www.youtube.com/watch?v=lxd2rerVsLo

## dcsync-and-ntdsdit-extraction

Preferred references:
- **Foundational:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Foundational:** Microsoft — AD DS replication permissions documentation — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864

## golden-ticket-and-krbtgt-compromise

Preferred references:
- **Foundational:** MITRE ATT&CK T1558.001 — Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Detection:** MITRE ATT&CK DET0144 — Detect Forged Kerberos Golden Tickets — https://attack.mitre.org/detectionstrategies/DET0144/
- **Recovery:** Microsoft Learn — AD Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz Golden Ticket Usage, Exploitation, and Detection — https://adsecurity.org/?p=1515

## silver-ticket-and-service-account-persistence

Preferred references:
- **Foundational:** MITRE ATT&CK T1558.002 — Silver Ticket — https://attack.mitre.org/techniques/T1558/002/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — How Attackers Use Kerberos Silver Tickets to Exploit Systems — https://adsecurity.org/?p=2011
- **Foundational:** Microsoft Learn — Kerberos authentication overview — https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview
- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview

## gmsa-and-modern-service-account-hardening

Preferred references:
- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview
- **Hardening:** Microsoft Learn — Get started with group Managed Service Accounts — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/getting-started-with-group-managed-service-accounts
- **Foundational:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Active Directory Security Tip #14: Group Managed Service Accounts (GMSAs) — https://adsecurity.org/?p=4904

## krbtgt-rotation-and-tier-zero-recovery

Preferred references:
- **Recovery:** Microsoft Learn — AD Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Recovery:** Microsoft Learn — AD Forest Recovery Guide — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide
- **Foundational:** MITRE ATT&CK T1558.001 — Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts now available for customers — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/

## pass-the-hash-and-ntlm-credential-reuse

Preferred references:
- **Foundational:** MITRE ATT&CK T1550.002 — Use Alternate Authentication Material: Pass the Hash — https://attack.mitre.org/techniques/T1550/002/
- **Hardening:** Microsoft — Mitigating Pass-the-Hash and Other Credential Theft, version 2 — https://www.microsoft.com/en-us/download/details.aspx?id=54095
- **Hardening:** Microsoft Learn — Credential Guard overview — https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/

## tier-zero-administration-and-paw

Preferred references:
- **Hardening:** Microsoft Learn — Enterprise Access Model — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model
- **Hardening:** Microsoft Learn — Privileged Access Workstations deployment — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-deployment
- **Hardening:** Microsoft Learn — Protected Users security group — https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Securing Domain Controllers to Improve Active Directory Security — https://adsecurity.org/?p=3299

## windows-privilege-escalation

Preferred references:
- **Foundational:** MITRE ATT&CK TA0004 — Privilege Escalation tactic — https://attack.mitre.org/tactics/TA0004/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — LAPS and Windows privilege escalation patterns — https://adsecurity.org/?p=4063
- **Official Tool Docs:** Microsoft Sysinternals Suite (accesschk, autoruns, procmon, sysmon) — https://learn.microsoft.com/en-us/sysinternals/
- **Hardening:** Microsoft Learn — Securing privileged access in Windows — https://learn.microsoft.com/en-us/security/privileged-access-workstations/overview

---

## Registry usage rules

- choose the smallest set of strongest references for the exact note
- prefer one ATT&CK reference + one canonical SpecterOps/Metcalf post per note where possible
- keep references centered on AD attacks, defenses, and detection telemetry; route protocol-level Kerberos / NTLM crypto details through the cryptography registry instead
