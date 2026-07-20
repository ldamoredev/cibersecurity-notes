---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Load Balancers

## Definition

A load balancer is an entrypoint that distributes traffic across backend services and often performs TLS termination, health checks, host/path routing, connection reuse, and header injection.

## Why it matters

Load balancers are operational components that become security boundaries. They decide which backend receives a request, which headers are added, whether TLS ends at the edge, whether health endpoints are reachable, and whether direct backend access should exist.

This note owns entrypoint routing and backend reachability. [[reverse-proxies]] owns deeper HTTP normalization and parser-disagreement behavior.

## How it works

A load balancer applies **5 security-relevant functions**:

1. **Accept traffic.** Listens on public or private IPs/ports.
2. **Terminate or pass through TLS.** May decrypt at the edge or forward encrypted traffic.
3. **Choose a backend.** Routes by host, path, port, protocol, weight, health, or target group.
4. **Rewrite or add metadata.** Adds `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Port`, `Forwarded`, or provider-specific headers.
5. **Perform health checks.** Probes backend paths or ports and removes unhealthy targets.

Example path:

```
client -> CDN/WAF -> public load balancer :443
load balancer -> app target group          :8080
load balancer -> /health every 30s
```

The security question is whether the backend only trusts traffic and metadata that actually came through this path.

## Techniques / patterns

Attackers and defenders inspect:

- public listeners and exposed ports
- host/path routing rules
- TLS termination and backend encryption
- direct backend IP/port reachability
- health-check paths and diagnostic leakage
- forwarded headers and client IP propagation
- target groups, backend pools, and stale targets
- default backends and catch-all routes
- sticky sessions and routing affinity
- mismatch between load balancer logs and app logs

## Variants and bypasses

Load-balancer issues fall into **6 classes**.

### 1. Direct backend bypass

The backend is reachable directly by IP, alternate DNS, or public security-group rule. This bypasses edge TLS, WAF, auth gateways, rate limits, and header overwrite rules.

### 2. TLS termination gaps

TLS ends at the load balancer, but backend traffic is plaintext or unauthenticated. This may be acceptable in a trusted network, but dangerous across shared or weakly segmented paths.

### 3. Header trust confusion

The load balancer adds forwarding headers, but the backend also accepts client-supplied versions. This creates client-IP, scheme, host, and URL-generation bugs.

### 4. Routing rule mistakes

Host/path/default rules send traffic to the wrong target group, expose admin paths, or let hostile `Host` values reach unexpected backends.

### 5. Health-check exposure

Health endpoints reveal internals, bypass auth, or remain publicly reachable because they were designed for the load balancer and then exposed to everyone.

### 6. Stale or mixed target groups

Old versions, debug instances, or wrong-environment targets remain registered behind the same load balancer.

## Impact

Ordered roughly by severity:

- **Bypass of edge controls.** Direct backend access skips WAF, CDN, auth, logging, or TLS policy.
- **Credential/session exposure.** Plaintext backend hops can expose sensitive headers if the internal network is not trustworthy.
- **Privilege or tenant routing bugs.** Host/path mistakes route users to wrong apps or admin surfaces.
- **Client-IP trust abuse.** Bad forwarding-header handling breaks rate limits, allowlists, logs, and access controls.
- **Information leakage.** Health checks and default backends expose internals.
- **Availability risk.** Bad health checks or target drift route traffic to unhealthy or unintended services.

## Detection and defense

Ordered by effectiveness:

1.
**Block direct backend reachability.**
   Backends should accept inbound traffic only from the load balancer or trusted upstream identity. This is the control that makes the load balancer a real boundary.

2.
**Define TLS policy for both client and backend hops.**
   Use modern TLS at the edge and decide explicitly whether backend TLS or mTLS is required. Sensitive traffic across shared networks should be encrypted and authenticated end-to-end.

3.
**Overwrite forwarding headers at the load balancer and trust them only from that path.**
   The edge should set source/proto/host headers consistently; the backend should ignore those headers from any other source.

