---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Tier 0 Administration and Privileged Access Workstations

## Definition

**Tier 0** is the set of identities, hosts, and components that have *effective control over the directory itself* — Domain Controllers, the principals with `DCSync` or equivalent replication rights, the AD recovery infrastructure (backups, key servers), and the certificate authorities that issue trust material. **Tier 0 administration** is the discipline of treating those identities and hosts as a strictly isolated security plane: they never log in to lower-tier systems, never run user-tier software, and never share credential material with anything outside the Tier 0 boundary. A **Privileged Access Workstation (PAW)** is the dedicated hardware (or VM) that Tier 0 admins use exclusively to perform Tier 0 work — locked down, internet-isolated, with no email client, no browser to arbitrary destinations, and no daily-driver applications.

## Definition (continued)

The Microsoft model layers below Tier 0:
- **Tier 1** = server admins (application servers, database admins, hypervisor admins).
- **Tier 2** = workstation admins, helpdesk, user-facing IT.
The defining rule is one-way: a higher tier can administer a lower tier; **a lower tier cannot escalate into a higher tier**. Credentials, sessions, and trust flow downward only.

## Why it matters

Every AD attack in this branch — [[kerberoasting|Kerberoasting]], [[as-rep-roasting|AS-REP Roasting]], [[bloodhound-attack-path-analysis|BloodHound]] path-finding, [[dcsync-and-ntdsdit-extraction|DCSync]], [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] — has the same fundamental shape: an attacker compromises a low-tier credential and traverses a chain of trust relationships that ends at Tier 0. **Tier separation is what eliminates the chain.** If a Tier 0 admin's credentials never appear on a Tier 1 or Tier 2 host, every credential-theft attack on those lower-tier hosts produces credentials that cannot reach Tier 0. The blast radius of a workstation compromise is bounded at the workstation.

The senior framing is that tier administration is the **structural** defense — the one that does not depend on detection working, behavioral analytics being tuned correctly, or the operator making mistakes. It changes the rules of the game rather than the speed of one side. BloodHound output without Tier 0 isolation is "show me my attack paths"; BloodHound output with proper Tier 0 isolation is "show me that no attack paths exist between Tier 1/2 and Tier 0".

The technique also matters as a teaching note because it forces three difficult organizational facts into view:

- **Most organizations have far more Tier 0 principals than their org chart implies.** "Domain Admins" is the visible subset. Effective Tier 0 includes anyone with `DCSync`, anyone in `Backup Operators` (can read `ntds.dit`), anyone with `Manage CA` on AD-CS, anyone with admin rights on a DC, anyone who can sign code that DCs trust, and anyone who can modify GPOs that DCs apply. The real count is routinely 5–10× the org-chart count.
- **Tier 0 admin work is operationally inconvenient by design.** No email, no browser, no Slack on the PAW. Admins push back. The senior framing is that *the inconvenience is the control* — anything that makes Tier 0 administration feel like normal IT work has weakened the boundary.
- **Microsoft has moved away from "ESAE / Red Forest" toward the simpler Enterprise Access Model.** Operators reading 2017–2020 documentation will see "Enhanced Security Admin Environment" (ESAE / Red Forest) as the recommended architecture. Microsoft deprecated ESAE in 2020 and now recommends the Enterprise Access Model with PAWs, Just-In-Time access, and Privileged Identity Management instead. The current guidance is *simpler and stronger*.

## How it works

The Tier 0 discipline operationalizes through **4 rules**:

1.
**Define and enumerate Tier 0 explicitly.** Use [[bloodhound-attack-path-analysis|BloodHound]] defensively: `MATCH (n)-[:DCSync|GetChanges|GetChangesAll]->(:Domain) RETURN n.name` plus `MATCH (n)-[:AdminTo|GenericAll|WriteDACL]->(:Computer {tier0: true}) RETURN n.name`. Tag every result as Tier 0 in the directory. The exhaustive list is the input to every subsequent rule.

