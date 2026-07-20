---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Detect DCSync and ntds.dit Access

## Goal

Detect both forms of bulk Active Directory credential extraction — **DCSync** (`IDL_DRSGetNCChanges` via the DRSUAPI RPC interface) and **offline `ntds.dit` extraction** (file-level access, VSS shadow-copy abuse, `ntdsutil` invocations) — with high enough fidelity to identify the source principal, the affected accounts, and the post-extraction window before forged tickets ([[golden-ticket-and-krbtgt-compromise|Golden Ticket]] or [[silver-ticket-and-service-account-persistence|Silver Ticket]]) can be used.

## Assumptions

- you collect Windows Security event logs from **all Domain Controllers** into a SIEM with ≥ 90 days retention
- you have EDR coverage on every Domain Controller (Sysmon, Microsoft Defender for Identity, or equivalent)
- you maintain an authoritative list of principals with `DS-Replication-Get-Changes-All` and related replication rights (audited monthly via [[bloodhound-attack-path-analysis|BloodHound]])
- you can hot-disable a compromised account and initiate the **twice-in-sequence `krbtgt` rotation procedure** within hours
- the goal is **detect, contain, and recover** — DCSync is the endgame attack; by the time it fires you are in incident-response mode

## Prerequisites

- DC audit policy: `Audit Directory Service Access: Success/Failure` enabled (this generates Event 4662 — **not on by default** on most Windows Server defaults)
- SIEM parsing for Event 4662 with the `Object > Properties` field indexed so the replication-rights GUIDs are queryable
- Authoritative list of:
- Domain Controller computer accounts (the only principals that should legitimately perform DCSync)
- Principals with effective replication rights via [[bloodhound-attack-path-analysis|BloodHound]] Cypher query
- Allowlist of legitimate ntds.dit access sources (backup software, AD recovery tooling)
- Pre-staged `krbtgt` rotation script (Microsoft's `New-KrbtgtKeys.ps1` or equivalent) tested in a recovery exercise — runbook ready, not improvised under pressure
- Optional: honey-principal with replication rights and a strong unused password — any DCSync attempt against this principal is high-confidence adversary activity

## Detection steps

> *This playbook pairs with [[dcsync-and-ntdsdit-extraction|DCSync and ntds.dit Extraction]]. Read offense + defense as the [[attacker-defender-duality-as-a-learning-tool|paired-reading discipline]] requires.*

### Phase 0 — Baseline (do once, refresh monthly)

1. **Enumerate effective replication rights.** In [[bloodhound-attack-path-analysis|BloodHound]]:
   `cypher
   MATCH (n)-[r:DCSync|GetChanges|GetChangesAll]->(:Domain)
   RETURN DISTINCT n.name AS principal, labels(n)[0] AS type`
   Only Domain Controller computer accounts and explicit Tier 0 admins should appear. Anything else is a **finding** — remediate before relying on detection.

2. **Inventory DC computer accounts.** SIEM lookup table populated with the SAM accounts and source IPs of every DC. Detection rules join against this list.
3. **Inventory legitimate `ntds.dit` access.** Backup vendors (Veeam, Commvault, native Windows Backup), AD recovery tooling, and *nothing else* should ever touch the file. Document the allowlist.
4. **Audit baseline `krbtgt` rotation cadence.** If `krbtgt` was last rotated more than a year ago, schedule a **single proactive rotation** before relying on this playbook — the password-history window assumes the current `krbtgt` is the only valid key.

### Phase 1 — Detect classic DCSync (DRSUAPI)

Operator signature: **Event 4662 on a Domain Controller with `Properties` containing the replication GUIDs, where the `Subject` is *not* a DC computer account**.

1.
**Replication-rights GUID rule (highest fidelity).** Alert when Event 4662 contains *any* of:
   - `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes)
   - `1131f6ad-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes-All)
   - `89e95b76-444d-4c62-991a-0facbeda640c` (DS-Replication-Get-Changes-In-Filtered-Set)
   `text
   index=wineventlog EventCode=4662
   (Properties="*1131f6aa-9c07-11d1-f79f-00c04fc2dcd2*"
     OR Properties="*1131f6ad-9c07-11d1-f79f-00c04fc2dcd2*"
     OR Properties="*89e95b76-444d-4c62-991a-0facbeda640c*")
   | lookup dc_computer_accounts SubjectUserSid AS legitimate_dc
   | where isnull(legitimate_dc)`
   Every match is an **immediate high-severity alert**. There are essentially zero legitimate false positives.

2.
**Per-account targeting profile.** If multiple 4662 events for replication GUIDs fire from one source against many distinct target accounts, the operator is performing `-just-dc` (full dump) rather than `-just-dc-user krbtgt` (surgical). The full-dump variant is louder but more frequently used by less-careful operators; the surgical variant requires faster response because the goal is usually one account (`krbtgt`).

3.
**Source-host process correlation via EDR.** Cross-reference the source IP from the 4662 event against EDR process telemetry on that host. Look for `secretsdump.py`, `mimikatz.exe`, `Rubeus.exe`, Impacket Python signatures, or unsigned binaries spawning during the alert window. A Windows host running `secretsdump.py` is a confirmed adversary; a Linux Impacket source is the canonical Kali/operator-host signature.

### Phase 2 — Detect ntds.dit offline extraction

Operator signature: **direct access to `C:\Windows\NTDS\ntds.dit`** on a DC, or **VSS shadow-copy creation** followed by file access, or **`ntdsutil` invocation** with `ifm` / `IFM` subcommands.

1.
**Sysmon Event 11 (file create) on shadow-copy paths.**
   `text
   index=sysmon EventCode=11
   TargetFilename="\\GLOBALROOT\Device\HarddiskVolumeShadowCopy*\Windows\NTDS\ntds.dit"`
   Any match is a **high-fidelity alert**. Legitimate backup software uses VSS but does *not* extract individual files this way.

2.
**Process creation: `ntdsutil`, `vssadmin create shadow`, `wbadmin start backup`.**
   `text
   index=wineventlog EventCode=4688 (NewProcessName="*\\ntdsutil.exe" OR
     (NewProcessName="*\\vssadmin.exe" AND CommandLine="*create shadow*") OR
     (NewProcessName="*\\wbadmin.exe" AND CommandLine="*ntds*"))`
   Alert with allowlist suppression for known-legitimate backup-software parent processes.

3.
**Sysmon Event 1 with `ntdsutil` + `IFM` argument pattern.** `ntdsutil "ac i ntds" "ifm" "create full c:\extract" q q` is the canonical operator command. The argument string is recognizable; alert specifically on it.

4.
**EDR file-handle telemetry on `ntds.dit`.** Modern EDR products (Defender for Endpoint, CrowdStrike, SentinelOne) emit file-handle-open events for sensitive AD database paths. Cross-reference with the legitimate-backup allowlist; everything else alerts.

### Phase 3 — Detect DCShadow (rogue-DC registration)

Operator signature: **anomalous changes to AD configuration container objects** — a non-DC host registering itself as a DC, then walking back the registration after pushing changes.

1. **Event 4929 / 4928** (replication source replica added/removed) outside the change-management window.
2. **Event 5136** (directory service object modified) on objects in `CN=Sites,CN=Configuration,...` with `SubjectUserSid` that is not a DC or scheduled-task service.
3. **Sysmon network connections to TCP 135 (RPC) + dynamic high ports** from a non-DC host with a target of a DC — the DRSUAPI inbound-replication signature when *the source is impersonating a DC*.

DCShadow is rarer and stealthier than classic DCSync; detection often relies on Microsoft Defender for Identity's purpose-built rule rather than raw Event-Log queries.

### Phase 4 — Investigation and response

Once any Phase 1–3 alert fires:

1. **Treat as a confirmed compromise until proven otherwise.** False-positive rate on these rules is near zero; the response posture should reflect that.
2. **Identify the source host and principal.** Phase 1: pull `SubjectUserSid` and source IP from the 4662 event. Phase 2: pull the parent process tree from EDR. Build the operator timeline for the last 24 hours from that source.
3. **Determine extraction scope.**
   - `-just-dc-user <target>` → only the named account's hash is compromised. Surgical response: rotate that account's password.
   - `-just-dc` (full dump) → **every account in the domain** is compromised, including `krbtgt`. Full-domain response.
   - ntds.dit + SYSTEM hive copied → same as full dump.
4. **Initiate `krbtgt` rotation if `krbtgt` was in scope.** Use Microsoft's `New-KrbtgtKeys.ps1` script. **Twice in sequence**, with ≥ 10 hours between rotations to let replication and the password-history window roll over. A single rotation is insufficient because the previous `krbtgt` hash remains valid.
5. **Disable the source account.** Force re-authentication for every Tier 0 admin (assume their credential may have enabled the attack chain). Audit every authentication event from the source IP in the past 30 days.
6. **Audit Golden / Silver Ticket use.** Any TGT or TGS for `krbtgt` or service accounts issued between the extraction time and the rotation completion is potentially forged. Cross-reference with [[detect-kerberoasting-and-as-rep-roasting]] alerts in the same window.
7. **Open an IR ticket** with: triggering event(s), source host + principal + IP, list of extracted accounts (if known), `krbtgt` rotation status, Golden/Silver Ticket audit findings, full BloodHound snapshot before and after the suspected extraction.

## Validation clues

- **High-confidence DCSync:** Event 4662 with replication GUIDs from a non-DC `SubjectUserSid`. Single event is sufficient.
- **High-confidence ntds.dit extraction:** Sysmon Event 11 on a shadow-copy path ending in `ntds.dit`, or `ntdsutil` invocation with `IFM`/`ifm` arguments outside the change-management window.
- **Honey-principal fired:** any DCSync attempt against the honey replication-rights principal. Near-zero false positive — investigate as confirmed adversary activity.
- **Chain evidence:** the same source IP/principal that triggered a Kerberos alert ([[detect-kerberoasting-and-as-rep-roasting]]) in the previous hours, now performs DCSync. Confirms a Kerberoasting → cracked-service-account → DCSync chain — the canonical AD endgame.
- **Forged-ticket evidence post-rotation:** Event 4769 (TGS issued) where the ticket's `krbtgt` encryption type does not match either the current or previous `krbtgt` key. Indicates a Golden Ticket forged with an old, leaked `krbtgt` hash still in use after a single (insufficient) rotation.

## Mitigation / remediation

On the defender side, these are durable controls (not per-alert fixes):

- **Monthly BloodHound audit of effective replication rights.** Query `MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name`. The healthy result is "only DCs and explicit Tier 0 admins". Anything else is a finding to remediate. See [[dcsync-and-ntdsdit-extraction|DCSync]] §Detection-and-defense item 1.
- **Quarterly proactive `krbtgt` rotation.** Twice in sequence, on a quarterly cadence, even without suspected compromise. Shortens the worst-case Golden Ticket window from "decades" to "≤ 3 months".
- **[[tier-zero-administration-and-paw|Tier 0 administration]] discipline.** PAWs, Authentication Policies, Protected Users membership for all Tier 0 admins. The structural defense that prevents the credential-theft chain ending at DCSync.
- **Audit `Exchange Trusted Subsystem` and related Exchange-installed groups.** Historical Exchange installations grant effective DCSync to multiple groups. Decommissioning Exchange does *not* automatically remove these grants — explicit audit-and-remove required.
- **Disable NTLMv1 domain-wide.** NTLM-relay-to-DCSync chains exist; eliminating the relay surface forces operators into Kerberos-only paths that this playbook detects better.
- **Plant honey-principals.** A fake account with `DS-Replication-Get-Changes-All` and a strong unused password is by definition adversary-only traffic when accessed.

### What does not work as a primary defense

- **Blocking DRSUAPI at the network level.** DCs must replicate; blocking the protocol breaks the directory.
- **Trusting that "only DCs have replication rights".** Verify with BloodHound. Exchange-installation legacy grants routinely produce surprise principals.
- **Single `krbtgt` rotation.** Password history retains the previous hash; one rotation does not invalidate leaked material.
- **Trusting low alert volume.** A *single* 4662 event with a replication GUID from a non-DC source is the signature. Volumetric thresholds miss the surgical operator.
- **Trusting EDR alone.** Modern operators use signed Microsoft binaries (Impacket via Python, in-memory secretsdump variants) that bypass binary-name signatures. The Event-Log-side detection is structural; EDR is the corroboration layer.

## Logging / forensics

- **Retain DC Security logs for ≥ 90 days.** DCSync followed by Golden Ticket use often spans weeks; retention is the floor that supports forensic timeline reconstruction.
- **Tag every alert with:** source IP, source `SubjectUserSid`, target account(s), replication GUID(s) used, allowlist status (was the source a legitimate DC?), `krbtgt` rotation status at time of alert, correlated Kerberoasting/AS-REP alerts in the prior 30 days.
- **Capture the full DRSUAPI RPC traffic from the source if possible.** Network telemetry (Zeek `dce_rpc.log`, Sysmon Event 3) from the source IP during the alert window often reveals the operator's tool fingerprint (Impacket vs Mimikatz vs custom).
- **Snapshot BloodHound before *and* after the suspected compromise.** Comparing graph states reveals whether the operator added DCSync rights to other principals post-compromise (a common persistence move).
- **Cross-reference with [[attack-path-correlation-and-kill-chain-observability|attack-path correlation]].** A single DCSync alert is high-confidence; a DCSync alert preceded by Kerberoasting, BloodHound collection, and lateral SMB activity is a confirmed kill chain ready for incident-response handoff.

## Operational safety

- **never** auto-disable replication on a DC computer account in response to an alert — the DC must replicate to remain in the directory.
- **never** rotate `krbtgt` only once after suspected compromise; always twice in sequence with replication-wait between.
- **always** maintain a documented allowlist of legitimate ntds.dit access sources (backup software, AD recovery tooling) before relying on Phase 2 detection rules.
- **always** test the detection rules against an authorized internal lab running [[dcsync-and-ntdsdit-extraction|DCSync]] before relying on them in production. Untested rules are theater.
- **always** treat a Phase 1 alert as a confirmed compromise until proven otherwise — the false-positive rate is near zero and the cost of slow response is total-domain compromise.

## Related notes

- [[dcsync-and-ntdsdit-extraction|DCSync and ntds.dit Extraction]] — the offense playbook this one mirrors.
- [[golden-ticket-and-krbtgt-compromise|Golden Ticket and krbtgt Compromise]] — the immediate-next attack after DCSync; the reason `krbtgt` rotation is the response priority.
- [[silver-ticket-and-service-account-persistence|Silver Ticket and Service Account Persistence]] — the service-account-scoped equivalent after DCSync recovers a service-account hash.
- [[krbtgt-rotation-and-tier-zero-recovery|krbtgt Rotation and Tier 0 Recovery]] — the canonical recovery procedure after suspected `krbtgt` compromise.
- [[bloodhound-attack-path-analysis|BloodHound]] — the tool for both the offensive enumeration of replication rights and the defensive audit.
- [[tier-zero-administration-and-paw|Tier 0 Administration]] — the structural defense that makes the chain to DCSync impossible.
- [[detect-kerberoasting-and-as-rep-roasting]] — the upstream detection that frequently precedes a DCSync alert in the same chain.
- [[windows-event-logs|Windows Event Logs]] — Event 4662 + replication GUIDs reference; Event 4929 / 5136 (DCShadow indicators).
- [[behavioral-detection-vs-signature-detection|Behavioral vs Signature Detection]] — the right framing for DCSync detection; no useful signature exists at the bug-class layer.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — multi-stage correlation across recon + Kerberoast + DCSync + Golden Ticket.
- [[run-scan-pipeline]] / [[detect-external-scan-pipeline]] — the parallel offense/defense playbook pair pattern this playbook follows.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the meta-principle.

## References

- **Foundational:** MITRE ATT&CK T1003.006 — OS Credential Dumping: DCSync — https://attack.mitre.org/techniques/T1003/006/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Mimikatz DCSync Usage, Exploitation, and Detection — https://adsecurity.org/?p=1729
- **Foundational:** Microsoft Learn — AD DS replication permissions and audit guidance — https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/ad-replication-event-id-1864
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/
- **Research / Deep Dive:** Microsoft Defender for Identity — DCSync attack detection — https://learn.microsoft.com/en-us/defender-for-identity/credential-access-alerts
