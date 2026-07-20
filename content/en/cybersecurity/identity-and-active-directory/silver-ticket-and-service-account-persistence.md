---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Silver Ticket and Service Account Persistence

## Definition

A Silver Ticket is a forged Kerberos **service ticket** (TGS) created with a compromised service account key rather than the domain-wide `krbtgt` key. It is service-scoped Kerberos forgery: if an attacker knows the NTLM hash or AES key for the account behind an SPN, the attacker can forge a ticket for that specific service without first asking the KDC for a legitimate TGS.

## Why it matters

Silver Tickets sit between [[kerberoasting|Kerberoasting]] and [[golden-ticket-and-krbtgt-compromise|Golden Ticket]] compromise. They do not require `krbtgt`, so they are not domain-wide authentication-root compromise. But they also do not require a normal KDC service-ticket request at use time, so they can create durable, quiet, service-scoped persistence where defenders only watch Domain Controller logs.

The core distinction:

- **Golden Ticket:** forged TGT, signed with `krbtgt`, can request service tickets broadly.
- **Silver Ticket:** forged TGS, signed/encrypted with one service account key, useful only for that service/SPN class.

This makes service-account design a security boundary. A weak MSSQL service account password is not merely "a password finding"; if cracked, it may become a forged-ticket persistence path to MSSQL, CIFS, HTTP, LDAP, HOST, or application-tier access depending on SPN ownership and account privilege.

## How it works

Silver Ticket abuse reduces to **5 protocol facts**:

1. **Services have SPNs.** An SPN maps a service instance (`MSSQLSvc/sql01.lab.local:1433`, `HTTP/app.lab.local`, `CIFS/fileserver.lab.local`) to an AD account.
2. **The KDC normally issues a TGS.** A client presents a TGT to the KDC and requests a TGS for a target SPN. The KDC returns a service ticket encrypted with the target service account key.
3. **The service validates the ticket locally.** The service decrypts and validates the ticket with its own long-term key. Depending on service and configuration, the DC may not be contacted for full PAC validation on every request.
4. **A compromised service key can forge that ticket.** If the attacker has the service account NTLM hash or AES key, they can mint a TGS for that service directly.
5. **The forged ticket is scoped to that service.** It does not grant arbitrary domain access unless the service itself has broad privileges or is a pivot point.

Conceptual authorized-lab flow:

```
kerberoastable service account
  -> crack or otherwise recover service key
  -> identify SPN and service class
  -> forge TGS for CIFS/HTTP/MSSQL/LDAP/HOST
  -> inject ticket into lab session
  -> access only the scoped lab service
  -> compare DC logs vs host/service logs
```

The structural bug is not "Kerberos is broken"; it is *service accounts often hold long-lived password-derived keys, and services may accept locally valid Kerberos service tickets even when the KDC did not issue them during the observed session*.

## Techniques / patterns

- **Kerberoasting is the common predecessor.** [[kerberoasting|Kerberoasting]] recovers service account passwords; Silver Ticket abuse uses the resulting NTLM/AES key for service-ticket forgery.
- **SPN selection defines blast radius.** `CIFS` grants file-share access on the target host, `HTTP` grants web application context, `MSSQLSvc` grants database access, `LDAP` can target directory service operations, and `HOST` can map into multiple local service classes depending environment.
- **Service account privilege is the real impact multiplier.** A forged ticket for a low-privilege web app may only read app data. A forged ticket for a service account that is local admin on many servers becomes lateral-movement infrastructure.
- **PAC validation changes detection and failure modes.** Some services validate the Privilege Attribute Certificate with a DC under specific conditions; others rely primarily on local ticket validation. Lack of DC contact is a detection blind spot, not a guarantee of success.
- **AES vs RC4 matters again.** RC4 forged tickets use NTLM hash material and are suspicious in modern domains. AES tickets require AES keys and fit better in AES-only environments, but key compromise still defeats the model.
- **Local admin is not domain compromise.** Silver Ticket to `CIFS/fileserver` can be severe without being equal to `krbtgt` compromise. Precision matters for IR severity and recovery sequencing.
- **Service-side telemetry becomes primary.** If no KDC `4769` exists for the forged service ticket, host logs, application logs, EDR, and service-specific access logs carry the signal.

## Variants and bypasses

Silver Ticket abuse has **5 common target patterns**.

### 1. CIFS file-server access

Forged `CIFS/<host>` tickets target SMB file access and admin shares. Impact depends on the forged identity's local rights and share ACLs. Detection is usually target-host `4624`/`5140` plus SMB activity, not a DC-side TGS request.

### 2. HTTP application access

Forged `HTTP/<host>` tickets target IIS, reverse proxies, or internal web apps using Windows Integrated Authentication. This variant often blends with normal browser/app traffic unless app logs preserve identity, source, and authentication mechanism.

### 3. MSSQL service access

Forged `MSSQLSvc/<host>:<port>` tickets target SQL Server. Impact ranges from read-only DB access to OS command execution if SQL service configuration is weak.

### 4. LDAP / directory-service access

Forged LDAP tickets can be powerful when targeting DC-hosted services and when the identity claims map to directory permissions. More likely to trigger PAC validation or DC-side inconsistencies; environment-specific.

### 5. HOST / machine-service persistence

`HOST`-class tickets can interact with multiple host services and are especially sensitive when machine account keys are compromised. This is where "service-scoped" can still be broad on a single host.

## Impact

Ordered by typical real-world severity:

- **Service-scoped persistence.** The attacker can regain access to a service as long as the service account key remains valid.
- **KDC-log blind spots.** Forged TGS use may produce no corresponding `4769` because no TGS was requested from the KDC.
- **Lateral movement through service access.** CIFS, MSSQL, HTTP, and HOST tickets can provide practical movement even without domain-wide compromise.
- **Application-layer impersonation.** Internal apps that trust Kerberos identity may accept forged identity claims and expose business data or admin functions.
- **Privilege amplification through bad service design.** A service account that is local admin everywhere turns a scoped ticket into a wide operational capability.

## Detection and telemetry

Detection needs to compare **normal TGS flow** against **service-side access**.

1.
**Service access without corresponding `4769`.**
   A target host records `4624` Kerberos logon or service access, but DC telemetry lacks a nearby TGS request for that account/SPN/source. This is the classic Silver Ticket correlation gap.

2.
**Impossible or stale group claims.**
   PAC group memberships seen on the service side do not match current directory membership. Requires enrichment and sometimes service-specific parsing.

3.
**Unexpected service class.**
   A user or host accesses `CIFS`, `MSSQLSvc`, `HTTP`, `LDAP`, or `HOST` services it has never historically used. This is behavioral, not signature-based.

4.
**RC4 service tickets in AES-preferred domains.**
   RC4-HMAC remains a useful suspicion feature, especially for service accounts that should support AES.

5.
**Kerberoasting precursor.**
   A burst or targeted set of `4769` requests against an SPN followed later by service access without KDC TGS requests is a strong sequence. See [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]].

6.
**Endpoint and application logs.**
   EDR process ancestry, SMB share events, IIS logs, SQL audit, and Windows logon events often carry more useful Silver Ticket evidence than DC logs alone.

## Defensive controls

Ordered by effectiveness:

1.
**Use gMSA or equivalent modern service-account design.**
   [[gmsa-and-modern-service-account-hardening|gMSA]] reduces static-password exposure by using long, random, automatically rotated secrets. It does not remove all service-account risk, but it changes the economics dramatically.

2.
**Remove privilege from service accounts.**
   Service accounts should not be Domain Admins, broad local admins, backup operators, or all-purpose application administrators. Silver Ticket blast radius equals service-account blast radius.

3.
**Enforce AES and disable RC4 where possible.**
   Reduces weak-key abuse and makes RC4 tickets a higher-confidence signal. Still rotate the account if any key is compromised.

4.
**Rotate compromised service account keys immediately.**
   A Silver Ticket remains viable while the service key remains valid. Password/key rotation is the direct revocation action.

5.
**Inventory SPNs and ownership.**
   Track every SPN, its owning account, password policy, service owner, hosts using it, and privilege assignments. Unowned SPNs become persistence debt.

6.
**Correlate DC, endpoint, and service logs.**
   Silver Ticket detection fails when the SIEM only ingests Domain Controller events. Host and application telemetry are first-class sources.

### What does not work as a primary defense

- **Only monitoring Domain Controller `4769` events.** Forged service tickets may not request a TGS from the KDC during use.
- **Assuming "not Domain Admin" means low severity.** A service account with local admin on 200 servers is a major compromise even without DA membership.
- **Renaming SPNs or service accounts.** SPN enumeration and service configuration expose the mapping.
- **Disabling Kerberoasting detections after password rotation.** The attack can reappear whenever a static service account password is weak again.
- **Relying on PAC validation as universal protection.** PAC validation behavior is service- and configuration-dependent. Treat it as a control to understand, not a blanket guarantee.
- **Blocking one offensive tool.** Ticket forgery is a protocol capability once key material is known.

## Operational misconceptions

- **"Silver Ticket is just a weaker Golden Ticket."** Partly true by scope, false by detection model. Silver Tickets can be harder to see because they may avoid KDC telemetry at use time.
- **"Kerberoasting ends at cracked password."** False. The recovered key can become service-ticket signing material.
- **"Service account compromise is isolated."** Only if the service account has tight privilege, few SPNs, no broad host rights, and fast rotation.
- **"No 4769 means no Kerberos."** False. It may mean the KDC was bypassed for this forged TGS use.
- **"gMSA eliminates service account risk."** False. It reduces password-cracking economics but does not fix excessive permissions or bad delegation.

## Practical labs

Run only in a private AD lab, intentionally vulnerable range, or authorized assessment.

```
Lab 1 — Model service-ticket scope.
Objective: prove that Silver Ticket impact is bounded by SPN and service-account privilege.
Setup: lab domain, SQL or SMB host, service account with one SPN, low-priv user.
Steps:
  1. Create one SPN-backed lab service account.
  2. Document which hosts and services accept that SPN.
  3. Compare access with a normal TGS vs no access.
Expected telemetry: normal `4769` for legitimate TGS request, target-host `4624` for successful Kerberos logon.
Defender interpretation: the SPN is the trust edge; the service account is the blast-radius unit.
```

```
# Lab 2 — Conceptual authorized-lab Silver Ticket flow.
# Preconditions: owned lab domain, explicit authorization, recovered key for a lab service account.
# Do not run this outside your lab.

# Example: forge a lab CIFS service ticket with Impacket ticketer.
impacket-ticketer -nthash <LAB_SERVICE_NTLM_HASH> \
  -domain-sid S-1-5-21-<LAB-SID> \
  -domain LAB.LOCAL \
  -spn CIFS/fileserver.lab.local \
  labuser

export KRB5CCNAME=labuser.ccache
impacket-smbclient LAB.LOCAL/labuser@fileserver.lab.local -k -no-pass
```

Expected defender view: target-host Kerberos logon and SMB access, but possibly no matching KDC `4769` for that service ticket in the same time window.

```
# Lab 3 — Detection contrast: normal TGS vs forged service-ticket behavior.
# On the lab DC:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4769} -MaxEvents 100 |
  Select-Object TimeCreated, ProviderName, Id

# On the target lab server:
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624} -MaxEvents 100 |
  Where-Object { $_.Properties[8].Value -match 'Kerberos' }

# Analyst exercise:
# - match account + client + service between DC and target host
# - mark target logons that lack a nearby DC TGS event
# - then check whether the source/user has historical access to that SPN
```

```
Lab 4 — Service-account blast-radius table.
Objective: separate "service compromise" from "domain compromise".
Steps:
  1. List SPNs owned by the service account.
  2. List local admin rights and application roles.
  3. List systems where the account can authenticate.
  4. Mark which accesses would remain after a user password reset.
Misconception corrected: service-scoped does not mean low impact; scope has to be measured.
```

## Practical examples

- **Kerberoast-to-MSSQL persistence.** A weak `svc_sql` password is cracked. The attacker forges `MSSQLSvc/sql01` tickets for months until the service account rotates.
- **CIFS access without DC TGS.** A file server records Kerberos SMB logons from an identity, but DC logs show no nearby TGS request. The missing DC event is the clue, not proof of no activity.
- **HTTP application impersonation.** An internal admin portal trusts Windows Integrated Authentication. Forged `HTTP/app` ticket grants access to app admin functions even though the domain is not fully compromised.
- **Overprivileged service account.** `svc_web` is local admin across an entire web tier. A Silver Ticket scoped to HTTP/HOST on those servers becomes lateral movement infrastructure.

## Related notes

- [[kerberoasting]] — the most common way service-account key material is recovered.
- [[golden-ticket-and-krbtgt-compromise]] — compare service-scoped TGS forgery with domain-wide TGT forgery.
- [[as-rep-roasting]] — another offline-cracking path that can yield service or admin credentials.
- [[dcsync-and-ntdsdit-extraction]] — DCSync can recover service keys as well as `krbtgt`.
- [[gmsa-and-modern-service-account-hardening]] — the defensive service-account design pattern that reduces Silver Ticket preconditions.
- [[attack-path-correlation-and-kill-chain-observability|Attack Path Correlation]] — Silver Ticket detection depends on linking precursor roasting to later service access.
- [[telemetry-normalization-correlation-and-enrichment|Telemetry Normalization, Correlation, and Enrichment]] — correlation keys make or break Silver Ticket detection.

### Suggested future atomic notes

- kerberos-pac-validation
- spn-inventory-and-ownership
- service-account-blast-radius-modeling
- detect-golden-ticket-and-silver-ticket
- mssql-kerberos-abuse

## References

- **Foundational:** MITRE ATT&CK T1558.002 — Steal or Forge Kerberos Tickets: Silver Ticket — https://attack.mitre.org/techniques/T1558/002/
- **Research / Deep Dive:** Sean Metcalf (ADSecurity.org) — How Attackers Use Kerberos Silver Tickets to Exploit Systems — https://adsecurity.org/?p=2011
- **Foundational:** Microsoft Learn — Kerberos authentication overview — https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview
- **Hardening:** Microsoft Learn — Group Managed Service Accounts overview — https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview
