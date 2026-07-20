---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# External Attack Surface

## Definition

External attack surface is the set of assets, services, interfaces, data stores, and trust paths reachable from outside the organization's internal networks — most often over the public internet, but also through partner networks, vendor portals, and federated identity boundaries. It is **the dominant view real attackers, bug bounty researchers, and search engines actually see**.

## Why it matters

External surface is usually the first thing an attacker discovers and the last thing a defender finishes mapping. It includes public domains, APIs, ports, object storage, login pages, remote-access services, cloud-hosted apps, vendor-hosted content, and forgotten environments. Most real-world initial-access events come from this surface — a forgotten Jenkins, a public S3 bucket, a stale subdomain, an exposed admin panel — not from custom application bugs.

Keep it distinct from [[internal-attack-surface]]: external surface is about **public reachability**, not what becomes reachable only after SSRF, foothold, or private network access. Mixing the two produces incoherent prioritization.

External surface is also the highest-leverage defensive target. Every exposure removed here cuts attacker dwell time and discovery cost without any change to internal controls. The math favors maintenance: a continuous outside-in view costs less than the average post-incident response.

## How it works

External attack surface has **4 discovery layers**. A useful map covers all four; missing any one creates a known blind spot.

1. **Name layer.** Domains, subdomains, certificates (`crt.sh` certificate transparency), DNS records (current + historical via passive DNS), cloud hostnames, vendor mappings (CNAME chains). The first thing an attacker enumerates and the easiest to map.
2. **Network layer.** IPs, ASN/BGP records, ports, protocols, CDNs, reverse proxies, remote-access services. Resolves "what is the address" into "what is reachable at the address."
3. **Application layer.** Web apps, APIs, routes, admin panels, storage, exposed documents, JavaScript routes, GraphQL endpoints. Most product surface lives here, but admin and storage exposures here cause the largest incidents.
4. **Relationship layer.** Third-party providers, callbacks, identity providers, analytics, support tools, SaaS integrations, OAuth scopes. Trust extends through CNAMEs and tokens; this is where vendor breaches become target breaches.

The bug is **not that public assets exist** — most of them must be public. The bug is public assets that are **unknown, unowned, overprivileged, stale, or weaker than the main product surface**.

A worked example, the four layers in concert:

```
Question:   What's externally reachable for example.com that is not on the asset list?
Layer 1:    crt.sh returns 47 names; passive DNS adds 8 historical names.
Layer 2:    52 names resolve; 6 are CDN-fronted, 4 direct cloud origin, 1 unknown ASN.
Layer 3:    direct probe finds 12 web apps + 4 admin/login pages + 2 GraphQL endpoints.
Layer 4:    CNAME inspection: 3 zendesk, 2 statuspage, 1 deprovisioned vendor (CLAIMABLE).
Findings:   2 admin panels with weak auth; 1 GraphQL with introspection on; 1 takeover-candidate.
Action:     [admin → enforce SSO + IP allowlist], [GraphQL → disable intro], [CNAME → remove DNS].
```

The takeover candidate is the highest-severity finding. Layer 1 alone would have missed it.

## Techniques / patterns

The discipline is "outside-in plus inside-out, then diff."

- **Root domains, subdomains, certificates** via certificate transparency (`crt.sh`), DNS history (SecurityTrails, ViewDNS), wordlist-based enumeration.
- **Cloud hostnames, object storage, CDN mappings** via cloud-provider hostname patterns (`*.s3.amazonaws.com`, `*.blob.core.windows.net`, `*.storage.googleapis.com`).
- **Common ports, web technologies, login surfaces** via authorized scanning (nmap, masscan), web fingerprinting (Wappalyzer-style), screenshot-based triage (`gowitness`, `eyewitness`).
- **Staging, preview, beta, dev, regional environment names** via wordlist-based subdomain enumeration and certificate transparency wildcards.
- **Public API docs, OpenAPI specs, GraphQL endpoints, JavaScript routes** via standard well-known paths (`/openapi.json`, `/graphql`, `/.well-known/`), source-map extraction, and JS bundle analysis.
- **Exposed backups, logs, source maps, artifacts** via [[google-dorking|exposure-shaped queries]] and bucket-name enumeration.

