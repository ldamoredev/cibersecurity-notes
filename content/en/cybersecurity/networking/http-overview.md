---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# HTTP Overview

## Definition

HTTP (Hypertext Transfer Protocol) is the request/response application protocol that carries the overwhelming majority of web and API traffic. Wire format is text-based in HTTP/1.x and binary-framed in HTTP/2 and HTTP/3. The protocol does not enforce semantics — it transports them. Every web vulnerability ultimately presents as an HTTP transaction whose parts were parsed, trusted, or routed in a way the designer did not intend.

## Why it matters

HTTP is the substrate every web-security and api-security finding sits on top of. It matters because:

- **Every web exploit is an HTTP transaction.** XSS, SQLi, CSRF, SSRF, IDOR, smuggling, deserialization — all are vulnerabilities in how an HTTP request's parts get bound to backend behavior.
- **State lives in headers.** Auth, sessions, cookies, CORS, CSP, cache directives, forwarded identity — every one is a header attached to an HTTP transaction.
- **Trust boundaries live at parser seams.** Reverse-proxy translation, request smuggling, cache poisoning all live where two HTTP parsers disagree on the same bytes.
- **It is the meta-skill.** Without an HTTP model the reader can hold in working memory, every higher-level note becomes pattern matching without understanding.

This note stays at the protocol-model level. [[http-messages]] owns the depth on the wire format and parser framing rules. [[http-headers]] owns the depth on which header fields actually steer security behavior.

## How it works

An HTTP transaction has **5 stages**. Each stage is a trust boundary; each can be tampered with or misinterpreted independently.

1. **Resolve target** — client looks up the host (DNS) and chooses a port (default 80 for HTTP, 443 for HTTPS). DNS hijacks land here. See [[dns-resolution]].
2. **Establish transport** — TCP three-way handshake; TLS handshake if HTTPS; the connection may be reused for many requests (keep-alive in HTTP/1.1, multiplexed streams in HTTP/2/3). MITM and downgrade attacks land here.
3. **Send request** — method + URI + version + headers + (optional) body. The wire bytes are exactly what the next hop parses.
4. **Server processes** — parse, route, authorize, execute, render. *Each step is independently forgeable from the request bytes.* Most application vulnerabilities live in this stage.
5. **Return response** — status code + headers + (optional) body. Connection may persist or close.

A minimal HTTP/1.1 request:

```
GET /users/42 HTTP/1.1
Host: api.example.com
Accept: application/json
Cookie: session=abc123
```

A minimal response:

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 27
Cache-Control: private

