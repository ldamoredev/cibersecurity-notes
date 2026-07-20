---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Broken Object Level Authorization

## Definition

Broken Object Level Authorization (BOLA) occurs when an API lets a caller read, update, delete, export, or act on an object they are not authorized to access, usually by changing an object identifier.

## Why it matters

BOLA is one of the highest-value API bug classes because APIs naturally expose object references in URLs, query strings, JSON bodies, and response data. Machine clients can enumerate, replay, and mutate these references faster than a UI-driven attacker.

BOLA is the API-specific form of [[idor|IDOR]], but API scale, batch operations, and rich object graphs make it broader than classic web ID swapping.

## How it works

BOLA has **4 steps**:

1. The API exposes an object reference.
2. The caller authenticates successfully.
3. The server loads the object by reference.
4. The server fails to verify that the caller may access that object.

Unsafe pattern:

```
const invoice = await db.invoice.findById(req.params.invoiceId)
return res.json(invoice)
```

Safer shape:

```
const invoice = await db.invoice.findFirst({
  where: { id: req.params.invoiceId, accountId: req.user.accountId }
})
if (!invoice) return res.sendStatus(404)
```

The bug is fetching by identifier without scoping the object to the caller's authority.

## Techniques / patterns

Attackers test:

- path IDs: `/users/123`, `/orders/456`, `/files/789`
- query IDs: `?accountId=`, `?invoice=`, `?tenant=`
- body IDs in `POST`, `PUT`, `PATCH`, and action endpoints
- nested IDs: project → task, org → user, invoice → attachment
- list-to-detail pivots where list responses leak useful IDs
- export, bulk, share, preview, and download endpoints
- predictable IDs and UUIDs copied from logs, emails, mobile traffic, or API responses

## Variants and bypasses

BOLA appears in **6 common forms**.

### 1. Read-side BOLA

The caller reads another user's object, file, metadata, or detail response.

### 2. Write-side BOLA

The caller modifies, deletes, or triggers a state change on another user's object.

### 3. Nested-object BOLA

The parent object is checked, but child IDs are not scoped to that parent or tenant.

### 4. Bulk/export BOLA

Single-object endpoints are protected, but bulk routes, exports, reports, or background jobs are not.

### 5. Relationship BOLA

The caller cannot access the object directly but can attach, share, invite, transfer, or link it through a relationship endpoint.

### 6. UUID/opaque-ID myth

The team relies on unguessable IDs instead of checking authorization. Leaked IDs still work.

## Impact

Ordered roughly by severity:

- **Cross-tenant data exposure.** One tenant reads another tenant's records.
- **Unauthorized object modification.** Updates, deletes, transfers, approvals, or workflow actions affect another object.
- **File or export leakage.** Downloads and reports expose sensitive data at scale.
- **Privilege pivot.** Object access leads to related users, tokens, invoices, or admin workflows.
- **Business integrity damage.** Ownership, status, price, quota, or approval state is changed.

## Detection and defense

Ordered by effectiveness:

1.
**Scope every object lookup to the caller's authorization context.**
   Query by both object ID and tenant/account/owner/relationship. This makes unauthorized objects indistinguishable from absent objects to the handler.

2.
**Apply the same policy to read, write, delete, export, and action paths.**
   Protecting `GET` while forgetting `DELETE`, `download`, or `export` is common.

3.
**Validate nested object relationships.**
   Check that child resources belong to the authorized parent and tenant, not just that both IDs exist.

4.
**Test with two real identities.**
   BOLA is not proven with one account. Use two users or tenants and swap only the object reference.

5.
**Log cross-object attempts.**
   Repeated attempts to access adjacent IDs, foreign tenants, or unknown object IDs are high-signal.

### What does not work as a primary defense

- **UUIDs or opaque IDs alone.** They reduce guessing but do not authorize leaked or harvested references.
- **Route authentication.** Being logged in does not imply access to every object.
- **Hiding object IDs in the UI.** APIs, mobile apps, logs, exports, and traffic reveal IDs.
- **Returning 404 without enforcing policy.** Status-code camouflage is not authorization.

## Practical labs

Use two users or tenants.

### Capture a valid object request

```
curl -i -H "Authorization: Bearer $USER_A" \
  https://api.example.test/invoices/100
```

Record status, body shape, and object owner.

### Replay with another identity

```
curl -i -H "Authorization: Bearer $USER_B" \
  https://api.example.test/invoices/100
```

Expected: denied or not found without leaking data.

### Test write-side BOLA

```
curl -i -X PATCH -H "Authorization: Bearer $USER_B" \
  -H 'Content-Type: application/json' \
  -d '{"nickname":"changed"}' \
  https://api.example.test/invoices/100
```

Write routes often fail differently than read routes.

### Test nested object scope

```
curl -i -H "Authorization: Bearer $USER_A" \
  https://api.example.test/projects/1/tasks/900
```

Verify task `900` belongs to project `1` and the caller, not just any accessible project.

### Test export and batch routes

```
curl -i -X POST -H "Authorization: Bearer $USER_A" \
  -H 'Content-Type: application/json' \
  -d '{"invoiceIds":[100,200,300]}' \
  https://api.example.test/invoices/export
```

Batch inputs must authorize every object.

## Practical examples

- `/api/orders/101` can be changed to `/api/orders/102`.
- A user can download another tenant's invoice PDF.
- A project member can attach a task from another project.
- A bulk export includes foreign IDs mixed into the request body.
- A share endpoint lets a user invite themselves to another account's object.

## Related notes

- [[authorization]]
- [[broken-function-level-authorization]]
- [[broken-object-property-level-authorization]]
- [[idor|IDOR]]
- [[exploit-idor|Exploit IDOR]]

### Suggested future atomic notes

- tenant-scoped-queries
- nested-object-authorization
- bulk-operation-authorization
- relationship-based-access-control
- uuid-is-not-authorization

## References

- **Foundational:** OWASP API1:2023 Broken Object Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa1-bola/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger IDOR — https://portswigger.net/web-security/access-control/idor
