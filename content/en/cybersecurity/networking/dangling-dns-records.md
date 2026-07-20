---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Dangling DNS Records

## Definition

Dangling DNS records are DNS entries that still point to infrastructure, cloud resources, SaaS mappings, storage buckets, CDN distributions, or service targets that no longer exist or are no longer controlled by the intended owner.

## Why it matters

Dangling records are the lifecycle failure underneath many subdomain takeover findings. A hostname can look legitimate to users, browsers, cookies, HSTS policy, OAuth redirect allowlists, and internal documentation while its backing target is abandoned or claimable.

This networking note owns the stale name-target mechanism. [[subdomain-takeover|Subdomain Takeover]] owns the confirmed exposure condition where an attacker can claim the target.

## How it works

A dangling-record failure has **4 moving parts**:

1. **DNS name remains live.** The organization still publishes `blog.example.com`, `docs.example.com`, or another hostname.
2. **Target lifecycle changes.** The backing app, bucket, CDN distribution, SaaS tenant, or cloud load balancer is deleted, renamed, expired, or moved.
3. **DNS cleanup does not happen.** The stale record still points at the old provider target.
4. **Provider behavior decides impact.** Some providers return harmless errors; others allow a new tenant/resource to claim the same target.

Example:

```
docs.example.com. 300 IN CNAME example-docs.vendor-cdn.net.
```

If `example-docs` is deleted at the vendor but DNS remains, an attacker may be able to register `example-docs` and serve content as `docs.example.com`.

The bug is the broken lifecycle link between DNS and the provider resource, not DNS resolution alone.

## Techniques / patterns

Attackers and defenders inspect:

- `CNAME` records pointing to SaaS, CDN, app-hosting, storage, and cloud-provider names
- `A` / `AAAA` records pointing to deallocated cloud IPs or old load balancers
- provider-specific error strings such as "no such app", "project not found", "bucket not found", or "unconfigured domain"
- TXT verification records that may preserve old provider ownership
- DNS records for retired environments: `staging`, `preview`, `old`, `docs`, `help`, `status`, `campaign`
- CT logs and DNS history for hostnames that no longer appear in current inventory
- provider documentation on whether custom-domain targets are claimable after deletion

## Variants and bypasses

Dangling records appear in **6 common shapes**.

### 1. Dangling CNAME to SaaS or app hosting

The hostname aliases to a provider-managed name, but the tenant/project/site no longer exists. This is the classic subdomain takeover shape for documentation sites, support portals, marketing pages, and app platforms.

### 2. Deleted storage bucket or static site

The DNS record points to object storage or static hosting, and the bucket/site name becomes available to another account. Impact depends on provider namespace rules and region matching.

### 3. Deallocated cloud IP or load balancer

An `A` record points to an IP or load balancer that was released. If the address or endpoint can later be assigned to another customer, the stale record can route traffic to the wrong owner.

### 4. Stale CDN distribution or custom domain

The organization removes the CDN distribution or custom-domain binding but leaves DNS. Another distribution may be able to claim the hostname if certificate/domain validation permits it.

### 5. Verification-token residue

TXT records for email, SaaS, domain validation, search consoles, analytics, or cloud providers remain after the integration is retired. The record may not route traffic, but it can preserve proof-of-control.

### 6. Internal/private dangling records

Private hosted zones and internal DNS can dangle too. The impact is usually internal misrouting, SSRF amplification, service impersonation, or confusing incident response rather than public takeover.

## Impact

Ordered roughly by severity:

- **Subdomain takeover.** Attacker serves content under a trusted hostname after claiming the backing provider target.
- **Credential/session abuse.** Trusted subdomain status can influence cookies, OAuth redirect allowlists, CORS, SSO callbacks, or phishing credibility.
- **Traffic interception.** Users, API clients, or automation continue sending requests to a name whose target is no longer yours.
- **Brand and phishing abuse.** The attacker gets HTTPS and a legitimate-looking hostname if certificate issuance succeeds.
- **Internal service confusion.** Private stale names route workloads to wrong services or dead endpoints.
- **Inventory drift.** Dangling records are evidence that asset lifecycle and DNS lifecycle are disconnected.

## Detection and defense

Ordered by effectiveness:

1.
**Bind DNS records to owned provider resources in inventory.**
   Every external record should map to a concrete cloud/SaaS/CDN/storage resource with an owner and lifecycle state. If the backing resource disappears, DNS should alert or fail review.

2.
**Delete or park DNS before destroying the target.**
   Deprovisioning should remove the DNS record or point it to a controlled parking endpoint before deleting the provider resource. This avoids the claimable window.

