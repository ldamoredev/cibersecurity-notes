---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# JWT Cryptographic Correctness

## Definition

A JWT (RFC 7519) is a base64url-encoded `header.payload.signature` triple where the signature is either an HMAC tag (JWS HS*) or an asymmetric digital signature (JWS RS*, ES*, PS*, EdDSA). "JWT cryptographic correctness" means the verifier authenticates the signature with the *expected algorithm and key*, validates registered claims, and never trusts the header to choose the verification path.

## Why it matters

JWTs are the most commonly mis-implemented authentication primitive in modern web stacks. The header carries an `alg` field that suggests how to verify the signature — and historically many libraries did exactly what the header asked, including `alg: none`, `alg: HS256` with a public RSA key as the secret, or `kid`/`jku`/`jwk` headers that pointed at attacker-controlled keys. Each of these turns the token into an unauthenticated cookie that the attacker writes themselves. Reading JWT failures correctly is also a prerequisite for SAML/OIDC reasoning, API-token systems, and signed-cookie patterns.

## How it works

The structure:

```
header.payload.signature
header  = base64url({"alg":"RS256","kid":"abc","typ":"JWT"})
payload = base64url({"sub":"u-1","exp":1735689600,"iss":"https://idp"})
signature = sign(alg, key, header || "." || payload)
```

The 5 verification steps that must all be enforced:

1. **Decide the algorithm before parsing the token.** The verifier must know whether it expects HS256, RS256, ES256, EdDSA, etc. — based on configuration, not the token. Reading `header.alg` and trusting it is the original "alg confusion" bug.
2. **Resolve the key for that algorithm.** For HS*, a server-side secret. For RS*/ES*/PS*/EdDSA, a public key from a trusted JWKS endpoint or an embedded set.
3. **Verify the signature with the chosen `(alg, key)`.** Use a library that takes the algorithm as input, *not* one that reads it from the header.
4. **Validate the registered claims.** `exp` (expiration), `nbf` (not before), `iat` (issued at), `iss` (issuer), `aud` (audience), and any custom claims the application requires.
5. **Pin the token's purpose.** If the token is for API A, do not accept it for API B. Audience-mismatch is a common bug when one IdP issues tokens for many resource servers.

```
expected_alg = config["alg"]                  # NOT header.alg
key          = lookup(expected_alg, header.kid_if_safe)
verify(token, key, expected_alg)              # exact alg match
require(payload.exp > now and payload.iss == "https://idp" and aud_check)
```

The bug is not "JWT is broken"; it is "the verifier let the token decide which key and algorithm to use." Cryptographically, JWT is fine. Operationally, the JOSE flexibility (alg, kid, jku, jwk, x5u, x5c) is a footgun unless every dynamic field is constrained by configuration.

## Techniques / patterns

The reasoning model when reviewing JWT-using code:

- **What does the verifier expect for `alg`?** Hard-coded? Read from the token? "Whatever the library decides"?
- **Where does the key come from?** Static config? JWKS URL? Header-driven (`jku`, `jwk`, `kid` lookup)?
- **What claims are validated?** `exp`, `nbf`, `iss`, `aud`, custom?
- **Is there a clock skew?** A small positive skew (≤ 60s) is fine; large skews defeat `exp`.
- **Is the token bound to a session, channel, or origin?** JWT alone is bearer; pair with channel binding (DPoP, mTLS) or short lifetime + refresh for high-value flows.
- **Probe pattern in code review:** grep for `jwt.decode`, `jwt.verify`, `verify_options`, `algorithms=`, `verify=False`, `alg`, `kid`, `jku`, `jwk`, `x5u`, `x5c`. Each occurrence is a place where the verifier might be over-flexible.

## Variants and bypasses

The 7 historical (and current) JWT exploit shapes worth recognizing:

### `alg: none`

The original bug. The token is `header.payload.` with no signature, header `{"alg":"none"}`. Libraries that follow the header treated this as "no signature required" and accepted the token. Modern libraries refuse `none` by default, but configuration ("accept `none` if no key is configured") still appears in the wild.

### Algorithm confusion (RS256 → HS256)

The verifier expects RS256 (asymmetric: verify with the public key). The attacker changes the header to `HS256` and signs the token using the *server's RSA public key* as the HMAC secret. A library that reads `alg` from the header and calls `HS256_verify(public_key, token)` will accept it because the attacker computed an HMAC with that exact key. Fix: hard-code the expected algorithm; reject if the header disagrees.

### Weak HMAC secrets

HS256 with a guessable secret (`"secret"`, the company name, a URL slug). Offline brute force on the signature recovers the secret in seconds. Fix: 256-bit random secret minimum; rotate; prefer asymmetric for cross-org tokens.

### `kid` injection

