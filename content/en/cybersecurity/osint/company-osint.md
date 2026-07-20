---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Company OSINT

## Definition

Company OSINT is the use of public sources to understand an organization's brands, domains, products, subsidiaries, vendors, technologies, public people context, and exposed digital footprint. It is the OSINT mode that produces a **defensible ownership and surface map** — the artifact that downstream [[scope-validation|scope validation]] and [[external-attack-surface|external attack surface]] depend on.

## Why it matters

Companies rarely expose themselves through a single domain. Public pages, support portals, job posts, status pages, docs, vendor CNAMEs, social accounts, certificates, and acquisition history all describe the real organization. Treating "the main marketing site" as the scope is the most common reason scopes miss real exposure.

Company OSINT is the defensive equivalent of attacker reconnaissance. The same map an attacker assembles from public sources is the map a defender needs to know what implies trust to users, partners, and search engines. Without it, scope is guesswork and "third-party trust" is invisible.

The deliverable is a scoped, evidence-backed map that downstream branches can act on:
- **Scope validation** receives an ownership-confidence list before any active testing.
- **External attack surface** receives a domain/vendor inventory tied to ownership evidence.
- **Third-party exposure** receives the vendor relationship list with evidence quality grades.

## How it works

Company OSINT pulls from **6 clue families**. A useful map crosses at least three of them per asset.

1. **Brand and product clues.** Public product names, app store listings, customer-facing domains, public docs, status pages, terms-of-service pages.
2. **Legal and ownership clues.** Subsidiaries, acquisitions, corporate filings, regulatory disclosures, terms-of-service legal-entity fields, certificate "O=" organization fields.
3. **Technical clues.** Stack, cloud provider, APIs, SDKs, package names, certificate transparency entries, ASN/BGP records.
4. **Vendor clues.** Support, identity, analytics, status, CDN, SaaS providers — most visible via CNAME records on subdomains and via referenced third-party scripts.
5. **People clues.** Roles, teams, hiring, public maintainers, security contacts. Used for organizational context only, with [[social-media-osint|minimization rules]] applied.
6. **Historical clues.** Archived pages, legacy products, old brands, stale support docs, expired-but-published certificates.

The bug is **not that public company context exists**. The OSINT skill is **connecting clues without overclaiming ownership** — a vendor-hosted page is not target infrastructure; an acquired-brand domain may or may not still belong to the parent; a cert SAN does not prove deployment.

A worked example:

```
Question:    Map Example Corp's external surface for scope validation.
Brand clue:  example.com main site, example.app product, exampledev.com developer portal.
Legal clue:  TOS lists "Example Corp Inc." as legal entity; subsidiary "ExSubsidiary Ltd." in filings.
Technical:  certificate transparency returns 47 names under example.com + 12 under exampledev.com.
Vendor:     CNAME chain on support.example.com → zendesk; status.example.com → statuspage.io.
People:     LinkedIn shows ExSubsidiary employees with "Example Corp" group affiliation (corroboration).
Historical: archive.org reveals legacy-brand.example.io still resolves to a live page.
Output:     ownership map with 3 verified primary domains, 4 vendor-hosted (third-party trust), 1 legacy.
```

Each entry in the map carries evidence and a confidence label, not a single-source assertion.

## Techniques / patterns

The discipline is "verify ownership across at least three clue families before promoting to verified."

- **Official websites, terms, privacy, status, support pages** — anchor for legal entity and primary brand.
- **Certificate transparency (`crt.sh`) and DNS records** — primary technical inventory source.
- **Job postings and engineering blogs** — disclose stack, cloud, and team structure.
- **Public repositories and package registries** — reveal naming conventions and maintainer identities.
- **Vendor-hosted custom domains** — CNAMEs to `*.zendesk.com`, `*.statuspage.io`, `*.cloudfront.net`, `*.elasticbeanstalk.com` indicate third-party trust.
- **Social accounts and product announcements** — anchor for current brand and vendor relationships.
- **Acquisition/brand history and archived pages** — surface legacy assets that still carry trust.

## Variants and bypasses

Company OSINT clusters into **5 ambiguity classes**. Most map errors are one of these.

### 1. Brand ambiguity

Product and brand names may not match legal entities. "Example" the brand, "Example Corp Inc." the company, and "ExSubsidiary Ltd." the legal owner of half the infrastructure can all be the same organization — or not. Resolve via terms-of-service legal-entity fields, certificate "O=" fields, and corporate filings.

### 2. Vendor ambiguity

Vendor-hosted surfaces (`support.example.com` → Zendesk) carry target trust without being target-owned infrastructure. Test against the vendor host, not the target. Evidence: CNAME chain, response headers, vendor-specific TLS cert SANs.

### 3. Acquisition drift

Old assets and domains often remain after ownership changes — sometimes for years. The current owner may not know they exist. Evidence: archive.org snapshots, legal-entity history, certificate timeline. Acquisition drift is a frequent source of "wait, that's still ours?" exposure.

### 4. Shared-platform ambiguity

CDN, cloud, and SaaS platforms host many tenants. A `*.cloudfront.net` IP serves thousands of customers; an Elasticsearch endpoint on a shared cluster does not "belong" to one tenant. Resolve via Host-header behavior, vendor-tenant identifiers, or out-of-band ownership confirmation.

### 5. People-context ambiguity

Public profiles may be stale, personal, or unrelated to current scope. A LinkedIn profile listing "Example Corp" as employer may be 5 years out of date. Use only with corroboration; never use as primary scope evidence.

## Impact

Ordered roughly by severity:

