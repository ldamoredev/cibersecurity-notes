---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Excessive Data Exposure

## Definition

Excessive data exposure happens when an API returns more data than the client needs or the caller is authorized to see, often trusting the frontend to hide or ignore sensitive fields.

## Why it matters

APIs are machine-readable. Extra fields are easy to inspect, diff, script, and store even if the UI never renders them. This makes hidden response data a direct trust-boundary failure, not a cosmetic issue.

This is the read-side symptom of [[broken-object-property-level-authorization]]. [[mass-assignment]] is the corresponding write-side risk where the server accepts too many fields.

## How it works

Excessive data exposure has **4 leak shapes**:

1. **Full object serialization.** The API returns internal models instead of response DTOs.
2. **Nested relation leakage.** Included relationships reveal fields from related users, accounts, tenants, or files.
3. **Role or tenant field leakage.** Normal callers receive fields reserved for admin, support, or another tenant.
4. **Hidden metadata leakage.** Debug, audit, token, risk, IP, path, or infrastructure metadata appears in responses.

The common unsafe pattern is:

```
const user = await db.users.findAuthorized(req.user, req.params.id)
res.json(user)
```

Authorization to read the user object does not mean every property on the internal user record should cross the API boundary.

## Techniques / patterns

Attackers test:

- raw API responses vs what the UI displays
- field differences between user, admin, support, and wrong-tenant accounts
- detail, list, search, export, and report responses
- old API versions and mobile-specific endpoints
- nested `include=`, `expand=`, `fields=`, and GraphQL selection behavior
- response metadata, error bodies, and debug modes

## Variants and bypasses

Excessive exposure appears in **7 forms**.

### 1. Internal entity serialization

ORM or domain objects are returned directly with internal fields.

### 2. Hidden frontend filtering

The backend sends sensitive fields and expects the UI not to render them.

### 3. Role-diff leakage

Normal users receive fields intended only for admin, support, or internal clients.

### 4. Nested include leakage

Related objects expose fields that the top-level endpoint would not normally reveal.

### 5. Export and report leakage

Bulk formats include richer data than normal API responses.

### 6. Version drift

Old API versions continue returning verbose objects after newer endpoints are fixed.

### 7. Error and debug exposure

Error bodies include stack traces, internal IDs, tokens, paths, or infrastructure details.

## Impact

Ordered roughly by severity:

- **Sensitive data disclosure.** PII, secrets, tokens, hashes, internal notes, or financial fields leak.
- **Tenant information leakage.** One tenant infers data, IDs, or structure from another.
- **Privilege reconnaissance.** Role flags, risk scores, feature gates, and support metadata reveal attack paths.
- **Regulatory exposure.** Personal or financial data is processed or leaked outside intended purposes.
- **Follow-on exploitation.** Extra IDs and state fields enable BOLA, BFLA, or mass assignment testing.

## Detection and defense

Ordered by effectiveness:

1.
**Use explicit response DTOs per endpoint and caller context.**
   The API response should contain only fields intentionally exposed for that route, role, tenant, and object state.

2.
**Authorize properties, not just objects.**
   A caller may read an object but not every property on it. Field visibility is a policy decision.

3.
**Review list, detail, export, search, and nested include paths separately.**
   Different code paths often use different serializers or projections.

4.
**Fail closed on `include`, `expand`, `fields`, and GraphQL selections.**
   Caller-controlled projection features need allowlists and per-field authorization.

5.
**Diff responses across roles and versions in tests.**
   Tests should assert absent sensitive fields, not only present expected fields.

6.
**Strip debug and internal metadata from production responses.**
   Errors should be useful to clients without exposing implementation details.

### What does not work as a primary defense

- **Frontend hiding.** The data already crossed the boundary.
- **Assuming "read object" means "read all fields."** Property authorization is separate.
- **Relying on serializer defaults.** Defaults tend to expose whatever the object contains.
- **Fixing only the detail endpoint.** Lists, exports, reports, and old versions often remain verbose.
- **Obscure field names.** Machine clients can inspect and diff every property.

## Practical labs

Use an owned API with at least two roles or tenants.

### Compare raw response to UI display

```
curl -s -H "Authorization: Bearer $USER" \
  https://api.example.test/users/me | jq .
```

List every field not shown in the UI and decide whether it is intentionally exposed.

### Diff fields across roles

```
curl -s -H "Authorization: Bearer $USER"  https://api.example.test/accounts/123 | jq -S 'keys'
curl -s -H "Authorization: Bearer $ADMIN" https://api.example.test/accounts/123 | jq -S 'keys'
```

Differences should match documented field policy.

### Test nested expansion

```
curl -s -H "Authorization: Bearer $USER" \
  'https://api.example.test/projects/123?include=members,owner,billing' | jq .
```

Nested relations need the same property filtering as top-level endpoints.

### Test export response shape

```
curl -s -H "Authorization: Bearer $USER" \
  https://api.example.test/accounts/export | jq '.[0]'
```

Exports should not bypass response DTOs.

## Practical examples

- A response includes password hashes, reset tokens, or internal IDs.
- An admin-only field appears for normal users but is hidden by the UI.
- Old API versions still return verbose internal objects.
- `include=owner` leaks another user's email and risk score.
- Error responses include stack traces and server paths.

## Related notes

- [[broken-object-property-level-authorization]]
- [[mass-assignment]]
- [[api-inventory-management]]
- [[authorization]]
- [[http-messages|HTTP Messages]]
- [[broken-access-control|Broken Access Control]]

### Suggested future atomic notes

- response-dto-design
- field-visibility-policy
- api-response-diffing
- graphql-field-exposure
- debug-metadata-leakage

## References

- **Foundational:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure
- **Foundational:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
