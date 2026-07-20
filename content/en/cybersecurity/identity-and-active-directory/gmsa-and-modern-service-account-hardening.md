---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# gMSA and Modern Service Account Hardening

## Definition

A group Managed Service Account (gMSA) is an Active Directory-managed service identity whose password is long, random, automatically rotated, and retrievable only by explicitly authorized computers. gMSA is not a magic anti-Kerberoasting feature. It is a service-account design pattern that reduces static-password risk when SPN ownership, retrieval permissions, delegation, privilege, and monitoring are engineered correctly.

## Why it matters

Legacy service accounts are among the most common AD compromise bridges: they have SPNs, weak or never-rotated passwords, broad local rights, application privileges, and unclear owners. That makes them prime [[kerberoasting|Kerberoasting]] targets and direct predecessors to [[silver-ticket-and-service-account-persistence|Silver Ticket]] abuse.

gMSA changes the economics:

- no human-known password to reuse
- long random secrets that are impractical to crack offline
- automatic rotation through AD
- explicit scoping of which hosts may retrieve the managed password

But gMSA does not fix bad authorization. A gMSA that is local admin everywhere, allowed to delegate broadly, or retrievable by a huge computer group is still dangerous. The control is strongest when paired with least privilege, SPN inventory, delegation review, and telemetry.

## How it works

gMSA hardening reduces to **6 design facts**:

1. **The account is an AD security principal.** A gMSA has a SID, can own SPNs, can be granted permissions, and can authenticate to Kerberos-backed services.
2. **AD manages the password.** Domain Controllers compute and rotate a long random password according to policy; humans do not type or store it.
3. **Only authorized computers can retrieve it.** The `PrincipalsAllowedToRetrieveManagedPassword` setting defines which computers or groups may obtain the current managed password.
4. **SPNs still bind service identity.** The SPN must map cleanly to the service identity. Duplicate or stale SPNs create authentication failures and attack surface.
5. **Delegation remains dangerous.** Constrained delegation, resource-based constrained delegation (RBCD), and unconstrained delegation decisions still define where the account can act.
6. **Blast radius is privilege, not account type.** gMSA reduces password cracking risk; it does not reduce excessive ACLs, local admin rights, database roles, or application permissions by itself.

The structural lesson is *service-account hardening is identity engineering, not checkbox hardening*. gMSA removes one weak static secret from the system; the rest of the trust model still has to be designed.

## Techniques / patterns

- **Prefer gMSA for services that support it.** Windows services, scheduled tasks, IIS app pools, and some SQL Server deployments can use gMSA. Third-party support varies.
- **Use one gMSA per service boundary.** Do not create one universal `gmsa_app$` for every application. A shared identity collapses blast-radius boundaries.
- **Keep `PrincipalsAllowedToRetrieveManagedPassword` narrow.** Authorize only the hosts that actually run the service. Avoid broad groups like "Domain Computers".
- **Separate SPN ownership.** Each SPN should have a clear service owner, host set, business owner, and retirement process.
- **Deny interactive logon.** Service accounts should not be daily-driver identities. Restrict interactive, RDP, and remote shell logon where possible.
- **Remove local admin by default.** Grant the minimum file, registry, database, and network permissions the service needs. Local admin should require a documented exception.
- **Review delegation.** Prefer no delegation; if required, use constrained delegation to specific services. Treat RBCD writes as privileged edges in [[bloodhound-attack-path-analysis|BloodHound]].
- **Audit retrieval permissions.** Who can retrieve the managed password is equivalent to who can run as the service. That is an access-control surface.
- **Migrate legacy accounts by risk.** Start with SPN-bearing accounts that are privileged, weak-password suspected, RC4-capable, or reachable in BloodHound paths.

## Variants and design choices

Modern service-account design has **5 common patterns**.

### 1. Legacy user service account

User object with SPN and human-set password. Highest roasting and reuse risk. Acceptable only as a temporary state with random long password, AES-only, owner, rotation, and restricted privilege.

### 2. Standalone Managed Service Account

Managed password but bound to one host. Useful in older single-server patterns; less flexible than gMSA for clusters and farms.

### 3. gMSA per service

Preferred default. One managed identity per service boundary, narrow retrieval permissions, narrow SPNs, narrow local/application rights.

### 4. gMSA per tier or app family

Sometimes used for operational simplicity. Higher blast radius because compromise or misconfiguration affects multiple services. Requires explicit risk acceptance.

### 5. Delegated gMSA

