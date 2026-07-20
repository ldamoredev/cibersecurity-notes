---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Subdomain Takeover

## Definition

Subdomain takeover is an exposure condition where a DNS name points to infrastructure or a third-party service relationship that no longer exists, allowing another party to claim the target and serve content under the trusted subdomain.

## Why it matters

Subdomain takeover is asset lifecycle drift made visible. The domain is still trusted by users, browsers, cookies, CORS rules, OAuth redirects, allowlists, and brand expectations, but the backing service has been deleted or abandoned.

[[dangling-dns-records|Dangling DNS Records]] owns the DNS hygiene mechanism. This note owns the attack-surface finding: whether a dangling mapping is claimable and security-relevant.

## How it works

Takeover requires **4 conditions**:

1. **A trusted subdomain exists.** Example: `help.example.test`.
2. **DNS points to an external or deprovisioned target.** Usually CNAME, ALIAS, or cloud-hosted service mapping.
3. **The target is unclaimed or claimable.** The provider lets a new account create the missing resource.
4. **The subdomain has trust value.** Users, cookies, OAuth, CORS, CSP, links, email, or brand trust make control meaningful.

The bug is not just a stale DNS record. It is a stale name plus a claimable backing service plus trust attached to the name.

A worked example, stale DNS to severity:

```
Name:
  help.example.test

DNS:
  CNAME old-helpdesk.vendor.example

HTTP behavior:
  provider returns "project not found"

Claimability:
  provider docs say custom domain must be bound before serving traffic

Trust amplification:
  password reset emails link to help.example.test articles, but no cookies or OAuth redirects use it

Triage:
  likely brand/content takeover risk, lower than account-compromise unless trust paths are found
```

The mature decision is not "takeover yes/no"; it is claimability plus trust amplification plus safe proof.

## Techniques / patterns

Practitioners look for:

- CNAMEs to SaaS/cloud providers returning "not found" or "no such app" errors
- cloud apps deleted without DNS cleanup
- marketing, docs, support, preview, and staging subdomains
- old vendor onboarding records and verification tokens
- names included in OAuth redirect allowlists, CORS allowlists, cookies, or CSP
- certificate transparency names with provider-specific CNAMEs

## Variants and bypasses

Subdomain takeover appears in **6 forms**.

### 1. Deleted cloud app mapping

The DNS name points to a deleted Heroku, Azure, Netlify, Vercel, S3/static site, or similar resource.

### 2. Abandoned SaaS integration

A support, docs, status, marketing, or ticketing platform mapping remains after offboarding.

### 3. Expired custom domain binding

The provider no longer has a valid owner binding for the custom domain.

### 4. Stale verification record

TXT or CNAME verification artifacts remain and can help claim or validate ownership elsewhere.

### 5. Wildcard or shared-service confusion

Wildcard DNS or shared provider routing sends many names to claimable resources.

### 6. Trust amplification

The takeover becomes more severe because cookies, CORS, OAuth, CSP, links, or user trust include the subdomain.

## Impact

Ordered roughly by severity:

- **Account compromise path.** OAuth redirects, password reset links, or trusted cookies interact with the controlled subdomain.
- **Phishing and brand abuse.** The attacker serves trusted-looking content on a real subdomain.
- **Data or token theft.** Overbroad cookies, CORS, or redirects leak sensitive material.
- **Content integrity failure.** Docs, downloads, scripts, or support pages can be replaced.
- **Recon pivot.** The takeover confirms asset lifecycle weakness and may reveal other stale mappings.

## Detection and defense

Ordered by effectiveness:

1.
**Tie DNS cleanup to resource deprovisioning.**
   Deleting a cloud app or SaaS integration should remove custom domains and DNS records in the same workflow.

2.
**Continuously scan DNS targets for provider-specific claimable states.**
   Stale records appear after normal business changes, not only during migrations.

3.
**Track third-party custom-domain ownership.**
   Inventory should know which provider owns each mapping and how ownership is verified.

4.
**Reduce trust attached to broad subdomains.**
   Avoid overbroad cookies, CORS, OAuth redirects, and CSP rules that include many subdomains.

5.
**Verify suspected takeovers safely.**
   In bug bounty or internal testing, follow provider-safe proof methods and avoid serving deceptive content.

### What does not work as a primary defense

- **Deleting the backend resource only.** DNS can keep pointing to the now-claimable target.
- **Assuming all dangling records are exploitable.** Claimability depends on provider behavior and ownership checks.
- **Wildcard trust.** `*.example.com` in cookies, CORS, CSP, or OAuth can amplify a single stale name.
- **Manual DNS review once a year.** Stale records appear continuously.

## Practical labs

Use owned domains or explicit bug bounty scope.

### Find provider CNAMEs

```
dig CNAME help.example.test +short
dig CNAME docs.example.test +short
```

Record provider targets and expected owners.

### Compare DNS target to HTTP behavior

```
curl -i https://help.example.test/
```

Look for provider-specific unclaimed or missing-project messages, then confirm against provider documentation.

### Check trust amplification

```
curl -I https://app.example.test/ | rg -i "set-cookie|access-control|content-security-policy"
```

Cookies, CORS, and CSP can make a takeover more severe.

### Sweep subdomains for provider errors

```
while read host; do
  curl -m 5 -ks -I "https://$host" | head -n 1 | sed "s|^|$host |"
done < subdomains.txt
```

Use low volume and owned scope.

### Build a takeover confidence table

```
host | DNS target | provider | error text | claimability evidence | trust paths | confidence
```

Provider error pages alone are not enough; pair them with provider behavior and trust evidence.

### Review cookie and OAuth scope

```
Cookie Domain attributes:
OAuth redirect URIs:
CORS allowed origins:
CSP script/connect/frame sources:
Password reset links:
```

These decide whether a stale subdomain is only content risk or an account-risk path.

## Practical examples

- A subdomain still points to a deleted cloud app.
- A SaaS integration hostname remains live in DNS after offboarding.
- A bug bounty hunter claims a stale service mapping and serves proof content.
- An OAuth allowlist includes a takeover-prone subdomain.
- A broad cookie domain sends cookies to a controlled subdomain.

## Related notes

- [[dangling-dns-records|Dangling DNS Records]]
- [[dns-security|DNS Security]]
- [[third-party-exposure]]
- [[external-attack-surface]]
- [[subdomain-enumeration|Subdomain Enumeration]]

### Suggested future atomic notes

- provider-specific-takeover-fingerprints
- custom-domain-ownership
- oauth-redirect-subdomain-risk
- wildcard-cookie-risk
- safe-takeover-proof

## References

- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers / subdomain takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
