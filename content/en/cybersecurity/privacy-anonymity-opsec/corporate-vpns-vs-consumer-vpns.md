---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Corporate VPNs vs Consumer VPNs

## Definition

Corporate VPNs are usually access-control infrastructure for reaching private organizational resources. Consumer VPNs are usually privacy-routing products for changing network-path visibility on the public internet.

The word VPN is the same, but the security objective is different.

## Why it matters

Confusing corporate and consumer VPNs leads to bad expectations. A corporate VPN is often identity-aware, device-managed, monitored, and logged by design. A consumer VPN is marketed as a privacy tool, but its value depends on provider trust, routing behavior, and leakage controls.

Corporate VPNs are usually about "who may access this internal resource?" Consumer VPNs are usually about "who can observe my public internet path?"

## How it works

Use the 4-difference model:

1.
**Security goal**
   Corporate VPN: authenticated access to company resources. Consumer VPN: reduced local-network or ISP visibility and changed apparent source network.

2.
**Identity**
   Corporate VPN: tied to employee identity, device posture, MFA, policy, and monitoring. Consumer VPN: tied to provider account, payment, device, or subscription identity.

3.
**Logging**
   Corporate VPN: logging is expected for security operations, compliance, and incident response. Consumer VPN: logging is a privacy trust issue.

4.
**Traffic scope**
   Corporate VPN: may route private subnets or all traffic through company infrastructure. Consumer VPN: usually routes public internet traffic through provider exits.

Comparison:

```
Corporate VPN:
  purpose: access control
  identity: employee/device
  logging: expected
  owner: employer
  trust question: can this user/device reach this resource?

Consumer VPN:
  purpose: privacy routing
  identity: subscriber/provider account
  logging: privacy-sensitive
  owner: provider
  trust question: who sees my network path now?
```

The bug is not using a corporate VPN. The bug is expecting it to behave like a consumer privacy product.

## Techniques / patterns

- Identify whether the VPN exists for access control or privacy routing.
- Check whether all traffic or only private subnets are routed.
- Read corporate acceptable-use and monitoring notices.
- Treat corporate VPN logs as normal security evidence, not a privacy failure.
- Evaluate consumer VPN logs as provider trust evidence.
- Avoid using employer-managed VPNs or devices for personal privacy workflows.

## Variants and bypasses

Use the 5 deployment patterns:

### 1. Full-tunnel corporate VPN

All traffic routes through company infrastructure. This can support monitoring and protection but means personal browsing may be visible to employer systems.

### 2. Split-tunnel corporate VPN

Only corporate routes use the VPN. This reduces load and preserves local internet paths, but split policy must be clear and tested.

### 3. Identity-aware corporate access

Modern access may combine VPN, device posture, MFA, SSO, EDR, and conditional access. The tunnel is only one control in a broader access system.

### 4. Consumer full-tunnel VPN

Most consumer VPN use routes public internet traffic through provider exits. The provider becomes the new network-path trust point.

### 5. Consumer privacy marketing gap

Consumer VPNs may overpromise anonymity. They do not remove account identity, browser fingerprints, cookies, behavior, or provider trust.

## Impact

- Better expectations for employer monitoring and incident response.
- Reduced misuse of corporate VPNs for personal privacy.
- Clearer evaluation of consumer VPN trust claims.
- Better architecture conversations about replacing broad VPN access with identity-aware controls.
- Fewer false assumptions about what "connected to VPN" proves.

## Detection and defense

Ordered by effectiveness:

1.
**Name the VPN objective**
   Decide whether the VPN is for private-resource access, public-internet privacy, censorship resistance, or network segmentation. The objective determines what "secure" means.

2.
**Document identity and logging**
   Corporate VPNs should state what identity, device, route, and activity data are logged. Consumer VPNs should be evaluated for minimization and trust evidence.

3.
**Prefer least-privilege access for corporate resources**
   Broad network access should be reduced where possible through segmentation, identity-aware proxies, per-app access, and zero-trust patterns.

4.
**Test route scope**
   Full tunnel and split tunnel have different privacy and security consequences. Verify route tables and DNS behavior.

5.
**Separate personal privacy from managed work environments**
   Employer-managed devices and VPNs are usually not appropriate for private personal workflows.

### What does not work as a primary defense

- **Corporate VPN is not personal anonymity.** It often increases employer visibility.
- **Consumer VPN is not corporate access control.** It does not authenticate a user to private company resources by itself.
- **Split tunnel is not automatically safer.** It reduces some exposure and creates other routing ambiguity.
- **Zero trust is not just "no VPN."** It is an architecture of identity, device, policy, telemetry, and least privilege.

## Practical labs

### Classify a VPN deployment

```
VPN name:
Owner:
Purpose:
Users:
Resources reached:
Identity provider:
Device posture required:
MFA required:
Logging expected:
Full or split tunnel:
```

The result should make corporate vs consumer intent obvious.

### Inspect route scope

```
netstat -rn | sed -n '1,120p'
```

Run before and after connection. Look for whether default traffic or only private subnets use the VPN.

### Build a monitoring expectation card

```
Corporate VPN:
Logs user identity:
Logs device:
Logs source IP:
Logs destination/internal resource:
Logs DNS:
Retention:
Notice/policy:
```

This turns monitoring into an explicit policy and engineering fact.

### Compare consumer trust claims

```
Provider:
No-log claim:
Connection logs:
Traffic logs:
Payment metadata:
Audit:
Jurisdiction:
Owner:
Decision:
```

Use this for consumer VPNs, not corporate access infrastructure.

## Practical examples

- An employee uses corporate VPN to reach internal Git, and the company logs identity, device, and access time.
- A company moves from broad VPN access to per-app access with MFA and device posture checks.
- A consumer VPN reduces ISP visibility on home internet but does not hide account login from websites.
- A split-tunnel corporate VPN sends internal apps through the company and public browsing through the local ISP.
- A user tries to use a work laptop plus corporate VPN for personal privacy and misunderstands employer visibility.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-logging-and-trust|VPN Logging and Trust]]
- [[vpn-protocols|VPN Protocols]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[secure-by-design|Secure by Design]]

### Suggested future atomic notes

- zero-trust-network-access
- split-tunneling
- device-posture-checks
- corporate-monitoring-boundaries

## References

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** NIST Zero Trust Architecture SP 800-207 - https://csrc.nist.gov/pubs/sp/800/207/final
- **Foundational:** CISA Zero Trust Maturity Model - https://www.cisa.gov/zero-trust-maturity-model
