---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Host and Port Discovery

## Definition

Host and port discovery is the process of finding live hosts and the reachable ports and services they expose within an authorized scope.

## Why it matters

Once domains and candidates are known, host and port discovery validates what is actually listening. This is one of the cleanest ways to separate stale surface from live surface and to identify alternate entry points.

Keep the boundary clear: this note is about reachability and exposed ports, while [[service-validation]] and [[service-enumeration|Service Enumeration]] go deeper into what those responses mean.

## How it works

Host and port discovery has **4 layers**:

1. **Resolve.** Convert names to IPs and identify provider/CDN/origin clues.
2. **Reach.** Determine whether hosts answer at all.
3. **Scan.** Identify open ports and likely protocols within scope.
4. **Prioritize.** Route interesting services to validation and attack-surface triage.

The bug is not an open port by itself. The risk is a reachable service that is unexpected, sensitive, unowned, or weakly controlled.

A worked example, port scan to triage:

```
Host:
  api-preview.example.test

Open ports:
  443/tcp HTTPS
  8443/tcp HTTPS-alt
  22/tcp SSH

Peer comparison:
  other preview hosts expose only 443

Decision:
  8443 and 22 are outliers; route 8443 to service validation and 22 to exposed-service triage
```

Port discovery becomes valuable when each outlier receives a role hypothesis and next validation.

## Techniques / patterns

Practitioners check:

- live HTTP/HTTPS behavior
- top ports and environment-specific ports
- remote access ports such as SSH, RDP, VPN
- database/cache/search/queue ports
- high-port dashboards and dev servers
- CDN/proxy versus direct-origin differences
- peer hosts with unusual extra services

## Variants and bypasses

Discovery results fall into **6 classes**.

### 1. Expected public web ports

Normal HTTP/HTTPS/API exposure.

### 2. Remote access ports

SSH, RDP, VPN, admin protocols, or bastion-like services.

### 3. Data service ports

Databases, caches, queues, search engines, and object gateways.

### 4. Admin/dashboard ports

Grafana, Kibana, Jenkins, debug servers, metrics, and management panels.

### 5. Edge/origin split

CDN/proxy path differs from direct origin reachability.

### 6. False positive or filtered state

Firewalls, CDN edges, tarpit behavior, or shared hosting distort scan output.

## Impact

Ordered roughly by severity:

- **Initial access.** Remote access or exploitable service is reachable.
- **Data exposure.** Data services appear outside intended networks.
- **Control-plane exposure.** Dashboards and admin services are reachable.
- **Edge bypass.** Direct origins bypass CDN/WAF controls.
- **Inventory correction.** Unexpected services become owner questions.

## Detection and defense

Ordered by effectiveness:

1.
**Define expected ports per asset role.**
   A web server, database, admin tool, and CDN origin should have different expected exposure.

2.
**Continuously scan owned public assets.**
   External scan results should be compared to inventory.

3.
**Restrict management and data ports.**
   These should not be broadly internet-facing.

4.
**Validate origin isolation.**
   Direct origins should reject traffic that bypasses intended edges.

5.
**Monitor changes in port posture.**
   New ports often appear during incidents, migrations, or temporary debugging.

### What does not work as a primary defense

- **Non-standard ports.** Scanners find them.
- **Filtered state without ownership.** You still need to know why a port behaves that way.
- **One-time scanning.** Port posture changes with deployments and firewall updates.
- **Assuming CDN means origin is hidden.** Origins leak through DNS, certs, and direct IPs.

## Practical labs

Use owned targets.

### Scan common ports

```
nmap -sV -Pn --top-ports 100 target.example.test
```

Route unexpected findings into service validation.

### Check high-risk ports

```
nmap -sV -Pn -p 22,3389,5432,3306,6379,9200,5601,8080,8443 target.example.test
```

These ports often represent admin or data exposure.

### Compare peer hosts

```
nmap -sV -Pn -iL hosts.txt --top-ports 50
```

Outliers often deserve triage first.

### Build a port posture table

```
host | port | service guess | expected? | peer outlier? | owner | next validation
```

This turns scans into exposure decisions.

### Check IPv4 and IPv6 exposure

```
nmap -6 -sV -Pn --top-ports 50 ipv6-host.example.test
```

Dual-stack services can expose ports missed by IPv4-only reviews.

### Route ports to service validation

```
port class | examples | next note
remote admin | 22, 3389 | exposed-service-triage
dashboard | 3000, 5601, 9090 | service-validation
data | 5432, 6379, 9200 | internal/exposed-service review
```

The scan is only useful once ports are routed to decisions.

## Practical examples

- Scanning reveals SSH or database ports that should not be public.
- One host exposes more services than its peers.
- A public service responds on a nonstandard port and was never documented.
- A direct origin exposes HTTP outside the CDN.
- A metrics dashboard answers on `9090`.

## Related notes

- [[nmap-scanning|Nmap Scanning]]
- [[service-enumeration|Service Enumeration]]
- [[public-asset-discovery]]
- [[service-validation]]
- [[exposed-service-triage|Exposed Service Triage]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]

### Suggested future atomic notes

- remote-access-exposure
- database-port-exposure
- direct-origin-discovery
- dashboard-port-triage
- scan-result-prioritization

## References

- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
