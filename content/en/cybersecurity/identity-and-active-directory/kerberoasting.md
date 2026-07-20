---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Kerberoasting

## Definition

Kerberoasting is an Active Directory credential attack where an authenticated domain user requests **TGS service tickets** for accounts that have a Service Principal Name (SPN), then attempts to **crack the resulting tickets offline** to recover the service account's plaintext password. The attack works because (a) any authenticated domain user can request a TGS for any SPN, and (b) the portion of the TGS encrypted with the service account's password-derived key is observable to the requester.

## Why it matters

Kerberoasting is the single highest-impact post-foothold AD attack that requires no privilege escalation, no exploit, and no malware. Every domain user can run it. The only thing the defender controls is **whether service account passwords are strong enough to survive offline cracking** — and historically, service accounts are configured with weak, never-rotated, human-chosen passwords because "they are service accounts, nobody types them". The result is a reliable path from any domain user to a service account, and frequently from a service account to domain admin via lateral movement.

The technique is also the textbook bridge between three branches of this atlas that otherwise sit far apart:
- **Cryptography** — the attack only works because the encryption key is derived from a password via a known KDF. Strong passwords + AES + Kerberos PBKDF2 = uncrackable in practice; weak passwords + RC4 = cracked in hours on a single GPU.
- **Detection Engineering** — it is the cleanest example of an attack whose *only* defensive signal is behavioral, not signature. Every TGS request is a normal Kerberos operation; the attack is in the *pattern* (which accounts, at what rate, with what encryption type).
- **Offensive Security** — it is the canonical first move after gaining any AD user credential, and every red-team / pentest / IR walkthrough teaches it.

## How it works

Kerberoasting reduces to **5 protocol steps**:

1. **Authenticate to the domain.** Any valid domain user credential (purchased, phished, stolen, defaulted). No special privileges required.
2. **Enumerate SPNs.** Query AD for user accounts that have a `servicePrincipalName` attribute set. These are service accounts (a non-zero SPN is the marker). Any authenticated user can query this via LDAP — `(&(objectClass=user)(servicePrincipalName=*))` — no audit trail beyond standard LDAP query logs.
3. **Request TGS tickets.** For each SPN, ask the KDC for a TGS using normal `KRB_TGS_REQ` traffic. The KDC returns a TGS *encrypted with the service account's long-term key* (which is derived from its password).
4. **Extract the encrypted portion.** The TGS ticket's encrypted blob is observable to the requester. Tools like `GetUserSPNs.py` (Impacket), `Rubeus`, or PowerShell `Add-Type` + KerberosRequestorSecurityToken automate this and emit a hashcat-compatible string.
5. **Crack offline.** Run hashcat (mode `13100` for RC4-HMAC TGS, `19700`–`19900` for AES TGS) against the extracted hash with a wordlist or rules. RC4 + a weak password = minutes. AES-256 + a strong password = years.

A representative end-to-end command sequence:

```
# From a Linux foothold, with any valid domain credential
impacket-GetUserSPNs DOMAIN.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1 -request -outputfile spns.hash
hashcat -m 13100 spns.hash /usr/share/wordlists/rockyou.txt --force
```

The bug is not "Kerberos is broken"; it is *the encryption key for a TGS is a service account's password, and the offline cracking workflow operates on data any domain user can legitimately request*.

## Techniques / patterns

- **SPN enumeration is the first move.** Without SPNs there is nothing to roast. Tools: `setspn -Q */*` (Windows native), `GetUserSPNs.py` (Impacket), `Rubeus.exe kerberoast /stats` (in-process Windows). Each leaves slightly different telemetry.
- **Filter SPNs by interest.** Service accounts with high privileges (in `Domain Admins`, `Enterprise Admins`, `Backup Operators`, service-tier admin groups) are the prize. `BloodHound` paths show which service accounts grant the most onward movement.
- **Pick RC4 over AES whenever possible.** The KDC negotiates the encryption type per ticket. Tools can hint `RC4-HMAC` to force the weaker algorithm; `Rubeus.exe kerberoast /tgtdeleg` or `GetUserSPNs.py -hashes` workflows expose this knob. RC4 + GPU = orders of magnitude faster crack than AES-256.
- **Targeted vs unfiltered roasting.** `GetUserSPNs.py -request-user <target>` asks for one specific SPN — quieter than "request all SPNs at once". Targeted roasting against pre-identified high-value SPNs is the OPSEC-aware variant.
- **Use BloodHound to pick targets.** Once SPNs are known, BloodHound's `OutboundControl` and `MemberOf` analysis identifies which roasted-account compromise yields the largest blast radius. Avoid roasting low-impact service accounts to reduce noise.
- **Always run on an authorized engagement.** Kerberoasting in production without explicit scope authorization is a felony in most jurisdictions and a one-strike-out behavior in any structured engagement.

## Variants and bypasses

Kerberoasting has **4 important variants**, each with distinct preconditions and detection profiles.

### 1. Classic Kerberoasting

The flow described above. Requires any authenticated domain user. The default red-team and pentest move. Detection is behavioral (request volume, account selection, encryption type) — there is no signature.

### 2. Targeted Kerberoasting (one SPN at a time)

Same protocol, restricted to one or a few high-value SPNs identified in advance via BloodHound or manual analysis. Significantly quieter than mass roasting. Defenders who alert on bulk TGS-request anomalies miss the targeted variant.

### 3. AS-REP Roasting (the sibling attack)

Different attack, often confused with Kerberoasting. Requires no authenticated user — only knowledge of usernames. Targets accounts with the `DONT_REQ_PREAUTH` flag in `userAccountControl`. Same offline-cracking economics, different protocol step (AS-REQ/AS-REP instead of TGS-REQ/TGS-REP). The variant where the attack works *without even needing a valid credential first*. See [[as-rep-roasting|AS-REP Roasting]] for the full treatment.

### 4. Cross-realm / cross-trust Kerberoasting

In multi-forest or two-way-trust environments, an authenticated user in domain A can sometimes roast SPNs in domain B because trust transitivity issues TGS tickets across the boundary. Highly environment-specific; valuable in red-team scenarios against acquired-but-not-merged subsidiaries.

## Impact

Ordered by typical real-world severity:

- **Lateral movement to service account context.** The roasted password grants impersonation as the service account, including access to whatever the account can reach (file shares, databases, SQL Server linked-server chains, application service tier).
- **Privilege escalation to domain admin.** When a service account is (mistakenly) in `Domain Admins` or has equivalent permissions — common in legacy environments. Direct foothold-to-DA in a single step.
- **Persistence via Silver Ticket.** Once the service account's NTLM hash or AES key is recovered, an attacker can forge service-specific Kerberos tickets locally without further contact with the KDC. See [[silver-ticket-and-service-account-persistence|Silver Ticket and Service Account Persistence]] for the service-scoped forgery model.
- **Path to `krbtgt` compromise.** If the roasted account has replication rights or can reach them through a graph path, Kerberoasting becomes the predecessor to [[dcsync-and-ntdsdit-extraction|DCSync]] and [[golden-ticket-and-krbtgt-compromise|Golden Ticket]] capability.
- **Lateral phishing via SQL Server / web app impersonation.** Many service accounts run web apps or SQL services that trust the AD identity — credential reuse lets the attacker access internal admin interfaces, exfil data, or pivot.
- **Stealth.** The TGS request itself is normal Kerberos traffic. Without behavioral analytics, the only artifact is `Event ID 4769` and the offline crack happens entirely off the wire.

## Detection and defense

Ordered by effectiveness:

1.
**Use Managed Service Accounts (gMSA) with auto-rotated AES-only passwords.**
   The hard fix. gMSA passwords are 240-byte randomly-generated values rotated by AD on a schedule. The "service account password is a human-chosen weak string" precondition disappears. New service accounts should default to gMSA; legacy accounts should migrate.

