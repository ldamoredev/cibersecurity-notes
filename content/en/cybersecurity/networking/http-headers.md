---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# HTTP Headers

## Definition

HTTP headers are named metadata fields on requests and responses that tell clients, servers, proxies, caches, and browsers how to interpret the message. They carry routing, identity, state, content, caching, and browser-policy signals.

## Why it matters

Headers are the steering layer of HTTP security. The body may carry the business data, but headers decide who the request appears to be from, which host/path/protocol the backend believes was used, whether a response can be cached, whether a browser may expose a cross-origin response, and how content should be interpreted.

The recurring lesson: **headers are not neutral metadata**. They are inputs to multiple independent parsers and policy engines.

This note owns header semantics. [[http-messages]] owns raw message framing; [[client-ip-trust]] owns forwarded-IP trust; [[cookies-and-sessions]] owns `Set-Cookie` / `Cookie` state; [[caching-and-security]] owns cache-key behavior.

## How it works

Every header has three properties that matter for security:

1. **Direction.** Request headers go client/proxy → server. Response headers go server/proxy → client. Some are valid in both directions but mean different things.
2. **Scope.** End-to-end headers are intended for the final recipient; hop-by-hop headers apply only to a single connection and should not be forwarded past that hop.
3. **Interpreter.** A browser, CDN, WAF, reverse proxy, framework, cache, or application may each read the same header differently.

Example request and response:

```
GET /account HTTP/1.1
Host: app.example.com
Cookie: __Host-session=9f2a...
Authorization: Bearer eyJ...
X-Forwarded-For: 203.0.113.42
Origin: https://app.example.com
Accept: text/html
```

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: no-store
Set-Cookie: __Host-session=9f2a...; Path=/; Secure; HttpOnly; SameSite=Lax
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; frame-ancestors 'none'
```

The same bytes carry at least five security meanings: identity, state, routing, cache behavior, and browser policy.

The bug usually lives where one component treats a header as authoritative even though another component can supply, transform, omit, duplicate, or ignore it.

## Techniques / patterns

Attackers and defenders inspect:

- **routing headers:** `Host`, `X-Forwarded-Host`, `Forwarded`, `X-Original-URL`, `X-Rewrite-URL`
- **identity headers:** `Authorization`, `Cookie`, `X-Forwarded-For`, `X-Real-IP`, `True-Client-IP`
- **state headers:** `Set-Cookie`, `Cookie`, cache validators, CSRF-adjacent `Origin` / `Referer`
- **content interpretation:** `Content-Type`, `Content-Length`, `Transfer-Encoding`, `Content-Encoding`, `Accept`
- **browser policy:** `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `Referrer-Policy`, CORS headers
- **cache behavior:** `Cache-Control`, `Vary`, `ETag`, `Age`, `Surrogate-Control`, CDN-specific cache status headers
- **normalization quirks:** duplicate headers, case differences, whitespace, comma-joined values, proxy-added vs client-supplied variants

## Variants and bypasses

HTTP header security failures fall into **6 semantic classes**. This taxonomy is more useful than memorizing individual header names.

### 1. Identity and authorization headers

`Cookie` and `Authorization` prove application identity only if the server validates them correctly. Forwarded identity headers such as `X-Forwarded-For` prove nothing unless the network path is trusted. Duplicate or conflicting auth headers can produce proxy/backend disagreement.

### 2. Routing and origin headers

`Host`, `Forwarded`, `X-Forwarded-Host`, `X-Forwarded-Proto`, and rewrite headers influence URL generation, virtual-host routing, password-reset links, and internal redirect behavior. If the backend trusts attacker-supplied routing headers, host-header injection and proxy-bypass bugs follow.

### 3. State and cookie headers

`Set-Cookie` and `Cookie` are special because browsers store and replay them automatically. Their security depends on attributes, scope, prefix rules, and transport. [[cookies-and-sessions]] owns the full depth.

### 4. Content interpretation headers

`Content-Type`, `Content-Encoding`, `Content-Length`, and `Transfer-Encoding` tell parsers how to read bytes. Disagreement here leads to XSS via MIME confusion, request smuggling via body framing, upload validation gaps, and broken API parsing.

### 5. Cache-control headers

