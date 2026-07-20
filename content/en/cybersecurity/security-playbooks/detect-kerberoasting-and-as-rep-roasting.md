---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Detect Kerberoasting and AS-REP Roasting

## Goal

Detect both Active Directory Kerberos credential-attack families ([[kerberoasting|Kerberoasting]] and [[as-rep-roasting|AS-REP Roasting]]) via behavioral analysis on Event IDs 4768/4769 and complementary telemetry, with high enough fidelity to identify the source account, attacker host, and scope within minutes — and durable enough to survive small operator tradecraft variations (encryption type, request rate, account selection).

## Assumptions

- you collect Windows Security event logs from all Domain Controllers into a SIEM (Splunk, Sentinel, Elastic, or equivalent) with ≥ 30 days retention
- you have an authoritative list of service accounts (accounts with `servicePrincipalName` attribute set) and an audit of accounts with `DONT_REQ_PREAUTH` set
- you can hot-disable a compromised account and require Tier 0 approval for re-enable
- the goal is **detect, contain, investigate** — not prevention; the protocol features these attacks exploit are not patchable as bugs

## Prerequisites

- DC audit policy: `Audit Kerberos Authentication Service: Success/Failure` and `Audit Kerberos Service Ticket Operations: Success/Failure` both enabled (these generate 4768 and 4769 respectively) — see [[windows-event-logs|Windows Event Logs]] for the full audit-policy + Event-ID reference
- SIEM tables for Event 4768 and 4769 with the field for `TicketEncryptionType` (4769) or `PreAuthType` (4768) parsed and indexed
- A baseline of normal Kerberos behavior per service account: typical request rate, typical source IPs, typical encryption types
- An authoritative list of accounts that legitimately have `DONT_REQ_PREAUTH` set (should be ≤ 1 in a healthy environment, ideally zero)
- Optional: honey accounts with SPN set and/or pre-auth disabled (asymmetric high-confidence detection)

## Detection steps

> *This playbook pairs to two offense notes: [[kerberoasting|Kerberoasting]] and [[as-rep-roasting|AS-REP Roasting]]. Read offense + defense as the [[attacker-defender-duality-as-a-learning-tool|paired-reading discipline]] requires.*

### Phase 0 — Baseline (do once, refresh quarterly)

1. **Inventory accounts with SPNs.** These are your Kerberoasting targets. Audit which are legitimate service accounts vs which are misconfigurations.
   `text
   Get-ADUser -Filter {ServicePrincipalName -like "*"} -Properties ServicePrincipalName`

2. **Inventory accounts with `DONT_REQ_PREAUTH`.** These are your AS-REP roasting targets. The healthy count is zero.
   `text
   Get-ADUser -Filter 'DoesNotRequirePreAuth -eq $true' -Properties DoesNotRequirePreAuth`

3. **Baseline encryption types per account.** Run for 7 days and record the dominant TicketEncryptionType per service account (should be AES256 or AES128 — value 0x12 or 0x11 — in any modern environment).
4. **Baseline request rates per service account.** A real service account typically requests a small number of TGS tickets per day, from a small set of source hosts. Record per-account.
5. **Audit and remediate Phase 0 findings before relying on detection.** Reducing the surface area is more valuable than detecting attacks against unnecessary surface area.

### Phase 1 — Detect Kerberoasting

Operator signature: **bulk TGS-REQ traffic from one source against many service accounts, often with RC4-HMAC encryption type, often within seconds.**

1. **High-volume TGS request rule.** Alert when a single account requests TGS for ≥ N distinct service accounts within 60 s. N depends on baseline; 5–10 is a strong starting point.
   `text
   # Splunk-ish pseudocode
   index=wineventlog EventCode=4769 TicketEncryptionType IN ("0x17","0x12","0x11")
   | bin _time span=60s
   | stats dc(ServiceName) AS uniq_services BY _time, TargetUserName, IpAddress
   | where uniq_services >= 5`

2. **RC4-HMAC anomaly rule.** Alert on TGS-REQ with `TicketEncryptionType=0x17` (RC4-HMAC) for any service account whose baseline is AES. The attacker frequently downgrades to RC4 to make offline cracking economically viable.
   `text
   index=wineventlog EventCode=4769 TicketEncryptionType="0x17"
   | lookup service_account_baseline ServiceName OUTPUT baseline_enctype
   | where baseline_enctype != "0x17"`

