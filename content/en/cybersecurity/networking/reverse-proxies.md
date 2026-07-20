---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reverse Proxies

## Definition

A reverse proxy is an HTTP intermediary that accepts requests on behalf of one or more backend services, applies a fixed set of transformations, and forwards the result to the backend it picks. The defining property is not "it balances load" — load balancing is one transformation. The defining property is that **the proxy and the backend each parse the request independently**, which makes the proxy a trust boundary every time their interpretations differ.

Examples: Nginx, Envoy, HAProxy, Apache (mod_proxy), AWS ALB / CloudFront, Cloudflare, Akamai, Fastly, Kubernetes Ingress controllers, API gateways.

## Why it matters

Reverse proxies are the single most consequential trust boundary in modern HTTP-facing systems. They matter because:

- **They are usually the TLS termination point.** Whatever the proxy decides about a request, the backend sees as plaintext — including any headers the proxy injected.
- **They are a second parser on the same wire.** Every disagreement between proxy parser and backend parser is a candidate vulnerability.
- **They carry forwarded identity.** The backend's idea of "who the client is" almost always comes from a header the proxy injected. If the proxy does not strip the same header on inbound, attackers forge identity.
- **They normalize requests in ways the backend forgets about.** Path collapsing, header case folding, whitespace handling, query parameter merging — each is a chance for the proxy and backend to see a different request.
- **They cache.** Cached responses are shared across users. A proxy that caches the wrong key turns one user's leak into a public disclosure.

The recurring lesson: **a reverse proxy is a security boundary by accident**, because two independent parsers handle the same bytes and the operator rarely audits the diff.

## How it works

A reverse proxy applies five transformations on every request. Knowing all five lets you predict where the proxy and backend will disagree.

1. **TLS termination** — accepts HTTPS from the client, opens HTTP (or re-encrypted HTTPS) to the backend. The backend sees plaintext and trusts it.
2. **Header rewriting** — injects identity and routing headers (`X-Forwarded-For`, `X-Forwarded-Proto`, `X-Real-IP`, `X-Forwarded-Host`, `Forwarded`, `Via`), strips hop-by-hop headers (`Connection`, `Keep-Alive`, `Transfer-Encoding`), may rewrite `Host`.
3. **Path / host rewriting** — `/api/v1/users` at the edge becomes `/users` at the backend; `Host: app.example.com` may be replaced or preserved depending on config.
4. **Request normalization and buffering** — collapses `//` to `/`, decodes percent-encoded paths, may buffer the full request body before forwarding, may re-chunk or de-chunk transfer-encoded bodies.
5. **Response caching** — keyed by URL + a (configurable) subset of headers, served to *any* future client whose request hashes to the same key.

A request before and after the proxy, illustrating header injection and TLS termination:

```
# What the client sends over TLS
GET /admin HTTP/1.1
Host: app.example.com
Cookie: session=abc123
User-Agent: curl/8

# What the backend receives over plaintext HTTP
GET /admin HTTP/1.1
Host: app.example.com
Cookie: session=abc123
User-Agent: curl/8
X-Forwarded-For: 203.0.113.42
X-Forwarded-Proto: https
X-Real-IP: 203.0.113.42
Via: 1.1 nginx
```

The backend now believes the client is `203.0.113.42`. If the backend does **not** verify that this header arrived from the proxy (and not from a direct attacker who reached it on a non-edge port), the trust translation is broken.

The bug is not the proxy. The bug is the unaudited difference between what the proxy intends to communicate and what the backend chooses to believe.

## Techniques / patterns

What attackers look at and how they probe:

- **Fingerprint the proxy.** `Server`, `Via`, `X-Cache`, `X-Amz-Cf-Id`, `CF-Ray`, `X-Served-By` headers, error page styles, TLS handshake quirks, default 404 bodies.
- **Find direct backend reachability.** If the backend is exposed on a non-edge IP/port (cloud security-group misconfigure, leaked origin in DNS history, second hostname pointing at the same IP), every proxy-enforced control is bypassed.
- **Probe header trust.** Send `X-Forwarded-For: 127.0.0.1` from the public internet — does the app log it as the source IP, or trust it for an allowlist? Same for `X-Original-URL`, `X-Rewrite-URL`, `X-Forwarded-Host`.
- **Probe parser disagreement.** Ambiguous `Content-Length` + `Transfer-Encoding`, malformed chunked encoding, header-name case games, duplicated headers, whitespace-padded values. See [[request-smuggling]] for the full desync taxonomy.
- **Probe normalization disagreement.** `//admin`, `/admin/.`, `/admin%2F`, `/admin;jsessionid=x`, `/admin?` — does the proxy and backend agree on what path was requested? Differences become access-control bypasses.
- **Probe cache key.** Add unkeyed headers (`X-Forwarded-Host`, `User-Agent`, `Accept-Language`) and look for poisoning surface. See [[caching-and-security]].

## Variants and bypasses

Reverse-proxy security failures fall into **3 disagreement classes**. Holding this taxonomy in working memory is enough to navigate any specific finding.

### 1. Parser disagreement

