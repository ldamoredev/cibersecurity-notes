---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# DNS Resolution

## Definition

DNS resolution is the lookup process that turns a human-readable name, such as `app.example.com`, into the records a client needs to choose a destination: address records, aliases, mail exchangers, service records, text records, and provider-specific delegation chains.

## Why it matters

Every HTTP request begins with a naming decision before a packet reaches the app. DNS resolution decides which provider, CDN, load balancer, bucket, SaaS tenant, or origin a client will attempt to reach. Security work depends on reading that chain accurately because exposure often hides in indirection: aliases, split-horizon answers, stale CNAMEs, wildcard records, and third-party custom-domain mappings.

This note owns the lookup mechanics. [[dns-security]] owns DNS as an ownership and control problem. [[dangling-dns-records]] owns stale name-target mappings. [[subdomain-takeover|Subdomain Takeover]] owns the exposure finding when a stale mapping is claimable.

## How it works

DNS resolution answers **5 questions**:

1. **Who is authoritative for the name?** The resolver walks root → TLD → authoritative nameservers for the zone.
2. **Is the name an alias?** `CNAME` chains redirect the lookup to another owner-controlled or third-party-controlled name.
3. **What address or service record is returned?** `A`, `AAAA`, `MX`, `TXT`, `SRV`, `CAA`, and other records each carry different security meaning.
4. **How long can the answer be cached?** TTL controls how long recursive resolvers and clients may reuse the answer.
5. **Does the answer vary by resolver, source, or view?** CDNs, geo-DNS, split-horizon DNS, and private hosted zones can return different answers for the same name.

Example lookup chain:

```
app.example.com.      300 IN CNAME app-prod.edge.examplecdn.net.
app-prod.edge.examplecdn.net. 60 IN A 203.0.113.42
app-prod.edge.examplecdn.net. 60 IN AAAA 2001:db8::42
```

Security interpretation:

- `example.com` owns the public hostname.
- the CDN owns the target namespace and edge infrastructure.
- the low TTL suggests traffic steering can change quickly.
- the actual origin may be hidden, but certificate transparency or DNS history may still expose it.

The bug is rarely "DNS exists." The bug is assuming a name means one stable thing when resolution is really a chain of delegations, caches, and provider ownership.

## Techniques / patterns

Attackers and defenders inspect:

- `A` / `AAAA` records to find direct hosts, CDN edges, load balancers, and exposed origins
- `CNAME` chains to identify third-party providers and dangling custom-domain mappings
- `MX`, `TXT`, `SPF`, `DKIM`, and `DMARC` records to understand mail and identity posture
- `CAA` records to see which certificate authorities may issue for the domain
- `NS` records to identify authoritative providers and delegation boundaries
- wildcard behavior such as `anything.example.com` resolving unexpectedly
- TTL values that signal dynamic steering, stale records, or slow incident response windows
- split-horizon behavior by comparing answers from public resolvers, internal resolvers, VPN, and cloud VPC contexts
- DNS history / certificate transparency to find old origins, retired vendors, and untracked subdomains

## Variants and bypasses

DNS resolution behavior falls into **6 operational variants** that matter during security review.

### 1. Direct address records

`A` and `AAAA` records point directly to IPv4/IPv6 addresses. These are easiest to reason about but can still hide exposure when a public IP bypasses a CDN, WAF, or reverse proxy.

### 2. Alias chains

`CNAME` chains point one name at another name. Each hop may cross an ownership boundary. This is the common shape for SaaS custom domains, CDNs, cloud load balancers, and takeover-prone dangling records.

### 3. Wildcard records

`*.example.com` answers for arbitrary names. Wildcards can hide inventory mistakes, make brute-force enumeration noisy, and cause tools to report false positives unless they check baseline random names.

### 4. Split-horizon DNS

The same name resolves differently depending on whether the client uses public DNS, corporate DNS, VPN DNS, or cloud private hosted zones. This matters for SSRF, internal reachability, and incident response because the vulnerable server may resolve a target differently than the tester's laptop.

### 5. Geo-DNS and CDN steering

Resolvers return different answers based on geography, latency, health, or EDNS Client Subnet. A finding reproduced from one region may disappear from another, and a single hostname may front many edge IPs.

### 6. Negative and stale caching

NXDOMAIN, SERVFAIL, and old positive answers can be cached. During cleanup or incident response, a deleted record may still be remembered by resolvers, while a new record may not be visible everywhere yet.

## Impact

Ordered roughly by severity:

- **Traffic to attacker-controlled infrastructure.** Dangling aliases or poisoned ownership chains can route trusted hostnames to an attacker.
- **Bypass of edge controls.** DNS history, direct `A` records, or leaked origins can let traffic skip a CDN/WAF/reverse-proxy path.
- **SSRF allowlist bypass.** A benign-looking domain can resolve to private, loopback, or link-local addresses after redirect, rebinding, or split-horizon resolution.
- **Email and identity abuse.** Weak or confusing MX/TXT records affect phishing resistance, domain verification, and SaaS tenant ownership.
- **Asset-inventory drift.** Unknown subdomains, stale records, and provider dependencies widen attack surface beyond diagrams.
- **Operational fragility.** Low TTLs, bad delegation, or inconsistent authoritative answers make outages and incident response harder.

## Detection and defense

Ordered by effectiveness:

1.
**Maintain authoritative ownership inventory for every domain and subdomain.**
   Each hostname should have a business owner, technical owner, expected target, provider, and retirement path. DNS resolution is only safe when the organization knows who is allowed to point names where.