- **Scope clarification.** Ownership evidence guides safe testing in pentests and bug bounty work; the alternative is off-scope mistakes.
- **Public asset discovery.** Brands, vendors, and acquisitions reveal domains and services not in any internal inventory.
- **Third-party exposure mapping.** SaaS and identity providers become visible as part of the trust surface.
- **Technology targeting.** Job posts, engineering blogs, and public repositories reveal stack choices that drive prioritization.
- **Stale asset discovery.** Legacy brands and archived pages reveal forgotten systems that carry current trust.

## Detection and defense

Defenses cluster around **maintaining the company's own external map** with confidence labels.

1.
**Maintain an external-facing company map.**
   Defenders should know which brands, vendors, and domains imply trust. The map should match what an attacker would build, kept up to date.

2.
**Publish clear security scope and contacts.**
   `security.txt`, a security page, and a stated bug-bounty/disclosure scope reduce ambiguity for researchers and internal teams. See [[email-and-phone-osint]].

3.
**Clean up stale public signals.**
   Old docs, deprecated support pages, expired-product domains, and archived staging environments keep expanding perceived surface long after the team that built them moves on.

4.
**Review job posts and docs for unnecessary technical detail.**
   Public hiring can be useful without oversharing sensitive architecture. "We use Kubernetes" is fine; "our auth uses module X version Y on cluster Z" is not.

5.
**Use confidence levels for ownership.**
   Do not treat one clue as proof. The map should have verified / likely / uncertain / vendor-hosted columns with evidence per row.

### What does not work as a primary defense

- **Assuming the main website is the company.** Brands, vendors, and acquisitions expand context far beyond it.
- **Assuming shared infrastructure proves ownership.** Shared platforms (CDN, cloud, SaaS) host many tenants; "served from cloudfront.net" is not ownership evidence.
- **Ignoring old acquisitions.** Legacy assets often persist long after acquisitions complete; they carry current trust until decommissioned.
- **Treating people profiles as technical scope.** Roles are organizational context, never authorization to test systems.
- **Trusting WHOIS organization fields alone.** Privacy services and stale registrations make WHOIS unreliable as a single ownership source.

## Practical labs

Use a public company you own, an authorized scope, or a benign training target.

### Build a company map

```
brand          | domain               | evidence                         | owner confidence | related assets        | notes
example.com    | example.com          | TOS legal-entity + cert O=       | verified         | 47 cert SAN names     | primary
exampledev.com | exampledev.com       | TOS reference + cert chain       | verified         | 12 cert SAN names     | dev portal
support        | support.example.com  | CNAME → zendesk                  | vendor-hosted    | n/a                   | third-party trust
status         | status.example.com   | CNAME → statuspage.io            | vendor-hosted    | n/a                   | third-party trust
legacy-brand   | legacy-brand.example.io | archive.org 2018-2024, cur DNS A | likely           | 3 cert SAN names      | acquisition drift
```

The map is the deliverable. Confidence labels are load-bearing.

### Extract vendor relationships from CNAMEs

```
while read host; do
  cname=$(dig CNAME "$host" +short)
  [ -n "$cname" ] && echo "$host -> $cname"
done < subdomains.txt | tee vendor-cnames.txt

# Then summarize vendors
awk '{print $3}' vendor-cnames.txt | sed 's/\.$//; s/.*\.//' | sort | uniq -c | sort -rn
```

Vendor mappings feed [[third-party-exposure|third-party exposure]] review.

### Cross-corroborate ownership

```
Source 1: certificate "O=" field         → "Example Corp, Inc."
Source 2: terms-of-service legal entity  → "Example Corp, Inc."
Source 3: archive.org earliest snapshot  → 2014, branding consistent with current
Source 4: WHOIS organization (if visible)→ "Example Corp"
Decision: verified ownership; promote to map.
```

Three independent sources promote ownership from "likely" to "verified."

### Review public technology clues without overclaiming

```
source                      | technology clue                | confidence | security relevance        | next action
job post 2026-03            | "experience with Spring Boot"  | medium     | suggests Java/Spring stack | corroborate via headers
engineering blog 2025-11    | "we run on Kubernetes / GCP"   | high       | cloud + orchestration     | scope GCP-specific reviews
public commit 2026-04       | maintainer email pattern       | high       | email pattern + identity  | feed email pattern map
acquired-brand status page  | vendor list (Datadog, Auth0)   | high       | vendor inventory          | feed third-party map
```

Single-source clues do not become "verified" without corroboration.

### Audit acquisition drift

```
acquisition  | acquired entity      | acquisition date | known assets | unknown-but-found assets
2019         | LegacyBrand Inc.     | 2019-Q3          | 2 domains    | 3 additional domains via cert search
2022         | TinyTool Ltd.        | 2022-Q1          | 1 SaaS app   | 1 staging domain still resolving
```

Acquisition drift is the most common "we didn't know we still owned this" finding.

## Practical examples

- A status page reveals service names, regions, and dependent vendors that no public spec discloses.
- Job posts reveal cloud and framework choices that narrow active testing scope.
- Vendor CNAMEs identify support and identity providers, exposing third-party trust relationships.
- An acquired brand still has live infrastructure that the parent organization had forgotten about.
- Public repositories reveal package naming conventions that match internal naming visible elsewhere.
- Certificate transparency reveals an unannounced staging subdomain pattern, surfacing pre-launch surface.

## Related notes

- [[osint]]
- [[osint-triage]]
- [[social-media-osint]]
- [[email-and-phone-osint]]
- [[company-mapping|Company Mapping]]
- [[scope-validation|Scope Validation]]
- [[third-party-exposure|Third-Party Exposure]]

### Suggested future atomic notes

- brand-domain-inventory
- job-posting-osint
- vendor-relationship-mapping
- acquisition-surface-mapping
- public-repository-osint
- ownership-confidence-grading

## References

- **Foundational:** OSINT Framework — https://osintframework.com/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