The proxy and backend disagree on **where the request ends or what bytes belong to it**. Canonical example: `Content-Length` vs `Transfer-Encoding: chunked` mismatch yields request smuggling (CL.TE, TE.CL, TE.TE families). Header-line-folding quirks, NUL bytes, duplicate headers, and HTTP/2 → HTTP/1.1 downgrade all live here.

Impact ceiling: poison the request queue, hijack other users' requests, reach hidden endpoints, bypass edge auth.

Owns the depth: [[request-smuggling]].

### 2. Normalization disagreement

The proxy and backend disagree on **what request was made**, even though they agree on the bytes. Path collapsing, percent-encoding behavior, semicolon parameter handling, host header treatment, trailing-dot hostnames, case sensitivity. Example: edge enforces `/admin` is forbidden; backend treats `/admin/.` as `/admin/` and serves it.

Impact ceiling: access-control bypass, web cache poisoning (different normalization → different cache key → response served to wrong user), host-header injection.

### 3. Trust disagreement

The proxy and backend disagree on **what to believe about the request's identity or transport**. Backend trusts `X-Forwarded-For` from any source because the proxy is supposed to overwrite it; attacker reaches the backend directly (or through a misconfigured proxy that appends rather than overwrites) and forges identity. Same shape: `X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Original-URL`, `X-Rewritten-URL`, `True-Client-IP`.

Impact ceiling: rate-limit bypass, log forgery, allowlist bypass, IP-based authentication bypass, internal-only endpoint reachability.

Owns the depth: [[client-ip-trust]].

## Impact

Ordered roughly by severity:

- **Request smuggling RCE / auth bypass** — parser-disagreement family. Highest ceiling; affects every user behind the proxy on the same connection.
- **Cache poisoning** — normalization-disagreement family. One bad request becomes many bad responses to other users.
- **Direct backend reachability** — every proxy-enforced control becomes optional. WAF rules, edge auth, rate limiting, geo-blocking, all bypassed.
- **Forwarded-header forgery** — trust-disagreement family. Spoofed source IP for rate-limit bypass, log spoofing, allowlist bypass.
- **Hidden admin path access** — normalization or routing disagreement reaches a path the proxy thinks is blocked.
- **Host-header attacks** — `Host:` or `X-Forwarded-Host:` reaches the backend unfiltered, redirecting password-reset emails, poisoning generated URLs, or routing to a virtual host the proxy did not intend.
- **TLS demotion** — backend believes the request was HTTPS because of `X-Forwarded-Proto: https`, when in fact a misconfigured proxy forwarded plaintext.

## Detection and defense

Ordered by effectiveness:

1.
**Make the trust boundary explicit and one-way.**
   The proxy must always overwrite identity headers (`X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Proto`, `X-Forwarded-Host`) on inbound — never append, never preserve. The backend must only trust those headers when the connection arrived from the proxy's IP range. Without both halves, trust translation is forgeable. Most production breakages are because one half is correct in isolation and silently wrong as a pair.

2.
**Reject ambiguous requests at the edge.**
   Drop requests that contain both `Content-Length` and `Transfer-Encoding`, malformed chunked encoding, header-name whitespace, duplicate `Host` headers, or non-conforming line endings. The edge is the canonical parser; if it cannot canonicalize the message, it must fail closed. This cuts off the parser-disagreement family at the source.

3.
**Align proxy and backend behavior.**
   Use the same web server family and version on both sides where feasible, or at least audit the diff. Most desync findings come from one side being more permissive than the other on the same input. This is the reason "Nginx in front of Apache" has a long history of CVEs — the parsers were never designed to agree.

4.
**Make the cache key explicit.**
   Audit which request headers participate in the cache key. Treat any header the backend reads but the cache does not include as a poisoning candidate. Disable caching for authenticated responses entirely unless `Vary` correctly reflects every relevant header.

5.
**Block direct backend reachability.**
   Cloud security groups should accept inbound only from the proxy's source range. DNS history scanners (e.g., Censys, SecurityTrails) routinely find the origin IP — assume attackers will too. Mutual TLS between proxy and backend is the strongest version of this control.

6.
**Map the full chain.**
   CDN → WAF → load balancer → ingress controller → app server. Every hop is a parser. Every hop is a trust boundary. Every hop has its own normalization rules. Document them; rehearse what each one strips, injects, rewrites, and caches.

7.
**Monitor for desync indicators.**
   Watch for: requests attributed to the wrong user, unexpected `400 Bad Request` clusters from the backend, cache entries with mismatched keys, connection-reuse anomalies on keep-alive, sudden spikes in `X-Forwarded-For` values that match RFC1918 from the public internet.

### What does not work as a primary defense

- **WAF rules alone.** WAFs catch known smuggling payloads and known XSS; they do not catch novel parser disagreements, novel normalization games, or trust-header forgery from inside the trusted IP range.
- **Trusting `X-Forwarded-For` because "only the proxy can set it."** The proxy can *also* set it, but so can anyone who reaches the backend's IP directly. The trust comes from the network path, not from the header's existence.
- **Stripping `X-Forwarded-For` only on outbound.** The header has to be overwritten on **inbound**, before reaching any backend that might read it. Outbound stripping is too late.
- **Assuming HTTPS at the edge means HTTPS at the backend.** TLS termination by default produces a plaintext hop. Encrypt that hop too if the backend handles credentials, or at least authenticate it (mTLS) so a network attacker cannot inject requests that look proxy-originated.
- **One-time pen-test.** The proxy and backend versions drift. A clean smuggling test today is meaningless after the next Nginx point release.

