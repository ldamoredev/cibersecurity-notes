---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Broken Function Level Authorization

## Definition

Broken Function Level Authorization (BFLA) occurs when an API lets a caller invoke an operation, route, method, or workflow action that their role or context should not be allowed to perform.

## Why it matters

APIs expose business functions directly: approve, refund, export, invite, suspend, impersonate, delete, publish, sync. If those functions rely on UI visibility, route obscurity, or inconsistent middleware, normal clients can call privileged operations directly.

BFLA is different from [[broken-object-level-authorization]]: the problem is not only which object is targeted, but whether the caller may invoke the function at all.

## How it works

BFLA has **4 steps**:

1. A privileged function exists in the backend.
2. The route, method, action parameter, or GraphQL mutation is discoverable.
3. The server authenticates the caller but does not enforce the required privilege.
4. The function executes for the wrong role or workflow state.

Example:

```
POST /api/admin/users/123/disable HTTP/1.1
Authorization: Bearer normal-user-token
```

If the handler checks only "logged in", the normal user performs an admin action.

## Techniques / patterns

Attackers test:

- `/admin`, `/manage`, `/internal`, `/support`, `/moderation`, `/ops`
- HTTP method changes: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- hidden actions in JavaScript, mobile apps, OpenAPI schemas, and GraphQL introspection
- role-only buttons disabled in the UI but backed by callable routes
- alternate API versions and mobile/internal clients
- workflow transitions: approve, reject, refund, publish, suspend, invite, export

## Variants and bypasses

BFLA appears in **6 forms**.

### 1. Admin route exposure

Admin/support routes exist and are reachable by lower-privilege users.

### 2. Method confusion

One method on a resource is protected while another method on the same route is not.

### 3. Action-parameter abuse

A generic endpoint accepts `action=approve` or `operation=delete` without per-action authorization.

### 4. Alternate client path

Mobile, partner, legacy, or internal clients expose weaker route gating than the web UI.

### 5. Workflow-state bypass

The caller can invoke a function before prerequisites are complete or after a state should be locked.

### 6. GraphQL mutation exposure

Queries may be safe, but mutations or admin fields are callable without resolver-level checks.

## Impact

Ordered roughly by severity:

- **Privilege escalation.** Normal users perform admin or support actions.
- **Destructive operations.** Delete, suspend, refund, reset, revoke, or publish actions execute improperly.
- **Sensitive exports.** Reports or exports bypass object-by-object policy.
- **Workflow abuse.** Approvals, invites, payouts, or state transitions are forced.
- **Control-plane compromise.** Internal or operator functions become public API surface.

## Detection and defense

Ordered by effectiveness:

1.
**Define function-level permissions explicitly.**
   Every privileged operation should map to a named permission or policy, not just a route prefix.

2.
**Enforce authorization in server-side handlers/resolvers.**
   UI hiding, disabled buttons, and frontend role checks are irrelevant to direct API callers.

3.
**Protect every method and action variant.**
   Review `GET/POST/PATCH/DELETE`, batch actions, imports/exports, and generic action fields separately.

4.
**Keep admin/support/internal APIs behind strong boundaries and policy.**
   Network restriction helps, but function-level checks still belong in the server.

5.
**Test with role-downgraded tokens.**
   Try every privileged function with normal, read-only, expired, and wrong-tenant identities.

6.
**Log denied sensitive actions.**
   Attempts to invoke privileged operations are high-signal abuse indicators.

### What does not work as a primary defense

- **Hiding admin routes.** Routes leak through JS, mobile apps, docs, traffic, and guessing.
- **Checking only route prefixes.** Privileged functions often appear under normal route families.
- **Trusting client role claims.** The server must derive and enforce role/permission.
- **Returning 404 for all denials.** Camouflage without policy is still broken.

## Practical labs

Use normal and privileged accounts.

### Discover function surfaces

```
rg -n "admin|disable|approve|refund|export|invite|impersonate|delete" app.js src/ openapi.yaml
```

Look in routes, schemas, client bundles, and mobile traffic.

### Replay privileged route with normal token

```
curl -i -X POST -H "Authorization: Bearer $NORMAL" \
  https://api.example.test/admin/users/123/disable
```

Expected: `403` without side effects.

### Test method confusion

```
for method in GET POST PUT PATCH DELETE; do
  curl -i -X "$method" -H "Authorization: Bearer $NORMAL" \
    https://api.example.test/users/123
done
```

Each method needs its own authorization decision.

### Test action parameter abuse

```
curl -i -X POST -H "Authorization: Bearer $NORMAL" \
  -H 'Content-Type: application/json' \
  -d '{"action":"approve","targetUserId":"123"}' \
  https://api.example.test/workflows
```

Generic action endpoints are BFLA magnets.

## Practical examples

- A normal user calls `/api/admin/export`.
- A read-only user sends `DELETE /api/users/123`.
- A mobile route permits account suspension without web admin checks.
- A GraphQL mutation `makeUserAdmin` lacks resolver authorization.
- A support impersonation endpoint is callable from the public API.

## Related notes

- [[authorization]]
- [[broken-object-level-authorization]]
- [[api-inventory-management]]
- [[broken-access-control|Broken Access Control]]

### Suggested future atomic notes

- admin-api-exposure
- method-level-authorization
- graphql-mutation-authorization
- workflow-action-authorization
- support-tool-authorization

## References

- **Foundational:** OWASP API5:2023 Broken Function Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa5-bfla/
- **Foundational:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control
