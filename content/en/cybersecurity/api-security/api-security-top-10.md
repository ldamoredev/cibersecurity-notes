---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# API Security Top 10

## Definition

The OWASP API Security Top 10 is a focused awareness framework for the most important API-specific security risk categories. It complements broader web security guidance by emphasizing object access, function exposure, property control, resource consumption, and API inventory drift.

## Why it matters

APIs expose business objects, identifiers, machine-readable data, backend functions, and integration surfaces more directly than most browser UIs. This changes how attackers enumerate systems and how defenders should think about trust boundaries.

This page is the API branch map. Individual notes carry the operational detail: [[authorization]], [[broken-object-level-authorization]], [[broken-authentication]], [[broken-object-property-level-authorization]], [[api-rate-limiting]], [[broken-function-level-authorization]], [[api-inventory-management]], and [[polymorphic-deserialization]].

## How it works

The 2023 API Top 10 can be held as **5 API security questions**:

1. **Who can access which object?** BOLA and object authorization.
2. **Who can invoke which function?** BFLA and workflow/action authorization.
3. **Which properties cross the boundary?** BOPLA, excessive exposure, and mass assignment.
4. **How much can callers consume?** Rate limits, cost controls, and unrestricted resource consumption.
5. **What API surface exists?** Inventory, versions, misconfiguration, and unsafe consumption.

This framing is more useful than memorizing the list because most API reviews involve these questions repeatedly.

## Techniques / patterns

Attackers use APIs because:

- object identifiers are easier to manipulate directly
- functions are callable without the frontend
- machine-readable responses are easy to diff and automate
- undocumented or legacy endpoints often remain reachable
- mobile and partner clients reveal alternate API paths
- schemas and docs reveal route, field, and model structure

## Variants and bypasses

The OWASP API Top 10 2023 categories are:

1.
**API1: Broken Object Level Authorization.**
   Object references are accessible without per-object authorization.

2.
**API2: Broken Authentication.**
   Identity, credentials, tokens, or auth workflows are weak or inconsistent.

3.
**API3: Broken Object Property Level Authorization.**
   APIs expose or accept properties the caller should not see or control.

4.
**API4: Unrestricted Resource Consumption.**
   Callers can consume too much compute, memory, storage, downstream cost, or business resource.

5.
**API5: Broken Function Level Authorization.**
   Callers invoke functions their role or state should not allow.

6.
**API6: Unrestricted Access to Sensitive Business Flows.**
   Business workflows can be automated or abused at scale even without a classic technical bug.

7.
**API7: Server Side Request Forgery.**
   API-controlled URL fetches reach internal or unintended network resources.

8.
**API8: Security Misconfiguration.**
   Unsafe defaults, verbose errors, weak headers, permissive parsers, or exposed management surfaces increase risk.

9.
**API9: Improper Inventory Management.**
   Unknown versions, hosts, environments, or routes remain reachable.

10.
**API10: Unsafe Consumption of APIs.**
    An API trusts upstream or third-party APIs without enough validation, isolation, or failure handling.

## Impact

Ordered roughly by severity:

- **Tenant and account compromise.** Object, function, and property authorization failures cross account boundaries.
- **Account takeover or persistence.** Auth and token flaws allow unauthorized access or long-lived access.
- **Sensitive data exposure.** Responses, exports, schemas, and debug output leak data.
- **Business abuse.** Workflows, quotas, inventory, pricing, or approvals are automated or manipulated.
- **Infrastructure and cost damage.** Resource exhaustion, SSRF, and misconfiguration reach backend systems or create large spend.

## Detection and defense

Ordered by effectiveness:

1.
**Threat-model APIs by object, function, property, resource, and inventory.**
   These five questions catch most API-specific risk during design and review.

2.
**Build authorization and authentication tests as matrices.**
   Use multiple users, roles, tenants, token states, and API versions. Single-user happy-path tests miss API security bugs.

3.
**Use explicit request and response contracts.**
   DTOs, schemas, and field policies reduce mass assignment and excessive exposure.

4.
**Inventory and monitor deployed API surface continuously.**
   Security depends on what is reachable, not only what is documented.

5.
**Apply abuse controls to high-value and high-cost workflows.**
   Rate limits, concurrency limits, quotas, and anomaly detection belong on business flows, not only login.

6.
**Treat API dependencies and parsers as trust boundaries.**
   Validate inbound and outbound API data, avoid unsafe deserialization, and isolate third-party failures.

### What does not work as a primary defense

- **Frontend-only controls.** APIs are directly callable.
- **Authentication alone.** Logged-in users still need object, function, and property authorization.
- **Documentation-only inventory.** Attackers enumerate deployed surface.
- **Generic WAF coverage.** API bugs are often business-logic and authorization failures.
- **One-time launch review.** API surface and clients drift continuously.

## Practical labs

Use an owned API, training lab, or intentionally vulnerable app.

### Build an OWASP API review matrix

```
endpoint | object auth | function auth | property read/write | rate/cost | version/owner
```

Fill it for the most sensitive endpoints first.

### Map one endpoint to the five questions

```
POST /api/projects/{id}/members
object: can caller access project?
function: can caller invite members?
properties: can caller set role/status?
resource: are invites limited?
inventory: does v1/mobile behave the same?
```

This creates a reusable review habit.

### Compare deployed routes to docs

```
rg -n "/api/|router\\.|app\\.(get|post|put|patch|delete)" src routes openapi.yaml
```

Look for routes missing from docs or tests.

## Practical examples

- The UI hides fields the API still returns.
- Admin-only actions are callable directly by a normal client.
- Old API versions remain deployed and discoverable.
- A report endpoint can be triggered repeatedly to create high backend cost.
- An API fetches attacker-provided URLs from inside the network.

## Related notes

- [[authorization]]
- [[broken-object-level-authorization]]
- [[broken-authentication]]
- [[broken-object-property-level-authorization]]
- [[api-rate-limiting]]
- [[broken-function-level-authorization]]
- [[api-inventory-management]]
- [[polymorphic-deserialization]]

### Suggested future atomic notes

- unrestricted-access-to-sensitive-business-flows
- api-ssrf
- api-security-misconfiguration
- unsafe-consumption-of-apis
- api-security-review-matrix

## References

- **Foundational:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x00-header/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