{"id":42,"name":"Carlos"}
```

Every HTTP request carries **4 trust-relevant signals**. Treat each as forgeable until verified:

- **Identity** — `Cookie`, `Authorization`, client certificates, mTLS. *What the client claims to be.*
- **Intent** — method + URI. *What the client wants done, on what.*
- **Context / state** — `Host`, `Origin`, `Referer`, `X-Forwarded-*`, `User-Agent`. *Browser and proxy claims about the environment.*
- **Payload** — the body bytes, interpreted per `Content-Type`.

The bug is rarely in HTTP itself. The bug is in **which signal the backend trusts and how that trust travels across hops**.

## Techniques / patterns

What testers look at and how they probe:

- **Always read the response headers, not just the body.** `Server`, `Via`, `X-Cache`, `Content-Type`, `Content-Security-Policy`, `Set-Cookie` flags reveal the stack and its security posture before any vuln-specific test.
- **Status codes leak architecture.** 401 vs 403 vs 404 leak about authentication-vs-authorization layering and resource enumeration. 500 with a stack trace leaks framework version. 502/504 patterns reveal proxy boundaries.
- **Establish the protocol version first.** ALPN/TLS handshake reveals h2/h3 support. Behavior — and attack surface — diverges materially between 1.1, 2, and 3.
- **Read the wire, not the framework.** Frameworks normalize, hide, and lie. `curl -v --trace-ascii -` and `openssl s_client` are the only ground truth.
- **Look for forgotten endpoints.** `OPTIONS *`, `TRACE`, `PROPFIND`, `/.well-known/`, `/debug/`, `/metrics` — the HTTP method/URI surface is wider than the documented API.

## Variants and bypasses

The protocol has **4 deployed versions**, each with security-relevant differences. Knowing which version each hop in the chain speaks is the first step in any production analysis.

### HTTP/1.0

Connection-per-request by default. No `Host` header required (multi-hosting impossible). Mostly historical, but still appears on legacy services and some CLI tools. Worth recognizing on the wire because it eliminates the whole virtual-host-confusion family.

### HTTP/1.1

Text-based wire format, CRLF line endings, persistent connections (keep-alive) by default. Pipelining was specified but mostly disabled in practice. **Body framing via `Content-Length` *or* `Transfer-Encoding: chunked`** — this either-or is the source of the entire request-smuggling vulnerability class. See [[http-messages]] and [[request-smuggling]].

### HTTP/2

Binary framing over TCP+TLS. Multiplexed streams over a single connection. Header compression (HPACK). Length-prefixed frames eliminate textual ambiguity, which kills most smuggling at the front-end. **HTTP/2 → HTTP/1.1 downgrade between proxy and origin reintroduces the full smuggling surface** — the proxy speaks h2 to the client and h1 to the backend, and the translation layer becomes a parser-mismatch hotspot.

### HTTP/3

Binary framing over QUIC, which is over UDP. Native TLS 1.3. Connection migration: connection identity is no longer a `(src-IP, src-port, dst-IP, dst-port)` 4-tuple, which complicates source-IP-based controls (rate limiting, IP allowlists). UDP firewalling rules differ from TCP rules — a deployment that filtered HTTP/1.1 cleanly may be wide open on h3.

## Impact

HTTP misunderstanding is **meta-impactful** — it amplifies every other vulnerability class:

- Misunderstanding `Host` enables host-header injection (password-reset URL poisoning, virtual-host confusion).
- Misunderstanding `Content-Type` enables type-confusion bugs at deserialization or upload.
- Misunderstanding `Cache-Control` and `Vary` enables cache poisoning and cache deception.
- Misunderstanding TLS termination enables credential leakage to a plaintext backend hop.
- Misunderstanding connection reuse enables request smuggling.
- Misunderstanding redirects (`Location` header semantics) enables open-redirect and OAuth-flow theft.
- Misunderstanding `Origin` vs `Referer` enables CORS misconfigurations and CSRF.
- Misunderstanding HTTP method idempotency lets `GET` change state and become both CSRF-able and accidentally cacheable.

## Detection and defense

The defenses here are *operating-posture* defenses — generic guidance that makes the application-layer vulnerabilities tractable. Specific vuln-class defenses live in their own notes.

1.
**Read your own protocol on the wire.**
   `curl -v` your production traffic. Make sure the requests and responses you think you send are the ones actually on the wire. Frameworks abstract HTTP; that abstraction is exactly what makes wire-level vulnerabilities invisible from inside the codebase.

2.
**Treat every header as untrusted client data unless verified by network path.**
   This is the only durable rule for trust translation. Not "we sanitize XFF" — *the connection has to come from a known proxy IP*, and only then is the header data informative. See [[client-ip-trust]] for the full version.

3.
**Specify `Content-Type`, `Content-Length`, `Cache-Control`, and `Vary` explicitly.**
   Defaults vary by framework, by version, and by middleware. Ambiguity is attack surface — both for parser confusion and for cache key confusion.

4.
**Prefer HTTP/2 or HTTP/3 end-to-end where you control both ends.**
   Length-prefixed framing eliminates the largest single class of HTTP/1.1 vulnerabilities (smuggling, header-line games). The h2 → h1 downgrade hop is the failure mode to watch for; mTLS-to-origin with h2 throughout is the strongest posture.

5.
**Match parser behavior across hops.**
   Same web-server family and version on both sides where feasible. Most desync findings come from one side being more permissive than the other on the same input. See [[reverse-proxies]] for the long version.

6.
**Log the wire — version, method, URI, status, length — at every hop.**
   When something goes wrong, the wire is the only ground truth. Framework-level log lines are the value the framework chose to show you, not what the parser saw.

### What does not work as a primary defense

- **"We use HTTPS."** TLS protects the bytes in flight. It does not protect the parsing semantics on either end. Smuggling, cache poisoning, header-trust forgery, and Host-header attacks all happen *inside* an HTTPS session.
- **Reading framework abstractions instead of the actual wire.** Framework `request.headers` objects are a *view* of the wire, post-normalization. Whatever the wire said and the framework hid is exactly the attack surface.
- **WAF rules tuned for HTTP/1.1 in front of an h2 backend.** Different framing means different rules; a WAF that pattern-matches text-line CRLF is blind to h2 frame headers.
- **Trusting that "modern frameworks default to safe."** Every default is one config flag away from unsafe, and the default for a different framework version is rarely identical.

## Practical labs

Stock curl, openssl, dig, and nc cover the basics.

### Inspect headers, version, and TLS

```
# See request and response headers; verbose mode also shows TLS handshake summary
curl -v https://example.com 2>&1 | head -40

