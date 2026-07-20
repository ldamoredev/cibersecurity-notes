---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Golden Ticket and KRBTGT Compromise

## Definition

A Golden Ticket is a forged Kerberos **Ticket Granting Ticket** (TGT) created with the compromised long-term key material of the domain's `krbtgt` account. It is not a magic administrator password. It is abuse of the domain's Kerberos ticket-signing trust root: if an attacker can sign a TGT with a key the Key Distribution Center accepts as `krbtgt`, the attacker can mint authentication material for arbitrary domain principals and group memberships.

## Why it matters

`krbtgt` is Tier 0 because it is the cryptographic root of domain authentication. Domain Controllers use the `krbtgt` key to encrypt and sign TGTs. Services and KDCs do not start by asking "did this password login happen"; they ask "does this ticket validate under the domain trust model". A stolen `krbtgt` hash or AES key therefore moves the incident from credential theft into **identity-system trust compromise**.

This is why [[dcsync-and-ntdsdit-extraction|DCSync and ntds.dit extraction]] are endgame events. DCSync of ordinary users enables lateral movement; DCSync of `krbtgt` enables ticket forgery against the domain authentication fabric itself. Normal user password resets, even Domain Admin password resets, do not revoke a Golden Ticket forged with still-valid `krbtgt` material.

The senior distinction is:

- **Password compromise:** rotate the affected identity and investigate sessions.
- **Service-account compromise:** rotate the service secret and inspect service access.
- **`krbtgt` compromise:** treat the domain's Kerberos signing root as untrusted until recovery sequencing proves otherwise.

## How it works

Golden Ticket abuse reduces to **5 protocol facts**:

1. **Kerberos separates authentication from service access.** A user first receives a TGT from the KDC through AS exchange, then presents the TGT later to request TGS service tickets.
2. **The TGT is protected by `krbtgt`.** The ticket body is encrypted and signed with the `krbtgt` long-term key. The client cannot normally create a valid one.
3. **DCSync can recover `krbtgt` material.** A principal with replication rights can request the `krbtgt` NTLM hash and Kerberos AES keys from a DC. See [[dcsync-and-ntdsdit-extraction|DCSync and ntds.dit Extraction]].
4. **A forged TGT can contain attacker-chosen identity claims.** Tooling can choose username, RID, domain SID, group SIDs, SIDHistory, ticket lifetime, encryption type, and timestamps.
5. **The KDC validates the signature, not the original login.** When the forged TGT is later used for a TGS request, the KDC accepts it if the cryptographic material and fields are plausible under current policy.

Conceptual authorized-lab flow:

```
owned replication-right principal
  -> DCSync krbtgt hash/AES key
  -> obtain domain SID
  -> forge TGT for chosen user + group claims
  -> load ticket into a lab session
  -> request TGS for CIFS/LDAP/HTTP/MSSQL
  -> observe 4769/4624/4672-style telemetry
```

The structural bug is not "Kerberos is broken"; it is *if the domain ticket-signing account is compromised, the verifier can no longer distinguish real KDC-issued TGTs from attacker-signed TGTs without correlation and recovery*.

## Techniques / patterns

- **DCSync to `krbtgt` is the common predecessor.** Golden Tickets usually appear after DCSync, ntds.dit extraction, DC compromise, or backup compromise. The attack is downstream of Tier 0 access, not a first foothold.
- **Domain SID is required.** The forged PAC needs the domain SID plus RIDs/group SIDs. Operators usually obtain it from LDAP, `whoami /user`, BloodHound data, or Impacket lookup. Wrong SID = unusable or anomalous ticket.
- **RID and group manipulation matter.** Forging `Administrator` RID 500 is noisy. Mature operators may choose an existing user identity and inject privileged group SIDs. Defenders should compare observed group claims against directory membership.
- **SIDHistory can smuggle privilege.** A forged PAC can include unexpected `SIDHistory` values, including historical or foreign-domain privileged SIDs. This is why SID filtering, trust configuration, and PAC inspection matter in multi-domain environments.
- **Lifetime anomalies are a detection surface.** Old tooling defaulted to 10-year tickets. Modern operators tune lifetimes closer to domain policy, but mismatched `StartTime`, `EndTime`, `RenewTill`, and logon patterns still create correlation opportunities.
- **AES vs RC4 changes both crack and detection economics.** RC4-HMAC tickets are suspicious in modern AES-capable domains and often indicate legacy settings or attacker preference. AES-forged tickets are less obviously anomalous but require AES key material, not only the NTLM hash.
- **Golden Tickets still need service access.** A forged TGT usually has to obtain TGS tickets for services. That KDC interaction creates `4769` telemetry even when the original AS request never occurred.
- **Normal password resets do not revoke the trust root.** Resetting the impersonated user changes the real user's password-derived keys, not the `krbtgt` key that validates the forged TGT.

## Variants and bypasses

Golden Ticket usage has **4 operational variants** worth separating.

### 1. Classic high-privilege Golden Ticket

The attacker forges a TGT for a privileged identity such as `Administrator` with Domain Admin-like group SIDs. Easy to understand, high impact, high telemetry risk because privileged logons appear from unusual hosts and services.

### 2. Low-noise existing-user impersonation

The attacker forges a TGT for an existing account whose normal access resembles the target action. The ticket may add only a narrow privileged SID or may rely on existing access. Harder to detect with username-only rules; correlation must compare group claims, host history, and ticket issuance sequence.

### 3. SIDHistory / cross-domain abuse

The forged PAC includes SIDHistory or trusted-domain SIDs to obtain access across trust boundaries. This depends heavily on trust configuration and SID filtering. It is most relevant in forests with legacy migrations or weak external trusts.

### 4. Long-term persistence ticket

The attacker forges tickets with extended lifetime and renew fields for persistence. This was historically common. It is now a strong detection signal in domains where Kerberos policy is centrally known and telemetry is normalized.

## Impact

Ordered by typical real-world severity:

- **Tier 0 authentication-root compromise.** `krbtgt` material lets an attacker impersonate any domain principal from the Kerberos layer.
- **Persistence beyond ordinary account remediation.** User, admin, and service account password resets do not invalidate tickets signed by an unchanged `krbtgt` key.
- **Domain-wide privilege fabrication.** The forged PAC can claim privileged group membership even if the directory does not contain that membership.
- **Forensic ambiguity.** Authentication logs may show a real username even though the real user's password was never used.
- **Attack-path completion.** [[bloodhound-attack-path-analysis|BloodHound]] paths that end in DCSync effectively become paths to Golden Ticket capability.

## Detection and telemetry

Detection is correlational, not a single IOC. Useful signals include:

1.
**TGS request without a plausible preceding AS request.**
   Event ID `4769` appears when a TGS is requested. If there is no corresponding `4768` TGT request for that account, host, and time window, the TGT may have been injected or forged. This requires timestamp-aligned DC telemetry, not one isolated log.

2.
**Ticket lifetime and renewal anomalies.**
   Compare observed ticket fields with domain Kerberos policy. Abnormally long `EndTime` or `RenewTill` values are useful, but modern attackers can tune them; treat lifetime as one feature, not the whole detection.

3.
**Unexpected encryption type.**
   `0x17` RC4-HMAC in a modern AES-only or AES-preferred environment is suspicious, especially for privileged accounts. AES usage is not proof of legitimacy.

4.
**PAC / group membership mismatch.**
   Privileged SIDs in logon events (`4624`, `4672`) that do not match current AD group membership are high-value signals. This requires enrichment from directory state.

5.
**Privileged account behavior from unusual hosts.**
   Golden Ticket use usually produces service access: SMB, LDAP, WinRM, MSSQL, HTTP. Correlate `4624`, `4672`, `4769`, EDR process ancestry, and host/service baselines.

6.
**Precursor telemetry.**
   Golden Ticket detection should start before the ticket: DCSync `4662` replication GUIDs, `ntds.dit` access, LSASS access, BloodHound collection, or abnormal replication-right use. See [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]].

Modern telemetry reality: a perfectly field-tuned Golden Ticket may not trip a standalone Kerberos rule. The stronger detection is the sequence: graph collection -> replication abuse -> ticket injection -> privileged service access.

