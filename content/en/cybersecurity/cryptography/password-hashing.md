---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Password Hashing

## Definition

Password hashing is a deliberately slow, memory-hard, salted, keyed transformation that converts a user-supplied password into a verifier that is expensive to brute-force even when the verifier database leaks. It is *not* general-purpose hashing (SHA-256), is *not* encryption, and is *not* a MAC — it is its own primitive built specifically to resist offline cracking.

## Why it matters

Almost every leaked credential database that was useful to attackers was useful because the verifier was wrong: plaintext, MD5, SHA-1, unsalted SHA-256, fast-cycle bcrypt, or "encrypted" with a recoverable key. Modern GPUs and ASICs can compute tens of billions of plain SHA-256 hashes per second. A correct password hash function makes that throughput economically pointless. The only reasonable defaults today are Argon2id, scrypt, or bcrypt — chosen by ecosystem fit, parameterized for current hardware, and verified with constant-time comparison.

## How it works

Password hashing solves a different problem from data hashing. The 4 ingredients:

1. **Slowness (work factor / iteration count / memory cost).** A correct password hash must take meaningful CPU and ideally meaningful memory. The legitimate user pays this cost once per login. The attacker pays it for every guess in an offline crack.
2. **Salt (per-user random).** A unique salt per user prevents precomputation (rainbow tables) and ensures that two users with the same password produce different verifiers.
3. **Pepper (server-side secret, optional).** A site-wide secret mixed into the hash that lives outside the database (HSM, KMS, env). If only the database leaks, the pepper raises the cracking cost from "expensive" to "infeasible without also stealing the pepper."
4. **Memory hardness.** Modern functions (Argon2, scrypt) require significant memory per guess, defeating cheap parallelism on GPUs and ASICs.

```
verifier = encode(
    algorithm,         // argon2id, scrypt, bcrypt
    parameters,        // cost / m / t / p
    salt,              // 16 bytes random per user
    H(password, salt, pepper, parameters)
)
```

The bug is not "we used a hash"; it is "we used a hash that is too fast and too cheap." Password hashing is the one place in cryptography where slow is the feature.

## Techniques / patterns

The reasoning model when reviewing password storage:

- **Algorithm fit:** Argon2id (RFC 9106) is the modern default; scrypt is mature and widely supported; bcrypt is acceptable up to 72 bytes of input. PBKDF2 is allowed under FIPS but is the weakest of the four for password use.
- **Parameter fit:** the cost should saturate the user-facing latency budget on the smallest production node — typically 0.25–1 second per login. Re-tune annually.
- **Salt presence and shape:** 16 random bytes minimum, stored *with* the hash (encoded into the verifier).
- **Pepper presence:** if the threat model includes database-only leak, a pepper raises the bar dramatically.
- **Verifier shape:** a self-describing string (`$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>`) carries the algorithm and parameters with the hash so the verifier can upgrade old entries on next login.
- **Constant-time comparison:** verifier comparison must use a constant-time function — naive `==` on hashes leaks timing.
- **Probe pattern in code review:** grep for `md5(`, `sha1(`, `sha256(` near `password`, `pwd`, `passwd`, `secret`. Look for any custom hashing function. Check that the comparison is constant-time. Confirm there is a salt per user.

## Variants and bypasses

The 4 password-hashing functions you will see in the wild, with their tradeoffs.

### Argon2id (modern default)

Argon2id is the winner of the Password Hashing Competition (2015), standardized as RFC 9106. It combines the side-channel resistance of Argon2i with the GPU resistance of Argon2d. Parameters: memory cost `m` in KiB, time cost `t` in iterations, parallelism `p`. Sensible 2026-era defaults: `m = 19 MiB to 64 MiB, t = 2 to 3, p = 1 to 4`, tuned to ~1 second on the target node.

### scrypt

scrypt (RFC 7914) was designed for memory hardness. Mature, widely supported. Parameters: `N` (CPU/memory cost, power of 2), `r` (block size, usually 8), `p` (parallelism, usually 1). Sensible defaults: `N = 2^17, r = 8, p = 1` for ~256 MiB and ~1 second.