## Practical labs

Concrete commands you can run to build proxy-parser intuition. None of these require lab software beyond curl, nc, dig, and openssl.

### Fingerprint what's in front of the app

```
# Look for proxy-fingerprint headers in a normal response
curl -sI https://example.com | grep -iE 'server|via|x-cache|x-amz-cf-id|cf-ray|x-served-by'

# TLS handshake reveals the edge identity (ALPN, cert SANs, JA3)
openssl s_client -connect example.com:443 -servername example.com -alpn h2,http/1.1 </dev/null 2>/dev/null | head -30

# Compare the public hostname's IP set against the apex — extra A records often reveal origin
dig +short example.com
dig +short origin.example.com
dig +short www.example.com
```

### Probe forwarded-header trust

```
# Does the app log or trust an attacker-supplied client IP?
curl -sI https://example.com/ -H "X-Forwarded-For: 127.0.0.1"
curl -sI https://example.com/ -H "X-Real-IP: 127.0.0.1"
curl -sI https://example.com/admin -H "X-Forwarded-For: 10.0.0.1"

# Cache poisoning probe — does an unkeyed header reflect into the response?
curl -sI https://example.com/ -H "X-Forwarded-Host: evil.example"
```

### Probe normalization disagreement

```
# Path normalization games — does /admin/. or /admin%2F reach a "blocked" backend route?
for path in /admin /admin/ /admin/. //admin /admin%2F /admin%252F /./admin /admin?; do
  printf '%-25s -> %s\n' "$path" "$(curl -so /dev/null -w '%{http_code}' "https://example.com$path")"
done

# Host header injection — does the app generate URLs from the Host header?
curl -sI https://example.com/password-reset -H "Host: evil.example"
```

### Probe parser disagreement (smuggling)

```
# Send raw HTTP — curl is too well-behaved for this. Use printf + nc / openssl s_client.
# First confirm reachability and observe the proxy's normalization:
printf 'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n' \
  | openssl s_client -quiet -connect example.com:443 -servername example.com

# For real smuggling probes, use PortSwigger's HTTP Request Smuggler (Burp extension)
# or smuggler.py — see <a href="../web-security/request-smuggling.html">request-smuggling</a> for the full attack methodology.
```

### Confirm direct backend reachability is blocked

```
# If you find an origin IP via DNS history or certificate transparency,
# verify the security group blocks direct access:
curl -k --resolve example.com:443:<origin-ip> https://example.com/ -I
# A timeout or RST is the desired outcome. A 200 response means the proxy is bypassable.
```

## Practical examples

- A SaaS app trusts `X-Forwarded-For` from any source. Attacker sends `X-Forwarded-For: 127.0.0.1` to bypass an "internal-only" admin route.
- An Nginx edge in front of a Node backend disagrees on `Content-Length` vs `Transfer-Encoding`. Smuggled requests poison the keep-alive queue and hijack the next user's session cookie.
- A CDN caches `/profile` keyed only on the URL. Backend personalizes the response based on the `Cookie` header. Attacker triggers a cache fill while logged in; subsequent unauthenticated requests get the cached personalized response.
- A WAF strips `<script>` from request bodies but the backend interprets the body again after a `multipart/form-data` re-parse, recovering the payload — normalization disagreement.
- A Kubernetes ingress controller forwards `Host: evil.example` unmodified. The backend uses the Host header to build a password-reset URL. Reset emails point at the attacker's domain.
- A leaked origin IP in historical DNS records lets an attacker reach the EC2 instance directly, bypassing the Cloudflare WAF and rate limiter entirely.

## Related notes

- [[http-messages]] — the wire format every proxy parses.
- [[http-headers]] — header semantics, hop-by-hop vs end-to-end, forwarding headers.
- [[client-ip-trust]] — owns the depth on `X-Forwarded-For` and the trust-disagreement class.
- [[load-balancers]] — overlapping concept; reverse proxies focus on HTTP interpretation, load balancers on traffic distribution.
- [[firewalls-and-network-boundaries]] — the network-layer half of edge defense.
- [[caching-and-security]] — owns the depth on cache-key reasoning and poisoning.
- [[tls-https]] — TLS termination details and HSTS interaction.
- [[request-smuggling|Request smuggling]] — owns the depth on the parser-disagreement class.
- [[ssrf|SSRF]] — internal reachability becomes more dangerous when the backend is directly addressable.
- [[reverse-proxy-misconfig-checklist|Reverse Proxy Misconfig Checklist]]

### Suggested future atomic notes

- host-header-injection
- [[web-cache-poisoning]]
- origin-ip-discovery
- mtls-between-proxy-and-backend
- http2-downgrade-desync
- forwarded-header-spec

## References

- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