2.
**Tier 0 identities use Tier 0 credentials only on Tier 0 systems.** Tier 0 admins have a dedicated admin account (`svc-ad-admin-alice`) that is *separate* from their daily-driver account (`alice@corp.com`). The admin account is used only when logged on to the PAW; it is never used on workstations, servers, jump boxes, or anywhere else. Enforcing this requires GPO restrictions ("Deny logon locally" / "Deny logon as a service" on lower-tier hosts) and audit alerting for violations.

3.
**PAWs are physically (or logically) separate from the user's daily-driver machine.** The PAW has: dedicated hardware or a hypervisor-isolated VM; restricted internet egress (allowlist to Microsoft Update + Azure AD + nothing else); no Office, no email, no Slack, no general-purpose browser; Credential Guard + Device Guard enabled; AppLocker or WDAC enforcing executable allowlists; BitLocker on every drive. The PAW is the *only* host where Tier 0 credentials are typed or cached.

4.
**Tier 0 administration uses Just-In-Time access where possible.** The user's admin account is *not* a permanent member of `Domain Admins`; instead, they request elevation through Privileged Identity Management (PIM, in Entra ID / Microsoft Identity Manager). Membership is granted for a bounded window (typically ≤ 4 hours) and requires MFA at elevation time. The default state of every Tier 0 admin is "not a Tier 0 member" — they elevate only when needed.

A representative BloodHound query for the *defensive* enumeration step:

```
// Effective Tier 0: anyone with DCSync, RDP-to-DC, Admin-to-DC, or GPO control over DCs.
MATCH (n)-[:DCSync|GetChanges|GetChangesAll|AdminTo|CanRDP|GpLink|WriteDACL]->(t)
WHERE t.tier = 0 OR t.name CONTAINS 'DC' OR t.name CONTAINS 'DOMAIN CONTROLLERS'
RETURN DISTINCT n.name AS principal, labels(n)[0] AS type
ORDER BY type, n.name
```

The bug is not "AD has too many privileges"; it is *trust relationships flow transitively across hosts when credentials are cached, and any cached Tier 0 credential on a non-Tier-0 host extends the Tier 0 boundary to wherever that host lives*.

## Techniques / patterns

