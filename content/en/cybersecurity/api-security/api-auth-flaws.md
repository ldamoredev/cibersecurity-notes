---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# API Authentication Flaws

## Definition

API authentication flaws are practical weaknesses in how an API verifies identity across login, recovery, MFA, device, token, and machine-client flows.

## Why it matters

API authentication is rarely one neat login form. Real systems have SPAs, mobile apps, service accounts, refresh tokens, password reset flows, magic links, device pairing, OAuth/OIDC callbacks, and legacy clients. Each flow can accidentally define a different meaning of "authenticated."

This note focuses on applied workflow inconsistencies. [[broken-authentication]] is the broader category, while [[jwt-attacks]] and [[token-lifecycle]] isolate token-specific failure modes.

## How it works

API authentication flaws commonly appear across **5 auth surfaces**:

1. **Login.** Password, SSO, OAuth, passkey, or API-key entry points.
2. **Recovery.** Password reset, email verification, account recovery, and magic links.
3. **MFA and device trust.** Step-up authentication, remembered devices, and device registration.
4. **Refresh and session continuation.** Access-token renewal, rotation, logout, and revocation.
5. **Machine credentials.** API keys, service tokens, client credentials, and partner integrations.

The bug is usually not "no authentication." It is inconsistent authentication guarantees between these surfaces.

Example failure:

```
Web login: password + MFA -> full session
Mobile refresh: refresh token -> full session, no MFA state check
Password reset: one-time link -> access token, no device or MFA review
```

## Techniques / patterns

Attackers test:

- web vs mobile vs partner client behavior
- tokens issued before MFA is complete
- password reset links that create fully authenticated sessions
- device registration or remembered-device flows
- API keys with excessive scope or no rotation
- logout, password change, and account-lock effects
- differences between legacy and current API versions

## Variants and bypasses

API auth flaws appear in **6 recurring forms**.

### 1. Pre-MFA token bridging

The API issues a token after the password step and later treats it as fully authenticated.

### 2. Recovery flow as weaker login

Reset, magic-link, or verification flows become easier login paths than normal authentication.

### 3. Device trust overreach

Remembered devices or device registration produce durable credentials with weak revocation.

### 4. Client inconsistency

Mobile, web, partner, or internal clients enforce different credential, MFA, or session rules.

### 5. Machine credential sprawl

API keys and service tokens have broad privileges, long lifetimes, or unclear ownership.

### 6. Step-up bypass

Sensitive operations require step-up in one route but not another route that reaches the same effect.

## Impact

Ordered roughly by severity:

- **Account takeover.** Recovery, reset, or MFA gaps allow unauthorized access.
- **MFA bypass.** Password-only or pre-MFA states become enough for sensitive API calls.
- **Persistent access.** Tokens or device credentials survive logout, reset, or account lock.
- **Machine-client compromise.** Long-lived service credentials expose broad API reach.
- **Audit and incident confusion.** Multiple auth surfaces make it unclear which guarantee failed.

## Detection and defense

Ordered by effectiveness:

1.
**Inventory every authentication entry point and token type.**
   You cannot secure only the main login route. Recovery, device, refresh, service, and partner flows all issue trust.

2.
**Model auth states explicitly.**
   Separate anonymous, password-verified, MFA-verified, step-up verified, device-trusted, and service-authenticated states.

3.
**Centralize security decisions while preserving flow context.**
   Shared auth middleware helps consistency, but it must carry whether MFA, recovery, device trust, or service identity was used.

4.
**Treat recovery and device flows as login-equivalent.**
   A password reset or device pairing path can become the easiest way into the account if not hardened.

5.
**Scope and rotate machine credentials.**
   API keys and service tokens need ownership, least privilege, expiry, rotation, and revocation.

6.
**Test auth flows as cross-client workflows.**
   Compare web, mobile, API docs, legacy versions, and partner clients for equivalent security guarantees.

### What does not work as a primary defense

- **Assuming the main login flow represents all authentication.** Recovery, refresh, and machine flows often bypass it.
- **Client-side MFA flags.** The server must enforce auth state from trusted server-side context or validated token claims.
- **Long-lived API keys without ownership.** Unknown owners and no expiry make incident response slow.
- **Logout that only clears client storage.** Server-side token usefulness must be addressed.
- **Security by client type.** Mobile or partner clients are still direct API callers.

## Practical labs

Use an owned app or lab environment with web and API clients.

### Map auth entry points

```
rg -n "login|reset|recover|mfa|refresh|device|api-key|client_credentials" routes src openapi.yaml
```

Turn the results into a table of flow, credential, token issued, MFA state, lifetime, and revocation event.

### Test pre-MFA token behavior

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"email":"user@example.test","password":"correct-password"}' \
  https://api.example.test/auth/login
```

If the response includes a token before MFA, test whether that token can call sensitive endpoints.

### Test reset-token session strength

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"resetToken":"TOKEN","newPassword":"NewPass123!"}' \
  https://api.example.test/auth/reset/complete
```

Check whether reset completion creates a full session and whether old tokens remain usable.

### Test machine credential scope

```
curl -i -H "Authorization: Bearer $SERVICE_TOKEN" \
  https://api.example.test/admin/users
```

Service credentials should be limited to intended routes, tenants, and actions.

## Practical examples

- A mobile API route skips MFA enforced on the web flow.
- Password reset completion returns a full access token without invalidating old sessions.
- Device registration creates a long-lived token that cannot be revoked per device.
- A partner API key can call admin-like endpoints outside its integration scope.
- A sensitive operation requires step-up in the UI but not through the direct API route.

## Related notes

- [[broken-authentication]]
- [[jwt-attacks]]
- [[token-lifecycle]]
- [[break-jwt-validation|Break JWT Validation]]
- [[auth-flaws|Auth Flaws]]

### Suggested future atomic notes

- mfa-state-machines
- device-trust-flaws
- password-reset-api-security
- machine-credential-sprawl
- step-up-authentication

## References

- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication
