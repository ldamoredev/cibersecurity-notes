---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Enumeration

## Definition

Enumeration is the focused, methodical expansion of discovered leads into concrete, validated knowledge about reachable services, routes, identities, parameters, versions, and behaviors.

## Why it matters

Recon finds candidate assets. Enumeration turns candidates into actionable understanding: what is live, what responds, what the surface contains, and what merits deeper testing.

Operationally, this sits between broad recon and validation. [[subdomain-enumeration]] and [[host-and-port-discovery]] expand the target set, while [[service-validation]] confirms which findings deserve testing time.

## How it works

Enumeration asks **5 expansion questions**:

1. **What names exist?** Domains, subdomains, virtual hosts, and aliases.
2. **What answers?** Live hosts, ports, protocols, HTTP apps, APIs, and storage.
3. **What routes exist?** Paths, methods, parameters, versions, schemas, and hidden endpoints.
4. **What identities or roles exist?** Login surfaces, tenant hints, usernames, public roles, and support contacts.
5. **What patterns repeat?** Naming, stack, routes, environments, and ownership clues.

The bug in enumeration is collecting huge lists without validating or prioritizing them.

A worked example, enumeration to test queue:

```
Input:
  api-preview.example.test is live and in scope

Expansion:
  JS bundle reveals /api/v1/users/{id}, /api/v1/admin/export, /api/v2/search

Validation:
  normal user gets 200 on /users/{own_id}, 403 on /admin/export, 200 on /search

Classification:
  object-ID route, admin function, search endpoint

Handoff:
  /users/{id} -> BOLA/IDOR testing
  /admin/export -> BFLA/access-control testing
  /search -> injection/rate-limit review
```

Enumeration is mature when it sorts findings by likely test class instead of only increasing count.

## Techniques / patterns

Practitioners enumerate:

- subdomains and DNS records
- hosts, ports, virtual hosts, and services
- web paths, API routes, GraphQL schemas, and parameters
- technology fingerprints and default endpoints
- user/tenant/account clues where ethical and in scope
- staging, legacy, admin, and support surfaces

## Variants and bypasses

Enumeration has **6 streams**.

### 1. Name enumeration

Subdomains, hostnames, virtual hosts, and DNS aliases.

### 2. Network enumeration

Live hosts, ports, protocols, and service banners.

### 3. Web route enumeration

Paths, methods, redirects, status codes, and content patterns.

### 4. API enumeration

Versions, schemas, endpoints, fields, parameters, and auth states.

### 5. Technology enumeration

Frameworks, edge providers, cloud services, versions, and default paths.

### 6. Context enumeration

Business flows, roles, tenants, vendors, and support/admin functions.

## Impact

Ordered roughly by severity:

- **Target prioritization.** Enumeration identifies assets likely to contain real findings.
- **Hidden surface discovery.** Routes, versions, and parameters become visible.
- **Attack-path selection.** Findings route into BOLA, BFLA, SSRF, SQLi, XSS, or misconfiguration testing.
- **Inventory correction.** Defenders see what outsiders can enumerate.
- **Evidence quality.** Validated enumeration creates reproducible testing inputs.

## Detection and defense

Ordered by effectiveness:

1.
**Run controlled enumeration against owned assets.**
   Defensive enumeration prevents surprise exposure.

2.
**Feed results into inventory and ownership.**
   Enumeration without ownership becomes a pile of text.

3.
**Harden hidden and default surfaces.**
   Hidden routes, default pages, and old versions need real controls.

4.
**Monitor enumeration patterns.**
   Many 404s, route guessing, vhost probes, and parameter probing are useful signals.

5.
**Reduce unnecessary discoverability while preserving real controls.**
   Less noise helps, but authorization and exposure control matter more than hiding.

### What does not work as a primary defense

- **Relying on obscurity.** Enumeration is designed to find unlinked surfaces.
- **Rate limiting only by IP.** Distributed enumeration can stay low and broad.
- **Treating 404s as harmless.** Patterns of misses often reveal active enumeration.
- **Assuming docs are complete.** Enumeration tests deployed reality.

## Practical labs

Use owned targets.

### Build an enumeration pipeline table

```
lead | stream | evidence | validation | risk hint | next step
```

Keep evidence and next action together.

### Enumerate route patterns from code/artifacts

```
rg -o '["'\\''`]/[A-Za-z0-9_./{}:-]+' public dist src | sort -u
```

Classify routes by app, API, admin, debug, or unknown.

### Group findings by likely test class

```
admin route -> access control / BFLA
object id route -> BOLA / IDOR
url fetch route -> SSRF
file route -> path traversal / file access
search route -> injection / rate limits
```

The handoff matters as much as the list.

### Preserve enumeration state

```
asset | stream | candidate | verified? | auth state | likely class | next test
```

This keeps broad enumeration from losing context.

### Compare authenticated and unauthenticated views

```
curl -i https://app.example.test/api/profile
curl -i -H "Authorization: Bearer $TOKEN" https://app.example.test/api/profile
```

Different auth states often reveal different route families and controls.

## Practical examples

- Enumerating subdomains reveals live staging and admin hosts.
- Route validation identifies assets worth manual testing.
- Enumeration finds mismatch between docs and deployed API.
- Hidden parameters change response fields.
- High-port services reveal dashboards and vendor products.

## Related notes

- [[recon]]
- [[subdomain-enumeration]]
- [[host-and-port-discovery]]
- [[service-validation]]
- [[recon-to-testing-handoff]]

### Suggested future atomic notes

- wordlist-strategy
- route-guessing
- hidden-parameter-discovery
- api-enumeration
- enumeration-evidence-quality

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