# Detect HTTP/2 / HTTP/3 support via ALPN
openssl s_client -connect example.com:443 -servername example.com -alpn h2,http/1.1 </dev/null 2>/dev/null \
  | grep 'ALPN'

# Force HTTP/1.1 vs HTTP/2 vs HTTP/3 to compare server behavior across versions
curl -sI --http1.1 https://example.com
curl -sI --http2   https://example.com
curl -sI --http3   https://example.com   # requires curl built with HTTP/3
```

### Read the wire directly

```
# Plain HTTP — talk to the server with no curl normalization
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | nc example.com 80

# HTTPS — same idea, with openssl s_client wrapping the TCP socket
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect example.com:443 -servername example.com 2>/dev/null
```

### Probe method and endpoint surface

```
# Method discovery — many servers expose unintended verbs
for m in GET HEAD OPTIONS PUT DELETE PATCH TRACE PROPFIND CONNECT; do
  printf '%-9s -> %s\n' "$m" "$(curl -sI -X "$m" -o /dev/null -w '%{http_code}' https://example.com/)"
done

# Standard reconnaissance endpoints
for path in /.well-known/security.txt /robots.txt /sitemap.xml /server-status \
            /metrics /debug /actuator/health /api/v1/openapi.json; do
  printf '%-32s -> %s\n' "$path" "$(curl -sI -o /dev/null -w '%{http_code}' "https://example.com$path")"
done
```

### Status code semantics quick check

```
# 401 vs 403 vs 404 — does an unauthenticated request to a protected resource
# leak its existence (403 = exists, 404 = does not)?
curl -sI https://example.com/admin -o /dev/null -w '%{http_code}\n'
curl -sI https://example.com/admin/users/1 -o /dev/null -w '%{http_code}\n'
```

## Practical examples

- An app behind an HTTP/2 CDN deploys an HTTP/1.1 origin. The CDN serializes upstream as HTTP/1.1 and the smuggling surface that h2 was supposed to eliminate quietly reappears at the downgrade hop.
- A debug response includes `Server: gunicorn/19.6 Python/3.6` revealing a vulnerable Python web-server version. A public CVE search lights up immediately.
- A REST API uses `GET /users/42/delete` to delete users. The action is now CSRF-able from any image tag and quietly cacheable by any intermediary.
- A backend reads `request.headers['host']` to build password-reset URLs. The frontend proxy passes `Host:` unmodified. An attacker sends `Host: evil.example` and password reset emails point at the attacker.
- A Go service deployed behind Cloudflare speaks HTTP/3 to the public but no firewall rule existed for UDP/443. Half the perimeter monitoring becomes blind.
- An OAuth flow redirects to `Location: https://evil.example/callback?code=...`. The app validates the redirect against an allowlist on `Host` but not on the `Location` header it generates. Authorization code leaks.

## Related notes

- [[http-messages]] — wire format and parser framing rules; the "where does this part end" question.
- [[http-headers]] — semantics of the headers that steer security behavior.
- [[tls-https]] — transport-layer trust, HSTS, certificate handling.
- [[reverse-proxies]] — trust translation between HTTP parsers.
- [[client-ip-trust]] — the trust-disagreement specialization for forwarded-IP headers.
- [[cookies-and-sessions]] — the state layer attached to HTTP via `Set-Cookie`/`Cookie`.
- [[caching-and-security]] — `Cache-Control` and `Vary` semantics.
- [[dns-resolution]] — stage 1 of every transaction.
- [[request-smuggling|Request smuggling]] — the canonical h1/h2 parser-disagreement attack class.
- [[cors-misconfiguration|CORS misconfiguration]] — `Origin` header semantics.
- [[csrf|CSRF]] — method-idempotency and `Origin`/`Referer` trust.

### Suggested future atomic notes

- http-versions-comparison
- http3-quic-security
- alpn-and-version-negotiation
- http-status-code-semantics
- http-method-semantics
- content-type-handling
- connection-reuse-and-keep-alive

## References

- **Foundational:** MDN HTTP overview — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview
- **Foundational:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Foundational:** MDN HTTP request methods — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
