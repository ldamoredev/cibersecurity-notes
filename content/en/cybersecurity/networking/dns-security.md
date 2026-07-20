---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# DNS Security

## Definition

DNS security is the discipline of keeping the naming layer trustworthy: domains and subdomains should resolve only to intended destinations, be controlled by intended owners, resist spoofing or takeover, and expose no more attack surface than the organization means to publish.

## Why it matters

DNS is where architecture becomes discoverable. Even when the application is well built, DNS can reveal staging systems, point around a CDN, delegate trust to forgotten vendors, weaken email identity, or leave behind takeover-prone records. A messy DNS zone is usually a map of messy asset ownership.

This note owns DNS ownership and control. [[dns-resolution]] owns lookup mechanics. [[dangling-dns-records]] owns stale name-target mappings. [[subdomain-takeover|Subdomain Takeover]] owns the concrete exposure finding.

## How it works

DNS security is controlled through **5 ownership boundaries**:

1. **Registrar ownership.** Who can renew, transfer, lock, or change the domain registration.
2. **Authoritative DNS ownership.** Who controls the nameservers and zone records.
3. **Record ownership.** Which team owns each hostname, record type, target, and lifecycle.
4. **Provider ownership.** Which cloud, CDN, SaaS, storage, or mail provider the record delegates traffic or proof-of-control to.
5. **Client trust boundary.** Whether clients and resolvers can trust that the answer they receive has not been spoofed, poisoned, or downgraded.

Example high-risk shape:

```
support.example.com. 300 IN CNAME example-support.zendesk.com.
_amazonses.example.com. 300 IN TXT "old-verification-token"
example.com. 300 IN CAA 0 issue ";"
```

Security interpretation:

- `support.example.com` depends on a third-party tenant lifecycle.
- old verification tokens may preserve proof-of-control in external services.
- a restrictive or broken CAA policy affects certificate issuance.
- the DNS record is not just "a pointer"; it is a trust delegation.

The bug usually lives where DNS ownership outlives the system or vendor relationship it was created for.

## Techniques / patterns

Attackers and defenders inspect:

- registrar lock, MFA, account ownership, and domain renewal posture
- authoritative nameserver providers and delegation chains
- stale `CNAME`, `A`, `AAAA`, `NS`, `MX`, and `TXT` records
- third-party SaaS custom-domain mappings and verification records
- takeover fingerprints in provider error pages
- missing or weak SPF, DKIM, and DMARC records
- absent or overbroad CAA records
- DNSSEC presence, delegation status, and validation failures
- wildcard records hiding real inventory
- split-horizon DNS differences between public, internal, VPN, and cloud views

## Variants and bypasses

DNS security failures fall into **7 practical classes**.

### 1. Registrar compromise or mismanagement

If the registrar account is weak, an attacker can change nameservers, transfer domains, or hijack the domain at the root of trust. MFA, registry lock, and tight account ownership matter before any individual record setting.

### 2. Authoritative DNS control drift

Old DNS providers, forgotten hosted zones, shadow zones, and inconsistent delegation make the source of truth unclear. If two teams can publish conflicting records, incident response becomes guesswork.

### 3. Dangling records and claimable targets

DNS points to an external target that no longer exists or is no longer claimed. The stale record may become a [[subdomain-takeover|Subdomain Takeover]] if an attacker can register the backing resource.

### 4. Third-party verification residue

TXT records for SaaS verification, domain ownership, mail providers, analytics tools, and cloud services often remain after offboarding. Some providers treat old tokens as continuing proof of control.

### 5. Mail identity misconfiguration

Weak SPF, missing DKIM, permissive DMARC, and forgotten MX records make phishing and spoofing easier. DNS security includes mail identity because email trust is domain trust.

### 6. Certificate issuance control gaps

Missing or broad CAA records allow more certificate authorities to issue for a domain than intended. Weak DNS ownership can also enable fraudulent domain validation if an attacker controls a subdomain or record path.

### 7. Resolver and cache trust failures