The `kid` header points at a key in a server-side store. A path-traversal `kid` (`../../etc/passwd`), a SQL-injectable `kid`, or a `kid` that addresses a known-content file (`/dev/null` to make the secret empty) lets the attacker control which "key" verifies the signature. Fix: treat `kid` as an opaque ID, validate against an allowlist, never use it as a path or query fragment.

### `jku` / `jwk` / `x5u` / `x5c` injection

The JOSE header can carry a URL or inline key for verification. A verifier that fetches `jku` and trusts the returned JWKS allows the attacker to host their own key set and sign tokens themselves. Fix: never honor `jku`, `jwk`, `x5u`, or `x5c` from token headers in production verification; resolve keys only from the IdP's known JWKS URL.

### Missing or wrong claim validation

Tokens that are syntactically valid but have an expired `exp`, wrong `iss`, or wrong `aud` are accepted because the verifier only checked the signature. Fix: claim validation is part of "verify"; libraries usually require explicit `audience=` and `issuer=` parameters.

### Bearer-replay / stolen JWT

JWTs are bearer tokens by default. Anyone with the encoded string is the user. Fix: short lifetime, refresh tokens, channel binding (DPoP per RFC 9449, mTLS-bound tokens per RFC 8705), or sender-constrained access tokens.

### JWE confusion

JWE tokens (encrypted) and JWS tokens (signed) share the JOSE structure. A naive verifier that "just decodes" a token and trusts the payload may treat a JWE as a JWS, or vice versa. Fix: decide the format up front; reject the wrong shape.

## Impact

- **`alg: none` accepted:** total auth bypass; attacker mints any token.
- **Algorithm confusion:** total auth bypass when the public key is recoverable (which it usually is — JWKS is public).
- **Weak HMAC secret:** offline secret recovery → total auth bypass.
- **`kid`/`jku`/`jwk` injection:** verifier-controlled key → attacker-signed tokens accepted.
- **Missing `aud` validation:** cross-API token replay; a token meant for service A is accepted by service B.
- **Missing `exp`/`nbf`:** tokens never expire or are valid before they should be; revocation becomes operationally impossible.
- **Stolen bearer:** valid until expiry; if no short lifetime + refresh, exposure is hours to days.

Severity scales with token scope — root admin tokens, payment tokens, and tokens accepted by multiple resource servers are the highest-impact targets.

## Detection and defense

Ordered by what works:

1.
**Hard-code the expected algorithm; reject if the header disagrees.**
   `verify(token, key, algorithms=["RS256"])` (or `["EdDSA"]`). Never `algorithms=token.header.alg`. Never accept `none`.

2.
**Use asymmetric signatures for tokens crossing trust boundaries; HMAC only inside a single trust boundary.**
   RS256, PS256, ES256, or EdDSA between an IdP and resource servers. HS256 only if both sides are the same service or share a single secrets store. A breached resource server should not be able to mint tokens for other resources.

3.
**Resolve keys from the configured JWKS URL only; ignore header `jku`, `jwk`, `x5u`, `x5c`.**
   `kid` is acceptable as an opaque key index against the IdP's JWKS, but treat it as untrusted input — allowlist, never use as a path/query.

4.
**Validate registered claims explicitly.**
   `exp` must be in the future; `iat`/`nbf` must be sane; `iss` must match the expected issuer; `aud` must match the expected audience. Use the library's claim-validation parameters; do not write your own.

5.
**Keep tokens short-lived; pair with refresh tokens or sender-constrained tokens.**
   Access tokens of 5–15 minutes plus a refresh flow; or DPoP/mTLS-bound tokens for high-value APIs. Refresh tokens themselves should rotate and be one-time-use.

6.
**Reject tokens you do not intend to verify.**
   If your service expects RS256 from `https://idp.example/.well-known/jwks.json` for `aud=api.example`, anything else is rejected. No "fall back to local secret" path.

### What does not work as a primary defense

- **"We use JWT, so we are secure."** The JWT format does not make a system secure; correct verifier configuration does.
- **"We trust `header.alg`."** That is exactly the alg-confusion bug. Use a hard-coded algorithm.
- **"Our HMAC secret is `our-app-name-2026`."** Brute-forceable. Use a 256-bit CSPRNG-generated secret stored in a secrets manager.
- **"`exp` is far enough in the future that revocation does not matter."** Long-lived bearer tokens are the worst of both worlds — same exposure as a session cookie without the easy revocation. Use short tokens + refresh.
- **"We pass `verify=False` only in tests."** Tests that disable verification routinely escape into production via shared config helpers. Use explicit test fixtures that mint valid tokens, not unverified-decode helpers.
- **"We can use the same JWT for many APIs to make integration easier."** That is exactly an audience-mismatch attack vector. Per-audience tokens, even if it costs a refresh round trip.

## Practical labs

