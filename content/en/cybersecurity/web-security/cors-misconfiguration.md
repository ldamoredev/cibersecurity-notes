---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# CORS Misconfiguration

## Definition

CORS misconfiguration happens when a server’s cross-origin resource sharing policy is too permissive, incorrectly implemented, or misunderstood as a substitute for real server-side authorization.

## Why it matters

CORS is widely misunderstood. Teams often treat it as if it were an access-control mechanism, when it is really a browser-enforced policy about whether a response can be read by a requesting origin.

This confusion leads to bugs where:
- arbitrary origins are reflected
- credentials are allowed too broadly
- trusted-origin logic is weak
- developers assume CORS blocks attacks it does not actually block

## How it works

The mechanism is:
1. the browser sends an `Origin` header
2. the server responds with `Access-Control-*` headers
3. the browser decides whether the calling origin can read the response

The server-side mistake is often one of these:
- reflecting arbitrary origins
- using too-broad trust patterns
- allowing credentials with unsafe origin handling
- assuming CORS is equivalent to authorization

The dangerous shape — arbitrary origin reflected back with credentials allowed — looks like this:

```
GET /api/me HTTP/1.1
Host: api.example.com
Origin: https://attacker.example
Cookie: session=...

HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://attacker.example
Access-Control-Allow-Credentials: true

{"email":"victim@example.com","balance":12345}
```

A page on `attacker.example` can now call `fetch("https://api.example.com/api/me", {credentials: "include"})` and read the victim's response body. The browser enforced nothing, because the server told it the attacker origin is trusted.

The same anti-pattern appears with sloppy regexes — for example, trusting any origin matching `*.example.com` when an attacker can register `example.com.attacker.com` or take over a stale subdomain.

## Techniques / patterns

Attackers usually test:
- reflected `Origin` behavior
- wildcard or pattern-based origin trust
- credentialed requests
- preflight differences
- scheme / subdomain variations
- whether teams are relying on CORS where real auth should exist

## Variants and bypasses

### Reflected origin

The server reflects whatever origin the client sends.

### Unsafe credentialed CORS

A dangerous pattern where credentials are allowed and origin trust is too broad.

### Over-broad subdomain trust

The policy trusts a namespace the attacker can influence.

### Preflight / route inconsistency

One path or method is stricter than another.

### CORS vs CSRF confusion

Teams believe CORS blocks attackers when CSRF may still succeed.

### Non-browser misconceptions

CORS is a browser policy. Non-browser clients do not care about it.

## Impact

Typical impact:
- attacker-controlled origin can read sensitive API responses
- credentialed browser requests become readable cross-origin
- origin-trust assumptions expand data exposure
- admins or logged-in victims become useful cross-origin data sources

## Detection and defense

Ordered by effectiveness:

1.
**Treat CORS as browser policy, not authorization**
   CORS controls whether a browser allows a cross-origin response to be read by JavaScript. It does not authenticate or authorize the caller. Real authorization still has to live on the server. If your defense story for an endpoint reduces to "CORS won't let them read it," the endpoint is not actually protected.

2.
**Explicitly enumerate trusted origins**
   Match the `Origin` header against a server-side allowlist of full origins (scheme + host + port). Do not reflect the request `Origin` back. Do not match by `endsWith` or unbounded regex — those usually allow attacker-controlled subdomains or look-alike hosts.

3.
**Be careful with credentialed cross-origin access**
   `Access-Control-Allow-Credentials: true` combined with a permissive origin is the worst-case combination. If credentials are required, the allowlist must be exact and small. Ideally, sensitive APIs that take cookies should not be cross-origin reachable at all.

4.
**Review preflight and non-preflight behavior together**
   Many bugs come from inconsistencies — the preflight response is strict, but the actual request handler is permissive (or vice versa). Test both `OPTIONS` and the real method against each interesting endpoint.

5.
**Separate public resources from sensitive APIs**
   Static, non-credentialed assets can use `Access-Control-Allow-Origin: *`. Anything that reads a session, returns user-specific data, or accepts a state-changing call should never share that policy.

6.
**Do not rely on CORS to prevent CSRF**
   CORS controls *reads* of cross-origin responses. Browsers can still *send* state-changing requests cross-origin (form submissions, simple requests). CSRF requires its own defense — tokens, SameSite cookies, or origin/referer checks on state-changing routes.

7.
**Monitor**
   Watch for: `Origin` reflection in production responses, `Access-Control-Allow-Credentials: true` paired with a non-allowlisted origin, and unexpected origins appearing on sensitive endpoints. Active scanning with a CORS-fuzzer (CORStest, Corsy) catches the common shapes.

## Practical examples

- API reflects arbitrary `Origin` and allows browser-side reading
- broad trusted subdomain pattern includes attacker-influenceable origins
- sensitive cookie-auth endpoint is readable from an unexpected external origin
- team thinks CORS prevents CSRF, leaving intent-validation gaps elsewhere

## Related notes

- [[http-headers]]
- [[csrf]]
- [[cookies-and-sessions]]
- [[test-cors-behavior|Test CORS Behavior]]

### Suggested future atomic notes

- credentialed-cors-risk
- origin-matching-pitfalls
- cors-vs-csrf-confusion

## References

- **Foundational:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Research / Deep Dive:** PortSwigger, "Exploiting CORS misconfigurations for Bitcoins and bounties" — https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties
