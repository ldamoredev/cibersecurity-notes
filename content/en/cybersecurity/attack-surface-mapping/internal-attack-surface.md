---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Internal Attack Surface

## Definition

Internal attack surface is the set of services, routes, networks, credentials, metadata endpoints, admin interfaces, and trust paths reachable from inside an environment even if they are not public.

## Why it matters

Many severe incidents come from the gap between public reachability and internal reachability. Once an attacker gains SSRF, server-side execution, VPN access, a compromised workload, or a weakly isolated cloud identity, "internal-only" surfaces become part of the real attack surface.

This note differs from [[external-attack-surface]]: the core question is what becomes reachable after a trust boundary collapses.

## How it works

Internal attack surface has **5 reachability positions**:

1. **Application workload.** What the web/API server can reach.
2. **Container or pod.** What a container can reach on overlay networks, host interfaces, and service accounts.
3. **Cloud instance or function.** What cloud identity and metadata make reachable.
4. **Employee/VPN network.** What authenticated internal users can reach.
5. **Partner or vendor path.** What third parties can reach through integrations or private links.

The mistake is treating "not internet-facing" as equivalent to "safe." Internal reachability still needs authentication, authorization, segmentation, logging, and least privilege.

A worked example, from SSRF to internal surface:

```
External input:
  https://app.example.test/avatar?url=http://10.0.12.34:8080/health

Observed behavior:
  200 OK, body contains "management-api"

Reachability position:
  application workload

New attack-surface fact:
  the app server can reach 10.0.12.34:8080, even though the service is not public

Security question:
  does that internal service require workload identity, or does network location alone authorize access?
```

The useful output is not "SSRF exists" by itself. It is a map of what the compromised request position can reach and which controls still hold there.

## Techniques / patterns

Practitioners map:

- private IP ranges, service discovery, DNS zones, and internal hostnames
- metadata endpoints and cloud IAM paths
- admin APIs, dashboards, queues, databases, and internal HTTP services
- Kubernetes services, service-account tokens, and pod-to-pod reachability
- SSRF-controlled fetch paths and proxy egress rules
- VPN/zero-trust access policy and east-west segmentation

## Variants and bypasses

Internal surface appears in **6 forms**.

### 1. Metadata and identity surface

Cloud metadata, workload identities, service account tokens, and IAM roles.

### 2. Internal admin surface

Dashboards, consoles, APIs, debug endpoints, CI/CD, and observability tools.

### 3. Data-plane surface

Databases, queues, caches, file stores, internal APIs, and service meshes.

### 4. Flat-network surface

Private networks where one workload can reach many unrelated services.

### 5. SSRF-expanded surface

Server-side URL fetches let an external attacker issue internal network requests.

### 6. Vendor/private-link surface

Partner connections, private endpoints, and SaaS integrations widen internal trust.

## Impact

Ordered roughly by severity:

- **Cloud credential theft.** Metadata and workload identity exposure can grant cloud API access.
- **Lateral movement.** Flat networks expose databases, queues, and admin tools after one foothold.
- **Control-plane compromise.** Internal dashboards or CI/CD systems alter production.
- **Data exposure.** Internal APIs return data without strong caller authentication.
- **SSRF impact amplification.** A low-impact URL fetch becomes internal reconnaissance or credential access.

## Detection and defense

Ordered by effectiveness:

1.
**Map reachability from workload positions, not just network diagrams.**
   Test what app servers, containers, functions, and VPN users can actually reach.

2.
**Require authentication and authorization on internal services.**
   Network location should reduce exposure, not replace identity and policy.

3.
**Segment high-value services and block unnecessary east-west paths.**
   Databases, metadata, admin tools, queues, and CI/CD need tight reachability.

4.
**Harden metadata and workload identity access.**
   Enforce IMDSv2 or equivalent controls, restrict service accounts, and block link-local egress where possible.

5.
**Constrain server-side fetchers and proxies.**
   URL allowlists must resolve and block private, loopback, link-local, and redirect targets.

6.
**Log internal access by workload identity.**
   Internal service calls should be attributable to workload, user, token, and route.

### What does not work as a primary defense

- **"Private IP means safe."** Reachability depends on path, not address aesthetics.
- **Unauthenticated internal admin panels.** SSRF, VPN compromise, or workload compromise can reach them.
- **Perimeter-only monitoring.** Internal movement may never cross the public edge.
- **Denying only `169.254.169.254` by string.** SSRF bypasses include redirects, DNS rebinding, integer IPs, IPv6 forms, and alternate metadata hosts.

## Practical labs

Use an owned lab or cloud account.

### Map routes from a workload

```
ip route
ip addr
```

Record private ranges, default gateways, and link-local routes.

### Probe internal HTTP reachability safely

```
for host in 127.0.0.1 169.254.169.254 10.0.0.1 172.16.0.1 192.168.0.1; do
  curl -m 2 -i "http://$host/" | head
done
```

Run only in a lab/owned environment.

### Review Kubernetes service exposure

```
kubectl get svc -A -o wide
kubectl get pods -A -o wide
```

Map which services are cluster-internal, node-exposed, or load-balanced.

### Search code for server-side fetchers

```
rg -n "fetch\\(|axios|requests\\.get|http\\.Get|open-uri|curl" src
```

These are the places where external input can become internal reachability.

### Build a reachability matrix

```
Source position | Destination | Port | Expected? | Auth required? | Evidence | Owner
web-pod         | metadata    | 80   | no        | n/a            | blocked  | platform
web-pod         | redis       | 6379 | no        | yes/no         | timeout  | data
vpn-user        | grafana     | 443  | yes       | SSO+MFA        | 302 SSO  | observability
```

This turns scattered probes into a boundary review instead of a list of hosts.

### Review metadata egress controls

```
curl -sS --max-time 2 http://169.254.169.254/ || true
curl -sS --max-time 2 http://[fe80::a9fe:a9fe]/ || true
```

Run only from owned workloads; compare host, container, and app-level behavior.

## Practical examples

- An app server can reach cloud metadata and internal admin APIs.
- A supposedly private service is exposed to every workload in a VPC.
- Internal dashboards rely only on network location.
- SSRF reaches Redis, Elasticsearch, or Kubernetes APIs.
- A partner private link grants broader reach than intended.

## Related notes

- [[attack-surface-mapping]]
- [[external-attack-surface]]
- [[nat-and-private-networks|NAT and Private Networks]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[ssrf|SSRF]]
- [[admin-interface-discovery]]

### Suggested future atomic notes

- [[cloud-iam-boundaries]]
- kubernetes-internal-surface
- service-mesh-attack-surface
- ssrf-reachability-mapping
- internal-admin-surface

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP API7:2023 SSRF — https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
