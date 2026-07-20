---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Third-Party Exposure

## Definition

Third-party exposure is the portion of attack surface created by vendors, SaaS platforms, external APIs, CDNs, identity providers, managed services, widgets, and dependencies that handle traffic, content, authentication, or data on your behalf.

## Why it matters

Modern attack surface extends beyond assets an organization hosts directly. DNS, auth providers, observability tools, support platforms, CI/CD services, object storage, analytics scripts, and external APIs can all influence exposure and trust.

Keep the boundary tight: this note is about vendor-connected reachability and trust on exposed surfaces, not the entire software supply-chain problem.

## How it works

Third-party exposure has **5 trust roles**:

1. **Traffic mediator.** CDN, WAF, reverse proxy, load balancer, DNS, or email provider.
2. **Identity mediator.** SSO, OAuth/OIDC provider, MFA vendor, or directory sync.
3. **Content host.** Docs, marketing, support, status, storage, scripts, widgets, and downloads.
4. **Data processor.** Analytics, CRM, ticketing, logs, observability, and external APIs.
5. **Control-plane provider.** CI/CD, cloud, infrastructure, admin tooling, or automation platform.

The risk is that a vendor surface inherits trust from your domain, users, cookies, callbacks, tokens, or data flows.

A worked example, vendor CNAME to trust decision:

```
Host:
  support.example.test

Provider:
  support SaaS via CNAME

Trust role:
  content host + data processor

Data:
  customer attachments and ticket metadata

Technical trust:
  custom domain, SSO callback, email links

Offboarding state:
  vendor contract ended, DNS still points at provider

Decision:
  high-priority offboarding drift: remove DNS, revoke SSO/callbacks, export/delete data, rotate tokens
```

Third-party exposure is mature when each vendor is described by role, data, trust path, and lifecycle state.

## Techniques / patterns

Practitioners look for:

- vendor CNAMEs and custom domains
- OAuth redirect URIs and SSO callback URLs
- external scripts, widgets, iframes, and analytics origins
- CDN origins and cache behavior
- SaaS support/docs/status portals
- public vendor-hosted files and storage
- stale integrations after offboarding
- external APIs trusted without validation

## Variants and bypasses

Third-party exposure appears in **7 forms**.

### 1. Stale SaaS mapping

DNS or custom-domain mappings remain after vendor resources are deleted.

### 2. Overtrusted identity callback

OAuth/OIDC/SAML callbacks, redirect URIs, or tenant settings trust too broad a surface.

### 3. Third-party content execution

Scripts, widgets, or iframes execute in sensitive product contexts.

### 4. CDN and origin confusion

Edge controls are assumed, but origins or alternate routes remain reachable.

### 5. External API trust failure

The application trusts third-party responses without validation, isolation, or failure handling.

### 6. Vendor data exposure

Support, docs, analytics, or observability tools expose data outside intended audience.

### 7. Offboarding drift

Vendors are removed from the business process but remain in DNS, code, OAuth, webhooks, or allowlists.

## Impact

Ordered roughly by severity:

- **Account or token compromise.** Identity callbacks and trusted subdomains become takeover paths.
- **Content injection.** Third-party scripts or stale mappings serve attacker-controlled content.
- **Data disclosure.** Vendor-hosted logs, tickets, files, or analytics expose sensitive data.
- **Control-plane compromise.** CI/CD, cloud, or automation vendors influence production systems.
- **Availability and integrity failures.** External API failure or manipulation affects core workflows.

## Detection and defense

Ordered by effectiveness:

1.
**Inventory third parties by trust role and data sensitivity.**
   Vendor lists are not enough; capture what each provider can influence.

2.
**Tie vendor onboarding/offboarding to DNS, callbacks, tokens, and code.**
   Removing a vendor from procurement does not remove its technical trust paths.

3.
**Constrain identity and callback allowlists tightly.**
   OAuth/OIDC/SAML redirects and webhooks should use exact origins and paths where possible.

4.
**Review external content execution.**
   Third-party scripts, widgets, and iframes need CSP, subresource integrity where feasible, isolation, and ownership.

5.
**Validate and isolate external API consumption.**
   Treat third-party API responses as untrusted input and define failure behavior.

6.
**Monitor vendor-hosted domains and custom mappings.**
   Stale CNAMEs and changed provider states should trigger review.

### What does not work as a primary defense

- **Vendor trust as a blanket statement.** Trust depends on the specific role, data, and control path.
- **Offboarding without technical cleanup.** DNS, OAuth, webhooks, API keys, and scripts often remain.
- **Wildcard redirect or CORS rules.** Broad trust amplifies stale or compromised third-party surfaces.
- **Assuming CDN equals origin protection.** Direct origin paths can bypass edge controls.

## Practical labs

Use owned apps and vendor configurations.

### Map vendor DNS

```
while read host; do
  dig CNAME "$host" +short | sed "s|^|$host -> |"
done < subdomains.txt
```

Tag each provider, owner, and business purpose.

### Inventory external browser origins

```
curl -s https://app.example.test/ | rg -o 'https://[^"]+' | sort -u
```

Review scripts, frames, images, APIs, and analytics origins.

### Review OAuth redirect surfaces

```
client_id | redirect_uri | owner | environment | exact/wildcard | still needed
```

Wildcard or stale redirect URIs deserve immediate attention.

### Check stale webhook/callback paths

```
rg -n "webhook|callback|redirect_uri|saml|oauth|oidc|vendor|stripe|slack|zendesk" src config docs
```

Code and docs often preserve old integrations.

### Build a vendor trust register

```
vendor | role | domain/path | data handled | auth/callbacks | owner | offboarding steps
```

Vendor inventory needs technical trust paths, not only procurement names.

### Review external script privileges

```
curl -s https://app.example.test/ \
  | rg -o '<script[^>]+src="https://[^"]+"' \
  | sort -u
```

Every external script origin can execute in a browser context you own.

## Practical examples

- A deleted SaaS mapping leaves a claimable subdomain.
- An external API integration is trusted too broadly.
- A third-party file or widget origin widens exposure unexpectedly.
- An OAuth redirect URI points to a stale environment.
- A support portal exposes customer attachments.

## Related notes

- [[subdomain-takeover|Subdomain Takeover]]
- [[external-attack-surface]]
- [[api-inventory-management|API Inventory Management]]
- [[api-security-top-10|API Security Top 10]]
- [[supply-chain-security|Supply Chain Security]]

### Suggested future atomic notes

- oauth-redirect-uri-inventory
- third-party-script-risk
- webhook-exposure
- vendor-offboarding-security
- cdn-origin-exposure

## References

- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP API10:2023 Unsafe Consumption of APIs — https://owasp.org/API-Security/editions/2023/en/0xaa-unsafe-consumption-of-apis/
- **Research / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
