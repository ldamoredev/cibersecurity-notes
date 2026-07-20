---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Endpoint Discovery

## Definition

Endpoint discovery is the process of finding reachable routes, APIs, handlers, parameters, methods, and hidden request surfaces beyond what the visible UI or official documentation reveals.

## Why it matters

Applications and APIs usually expose more backend surface than the frontend shows. JavaScript bundles, mobile apps, old versions, schemas, hidden parameters, GraphQL fields, archived URLs, and generated clients can reveal routes that bypass normal product flows.

zSecurity's bug bounty curriculum highlights this well: hidden endpoints and hidden parameters are not separate trivia. They are how testers find the real backend shape.

## How it works

Endpoint discovery has **5 source classes**:

1. **Observed traffic.** Browser, mobile, API client, proxy logs, and HAR captures.
2. **Published contracts.** OpenAPI, Swagger, GraphQL, Postman, SDKs, and docs.
3. **Client-side artifacts.** JavaScript bundles, source maps, mobile apps, and route constants.
4. **Historical sources.** Wayback, search engine caches, old docs, and leaked examples.
5. **Guessable patterns.** Wordlists, route families, versions, actions, parameters, and method swaps.

The bug is not that endpoints are discoverable. The bug is that discovered endpoints behave outside the intended authorization, validation, inventory, or lifecycle model.

A worked example, route string to finding:

```
Source:
  static/app.8fd3.js contains "/api/internal/reports/export"

Inventory status:
  absent from public OpenAPI spec

Probe:
  GET returns 401, POST with normal user token returns 403

Follow-up:
  POST with changed method and "include=all" still denies

Conclusion:
  discovered endpoint exists, but current evidence shows authorization holds
```

Endpoint discovery is mature when it can distinguish "new route worth tracking" from "new exploitable route."

## Techniques / patterns

Practitioners test:

- `/api`, `/v1`, `/v2`, `/graphql`, `/internal`, `/admin`, `/debug`
- HTTP method changes on known routes
- route families found in JavaScript bundles
- hidden parameters such as `debug`, `admin`, `role`, `redirect`, `next`, `include`, `expand`, `fields`
- OpenAPI/Swagger and GraphQL introspection exposure
- archived endpoints and mobile-only routes
- content-type changes and alternate parsers

## Variants and bypasses

Endpoint discovery yields **7 endpoint classes**.

### 1. Documented but underprotected endpoints

The route is known but missing expected auth, rate limits, or validation.

### 2. Undocumented active endpoints

The backend route exists but is absent from docs, UI, inventory, and tests.

### 3. Legacy version endpoints

Old API versions remain reachable with weaker controls.

### 4. Client-specific endpoints

Mobile, partner, internal, or admin clients expose alternate behavior.

### 5. Hidden parameter behavior

Parameters alter authorization, fields, debug output, redirects, or workflow behavior.

### 6. GraphQL/schema-discovered fields

Schemas reveal queries, mutations, object fields, or deprecated operations.

### 7. Debug and diagnostic endpoints

Health, metrics, trace, actuator, and debug routes reveal state or control behavior.

## Impact

Ordered roughly by severity:

- **Authorization bypass.** Hidden routes or methods skip policy applied elsewhere.
- **Sensitive data exposure.** Hidden parameters, fields, or schemas reveal extra data.
- **Control-plane exposure.** Admin/debug routes become callable.
- **Version drift exploitation.** Old endpoints preserve old vulnerabilities.
- **Recon acceleration.** Route discovery feeds BOLA, BFLA, mass assignment, SSRF, and injection testing.

## Detection and defense

Ordered by effectiveness:

1.
**Generate and maintain an authoritative route inventory.**
   Compare deployed routes, gateway config, schemas, code, and observed traffic.

2.
**Apply security controls by policy, not by route obscurity.**
   Hidden endpoints should still enforce authentication, authorization, validation, rate limits, and logging.

3.
**Review schemas and client artifacts before publication.**
   Public docs and bundles should not expose internal-only operations or sensitive model details.

4.
**Test route families across methods, versions, and clients.**
   A protected `GET` does not prove `POST`, `PATCH`, mobile, or v1 behavior is safe.

5.
**Fail closed on unknown parameters.**
   Hidden parameters should not silently alter security-relevant behavior.

### What does not work as a primary defense

- **Not linking a route in the UI.** Direct HTTP callers do not need UI links.
- **Assuming API docs are the surface.** JavaScript, mobile apps, schemas, and history reveal more.
- **Security through random path names.** Guessing is only one discovery source.
- **Frontend-only parameter filtering.** Attackers can submit hidden parameters directly.

## Practical labs

Use an owned application or lab.

### Extract routes from JavaScript

```
rg -o '["'\\''`]/[A-Za-z0-9_./{}:-]+' public dist static | sort -u
```

Normalize findings into route, method, source file, and likely owner.

### Compare routes to OpenAPI

```
rg -n "/api/|router\\.|app\\.(get|post|put|patch|delete)" src routes openapi.yaml
```

Find routes present in code but absent from docs, and docs entries with no live route.

### Probe hidden parameters safely

```
curl -i 'https://api.example.test/users/me?debug=true&include=roles,permissions'
```

Look for field expansion, debug output, or policy changes.

### Test method variants

```
for m in GET POST PUT PATCH DELETE OPTIONS; do
  curl -i -X "$m" https://api.example.test/api/users/me
done
```

Every accepted method should have a reason and policy.

### Build an endpoint evidence table

```
endpoint | method | source | documented? | auth result | owner | risk | next test
```

This prevents route discovery from becoming an unstructured pile of URLs.

### Inspect source maps for route families

```
curl -sS https://app.example.test/static/app.js.map | jq -r '.sources[]?' | head
```

Source maps can be legitimate debug artifacts or accidental route/source exposure.

## Practical examples

- A JavaScript bundle exposes `/api/internal/reports`.
- An old `/v1/` endpoint still accepts weaker auth.
- `?debug=true` returns internal fields.
- GraphQL introspection reveals admin mutations.
- A mobile-only endpoint skips CSRF or rate limits.

## Related notes

- [[api-inventory-management|API Inventory Management]]
- [[deprecated-api-versions]]
- [[admin-interface-discovery]]
- [[broken-function-level-authorization|Broken Function Level Authorization]]
- [[public-asset-discovery|Public Asset Discovery]]

### Suggested future atomic notes

- hidden-parameter-discovery
- js-recon
- graphql-introspection-exposure
- openapi-security-review
- route-guessing

## References

- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
