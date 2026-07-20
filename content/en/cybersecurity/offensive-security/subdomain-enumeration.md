---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Subdomain Enumeration

## Definition

Subdomain enumeration is the process of discovering subdomains associated with a target and determining which are live, owned, interesting, risky, or stale.

## Why it matters

Subdomains reveal alternate entry points, staging hosts, old environments, admin surfaces, vendor mappings, customer tenants, and ownership drift. They are one of the richest bridges between OSINT and concrete attack surface.

This note is narrower than [[public-asset-discovery]] and earlier than full validation: its job is to expand the hostname surface before routing findings into reachability and ownership checks.

## How it works

Subdomain enumeration uses **5 discovery sources**:

1. **Certificate transparency.** Names issued in public certificates.
2. **DNS data.** Zone clues, brute force, permutations, CNAMEs, MX/TXT, and wildcard behavior.
3. **Search and archives.** Indexed pages, historical URLs, docs, and old links.
4. **Client artifacts.** JavaScript, source maps, mobile apps, and SDKs.
5. **Provider and vendor clues.** SaaS mappings, cloud hostnames, status/support/docs domains.

The bug is not having many subdomains. The risk is subdomains that are live, stale, claimable, privileged, or outside governance.

A worked example, names to classes:

```
Raw names:
  app.example.test
  staging-api.example.test
  help.example.test
  random-123.example.test

Checks:
  app -> 200 product app
  staging-api -> 401 API, target certificate
  help -> CNAME to support SaaS
  random-123 -> wildcard DNS baseline

Classes:
  product host, environment host, vendor-mapped host, noise

Next actions:
  validate staging scope, review vendor mapping, remove wildcard noise from list
```

The quality step is classification, not raw subdomain volume.

## Techniques / patterns

Practitioners look for:

- `dev`, `staging`, `test`, `qa`, `admin`, `api`, `internal`, `vpn`, `support`, `docs`, `status`
- wildcard DNS that creates noisy false positives
- CNAMEs to third-party providers
- names from certificates and archives
- environment naming conventions
- regional/customer/tenant patterns

## Variants and bypasses

Subdomain enumeration has **6 result classes**.

### 1. Live product host

An expected public app, API, or docs host.

### 2. Environment host

Staging, beta, preview, dev, QA, demo, or temporary deployment.

### 3. Admin/control host

Management, support, monitoring, CI/CD, or privileged interfaces.

### 4. Vendor-mapped host

CNAME or custom domain points to SaaS/cloud provider.

### 5. Stale or dangling host

DNS resolves or aliases to a target that no longer exists or can be claimed.

### 6. Noise or unrelated host

Wildcard, parked, shared, or misattributed records.

## Impact

Ordered roughly by severity:

- **Subdomain takeover.** Stale provider mappings can become claimable.
- **Admin or staging exposure.** Sensitive interfaces appear outside main product paths.
- **Hidden API discovery.** API and mobile hosts reveal alternate routes.
- **Scope expansion.** Brands and vendors become visible.
- **Inventory improvement.** Defenders discover forgotten names.

## Detection and defense

Ordered by effectiveness:

1.
**Continuously enumerate your own subdomains.**
   Treat names as lifecycle-managed assets.

2.
**Validate owner and environment for every live name.**
   Live unknown names deserve triage.

3.
**Remove stale DNS promptly.**
   DNS cleanup should be part of decommissioning.

4.
**Monitor high-risk naming patterns.**
   Admin, staging, support, and vendor names should be reviewed quickly.

5.
**Control wildcard DNS and tenant naming.**
   Wildcards create noisy inventory and can mask stale resources.

### What does not work as a primary defense

- **Assuming unlinked subdomains are hidden.** Certificates, DNS, archives, and wordlists reveal them.
- **Deleting the app but leaving DNS.** Stale names remain trust anchors.
- **Ignoring wildcard noise.** Noise can hide real exposure.
- **Treating every discovered name as in-scope without validation.** Ownership still matters.

## Practical labs

Use owned domains.

### Certificate transparency collection

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u
```

Deduplicate and normalize wildcard entries.

### Resolve and classify

```
while read host; do printf "%s " "$host"; dig +short "$host" | tail -n 1; done < subdomains.txt
```

Classify by provider, environment, and owner.

### Detect wildcard behavior

```
dig +short "random-$(date +%s).example.test"
```

Wildcard DNS changes how enumeration results should be interpreted.

### Build a subdomain classification table

```
host | source | resolves | http status | cname/provider | class | next action
```

Use the six result classes from this note to drive triage.

### Check provider-mapped hosts for drift

```
while read host; do
  cname=$(dig CNAME "$host" +short)
  printf "%s -> %s\n" "$host" "$cname"
done < subdomains.txt
```

Provider CNAMEs often feed third-party exposure or takeover review.

## Practical examples

- Enumeration reveals `staging`, `legacy-api`, and `admin` hosts.
- A subdomain points to a decommissioned service.
- Alternate customer-specific hosts expose more surface than the main domain.
- A vendor CNAME points to a support platform.
- Certificate logs reveal a temporary preview environment.

## Related notes

- [[dns-resolution|DNS Resolution]]
- [[dns-security|DNS Security]]
- [[subdomain-takeover|Subdomain Takeover]]
- [[public-asset-discovery]]
- [[scope-validation]]

### Suggested future atomic notes

- subdomain-permutation
- wildcard-dns-enumeration
- certificate-transparency-monitoring
- tenant-subdomain-patterns
- subdomain-takeover-triage

## References

- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 102 — https://projectdiscovery.io/blog/recon-series-2
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
