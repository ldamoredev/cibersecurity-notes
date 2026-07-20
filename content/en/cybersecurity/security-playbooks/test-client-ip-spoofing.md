---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Test Client IP Spoofing

## Goal

Determine whether the application or upstream components trust attacker-controlled headers when deriving the client IP.

## Assumptions

- rate limits, logs, allowlists, or admin controls may depend on client IP
- proxies may forward original client information
- trust settings may be broader than intended

## Prerequisites

- a route where client IP affects behavior or is observable
- ability to replay requests with custom headers

## Recon steps

1. Find endpoints or logs that surface perceived client IP.
2. Identify whether the app sits behind proxies or load balancers.
3. Review default framework trust-proxy behavior if known.

## Exploit / test steps

1. Send requests with crafted `X-Forwarded-For` and related headers.
2. Observe logs, rate limits, or allowlist behavior.
3. Try multi-hop header values to see how parsing is handled.
4. Compare behavior through the normal edge vs alternate paths if any.

## Validation clues

- logs record attacker-supplied IPs
- rate limits reset or misapply based on spoofed values
- IP-based restrictions are bypassed
- different services disagree on the client IP

## Mitigation

- trust forwarding headers only from known proxies
- configure framework trust boundaries explicitly
- derive security decisions from a consistent, vetted source
- document and test the expected header chain

## Logging / detection

- impossible or malformed forwarding chains
- high churn in client IP for same session/account
- mismatches between edge and app logs

## Related notes

- [[client-ip-trust]]
- [[reverse-proxies]]
- [[http-headers]]
- [[api-rate-limiting|API Rate Limiting]]

## References

- **Foundational:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