DNS spoofing, cache poisoning, malicious local resolvers, and unsigned answers can route clients to the wrong destination. DNSSEC helps where deployed correctly, but operational hygiene still matters.

## Impact

Ordered roughly by severity:

- **Domain or subdomain hijack.** Registrar, authoritative DNS, or dangling-record failures let an attacker serve content under trusted names.
- **Traffic interception or credential theft.** Changed DNS answers can route users, API clients, or mail to attacker-controlled infrastructure.
- **Phishing and brand abuse.** Weak mail records and takeover-prone subdomains make spoofing more believable and harder to filter.
- **Bypass of edge security.** Direct origin records or stale DNS can skip CDN/WAF/reverse-proxy controls.
- **Cloud/SaaS tenant abuse.** Old verification records or custom-domain mappings can preserve unintended trust in third-party systems.
- **Asset-inventory failure.** Unknown DNS records hide systems from patching, monitoring, and ownership review.
- **Incident-response delay.** Long TTLs, unclear authority, or multiple DNS providers slow containment.

## Detection and defense

Ordered by effectiveness:

1.
**Protect registrar and authoritative DNS accounts first.**
   Enforce MFA, least privilege, registry lock where available, renewal monitoring, and named owners. If an attacker can change nameservers or zone records, downstream controls are decoration.

2.
**Make DNS ownership inventory mandatory.**
   Every record should have an owner, purpose, expected target, provider, creation date, and retirement condition. Ownership metadata turns cleanup from archaeology into normal operations.

3.
**Automate stale-record and third-party-target review.**
   Continuously compare DNS records against cloud/SaaS inventories. Flag records pointing to deleted buckets, load balancers, app services, CDN distributions, SaaS tenants, or unclaimed provider targets.

4.
**Tie DNS cleanup to deprovisioning.**
   The same change that deletes a service should remove or park its DNS. This closes the gap where infrastructure lifecycle and naming lifecycle drift apart.

5.
**Harden mail and certificate-control records.**
   Use SPF with tight includes, DKIM signing, DMARC with enforcement (`p=quarantine` or `p=reject` after monitoring), and CAA records that list intended CAs. These records protect domain trust beyond web traffic.

6.
**Use DNSSEC where operationally supported.**
   DNSSEC provides integrity for DNS answers when the resolver validates it and the zone is signed correctly. It helps against spoofing/cache-poisoning classes, but it does not prevent stale records, bad targets, or takeover-prone SaaS mappings.

7.
**Monitor public DNS and certificate transparency.**
   Alert on new subdomains, nameserver changes, MX changes, CAA changes, and unexpected certificate issuance. DNS changes are high-signal security events.

### What does not work as a primary defense

- **"The domain is internal-looking."** Names do not enforce reachability or authorization. `admin.internal.example.com` is only internal if the network path and DNS view make it so.
- **DNSSEC as a takeover fix.** DNSSEC can prove the stale record is authentic; it does not prove the target is still owned.
- **Manual annual DNS review.** Records drift whenever teams ship, migrate, test vendors, or decommission infrastructure. Annual review finds fossils.
- **Deleting infrastructure before DNS.** This creates the exact dangling window attackers want. Remove or park DNS as part of the same change.
- **Relying on wildcard records to simplify operations.** Wildcards can mask missing inventory, make enumeration noisy, and route unexpected names to real infrastructure.
- **Assuming provider error pages are harmless.** Many takeover workflows start from provider-specific "not found" pages that reveal a claimable target.

## Practical labs

Run these against domains you own or have permission to review.

### Inventory authoritative control

```
domain=example.com
dig +short "$domain" NS
whois "$domain" | rg -i 'registrar|name server|status|expiry|expiration|updated'
```

Look for registrar lock/status, unexpected nameservers, old DNS providers, and renewal risk.

### Sweep high-risk record types

```
domain=example.com
for type in A AAAA CNAME MX TXT NS CAA; do
  printf '\n== %s ==\n' "$type"
  dig +short "$domain" "$type"
done

dig +short "_dmarc.$domain" TXT
dig +short "selector1._domainkey.$domain" TXT
```

