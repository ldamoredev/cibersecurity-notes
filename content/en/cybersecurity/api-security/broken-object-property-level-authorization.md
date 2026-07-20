---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Broken Object Property Level Authorization

## Definition

Broken Object Property Level Authorization (BOPLA) occurs when an API authorizes access to an object but fails to authorize which properties of that object the caller may read or modify.

## Why it matters

APIs often expose structured objects directly. Even when the route and object are allowed, individual fields can cross trust boundaries: role flags, tenant IDs, financial limits, workflow states, internal notes, PII, and security metadata.

BOPLA is the property-level branch of [[authorization]]. Its two most important symptoms are [[excessive-data-exposure]] on the read side and [[mass-assignment]] on the write side.

## How it works

BOPLA has **2 directions**:

1. **Read-side property exposure.** The caller receives fields they should not see.
2. **Write-side property mutation.** The caller changes fields they should not control.

It usually appears because the API treats "can access this object" as equivalent to "can see or edit every field on this object."

Unsafe response shape:

```
app.get('/api/users/:id', requireLogin, async (req, res) => {
  const user = await db.users.findAuthorized(req.user, req.params.id)
  res.json(user)
})
```

The object lookup may be authorized, but serializing the internal entity leaks every property.

Unsafe update shape:

```
app.patch('/api/profile', requireLogin, async (req, res) => {
  const updated = await db.users.update(req.user.id, req.body)
  res.json(updated)
})
```

The caller may update their profile, but not necessarily `role`, `tenantId`, `creditLimit`, or `mfaEnabled`.

## Techniques / patterns

Attackers test:

- response fields across roles, tenants, and API versions
- hidden properties present in mobile or admin responses
- extra JSON fields in `POST`, `PUT`, and `PATCH`
- nested objects such as `user.role.name`, `account.billingPlan`, or `permissions[]`
- fields returned by export, search, report, and debug endpoints
- differences between public, authenticated, support, and admin callers

## Variants and bypasses

BOPLA is easier to reason about as **5 protected property classes**:

### 1. Identity and ownership fields

Fields like `userId`, `ownerId`, `tenantId`, `organizationId`, and `accountId` decide who controls or sees the object.

### 2. Role and permission fields

Fields like `role`, `isAdmin`, `scopes`, `permissions`, and `supportAccess` alter authority.

### 3. Workflow and state fields

Fields like `approved`, `published`, `locked`, `refunded`, and `status` control business transitions.

### 4. Financial and quota fields

Fields like `creditLimit`, `account_credit_cents`, `plan`, `discount`, and `usageCap` affect money or resource consumption.

### 5. Sensitive or internal fields

Fields like `passwordHash`, `mfaSecret`, `resetToken`, `internalNotes`, `riskScore`, and `debugMetadata` should not be exposed to ordinary clients.

## Impact

Ordered roughly by severity:

- **Privilege escalation.** Writable role or permission fields grant stronger authority.
- **Tenant boundary break.** Ownership or tenant fields move data across accounts.
- **Sensitive data disclosure.** Internal, financial, or personal fields leak through responses.
- **Business logic abuse.** Workflow, quota, price, or approval fields are changed directly.
- **Audit confusion.** Logs show legitimate endpoints but miss unauthorized field access.

## Detection and defense

Ordered by effectiveness:

1.
**Define readable and writable fields per role, action, and object state.**
   Property policy must be explicit. A user may read `email` but not `riskScore`, or update `displayName` but not `role`.

2.
**Use response DTOs and request DTOs instead of internal models.**
   Public API shapes should be intentionally smaller than persistence entities. This prevents accidental serialization and binding of internal fields.

3.
**Reject unknown or forbidden request properties.**
   Silent ignoring can be acceptable for compatibility, but explicit rejection is better for sensitive endpoints because it surfaces probing and prevents false confidence in tests.

4.
**Test field behavior with multiple roles and tenants.**
   Compare responses and accepted writes for normal, admin, support, read-only, and wrong-tenant users.

5.
**Review export, search, and batch endpoints separately.**
   These often use different serializers or query projections than normal detail endpoints.

6.
**Log protected-field write attempts.**
   Attempts to submit `isAdmin`, `tenantId`, `ownerId`, or financial fields are useful abuse signals.

### What does not work as a primary defense

- **Route-level authorization alone.** Access to `/profile` does not imply access to every profile property.
- **Frontend forms.** Attackers can send JSON properties the UI never renders.
- **Serializer defaults.** Framework defaults often serialize more than the API contract intends.
- **Client-side field filtering.** Sensitive fields already crossed the boundary if the client had to remove them.
- **Naming fields obscurely.** Hidden or undocumented fields leak through traffic, schemas, mobile clients, and error messages.

## Practical labs

Use an owned API, local lab, or deliberately vulnerable app with at least two roles.

### Diff response fields by role

```
curl -s -H "Authorization: Bearer $USER"  https://api.example.test/users/me | jq -S 'keys'
curl -s -H "Authorization: Bearer $ADMIN" https://api.example.test/users/me | jq -S 'keys'
```

Expected: differences should match a documented property policy, not accidental serializer behavior.

### Submit protected write fields

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"displayName":"A","role":"admin","tenantId":"other","creditLimit":999999}' \
  https://api.example.test/users/me
```

The API should reject or ignore forbidden fields predictably, and it should not persist them.

### Check nested property binding

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"profile":{"timezone":"UTC"},"account":{"plan":"enterprise"}}' \
  https://api.example.test/profile
```

Nested objects often bypass simple top-level allowlists.

### Test export/search serializers

```
curl -s -H "Authorization: Bearer $USER" \
  'https://api.example.test/users/export?format=json' | jq '.[0]'
```

Exports should not return a richer internal object than normal API responses.

## Practical examples

- A profile response includes `mfaSecret` or `passwordResetToken`.
- A normal user can set `role: "admin"` in a JSON body.
- A support user can see `riskScore` for accounts outside their queue.
- An export endpoint includes internal notes hidden from the detail endpoint.
- A nested `account.plan` field can be changed through a profile update.

## Related notes

- [[authorization]]
- [[broken-object-level-authorization]]
- [[broken-function-level-authorization]]
- [[excessive-data-exposure]]
- [[mass-assignment]]

### Suggested future atomic notes

- field-level-permissions
- response-dto-design
- request-dto-allowlists
- serializer-overexposure
- nested-property-authorization

## References

- **Foundational:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure
