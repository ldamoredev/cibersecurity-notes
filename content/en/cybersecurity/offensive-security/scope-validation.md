---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Scope Validation

## Definition

Scope validation is the process of confirming which discovered assets are owned by the target, authorized for testing, and appropriate for further analysis.

## Why it matters

Recon produces ambiguity. Without scope validation, it is easy to waste time, test the wrong target, or confuse vendor-managed infrastructure with the organization's owned surface.

This note stays narrow: it is about ownership and allowed testing boundaries, not broad discovery or technical service validation.

## How it works

Scope validation asks **5 evidence questions**:

1. **Ownership.** What evidence links the asset to the target?
2. **Authorization.** Is it in the written scope, contract, or internal approval?
3. **Environment.** Production, staging, vendor, shared platform, or unknown?
4. **Control.** Does the target control content, auth, DNS, or infrastructure?
5. **Limits.** What tests, rates, accounts, data, or techniques are prohibited?

The bug is not uncertainty. The operational mistake is proceeding with active testing before uncertainty is resolved.

A worked example, ambiguous asset:

```
Asset:
  login-example.vendorcloud.com

Evidence:
  linked from example.test SSO docs; certificate is vendor-owned; page displays Example tenant name

Scope:
  program allows *.example.test but excludes third-party platform testing

Decision:
  test target-owned tenant configuration only if explicitly allowed;
  do not test vendor platform vulnerabilities
```

Scope validation is a safety control, not paperwork.

## Techniques / patterns

Practitioners validate using:

- scope documents and bug bounty rules
- DNS, certificates, redirects, and content ownership
- official links from trusted target domains
- vendor/platform clues
- legal/entity and brand mapping
- contact with program owners when ambiguous

## Variants and bypasses

Scope ambiguity appears in **6 forms**.

### 1. Vendor-hosted asset

The target uses a third-party platform but does not own the provider infrastructure.

### 2. Shared infrastructure

Cloud, CDN, or hosting IPs serve multiple tenants.

### 3. Acquired or legacy brand

Historical assets may or may not be authorized for testing.

### 4. Customer or tenant subdomain

Names look related but may belong to customers or users.

### 5. Public but excluded surface

The asset is owned but explicitly excluded from testing.

### 6. Unknown control boundary

DNS, content, and identity clues conflict or are incomplete.

## Impact

Ordered roughly by severity:

- **Legal/ethical risk.** Testing off-scope systems can harm third parties.
- **Wasted effort.** Wrong-target testing produces unusable findings.
- **Missed real risk.** Overly conservative classification can hide owned exposure.
- **Better reporting.** Validated scope creates stronger evidence and remediation paths.

## Detection and defense

Ordered by effectiveness:

1.
**Validate scope before active or intrusive tests.**
   Passive collection can generate leads, but active testing needs authorization clarity.

2.
**Preserve evidence for ownership decisions.**
   Reports should show why an asset is considered in scope.

3.
**Use confidence levels.**
   Unknown assets should be marked unknown, not forced into in/out prematurely.

4.
**Escalate ambiguity to the program owner.**
   A short clarification beats risky assumptions.

5.
**For defenders, publish clearer scope and security contacts.**
   Clear public scope reduces accidental wrong-target testing.

### What does not work as a primary defense

- **Name similarity alone.** Similar domains are not proof of ownership.
- **Shared IP ownership.** Cloud and CDN IPs are not target assets by default.
- **Assuming all vendor-hosted pages are testable.** Scope may include content but not platform attacks.
- **Proceeding because a target is public.** Public reachability is not permission.

## Practical labs

Use authorized programs or internal assets.

### Build a scope evidence table

```
asset | evidence | owner confidence | scope status | allowed tests | notes
```

Do not advance unknown assets into active testing without approval.

### Check official linking

```
Does a trusted target page link to this host?
Does DNS point from a target-owned zone?
Does the certificate include target-controlled names?
```

Multiple signals raise confidence.

### Separate provider from tenant

```
dig CNAME app.example.test +short
```

Provider infrastructure may be out of scope even when the custom domain is in scope.

### Write an ambiguity question for the owner

```
Asset:
Evidence:
Ambiguity:
Proposed test:
Potential third-party impact:
Decision needed:
```

Asking well is faster than guessing badly.

### Mark confidence before testing

```
in-scope confirmed | likely in scope | unknown | likely out of scope | excluded
```

Only confirmed or explicitly approved assets should advance to intrusive testing.

## Practical examples

- A subdomain belongs to a third-party SaaS instance rather than the target infrastructure.
- A public IP resolves to a shared platform and needs ownership confirmation.
- An acquired brand's domain is live but not part of current testing scope.
- A customer tenant name resembles the target but is excluded.
- A support portal is in scope only for tenant configuration, not vendor platform testing.

## Related notes

- [[company-mapping]]
- [[public-asset-discovery]]
- [[third-party-exposure|Third-Party Exposure]]
- [[external-attack-surface|External Attack Surface]]
- [[recon-to-testing-handoff]]

### Suggested future atomic notes

- bug-bounty-scope-reading
- vendor-scope-boundaries
- shared-infrastructure-scope
- scope-evidence-quality
- safe-harbor-basics

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** HackerOne Disclosure Guidelines — https://www.hackerone.com/disclosure-guidelines
