---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# JWT Attacks

## Definition

JWT attacks exploit weaknesses in how JSON Web Tokens are issued, validated, trusted, scoped, or expired. The risk is not that an API uses JWTs; the risk is accepting token content without the right cryptographic and contextual checks.

## Why it matters

JWTs are portable trust containers. That portability is useful for APIs and microservices, but it also means a bad validation decision can propagate across services, clients, and authorization layers.

This note focuses on token validation and token-contained trust. [[broken-authentication]] stays broader, and [[token-lifecycle]] owns issuance, refresh, rotation, revocation, and expiry behavior over time.

## How it works

A JWT consumer must pass **6 validation gates**:

1. **Structure.** The token is well-formed and decoded safely.
2. **Signature.** The signature is valid for the expected algorithm and key.
3. **Issuer.** `iss` matches the trusted identity provider.
4. **Audience.** `aud` matches this API or service.
5. **Time.** `exp`, `nbf`, and `iat` are acceptable for this trust decision.
6. **Claims and context.** `sub`, `scope`, `role`, tenant, session, and assurance claims are authorized for the action.

JWT attacks usually exploit one missing gate or inconsistent gates across services.

Example inspection:

```
jq -R 'split(".") | .[0], .[1] | @base64d | fromjson' <<< "$JWT"
```

Decoding is not validation. It only reveals what the token claims.

## Techniques / patterns

Attackers test:

- expired token reuse
- wrong `aud` or `iss` acceptance
- algorithm confusion or weak key selection
- acceptance of unsigned or improperly signed tokens
- stale roles, scopes, or tenant claims after change
- inconsistent validation between services
- logout, password reset, and revocation expectations

## Variants and bypasses

JWT attacks appear in **7 common forms**.

### 1. Signature validation failure

The service decodes the token but does not properly verify the signature.

### 2. Algorithm and key confusion

The service accepts unexpected algorithms, uses the wrong key source, or trusts attacker-influenced key metadata.

### 3. Issuer or audience mismatch

A token minted for another service, tenant, or environment is accepted.

### 4. Expiry and freshness failure

Expired, not-yet-valid, or very old tokens remain usable.

### 5. Stale authorization claims

Roles or scopes in old tokens continue to grant access after privilege changes.

### 6. Cross-service inconsistency

One API validates claims strictly while another service accepts weaker tokens.

### 7. Token presence confusion

The application treats "has a JWT" as equivalent to "may perform this action."

## Impact

Ordered roughly by severity:

- **Authentication bypass.** Invalid or attacker-crafted tokens are accepted.
- **Privilege escalation.** Stale or manipulated claims grant stronger access.
- **Cross-service access.** Tokens for one audience work against another API.
- **Persistent access.** Tokens survive logout, password change, or role downgrade.
- **Tenant boundary break.** Tenant claims are trusted without server-side authorization.

## Detection and defense

Ordered by effectiveness:

1.
**Use vetted JWT libraries with strict verification settings.**
   Do not hand-roll JWT validation. Configure allowed algorithms, expected issuer, expected audience, clock skew, and required claims explicitly.

2.
**Pin trust to expected issuer, audience, algorithm, and key material.**
   A valid signature is not enough if the token came from the wrong issuer or was meant for another service.

3.
**Keep tokens short-lived and narrowly scoped.**
   Short lifetimes reduce stale-claim risk. Narrow audiences and scopes reduce blast radius.

4.
**Treat JWT claims as inputs to authorization, not final authority.**
   Roles, tenant IDs, and scopes still need server-side policy checks against the requested object and action.

5.
**Design revocation and key rotation deliberately.**
   Stateless tokens still need practical answers for logout, compromise, role change, and signing-key rollover.

6.
**Test every token consumer.**
   In microservices, the weakest consumer defines the effective trust boundary.

### What does not work as a primary defense

- **Base64 decoding checks.** Reading the payload is not signature validation.
- **Trusting `alg`, `kid`, or key URLs from untrusted input.** Header metadata must not select arbitrary trust roots.
- **Long-lived role claims.** Roles embedded for hours or days become stale authority.
- **JWTs as authorization by themselves.** Tokens identify and carry claims; policy still decides access.
- **Logout that only deletes the browser token.** Other copies of the token may remain usable.

## Practical labs

Use only tokens from systems you own or intentionally vulnerable labs.

### Decode and document validation assumptions

```
jq -R 'split(".") | .[0], .[1] | @base64d | fromjson' <<< "$JWT"
```

Record `alg`, `kid`, `iss`, `aud`, `sub`, `exp`, `iat`, scopes, roles, and tenant claims.

### Test audience and issuer boundaries

```
curl -i -H "Authorization: Bearer $TOKEN_FOR_OTHER_API" \
  https://api.example.test/users/me
```

The API should reject tokens minted for a different audience or issuer.

### Test expiry behavior

```
curl -i -H "Authorization: Bearer $EXPIRED_TOKEN" \
  https://api.example.test/users/me
```

Expired tokens should fail consistently across all services.

### Test stale privilege claims

```
curl -i -H "Authorization: Bearer $OLD_ADMIN_TOKEN" \
  https://api.example.test/admin/users
```

After role downgrade, old privileged tokens should not keep granting sensitive access beyond the intended window.

## Practical examples

- A token with the wrong audience is accepted by an internal API.
- One service accepts expired tokens while another rejects them.
- A role downgrade does not affect previously issued admin tokens.
- JWT header metadata leads the verifier to the wrong key.
- A service checks signature but ignores tenant authorization.

## Related notes

- [[broken-authentication]]
- [[api-auth-flaws]]
- [[token-lifecycle]]
- [[authorization]]
- [[break-jwt-validation|Break JWT Validation]]
- [[session-management|Session Management]]

### Suggested future atomic notes

- jwt-audience-validation
- jwt-key-confusion
- stale-jwt-claims
- jwt-revocation-strategies
- microservice-token-validation

## References

- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP JSON Web Token for Java Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger JWT attacks topic — https://portswigger.net/web-security/jwt
