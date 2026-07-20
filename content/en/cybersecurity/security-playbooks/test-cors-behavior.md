---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Test CORS Behavior

## Goal

Determine whether CORS policy is too permissive, reflected unsafely, or misunderstood as an authorization control.

## Assumptions

- one or more API/browser endpoints rely on cross-origin access
- the browser enforces CORS, not the server in a general auth sense
- credentials and origin handling may be misconfigured

## Prerequisites

- endpoints returning CORS headers
- ability to send custom `Origin` headers
- understanding of whether cookies or credentials are involved

## Recon steps

1. Identify cross-origin endpoints.
2. Record `Access-Control-*` headers on normal responses and preflights.
3. Observe whether origins are static, wildcard, or reflected.

## Exploit / test steps

1. Send requests with attacker-controlled `Origin` values.
2. Check whether credentials are allowed alongside reflected origins.
3. Compare preflight and non-preflight behavior.
4. Test subdomain and scheme variations of trusted origins.
5. Confirm whether the team is relying on CORS where server-side auth should exist.

## Validation clues

- reflected attacker origin
- `Access-Control-Allow-Credentials: true` with unsafe origin behavior
- broad trust of attacker-influenceable subdomains
- confusion between readable responses and writable state changes

## Mitigation

- explicitly enumerate trusted origins
- never treat CORS as authorization
- review credentialed cross-origin flows carefully
- keep server-side access control independent of browser policy

## Logging / detection

- unexpected origins hitting sensitive routes
- drift in allowed origin patterns
- preflight anomalies on auth-sensitive endpoints

## Related notes

- [[cors-misconfiguration]]
- [[http-headers]]
- [[csrf]]
- [[cookies-and-sessions]]

## References

- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Foundational:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
