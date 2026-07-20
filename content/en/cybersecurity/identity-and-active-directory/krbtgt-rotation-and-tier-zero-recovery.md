---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# KRBTGT Rotation and Tier Zero Recovery

## Definition

KRBTGT rotation is the controlled reset of the domain's `krbtgt` account password material so previously stolen Kerberos ticket-signing keys can no longer validate forged Ticket Granting Tickets. It is not a normal password reset. After suspected `krbtgt` compromise, it is a Tier 0 recovery operation that must account for ticket lifetimes, password history, domain controller replication, trust relationships, privileged access hygiene, and operational outage risk.

## Why it matters

[[golden-ticket-and-krbtgt-compromise|Golden Ticket]] compromise turns AD recovery into a trust-restoration problem. If the attacker has the `krbtgt` key, they may not need any live user password to authenticate. They can present forged TGTs that appear to belong to real users. Rotating every administrator password while leaving `krbtgt` unchanged fixes the wrong secret.

The recovery principle:

```
If krbtgt is compromised, the domain cannot fully trust Kerberos TGTs
until old krbtgt material is pushed out of validity and replication windows.
```

This makes recovery operationally delicate. Rotate too casually and forged tickets remain valid. Rotate too aggressively without replication and dependency planning and legitimate Kerberos authentication can break across the domain.

## How it works

KRBTGT recovery depends on **6 mechanics**:

1. **`krbtgt` signs and encrypts TGTs.** The KDC uses `krbtgt` password-derived keys to protect TGTs. Services do not know the user's password; they trust Kerberos tickets.
2. **Domain Controllers cache current and previous keys.** AD keeps previous password material so existing tickets can continue working during normal rotation and replication.
3. **One reset does not necessarily invalidate all forged tickets.** A forged ticket made with the previous key can remain accepted until the second reset and ticket lifetime/replication windows expire.
4. **Replication timing matters.** Every DC must receive the new `krbtgt` password state before the next phase. A DC with stale material can continue validating old tickets or issue inconsistent responses.
5. **Ticket lifetime matters.** Existing TGTs and renewable tickets may continue until policy limits unless explicitly disrupted by key changes and operational controls.
6. **Tier 0 containment must precede recovery.** If attackers still control DCSync, DCs, Tier 0 admin sessions, or backups, they can simply steal the new key after rotation.

The structural lesson is *KRBTGT rotation is a sequencing problem*. The reset command is small; the recovery operation around it is the work.

## Techniques / patterns

- **Contain before rotating.** Remove or disable suspected DCSync principals, isolate compromised DCs, protect Tier 0 admin workstations, and stop active attacker access before changing the trust root.
- **Use the double-reset concept.** First reset moves away from the known compromised key; second reset pushes the compromised key out of the previous-password slot. Wait for replication and ticket lifetimes between resets.
- **Validate replication between phases.** Check DC convergence before the second reset. Multi-site domains and offline DCs are the classic failure points.
- **Assume backup exposure matters.** If attackers accessed DC backups, snapshots, or `ntds.dit`, the recovery boundary includes backup protection and restoration paths.
- **Account for trusts.** Forest trusts, child domains, external trusts, and SID filtering affect what forged tickets can access and which domains need recovery.
- **Separate admin identities.** Use clean Tier 0 credentials from trusted PAWs. Do not perform recovery from a compromised workstation.
- **Monitor intensely during and after.** Watch for replication requests, suspicious Kerberos failures, privileged logons, service outages, and old-ticket use.
- **Document rollback limits.** Rolling back a DC snapshot after `krbtgt` rotation can reintroduce old secret material. Recovery plans need explicit anti-rollback controls.

## Variants and operational scenarios

KRBTGT recovery has **5 common scenarios**.

### 1. Routine hygiene rotation

Planned rotation with no known compromise. Lower urgency, still requires replication validation and helpdesk awareness. Useful to prove the process before a crisis.

### 2. Suspected `krbtgt` exposure from DCSync

High confidence that `krbtgt` material was replicated or extracted. Requires containment, double reset, and monitoring for forged-ticket use.

### 3. Domain Controller compromise

More severe than one DCSync event. Assume attackers may have LSASS, NTDS, backup, and admin-session access. Rotation alone is insufficient until DC integrity is restored.

### 4. Forest or multi-domain compromise

Each domain has its own `krbtgt`. Recovery must identify which domains are compromised and how trusts can propagate access.