## Defensive controls

Ordered by effectiveness:

1.
**Prevent non-DC replication rights.**
   Audit `DS-Replication-Get-Changes*` and effective DCSync edges with [[bloodhound-attack-path-analysis|BloodHound]]. If attackers cannot recover `krbtgt`, Golden Ticket risk collapses.

2.
**Treat `krbtgt` as Tier 0 secret material.**
   Include `krbtgt` in privileged-access review, domain compromise playbooks, backup-protection assumptions, and DC hardening. It is not a normal user account.

3.
**Rotate `krbtgt` twice after suspected compromise.**
   One reset is normally insufficient because the previous key remains usable during the password-history and ticket-lifetime window. Pair with [[krbtgt-rotation-and-tier-zero-recovery|KRBTGT Rotation and Tier Zero Recovery]].

4.
**Enforce AES and retire RC4 where operationally possible.**
   This reduces weak-key and legacy-detection ambiguity. It does not prevent Golden Tickets if AES `krbtgt` keys are stolen.

5.
**Normalize Kerberos, logon, EDR, and directory telemetry.**
   Golden Ticket detections depend on correlation keys: account, SID, client address, DC, service SPN, logon ID, process, host role, and group membership snapshot. See [[telemetry-normalization-correlation-and-enrichment|Telemetry Normalization, Correlation, and Enrichment]].

6.
**Tier 0 isolation and PAWs.**
   Prevent the credential-theft chain that leads to DCSync: Tier 0 admins should not log on to lower-tier systems where credentials can be harvested.

### What does not work as a primary defense

- **Resetting Domain Admin passwords.** This does not change `krbtgt` and therefore does not invalidate forged TGTs signed with stolen `krbtgt` material.
- **Disabling or deleting the impersonated user.** Some KDC/service validation paths may catch nonexistent users, but forged tickets can still abuse other identities. Recovery must address the signing key.
- **Blocking Mimikatz by filename.** Golden Ticket creation exists in multiple tools and can be reimplemented. Detect the trust abuse and precursor behavior, not the brand name.
- **Relying on short ticket lifetime policy after compromise.** Policy helps future legitimate tickets. It does not revoke stolen `krbtgt` keys by itself.
- **One `krbtgt` reset as incident closure.** The old key can remain valid long enough for forged tickets to survive. Sequencing matters.
- **Assuming EDR sees everything.** Ticket validation happens through Kerberos and service logons; endpoint process telemetry is necessary but insufficient without DC logs and directory context.

## Operational misconceptions

- **"Golden Ticket equals Domain Admin password."** False. It is stronger in some ways and narrower in others: it forges Kerberos authentication, not every protocol credential.
- **"If we see no 4768, there is no Kerberos activity."** False. A forged TGT may appear first as `4769` TGS activity or as host logons.
- **"AES means safe."** False. AES removes RC4 weakness; it does not help if the AES key itself was replicated.
- **"The attacker must use Administrator."** False. Existing-user impersonation is usually better tradecraft and harder to detect.
- **"The ticket is invisible."** False. The original AS request may be missing, but service access, logons, group claims, process ancestry, and network paths still leak behavior.

## Practical labs

Run only in a private AD lab, intentionally vulnerable range, or authorized assessment.

```
Lab 1 — Map the Golden Ticket preconditions.
Objective: prove that Golden Ticket is downstream of Tier 0 material, not a first-step exploit.
Setup: one lab domain, one DC, one low-priv user, one admin user, BloodHound collection.
Steps:
  1. Run BloodHound against the lab.
  2. Query principals with DCSync/GetChangesAll rights.
  3. Record whether any non-DC/non-DA principal can reach DCSync.
Expected telemetry: LDAP collection, possible 4662 object access depending audit policy.
Defender interpretation: a path to DCSync is a path to krbtgt and Golden Ticket capability.
Misconception corrected: "Golden Ticket starts with a tool command"; it starts with a trust-path failure.
```

```
# Lab 2 — Conceptual authorized-lab Golden Ticket flow.
# Preconditions: owned lab domain, explicit permission, lab krbtgt material from your own DC.
# Do not run this against any third-party or production domain.

# 1. Recover only the lab krbtgt material, as shown in the DCSync note.
impacket-secretsdump LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1 -just-dc-user krbtgt

# 2. Obtain the lab domain SID.
impacket-lookupsid LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1

# 3. Forge a lab TGT with realistic lifetime settings.
impacket-ticketer -aesKey <LAB_KRBTGT_AES256_KEY> \
  -domain-sid S-1-5-21-<LAB-SID> -domain LAB.LOCAL labuser

# 4. Use the ticket only against lab services and observe DC + host logs.
export KRB5CCNAME=labuser.ccache
impacket-smbclient LAB.LOCAL/labuser@dc01.lab.local -k -no-pass
```

Expected defender view: `4769` for service ticket requests, `4624` on the target host, possible privileged `4672` if privileged SIDs were injected, and a missing or suspicious `4768` predecessor depending cache and sequence.

```
# Lab 3 — Detection reasoning over DC logs.
# Run on the lab DC after the authorized flow.
$tgs = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4769} -MaxEvents 200
$as  = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768} -MaxEvents 200

# Analyst exercise:
# - group by AccountName + ClientAddress
# - look for TGS activity without nearby AS activity
# - compare encryption types against domain policy
# - inspect target SPNs reached by the forged identity
```

```
Lab 4 — Ticket-field anomaly table.
Objective: learn which fields are features, not verdicts.
Setup: export 4768/4769/4624 events from normal lab users and the authorized forged-ticket flow.
Steps:
  1. Compare account, client address, service name, ticket encryption type, time fields, and logon type.
  2. Mark each field as normal, suspicious, or inconclusive.
  3. Write a detection that requires at least two suspicious features.
Limitations: a skilled operator can tune many fields. The value is correlation, not a single field.
```

## Practical examples

- **DCSync-to-Golden-Ticket chain.** Kerberoasting yields `svc_replication`, BloodHound shows DCSync rights, DCSync recovers `krbtgt`, and a forged TGT impersonates a privileged user. The real issue was the replication-right edge.
- **Post-incident false closure.** IR resets all Domain Admin passwords but does not rotate `krbtgt`. The attacker continues using a previously forged TGT. The organization fixed users, not the trust root.
- **Modern tuned ticket.** The attacker forges with AES, normal lifetimes, and a real username. Detection comes from TGS-without-AS correlation plus unusual service access and group-claim mismatch.
- **SIDHistory abuse in a legacy trust.** A migration-era trust leaves SID filtering weak. Forged SIDHistory grants access that current group membership does not explain.

## Related notes

- [[dcsync-and-ntdsdit-extraction]] — the most common way `krbtgt` material is recovered.
- [[bloodhound-attack-path-analysis]] — graph paths to DCSync are graph paths to Golden Ticket capability.
- [[kerberoasting]] — a common predecessor when cracked service accounts lead to replication rights.
- [[silver-ticket-and-service-account-persistence]] — the service-scoped contrast case for forged Kerberos tickets.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — Golden Ticket detection is strongest as a sequence, not a single event.
- [[edr-network-observability-and-process-correlation|EDR, Network Observability, and Process Correlation]] — endpoint telemetry explains ticket injection and service access context.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — Golden Ticket detection is behavioral and correlational.
- [[krbtgt-rotation-and-tier-zero-recovery]] — the recovery operation that invalidates stolen `krbtgt` material when sequenced correctly.

### Suggested future atomic notes

- kerberos-pac-validation
- sid-history-abuse-and-sid-filtering
- [[tier-zero-administration-and-paw]]
- detect-golden-ticket-and-silver-ticket
- ad-forest-trust-security

## References

- **Foundational:** MITRE ATT&CK T1558.001 — Steal or Forge Kerberos Tickets: Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Detection:** MITRE ATT&CK DET0144 — Detect Forged Kerberos Golden Tickets — https://attack.mitre.org/detectionstrategies/DET0144/
- **Recovery:** Microsoft Learn — Active Directory Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz Golden Ticket Usage, Exploitation, and Detection — https://adsecurity.org/?p=1515