2.
**Enforce AES-only encryption types via group policy.**
   `KerberosEncryptionTypes` set to AES128/AES256 only. Removes the RC4 cracking advantage — even a weak password becomes uncrackable in practical timeframes. Pair with PBKDF2 iteration audit to ensure the AES key derivation is robust.

3.
**Audit and remove privileged service accounts.**
   Service accounts should not be in `Domain Admins`. Period. The single highest-leverage Kerberoasting mitigation is *not technical* — it is removing the prize. Use BloodHound from the defender side to enumerate which service accounts grant high-impact access and revoke unneeded membership.

4.
**Behavioral detection on Event ID 4769.**
   Windows generates Event 4769 (Kerberos Service Ticket Operations) on every TGS request. Detection rules: (a) high volume of distinct service tickets requested by one account in a short window; (b) tickets requested with `Ticket Encryption Type 0x17` (RC4-HMAC) when AES is configured elsewhere — strong roasting signal; (c) service tickets requested for SPNs the user has never accessed historically; (d) account-baselined anomaly on request rate. See [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] for the framing.

5.
**Strong, long, random passwords on every service account.**
   If gMSA is unavailable, the bar is 25+ character truly random passwords with rotation every 30–90 days. The discipline must be enforced and audited; "we have a policy" without enforcement is theatre.

6.
**Honey SPNs.**
   Plant fake service accounts with SPNs and monitor for TGS requests against them. Legitimate users have no reason to request these SPNs — any request is a high-confidence Kerberoasting indicator. Asymmetric defense.

### What does not work as a primary defense

- **"We don't have service accounts in Domain Admins."** A common claim that turns out to be false on inspection. Audit, don't assert.
- **Blocking Kerberos at the network layer.** Kerberos is the authentication protocol; you cannot block it without breaking the directory.
- **Removing the `Logon as a service` right.** Doesn't prevent TGS requests; just affects whether the account can run services. The attack works against accounts with SPNs regardless of whether they actively run anything.
- **Disabling LDAP query.** Authenticated users can enumerate SPNs through several other channels including `setspn`, AdminSDHolder traversal, or GPO replication.
- **Renaming service accounts to obscure names.** Security by obscurity. SPN enumeration returns the canonical samAccountName regardless of display label.

## Practical labs

Run **only** against owned lab environments or authorized engagements. Kerberoasting against a production AD without authorization is a serious offense.

```
# Lab 1 — Build a lab AD with a kerberoastable service account.
# In a lab DC:
New-ADUser -Name "svc_sql" -SamAccountName "svc_sql" -AccountPassword (ConvertTo-SecureString "Summer2024!" -AsPlainText -Force) -Enabled $true
setspn -A MSSQLSvc/sqlhost.lab.local:1433 LAB\svc_sql
# This account is now kerberoastable from any domain user.
```

```
# Lab 2 — Enumerate kerberoastable accounts from a Linux host with valid creds.
impacket-GetUserSPNs LAB.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1
# Each result line is an SPN whose account can be roasted.
```

```
# Lab 3 — Request a TGS and dump the crackable hash.
impacket-GetUserSPNs LAB.LOCAL/lowpriv:'Password1' -dc-ip 10.0.0.1 -request -outputfile tgs.hash
cat tgs.hash
# The output is a $krb5tgs$23$* line ready for hashcat.
```

```
# Lab 4 — Crack offline.
hashcat -m 13100 tgs.hash /usr/share/wordlists/rockyou.txt --force
# Mode 13100 = TGS-REP / RC4-HMAC. Use 19700/19800/19900 for AES variants.
# A 9-character keyboard-walk password against RC4 cracks in seconds on a modern GPU.
```

```
# Lab 5 — AS-REP roast against a pre-auth-disabled lab account.
# In the lab DC, mark an account with "Do not require Kerberos preauthentication":
Set-ADAccountControl -Identity legacy_user -DoesNotRequirePreAuth $true
# From the attacker host:
impacket-GetNPUsers LAB.LOCAL/ -dc-ip 10.0.0.1 -usersfile users.txt -no-pass -format hashcat -outputfile asrep.hash
hashcat -m 18200 asrep.hash /usr/share/wordlists/rockyou.txt --force
```