## Variants and bypasses

External surface clusters into **6 forms**. Each form has a different "what should this be" expectation.

### 1. Expected public product surface

Main websites, APIs, documentation, and customer-facing services. Designed to be public; the discipline is keeping the controls (authentication, rate limiting, schema validation, monitoring) aligned with the data sensitivity.

### 2. Forgotten environment surface

Staging, preview, beta, old regional, training, or temporary systems that stayed online after their purpose ended. **Temporary exposure becomes permanent** when not tied to lifecycle automation. Highest-yield discovery target on most organizations.

### 3. Remote administration surface

VPN, SSH, RDP, management panels, appliance consoles, support dashboards, debug interfaces. Higher privilege than product surface, often weaker authentication. Internet exposure of admin surfaces should require explicit justification per asset.

### 4. Data and artifact surface

Object storage, logs, backups, source maps, reports, build artifacts exposed directly without an application gating them. Bucket-policy review and CI artifact-strip checks catch most of these at low cost.

### 5. Third-party hosted surface

SaaS portals, CDN origins, vendor callbacks, identity providers, hosted widgets. Trust extends through CNAMEs; vendor decommissioning failures cause [[subdomain-takeover|takeover]] risk.

### 6. Legacy protocol or service surface

Old services or ports kept for compatibility but missing current controls (cleartext protocols, unauthenticated SMB/NFS, deprecated SSH algorithms, FTP). Often the result of "leave it on, just in case" decisions that are never revisited.

## Impact

Ordered roughly by severity:

- **Initial access.** Exposed admin, remote access, or vulnerable services become entry points; one weak Jenkins is enough.
- **Sensitive data disclosure.** Public storage, source maps, and artifacts leak credentials, source code, customer data, or internal terminology.
- **Control bypass.** Staging or legacy systems miss production controls (no WAF, no rate limit, no auth proxy, no logging).
- **Takeover and impersonation.** Stale DNS or vendor mappings let attackers serve content under trusted names; covered by [[subdomain-takeover]].
- **Recon acceleration.** Public metadata reveals internal structure, technologies, and endpoints, sharpening every subsequent attacker action.

## Detection and defense

Defenses prioritize **continuous outside-in vs inside-out diffing** plus lifecycle automation.

1.
**Continuously inventory public assets from outside-in and inside-out views.**
   Combine external recon (certs, DNS, scanners) with cloud/provider inventories (asset registries, DNS provider zones). Each catches different failures; the diff is the load-bearing artifact.

2.
**Classify every public asset by owner, environment, and intended audience.**
   Production, staging, internal demo, vendor-hosted, and acquisition-legacy assets need different policies. "Unknown owner" is itself a finding.

3.
**Reduce public exposure for admin, debug, and remote-access surfaces.**
   Strong authentication is required, but unnecessary internet reachability should also be removed. Default admin surfaces to allowlist + VPN + SSO; require justification per public exposure.

4.
**Tie DNS, certificates, and cloud resources to lifecycle automation.**
   Deleting a service should remove names, certificates, routes, storage policies, secrets, and monitoring dependencies together. Manual decommissioning is the single largest source of drift.

5.
**Monitor for new public hosts and risky naming patterns.**
   Names matching `dev`, `staging`, `admin`, `vpn`, `backup`, `grafana`, `jenkins`, `kibana`, `phpmyadmin` deserve fast review. New cert-transparency entries should trigger ownership-confirmation workflow.

6.
**Treat third-party CNAMEs as part of the surface.**
   Vendor-hosted surfaces carry your trust. Vendor takedown of a tenant must trigger CNAME cleanup; otherwise [[subdomain-takeover]] becomes a real risk.

### What does not work as a primary defense

- **Assuming obscurity protects non-linked hosts.** Certificate transparency, passive DNS, search engines, and wordlists reveal names; "we never advertised it" is not a control.
- **Trusting internal asset lists alone.** Attackers see what is reachable, not what is documented; the diff is what matters.
- **Leaving staging public because it is temporary.** Temporary exposure becomes permanent; the average "temporary" public asset survives years.
- **Relying only on IP allowlists.** Cloud, proxy, VPN, and header-trust mistakes weaken them; allowlists are layered defenses, not primary ones.
- **One-time external scans.** External surface changes daily; quarterly scans miss most drift.