`Cache-Control`, `Vary`, `ETag`, and CDN-specific headers decide whether one user's response can become another user's response. Any header the origin reads but the cache does not key on is a candidate cache-poisoning input.

### 6. Browser-policy headers

CSP, HSTS, CORS, `X-Frame-Options`, `Permissions-Policy`, and `Referrer-Policy` shape what browsers allow. These headers reduce exploitability when correct but are often misunderstood as replacements for server-side validation or authorization.

## Impact

Ordered roughly by severity:

- **Authentication or authorization bypass.** Conflicting `Authorization`, trusted forwarded headers, or routing headers can make the backend believe a request came from a privileged path or identity.
- **Request smuggling and parser confusion.** `Content-Length`, `Transfer-Encoding`, duplicate headers, and whitespace quirks can make two components parse different requests.
- **Cache poisoning / sensitive cache leaks.** Missing `Cache-Control`, weak `Vary`, or unkeyed headers can expose personalized or attacker-controlled content.
- **XSS impact amplification.** Missing CSP, wrong `Content-Type`, or sniffable responses widen client-side execution paths.
- **CSRF and cross-origin data exposure.** Weak `SameSite`, permissive CORS, or bad `Origin` handling lets browser context do too much.
- **Trust-boundary confusion.** Proxy-injected headers become indistinguishable from client-supplied headers unless overwritten and validated at the boundary.

## Detection and defense

Ordered by effectiveness:

1.
**Define which component owns each security-relevant header.**
   The edge should own forwarding, protocol, and client-IP headers. The application should own auth/session validation and business authorization. Browser-policy headers should be emitted deliberately by the app or edge, not accidentally by framework defaults. Ownership prevents two components from silently accepting conflicting signals.

2.
**Overwrite untrusted inbound headers at trust boundaries.**
   Reverse proxies must overwrite, not append or preserve, `X-Forwarded-*`, `Forwarded`, and related identity/routing headers. Backends should trust those headers only from known proxy source ranges. This removes the common "attacker supplied a header the app thought only the proxy could set" failure.

3.
**Reject malformed, ambiguous, and duplicate critical headers.**
   Fail closed on duplicate `Host`, conflicting `Content-Length` / `Transfer-Encoding`, invalid line endings, whitespace-padded header names, and duplicate auth headers. Ambiguity is where parser disagreement lives.

4.
**Emit explicit cache policy for sensitive responses.**
   Use `Cache-Control: no-store` for authenticated pages and sensitive API responses. When caching public variants, make `Vary` match every request header that changes the response. Caches cannot protect data they were not told is private.

5.
**Set browser-policy headers as defense-in-depth.**
   HSTS, CSP, `frame-ancestors` or `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` reduce exploitability in browsers. They belong after server-side correctness because they constrain clients rather than fixing broken authorization.

6.
**Normalize and log the interpreted value, not only the raw header.**
   Logs should record both raw signals where useful and the value the application actually used: perceived client IP, selected host, auth scheme, content type, cache status. This makes proxy/backend disagreement visible during testing and incidents.

### What does not work as a primary defense

- **Adding security headers while leaving server-side bugs intact.** CSP does not fix XSS sinks, CORS does not authorize users, HSTS does not make origin HTTP safe, and `X-Frame-Options` does not protect state-changing endpoints.
- **Trusting a header because "the browser sets it."** `Origin`, `Referer`, `User-Agent`, and most request headers can be absent, forged by non-browser clients, or transformed by proxies. Treat them as signals with constraints, not ground truth.
- **Blocklisting bad header names.** Attackers use variants: different case, duplicate headers, legacy names, `Forwarded` vs `X-Forwarded-*`, whitespace, comma-joined lists, and framework-specific aliases.
- **Assuming the framework sees what the edge saw.** CDNs, WAFs, proxies, and load balancers normalize headers before the application reads them. Test the full chain.
- **Relying on response headers for secrets.** Headers are visible to clients and often logs/proxies. Do not put bearer secrets or sensitive internal details in custom headers.

## Practical labs

Run these against systems you own or are authorized to test. Stock `curl`, `openssl`, `nc`, and `rg` cover the basics.

### Inventory response security headers

```
curl -skI https://app.example.com/ | rg -i \
  '^(strict-transport-security|content-security-policy|x-frame-options|frame-options|referrer-policy|permissions-policy|cache-control|vary|content-type|set-cookie):'
```

