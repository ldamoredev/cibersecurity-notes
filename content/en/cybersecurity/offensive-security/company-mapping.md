---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Company Mapping

## Definition

Company mapping is the process of connecting domains, brands, subsidiaries, acquisitions, vendors, public identities, products, and infrastructure clues into a coherent model of what a target actually operates or trusts.

## Why it matters

Many targets do not exist as one neat namespace. Brands, regional domains, acquired companies, support portals, vendor-hosted login flows, cloud projects, and historical naming can make the real surface larger than the official homepage suggests.

This note is about ownership and organizational shape, not raw asset collection or service validation.

## How it works

Company mapping uses **5 relationship types**:

1. **Legal relationship.** Parent company, subsidiary, acquisition, brand, regional entity.
2. **Naming relationship.** Domains, product names, email domains, app names, package names.
3. **Infrastructure relationship.** DNS, certificates, ASNs, cloud accounts, shared hosting, CDNs.
4. **Vendor relationship.** Support, docs, identity, analytics, status, CRM, CI/CD, and SaaS portals.
5. **People relationship.** Employees, roles, job postings, social profiles, support contacts, public maintainers.

The bug is not knowing a company has vendors or brands. The risk is misclassifying ownership and either missing real surface or testing unrelated surface.

A worked example, relationship confidence:

```
Candidate asset:
  support.oldbrand.example

Legal clue:
  oldbrand was acquired by Example Inc. in 2023

Technical clue:
  CNAME points to support SaaS, page uses Example logo

Official clue:
  example.test/help links to support.oldbrand.example

Decision:
  high-confidence related surface; validate scope and vendor boundaries before active tests
```

Company mapping becomes reliable when legal, technical, and official-link evidence agree.

## Techniques / patterns

Practitioners collect:

- official domains, product pages, support docs, and legal pages
- certificate names and DNS relationships
- job postings and technology hints
- public repositories and package metadata
- vendor-hosted custom domains
- social and professional profile clues
- acquisition and brand history

## Variants and bypasses

Company mapping has **6 ambiguity classes**.

### 1. Subsidiary and brand ambiguity

Assets may belong to acquired or regional brands rather than the obvious parent domain.

### 2. Vendor-hosted ambiguity

The target may control content or auth on a vendor-hosted domain without owning the provider.

### 3. Shared infrastructure ambiguity

Cloud, CDN, and shared hosting IPs can host many unrelated tenants.

### 4. Historical ownership ambiguity

Old assets may remain from acquisitions, migrations, or abandoned products.

### 5. Employee and contractor ambiguity

People data helps context but should not be treated as technical scope by itself.

### 6. Open-source/project ambiguity

Public repos and packages may be official, personal, forked, or abandoned.

## Impact

Ordered roughly by severity:

- **Scope mistakes.** Testing wrong assets creates legal and ethical risk.
- **Missed exposure.** Acquired brands and vendor surfaces may carry real trust.
- **Better takeover discovery.** Stale brand/vendor mappings often reveal drift.
- **Improved social/context modeling.** Public people and process data explain likely systems.
- **Inventory improvement.** Defensive teams see how outsiders infer ownership.

## Detection and defense

Ordered by effectiveness:

1.
**Maintain a public-facing ownership map.**
   Brands, domains, vendors, and custom-hosted surfaces should be traceable to owners.

2.
**Publish clear security scope where appropriate.**
   Bug bounty and security contact pages should reduce ambiguity.

3.
**Clean up stale brand and vendor signals.**
   Old domains, support portals, and docs keep implying ownership.

4.
**Avoid oversharing internal structure in public artifacts.**
   Job posts and docs can be useful without leaking unnecessary detail.

5.
**Validate ownership before active testing.**
   Company mapping feeds scope validation; it does not replace it.

### What does not work as a primary defense

- **Assuming name similarity proves ownership.** Look for multiple supporting signals.
- **Assuming shared IP means same target.** Shared platforms host unrelated tenants.
- **Treating vendor surfaces as out of sight.** They can still carry target trust.
- **Ignoring old brands.** Historical assets often persist.

## Practical labs

Use public data and stay within ethical bounds.

### Build a relationship table

```
name | relationship type | evidence | confidence | next validation
```

Require evidence before adding assets to testing scope.

### Search for official domain links

```
site:example.test "privacy" "terms"
site:example.test "support"
site:example.test "status"
```

Legal/support pages often identify vendors and brands.

### Map vendor CNAMEs

```
while read host; do dig CNAME "$host" +short | sed "s|^|$host -> |"; done < subdomains.txt
```

Vendor mappings help identify trust relationships.

### Build an ownership confidence scale

```
asset | legal evidence | official link | DNS/cert evidence | content evidence | confidence
```

Use confidence levels instead of binary ownership when evidence is incomplete.

### Track acquisition drift

```
brand | acquired by | old domains | live hosts | redirects | scope status
```

Acquired brands are a common source of forgotten but real surface.

## Practical examples

- Multiple product domains map back to the same company.
- Support portals and hosted login pages reveal vendor relationships.
- An acquired brand still points to reachable legacy infrastructure.
- Job postings reveal cloud provider and framework choices.
- A public GitHub organization exposes package naming conventions.

## Related notes

- [[public-asset-discovery]]
- [[scope-validation]]
- [[passive-recon]]
- [[third-party-exposure|Third-Party Exposure]]
- [[external-attack-surface|External Attack Surface]]

### Suggested future atomic notes

- [[company-osint]]
- acquisition-surface-mapping
- vendor-relationship-mapping
- employee-osint-boundaries
- brand-domain-inventory

## References

- **Foundational:** OSINT Framework — https://osintframework.com/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