4.
**Audit routing rules and default targets.**
   Every host/path rule should have an owner and expected target group. Default catch-all routes should fail closed or serve harmless content.

5.
**Protect health and diagnostic endpoints.**
   Health endpoints should reveal minimal state and be reachable only where needed. Public users should not receive backend diagnostics.

6.
**Continuously prune target groups.**
   Remove stale instances, old deployments, debug hosts, and wrong-environment targets. Load balancer pools are inventory surfaces.

7.
**Correlate load-balancer and backend logs.**
   Request IDs, source IP, target ID, host, path, and status codes should let you prove which backend served a request.

### What does not work as a primary defense

- **Assuming the load balancer protects backends while backends are public.** Attackers can bypass the front door.
- **Trusting `X-Forwarded-*` because the load balancer sets it.** Clients can set those headers too unless the edge overwrites and the backend restricts trust by network path.
- **Edge-only HTTPS as a blanket guarantee.** Backend plaintext may still matter.
- **Health endpoint obscurity.** `/healthz` and `/actuator/health` are easy to find.
- **One default backend for everything.** Catch-all routes often leak wrong apps or admin panels.

## Practical labs

Run only against infrastructure you own or are authorized to test.

### Fingerprint the entrypoint

```
curl -skI https://app.example.com/ | rg -i 'server|via|x-cache|x-amz|cf-ray|x-forwarded|strict-transport-security'
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null | rg -i 'issuer=|subject=|ALPN|Protocol|Cipher'
```

Identify CDN/LB clues, TLS posture, and policy headers.

### Compare host/path routing

```
curl -skI https://app.example.com/
curl -skI https://app.example.com/health
curl -skI https://app.example.com/admin
curl -skI https://app.example.com/ -H 'Host: unexpected.example.com'
```

Unexpected successes or redirects may indicate routing/default-backend problems.

### Probe forwarded-header handling

```
curl -skI https://app.example.com/ \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'X-Forwarded-Proto: http' \
  -H 'X-Forwarded-Host: evil.example'
```

Look for changed status, redirects, generated URLs, or log effects.

### Test direct backend reachability

```
origin_ip=203.0.113.42
curl -skI "https://$origin_ip/" -H 'Host: app.example.com' --connect-timeout 5
curl -sI  "http://$origin_ip:8080/" -H 'Host: app.example.com' --connect-timeout 5
```

Expected: blocked unless direct origin access is intentionally allowed.

### Inspect health-check exposure

```
for path in /health /healthz /status /metrics /actuator/health; do
  printf '%s -> ' "$path"
  curl -sk -o /dev/null -w '%{http_code}\n' "https://app.example.com$path"
done
```

Follow up any verbose or public diagnostics.

### Compare load-balancer and backend logs

```
1. Send one request with X-Request-ID: lb-lab-001.
2. Find it in load-balancer logs.
3. Find it in backend logs.
4. Compare source IP, host, path, scheme, target, and status.
```

This proves how metadata crosses the boundary.

## Practical examples

- The public load balancer enforces HTTPS, but the backend is reachable directly over HTTP on `8080`.
- A default host rule routes unknown `Host` headers to an admin app.
- The app trusts `X-Forwarded-Proto: https`, allowing an attacker to make generated links or security decisions lie.
- `/actuator/health` is intended for the load balancer but exposes database and dependency status publicly.
- A stale target group still includes a debug build with verbose errors.

## Related notes

- [[reverse-proxies]] — deeper HTTP normalization and parser disagreement.
- [[client-ip-trust]] — forwarded client IP semantics.
- [[tls-https]] — edge and backend TLS posture.
- [[firewalls-and-network-boundaries]] — blocking direct backend reachability.
- [[http-headers]] — forwarding and policy headers.
- [[service-enumeration]] — identifying load balancer and backend behavior.

### Suggested future atomic notes

- direct-origin-bypass
- load-balancer-health-checks
- target-group-drift
- edge-vs-origin-tls
- host-based-routing
- sticky-sessions

## References

- **Foundational:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Foundational:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning
