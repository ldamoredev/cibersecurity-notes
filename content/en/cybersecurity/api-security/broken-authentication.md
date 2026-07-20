---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Broken Authentication

## Definition

Broken authentication in APIs refers to weaknesses in identity verification, credential handling, token issuance, session continuation, or authentication workflow enforcement that let callers gain or keep access they should not have.

## Why it matters

Authentication is the root trust decision for most API calls. When it is inconsistent, every downstream authorization, audit, rate limit, and abuse-control decision can inherit the wrong identity or wrong assurance level.

This note is the category-level map. [[api-auth-flaws]] covers applied workflow inconsistencies; [[jwt-attacks]] covers token validation and claim trust; [[token-lifecycle]] covers issuance, refresh, rotation, and revocation over time.

## How it works

API authentication should distinguish **4 states**:

1. **Anonymous.** No verified identity.
2. **Pre-authenticated.** A credential, token, or link was presented but not fully verified.
3. **Partially authenticated.** One factor or workflow step succeeded, but more assurance is required.
4. **Fully authenticated.** The API may treat the caller as the claimed identity for allowed actions.

Broken authentication happens when the API jumps states too early, forgets state transitions, or treats all credentials as equivalent.

Example failure:

```
POST /auth/login -> password correct -> access_token issued
POST /auth/mfa/verify -> optional second step
GET /api/billing -> accepts pre-MFA access_token
```

The password step succeeded, but the API should not treat the caller as fully authenticated until MFA is complete.

## Techniques / patterns

Attackers test:

- login, recovery, reset, registration, and email-verification flows
- token issuance before MFA, device verification, or account checks
- stale token reuse after logout, password change, disable, or role change
- credential stuffing and brute-force resistance
- differences between web, mobile, partner, and legacy clients
- service-account and API-key behavior

## Variants and bypasses

Broken authentication appears in **7 forms**.

### 1. Weak credential verification

Passwords, API keys, or client secrets are accepted with weak policy, weak storage, no throttling, or poor comparison logic.

### 2. MFA bypass

MFA is optional, inconsistently enforced, or represented by client-controlled state.

### 3. Recovery-flow takeover

Reset or recovery workflows are easier to exploit than normal login.

### 4. Premature token issuance

The API issues usable tokens before the authentication workflow is complete.

### 5. Token lifecycle failure

Tokens outlive logout, password change, account disable, device removal, or risk events.

### 6. Client inconsistency

Different clients or API versions enforce different authentication guarantees.

### 7. Machine credential weakness

Service credentials are too broad, long-lived, poorly stored, or impossible to attribute.

## Impact

Ordered roughly by severity:

- **Account takeover.** Attackers authenticate as another user.
- **MFA or step-up bypass.** Sensitive operations become reachable with lower assurance.
- **Persistent unauthorized access.** Revoked, stale, or leaked credentials keep working.
- **Credential stuffing and enumeration.** Weak throttling and feedback enable automated attacks.
- **Service compromise.** Machine credentials expose backend-to-backend API access.

## Detection and defense

Ordered by effectiveness:

1.
**Define authentication states and enforce transitions server-side.**
   Every endpoint should know whether it requires anonymous, partial, full, step-up, or service authentication.

2.
**Harden credential and recovery flows together.**
   Recovery is authentication. Password reset, magic links, and device enrollment need the same rigor as login.

3.
**Issue tokens only after the required assurance is satisfied.**
   Pre-MFA or recovery-intermediate tokens must be limited to the next auth step, not general API access.

4.
**Design revocation and session invalidation intentionally.**
   Logout, password change, MFA reset, account lock, device removal, and role change should have defined token effects.

5.
**Apply abuse controls to auth routes.**
   Rate limits, lockouts, risk checks, and monitoring belong on login, recovery, MFA, and token refresh.

6.
**Test every client and credential type.**
   Web, mobile, partner, service, and legacy flows should provide equivalent guarantees where they reach the same API surface.

### What does not work as a primary defense

- **Authentication without authorization.** A valid identity still needs per-object, per-function, and per-field checks.
- **MFA enforced only in the frontend.** Direct API callers bypass UI logic.
- **JWT structure alone.** A token-shaped string is not valid unless signature, claims, freshness, and context are correct.
- **Logout as local storage deletion.** Clearing a browser or app token does not revoke server-side acceptance.
- **Generic rate limits only by IP.** Auth abuse often rotates IPs and needs account, credential, and route-aware controls.

## Practical labs

Use an owned lab with at least one normal account and one test admin account.

### Trace the auth state machine

```
anonymous -> password accepted -> MFA pending -> full session -> step-up verified
```

Map which token or cookie exists at each step and which endpoints accept it.

### Test pre-MFA access

```
curl -i -H "Authorization: Bearer $PRE_MFA_TOKEN" \
  https://api.example.test/billing/payment-methods
```

Sensitive endpoints should reject partial-auth tokens.

### Test revocation events

```
curl -i -H "Authorization: Bearer $OLD_TOKEN" https://api.example.test/users/me
```

Repeat after logout, password change, account disable, MFA reset, and role downgrade.

### Test recovery as login

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"email":"user@example.test"}' \
  https://api.example.test/auth/password-reset
```

Check token lifetime, replay behavior, post-reset sessions, and old session invalidation.

## Practical examples

- An API issues a bearer token before MFA is completed.
- Logout does not stop access-token reuse.
- A mobile endpoint accepts weaker credentials than the web app.
- Password reset creates a full session but leaves old refresh tokens active.
- An API key with no owner can access sensitive tenant data.

## Related notes

- [[api-auth-flaws]]
- [[jwt-attacks]]
- [[token-lifecycle]]
- [[api-rate-limiting]]
- [[auth-flaws|Auth Flaws]]

### Suggested future atomic notes

- partial-authentication-states
- mfa-bypass-patterns
- password-reset-api-security
- credential-stuffing-defenses
- service-account-authentication

## References

- **Foundational:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