2.
**Resolve complete chains and record ownership boundaries.**
   Do not stop at the first `CNAME`. Follow the full chain and label when ownership crosses to a CDN, SaaS provider, cloud load balancer, storage bucket, or vendor. Most takeover and exposure drift lives at these boundaries.

3.
**Compare public, internal, and workload-context resolution.**
   Test from public resolvers, VPN/internal DNS, and the runtime context that matters (cloud VM, container, CI runner, SSRF-prone app server). Split-horizon answers are not bugs by themselves, but they are dangerous when defenders test from the wrong viewpoint.

4.
**Build stale-record cleanup into deprovisioning.**
   Destroying a cloud app, bucket, SaaS tenant, or load balancer should trigger DNS removal in the same change path. DNS should not be a separate manual afterthought.

5.
**Detect wildcard baselines before trusting enumeration results.**
   Query random names under the zone to learn wildcard behavior. Without a baseline, brute-force subdomain tools may mistake wildcard answers for real assets.

6.
**Use DNS data as one signal, not the whole truth.**
   DNS tells you intended naming, not necessarily all reachable services. Pair it with certificate transparency, HTTP probing, port scanning, cloud inventory, and attack-surface records.

7.
**Set TTLs deliberately.**
   Short TTLs help migration and incident response but increase dependency on authoritative availability. Long TTLs reduce query load but slow recovery and cleanup. The right value depends on operational purpose.

### What does not work as a primary defense

- **Assuming NXDOMAIN means no exposure.** DNS history, certificates, alternate records, and direct IP exposure may still reveal or reach the service.
- **Checking only `A` records.** `CNAME`, `AAAA`, `MX`, `TXT`, `CAA`, and wildcard behavior often carry the security story.
- **Testing only from your laptop.** Servers, containers, VPN clients, and cloud workloads may resolve different answers.
- **Treating DNS as authorization.** A private-looking name, internal suffix, or unlisted subdomain does not authorize the caller.
- **Relying on low TTL as cleanup.** TTL only controls cache lifetime. It does not delete stale records or revoke third-party ownership.

## Practical labs

Run these against domains you own or are authorized to assess. Stock `dig`, `host`, `curl`, and optional `jq` are enough.

### Trace authoritative resolution

```
# Show the delegation path from root to the final answer.
dig +trace app.example.com

# Ask the authoritative nameserver directly after identifying it.
dig NS example.com +short
dig @ns1.example-dns.net app.example.com A
```

Use this to distinguish recursive-cache behavior from authoritative truth.

### Follow CNAME chains and address records

```
name=app.example.com
dig +short "$name" CNAME
dig +short "$name" A
dig +short "$name" AAAA

# Full answer with TTLs.
dig "$name" A "$name" AAAA "$name" CNAME
```

Record each ownership boundary: your zone → CDN → cloud provider → SaaS target.

### Detect wildcard DNS behavior

```
domain=example.com
for sub in does-not-exist-$RANDOM definitely-missing-$RANDOM random-$RANDOM; do
  printf '%s -> ' "$sub.$domain"
  dig +short "$sub.$domain" A
done
```

If random names resolve, subdomain brute-force output must be filtered against the wildcard baseline.

### Compare resolvers and viewpoints

```
name=app.example.com
for resolver in 1.1.1.1 8.8.8.8 9.9.9.9; do
  printf '\nResolver %s\n' "$resolver"
  dig @"$resolver" +short "$name" A
done

# Compare from inside VPN/cloud/container when possible:
dig +short "$name" A
```

Different answers may be CDN steering, split-horizon DNS, or stale recursive caches.

### Inspect mail and domain-verification records

```
domain=example.com
dig +short "$domain" MX
dig +short "$domain" TXT
dig +short "_dmarc.$domain" TXT
dig +short "$domain" CAA
```

Look for old SaaS verification tokens, weak DMARC policy, and absent or overly broad CAA records.

### Check whether DNS points around the edge

```
name=app.example.com
dig +short "$name" A
curl -skI "https://$name" | rg -i 'server|via|x-cache|cf-ray|x-amz-cf-id|x-served-by'
```

Compare DNS answers with response headers. A direct origin IP without CDN/proxy headers may indicate edge bypass.

## Practical examples

- `app.example.com` points to a CDN, but an old `origin.example.com` `A` record still exposes the backend directly.
- `docs.example.com` is a `CNAME` into a SaaS provider; the SaaS tenant was deleted but DNS stayed.
- `*.dev.example.com` resolves to a catch-all staging ingress, causing scanners to report many false-positive hosts.
- A public tester sees no private address, but a vulnerable SSRF fetcher inside the VPC resolves the same name to `10.0.4.15`.
- A forgotten TXT verification record proves control of a SaaS tenant long after the integration was retired.

## Related notes

- [[dns-security]] — ownership, control, and exposure hygiene.
- [[dangling-dns-records]] — stale name-target mappings.
- [[subdomain-takeover|Subdomain Takeover]] — exposure finding when a dangling target is claimable.
- [[http-overview]] — DNS is stage 1 of every HTTP transaction.
- [[load-balancers]] — many DNS records terminate at load balancers or CDNs.
- [[service-enumeration|Service Enumeration]] — after resolution identifies reachable targets, enumerate what they actually run.
- [[ssrf|SSRF]] — resolver viewpoint and rebinding matter for URL-fetching bugs.
- [[external-attack-surface|External Attack Surface]]

### Suggested future atomic notes

- dns-record-types
- split-horizon-dns
- wildcard-dns
- dns-rebinding
- certificate-transparency-monitoring
- caa-records

## References

- **Foundational:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Foundational:** ICANN DNS Concepts — https://www.icann.org/resources/pages/dns-2012-02-25-en
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
