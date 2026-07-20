---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Identity Attack Paths Across IdPs

## Definition

Cross-IdP attack paths are lateral-movement chains that propagate compromise *across platform boundaries* by traversing the trust edges — **federation, directory synchronization, and SSO** — that tie on-prem Active Directory, cloud identity providers (Entra ID, Okta), and downstream SaaS (GitHub Enterprise, Google Workspace) together. The unit of analysis moves from a single directory to the **nested dependency chain**, because each downstream platform's security is bounded by its weakest *upstream* identity source. Per Jared Atkinson's framing (the single source this note rests on), the attack path does not stop at the identity provider — the IdP is a hop, not a wall.

## Why it matters

On-prem AD attack-path analysis is mature; the SaaS plane it now feeds is not. Three transferable lessons:

- **Identity is nested, not flat.** Okta and Entra do not *create* identity — they *translate* identity sourced from somewhere else (commonly on-prem AD via sync, or an HRIS like Workday). The real root of trust is whatever feeds the IdP, so "we secured Okta" misses that AD is effectively Tier 0 for the entire SaaS estate.
- **The trust edge is the new lateral-movement primitive.** Just as pass-the-hash reuses on-prem credentials, cross-IdP paths reuse *trust*: a federation assertion, a sync propagation, or an SSO token carries compromise from one platform to the next. The edge — not the host — is the unit of movement in the SaaS era.
- **The gaps between platforms are the attack surface.** Modern lateral movement is increasingly cross-platform — AD → Entra/Okta → GitHub Enterprise → source code / CI-CD — and each hop runs over a different protocol with different controls. The seam between two well-secured platforms is where the unmodeled path lives.

> **Source-confidence caveat (carried from the literature note).** This note derives from a single, conceptual source by a vendor (SpecterOps) executive. Its central prevalence claim — that these paths are *increasingly the primary* route in real compromises — is asserted, not yet demonstrated with incident data. Treat the *shape* of the problem as well-argued and the *frequency* as open. The source is also defender-blind; the detection guidance below is synthesized, not drawn from it.

## How it works

A SaaS app trusts an IdP; the IdP trusts an upstream source; compromise propagates downward along whichever edges it can reach:

```
on-prem AD / HRIS   ──sync──▶   Entra ID / Okta   ──SSO + federation──▶   SaaS (GitHub, Workspace)
 (root of trust)                  (translator)                              (downstream; bounded by upstream)
```

The propagation runs over **3 trust-edge types**, each with distinct reachability:

1. **Federation (SAML / WS-Fed).** The IdP asserts identity to a service provider via *signed* assertions. Compromise the token-signing key or the federation configuration and you can forge an assertion for *any* downstream user (the Golden SAML pattern).
2. **Directory synchronization (SCIM / Entra Connect / Okta AD agent).** User and group objects, and their membership, flow from AD into the IdP. Control the sync source — or a privileged sync account — and you inject or modify downstream identities. Sync rules that propagate a load-bearing group like **Domain Users** can create SaaS privilege the AD admins never realize they granted.
3. **SSO (OIDC / OAuth).** The IdP issues tokens to apps. Token theft or replay, OAuth app-consent abuse, and long-lived refresh tokens ride this edge into the application.

