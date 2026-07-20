---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Deprecated API Versions

## Definition

Deprecated API versions are old, superseded, beta, mobile, partner, or legacy endpoints that remain reachable after the organization believes clients have moved on.

## Why it matters

Old API versions often preserve weaker authentication, noisier responses, looser validation, missing rate limits, or simpler business logic. They create time-shifted attack surface: an old design remains exploitable after the main product has improved.

This is inventory drift first and a vulnerability category second. The old surface remains reachable because retirement lagged behind delivery.

## How it works

Deprecated API risk has **4 lifecycle states**:

1. **Current.** Supported, owned, tested, monitored, and documented.
2. **Deprecated.** Still supported temporarily, but scheduled for retirement.
3. **Zombie.** Supposed to be gone, but still reachable.
4. **Unknown.** Discovered from traffic, clients, docs, or code with no clear owner.

The highest-risk state is not always "deprecated"; it is "unknown" or "zombie," because controls and owners are unclear.

A worked example, old endpoint to control drift:

```
Current endpoint:
  GET /api/v2/users/me -> id, email, displayName

Old endpoint:
  GET /api/v1/users/me -> id, email, displayName, role, billingPlan, internalNotes

Auth:
  both require login

Difference:
  v1 returns fields removed from v2 privacy review

Decision:
  data-shape drift; fix v1 or remove it, because "deprecated" does not reduce live impact
```

The key comparison is not just route availability. It is whether security controls and data shape changed between versions.

## Techniques / patterns

Practitioners look for:

- `/v1`, `/v2`, `/beta`, `/legacy`, `/old`, `/mobile`, `/partner`
- version headers and content negotiation
- old OpenAPI specs, SDKs, Postman collections, and mobile clients
- archived docs and example requests
- differences in auth, response fields, rate limits, and validation
- legacy routes found in JavaScript or source maps

## Variants and bypasses

Deprecated API exposure appears in **6 forms**.

### 1. Versioned path drift

Old `/api/v1` routes remain live after `/api/v2` launches.

### 2. Client-specific drift

Mobile, partner, or internal APIs stay reachable with weaker assumptions.

### 3. Schema drift

Old docs or schemas reveal routes and fields no longer visible in the main product.

### 4. Control drift

Authentication, authorization, rate limits, validation, or logging differ between versions.

### 5. Data-shape drift

Old endpoints return more fields or accept broader input.

### 6. Sunset failure

Deprecation notices exist, but removal never happens.

## Impact

Ordered roughly by severity:

- **Authorization bypass.** Old routes miss current object/function/property checks.
- **Sensitive data exposure.** Legacy responses expose fields removed from newer APIs.
- **Mass assignment or validation bypass.** Older request models accept protected fields.
- **Rate-limit bypass.** Abuse controls apply only to current routes.
- **Patch bypass.** Vulnerabilities fixed in v2 remain in v1.

## Detection and defense

Ordered by effectiveness:

1.
**Inventory API versions with owners and sunset dates.**
   Every version should have a support state and removal plan.

2.
**Apply security fixes across every reachable version.**
   Until removed, deprecated versions are production attack surface.

3.
**Compare old and new versions with security-focused diffs.**
   Test auth, authorization, fields, validation, rate limits, and logging.

4.
**Measure live traffic before retirement, then enforce removal.**
   Monitoring supports migration, but indefinite compatibility creates permanent risk.

5.
**Remove stale docs, SDKs, and schemas or mark them clearly.**
   Public old contracts accelerate discovery and abuse.

### What does not work as a primary defense

- **Deprecation labels.** A deprecated endpoint is still exploitable while reachable.
- **Removing frontend calls.** Mobile apps, scripts, and direct HTTP clients can still call old routes.
- **Fixing only current versions.** Attackers choose the weakest reachable version.
- **Assuming low traffic means low risk.** Low-volume legacy endpoints are often high impact.

## Practical labs

Use owned APIs.

### Probe common version paths

```
for v in v1 v2 v3 beta legacy mobile partner; do
  curl -i "https://api.example.test/api/$v/health"
done
```

Record live, redirected, denied, and unknown versions.

### Diff response fields

```
curl -s -H "Authorization: Bearer $USER" https://api.example.test/api/v1/users/me | jq -S 'keys'
curl -s -H "Authorization: Bearer $USER" https://api.example.test/api/v2/users/me | jq -S 'keys'
```

Unexpected extra fields in old versions are findings.

### Test control drift

```
curl -i -X PATCH -H "Authorization: Bearer $USER" \
  -H 'Content-Type: application/json' \
  -d '{"role":"admin","debug":true}' \
  https://api.example.test/api/v1/users/me
```

Old versions often preserve older binding and validation behavior.

### Build a version lifecycle table

```
version | status | owner | live traffic | security parity | sunset date | blocker
```

Unknown owner or missing sunset date is an attack-surface smell.

### Compare rate-limit behavior

```
for v in v1 v2; do
  for i in $(seq 1 20); do
    curl -s -o /dev/null -w "$v %{http_code}\n" "https://api.example.test/api/$v/search?q=test"
  done
done
```

Deprecated versions often miss newer abuse controls.

## Practical examples

- `/api/v1/` still returns more fields than `/api/v2/`.
- A deprecated mobile API path remains internet-facing.
- Old auth or role checks persist in a legacy version.
- Partner routes still accept broad API keys.
- Deprecated schemas reveal hidden endpoints.

## Related notes

- [[api-inventory-management|API Inventory Management]]
- [[endpoint-discovery]]
- [[excessive-data-exposure|Excessive Data Exposure]]
- [[mass-assignment|Mass Assignment]]
- [[external-attack-surface]]

### Suggested future atomic notes

- api-version-sunsetting
- mobile-api-drift
- schema-exposure
- legacy-api-control-diffing
- partner-api-exposure

## References

- **Foundational:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