```
# Lab 6 — Validate detection from the defender side.
# After running the above, check the lab DC's Security log:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4769} -MaxEvents 50 |
  Where-Object { $_.Properties[5].Value -eq '0x17' }  # filter for RC4-HMAC
# Every line is a roasting candidate event. Build detection rules from this signal.
```

## Practical examples

- **Initial foothold via phished low-priv user.** Attacker phishes `lowpriv@corp.com`, kerberoasts the domain, recovers `svc_backup` password ("Backup2023!"), uses `svc_backup` membership in `Backup Operators` to access SAM database remotely, recovers `krbtgt` hash, forges Golden Ticket — domain compromised within hours of initial phish.
- **Acquired-company forest with weak service accounts.** Post-merger forest trust grants the parent domain authenticated-user access into the acquired domain. Kerberoasting reveals that the acquired domain's service accounts are 8-character dictionary words. Compromise of the acquired forest follows.
- **Web app SQL Server impersonation.** Web application connects to SQL Server as `svc_webapp`. Kerberoasting recovers the password, attacker logs into SQL Server as `svc_webapp` from another host, runs `xp_cmdshell`, lands as `NT SERVICE\MSSQLSERVER` on the SQL host, pivots from there.
- **Pre-auth-disabled legacy admin.** A 2009-era admin account left with pre-auth disabled (originally for a long-removed UNIX integration). AS-REP roast recovers the password (an ex-admin's name + birth year). Account is still in `Domain Admins`. Direct compromise without any prior credential.
- **Defender-side honeypot win.** Defender plants `svc_honeypot` with an SPN. Six months later, a TGS request from a workstation that never accesses anything else triggers the alert. The workstation is a beachhead the SOC didn't know about — the honeypot SPN catches the attacker mid-enumeration.

## Related notes

- [[password-hashing|Password hashing]] — Kerberoasting succeeds because the TGS encryption key is derived from a password; KDF strength determines crack cost.
- [[symmetric-encryption-modes|Symmetric encryption modes]] — RC4 vs AES in the Kerberos context is the difference between cracked-in-seconds and uncrackable.
- [[kdf-and-key-stretching|KDF and key stretching]] — why offline cracking economics depend on the KDF parameters.
- [[cia-triad-and-what-it-actually-decides|CIA triad]] — Kerberoasting is primarily an *integrity + authenticity* breach (impersonation), not pure confidentiality.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — Kerberoasting is the cleanest example of an attack with no signature, only behavioral detection.
- [[behavioral-detection-vs-signature-detection|Behavioral vs signature detection]] — the right defensive framing.
- [[attack-path-correlation-and-kill-chain-observability|Attack path correlation]] — Kerberoasting is rarely a single-event detection; chained with reconnaissance LDAP queries it produces a high-confidence signal.
- [[golden-ticket-and-krbtgt-compromise]] — the downstream trust-root abuse case when Kerberoasting leads to DCSync of `krbtgt`.
- [[silver-ticket-and-service-account-persistence]] — the direct service-scoped persistence path after service-account key recovery.
- [[gmsa-and-modern-service-account-hardening]] — the defensive service-account design pattern that changes Kerberoasting economics.
- [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] — the defender-side playbook pair for this note.
- [[enumeration|Enumeration]] — SPN enumeration is one specific case of the broader enumeration pattern.
- [[active-recon|Active Recon]] — Kerberoasting fits the active-recon stage of an AD engagement.

### Suggested future atomic notes

- ad-spn-enumeration-techniques

## References

- **Foundational:** MITRE ATT&CK T1558.003 — Steal or Forge Kerberos Tickets: Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Cracking Kerberos TGS Tickets Using Kerberoast — https://adsecurity.org/?p=2293
- **Research / Deep Dive:** Tim Medin — Attacking Microsoft Kerberos: Kicking the Guard Dog of Hades (DerbyCon 2014, the original Kerberoasting talk) — https://www.youtube.com/watch?v=PUyhlN-E5MU