- **Run BloodHound monthly *on your own AD* to monitor Tier 0 drift.** A clean BloodHound result one quarter does not mean clean next quarter — new delegations, new Exchange installations, new service-account creations all add edges. Continuous monitoring of the Tier 0 set is the operational discipline.
- **Use `Protected Users` group for every Tier 0 admin account.** Forces Kerberos with AES, disables NTLM/LM/DES/RC4 for that user, prevents long-term credential caching on member hosts. The single biggest defensive multiplier for Tier 0 accounts. See [[pass-the-hash-and-ntlm-credential-reuse|Pass-the-Hash]] §Detection-and-defense item 4.
- **Authentication Policies and Silos.** Beyond Protected Users, Authentication Policies let you restrict *which hosts* a credential can be used on (e.g., "the `svc-ad-admin-*` accounts can only authenticate to `paw-*` and `dc-*` computers"). The structural enforcement of the per-account rules.
- **Restrict Tier 0 group memberships with `AdminSDHolder` audit + alerting.** Tier 0 groups have their ACLs templated by `AdminSDHolder`. Changes propagate every 60 minutes. Alert on any modification to `AdminSDHolder` or to the membership of any Tier 0 group; both are high-fidelity red-team indicators.
- **Disable RDP for Tier 0 admins to anywhere other than PAWs and DCs.** GPO: deny logon via Remote Desktop for the Tier 0 admin group on every Tier 1/2 host. Closes the "admin RDP'd to the workstation to fix it, attacker harvested credentials from LSASS" failure mode.
- **PAW hardening checklist** (from Microsoft's Enterprise Access Model): Windows 11/Server 2022+, Credential Guard + Device Guard enabled, BitLocker with TPM PIN, AppLocker/WDAC allowlist policy, no local admin for the user, no software install rights, mandatory MFA at sign-in, time-limited sign-in window, full SIEM logging.
- **Don't forget the certificate authority.** AD-CS is Tier 0. Anyone with `Manage CA` or who can issue certificates with the right templates can forge auth as anyone in the domain (shadow-credentials-and-kerberos-pkinit). Audit AD-CS permissions with [[bloodhound-attack-path-analysis|BloodHound]] AD-CS edges and tier the CA admins accordingly.

## Variants and bypasses

Tier 0 architecture has **3 implementation variants** in real environments.

### 1. Microsoft Enterprise Access Model (current guidance, post-2020)

The current Microsoft recommendation. Three tiers, PAWs for Tier 0, Privileged Identity Management for Just-In-Time elevation, Authentication Policies and Silos enforcing the boundary. Implementable on Windows Server 2016+. The default starting point for new deployments.

### 2. ESAE / Red Forest (deprecated, but still deployed)

The 2014–2020 pattern: a dedicated *administrative forest* trusted by the production forest, with all Tier 0 admin accounts living in the admin forest. Provides strong isolation but operationally heavyweight. Microsoft deprecated this in 2020; environments that already deployed it are not advised to migrate just to migrate, but new deployments should use the Enterprise Access Model.

### 3. Cloud-native Tier 0 (Entra ID / Azure AD)

For organizations whose identity plane is Entra ID rather than on-prem AD. Tier 0 is `Global Administrator`, `Privileged Role Administrator`, and the Conditional Access policy administrators. PAWs are still hardware-isolated; PIM provides Just-In-Time elevation; Conditional Access policies enforce "Tier 0 sign-in only from compliant Intune-managed PAW devices". The cloud equivalent of the on-prem model.

## Impact

Ordered by how often these patterns appear in real-world AD compromises:

- **Most successful AD compromises terminate at Tier 0 via a chain that Tier separation would have eliminated.** This is the primary impact — not having the discipline is *the* enabler of total-domain compromise.
- **Tier 0 admins logging in to workstations.** The single most common chain: admin logs in to a workstation to fix an issue → credential cached in LSASS → workstation compromised later → operator extracts the cached admin credential → uses it for DCSync. PAW + "deny logon" GPOs eliminate this.
- **Service accounts in Tier 0 groups.** Service accounts in `Domain Admins` because someone-once-needed-DCSync-for-a-migration-script-in-2014. Kerberoast the service account → become Tier 0. Auditing Tier 0 group membership for service accounts is the single highest-leverage one-time cleanup.
- **Forgotten Tier 0 principals from legacy installations.** Exchange installation in 2015 added `Exchange Trusted Subsystem` with effective DCSync. Exchange was decommissioned in 2020. The group still exists. Anyone who can add themselves to it has Tier 0. Audit + remove.
- **Cross-forest trust scenarios with Tier 0 admin accounts that span both.** Tier 0 admin in forest A who also has Tier 0 in forest B = single foothold compromises both forests. Discipline: separate Tier 0 admin accounts per forest, even if the same human owns them.

## Detection and defense

This note *is* the defense — it does not have a separate "detection and defense" section in the usual sense. Defenders run BloodHound monthly and remediate; detection lives in adjacent notes ([[detect-kerberoasting-and-as-rep-roasting|Detect Kerberoasting and AS-REP Roasting]] and What to detect that indicates Tier 0 boundary violation).

### What to detect that indicates Tier 0 boundary violation

Ordered by detection value:

1.
**Tier 0 admin account authenticating on a non-Tier-0 host.**
   Event 4624 on a workstation or Tier 1 server with the user account in the Tier 0 admin set. This should never happen under the model. Generate an immediate high-severity alert.

2.
**Tier 0 group membership changes.**
   Events 4728/4732/4756 (member added to a security-enabled group) where the group is in the Tier 0 set. Alert on every change; legitimate Tier 0 group changes happen rarely (≤ once per month) and should always come from a known change-management ticket.

3.
**AdminSDHolder modification.**
   Event 4670 (permissions on an object were changed) where the object is `AdminSDHolder`. Often the first step of a Tier 0 backdoor (an attacker gives themselves persistent rights to a Tier 0 group via the ACL template).

4.
**NTLM authentication from a Tier 0 admin account.**
   Tier 0 admins should be in `Protected Users` and therefore unable to authenticate via NTLM. Any Event 4624 with LogonType=3, AuthenticationPackage=NTLM, and user in the Tier 0 set is either a misconfiguration or an active attack.

5.
**Concurrent active sessions for a Tier 0 admin account.**
   A real admin uses one session at a time. Two simultaneous sessions on different hosts are almost always either a forgotten session or a credential theft.

### What does not work as a primary defense

- **"Just tell admins not to log in to workstations."** Without GPO enforcement, the rule is honored when convenient and broken when inconvenient. The control must be technical.
- **MFA on the Tier 0 admin account without limiting *where* it can be used.** MFA prevents brute force / phishing of the password; it does not prevent credential extraction from LSASS on a workstation where the admin has already authenticated. PAW + Authentication Policies is the structural answer.
- **Trusting that "we removed Domain Admin from those accounts".** Run BloodHound. Domain Admin is one of many ways to be Tier 0. Effective enumeration is the only reliable answer.
- **A single audit at deployment time.** Tier 0 drift is continuous. The discipline must be ongoing.

## Practical labs

```
# Lab 1 — Enumerate the effective Tier 0 in a lab AD.
# In BloodHound's Cypher query box:
MATCH (n)-[:DCSync|GetChanges|GetChangesAll|AdminTo|CanRDP|WriteDACL]->(t)
WHERE t.name CONTAINS 'DC' OR t.name CONTAINS 'DOMAIN CONTROLLERS'
RETURN DISTINCT n.name AS principal, labels(n)[0] AS type
ORDER BY type, n.name
# Every result that is NOT a Domain Controller computer-account is a Tier 0 finding.
```

```
# Lab 2 — Audit Tier 0 group memberships in a lab AD.
$tier0Groups = @('Domain Admins', 'Enterprise Admins', 'Schema Admins',
                  'Administrators', 'Backup Operators', 'Account Operators',
                  'Server Operators', 'Print Operators', 'Domain Controllers',
                  'Read-only Domain Controllers', 'Enterprise Read-only Domain Controllers',
                  'Group Policy Creator Owners', 'Cryptographic Operators')
foreach ($g in $tier0Groups) {
    Get-ADGroupMember -Identity $g 2>$null |
        Select-Object @{n='Group';e={$g}}, SamAccountName, ObjectClass
}
# Anything other than a small number of dedicated admin accounts + DC computer accounts is a finding.
```

```
# Lab 3 — Add a test user to Protected Users and verify NTLM is blocked for them.
Add-ADGroupMember -Identity 'Protected Users' -Members 'testadmin'
# Then from a member host try NTLM auth:
$cred = Get-Credential testadmin
Invoke-Command -ComputerName lab-srv-01 -Credential $cred -Authentication Negotiate -ScriptBlock { whoami }
# Expected with NTLM negotiated: failure. With Kerberos: success.
# Validates the Protected Users hardening for Tier 0 admins.
```

```
# Lab 4 — GPO: deny Tier 0 admin logon to Tier 1/2 hosts.
# Create a GPO linked to OUs for Tier 1 (servers) and Tier 2 (workstations):
#   Computer Configuration -> Policies -> Windows Settings -> Security Settings ->
#     Local Policies -> User Rights Assignment ->
#       Deny log on locally:         add 'Tier 0 Admins' group
#       Deny log on through Remote Desktop Services: add 'Tier 0 Admins'
#       Deny log on as a batch job:  add 'Tier 0 Admins'
#       Deny log on as a service:    add 'Tier 0 Admins'
# Apply, force gpupdate, then verify by attempting to log on with a Tier 0 admin account:
$cred = Get-Credential
Enter-PSSession -ComputerName lab-ws-01 -Credential $cred
# Expected: explicit deny error, not "authentication failed".
```

```
# Lab 5 — Detect Tier 0 admin logon on a non-Tier-0 host (defender-side rule).
$tier0Users = @('alice-adm', 'bob-adm', 'carol-adm')
$nonTier0Computers = (Get-ADComputer -Filter * -SearchBase "OU=Workstations,DC=lab,DC=local").Name
Get-WinEvent -ComputerName lab-srv-01 -FilterHashtable @{
    LogName='Security'; ID=4624; StartTime=(Get-Date).AddHours(-24)
} -ErrorAction SilentlyContinue |
    Where-Object {
        $tier0Users -contains $_.Properties[5].Value -and
        $nonTier0Computers -contains $_.Properties[1].Value
    } |
    Select-Object TimeCreated, @{n='User';e={$_.Properties[5].Value}}, @{n='Host';e={$_.Properties[1].Value}}
# Every result is a Tier-0-boundary-violation alert. Pipe into your SIEM.
```

## Practical examples

- **Quarterly BloodHound audit eliminates 312 attack paths.** Defender's review shows `IT Helpdesk` group has `ForceChangePassword` on 47 service accounts, several of which are in `Domain Admins`. One ACE removal severs 312 distinct paths to DA. Reduces total Tier 0 path count by ~80% in one change.
- **PAW deployment after IR finding.** An IR investigation reveals the breach started when a Tier 0 admin RDP'd into a developer workstation to "quickly fix" something; the workstation was already compromised, the operator harvested the cached credential, and DA was achieved in 90 seconds. Three months later: PAWs deployed, deny-logon GPOs enforced, similar follow-up engagement six months later confirms the same chain no longer functions.
- **Service account audit catches the legacy DCSync principal.** Audit of Tier 0 effective-rights finds that `svc_exchange_2014` still has effective DCSync via inherited Exchange-installation permissions from a 2015 Exchange deployment decommissioned in 2020. Removal eliminates a near-invisible permanent backdoor.
- **PIM Just-In-Time access reduces Tier 0 footprint by 95%.** Before PIM: 12 permanent Tier 0 admin accounts. After PIM: 0 permanent Tier 0 admins; the same 12 humans can request elevation, MFA at elevation time, ≤ 4-hour membership window. A compromised credential outside the activation window is not Tier 0.
- **Cross-forest trust violation found.** An admin in forest A also has Tier 0 in forest B. Single compromise of their workstation (which is in forest A) would compromise both forests. Remediation: separate admin accounts per forest, never the same credential material.

## Related notes

- [[bloodhound-attack-path-analysis]] — the canonical tool for enumerating effective Tier 0 and identifying boundary-violation chains.
- [[kerberoasting]] — service accounts in Tier 0 are the highest-impact Kerberoasting targets; this note's "audit and remove privileged service accounts" defense is the same control.
- [[as-rep-roasting]] — same: pre-auth-disabled accounts in Tier 0 = catastrophic exposure.
- [[dcsync-and-ntdsdit-extraction]] — DCSync rights are *the* Tier 0 boundary; auditing them is the Tier 0 audit.
- [[pass-the-hash-and-ntlm-credential-reuse]] — PtH chains terminate at Tier 0; this note is the structural break for those chains.
- [[gmsa-and-modern-service-account-hardening]] — gMSA accounts eliminate the "service account in Tier 0 with a weak password" pattern; pairs with this note for the service-account hardening discipline.
- [[krbtgt-rotation-and-tier-zero-recovery]] — when Tier 0 isolation fails and recovery is required.
- [[threat-modeling-quickstart|Threat Modeling Quickstart]] — Tier separation is the AD-specific application of the threat-modeling discipline of trust-boundary analysis.

### Suggested future atomic notes

- authentication-policies-and-silos — the GPO+claims mechanism that enforces "this credential can only be used here".
- just-in-time-privileged-identity-management — PIM patterns for AD and Entra ID.
- adminsdholder-and-tier-0-acl-templates — the AD-specific ACL propagation mechanism for Tier 0 groups.
- enterprise-access-model-vs-esae — the historical migration and why ESAE was deprecated.

## References

- **Hardening:** Microsoft Learn — Enterprise Access Model — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model
- **Hardening:** Microsoft Learn — Privileged Access Workstations (PAW) — https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-deployment
- **Hardening:** Microsoft Learn — Protected Users security group — https://learn.microsoft.com/en-us/windows-server/security/credentials-protection-and-management/protected-users-security-group
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Securing Domain Controllers to Improve Active Directory Security — https://adsecurity.org/?p=3299
