---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# API Rate Limiting

## Definition

API rate limiting is the set of controls that restrict how often a client, identity, token, source, tenant, or workflow can consume API resources within a period.

## Why it matters

APIs are meant to be called programmatically, which means abuse can happen at machine speed. Weak limits enable credential attacks, scraping, enumeration, cost spikes, expensive report generation, inventory exhaustion, and denial-of-wallet incidents even when no classic injection bug exists.

Rate limiting belongs near [[broken-authentication]], [[api-inventory-management]], and [[client-ip-trust|Client IP Trust]] because the key question is: which identity or resource is actually being protected?

## How it works

Useful API limits combine **4 limit keys**:

1. **Source limits.** IP address, ASN, region, proxy reputation, or network edge identity.
2. **Caller limits.** Account, user, tenant, client ID, API key, or token subject.
3. **Route limits.** Endpoint, method, action, workflow, or resource type.
4. **Cost limits.** Search complexity, export size, report cost, file size, or downstream spend.

The bug is usually choosing only one key. Per-IP limits fail under distributed abuse; per-account limits miss anonymous endpoints; route limits miss expensive parameters.

Example policy shape:

```
POST /auth/login      -> per account + per IP + credential pair
GET /search           -> per account + query cost + tenant quota
POST /reports/export  -> per account + report cost + concurrency
POST /auth/refresh    -> per refresh token family + account + anomaly signals
```

## Techniques / patterns

Attackers test:

- burst capacity and sustained request rate
- per-IP vs per-account vs per-token enforcement
- alternate API versions, mobile routes, GraphQL endpoints, and batch routes
- spoofed or trusted proxy headers
- login, reset, MFA, and refresh endpoints
- high-cost search, export, report, file, and AI/model endpoints
- whether limits reset on token rotation or account switching

## Variants and bypasses

Rate limit failures appear in **7 forms**.

### 1. IP-only limiting

Attackers rotate IPs or exploit proxy-header trust issues.

### 2. Account-only limiting

Anonymous or credential-stuffing flows bypass limits by changing target accounts or credentials.

### 3. Route inconsistency

The main endpoint is limited, but mobile, versioned, GraphQL, batch, or export routes are not.

### 4. Cost-blind limits

Every request counts as one even when some requests trigger expensive work.

### 5. Token-reset bypass

Refreshing or reissuing tokens resets counters improperly.

### 6. Distributed enforcement lag

Multiple gateways or services maintain inconsistent counters.

### 7. Concurrency gaps

The API limits request count but not simultaneous jobs, exports, or background tasks.

## Impact

Ordered roughly by severity:

- **Credential compromise.** Brute force, credential stuffing, reset-token guessing, or MFA fatigue.
- **Data scraping and enumeration.** Search, list, and detail endpoints leak at scale.
- **Resource exhaustion.** CPU, database, queue, storage, email, SMS, or third-party API costs spike.
- **Denial of wallet.** Expensive downstream services are consumed by abuse.
- **Reliability degradation.** Legitimate users are slowed or blocked by unbounded callers.

## Detection and defense

Ordered by effectiveness:

1.
**Define the protected resource before choosing the limit key.**
   Login protects accounts and credentials; exports protect data volume and backend jobs; search protects query cost and scraping surface.

2.
**Combine source, caller, route, and cost-aware limits.**
   Layered keys make common bypasses harder and reduce false positives.

3.
**Enforce limits at the edge and in the application.**
   Gateways are useful for coarse controls; application logic understands accounts, tenants, workflows, and business cost.

4.
**Normalize and trust client IPs only through known proxy chains.**
   Rate limits based on spoofable `X-Forwarded-For` are easy to bypass.

5.
**Add concurrency and job limits for expensive operations.**
   Reports, exports, imports, file processing, and AI/model calls need more than request-per-minute limits.

6.
**Monitor denials, near-limits, and distributed patterns.**
   Abuse often appears as many callers staying just under a simple threshold.

### What does not work as a primary defense

- **Per-IP limits alone.** Cloud, proxy, and bot traffic make IP a weak identity by itself.
- **CORS.** Non-browser clients ignore it, and browser origin control is not abuse control.
- **Frontend pacing.** Attackers call the API directly.
- **One global limit for every route.** Expensive and security-sensitive routes need different policies.
- **Trusting client-supplied IP headers.** Only headers inserted by known proxies should influence identity.

## Practical labs

Use only owned systems or lab targets, and keep request volumes low.

### Identify limit keys from responses

```
curl -i -H "Authorization: Bearer $USER" https://api.example.test/search?q=test
```

Record `429` behavior, `Retry-After`, rate-limit headers, and whether counters seem per IP, account, token, or route.

### Test per-account vs per-IP safely

```
for i in 1 2 3 4 5; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $USER" \
    https://api.example.test/auth/refresh
done
```

Observe whether the policy is documented and stable; do not generate disruptive volume.

### Test proxy-header trust in a lab

```
curl -i -H 'X-Forwarded-For: 203.0.113.10' \
  https://api.example.test/rate-limit-demo
```

Changing untrusted headers should not change the caller identity.

### Test cost-aware limits

```
curl -i -H "Authorization: Bearer $USER" \
  'https://api.example.test/search?q=a&limit=1000&include=deep'
```

High-cost parameters should have stricter limits than cheap reads.

## Practical examples

- Login endpoints allow unlimited credential attempts.
- Search can be scraped at high volume because only write routes are limited.
- `X-Forwarded-For` spoofing bypasses per-IP controls.
- Report generation allows many concurrent expensive jobs.
- Refreshing a token resets counters and enables sustained abuse.

## Related notes

- [[client-ip-trust|Client IP Trust]]
- [[broken-authentication]]
- [[api-auth-flaws]]
- [[api-inventory-management]]
- [[test-client-ip-spoofing|Test Client IP Spoofing]]

### Suggested future atomic notes

- cost-aware-rate-limiting
- credential-stuffing-rate-limits
- rate-limit-key-design
- graphql-rate-limiting
- concurrency-limits

## References

- **Foundational:** OWASP API4:2023 Unrestricted Resource Consumption — https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