Look for missing HSTS on HTTPS sites, missing or weak CSP, absent frame protection, cacheable authenticated pages, and cookie attributes.

### Compare public and authenticated cache headers

```
# Public page
curl -skI https://app.example.com/ | rg -i '^(cache-control|vary|etag|age|x-cache|cf-cache-status):'

# Authenticated page with a cookie jar
curl -sk -b /tmp/app.cookies -I https://app.example.com/account | \
  rg -i '^(cache-control|vary|etag|age|x-cache|cf-cache-status):'
```

Expected: authenticated or personalized responses should not be stored by shared caches.

### Probe host and forwarded-host handling

```
curl -skI https://app.example.com/reset \
  -H 'Host: evil.example' \
  -H 'X-Forwarded-Host: evil.example' \
  -H 'X-Forwarded-Proto: http'
```

Watch redirects, absolute URLs, password-reset links in test accounts, and generated canonical links. A backend that reflects attacker-controlled host/proto has a routing-trust bug.

### Probe client-IP header trust

```
curl -skI https://app.example.com/admin \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'X-Real-IP: 127.0.0.1' \
  -H 'Forwarded: for=127.0.0.1;proto=https;host=app.example.com'
```

A status, content, rate-limit bucket, or log change means the backend may trust client-supplied forwarding headers. See [[client-ip-trust]] for the deeper workflow.

### Probe duplicate critical headers

```
# Duplicate Host through raw HTTP.
printf 'GET / HTTP/1.1\r\nHost: app.example.com\r\nHost: evil.example\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect app.example.com:443 -servername app.example.com 2>/dev/null

# Duplicate Authorization through curl.
curl -skI https://app.example.com/api/me \
  -H 'Authorization: Bearer valid-test-token' \
  -H 'Authorization: Bearer invalid-test-token'
```

Expected: critical duplicates should be rejected or handled consistently by every hop.

### Inspect exact request/response header bytes

```
curl -sk --trace-ascii /tmp/headers.trace https://app.example.com/login \
  -H 'X-Debug-Probe: header-lab' >/dev/null

rg -n '=> Send header|<= Recv header|X-Debug-Probe|Set-Cookie|Cache-Control' /tmp/headers.trace
```

This shows what curl actually sent and what the server actually returned, without browser UI abstraction.

## Practical examples

- A backend builds password-reset URLs from `X-Forwarded-Host`; an attacker injects their domain and captures reset tokens.
- A CDN keys only on URL while the origin varies output by `X-Forwarded-Host`, creating web cache poisoning.
- A WAF rejects `Transfer-Encoding: chunked`, but the backend accepts `Transfer-Encoding:  chunked` with extra whitespace.
- An API accepts two `Authorization` headers; the proxy validates one while the app reads the other.
- A site sets CSP on HTML pages but leaves JSON or file-preview endpoints with wrong `Content-Type`, enabling browser interpretation bugs.
- A response includes `Access-Control-Allow-Origin: *` with credentialed behavior elsewhere, revealing that CORS policy is not centrally owned.

## Related notes

- [[http-overview]] — protocol lifecycle and version-level behavior.
- [[http-messages]] — raw message framing, duplicate headers, and parser ambiguity.
- [[cookies-and-sessions]] — `Set-Cookie` and `Cookie` state semantics.
- [[client-ip-trust]] — forwarded-IP identity headers.
- [[reverse-proxies]] — where forwarding, normalization, and trust headers are usually introduced.
- [[caching-and-security]] — `Cache-Control`, `Vary`, and cache-key consequences.
- [[tls-https]] — HSTS and transport guarantees.
- [[cors-misconfiguration|CORS Misconfiguration]] — `Origin` and CORS response headers.
- [[xss|XSS]] — CSP and content-type constraints.
- [[csrf|CSRF]] — `Origin`, `Referer`, and cookie behavior.
- [[test-cors-behavior|Test CORS Behavior]]
- [[test-client-ip-spoofing|Test Client IP Spoofing]]

### Suggested future atomic notes

- host-header-injection
- security-response-headers
- content-type-sniffing
- duplicate-header-resolution
- forwarded-header-spec
- cache-control-semantics
- permissions-policy

## References

- **Foundational:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Foundational:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Mitigation:** OWASP HTTP Headers Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
