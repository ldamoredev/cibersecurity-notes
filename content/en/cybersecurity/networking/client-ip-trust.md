---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Client IP Trust

## Definition

Client IP trust is the question of **which IP an application treats as "the client"** when requests pass through any intermediary — reverse proxy, load balancer, CDN, WAF, or service-mesh sidecar. The bug is rarely "we read the wrong header." The bug is that the trust translation between network identity and HTTP-header identity is unaudited: the proxy speaks one truth, the backend believes a different one, and the attacker chooses which.

## Why it matters

A surprising amount of production security depends on this single string:

- **Rate limiting** — keyed by client IP. Spoofed IP → unlimited rotation.
- **IP allowlists** — admin panels, internal APIs, vendor integrations. Spoofed IP → privileged access.
- **Audit logs** — fraud, abuse, incident response. Spoofed IP → wrong attribution, evidence chain corrupted.
- **Geo-blocking and license enforcement** — spoofed IP → policy bypass.
- **Fraud-detection signals** — spoofed IP → laundered behavior.
- **WAF and abuse blocklists** — spoofed IP → ban evasion by header rotation.
- **Cache keys** — when `X-Forwarded-For` is part of the cache key, spoofed values become a poisoning surface.

Forwarded-header trust is also the canonical example of the **trust-disagreement class** introduced in [[reverse-proxies]]: the proxy and backend agree on the bytes but disagree on what to believe about identity.

## How it works

There is no "real client IP." There is only a **trust translation** between two facts:

1. **Network identity** — the source IP of the TCP connection that reached the backend. The kernel knows this; it cannot be forged at the TCP layer (modulo BGP/route-hijack scenarios, which are out of scope for this note). For a backend behind a proxy, this is *the proxy's IP*, not the user's.
2. **Header injection** — the proxy injects a header (`X-Forwarded-For`, `X-Real-IP`, `X-Forwarded`, `Forwarded`, `True-Client-IP`, `CF-Connecting-IP`, `Fastly-Client-IP`, etc.) carrying its claim about the original client.
3. **Backend interpretation** — the backend chooses to believe (or not) that header. *Whether that belief is sound depends entirely on whether the connection in step 1 came from a trusted proxy.*

The standard `X-Forwarded-For` chain grows left-to-right as a request traverses hops:

```
# Client → CDN → ALB → app server, what the app server sees:
GET / HTTP/1.1
Host: example.com
X-Forwarded-For: 203.0.113.42, 198.51.100.10, 198.51.100.20
X-Real-IP: 203.0.113.42
```

`203.0.113.42` is the leftmost — claimed to be the original client. `198.51.100.10` is the CDN. `198.51.100.20` is the ALB. The TCP source IP (what the kernel sees) is the ALB.

The standardized replacement, defined in **RFC 7239**, is the structured `Forwarded:` header:

```
Forwarded: for=203.0.113.42;proto=https;by=198.51.100.20
```

The bug is not in the chain. The bug is that **the leftmost IP is attacker-controllable**. If the client sent `X-Forwarded-For: 1.2.3.4` and the CDN appended its own value rather than overwriting, the chain is `1.2.3.4, <real-client>, <cdn>, <alb>` — and any backend that reads the leftmost entry now reads attacker input.

The rule: trust comes from the **network path** (step 1), not from the header (step 2). The header is data. The network path is the security boundary.

## Techniques / patterns

What attackers look at and how they probe:

- **Read the response and the logs.** If the app reflects `X-Forwarded-For` anywhere (debug pages, error messages, logs visible in admin) the attribution behavior is half-revealed for free.
- **Try the obvious values first.** `X-Forwarded-For: 127.0.0.1`, `X-Forwarded-For: 10.0.0.1`, `X-Forwarded-For: ::1`. Apps that whitelist "internal" IPs without verifying network path break immediately.
- **Try every header variant.** Many backends read multiple headers in priority order. Spoof them all: `X-Forwarded-For`, `X-Real-IP`, `X-Client-IP`, `True-Client-IP`, `X-Cluster-Client-IP`, `Forwarded`, `CF-Connecting-IP`, `Fastly-Client-IP`. The backend may read the one the proxy *doesn't* overwrite.
- **Probe the trust-hop count.** Send chains of varying length (`1.2.3.4`, then `1.2.3.4, 5.6.7.8`, then more) and observe which IP the app uses. This reveals whether it reads first-trusted-from-right (correct) or leftmost (broken).
- **Find direct backend reachability.** If the backend is exposed on a non-edge IP, *every* forwarded-header check is bypassable because the network path no longer originates from the proxy. See [[reverse-proxies]] §"Block direct backend reachability".
- **Test for cache-key inclusion.** A reflected `X-Forwarded-For` value in a cached response is a web-cache-poisoning primitive.