gMSA with constrained delegation or RBCD. High risk if the delegation target is broad or if write access to delegation attributes is weak. Must be represented as an attack-path edge.

## Impact

Ordered by defender value:

- **Kerberoasting economics improve dramatically.** Long random managed passwords make offline cracking impractical in normal conditions.
- **Password reuse disappears.** The gMSA secret is not a human password reused for RDP, SMB, admin portals, or break-glass accounts.
- **Rotation becomes operationally normal.** The organization no longer depends on manual service outage windows for routine password rotation.
- **Inventory becomes enforceable.** SPN ownership, allowed retrieval hosts, and service identity can be represented in AD and monitored.
- **Blast radius becomes measurable.** One gMSA per service allows defenders to reason about exactly which systems and data a service identity can access.

## Detection and telemetry

Detection should focus on service-account inventory, use, and permission drift:

1.
**SPN-bearing legacy account inventory.**
   Query user accounts with `servicePrincipalName` and classify them by gMSA vs legacy account, encryption types, privilege, and owner.

2.
**Abnormal password retrieval permissions.**
   Monitor `PrincipalsAllowedToRetrieveManagedPassword`. Broad groups or unexpected computers are high-risk findings.

3.
**Service account logon outside service hosts.**
   gMSA or legacy service identity authenticating from a non-service host is suspicious. Correlate `4624`, host inventory, and service deployment records.

4.
**Interactive or remote logon attempts.**
   RDP/WinRM/console logon as a service account indicates misuse or compromise. Legitimate services should not behave like users.

5.
**Delegation drift.**
   Changes to constrained delegation, RBCD attributes, or SPN ownership can create lateral-movement paths. Feed these into [[bloodhound-attack-path-analysis|BloodHound]] and detection correlation.

6.
**Kerberoasting pressure against legacy service accounts.**
   Event `4769` patterns against SPNs identify which accounts attackers target and which legacy accounts should migrate first.

## Defensive controls

Ordered by effectiveness:

1.
**Default new services to gMSA where supported.**
   Make gMSA the standard path, not the exception. Exceptions must document why the service cannot support it.

2.
**Narrow retrieval scope.**
   `PrincipalsAllowedToRetrieveManagedPassword` should name only the computers or tightly controlled computer groups that run the service.

3.
**Least privilege at every layer.**
   Domain groups, local groups, SQL roles, file shares, application roles, and cloud connectors all need separate review. gMSA does not shrink these automatically.

4.
**Restrict logon rights.**
   Deny interactive logon, RDP, and network logon patterns that are not needed. Service identities should not be used by humans.

5.
**Use AES and disable RC4 for service accounts where possible.**
   This improves Kerberos security posture and turns RC4 usage into a more meaningful anomaly.

6.
**Continuously inventory SPNs and delegation.**
   Treat SPNs and delegation settings as production configuration, not as one-time AD setup.

7.
**Retire shared service accounts.**
   Shared identities make logs ambiguous and multiply blast radius. Split by service boundary and owner.

### What does not work as a primary defense

- **"We use gMSA, so Kerberoasting is solved."** gMSA helps strongly, but legacy SPNs, delegation, broad retrieval groups, and overprivilege still matter.
- **Long passwords on legacy accounts without ownership.** Helpful but fragile. Someone eventually reuses, weakens, or stops rotating them.
- **One gMSA for every service.** Operationally easy, security-poor. It recreates the all-powerful service account pattern.
- **Hiding service account names.** SPNs and service configuration reveal service identity.
- **Blocking roasting tools.** Roasting is normal TGS protocol usage. Fix service-account economics and detect behavior.
- **Assuming local admin is harmless for service accounts.** Local admin often creates lateral-movement and credential-exposure paths.

## Operational misconceptions

- **"gMSA is a product feature, not an architecture choice."** False. Its value depends on scoping, delegation, ownership, and monitoring.
- **"Automatic rotation means no recovery planning."** False. Services can still break if SPNs, host authorization, or rollout sequencing are wrong.
- **"Only Domain Admin service accounts matter."** False. Application, SQL, backup, and deployment accounts often carry business-critical privilege.
- **"Retrieval permission is low-risk."** False. Permission to retrieve the managed password is permission to run as the service.
- **"Service accounts do not need threat modeling."** False. They are machine-speed identities with often-broad access and weak human ownership.

## Practical labs

Run only in a private AD lab, intentionally vulnerable range, or authorized enterprise environment.

