---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Token Lifecycle

## Definition

Token lifecycle is the full sequence of creating, issuing, refreshing, rotating, revoking, expiring, and invalidating tokens across an authenticated API session or machine-to-machine relationship.

## Why it matters

Many API authentication weaknesses are lifecycle failures rather than login failures. A token that survives too long, refreshes without rotation, or ignores revocation events becomes a standing trust artifact.

This note is about what happens after issuance. [[jwt-attacks]] covers validation semantics, while [[broken-authentication]] and [[api-auth-flaws]] cover broader authentication workflows.

## How it works

Token lifecycle has **6 events**:

1. **Issuance.** The system creates a token after a defined authentication state.
2. **Use.** APIs accept the token for specific audiences, scopes, routes, and actions.
3. **Refresh.** The client obtains new access without repeating full authentication.
4. **Rotation.** Refresh credentials are replaced to reduce replay value.
5. **Revocation.** The system invalidates tokens after security or account events.
6. **Expiry.** The token stops working after a planned lifetime.

The weakness appears when teams define issuance but leave refresh, rotation, revocation, and expiry fuzzy.

Example lifecycle table:

```
access token  | 10 min | bearer | no rotation | expires only
refresh token | 30 days | stored | rotate each use | revoke on logout/password change
api key       | 90 days | header | manual rotate | revoke on owner removal
```

## Techniques / patterns

Attackers test:

- access tokens that remain valid after logout
- refresh tokens that can be replayed after use
- tokens that survive password change, MFA reset, account lock, or device removal
- old role or tenant claims after privilege changes
- service tokens with no expiry or owner
- inconsistent invalidation across services

## Variants and bypasses

Token lifecycle failures appear in **7 forms**.

### 1. Overlong access tokens

Access tokens live long enough that compromise has a large window.

### 2. Non-rotating refresh tokens

Refresh tokens can be replayed repeatedly if stolen.

### 3. Logout mismatch

Logout clears client state but does not invalidate token usefulness.

### 4. Security-event blind spots

Password change, MFA reset, account disable, or device removal does not affect active tokens.

### 5. Stale authorization claims

Issued tokens preserve old roles, scopes, or tenant state for too long.

### 6. Service-token permanence

Machine credentials have no owner, expiry, scope, or rotation process.

### 7. Distributed revocation lag

One API rejects a revoked token while another continues accepting it.

## Impact

Ordered roughly by severity:

- **Persistent unauthorized access.** Stolen or old tokens remain useful.
- **Privilege persistence.** Role or scope changes do not take effect quickly.
- **Session fixation or replay.** Refresh tokens can be reused after theft.
- **Machine credential compromise.** Long-lived service tokens expose broad API surface.
- **Incident response delay.** Teams cannot confidently invalidate affected credentials.

## Detection and defense

Ordered by effectiveness:

1.
**Define lifecycle rules per token type.**
   Access tokens, refresh tokens, API keys, device tokens, and service tokens need different lifetimes, scopes, storage rules, and revocation semantics.

2.
**Use short-lived access tokens with narrow audience and scope.**
   This limits replay value and stale authorization exposure.

3.
**Rotate refresh tokens and detect reuse.**
   Refresh-token reuse after rotation is a strong signal of theft and should revoke the token family.

4.
**Bind revocation to meaningful security events.**
   Logout, password change, MFA change, device removal, account lock, role downgrade, and key compromise should have explicit token effects.

5.
**Track token families, devices, and owners.**
   Users and operators need to revoke a device, integration, or service credential without destroying unrelated sessions.

6.
**Test revocation propagation across services.**
   Distributed systems need consistent rejection of revoked or stale tokens.

### What does not work as a primary defense

- **Very long-lived bearer tokens.** Anyone holding the token can use it for too long.
- **Refresh without rotation.** A stolen refresh token remains valuable indefinitely inside its lifetime.
- **Logout as UI cleanup only.** The token must stop being accepted where policy requires it.
- **Embedding long-lived roles in tokens.** Authorization truth changes faster than token expiry.
- **Manual spreadsheets for API key ownership.** Service credentials need enforceable ownership and rotation.

## Practical labs

Use a lab account where you can trigger auth events safely.

### Build a lifecycle matrix

```
token type | lifetime | audience | scope | rotation | revocation events | owner/device
```

Fill it for access tokens, refresh tokens, API keys, service tokens, and device tokens.

### Test logout revocation

```
curl -i -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.test/users/me
curl -i -X POST -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.test/auth/logout
curl -i -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.test/users/me
```

The expected result depends on the design, but it must be documented and consistent.

### Test refresh token rotation

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"refreshToken":"'$REFRESH_TOKEN'"}' \
  https://api.example.test/auth/refresh
```

Repeat with the old refresh token. Reuse should fail if rotation is enabled.

### Test privilege-change freshness

```
curl -i -H "Authorization: Bearer $OLD_ADMIN_TOKEN" \
  https://api.example.test/admin/users
```

After role downgrade, old tokens should stop granting privileged access within the intended window.

## Practical examples

- Access tokens remain valid after password change.
- Refresh token rotation is missing, enabling replay.
- A role downgrade does not affect already-issued tokens.
- API keys have no owner or expiry.
- One microservice honors revocation while another accepts stale tokens.

## Related notes

- [[jwt-attacks]]
- [[broken-authentication]]
- [[api-auth-flaws]]
- [[api-rate-limiting]]
- [[inspect-session-handling|Inspect Session Handling]]
- [[session-management|Session Management]]

### Suggested future atomic notes

- refresh-token-rotation
- token-family-revocation
- device-session-management
- api-key-rotation
- stale-authorization-claims

## References

- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