### 5. Legacy fragile environment

Old applications, RC4 dependencies, hard-coded SPNs, offline sites, and stale DCs can make rotation noisy. This is why routine rehearsal matters.

## Impact

Ordered by recovery significance:

- **Invalidates stolen TGT-signing material when sequenced correctly.** This is the direct control against Golden Tickets.
- **Forces attackers back to live credentials or newly stolen keys.** A completed recovery closes the old forged-ticket path.
- **Can disrupt authentication if rushed.** Bad sequencing can break Kerberos for legitimate users and services.
- **Reveals Tier 0 dependency debt.** Fragile trusts, stale DCs, and old service dependencies surface during rotation planning.
- **Raises incident-response maturity.** A team that can rotate `krbtgt` safely has usually done the Tier 0 inventory work many organizations avoid.

## Detection and telemetry

Monitor before, during, and after rotation:

1.
**DCSync and replication abuse.**
   Watch `4662` with replication GUIDs and any non-DC replication behavior. Rotation is pointless if attackers still have DCSync.

2.
**Kerberos failures after reset.**
   Track spikes in `4768`, `4769`, `4771`, and `4776` failures by DC, site, account, and service. Some failure spike is expected; unexplained concentration points to replication or service dependency problems.

3.
**TGS activity with old behavioral patterns.**
   If the same suspicious account/source/service pattern continues after rotation, the attacker may have live credentials, new key access, or a missed persistence path.

4.
**Privileged logons and special privileges.**
   Monitor `4624`, `4672`, admin group changes, DC logons, and PAW usage. Recovery should narrow privileged activity, not create new ambiguous admin sessions.

5.
**Endpoint and process telemetry on DCs.**
   Watch LSASS access, `ntds.dit` reads, VSS operations, suspicious PowerShell, remote execution, and backup access.

6.
**Replication health.**
   DC convergence is a security signal here, not only operations hygiene. Stale DCs can undermine recovery.

## Defensive controls

Ordered by recovery effectiveness:

1.
**Tier 0 containment first.**
   Disable or isolate compromised Tier 0 principals, remove unexpected DCSync rights, secure DCs, protect backups, and use trusted admin workstations.

2.
**Double-reset `krbtgt` with validated wait periods.**
   Perform reset 1, validate replication and operational stability, wait through the ticket lifetime/replication window, then perform reset 2 and validate again.

3.
**Use vendor-supported scripts and procedures.**
   Microsoft publishes forest recovery guidance and KRBTGT reset tooling. Use supported procedures so replication and compatibility checks are not improvised under stress.

4.
**Validate every DC.**
   Confirm replication health, time synchronization, authentication behavior, and absence of offline/stale DCs before declaring recovery complete.

5.
**Rebuild trust in privileged access.**
   Reset admin credentials, rotate service secrets where relevant, clean PAWs, review delegation, and remove graph paths to DCSync.

6.
**Monitor post-recovery for old patterns.**
   A successful `krbtgt` rotation invalidates old Golden Tickets; it does not prove the adversary has no other persistence.

### What does not work as a primary defense

- **Rotating every human password but not `krbtgt`.** Human credentials are not the secret that signs forged TGTs.
- **One `krbtgt` reset as a complete recovery.** The previous key can remain accepted. The double-reset sequence exists for a reason.
- **Rotating while attackers still have DCSync.** They can recover the new key and the rotation becomes theatre.
- **Running recovery from a compromised workstation.** Tier 0 recovery requires clean administrative endpoints.
- **Assuming replication will catch up eventually.** Eventual convergence is not a recovery guarantee. Validate it.
- **Snapshot rollback of DCs after rotation.** Restoring old DC state can reintroduce old key material and break trust assumptions.
- **Treating Golden Ticket recovery as a SIEM rule.** Detection helps; recovery requires changing the trust root and containing the path that exposed it.

## Operational misconceptions

- **"KRBTGT is just another account."** False. It is the domain Kerberos trust root.
- **"The reset command is the recovery."** False. The command is one step in containment, replication, validation, and monitoring.
- **"If users can still log in, recovery worked."** False. Availability is not the same as invalidating attacker-held key material.
- **"Only the compromised domain admin account matters."** False. Replication rights, DCs, backups, and PAWs define the recovery boundary.
- **"Rotation is too risky to practice."** Backwards. It is risky precisely because organizations do not rehearse it.

## Practical labs