3.
**Continuously scan provider-specific dangling fingerprints.**
   Periodically resolve CNAMEs and request the host over HTTP/HTTPS. Provider "not found" messages are high-signal. Keep a fingerprint list but verify manually before declaring takeover.

4.
**Clean up stale verification TXT records.**
   Remove SaaS, email, search, and cloud validation records when integrations end. Verification tokens are often forgotten because they do not serve traffic directly.

5.
**Prefer provider configurations that require domain validation before claim.**
   Some platforms prevent arbitrary claim without a fresh DNS token or certificate validation. Choose safer providers and enable domain-ownership checks where available.

6.
**Monitor DNS and certificate transparency for abandoned names.**
   CT logs may show certificates for old hosts. DNS history may show names that disappeared from inventory but still receive traffic or remain delegated.

7.
**Document accepted parked states.**
   A deliberate `CNAME` to a controlled parking host or `A` to a sink page is different from an accidental provider error. Make the difference visible.

### What does not work as a primary defense

- **Assuming a provider 404 is harmless.** Some provider 404s are exactly the signal that a target can be claimed.
- **Relying on HSTS or HTTPS.** TLS can protect the connection to an attacker-controlled claimed target; it does not prove the target is yours.
- **Deleting the cloud resource first.** That creates the dangling condition. DNS cleanup must happen before or with deletion.
- **Scanning only current inventory.** Dangling records often live in forgotten hosts found through CT logs, DNS history, docs, or old repos.
- **Treating all fingerprints as confirmed takeovers.** Provider behavior changes. A fingerprint means investigate and safely prove claimability in authorized scope.

## Practical labs

Run only against domains you own or are authorized to assess.

### List CNAME targets and provider boundaries

```
while read -r name; do
  target=$(dig +short "$name" CNAME | tail -n1)
  [ -n "$target" ] && printf '%-45s -> %s\n' "$name" "$target"
done < subdomains.txt
```

Label each target by provider and expected owner.

### Probe provider error fingerprints

```
while read -r name; do
  printf '\n== %s ==\n' "$name"
  dig +short "$name" CNAME
  curl -skL --max-time 5 "https://$name" | sed -n '1,12p'
done < subdomains.txt
```

Look for provider-specific unconfigured-domain messages, then verify against the provider's current docs and your scope rules.

### Compare DNS with asset inventory

```
while read -r name; do
  target=$(dig +short "$name" CNAME A AAAA | tr '\n' ' ')
  printf '%s,%s\n' "$name" "$target"
done < subdomains.txt > dns-targets.csv
```

Diff `dns-targets.csv` against cloud/CDN/SaaS inventory exports. Unmatched targets are review candidates.

### Check stale verification records

```
domain=example.com
dig +short "$domain" TXT
for sub in google-site-verification atlassian-domain-verification amazonses; do
  dig +short "$sub.$domain" TXT
done
```

Unexpected tokens should map to active integrations or be removed.

### Review Certificate Transparency for forgotten names

```
domain=example.com
curl -s "https://crt.sh/?q=%25.$domain&output=json" \
  | jq -r '.[].name_value' 2>/dev/null \
  | tr '\n' '\n' \
  | sort -u
```

Names in CT but not inventory are good dangling-record candidates.

### Safe confirmation pattern

```
1. Confirm the hostname is in authorized scope.
2. Confirm the provider target no longer maps to an owned resource.
3. Confirm provider docs say the target is claimable.
4. Use the least invasive proof allowed by the program or owner.
5. Never serve deceptive content or collect traffic.
```

## Practical examples

- `help.example.com` points to a deleted helpdesk tenant and displays a provider "project not found" page.
- `static.example.com` points to a removed storage bucket whose name can be re-created.
- `campaign.example.com` points to a retired marketing SaaS custom domain after the contract ended.
- `_amazonses.example.com` remains long after SES sending was migrated elsewhere.
- A private DNS record still points `payments.internal` to an old service IP now used by another workload.

## Related notes

- [[dns-resolution]] — how the name-target chain resolves.
- [[dns-security]] — ownership, control, and cleanup process.
- [[subdomain-takeover|Subdomain Takeover]] — exposure finding when the target is claimable.
- [[third-party-exposure|Third-Party Exposure]]
- [[subdomain-enumeration|Subdomain Enumeration]]
- [[tls-https]] — HSTS and certificate behavior can amplify trusted-subdomain impact.

### Suggested future atomic notes

- provider-takeover-fingerprints
- stale-verification-records
- cloud-storage-takeover
- cdn-custom-domain-takeover
- dns-inventory-automation
- safe-takeover-proof

## References

- **Foundational:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20