```
# Lab 1 — Inventory SPN-bearing service accounts.
# Objective: find legacy service accounts that should be considered for gMSA migration.
Get-ADUser -LDAPFilter "(servicePrincipalName=*)" `
  -Properties servicePrincipalName,msDS-SupportedEncryptionTypes,memberOf,lastLogonTimestamp |
  Select-Object SamAccountName, Enabled, servicePrincipalName, msDS-SupportedEncryptionTypes

# Defender observation:
# - legacy user accounts with SPNs are roastable candidates
# - privileged group membership raises migration priority
```

```
# Lab 2 — Create a lab gMSA with narrow retrieval scope.
# Preconditions: lab domain with KDS root key already created in the lab.
New-ADServiceAccount -Name gmsa_web `
  -DNSHostName gmsa_web.lab.local `
  -ServicePrincipalNames HTTP/web01.lab.local `
  -PrincipalsAllowedToRetrieveManagedPassword WEB01$

# On WEB01 in the lab:
Install-ADServiceAccount gmsa_web
Test-ADServiceAccount gmsa_web
```

Expected telemetry: AD object creation/modification, service installation on the authorized host, and normal Kerberos use from the service host only.

```
# Lab 3 — Audit managed-password retrieval permissions.
Get-ADServiceAccount -Filter * -Properties PrincipalsAllowedToRetrieveManagedPassword |
  Select-Object Name, PrincipalsAllowedToRetrieveManagedPassword

# Analyst exercise:
# - flag broad groups
# - flag computers that do not host the service
# - compare against CMDB/deployment inventory
```

```
Lab 4 — Before/after risk model.
Objective: show what gMSA changes and what it does not.
Before:
  svc_web user account, SPN HTTP/web01, weak password, local admin on WEB01/WEB02.
After:
  gmsa_web$, SPN HTTP/web01, retrieval only by WEB01$, no local admin, app pool-only rights.
Measure:
  - offline crackability
  - password reuse risk
  - hosts allowed to run as identity
  - local privilege
  - delegation settings
Misconception corrected: gMSA solves the secret-management problem, not all authorization problems.
```

```
# Lab 5 — Detect abnormal service-account logon.
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 200 |
  Where-Object {
    $_.Properties[5].Value -match 'gmsa_|svc_' -and
    $_.Properties[8].Value -notin @('5') # service logon type varies by deployment; tune in lab
  }

# Defender exercise:
# - map expected service hosts
# - alert on service identities authenticating from workstations
# - enrich with process and service name from EDR
```

## Practical examples

- **Kerberoasting risk reduction.** `svc_sql` with `Winter2020!` becomes `gmsa_sql$` with managed long random secret. TGS requests may still occur, but offline cracking becomes uneconomical.
- **Bad gMSA rollout.** `PrincipalsAllowedToRetrieveManagedPassword` is set to `Domain Computers`. Any compromised domain-joined host can retrieve the service secret. The account type is modern; the scoping is broken.
- **Delegation edge persists.** A migrated gMSA retains unconstrained delegation from the legacy account. Roasting risk improves, but lateral-movement risk remains.
- **Shared identity collapse.** One gMSA serves web, SQL jobs, and backup scripts. Logs are ambiguous and blast radius is broad. Split identities by service boundary.

## Related notes

- [[kerberoasting]] — the attack gMSA most directly changes economically.
- [[silver-ticket-and-service-account-persistence]] — service-account key compromise becomes service-ticket forgery.
- [[golden-ticket-and-krbtgt-compromise]] — contrast service-account hardening with domain trust-root compromise.
- [[bloodhound-attack-path-analysis]] — model service-account privilege, delegation, and local-admin edges.
- [[false-positives-false-negatives-and-detection-tradeoffs|False Positives, False Negatives, and Detection Tradeoffs]] — service-account alerts need baselines to avoid noisy operations.
- [[telemetry-normalization-correlation-and-enrichment|Telemetry Normalization, Correlation, and Enrichment]] — service identity detection depends on asset and service-owner enrichment.

### Suggested future atomic notes

- spn-inventory-and-ownership
- service-account-blast-radius-modeling
- kerberos-delegation-and-rbcd
- [[tier-zero-administration-and-paw]]
- detect-service-account-misuse

## References

- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview
- **Hardening:** Microsoft Learn — Get started with group Managed Service Accounts — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/getting-started-with-group-managed-service-accounts
- **Foundational:** MITRE ATT&CK T1558.003 — Kerberoasting — https://attack.mitre.org/techniques/T1558/003/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — Active Directory Security Tip #14: Group Managed Service Accounts (GMSAs) — https://adsecurity.org/?p=4904