3. **Service-account behavioral deviation rule.** Alert when a service account's TGS request *source* deviates from baseline. Real service accounts are used from the same small set of hosts; the attacker host is new.
4. **Per-source LDAP+Kerberos correlation.** A Kerberoasting operator usually queries LDAP for service accounts (`(&(objectClass=user)(servicePrincipalName=*))`) immediately before issuing TGS-REQs. Alert on LDAP-with-SPN-filter followed within 60 s by anomalous TGS-REQ from the same source.

### Phase 2 — Detect AS-REP Roasting

Operator signature: **AS-REQ from one source for one or more accounts, with `Pre-Authentication Type: 0`** (no `PA-ENC-TIMESTAMP` provided).

1. **`PreAuthType=0` rule (highest fidelity).** Event 4768 with `PreAuthType=0` is by definition pre-authentication-disabled traffic. In an environment where no account should have `DONT_REQ_PREAUTH` set, *any* event of this type is an immediate high-severity alert.
   `text
   index=wineventlog EventCode=4768 PreAuthType="0"
   | lookup preauth_disabled_allowlist TargetUserName OUTPUT allowed
   | where isnull(allowed)`

2. **AS-REQ source diversity rule.** A single source sending AS-REQ against many usernames (especially against non-existent ones, which generate `KRB5KDC_ERR_C_PRINCIPAL_UNKNOWN`) is a username-enumeration + roasting signature. Alert on the combination.
3. **AS-REQ + KRB-ERROR pattern.** A roasting operator often gets a mix of `KRB-AS-REP` (success against pre-auth-disabled accounts) and `KRB5KDC_ERR_PREAUTH_REQUIRED` (the expected response for protected accounts) from one source. The pattern is distinctive.

### Phase 3 — Investigation and response

Once a Phase 1 or Phase 2 alert fires:

1. **Identify the source host.** Pull `IpAddress` (4769) or `Source Network Address` (4768) from the triggering event. Correlate with DHCP and AD computer logs to identify the host.
2. **Pull all Kerberos events from that source in the last 24 hours.** Build the operator's activity timeline.
3. **Hash the timeline.** If the source also performed LDAP enumeration, SMB session enumeration, or BloodHound-style ACL queries within the same window, you are looking at an authenticated foothold doing AD reconnaissance ([[bloodhound-attack-path-analysis|BloodHound]]).
4. **Determine compromise scope.**
   - For Kerberoasting: every account whose TGS was requested in the timeline should be considered "hash potentially exfiltrated, password potentially crackable" until proven otherwise. Rotate every such account's password.
   - For AS-REP roasting: the named target accounts should be rotated *and* the `DONT_REQ_PREAUTH` flag cleared.
5. **Disable the source account.** Until you can prove the source is legitimate or remediate it, treat it as hostile.
6. **Open IR ticket** with: triggering event(s), source host/IP/user, list of affected service accounts, rotation status of each, BloodHound output snapshot.

## Validation clues

- **High-confidence Kerberoasting:** one source account requests TGS for ≥ 5 distinct service accounts within 60s, with RC4-HMAC encryption type against an AES-baseline environment.
- **High-confidence AS-REP roasting:** Event 4768 with `PreAuthType=0` against any account *not* on the explicit allowlist.
- **Honey account fired:** TGS-REQ or AS-REQ against the honey SPN/account. Near-zero false-positive — investigate immediately as confirmed adversary activity.
- **Behavioral cluster:** the same source IP that triggered the Kerberos alert also performed LDAP enumeration with SPN filter or BloodHound-style ACL queries in the same window. Confirms recon-phase activity.
- **Cracking evidence:** if the operator successfully cracked a service account password, you may see a `4768` (TGT request) success from a *different* source IP using the same account's credential within hours. Detection-ready.

## Mitigation / remediation

On the defender side, these are durable controls (not per-alert fixes):