## Variants and bypasses

Forwarded-IP trust fails in **5 distinct ways**. Holding the taxonomy in working memory is enough to navigate any specific finding.

### 1. Trust-from-anywhere

Backend reads `X-Forwarded-For` and uses it without checking that the connection came from a proxy. Direct attacker → backend → spoofed IP wins.

This is the failure mode in default Express, default Flask, default Django, default Spring Boot — all require explicit "trust proxy" configuration to read forwarding headers safely, and many apps either misconfigure this or set it too permissively (`trust proxy: true` with no IP scoping).

### 2. Append-not-overwrite

Proxy preserves attacker-supplied `X-Forwarded-For` and appends its own observation: chain becomes `<attacker-supplied>, <real-client>, <cdn>`. Backends that read the leftmost entry get attacker input. This is the **default** behavior of many proxies (Nginx with `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for` appends; the safer config is to overwrite).

### 3. Header-name confusion

Backend reads `X-Real-IP` while the proxy only overwrites `X-Forwarded-For`. Or backend reads `True-Client-IP` (a Cloudflare/Akamai header) which the local Nginx never sanitizes. Or backend reads `Forwarded:` (RFC 7239) while the proxy only manipulates legacy headers. The attacker spoofs the unsanitized variant.

### 4. Position-trust

Backend reads the leftmost IP in the chain instead of the rightmost-trusted (or vice versa, in a flipped deployment). The correct algorithm is: **count back N hops from the right**, where N is the number of trusted proxies in front of the app. Most production bugs are the result of either reading position 0 (always attacker-controlled) or reading position -1 (always the proxy's own IP).

### 5. Loopback / RFC1918 magic

Backend trusts `X-Forwarded-For` *only* when the value is a private-range or loopback IP (`127.0.0.1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`). The attacker just sends `X-Forwarded-For: 127.0.0.1` and inherits "internal" trust. This pattern is depressingly common in admin allowlists.

## Impact

Ordered roughly by severity:

- **IP allowlist bypass** — admin panels, internal APIs, partner integrations exposed by spoofing a "trusted" source IP. Highest ceiling because allowlists frequently substitute for authentication.
- **Rate-limit bypass / abuse** — every spoofed IP is a fresh quota. Cleartext route to credential stuffing, content scraping, and SMS-bomb abuse.
- **Audit-log forgery / fraud attribution** — fraud team chases the wrong IP. Incident response derails.
- **Cache poisoning** — `X-Forwarded-For` reflected into a response that's keyed on URL alone. One bad request, many bad responses. See [[caching-and-security]].
- **Geo / license bypass** — content licensing, payment-region restrictions, sanctions compliance all collapse on a single spoofed header.
- **WAF blocklist evasion** — banned IP rotates `X-Forwarded-For` and reappears as a fresh client.
- **Internal-only endpoint reachability** — when "internal IP" trust grants access to debug endpoints, metrics, or management routes.

## Detection and defense

Ordered by effectiveness:

1.
**Anchor trust in the network path, not the header.**
   The backend must verify that the TCP source IP is a known proxy (CIDR allowlist) before reading any forwarding header. If the connection arrives from a non-proxy address, every `X-Forwarded-For`, `X-Real-IP`, `Forwarded:` is data, not identity. This single rule defeats the entire trust-disagreement class.

2.
**Configure the trusted-hop count explicitly.**
   Express `trust proxy: 1` (one trusted hop), Django `USE_X_FORWARDED_HOST = True` paired with `SECURE_PROXY_SSL_HEADER`, Spring `ForwardedHeaderFilter`, Rails `config.action_dispatch.trusted_proxies`. The right answer is *the count of proxies between the public internet and this process*, not `true`. Set it to a number, not a boolean.

3.
**Make the proxy overwrite, not append.**
   Edge proxy must replace the inbound `X-Forwarded-For` with the observed source IP (Nginx: `proxy_set_header X-Forwarded-For $remote_addr;` — note `$remote_addr`, not `$proxy_add_x_forwarded_for`). Same for `X-Real-IP`, `X-Forwarded-Host`, `Forwarded`. If you trust an upstream CDN, *that* CDN's overwrite policy is also part of your trust model — verify it.

4.
**Strip every variant you don't authoritatively own.**
   At the edge, drop or reset `True-Client-IP`, `X-Real-IP`, `Forwarded:`, `X-Cluster-Client-IP`, `X-Originating-IP`, `CF-Connecting-IP`, etc. unless you specifically generate them. Most header-name-confusion bugs come from "we sanitize XFF" and the backend quietly reads a sibling.

5.
**Prefer RFC 7239 `Forwarded:` end-to-end where you control both ends.**
   Structured (`for=...;proto=...;by=...`), parser-disagreement-resistant, and unambiguous about the direction of the chain. Legacy `X-Forwarded-For` lives forever, but new internal hops can start with `Forwarded:` and avoid two decades of compatibility quirks.

6.
**Log the network-source IP and the claimed header IP separately, always.**
   `client_ip` (what the framework decided) and `tcp_source_ip` (what the kernel saw). When forensics needs the truth, the kernel's value is the only one that matters. Most apps log only the framework-decided value, which is exactly the value an attacker controls.

7.
**Treat IP-based controls as defense-in-depth, never as primary auth.**
   Allowlists are useful as one layer of a multi-control admin path. They are not authentication. Pair them with mTLS, hardware-key SSO, or signed tokens — anything where forging the IP no longer suffices.

### What does not work as a primary defense

- **Trusting `X-Forwarded-For: 127.0.0.1` because "loopback is internal."** It isn't, when the value is in an HTTP header an attacker types. Loopback trust must come from the kernel's `lo` interface, not from a string.
- **Reading the leftmost entry of `X-Forwarded-For`.** That is always attacker-controlled in any chain that includes attacker input — which is every public deployment.
- **Reading the rightmost entry without a trusted-hop count.** That is always the previous proxy's IP — useful only if "previous proxy" is the public internet (i.e., your app is the edge), which contradicts the existence of the header.
- **Stripping `X-Forwarded-For` only on outbound responses.** The header is read on **inbound**, before any handler runs. Outbound stripping is too late.
- **Custom WAF rules that drop `X-Forwarded-For` containing private IPs.** Easy to evade with `X-Forwarded-For: 1.2.3.4, 127.0.0.1` (depending on which entry the backend reads) or by switching to a sibling header the WAF doesn't filter.
- **Assuming the CDN sanitizes for you.** Some do, some don't, some only sanitize the headers they themselves wrote. Read the CDN's docs *and* test the boundary; your assumption is your CVE.

## Practical labs

Concrete commands for building forwarded-header-trust intuition. Stock curl is enough for the basics.

### Read what the app thinks the client IP is

```
# Many apps reflect the perceived client IP on debug or error pages.
# httpbin (or any local tool that echoes the request) is the easiest practice target:
curl -s https://httpbin.org/get | jq '.origin, .headers'

# In a real engagement, look for:
#   - "Logged in from <IP>" notices on profile pages
#   - error messages quoting the requesting IP
#   - rate-limit response headers (X-RateLimit-* often expose what's keyed)
curl -sI https://example.com/login -o /dev/null -D - | grep -iE 'rate|limit|client'
```

### Test trust-from-anywhere

```
# Default test — does the app log or trust an attacker-supplied client IP?
curl -i https://example.com/admin -H "X-Forwarded-For: 127.0.0.1"
curl -i https://example.com/admin -H "X-Forwarded-For: 10.0.0.1"
curl -i https://example.com/admin -H "X-Real-IP: 127.0.0.1"

# A 200 (or different content) when the same path returns 403 without the header
# is direct evidence of trust-from-anywhere or loopback-magic.
```

### Test header-name confusion

```
# Spray every common forwarding header name; see which one the backend prefers.
for h in 'X-Forwarded-For' 'X-Real-IP' 'X-Client-IP' 'True-Client-IP' \
         'X-Originating-IP' 'X-Cluster-Client-IP' 'CF-Connecting-IP' \
         'Fastly-Client-IP' 'X-ProxyUser-Ip' 'Forwarded'; do
  printf '%-25s -> ' "$h"
  curl -sI "https://example.com/" -H "$h: 1.2.3.4" \
    -o /dev/null -w '%{http_code}\n'
done
```

### Probe the trust-hop count

```
# Send chains of increasing length; the value the app *uses* tells you which
# position it reads. Watch logs or response reflections to identify which one wins.
curl -sI https://example.com/ -H "X-Forwarded-For: 1.2.3.4"
curl -sI https://example.com/ -H "X-Forwarded-For: 1.2.3.4, 5.6.7.8"
curl -sI https://example.com/ -H "X-Forwarded-For: 1.2.3.4, 5.6.7.8, 9.10.11.12"

# Use RFC 7239 too — many apps read this without sanitizing it:
curl -sI https://example.com/ -H 'Forwarded: for=1.2.3.4;proto=https'
```

### Bypass an IP rate-limit

```
# If the app caps requests per IP and reads a forwarded header naively,
# rotating the header rotates the bucket:
for i in $(seq 1 200); do
  curl -s -o /dev/null -w '%{http_code}\n' \
    -H "X-Forwarded-For: 192.0.2.$((i % 254 + 1))" \
    https://example.com/api/login
done | sort | uniq -c
# A clean stream of 200s past the documented rate limit confirms the bypass.
```

### Confirm the backend rejects forwarded headers from non-proxy IPs

```
# Best test if you have access to the origin's IP directly. Spoof XFF over the
# direct path; a correctly configured backend should ignore the header entirely.
curl -k --resolve example.com:443:<origin-ip> https://example.com/whoami \
  -H "X-Forwarded-For: 1.2.3.4"
# If the response shows 1.2.3.4 as the client IP, the backend is reading
# forwarded headers from the public internet — full trust-disagreement bug.
```

## Practical examples

- An Express API runs `app.set('trust proxy', true)` (boolean, not count). Any client can spoof `X-Forwarded-For` and the framework treats them as the source. The rate-limiter middleware keys on `req.ip`; abuse becomes trivial.
- A Django admin allowlist permits `127.0.0.1` and `10.0.0.0/8`. The backend reads `request.META['HTTP_X_FORWARDED_FOR']` directly. Attacker sends `X-Forwarded-For: 10.0.0.5` from the public internet and reaches `/admin/`.
- A Cloudflare-fronted app reads `CF-Connecting-IP` for rate-limiting but never verifies the connection came from a Cloudflare IP range. Origin IP leaks via DNS history; attacker bypasses the rate limit by reaching the origin directly *and* spoofing `CF-Connecting-IP` to look fresh on every request.
- An Nginx proxy is configured with `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for` (the append default). Backend reads the leftmost IP. Attacker prepends `X-Forwarded-For: 1.2.3.4` and the chain reaches the app as `1.2.3.4, <real-client>` — backend logs `1.2.3.4`.
- A fraud-detection vendor keys risk scores on the request's source IP. The vendor reads `X-Forwarded-For` directly because "the client gave it to us." Attacker rotates the header to a clean range; risk score collapses.
- A CDN includes `X-Forwarded-For` in the cache key. Attacker reflects a payload via the header into a cacheable response and primes a per-IP cache entry that subsequent requests with the same forged value retrieve.

## Related notes

- [[reverse-proxies]] — the trust-disagreement class lives here; this note is its specific specialization for forwarded-IP headers.
- [[http-headers]] — header semantics, hop-by-hop vs end-to-end, header-name normalization quirks.
- [[http-messages]] — the wire format the proxy and backend each parse.
- [[load-balancers]] — same trust-translation surface; LBs typically inject `X-Forwarded-For` too.
- [[caching-and-security]] — XFF in cache keys becomes a poisoning primitive.
- [[firewalls-and-network-boundaries]] — the network-layer half of edge defense.
- [[api-rate-limiting|API Rate Limiting]] — the most common direct consumer of client-IP trust.
- [[business-logic-vulnerabilities|Business logic vulnerabilities]] — IP-based abuse controls are business logic; spoofing them is a logic flaw rooted in trust translation.
- [[test-client-ip-spoofing|Test Client IP Spoofing]]

### Suggested future atomic notes

- forwarded-header-spec
- trust-proxy-configuration
- origin-ip-discovery
- ip-allowlist-design
- ipv6-forwarding-quirks
- bgp-route-hijack-and-source-ip

## References

- **Foundational:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning
