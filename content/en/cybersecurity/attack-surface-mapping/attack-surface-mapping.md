---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Attack Surface Mapping

## Definition

Attack surface mapping is the practice of identifying which assets, services, routes, interfaces, dependencies, data stores, environments, and trust relationships are **actually exposed or reachable** from an attacker's perspective — and comparing that observable reality against the organization's intended design. The deliverable is a maintained inventory with owner, environment, exposure level, and lifecycle state per asset.

## Why it matters

Security teams routinely reason from architecture diagrams, intended designs, and ownership assumptions. Attackers reason from what responds. Attack surface mapping closes that gap by starting from observable reality and treating every mismatch — undocumented service, stale DNS, hidden endpoint, undocumented API, exposed admin panel, claimable storage, vendor-connected surface, abandoned environment, drifted cloud resource — as a triage candidate.

The asymmetry is structural: attackers find the surface for free using public sources and a bit of probing; defenders need explicit work to maintain a current view. A team that does not invest in mapping is permanently behind, and the gap grows with every deployment, vendor change, certificate, and DNS record.

This is the **umbrella note** for the branch:
- [[external-attack-surface]] owns public reachability (the dominant attacker view).
- [[internal-attack-surface]] owns post-boundary-collapse reachability (what becomes reachable after SSRF, foothold, or VPN).
- [[recon|Recon]] owns the operator workflow that discovers candidate surface.
- This note owns the **reasoning model** that ties them together into an actionable map.

## How it works

Attack surface mapping asks **5 inventory questions** of every observed asset. Skipping any one of them produces a map that cannot drive remediation.

1. **What exists?** Domains, hosts, IPs, ports, services, routes, APIs, storage, identities, vendors, environments, and the relationships between them. Source: external recon ([[passive-recon]]) plus inside-out inventory (cloud accounts, gateways, repositories, certificates, traffic logs).
2. **What is reachable?** Internet, internal network, cloud VPC, workload, browser, partner network, or only through SSRF/foothold paths. Reachability is a property of the path, not the address ([[nat-and-private-networks]]).
3. **What is intended?** Public product surface, private control plane, staging environment, legacy compatibility, vendor integration, or unknown/orphaned. The "unknown" answer is itself a finding.
4. **Who owns it?** Team, system, vendor, environment, lifecycle state, escalation path. **"Unknown owner" is a security finding** because nobody can safely retire, patch, or harden the asset.
5. **What changed?** New deployments, version drift, stale DNS, abandoned services, leaked schemas, deprovisioned-but-still-reachable assets, new vendor relationships. Mapping is a diff, not a snapshot.

There is no payload here. The note is a **reasoning model**: compare observable surface against intended design, treat every mismatch as a triage candidate, and route every candidate to validation, remediation, ownership-assignment, or retirement.

A worked example, the diff in action:

```
Question:  Map example.com's external surface and flag drift.
Source A (outside-in): cert transparency + DNS + nmap → 47 names, 12 active services, 3 vendor-hosted.
Source B (inside-out): cloud account + DNS provider + asset registry → 41 names, 11 services.
Diff:      6 names in A not in B (drift candidates), 0 in B not in A.
Triage:    3 drift names → owned by team that left (orphaned), 2 → vendor-acquired stale, 1 → recent deploy not yet registered.
Action:    orphaned → retire DNS+cert; stale → vendor takedown; new → register in asset DB.
```

The diff between outside-in and inside-out is the load-bearing artifact. Single-source inventory always misses one direction.

## Techniques / patterns

Practitioners combine outside-in discovery and inside-out inventory.

- **Outside-in:** root domains, subdomains, certificate transparency (`crt.sh`), DNS records (passive DNS history), ASN/BGP records, IP/port enumeration, web tech fingerprinting, JavaScript/source-map route extraction, public API specs, GraphQL introspection, exposed storage triage.
- **Inside-out:** cloud account inventories (AWS Config, GCP Asset Inventory, Azure Resource Graph), DNS-provider zones, gateway/load-balancer configs, repository code search, traffic logs, certificate orchestration system records, owner registries.
- **Diff comparison:** outside-in vs inside-out, current vs prior snapshot, observed vs documented, public-asset name vs asset registry.
- **Lifecycle integration:** discovery feeds release pipelines (new asset → asset DB before launch) and decommission workflows (retired asset → DNS, cert, route, storage, monitoring removed together).

