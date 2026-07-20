---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reverse Proxy Misconfig Checklist

## Goal

Identify whether proxy and backend behavior create trust-boundary bugs, parser confusion, header abuse, or unintended routing exposure.

## Assumptions

- one or more reverse proxies, CDNs, or load balancers sit in front of the app
- headers may be added, stripped, or trusted inconsistently
- proxy/backend parsing differences can create security issues

## Prerequisites

- visibility into requests and responses
- ability to send crafted headers and observe behavior
- rough understanding of the request chain

## Recon steps

1. Identify all request hops if possible.
2. Compare externally visible behavior with backend expectations.
3. Record proxy-added headers and route behaviors.

## Exploit / test steps

1. Test header trust: `X-Forwarded-For`, `X-Real-IP`, host-related headers.
2. Observe whether direct backend access also exists.
3. Check routing and path normalization differences.
4. Probe for request parsing ambiguity where appropriate.
5. Inspect health, debug, or alternate virtual host exposure.

## Validation clues

- attacker-controlled forwarding headers influence security decisions
- proxy and backend disagree on request interpretation
- backends are reachable directly outside the intended front door
- hidden paths or routing behaviors appear through proxy quirks

## Mitigation

- define a clear trusted proxy boundary
- normalize or reject ambiguous requests
- restrict direct backend exposure
- centralize and review forwarding/header trust policy
- patch and test the whole chain consistently

## Logging / detection

- unexpected forwarding-header values
- malformed request patterns
- traffic bypassing expected entrypoints
- inconsistencies between edge and backend logs

## Related notes

- [[reverse-proxies]]
- [[request-smuggling]]
- [[client-ip-trust]]
- [[load-balancers]]

## References

- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** PortSwigger Research — https://portswigger.net/research
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