Run as tabletop or in an owned lab domain. Do not experiment with production `krbtgt` rotation without an approved change and recovery plan.

```
Lab 1 — Tabletop the decision tree.
Objective: decide when KRBTGT rotation is required.
Inputs:
  - DCSync confirmed? yes/no
  - krbtgt material extracted? yes/no/unknown
  - DC compromise? yes/no
  - Tier 0 admin workstation compromise? yes/no
  - backup exposure? yes/no
Decision:
  If krbtgt exposure is confirmed or reasonably suspected, plan double reset after containment.
Misconception corrected: "no Golden Ticket observed" is not proof krbtgt is safe.
```

```
# Lab 2 — Replication health pre-check in a lab.
repadmin /replsummary
dcdiag /test:replications
w32tm /monitor

# Defender interpretation:
# - stale DCs and time drift are recovery blockers
# - replication health is part of the security control
```

```
Lab 3 — Simulated double-reset runbook.
Objective: rehearse sequencing without touching production.
Steps:
  1. Announce change window and freeze Tier 0 admin activity.
  2. Confirm DCSync paths removed.
  3. Reset krbtgt once using supported tooling.
  4. Validate replication to every DC.
  5. Wait through the defined ticket lifetime/replication window.
  6. Reset krbtgt a second time.
  7. Validate authentication, replication, and monitoring.
Expected telemetry:
  - account password-set events for krbtgt
  - Kerberos failure spikes if clients hold stale tickets
  - replication traffic across DCs
Limitations: tabletop cannot prove app compatibility; lab rotation should precede production playbook approval.
```

```
# Lab 4 — Monitor Kerberos failures during a lab reset window.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4768,4769,4771,4776} -MaxEvents 500 |
  Select-Object TimeCreated, Id, ProviderName

# Analyst exercise:
# - group by DC and account
# - separate expected cache churn from persistent service breakage
# - identify services still using stale Kerberos material
```

```
Lab 5 — Post-recovery validation checklist.
Validate:
  - every DC replicated the new krbtgt password version
  - no non-DC principal has DCSync rights
  - privileged accounts were rotated from clean PAWs
  - service accounts with high privilege were reviewed
  - DC backups and snapshots are protected
  - old suspicious TGS patterns stopped
  - incident timeline records exact reset times
```

## Practical examples

- **Single-reset incident gap.** An IR team rotates Domain Admin passwords and resets `krbtgt` once. Forged tickets continue during the old-key window. The missing second reset leaves the domain partially untrusted.
- **Replication failure.** One remote DC is offline during the rotation. It later returns with stale state and creates inconsistent authentication behavior. Recovery declaration was premature.
- **DCSync path not contained.** The attacker still controls a service account with replication rights. They steal the new `krbtgt` key after reset. The organization changed the secret but not the path to the secret.
- **Practiced routine rotation.** A team performs annual planned rotation with monitoring and rollback boundaries. During a real incident, the procedure is known and the risk is lower.

## Related notes

- [[golden-ticket-and-krbtgt-compromise]] — the compromise model this recovery operation addresses.
- [[dcsync-and-ntdsdit-extraction]] — the most common way `krbtgt` material is exposed.
- [[bloodhound-attack-path-analysis]] — use graph analysis to remove paths to DCSync and Tier 0.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — recovery monitoring is sequence-based.
- [[telemetry-normalization-correlation-and-enrichment|Telemetry Normalization, Correlation, and Enrichment]] — reset validation depends on normalized DC, endpoint, and identity telemetry.
- [[edr-network-observability-and-process-correlation|EDR, Network Observability, and Process Correlation]] — DC and PAW endpoint telemetry matter during containment.

### Suggested future atomic notes

- [[tier-zero-administration-and-paw]]
- ad-forest-recovery
- dc-backup-security
- dcsync-containment-playbook
- kerberos-ticket-lifetime-policy

## References

- **Recovery:** Microsoft Learn — Active Directory Forest Recovery: Reset the krbtgt password — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-reset-the-krbtgt-password
- **Recovery:** Microsoft Learn — AD Forest Recovery Guide — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-guide
- **Foundational:** MITRE ATT&CK T1558.001 — Golden Ticket — https://attack.mitre.org/techniques/T1558/001/
- **Recovery:** Microsoft Security Blog — KRBTGT Account Password Reset Scripts now available for customers — https://www.microsoft.com/en-us/security/blog/2015/02/11/krbtgt-account-password-reset-scripts-now-available-for-customers/
