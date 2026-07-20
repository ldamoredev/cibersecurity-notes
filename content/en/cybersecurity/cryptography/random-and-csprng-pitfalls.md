---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Random and CSPRNG Pitfalls

## Definition

A cryptographically secure pseudorandom number generator (CSPRNG) produces unpredictable bytes suitable for keys, nonces, session ids, CSRF tokens, salts, and challenges. Randomness failures happen when security-critical values are generated with predictable, low-entropy, repeated, biased, or attacker-influenced sources.

## Why it matters

Many security controls reduce to "the attacker cannot guess this value before it expires." Session ids, password reset tokens, OAuth state, WebAuthn challenges, API keys, encryption keys, and nonces all depend on that assumption. If randomness is weak, the surrounding crypto can be mathematically correct and still fail completely. This is the quiet failure underneath broken sessions, repeated AES-GCM nonces, predictable reset links, and duplicated VM keys.

## How it works

Randomness for security has **4 requirements**:

1.
**Enough entropy**
   The value must come from a source with enough uncertainty. A timestamp, PID, username, or counter is not entropy.

2.
**Unpredictability**
   Observing previous outputs should not let an attacker predict future outputs.

3.
**Uniqueness where required**
   Some values, such as nonces, need uniqueness under a key. They may not need secrecy, but repeats can be catastrophic.

4.
**Correct API use**
   The application must use OS-backed cryptographic APIs, not general-purpose PRNGs.

```
// Good: Node CSPRNG
import crypto from "node:crypto";
const token = crypto.randomBytes(32).toString("base64url");

// Bad: predictable PRNG
const token2 = Math.random().toString(36).slice(2);
```

The bug is not "randomness is hard." The bug is usually using a convenience random function where the design needs an attacker-resistant secret or unique value.

## Techniques / patterns

- Search for `Math.random`, `random()`, `rand()`, `mt_rand`, `java.util.Random`, timestamps, counters, UUIDv1, or homegrown token generation.
- Check token length in bits, not characters. Encoding expands or changes representation; it does not create entropy.
- Check whether values need secrecy, uniqueness, or both. Keys need secrecy; AES-GCM nonces need uniqueness; session ids need unguessability.
- Check VM/container cloning. Systems cloned before entropy pools are ready can generate duplicate keys or tokens.
- Check test fixtures and defaults. "temporary" deterministic secrets often escape into production.
- Check modulo bias when mapping random bytes to characters or numbers.

## Variants and bypasses

Randomness failures appear in **5 common families**.

### 1. General-purpose PRNG used for secrets

Language PRNGs are often deterministic and optimized for simulation, not adversaries. If an attacker can infer seed state, outputs become predictable.

### 2. Timestamp or counter tokens

Tokens derived from time, user id, request count, or process id are searchable. Attackers can bracket the creation time and brute force the missing space.

### 3. Insufficient length

A 6-digit numeric code has about 20 bits of space. That can be fine with tight online rate limits and short expiry, but not as a long-lived bearer secret.

### 4. Nonce reuse

Nonce reuse under the same key breaks stream ciphers and AEAD modes such as AES-GCM and ChaCha20-Poly1305. Reuse can expose plaintext relationships and sometimes authentication keys.

### 5. Biased mapping

Using modulo arithmetic over random bytes to choose characters can make some outputs more likely than others. Bias becomes exploitable when the space is already small or many samples are visible.

## Impact

Ordered roughly by severity:

- **Session takeover.** Predictable session ids or reset tokens become authentication bypass.
- **Key compromise.** Weak key generation can make encrypted data brute-forceable.
- **AEAD failure.** Repeated nonces can destroy confidentiality and integrity.
- **CSRF/OAuth bypass.** Predictable state/challenge values allow request binding failures.
- **Fleet-wide duplicate secrets.** VM images or containers cloned with seeded state generate repeated keys across systems.

## Detection and defense

Ordered by effectiveness:

1.
**Use OS-backed CSPRNG APIs.**
   Use `crypto.randomBytes`, `crypto.getRandomValues`, `/dev/urandom` through vetted libraries, `secrets` in Python, `SecureRandom` correctly in Java, and equivalent platform APIs.

2.
**Design values by required property.**
   Keys need secrecy; nonces need uniqueness under a key; salts need uniqueness; challenges need unpredictability and freshness. Do not use one generator pattern for every case without naming the property.

3.
**Use adequate lengths.**
   Session ids, API keys, and reset tokens should generally use at least 128 bits of entropy; 192 or 256 bits is often cheap and boring.

4.
**Let AEAD libraries generate or manage nonces where possible.**
   If you must manage nonces, persist counters or use misuse-resistant modes such as AES-GCM-SIV when repeat risk is real.

5.
**Test for forbidden APIs in CI.**
   Static checks for `Math.random` or `rand()` in auth/crypto paths catch many avoidable mistakes.

### What does not work as a primary defense

- **Base64 or hex encoding.** Encoding does not add entropy.
- **Hashing a timestamp.** Hashing predictable input gives predictable output.
- **UUIDs without understanding version.** UUIDv4 is random; UUIDv1 leaks time/MAC structure; UUIDs are not automatically secrets.
- **Short expiry alone.** Expiry helps only if guessing is also rate-limited and the space is large enough.
- **"It is only internal."** Internal tokens often cross logs, queues, browsers, and services.

## Practical labs

### Compare predictable and secure token generation

```
node - <<'JS'
const crypto = require("node:crypto");
for (let i = 0; i < 3; i++) {
  console.log("bad-ish", Math.random().toString(36).slice(2));
  console.log("good", crypto.randomBytes(32).toString("base64url"));
}
JS
```

The secure tokens are longer and backed by the OS CSPRNG; the point is API choice, not visual randomness.

### Estimate brute-force space

```
python3 - <<'PY'
import math
for bits in [20, 32, 64, 128, 256]:
    print(bits, "bits =", f"{2**bits:.3e}", "possibilities")
PY
```

Short codes need rate limits because their search space is intentionally small.

### Detect forbidden random APIs

```
rg -n "Math\\.random|\\brand\\(|\\bmt_rand\\b|java\\.util\\.Random|new Random" .
```

Every match in token, auth, password-reset, nonce, or key-generation code deserves review.

### Generate a 256-bit secret safely

```
openssl rand -base64 32
python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
```

Use platform CSPRNG helpers instead of inventing token formats.

## Practical examples

- A password reset link uses `md5(user_id + timestamp)`, letting attackers brute force reset URLs for recently requested accounts.
- A service uses `Math.random()` for session ids. Process restart reseeds predictably and sessions become guessable.
- A VM image includes a generated SSH host key; every cloned VM has the same identity.
- An AES-GCM service uses a timestamp nonce and high request concurrency creates nonce collisions.
- OAuth state is a short counter; login CSRF becomes practical.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[aead-and-nonce-misuse]]
- [[password-hashing]]
- [[session-management|Session Management]]
- [[token-lifecycle|Token Lifecycle]]

### Suggested future atomic notes

- token-entropy-review
- uuid-security-properties
- nonce-generation-patterns
- vm-cloning-and-entropy

## References

- **Standard / RFC:** NIST SP 800-90A Rev. 1: Random Bit Generation — https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final
- **Standard / RFC:** NIST SP 800-90B: Entropy Sources — https://csrc.nist.gov/publications/detail/sp/800-90b/final
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
