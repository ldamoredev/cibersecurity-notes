---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Mass Assignment

## Definition

Mass assignment happens when an API automatically binds client-supplied properties onto an internal object without explicitly restricting which properties the client may set.

## Why it matters

Mass assignment turns framework convenience into an authorization bug. JSON bodies often look harmless, but binding helpers may accept fields the UI never exposes and the product never intended clients to control.

This is the write-side symptom of [[broken-object-property-level-authorization]]. [[excessive-data-exposure]] is the read-side sibling: one leaks too many fields, the other accepts too many fields.

## How it works

Mass assignment is a **3-shape mismatch**:

1. **Public request shape.** What the client should be allowed to send.
2. **Internal domain shape.** What the application uses to represent business state.
3. **Persistence shape.** What the database stores.

The vulnerability appears when the public request shape is treated as if it can safely map to the internal or persistence shape.

Unsafe pattern:

```
app.patch('/api/profile', requireLogin, async (req, res) => {
  const user = await db.users.update(req.user.id, req.body)
  res.json(user)
})
```

Safer shape:

```
const allowed = {
  displayName: req.body.displayName,
  timezone: req.body.timezone
}

const user = await db.users.update(req.user.id, allowed)
```

The important boundary is not whether the field is valid JSON. It is whether this caller may set this field through this endpoint in this state.

## Techniques / patterns

Attackers test:

- guessed top-level fields such as `isAdmin`, `role`, `status`, `approved`, and `plan`
- ownership fields such as `ownerId`, `tenantId`, `organizationId`, and `accountId`
- financial fields such as `creditLimit`, `balance`, `price`, `discount`, and `account_credit_cents`
- workflow fields such as `published`, `verified`, `locked`, and `refunded`
- nested fields that bind into related objects
- create/update differences where `PATCH` is looser than `POST`
- alternate clients, older versions, and bulk endpoints

## Variants and bypasses

Mass assignment appears in **6 common forms**.

### 1. Privilege flag mutation

The client sets `isAdmin`, `role`, `permissions`, or `scopes`.

### 2. Ownership reassignment

The client changes `ownerId`, `tenantId`, or related routing fields.

### 3. Workflow-state mutation

The client forces `approved`, `published`, `verified`, `locked`, or similar state.

### 4. Financial or quota mutation

The client changes plan, credits, usage caps, discounts, or limits.

### 5. Nested object binding

The endpoint allowlists top-level fields but accepts nested objects that update protected related records.

### 6. Bulk assignment

Batch endpoints apply attacker-controlled fields across many objects without per-field authorization.

## Impact

Ordered roughly by severity:

- **Privilege escalation.** Role, permission, or admin flags become client-controlled.
- **Tenant boundary break.** Ownership or tenant fields are reassigned.
- **Business logic bypass.** Approval, verification, pricing, quota, or workflow state is forced.
- **Data integrity damage.** Server-owned fields no longer reflect trusted state.
- **Stealthy persistence.** The attack may look like a normal profile or settings update.

## Detection and defense

Ordered by effectiveness:

1.
**Allowlist writable fields per endpoint, role, and state.**
   The safest rule is that fields are not writable unless intentionally exposed for that operation.

2.
**Separate request DTOs from domain and persistence models.**
   Never bind request JSON directly into ORM entities or internal domain objects.

3.
**Reject unknown or forbidden properties on sensitive endpoints.**
   Explicit rejection catches probing, makes tests clearer, and prevents silent partial updates from hiding bugs.

4.
**Keep server-owned fields server-owned.**
   Tenant, owner, role, workflow, financial, and audit fields should come from trusted server context or policy, not the request body.

5.
**Test create, update, patch, nested, and bulk flows separately.**
   A strict create endpoint does not prove the update or batch endpoint is safe.

6.
**Log protected-field submission attempts.**
   Unexpected fields like `isAdmin` or `tenantId` in ordinary requests are high-signal.

### What does not work as a primary defense

- **Hiding fields in the frontend.** HTTP clients can send arbitrary JSON.
- **Relying on validation only.** A field can be valid but unauthorized.
- **Using ORM protected fields inconsistently.** Framework-level protection often varies by model, endpoint, or update method.
- **Ignoring unknown properties silently everywhere.** This can reduce exploitability, but it also hides probing and may fail on nested or alternative update paths.
- **Assuming PATCH is safer because it is partial.** Partial updates often make mass assignment easier.

## Practical labs

Use an owned API or local lab where you can create two accounts and inspect resulting state.

### Probe top-level protected fields

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"A","isAdmin":true,"role":"admin","account_credit_cents":999999}' \
  https://api.example.test/profile
```

After the request, fetch the object again and verify whether any protected field changed.

### Probe ownership fields

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"tenantId":"other-tenant","ownerId":"other-user"}' \
  https://api.example.test/projects/123
```

Ownership fields should be ignored or rejected, never trusted from the body.

### Probe nested binding

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"profile":{"timezone":"UTC"},"account":{"plan":"enterprise","locked":false}}' \
  https://api.example.test/settings
```

Nested objects should have their own allowlists or be disallowed.

### Probe bulk updates

```
curl -i -X POST -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"ids":["1","2"],"updates":{"status":"approved","discount":100}}' \
  https://api.example.test/items/bulk-update
```

Bulk flows need per-object and per-field authorization.

## Practical examples

- Sending `{"isAdmin": true}` upgrades a normal user.
- A profile update accepts `support_priority` or `account_credit_cents`.
- A project update lets a user change `tenantId`.
- A draft item can be published by setting `status: "published"`.
- A nested `account.plan` field changes billing state through a settings endpoint.

## Related notes

- [[broken-object-property-level-authorization]]
- [[excessive-data-exposure]]
- [[authorization]]
- [[api-security-top-10]]
- [[business-logic-vulnerabilities|Business Logic Vulnerabilities]]

### Suggested future atomic notes

- request-dto-allowlists
- server-owned-fields
- nested-mass-assignment
- bulk-update-authorization
- orm-binding-security

## References

- **Foundational:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- **Foundational:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