## Practical labs

Use an owned domain, an authorized scope, or a lab environment.

### Enumerate public names from certificate transparency

```
# Get all SAN names from cert transparency
curl -s 'https://crt.sh/?q=%25.example.test&output=json' \
  | jq -r '.[].name_value' | tr ',' '\n' | sed 's/^\*\.//' | sort -u > names-ct.txt

# Add passive DNS history (if available via your DNS provider or SecurityTrails)
# Append to names-ct.txt, then sort -u
```

Tag each name as production / staging / vendor-hosted / unknown / retire-candidate.

### Resolve and group public hosts

```
# Resolve and capture the resolution path
while read host; do
  ip=$(dig +short "$host" | tail -1)
  cname=$(dig CNAME +short "$host" | head -1)
  echo "$host | $ip | ${cname:--}"
done < names-ct.txt > resolved.txt

# Group by destination
awk -F'|' '{print $3}' resolved.txt | sort | uniq -c | sort -rn
```

The CNAME column reveals vendor relationships. The IP column reveals cloud, CDN, or direct origins.

### Fingerprint web ports and capture screenshots

```
# Authorized scope only.
nmap -sV -Pn -p 80,443,8080,8443,8000,3000,5000,9000,8888 --open names-ct.txt

# Screenshot triage with gowitness or eyewitness
gowitness scan file -f names-ct.txt -t 10
```

Screenshots make admin/login surfaces obvious at a glance; classify each as expected / unexpected / unknown / retire-candidate.

### Search for risky naming patterns

```
rg -i 'admin|staging|dev|test|vpn|backup|grafana|jenkins|kibana|phpmyadmin|debug|preview|beta|legacy|old|temp' names-ct.txt
```

Risky names do not prove exposure; they focus triage. Verify each hit with [[exposed-service-triage]].

### Detect potential subdomain takeover

```
# Look for CNAMEs pointing at decommissioned vendor tenants.
while read host; do
  cname=$(dig CNAME +short "$host" | head -1)
  if [ -n "$cname" ]; then
    # Probe destination for "no such tenant" or similar fingerprints.
    response=$(curl -s -o /dev/null -w "%{http_code}" "https://$host" --max-time 5)
    echo "$host | $cname | $response"
  fi
done < names-ct.txt
```

Hand off candidates to [[subdomain-takeover]] for full validation.

### Audit third-party CNAMEs against active vendor relationships

```
subdomain               | CNAME target              | vendor             | active relationship?
support.example.com     | example.zendesk.com       | Zendesk            | yes
status.example.com      | example.statuspage.io     | StatusPage         | yes
old-help.example.com    | example.helpscoutdocs.com | HelpScout          | NO — retired 2024 — TAKEOVER RISK
```

The "no — retired" rows are the dangerous ones; remove DNS before the vendor releases the tenant.

## Practical examples

- A staging host is internet-facing and uses test credentials, providing a low-friction initial access path.
- A legacy VPN service remains reachable after migration, exposing weaker authentication and outdated TLS.
- Public object storage exposes build artifacts containing application secrets and source code.
- A support dashboard is reachable on a forgotten subdomain that nobody on the current team remembers.
- A CDN origin is directly reachable, bypassing edge controls (rate limiting, WAF, geo restrictions).
- A retired vendor relationship leaves a CNAME pointing at a tenant the vendor reassigns, allowing takeover.

## Related notes

- [[attack-surface-mapping]]
- [[internal-attack-surface]]
- [[exposed-service-triage]]
- [[exposed-storage]]
- [[admin-interface-discovery]]
- [[subdomain-takeover]]
- [[third-party-exposure]]
- [[public-asset-discovery|Public Asset Discovery]]
- [[company-osint|Company OSINT]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]

### Suggested future atomic notes

- staging-environments
- remote-access-exposure
- certificate-transparency-monitoring
- cloud-origin-exposure
- public-object-storage-review
- outside-in-vs-inside-out-diff

## References

- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services
