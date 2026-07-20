---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Server-Side Request Forgery (SSRF)

## Definition

SSRF happens when an application can be induced to make a server-side request to an attacker-chosen destination. The key danger is that the server can often reach internal or privileged resources that the external attacker cannot directly access.

## Why it matters

SSRF is one of the clearest examples of why networking and web security must be learned together. It turns server-side network reachability into exploitable impact.

Unlike many input bugs, the blast radius depends heavily on environment:
- internal network reachability
- metadata service exposure
- proxy behavior
- redirect handling
- DNS behavior

## How it works

The usual shape is:

1. the application accepts a URL or remote resource reference
2. the server performs the request on behalf of the user
3. destination validation is weak, bypassable, or absent
4. the attacker uses the server’s network position and trust to reach targets they cannot call directly

Common SSRF entry points:
- URL preview features
- webhooks and callback testers
- document or image fetchers
- import/sync features
- PDF/render pipelines
- “fetch remote resource” helpers

## Techniques / patterns

Attackers usually test:
- loopback and localhost targets
- RFC1918/private ranges
- metadata service addresses
- alternate IP representations
- domain vs direct IP behavior
- redirect chains
- DNS-based destination changes
- protocol and scheme handling

## Variants and bypasses

### Basic internal reachability

The app can fetch internal services the attacker cannot reach directly.

### Metadata targeting

The app can reach cloud metadata endpoints and expose credentials or instance context.

### Redirect bypass

Validation happens only on the first URL, but redirects lead somewhere dangerous.

### DNS rebinding / resolution tricks

Validation and connection do not treat hostname resolution consistently.

### Parser / URL normalization quirks

Different components disagree about the real destination.

### Blind SSRF

The attacker cannot read the response directly, but can still infer reachability from timing, side effects, or out-of-band callbacks.

## Impact

Typical impact:
- internal API access
- metadata credential exposure
- internal admin surface reachability
- trust-boundary bypass into private services
- pivoting into wider infrastructure compromise

The same SSRF sink can be low-severity in one environment and critical in another.

## Detection and defense

Ordered by effectiveness:

1. **Restrict where server-side requests can go**
2. **Validate and normalize destinations carefully**
3. **Be explicit about redirects, DNS, and IP handling**
4. **Segment networks so app servers cannot casually reach sensitive internals**
5. **Protect metadata access explicitly**
6. **Monitor outbound requests from application tiers**

## Practical examples

- a URL preview feature fetches arbitrary addresses
- a backend can reach `169.254.169.254` and expose cloud metadata
- an internal-only service becomes reachable through a public app’s fetch capability
- a redirect chain bypasses an allowlist that only checks the first host

## Related notes

- [[nat-and-private-networks|NAT and Private Networks]]
- [[metadata-endpoints|Metadata Endpoints]]
- [[dns-resolution|DNS Resolution]]
- [[reverse-proxies|Reverse Proxies]]
- [[investigate-ssrf|Investigate SSRF]]

## References

- **Foundational:** OWASP SSRF Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf
- **Research / Deep Dive:** AWS IMDS docs — https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