The canonical chain (the source's worked example): a compromised on-prem AD account propagates via sync/federation into Okta/Entra, which fans out via SSO to GitHub Enterprise, reaching source code and CI/CD. The security of GitHub is bounded by the security of whatever feeds the IdP — usually on-prem AD.

The bug is not any single platform; it is that the *trust edges between them* are unmodeled, so a compromise high in the chain reaches everything downstream of it.

## Techniques / patterns

- **Map the trust topology first.** Enumerate what feeds the IdP (Entra Connect, Okta AD agent, HRIS), which apps the IdP fans out to, and which sync rules propagate group membership. The graph *is* the attack surface.
- **Find the real Tier 0.** Any account that can write to the sync source or alter the federation configuration is effectively Tier 0 across the whole SaaS estate — even if it looks like a low-tier service account on-prem.
- **Federation-trust abuse (Golden SAML).** Steal the token-signing certificate (e.g., from ADFS) to forge SAML assertions for arbitrary downstream identities — independent of passwords or MFA at the SP.
- **Sync-account abuse.** The AD↔Entra sync account is highly privileged and a known hybrid pivot; compromising it manipulates downstream identity directly.
- **SSO token and consent abuse.** OAuth app-consent grants, refresh-token longevity, and conditional-access gaps extend access into apps without re-authenticating.
- **Cross-IdP enumeration tooling.** BloodHound CE (Azure/Entra), AzureHound, and ROADtools build the cloud-identity graph; cross-*platform* graphing at scale is currently weighted toward commercial BloodHound Enterprise OpenGraph, with only partial FOSS analogs (an honest gap, per the source).

## Variants and bypasses

The **3 trust edges** are the variant axes; each is a distinct attack-path family.

### 1. Federation edge (SAML / WS-Fed)

Golden SAML, federation-config manipulation, and token-signing-certificate theft let an attacker forge assertions for any downstream service provider. Survives password resets and SP-side MFA because the trust is in the signing key, not the user credential.

### 2. Directory-synchronization edge (SCIM / Entra Connect / Okta AD agent)

Sync-account compromise, sync-rule abuse, and over-broad group propagation (the Domain Users case) inject or modify downstream identities and membership. The on-prem object becomes the SaaS principal.

### 3. SSO edge (OIDC / OAuth)

Token theft/replay, OAuth app-consent phishing, and refresh-token abuse ride the issued-token edge into applications. Conditional Access *reshapes* this path (forcing the attacker to also satisfy device/risk signals) rather than eliminating it.

## Impact

Ordered by severity:

- **Cross-platform lateral movement.** A single on-prem foothold reaches the full SaaS estate via the trust edges — the broadest blast-radius outcome.
- **Source code and CI/CD compromise.** Reaching GitHub Enterprise (or equivalent) yields source code and pipeline access — a supply-chain foothold.
- **Privilege escalation via unrecognized Tier 0.** The sync source or federation config is effectively Tier 0; abusing it grants SaaS-wide privilege from a low-looking on-prem position.
- **Durable persistence.** Federation abuse (Golden SAML) persists across credential resets because it forges trust rather than stealing a password.

## Detection and defense

The source provides no detection content; the following is synthesized and should be validated against a real hybrid environment. Ordered by effectiveness:

1.
**Map and minimize the trust topology; extend Tier 0 to the sync source and federation config.**
   Treat any account or system that can write the sync source or alter federation as Tier 0, and apply [[tier-zero-administration-and-paw|PAW/Tier-0 discipline]] to it. Most cross-IdP risk reduces to "an unrecognized Tier 0 was reachable."

2.
**Scope synchronization tightly.**
   Do not propagate Domain Users or broad groups downstream; filter sync scope to exactly the objects each SaaS platform needs. Over-propagation is the load-bearing misconfiguration in the worked example.

3.
**Protect federation signing keys.**
   Store token-signing certificates in an HSM, rotate them, and monitor for export — the structural defense against Golden SAML.

4.
**Harden the SSO edge.**
   Short token lifetimes, Conditional Access with device + risk gating, and OAuth app-consent governance shrink the SSO attack path (and reshape it so a single stolen token is insufficient).

5.
**Build cross-IdP detection (the current literature gap).**
   Monitor and correlate IdP/SaaS audit logs — Okta System Log, Entra sign-in/audit, GitHub audit — for SCIM-sync anomalies, federation-config changes, token reuse, and impossible-travel *across platforms*. This is the SaaS-plane extension of on-prem BloodHound detection and is currently underspecified — an open research direction, not a solved playbook.

### What does not work as a primary defense

- **Securing each platform in isolation.** "We hardened Okta" misses that AD (via sync) is the real root of trust. The source's central point: the unit of analysis must be the chain, not the platform.
- **Treating the IdP as the trust boundary.** The IdP is a hop. Its downstream security is bounded by its upstream source.
- **Assuming Conditional Access closes the path.** CA *reshapes* the path into "compromise the credential *and* the device-trust signal"; it raises cost but does not eliminate the trust edge.

## Practical labs

Honest constraint: unlike a single-binary or single-web-app topic, cross-IdP attack paths need an *owned hybrid environment* (AD + Entra/Okta + a SaaS app) to exercise end-to-end. The labs below are read-only topology/enumeration exercises against a tenant you own or are authorized to assess.

### Enumerate the cloud-identity graph (owned tenant)

```
# AzureHound collects Entra ID identities, roles, and app relationships into a
# BloodHound-CE-importable graph. Authorized tenant only.
azurehound -u "<user>" -p "<pass>" --tenant "<tenant-id>" list --output azure.json
# Then import azure.json into BloodHound CE and look for paths from low-tier
# principals to privileged app/role nodes.
```

### Inventory the trust edges feeding your IdP

```
For an owned tenant, document:
  - Sync:        Entra Connect / Okta AD agent — which OUs/groups are in scope?
  - Federation:  which domains are federated; where do the signing certs live?
  - SSO apps:    which SaaS apps trust the IdP; which use SCIM provisioning?
The accounts that can write any of these are your cross-IdP Tier 0.
```

### Review group-propagation scope

```
Check whether Domain Users (or other broad groups) propagate downstream via sync
rules into any SaaS role assignment. The worked-example attack path depends on
exactly this over-propagation; mature tenants filter it.
```

### Inspect federation/sync audit signals

```
In Entra audit logs / Okta System Log, locate the event types for:
  - federation configuration changes, signing-cert updates
  - new SCIM provisioning / sync-rule changes
  - OAuth app-consent grants
These are the raw material for the cross-IdP detection the literature still lacks.
```

## Practical examples

- **AD → Okta → GitHub Enterprise → source code.** The source's worked chain: an on-prem account propagates through sync/federation to the IdP, then SSO into GitHub, reaching code and CI/CD. (The Domain-Users-to-GitHub specifics depend on the org having propagated Domain Users through sync scope — mature orgs filter this.)
- **Golden SAML.** A stolen ADFS token-signing certificate is used to forge SAML assertions for arbitrary users, granting cloud-SaaS access independent of passwords or SP-side MFA — the federation-edge technique demonstrated at scale in the SolarWinds/SUNBURST intrusions.
- **Entra Connect sync-account abuse.** Compromise of the hybrid sync account manipulates downstream identity and membership directly, escalating from on-prem to cloud.
- **OAuth app-consent phishing.** A user is tricked into consenting to a malicious OAuth app, granting the attacker persistent token-based SaaS access that survives password resets — the SSO-edge variant.

## Related notes

- [[bloodhound-attack-path-analysis]] — the on-prem attack-path-graph parent this concept extends across IdP boundaries.
- [[pass-the-hash-and-ntlm-credential-reuse]] — the on-prem credential-reuse analog; cross-IdP paths are the SaaS-era equivalent (trust/token reuse).
- [[golden-ticket-and-krbtgt-compromise]] — Golden Ticket is to Kerberos what Golden SAML is to federation: forge the trust artifact rather than steal a credential.
- [[tier-zero-administration-and-paw]] — the Tier 0 discipline that must extend to the sync source and federation config.
- [[dcsync-and-ntdsdit-extraction]] — the on-prem credential endgame that often seeds the upstream compromise feeding the chain.
- [[index|Cloud Security]] — cross-IdP paths span identity and cloud; the cloud branch is the downstream half.
- [[detect-bloodhound-collection|Detect BloodHound Collection]] — the on-prem detection pair; the SaaS-plane detection equivalent is the open gap noted above.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — offense (trust-edge traversal) vs defense (trust-topology minimization).

### Suggested future atomic notes

- golden-saml-and-federation-abuse
- entra-connect-and-hybrid-identity-attacks
- oauth-token-and-consent-abuse
- detect-cross-idp-attack-paths
- saas-identity-tier-zero

> Future atomic notes are listed as `<span class="unresolved-link" title="Unpublished or unresolved: wikilinks">wikilinks</span>` even when the target file does not exist yet, so they register as forward-links in Obsidian.

## References

- **Research / Deep Dive:** Jared Atkinson (SpecterOps) — Attack Paths Don't Stop at Identity Providers — https://specterops.io/blog/2026/03/24/attack-paths-dont-stop-at-identity-providers/
- **Official Tool Docs:** BloodHound Community Edition documentation (SpecterOps; models Entra/Azure attack paths) — https://bloodhound.specterops.io/
- **Foundational:** MITRE ATT&CK T1199 — Trusted Relationship — https://attack.mitre.org/techniques/T1199/
- **Foundational:** MITRE ATT&CK T1556 — Modify Authentication Process — https://attack.mitre.org/techniques/T1556/