## Variants and bypasses

Attack surface clusters into **6 exposure classes**. Each class has a different discovery pattern and remediation pattern.

### 1. Public internet surface

Domains, hosts, ports, web apps, APIs, storage, and remote-access services reachable from the public internet. The dominant attacker view; covered in depth by [[external-attack-surface]]. Discovery: cert transparency + DNS + port scan + web crawl.

### 2. Hidden application surface

Routes, parameters, GraphQL fields, API versions, mobile-app endpoints, and JavaScript-discovered paths not visible in the normal UI. The application has more surface than its UI suggests. Discovery: source-map extraction, mobile-app reverse engineering, [[api-inventory-management|API inventory]].

### 3. Control-plane surface

Admin panels, support tools, debug interfaces, CI/CD systems, dashboards, vendor consoles, and management APIs. Often higher privilege than product surface, often weaker authentication. Covered in depth by [[admin-interface-discovery]].

### 4. Environment drift

Staging, preview, beta, legacy, regional, demo, and temporary environments that remain reachable after their purpose ended. **Temporary exposure becomes permanent** if not tied to lifecycle automation. Risky naming patterns (`dev.`, `staging.`, `beta.`, `legacy.`) accelerate triage.

### 5. Third-party and cloud surface

CDNs, object storage, SaaS portals, identity providers, external APIs, cloud metadata endpoints, vendor-hosted assets. Trust extends through CNAMEs and OAuth scopes; failures cascade across the boundary. Covered by [[third-party-exposure]].

### 6. Internal reachability surface

Private services that become reachable after SSRF, server-side execution, VPN access, compromised workload, or weak segmentation. Covered in depth by [[internal-attack-surface]]. Discovery happens after a foothold or via SSRF reachability tests.

## Impact

Ordered roughly by severity:

- **Direct compromise path.** An exposed admin, debug, storage, or vulnerable service becomes the easiest entry point. One forgotten Jenkins is enough.
- **Access-control bypass.** Hidden endpoints, deprecated API versions, or staging environments skip controls present in the main product path.
- **Data exposure.** Storage, schemas, logs, source maps, exports, and verbose APIs leak credentials, source, customer data, or internal terminology.
- **Cloud or vendor takeover.** Stale CNAMEs, orphaned DNS records, and overly trusted third parties become claimable. Covered by [[subdomain-takeover]].
- **Patch and monitoring gaps.** Unknown assets are not patched, logged, rate-limited, or owned. The asset becomes its own attack vector by being invisible to defenders.

## Detection and defense

Defenses prioritize **maintaining the diff**, not running one-time scans.

1.
**Maintain a living inventory from multiple signals.**
   Combine DNS, cloud accounts, gateways, repositories, traffic logs, certificates, scanners, and owner records. A single inventory source always misses drift; the diff between sources is where drift hides.

2.
**Assign owner, environment, exposure, and lifecycle state to every asset.**
   "Unknown owner" and "unknown purpose" are security findings. Without owners, no remediation completes; without lifecycle state, retirement never happens.

3.
**Continuously compare intended design against observed reachability.**
   Mapping is a diff, not a snapshot. Schedule outside-in vs inside-out comparison; treat every name in one view but not the other as a triage candidate.

4.
**Prioritize by reachability, privilege, data sensitivity, and control-plane power.**
   Internet-facing admin and storage surfaces outrank low-impact brochure pages. Risk = (reachability) × (privilege if compromised) × (data sensitivity).

5.
**Integrate discovery into release and decommissioning pipelines.**
   New assets enter inventory before launch; retired systems lose DNS, certificates, routes, credentials, storage policies, and monitoring dependencies together. Lifecycle automation prevents the most common drift.

6.
**Use safe, authorized scanning and rate limits.**
   Discovery should be repeatable and low-noise across production environments. Aggressive scanning of your own surface is fine but generates alerts and load; budget for it.

### What does not work as a primary defense

- **Architecture diagrams alone.** They describe intent, not observed exposure; the diagram is what should exist, not what does.
- **Removing UI links to hide endpoints.** Hidden API routes remain callable; obscurity is not access control.
- **One-time scans.** Attack surface changes with every deployment, vendor change, certificate, and DNS record. A scan from last quarter is wrong today.
- **Asset lists without owners.** Unowned inventory does not produce remediation; the list grows but nothing happens.
- **Assuming "cloud" or "private" means unreachable.** Reachability depends on network path, identity, and workload context — not on the address space.

## Practical labs

Use an owned domain, an authorized scope, or a lab environment.

### Build a surface inventory table

```
asset                  | type         | environment | reachability | owner       | auth        | data sensitivity | lifecycle
example.com            | web app      | production  | internet     | platform    | OIDC        | medium           | active
api.example.com        | REST API     | production  | internet     | api-team    | OAuth+JWT   | high             | active
support.example.com    | vendor (zd)  | production  | internet     | support     | vendor SSO  | medium           | active
admin.example.com      | admin panel  | production  | internet     | platform    | basic auth  | high             | DEPRECATE
staging.example.com    | staging app  | staging     | internet     | unknown     | weak        | high             | INVESTIGATE
legacy-blog.example.io | legacy site  | unknown     | internet     | UNKNOWN     | none        | low              | RETIRE
```

The "unknown" rows are findings. The map is the deliverable.

### Compare certificates to DNS to asset registry (the diff)

```
# Outside-in: certificate transparency
curl -s 'https://crt.sh/?q=%25.example.test&output=json' \
  | jq -r '.[].name_value' | tr ',' '\n' | sort -u > outside.txt

# Inside-out: DNS provider zone export + asset registry
cat dns-zone.txt asset-registry.txt | sort -u > inside.txt

# The diff
comm -23 outside.txt inside.txt > drift-outside-only.txt   # observed but not registered
comm -13 outside.txt inside.txt > drift-inside-only.txt    # registered but not observed (decommissioned?)
```

Outside-only names are drift candidates; inside-only names are decommission-verification candidates.

### Compare documented API routes to deployed routes

```
# Routes in code
rg -n "/api/|router\\.|app\\.(get|post|put|patch|delete)" src/ > routes-in-code.txt

# Routes in OpenAPI spec
yq '.paths | keys' openapi.yaml > routes-in-spec.txt

# Routes hit in traffic
awk '$7 ~ "/api/" {print $7}' access.log | sort -u > routes-in-traffic.txt
```

Routes in code but not in spec are undocumented. Routes in traffic but not in code are stale routing or proxy issues.

### Triage reachable services

```
# Owned target only.
nmap -sV -Pn -p 22,80,443,3389,5432,6379,8080,8443,9000-9100 --open target.example.test
```

For each open service, classify as expected / unexpected / unknown / retire-candidate.

### Build the lifecycle-decommission checklist

```
asset retired:           api-staging-old.example.com
DNS A/CNAME removed:     yes / no
certificate revoked:     yes / no
load-balancer rule:      yes / no
cloud resource deleted:  yes / no
secrets/credentials:     rotated and removed
monitoring alerts:       removed (no false positive on retired asset)
```

Decommissioning is the most common source of drift; the checklist forces all the cleanup steps to complete together.

## Practical examples

- A staging host stays internet-facing months after launch and uses weaker authentication than production.
- A JavaScript bundle exposes undocumented API endpoints that bypass UI-level access controls.
- A deleted SaaS integration leaves a claimable DNS CNAME pointing at a deprovisioned vendor tenant.
- An object storage bucket exposes logs, backups, or source maps because the bucket policy was never reviewed after launch.
- A legacy API version still returns sensitive fields that the current version filters out.
- A new vendor relationship adds a CNAME on `support.example.com` without going through the asset registry, becoming invisible to inventory.

## Related notes

- [[external-attack-surface]]
- [[internal-attack-surface]]
- [[exposed-service-triage]]
- [[endpoint-discovery]]
- [[admin-interface-discovery]]
- [[third-party-exposure]]
- [[subdomain-takeover]]
- [[api-inventory-management|API Inventory Management]]
- [[recon|Recon]]
- [[company-osint|Company OSINT]]

### Suggested future atomic notes

- staging-environments
- schema-exposure
- asset-ownership-model
- internet-exposure-reduction
- cloud-asset-inventory
- hidden-parameter-discovery
- lifecycle-decommission-automation

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
- **Foundational:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services
