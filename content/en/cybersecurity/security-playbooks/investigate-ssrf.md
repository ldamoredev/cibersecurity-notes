---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Investigate SSRF

## Goal

Determine whether server-side request functionality can be used to reach internal, privileged, or attacker-chosen destinations.

## Assumptions

- the app fetches URLs, files, previews, webhooks, or remote content
- internal reachability may differ from public reachability
- redirects and alternate representations may bypass naive validation

## Prerequisites

- a feature that triggers server-side requests
- ability to observe responses, timing, or side effects
- knowledge of likely internal targets where ethically appropriate

## Recon steps

1. Identify all features that accept URLs or remote resources.
2. Observe how the server normalizes and fetches destinations.
3. Note whether redirects, DNS changes, or alternate IP formats are followed.

## Exploit / test steps

1. Confirm basic outbound request capability.
2. Test loopback, private ranges, and metadata-style targets where authorized.
3. Observe timing, status codes, header leakage, or indirect success signals.
4. Check whether redirects bypass allowlists.
5. Compare behavior for HTTP vs HTTPS and domain vs direct IP forms.

## Validation clues

- server can fetch attacker-controlled destinations
- internal or private targets produce distinguishable behavior
- metadata or internal admin paths are reachable
- URL validation blocks some forms but not equivalent alternatives

## Mitigation

- restrict egress destinations tightly
- validate and normalize URLs carefully
- avoid generic fetchers where possible
- segment networks so app servers cannot casually reach sensitive systems
- protect metadata access explicitly

## Logging / detection

- unusual outbound requests from app tier
- requests to loopback, RFC1918, or metadata-style addresses
- failed or repeated fetch attempts against internal targets

## Related notes

- [[ssrf]]
- [[nat-and-private-networks]]
- [[metadata-endpoints]]
- [[dns-resolution]]

## References

- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Research / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
