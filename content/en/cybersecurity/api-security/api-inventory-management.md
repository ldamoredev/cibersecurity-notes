---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# API Inventory Management

## Definition

API inventory management is the practice of knowing which API hosts, versions, routes, schemas, clients, environments, and owners exist, are reachable, and are still supposed to exist.

## Why it matters

A lot of API risk is exposure drift rather than one dramatic vulnerability. Old versions, undocumented endpoints, mobile-only routes, internal hosts, forgotten staging systems, and stale schemas create attack surface long after teams stop thinking about them.

For APIs, inventory management sits between [[api-security-top-10]] and attack surface mapping. Machine clients can keep calling deprecated routes even after the product UI stops using them.

## How it works

Strong API inventory tracks **5 dimensions**:

1. **Hosts and environments.** Production, staging, dev, internal, partner, regional, and temporary hosts.
2. **Versions and lifecycles.** `v1`, `v2`, beta, deprecated, sunset, and legacy routes.
3. **Routes and methods.** Path, HTTP method, GraphQL operation, RPC method, or event endpoint.
4. **Schemas and contracts.** OpenAPI, GraphQL schema, protobuf, request/response DTOs, and generated clients.
5. **Owners and consumers.** Team, service owner, client app, integration, tenant, and intended exposure.

The bug is not simply "an endpoint exists." The bug is that nobody knows whether it should exist, who owns it, or what security controls it is supposed to have.

## Techniques / patterns

Attackers and defenders look for:

- `/api/v1`, `/api/v2`, `/beta`, `/internal`, `/admin`, `/mobile`, `/partner`
- OpenAPI, Swagger UI, GraphQL introspection, Postman collections, and client SDKs
- JavaScript bundle route strings and mobile traffic
- staging, preview, regional, and forgotten cloud hosts
- mismatches between docs, frontend calls, and backend availability
- legacy routes with weaker auth, validation, or rate limits

## Variants and bypasses

Inventory failures appear in **7 forms**.

### 1. Zombie versions

Deprecated API versions remain reachable and weakly maintained.

### 2. Shadow endpoints

Routes exist in code or gateways but not in documentation or tests.

### 3. Environment exposure

Staging, dev, preview, or internal hosts are internet reachable.

### 4. Client-specific drift

Mobile, partner, or legacy clients call routes with weaker controls than the primary web app.

### 5. Schema leakage

Docs, introspection, or generated clients expose sensitive routes and data models.

### 6. Ownership gaps

No team owns a route, token, host, or version, so security fixes do not land.

### 7. Gateway/backend mismatch

The gateway inventory differs from what backend services actually expose.

## Impact

Ordered roughly by severity:

- **Unauthorized access through old routes.** Legacy endpoints may miss current auth or authorization controls.
- **Data exposure.** Stale schemas, verbose responses, and debug endpoints leak sensitive fields.
- **Control-plane exposure.** Internal or admin APIs become externally reachable.
- **Patch bypass.** Fixes land in current APIs while old versions remain vulnerable.
- **Monitoring blind spots.** Unknown endpoints are not logged, tested, or rate-limited properly.

## Detection and defense

Ordered by effectiveness:

1.
**Maintain a living API inventory from multiple sources.**
   Combine gateway config, service routes, OpenAPI/GraphQL schemas, traffic logs, cloud assets, and client usage. One source will miss drift.

2.
**Assign an owner and lifecycle state to every API surface.**
   Each route and host should have an owner, intended exposure, auth model, version, and deprecation state.

3.
**Continuously compare documented, deployed, and observed APIs.**
   Differences between specs, code, gateway, and traffic are where forgotten risk hides.

4.
**Retire versions with explicit sunset plans.**
   Deprecation without removal leaves attackers a long-lived compatibility layer.

5.
**Gate sensitive documentation and introspection.**
   Docs are valuable, but public schemas should not expose internal-only operations or hidden models.

6.
**Fold inventory into security testing.**
   Unknown routes should trigger review for auth, authorization, rate limiting, logging, and data exposure.

### What does not work as a primary defense

- **Assuming documentation is complete.** Attackers test what is reachable, not what is documented.
- **Removing UI links.** Machine clients can call old routes directly.
- **Gateway-only inventories.** Backend services may expose routes outside the gateway or behind alternate hosts.
- **Indefinite backward compatibility.** Old versions become permanent attack surface.
- **Security reviews only at launch.** API surface changes continuously.

## Practical labs

Use only systems you own or have explicit permission to assess.

### Build an endpoint inventory from code

```
rg -n "app\\.(get|post|put|patch|delete)|router\\.|@Get|@Post|@RequestMapping|graphql" src routes
```

Normalize findings into host, version, route, method, owner, auth requirement, and lifecycle state.

### Compare docs to traffic

```
rg -n "/api/|swagger|openapi|graphql" public src mobile openapi.yaml
```

Look for routes used by clients but absent from the official schema, and schema routes not used by clients.

### Probe version exposure safely

```
for v in v1 v2 beta internal partner mobile; do
  curl -i "https://api.example.test/api/$v/health"
done
```

The goal is inventory and reachability, not volume.

### Check documentation exposure

```
curl -i https://api.example.test/swagger.json
curl -i https://api.example.test/graphql
```

Public docs should match intentional exposure and not reveal internal-only operations.

## Practical examples

- `/api/v1/` still works after migration to v2.
- Mobile APIs expose routes the web client never calls.
- Staging endpoints are internet-facing and forgotten.
- Swagger exposes internal admin operations.
- A gateway blocks `/admin`, but the backend service is reachable on another host.

## Related notes

- [[api-security-top-10]]
- [[api-rate-limiting]]
- [[excessive-data-exposure]]
- [[endpoint-discovery|Endpoint Discovery]]
- [[external-attack-surface|External Attack Surface]]
- [[http-overview|HTTP Overview]]

### Suggested future atomic notes

- api-version-sunsetting
- shadow-api-discovery
- openapi-security-review
- graphql-introspection-exposure
- staging-api-exposure

## References

- **Foundational:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing and OWASP alignment — https://portswigger.net/web-security/api-testing/top-10-api-vulnerabilities
