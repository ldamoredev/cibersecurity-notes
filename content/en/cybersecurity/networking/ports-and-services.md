---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Ports and Services

## Definition

A port is a numbered endpoint on a host used by transport protocols such as TCP or UDP. A service is the process or application listening on that port and speaking a protocol to clients.

## Why it matters

Ports are how network reachability becomes application attack surface. An open port is not automatically a vulnerability, but every listening service needs a reason to exist, a boundary, an owner, and a patching story.

This note owns exposed listening surface. [[service-enumeration]] starts once you want to identify what the service actually is.

## How it works

Ports and services are best understood through **4 layers**:

1. **Address.** Which host/interface receives traffic.
2. **Transport.** TCP or UDP carries traffic to a numbered port.
3. **Listener.** A process binds to that address and port.
4. **Protocol/application.** The service speaks SSH, HTTP, TLS, Postgres, Redis, DNS, or another protocol.

Example:

```
0.0.0.0:5432/tcp -> postgres process -> PostgreSQL protocol
127.0.0.1:3000/tcp -> node process -> HTTP dev server
203.0.113.10:443/tcp -> nginx -> TLS/HTTP reverse proxy
```

The same port number can mean different risk depending on where it is bound and who can reach it.

## Techniques / patterns

Attackers and defenders inspect:

- local listening sockets with `lsof`, `ss`, or `netstat`
- remote open ports with Nmap or targeted `nc`
- TCP vs UDP exposure
- bind address: loopback, private, public, all interfaces, IPv6
- expected vs unexpected service inventory
- high-numbered admin/dev ports
- database/cache/queue ports reachable outside intended networks
- direct backend ports that bypass reverse proxies or load balancers

## Variants and bypasses

Listening surface falls into **6 service classes**.

### 1. Public web entrypoints

Ports 80 and 443 normally expose HTTP/HTTPS through a reverse proxy, CDN, or load balancer. Expected, but still needs TLS, headers, routing, and app security review.

### 2. Remote administration

SSH, RDP, VPN, management consoles, and bastions are high-value because they control systems rather than app features.

### 3. Data stores and queues

PostgreSQL, MySQL, Redis, Elasticsearch, RabbitMQ, Kafka, and similar services should almost never be internet-reachable directly.

### 4. Developer and debug services

Framework dev servers, debug ports, hot reloaders, notebooks, and profiling endpoints often appear during incidents or experiments and then linger.

### 5. Health, metrics, and diagnostics

Prometheus, actuator, `/metrics`, `/health`, tracing, and admin APIs can reveal internal state or provide control-plane actions.

### 6. UDP services

DNS, NTP, SNMP, VPN, and discovery protocols behave differently than TCP and are often under-scanned.

## Impact

Ordered roughly by severity:

- **Direct compromise path.** Exposed admin or data services may allow auth bypass, weak credential attacks, or known-service exploitation.
- **Proxy/control bypass.** Direct backend ports skip WAF, auth gateway, rate limits, or logging.
- **Data exposure.** Databases, caches, and search services may expose sensitive data.
- **Internal reconnaissance.** Banners and port combinations reveal stack and architecture.
- **Lateral movement.** Internal services reachable after one foothold widen blast radius.
- **Operational drift.** Unknown listeners indicate deployment/inventory mismatch.

## Detection and defense

Ordered by effectiveness:

1.
**Keep an expected-service inventory.**
   For every host or workload, define which ports should listen, on which interfaces, and from which source ranges. Detection only works against an expected state.

2.
**Bind services narrowly.**
   Local-only services should bind loopback. Internal services should bind private interfaces. Public exposure should be intentional and documented.

3.
**Enforce network boundaries around non-public services.**
   Databases, caches, queues, admin panels, and metrics should be blocked from public paths regardless of app-level authentication.

4.
**Scan from relevant viewpoints.**
   Public, VPN, internal subnet, container, and cloud workload views produce different reachable port sets.

5.
**Remove or protect diagnostic surfaces.**
   Health and metrics endpoints should reveal minimum information and be access-controlled where they expose internals.

6.
**Review IPv6 and UDP explicitly.**
   Many exposure reviews accidentally cover only TCP/IPv4.

### What does not work as a primary defense

- **Using nonstandard ports.** Scanners find high ports.
- **Assuming localhost in development equals localhost in production.** Bind settings often change with container or framework defaults.
- **Relying on "security by obscurity" for admin ports.** Hidden paths and unusual ports are discovery problems, not defenses.
- **Ignoring closed vs filtered semantics.** They mean different things for boundary validation.
- **Letting every service bind `0.0.0.0`.** Convenience becomes exposure.

## Practical labs

Run only against owned or authorized systems.

### List local listening services

```
lsof -i -P -n | rg 'LISTEN|UDP'
ss -lntup 2>/dev/null || true
```

Look for unexpected processes and bind addresses.

### Scan common remote ports

```
nmap -Pn --top-ports 1000 your-host.example.com
```

This gives a fast external listening-surface snapshot.

### Scan all TCP ports

```
nmap -Pn -p- --min-rate 1000 your-host.example.com
```

Use when looking for high-port admin/dev services.

### Test one service manually

```
nc -vz your-host.example.com 443
curl -skI https://your-host.example.com/
```

Manual probes help validate scanner output.

### Compare localhost vs public binding

```
curl -sI http://127.0.0.1:3000
hostname -I 2>/dev/null || ipconfig getifaddr en0
```

Then test from another host if authorized. Local success does not imply remote reachability.

### Check UDP intentionally

```
nmap -Pn -sU -p 53,123,161 your-host.example.com
```

Keep UDP scans targeted and interpret silence carefully.

## Practical examples

- Redis on `6379/tcp` is exposed publicly because a container published all ports.
- A backend app on `8080/tcp` is reachable directly, bypassing the HTTPS reverse proxy.
- SSH is intended to be bastion-only but appears open from the public internet.
- A metrics service on `9100/tcp` exposes hostnames, process names, and internal labels.
- IPv6 exposes `22/tcp` while IPv4 blocks it.

## Related notes

- [[tcp-ip-basics]] — addressing, routing, and transport foundation.
- [[service-enumeration]] — identifying what listens on an open port.
- [[nmap-scanning]] — scan strategy.
- [[firewalls-and-network-boundaries]] — allowed and blocked paths.
- [[exposed-service-triage|Exposed Service Triage]]
- [[load-balancers]] — public entrypoint routing.

### Suggested future atomic notes

- common-service-ports
- bind-addresses
- localhost-vs-public-bind
- udp-service-exposure
- admin-port-exposure
- metrics-endpoint-exposure

## References

- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
