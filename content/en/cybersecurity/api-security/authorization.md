---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Authorization

## Definition

Authorization is the server-side decision that determines what an authenticated API caller may read, write, invoke, or transition. In APIs, authorization must be enforced at object, function, and property boundaries.

## Why it matters

Authentication only answers "who is calling?" Authorization answers "is this caller allowed to do this exact thing to this exact resource with these exact fields?" APIs expose identifiers, methods, routes, JSON bodies, batch actions, and machine-readable responses directly, so frontend hiding is never a control.

This is the umbrella note. [[broken-object-level-authorization]] owns object access, [[broken-function-level-authorization]] owns action access, and [[broken-object-property-level-authorization]] owns field visibility/mutability.

## How it works

API authorization has **3 enforcement layers**:

1. **Object-level:** Can this identity access this object? Example: `invoice_id=123`.
2. **Function-level:** Can this identity invoke this operation? Example: `POST /admin/users/ban`.
3. **Property-level:** Can this identity see or modify this field? Example: `isAdmin`, `ownerId`, `account_credit_cents`.

Example unsafe handler:

```
app.get('/api/invoices/:id', requireLogin, async (req, res) => {
  const invoice = await db.invoices.findById(req.params.id)
  res.json(invoice)
})
```

The caller is authenticated, but the object lookup is not scoped to `req.user`. The authorization decision is missing.

The bug is treating identity as permission.

## Techniques / patterns

Attackers and defenders test:

- object IDs in paths, queries, JSON bodies, and nested structures
- role-only routes such as `/admin`, `/support`, `/internal`, `/moderation`
- hidden fields accepted by `POST`, `PUT`, and `PATCH`
- batch, export, import, and report endpoints
- alternate clients and API versions
- workflow state transitions such as approve, refund, publish, invite, suspend
- read/write asymmetry where reads are checked but updates are not

## Variants and bypasses

API authorization failures fall into **3 canonical families**.

### 1. Object-level failures

The API checks that the caller is logged in but not that the target object belongs to them or is otherwise authorized. This is BOLA/IDOR.

### 2. Function-level failures

The API exposes a route or action that the caller's role should not invoke. This includes admin, support, export, destructive, and workflow endpoints.

### 3. Property-level failures

The API returns or accepts fields the caller should not see or control. This includes excessive data exposure and mass assignment.

## Impact

Ordered roughly by severity:

- **Tenant boundary break.** One tenant reads or changes another tenant's data.
- **Privilege escalation.** Normal users invoke admin/support actions or mutate privileged fields.
- **Data disclosure.** Sensitive properties or entire objects leak through API responses.
- **State corruption.** Unauthorized fields or workflow states are changed.
- **Business abuse.** Refunds, approvals, exports, invites, credits, quotas, or ownership are manipulated.
- **Audit failure.** Logs show authenticated users but not missing authorization decisions.

## Detection and defense

Ordered by effectiveness:

1.
**Deny by default at object, function, and property layers.**
   Every route should require an explicit policy decision. Missing policy should fail closed, not inherit "authenticated is enough."

2.
**Scope data access in the query.**
   Fetch objects through the caller's allowed dataset: `WHERE id = ? AND account_id = ?`. Post-fetch checks are better than none, but scoped queries prevent accidental exposure and reduce race mistakes.

3.
**Centralize policy but keep decisions specific.**
   Use shared authorization helpers/policy objects, but pass resource, action, actor, tenant, and field context. Generic role checks alone are too blunt for APIs.

4.
**Separate request DTOs from internal models.**
   Public request/response shapes should define what fields are accepted and returned. Internal entities should not be serialized or bound directly.

5.
**Test authorization as a matrix.**
   Use at least two users, two roles, and two tenants. Test read, write, delete, export, batch, and workflow routes separately.

6.
**Log denials and suspicious cross-boundary attempts.**
   Repeated object ID changes, admin route attempts, and protected-field submissions are useful abuse signals.

### What does not work as a primary defense

- **Hiding UI controls.** API callers can send HTTP directly.
- **Using UUIDs as authorization.** Unpredictability helps enumeration resistance but does not prove access.
- **Trusting client-supplied roles or tenant IDs.** The server must derive authority from trusted session/token context and policy.
- **CORS.** CORS controls browser read access; it does not authorize API actions.
- **Indirect references alone.** Mapping `abc123` to an object is not authorization unless the mapping is scoped to the caller.

## Practical labs

Use an owned API or lab app with at least two users and two roles.

### Build an authorization matrix

```
Rows: users/roles/tenants
Columns: endpoints/actions/fields
Cells: allowed, denied, not applicable
```

Keep this as the source of truth for tests.

### Test object access with two users

```
curl -s -H "Authorization: Bearer $USER_A" https://api.example.test/invoices/100
curl -s -H "Authorization: Bearer $USER_B" https://api.example.test/invoices/100
```

The second request should fail if invoice `100` belongs only to user A.

### Test function access

```
curl -i -X POST -H "Authorization: Bearer $USER" \
  https://api.example.test/admin/users/123/disable
```

Normal users should receive `403`, not `200`, `404` by obscurity, or a partial action.

### Test property write control

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"A","isAdmin":true,"account_credit_cents":999999}' \
  https://api.example.test/profile
```

Protected fields should be rejected or ignored predictably and never persisted.

### Test response field exposure

```
curl -s -H "Authorization: Bearer $USER" https://api.example.test/users/me | jq .
```

Look for internal fields, role flags, secrets, ownership IDs, or other users' data.

## Practical examples

- A user can read another user's invoice by changing `/api/invoices/{id}`.
- A non-admin can call `POST /api/admin/export`.
- A profile update accepts `isAdmin` or `support_priority`.
- A list endpoint hides sensitive fields, but detail and export endpoints return them.
- A mobile API route skips the policy applied in the web route.

## Related notes

- [[broken-object-level-authorization]]
- [[broken-function-level-authorization]]
- [[broken-object-property-level-authorization]]
- [[mass-assignment]]
- [[excessive-data-exposure]]
- [[broken-access-control|Broken Access Control]]
- [[exploit-idor|Exploit IDOR]]

### Suggested future atomic notes

- policy-based-authorization
- tenant-scoped-queries
- authorization-test-matrix
- field-level-permissions
- workflow-state-authorization

## References

- **Foundational:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control