This gives a fast picture of web, mail, verification, delegation, and certificate-control posture.

### Check mail identity posture

```
domain=example.com
dig +short "$domain" TXT | rg -i 'v=spf1'
dig +short "_dmarc.$domain" TXT

# If you know DKIM selectors, check them explicitly.
dig +short "default._domainkey.$domain" TXT
dig +short "selector1._domainkey.$domain" TXT
```

Look for missing SPF, `~all` or `?all` during mature operation, missing DMARC, or `p=none` that never graduated to enforcement.

### Detect stale SaaS and cloud mappings

```
while read -r name; do
  target=$(dig +short "$name" CNAME | tail -n1)
  if [ -n "$target" ]; then
    printf '%-40s -> %s\n' "$name" "$target"
    curl -skI "https://$name" | sed -n '1,8p'
  fi
done < subdomains.txt
```

Provider-specific 404 or "no such app/bucket/site" messages should hand off to [[dangling-dns-records]] and [[subdomain-takeover|Subdomain Takeover]].

### Check CAA and unexpected certificate issuance

```
domain=example.com
dig +short "$domain" CAA

# Certificate Transparency via crt.sh JSON API.
curl -s "https://crt.sh/?q=%25.$domain&output=json" \
  | jq -r '.[].name_value' 2>/dev/null \
  | tr '\n' '\n' \
  | sort -u
```

Compare issued names and CAs against expected providers. Unexpected certificates often reveal forgotten hosts or unauthorized issuance paths.

### Compare public and internal views

```
name=admin.example.com
for resolver in 1.1.1.1 8.8.8.8 9.9.9.9; do
  printf '%s public -> ' "$resolver"
  dig @"$resolver" +short "$name" A
done

printf 'local resolver -> '
dig +short "$name" A
```

Run the local resolver test from VPN, office network, cloud VM, and container contexts when those are in scope. Split-horizon surprises are common.

### Verify DNSSEC status

```
domain=example.com
dig +dnssec "$domain" SOA
dig +short DS "$domain"
```

DNSSEC is useful only if the zone is signed, delegation is correct, and validators can build a chain of trust.

## Practical examples

- A registrar account has no MFA; a compromised email account can transfer the domain or change nameservers.
- A retired marketing microsite leaves `campaign.example.com CNAME vendor.example.net`; the vendor target becomes claimable.
- `_amazonses.example.com` or old SaaS TXT records remain after the provider relationship ends.
- DMARC stays at `p=none` for years, allowing spoofed mail to pass with minimal receiver enforcement.
- A new CDN migration leaves `origin.example.com` publicly resolvable and reachable outside the WAF.
- A private hosted zone resolves `api.example.com` to `10.0.0.12`, while public DNS resolves it to the CDN. An SSRF inside the VPC follows the internal path.

## Related notes

- [[dns-resolution]] — lookup mechanics, aliases, resolver viewpoints, and TTL behavior.
- [[dangling-dns-records]] — stale DNS targets and lifecycle failures.
- [[subdomain-takeover|Subdomain Takeover]] — exposure finding when a dangling target is claimable.
- [[external-attack-surface|External Attack Surface]] — DNS as public discoverability layer.
- [[tls-https]] — CAA records, certificate issuance, and domain validation.
- [[reverse-proxies|Reverse Proxies]] — DNS often points users to the edge that enforces proxy controls.
- [[ssrf|SSRF]] — resolver context and DNS rebinding affect URL-fetching risks.

### Suggested future atomic notes

- registrar-security
- dnssec
- spf-dkim-dmarc
- caa-records
- dns-monitoring
- dns-rebinding
- third-party-domain-verification

## References

- **Foundational:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Foundational:** ICANN DNSSEC — https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-05-en
- **Mitigation:** CISA Domain Name System Security Best Practices — https://www.cisa.gov/resources-tools/resources/domain-name-system-dns-security-best-practices
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** HackerOne guide to subdomain takeovers — https://www.hackerone.com/blog/guide-subdomain-takeovers-20