### Mint and verify a JWT correctly

```
# pip install pyjwt cryptography
import jwt, datetime, os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
sk = Ed25519PrivateKey.generate()
pk = sk.public_key()
sk_pem = sk.private_bytes_raw().hex()  # for demo only
now = datetime.datetime.utcnow()
token = jwt.encode(
    {"sub":"u-1","iss":"https://idp.example","aud":"api.example",
     "iat": now, "exp": now + datetime.timedelta(minutes=10)},
    sk, algorithm="EdDSA"
)
decoded = jwt.decode(token, pk, algorithms=["EdDSA"], audience="api.example", issuer="https://idp.example")
print(decoded)
```

Result: a correct verifier rejects mismatched algorithm, wrong audience, wrong issuer, or expired tokens.

### Reproduce `alg: none` on a vulnerable verifier

```
import base64, json
header = base64.urlsafe_b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b"=").decode()
payload = base64.urlsafe_b64encode(json.dumps({"sub":"admin"}).encode()).rstrip(b"=").decode()
token = f"{header}.{payload}."
# Send this to a verifier that trusts header.alg and observe whether it accepts the token
```

Result: a correctly configured verifier (`algorithms=["RS256"]`) rejects this immediately. A library or wrapper that reads `alg` from the header may accept it. The presence or absence of acceptance is the test.

### Reproduce algorithm confusion (RS → HS)

```
import jwt
public_pem = open("idp_public.pem","rb").read()
# Attacker signs with HS256 using the IdP's PUBLIC key as the HMAC secret
forged = jwt.encode({"sub":"admin"}, public_pem, algorithm="HS256")
# A vulnerable verifier that calls `decode(forged, public_pem)` without locking algorithms
# will try HS256 and succeed.
print(forged)
```

Result: the test target accepts the forged token only if the verifier reads `alg` from the header. This lab is the canonical demonstration of "always pin algorithms".

### Detect over-flexible verifier configuration in code

```
# Sniff Python/Node/Java code for JWT misuse patterns
rg -n "jwt\.decode\(|jwt\.verify\(|verify\(.*algorithms\s*=\s*\[" .
rg -n "algorithms\s*=\s*token\.header|header\[.alg.\]" .
rg -n "alg.*none|verify_signature\s*=\s*False" .
```

Result: every occurrence is a review point. Confirm the algorithm is hard-coded and `none` is rejected.

### JWKS rotation lab

```
1. Stand up an IdP with two RSA key pairs (current + next), publish both at /.well-known/jwks.json.
2. Mint tokens with kid=current.
3. Rotate: mint with kid=next, keep current published for the legacy refresh window.
4. Confirm the resource server resolves keys via JWKS and accepts both during the overlap.
```

Result: a working rotation playbook proves your verifier can survive key rotation without downtime, which is the prerequisite for short-lived signing keys.

## Practical examples

- A microservice imports `jsonwebtoken` and calls `verify(token, key)` with no `algorithms` option. A penetration test demonstrates RS→HS confusion. Fix: pin `algorithms: ['RS256']`.
- An admin tool issues HS256 tokens with secret `admin-prod-2026`. The secret leaks via a public commit. Fix: rotate, switch to RS256/EdDSA from a KMS-managed key.
- A multi-API gateway accepts any JWT signed by the corporate IdP. A token issued for the test API is replayed against the production billing API. Fix: enforce `aud=billing.example` on the billing API.
- A mobile app decodes the JWT locally to "extract the user id" and trusts the payload. Local decode is acceptable for display; never make a security decision on decoded-but-unverified payloads.
- A new service implements its own JWT library because "the standard one is too heavy". The custom verifier accidentally treats `alg: HS256` and `alg: RS256` interchangeably. Replace with a vetted library; delete the custom code.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[digital-signatures]]
- [[asymmetric-encryption-and-key-exchange]]
- [[random-and-csprng-pitfalls]]
- [[jwt-attacks|JWT Attacks]]
- [[token-lifecycle|Token Lifecycle]]
- [[auth-flaws|Auth Flaws]]
- [[oauth-security|OAuth Security]]

### Suggested future atomic notes

- oidc-deep-dive
- dpop-and-sender-constrained-tokens
- mtls-bound-tokens-rfc-8705
- jwks-rotation-and-kid-handling
- paseto-and-jwt-alternatives
- jwt-claim-validation-pitfalls

## References

- **Foundational:** OWASP JSON Web Token for Java Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **Standard / RFC:** RFC 7519 JSON Web Token (JWT) — https://www.rfc-editor.org/rfc/rfc7519
- **Testing / Lab:** PortSwigger JWT attacks — https://portswigger.net/web-security/jwt
- **Research / Deep Dive:** Auth0 JWT handbook — https://auth0.com/resources/ebooks/jwt-handbook
