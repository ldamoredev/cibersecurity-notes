---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Public Asset Discovery

## Definition

Public asset discovery is the process of identifying internet-facing domains, subdomains, hosts, services, APIs, storage surfaces, documents, and supporting infrastructure that belong to or materially relate to a target.

## Why it matters

Before testing deeply, you need to know what exists. Public asset discovery reveals undocumented, legacy, vendor-hosted, cloud-hosted, or weakly governed exposure. It is the recon workflow that feeds [[external-attack-surface|External Attack Surface]].

This note stays focused on finding assets. [[company-mapping]] proves organizational relationships, while [[tech-stack-fingerprinting]] infers what those assets run.

## How it works

Public asset discovery has **5 asset classes**:

1. **Names.** Domains, subdomains, hostnames, certificates, and DNS records.
2. **Network locations.** IPs, ASNs, cloud ranges, CDN origins, and ports.
3. **Applications.** Websites, APIs, admin panels, staging apps, docs, and portals.
4. **Storage and artifacts.** Buckets, uploads, source maps, backups, logs, and CI outputs.
5. **Third-party surfaces.** SaaS portals, support systems, identity callbacks, widgets, and vendor-hosted content.

The bug is not discovery itself. The value is turning discovered public assets into ownership and exposure decisions.

A worked example, asset discovery to classification:

```
Candidate:
  docs-preview.example.test

Discovery source:
  certificate transparency + search result

Resolution:
  CNAME to vendor-docs.example

HTTP:
  200 with target logo, no login

Classification:
  vendor-hosted documentation surface, likely target-controlled content

Next action:
  scope validation + third-party exposure review, not platform testing
```

Public asset discovery is useful when each asset gets a role, owner hypothesis, and next validation step.

## Techniques / patterns

Practitioners use:

- certificate transparency and DNS enumeration
- search operators and archived URLs
- ASN/IP range mapping where in scope
- cloud-hostname and provider mapping
- JavaScript and source map route extraction
- storage/bucket naming patterns
- SaaS and vendor CNAME identification

## Variants and bypasses

Public assets appear in **6 forms**.

### 1. Primary product assets

Main web apps, APIs, docs, and customer-facing domains.

### 2. Environment assets

Staging, preview, beta, dev, demo, and regional deployments.

### 3. Vendor-hosted assets

Support portals, docs sites, status pages, identity providers, and marketing systems.

### 4. Cloud infrastructure assets

Cloud hostnames, load balancers, object storage, static sites, and serverless endpoints.

### 5. Artifact assets

Source maps, bundles, packages, logs, backups, and exported reports.

### 6. Orphan or legacy assets

Old systems, acquired brands, stale DNS, and forgotten services.

## Impact

Ordered roughly by severity:

- **Hidden entry points.** Unknown assets may lack current controls.
- **Sensitive data exposure.** Storage, docs, source maps, or artifacts leak information.
- **Takeover risk.** Orphaned custom domains and vendor mappings can become claimable.
- **Scope expansion.** Public assets reveal brands, subsidiaries, and vendors.
- **Better test targeting.** Discovery identifies likely high-value manual targets.

## Detection and defense

Ordered by effectiveness:

1.
**Continuously discover public assets from outside the perimeter.**
   Public asset discovery should be part of defensive inventory, not just attacker workflow.

2.
**Tie every asset to owner, environment, and intended exposure.**
   Unowned public assets become remediation priorities.

3.
**Retire stale DNS, storage, and vendor mappings.**
   Old names and integrations are common public-asset drift.

4.
**Review public artifacts before release.**
   Source maps, docs, packages, logs, and reports should not accidentally publish sensitive context.

5.
**Validate ownership before testing.**
   Public does not always mean in-scope or owned by the target.

### What does not work as a primary defense

- **Assuming the main domain is the whole target.** Brands, subsidiaries, vendors, and cloud assets expand surface.
- **Relying on documentation.** Public discovery finds what docs omit.
- **Leaving temporary hosts public.** Temporary assets are often forgotten.
- **Treating vendor-hosted surfaces as someone else's problem.** They can carry your brand, auth, data, and trust.

## Practical labs

Use owned targets.

### Build a public asset list

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u > subdomains.txt
```

Classify each host by owner, environment, and likely role.

### Resolve candidates

```
while read host; do printf "%s " "$host"; dig +short "$host" | tail -n 1; done < subdomains.txt
```

Group by provider, CDN, cloud, and unknown destinations.

### Identify web assets

```
while read host; do curl -m 3 -ks -o /dev/null -w "%{http_code} $host\n" "https://$host"; done < subdomains.txt
```

Move live assets into validation.

### Classify public assets by role

```
asset | source | provider | role | owner confidence | exposure concern | next step
```

Classification is the difference between discovery and usable recon.

### Find static artifact candidates

```
site:example.test filetype:map
site:example.test filetype:zip
site:example.test inurl:backup OR inurl:export
```

Artifact assets often feed endpoint discovery and exposed-storage review.

## Practical examples

- A forgotten static site still serves content.
- A public API host is reachable but absent from formal docs.
- Public assets spread across multiple vendors and providers.
- A cloud load balancer hostname exposes a direct origin.
- A source map reveals hidden API paths.

## Related notes

- [[external-attack-surface|External Attack Surface]]
- [[recon]]
- [[subdomain-enumeration]]
- [[host-and-port-discovery]]
- [[company-mapping]]

### Suggested future atomic notes

- cloud-asset-discovery
- source-map-exposure
- public-document-discovery
- vendor-hosted-assets
- asset-ownership-model

## References

- **Foundational:** OSINT Framework — https://osintframework.com/
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