### bcrypt

bcrypt (1999) is older but still acceptable. Parameters: `cost` (work factor, 2^cost). Limit: input is truncated to 72 bytes; pre-hash long inputs with HMAC-SHA-256 or use a different algorithm. Sensible defaults for 2026: `cost = 12 or 13`.

### PBKDF2

PBKDF2 (RFC 8018) is FIPS-approved but the weakest of the four. Use only when an environment requires FIPS 140-3 validated cryptography and Argon2id/scrypt are unavailable. Sensible defaults for 2026: PBKDF2-HMAC-SHA-256 with `≥ 600,000` iterations, per OWASP.

## Impact

Severity is dominated by the speed of the verifier and the size of the salt + pepper space:

- **Plaintext storage:** instant compromise of every password on leak. Same for reversibly "encrypted" passwords.
- **Unsalted SHA-1 / SHA-256 / MD5:** rainbow-table cracking; entire database broken in hours on consumer hardware.
- **Salted but fast hash:** GPU-cracked at 10⁹ to 10¹⁰ guesses per second per modern card; common-password lists clear millions of users in days.
- **Salted bcrypt cost 8 / scrypt low N / Argon2 t=1 m=4 MiB:** still crackable on dedicated hardware, but slow enough that mass cracking is uneconomic.
- **Salted Argon2id with current parameters + pepper:** offline cracking is largely uneconomic. The remaining risk shifts to credential stuffing, phishing, and password reuse — not the verifier itself.

Severity escalates when the password also unlocks high-value targets (admin, payment, encryption keys), when MFA is absent, and when password reuse across services is likely.

## Detection and defense

Ordered by what works:

1.
**Use Argon2id with parameters tuned to ~1 second on your slowest production node.**
   `m = 19456 KiB (19 MiB), t = 2, p = 1` is the OWASP-recommended starting point as of 2024–2026. Re-tune annually as hardware advances.

2.
**Use a per-user salt of at least 16 random bytes from a CSPRNG.**
   Store it with the verifier in the encoded string. Unique salt per user prevents rainbow tables and equality-of-hash attacks across users.

3.
**Use a server-side pepper kept outside the database.**
   HMAC-SHA-256(pepper, password) before hashing, or use a library that supports a server secret natively. Pepper lives in HSM/KMS/env, not the same SQL row as the verifier.

4.
**Compare in constant time and rehash on parameter upgrade.**
   `crypto.timingSafeEqual`, `hmac.compare_digest`, or library `verify` functions that handle the comparison. After a successful login, if the stored parameters are below current targets, transparently re-hash with new parameters.

5.
**Pair password hashing with rate limiting and MFA.**
   Even a perfect verifier does not stop online guessing. Throttle, lock, alert, and prefer phishing-resistant MFA — see [[mfa-phishing-resistance|MFA Phishing Resistance]].

### What does not work as a primary defense

- **"We use SHA-256 with a salt."** SHA-256 is too fast. Salting prevents rainbow tables but does not slow per-guess cost. Switch to Argon2id or scrypt.
- **"We use MD5 but with a long salt."** MD5 is broken for collisions and far too fast. Replace.
- **"We encrypt the password and decrypt it on login."** Decryption means the key exists; the key will eventually leak. Use a hash function, not encryption.
- **"We store the password hashed once with bcrypt cost 4."** Cost 4 is below the legitimate-user latency budget; this is essentially unsalted hash from a cracker's perspective.
- **"We compare with `==`."** Naive equality leaks per-byte timing; an attacker can recover the verifier by timing.
- **"Bcrypt limits inputs to 72 bytes, so we just truncate."** Silent truncation makes long passwords equivalent to their first 72 bytes; collisions become easy. Pre-hash with HMAC-SHA-256 or move off bcrypt.
- **"We hashed the password before sending over the wire so the server never sees it."** That just moves the password — the hash *is* the password. The server still needs a server-side hash; client-side hashing alone is not a substitute.

## Practical labs

### Hash a password with Argon2id and verify it

```
# pip install argon2-cffi
from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)  # ~1s target
verifier = ph.hash("correct horse battery staple")
print(verifier)  # $argon2id$v=19$m=19456,t=2,p=1$...$...
print(ph.verify(verifier, "correct horse battery staple"))
print(ph.check_needs_rehash(verifier))  # False if parameters match
```

Result: the verifier is self-describing. Compare timings of correct vs incorrect passwords; both should be the same wall-clock time (constant-time inside the library).

### Compare bcrypt cost factors and time them

```
import bcrypt, time
pw = b"correct horse battery staple"
for cost in (8, 10, 12, 13):
    salt = bcrypt.gensalt(rounds=cost)
    t0 = time.time()
    bcrypt.hashpw(pw, salt)
    print(cost, round(time.time() - t0, 3), "s")
```

Result: each `+1` to cost roughly doubles time. Pick the highest cost where login latency stays under your budget.

### Demonstrate why naive equality is wrong

```
import secrets, time
def naive_eq(a, b):
    if len(a) != len(b): return False
    for x, y in zip(a, b):
        if x != y: return False
    return True
target = secrets.token_bytes(32)
# Time a comparison where the first byte matches vs. does not
```

Result: with enough samples, the matching-prefix comparison is measurably slower. Use `hmac.compare_digest` or `secrets.compare_digest` instead.

### Show why a pepper raises the bar

```
import hmac, hashlib, os
pepper = os.environ["PASSWORD_PEPPER"].encode()  # not in the DB
def pre_hash(pw): return hmac.new(pepper, pw, hashlib.sha256).digest()
# feed pre_hash(pw) into Argon2id instead of pw
```

Result: an attacker who steals only the database cannot crack offline without also stealing the pepper. Combine with library-native server-secret support if available.

### Inventory existing verifiers in a sample app

```
# Quick sniff for legacy hashing in source
rg -i "md5\(|sha1\(|sha256\(.+password|hashlib\.md5|new MD5|MessageDigest\.getInstance\(\"MD5\"\)" .
# Sniff for missing salt
rg -i "hash\(\s*pw\s*\)" .
```

Result: a non-empty hit list is the migration backlog.

## Practical examples

- A SaaS imports a legacy CSV with `md5(password)` for 800k users. Migration plan: on next successful login, pre-hash the supplied password with the same legacy MD5, compare against the stored verifier, then re-hash with Argon2id and update the row. After a deadline, force password reset for stragglers.
- An internal tool stores bcrypt with cost 4 because "we tested cost 12 and it slowed login to 700 ms." That latency budget is the *point*; raise cost to 12, scale the auth service horizontally, and add MFA.
- A self-built encryption product "encrypts" passwords with AES-GCM using a key in `config.yml`. The first config leak compromises every user. Switch to Argon2id; remove the encryption code path.
- A microservice compares password hashes using `==`. Add a constant-time comparison and a unit test that fails if the comparison is replaced with naive equality.
- A long-password user reports inconsistent behavior with bcrypt at 73 bytes. The library silently truncated. Either pre-hash with HMAC-SHA-256 or switch to Argon2id.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[kdf-and-key-stretching]]
- [[mac-and-hmac]]
- [[random-and-csprng-pitfalls]]
- [[auth-flaws|Auth Flaws]]
- [[session-management|Session Management]]
- [[mfa-phishing-resistance|MFA Phishing Resistance]]

### Suggested future atomic notes

- credential-stuffing-and-mitigations
- breached-password-detection
- password-spraying
- opaque-and-pake-protocols
- passwordless-and-passkey-migration

## References

- **Foundational:** OWASP Password Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **Standard / RFC:** RFC 9106 Argon2 Memory-Hard Function — https://www.rfc-editor.org/rfc/rfc9106
- **Standard / RFC:** NIST SP 800-63B Digital Identity Guidelines (Memorized Secret Verifiers) — https://pages.nist.gov/800-63-3/sp800-63b.html
