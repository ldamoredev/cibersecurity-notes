---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Request Smuggling

## Definition

Request smuggling happens when two components in the HTTP request chain parse the same request differently, allowing an attacker to desynchronize front-end and back-end understanding of message boundaries.

## Why it matters

Request smuggling is one of the clearest examples of networking and web security colliding. It is not just an HTTP bug. It is a trust-boundary bug between intermediaries.

This matters because the impact can include:
- request hijacking
- cache poisoning
- authentication side effects
- route confusion
- access to hidden functionality
- cross-user interference

## How it works

The core mechanism is:
1. an attacker sends an ambiguous HTTP request
2. the front-end and back-end disagree about where that request ends
3. leftover bytes are interpreted as a second request or as part of someone else’s request stream

The most famous family involves disagreement between:
- `Content-Length`
- `Transfer-Encoding`

Minimal CL.TE skeleton (front-end uses `Content-Length`, back-end uses `Transfer-Encoding: chunked`):

```
POST / HTTP/1.1
Host: vulnerable.example
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

The front-end forwards the full body because it trusts `Content-Length: 13`. The back-end stops at the `0\r\n\r\n` chunk terminator and treats `SMUGGLED` as the start of the next request on the keep-alive connection — which the next victim's request gets appended to.

The vulnerability is not the headers themselves. It is the disagreement between two parsers sharing a connection.

## Techniques / patterns

Attackers usually test:
- CL.TE / TE.CL style ambiguities
- front-end / back-end parser mismatch
- unusual header combinations
- chunked encoding edge cases
- request queue poisoning
- hidden path reachability through desync
- interaction with caching and auth layers

## Variants and bypasses

### CL.TE

Front-end trusts `Content-Length`, back-end trusts `Transfer-Encoding`.

### TE.CL

Front-end trusts `Transfer-Encoding`, back-end trusts `Content-Length`.

### TE.TE / parser differences

Both parse transfer encoding, but differently.

### Header normalization and edge quirks

Different components may rewrite or accept malformed headers differently.

### Cache and auth side effects

The attack may show up as poisoning, routing confusion, or auth weirdness rather than obvious direct RCE-style effect.

## Impact

Typical impact:
- interfere with another user’s request
- reach hidden endpoints
- bypass expected front-end protections
- poison cache or request queue behavior
- create confusing auth and routing side effects

## Detection and defense

Ordered by effectiveness:

1.
**Normalize or reject ambiguous requests**
   The edge should canonicalize messages before forwarding: reject requests that contain both `Content-Length` and `Transfer-Encoding`, reject malformed chunked encoding, and reject non-conforming whitespace or duplicate headers. If the edge cannot fix the message, fail closed.

2.
**Use HTTP/2 end-to-end where possible**
   HTTP/2 framing is length-prefixed and removes the textual ambiguity that drives most desync. Downgrades from HTTP/2 to HTTP/1.1 between proxy and origin reintroduce the same parser-mismatch surface — keep the back channel HTTP/2 if the front-end is HTTP/2.

3.
**Keep front-end and back-end behavior aligned**
   Use the same web server family, version, and parsing config on both sides where feasible. Most desync findings come from one side being more permissive than the other on the same input.

4.
**Understand the full chain**
   Map every hop: CDN, WAF, load balancer, ingress controller, app server. Each hop is a parser. Document the order so the team knows which component sees the request first and which one sees it last.

5.
**Reduce hidden trust in intermediaries**
   Do not let internal headers like `X-Forwarded-For`, `X-Original-URL`, or rewriter hints become trust boundaries the back-end relies on without re-validation. Smuggled requests can carry forged versions of these.

6.
**Monitor for desync indicators**
   Watch for: requests being attributed to the wrong user, unexpected `400 Bad Request` clusters from the back-end, cache entries with mismatched keys, and connection-reuse anomalies on the keep-alive layer.

7.
**Test the exact deployed chain**
   Lab parsers are not deployed parsers. Run smuggling probes against the staging chain that mirrors production hop-for-hop. PortSwigger's HTTP Request Smuggler and `smuggler.py` style probes are the practical tools.

## Practical examples

- front-end and back-end disagree on where request body ends
- attacker poisons the queue so another user’s request is interpreted differently
- hidden admin path becomes reachable because the edge and origin disagree on request structure
- cache behavior changes because of desynchronized routing

## Related notes

- [[http-messages]]
- [[reverse-proxies]]
- [[caching-and-security]]
- [[reverse-proxy-misconfig-checklist|Reverse Proxy Misconfig Checklist]]

### Suggested future atomic notes

- cl-te-vs-te-cl
- http-desync-impact-patterns
- http2-downgrade-desync

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- **Research / Deep Dive:** James Kettle, "HTTP/2: The Sequel is Always Worse" — https://portswigger.net/research/http2