- **Migrate all service accounts to Group Managed Service Accounts (gMSA).** gMSA passwords are 240-byte random values rotated by AD on a schedule, making offline cracking infeasible regardless of encryption type. See [[gmsa-and-modern-service-account-hardening|gMSA and modern service account hardening]] for the migration discipline.
- **Enforce AES-only encryption types domain-wide** (`KerberosEncryptionTypes` GPO set to AES128/AES256 only). Removes the RC4 cracking advantage. Even a weak password becomes uncrackable in practical timeframes against AES-PBKDF2.
- **Remove `DONT_REQ_PREAUTH` from every account.** The bitmask audit query (`(userAccountControl:1.2.840.113556.1.4.803:=4194304)`) returns the list. Re-enable pre-auth or disable the account. The healthy long-term state is zero pre-auth-disabled accounts.
- **Remove privileged service accounts from Tier 0 groups.** Service accounts should not be in `Domain Admins`. Period. See [[tier-zero-administration-and-paw|Tier 0 Administration]] for the structural framing.
- **Honey accounts.** Plant a fake service account with SPN set and another with `DONT_REQ_PREAUTH`. Both with strong random passwords nobody uses. Any TGS-REQ or AS-REQ for either is, by definition, adversary activity.
- **Disable NTLMv1 domain-wide.** AS-REP and TGS hashes can sometimes be downgraded to NTLMv1 in cross-trust scenarios. Block NTLMv1 outright.

### What does not work as a primary defense

- **Blocking outbound Kerberos.** Kerberos *is* the authentication protocol; you cannot block it without breaking AD.
- **Renaming service accounts to obscure names.** LDAP returns the canonical attribute. Security by obscurity.
- **Trusting that "we audited a year ago".** `userAccountControl` flags drift; new service accounts get created with weak passwords; new Exchange installations grant unexpected rights. The audit cadence must be quarterly.
- **Disabling Mimikatz / Impacket binaries.** The protocol is the attack surface, not the tool. Block-listing tools is a delaying tactic, not a defense.
- **Trusting low alert volume.** A *single* TGS-REQ for `krbtgt` or a *single* `PreAuthType=0` event is the signature. Volumetric thresholds miss the surgical operator.

## Logging / forensics

- **Retain DC Security logs for ≥ 90 days.** Roasting → cracking → reuse chains often span days or weeks. Without retention, the chain is invisible.
- **Tag every alert with:** source account, source IP, target service accounts, encryption type, allowlist status (was this an expected pre-auth-disabled account?). These tags drive trend analysis.
- **Capture the full TGS-REQ / TGS-REP exchange where possible.** Wireshark on a Domain Controller during an active alert gives you the operator's exact request payload — useful for tool fingerprinting and forensics.
- **Correlate with [[attack-path-correlation-and-kill-chain-observability|attack-path correlation]] across the chain.** A single Kerberoast event is suspicious; a Kerberoast event followed by a cracked credential authenticating from a different source IP days later is a confirmed kill chain.

## Operational safety

- **never** disable a service account "to be safe" without coordinating with the application team. Service accounts in production runners can cause outages.
- **never** rely on a single detection rule. Phase 1 alert + LDAP-enumeration correlation + behavioral deviation produces much higher-fidelity findings than any single rule alone.
- **always** maintain a written allowlist of accounts with legitimate pre-auth-disabled or weak-encryption-type configurations. Without it, every alert is potentially a false positive.
- **always** rotate every Kerberoasted service account's password as part of remediation, even if you believe the operator could not crack it. The hash was exfiltrated; the only durable response is rotation.
- **always** test detection rules against an authorized internal lab running the offense attacks before relying on them. Untested rules are theater.

## Related notes

- [[kerberoasting|Kerberoasting]] — the offense playbook half of Phase 1.
- [[as-rep-roasting|AS-REP Roasting]] — the offense playbook half of Phase 2.
- [[bloodhound-attack-path-analysis|BloodHound]] — the recon tool the operator usually pairs with these attacks; alert correlation finds both.
- [[dcsync-and-ntdsdit-extraction|DCSync]] — the endgame after a cracked service-account password yields DCSync rights.
- [[gmsa-and-modern-service-account-hardening|gMSA hardening]] — the structural mitigation referenced repeatedly above.
- [[tier-zero-administration-and-paw|Tier 0 Administration]] — the structural defense that makes the post-Kerberoast escalation chain impossible.
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — the right framing for AD attack telemetry.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — multi-stage correlation across recon + Kerberoast + cracked-credential reuse.
- [[run-scan-pipeline]] and [[detect-external-scan-pipeline]] — the parallel offense/defense pair pattern this playbook follows.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the meta-principle.

## References

- **Foundational:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Foundational:** MITRE ATT&CK T1558.004 — AS-REP Roasting — https://attack.mitre.org/techniques/T1558/004/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Detecting Kerberoasting Activity — https://adsecurity.org/?p=3458
- **Research / Deep Dive:** Microsoft Threat Intelligence — How attacks abuse Kerberos: detection and mitigations — https://www.microsoft.com/en-us/security/blog/2022/01/26/evolving-kerberos-attack-detection/
