---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Hashing vs Encryption vs Signing

## Definition

Hashing, encryption, and signing are three different cryptographic primitives that solve three different problems: hashing produces a fixed-size, one-way fingerprint of data; encryption transforms data so only a key holder can read it; signing produces a token that proves a specific key holder authored a specific message. Almost every "we used crypto" bug is really a "we used the wrong primitive" bug.

## Why it matters

The single most common cryptography mistake in real systems is choosing the wrong primitive: hashing a password with SHA-256 (fast, no stretching), "encrypting" data with a hash (impossible — it is one-way), "signing" a session by encrypting with a shared secret (that is a MAC, not a signature), or "verifying" identity with a hash that anyone can recompute. Knowing what each primitive *guarantees* is the entry ticket to reading TLS, JWT, password storage, MFA, and secret-management failures correctly.

## How it works

The three primitives are distinguished by **direction**, **key model**, and **what they prove**:

1.
**Hashing** — one-way, no key, fixed-size output. Given input *m* you compute `H(m)`. There is no inverse function. The guarantee is *integrity*: if `H(m)` matches a known value, the input is the same. There is no secrecy and no authorship guarantee. Examples: SHA-256, SHA-3, BLAKE2, BLAKE3.

2.
**Encryption** — two-way (with a key), output size ≈ input size + overhead. Given input *m* and key *k* you compute `Enc(k, m) = c`, and `Dec(k, c) = m`. The guarantee is *confidentiality*: only key holders can read *m*. By itself encryption does **not** prove authorship or detect tampering — that is what AEAD (authenticated encryption) or a separate MAC provides.

3.
**Signing** — asymmetric authorship proof. Given private key `sk` and message *m*, the signer computes `Sign(sk, m) = σ`. Anyone with the matching public key `pk` can run `Verify(pk, m, σ)` and learn whether the holder of `sk` actually produced the signature. The guarantee is *authenticity* and *non-repudiation*. Examples: RSA-PSS, ECDSA, Ed25519.

```
hash:      H(m) -> digest                  (no key, no inverse)
encrypt:   Enc(k, m) -> c    Dec(k, c) -> m (symmetric or asymmetric)
sign:      Sign(sk, m) -> σ  Verify(pk, m, σ) -> bool
```

The bug is not "we used crypto wrong"; it is "we picked a primitive whose guarantee does not match the threat model." A password-equality check needs slow keyed hashing. A session-token check needs a MAC or signature. A confidential field at rest needs AEAD. Hashing alone never solves confidentiality, MAC-less encryption never solves authenticity, and signing never solves secrecy.

## Techniques / patterns

The reasoning model is: *what threat are we defending against, and which primitive proves the absence of that threat?*

- **What needs to stay secret?** Confidentiality → AEAD encryption (e.g. AES-GCM, ChaCha20-Poly1305).
- **What needs to be unforgeable but readable?** Integrity + authenticity, no secrecy → MAC (HMAC) or signature.
- **What needs both unforgeable *and* secret?** Encrypt-then-MAC, or AEAD.
- **What needs to be non-repudiable across organizational trust boundaries?** Signature, not MAC. A MAC verifier has the same key as the signer, so it could have produced the MAC itself; that breaks non-repudiation.
- **What needs to be a fingerprint only?** Hash. But not for passwords (see [[password-hashing]]).
- **Probe pattern in code review:** find every call to `hash`, `encrypt`, `sign`, `verify`, `compare`, or `==` over secret-shaped data. For each one, ask "what threat does this defend against, and does this primitive actually defend against it?"

## Variants and bypasses

The primitive family splits into 5 useful sub-categories that show up in real systems. Knowing them prevents the most common confusion.

### Plain (unkeyed) hash

SHA-256 of a value. Anyone can recompute it given the same input. Useful for content-addressing, integrity check against a known good digest, and Merkle trees. Useless for password storage (no slowness, no secret), useless for "signing" (no key, no authorship), and never appropriate for HMAC by itself.

### Keyed hash / MAC

HMAC-SHA-256, KMAC, BLAKE3 with key. Two parties sharing a key can prove a message was authored by *someone with the key*. Symmetric: verifier and signer are interchangeable. This is a tag, not a signature. JWTs with `alg=HS256` are MACs, not signatures.

### Symmetric encryption

AES-GCM, ChaCha20-Poly1305, AES-CBC + HMAC. Both parties share a key. Only key holders can decrypt. AEAD modes also detect tampering. CBC + HMAC needs careful order (encrypt-then-MAC).

### Asymmetric encryption

RSA-OAEP, ECIES, hybrid encryption (encrypt symmetric data key with the public key, encrypt the payload with that data key). Sender uses recipient's *public* key, recipient decrypts with their *private* key. Slower than symmetric and bandwidth-bound; almost always used in hybrid mode.

### Digital signature

RSA-PSS, ECDSA, Ed25519. Signer uses *private* key, anyone uses *public* key to verify. The signature proves authorship and integrity, not secrecy. WebAuthn, TLS server-auth, code signing, JWT `alg=RS256`/`ES256`/`EdDSA`, package signing, and PGP signatures all live here.

## Impact

Choosing the wrong primitive escalates almost linearly with how trusted the wrong artifact looks:

- Hashing a password without stretching → entire password database is brute-forceable on a GPU farm.
- Encryption without authentication → padding-oracle attacks (e.g., CBC without MAC), bit-flip attacks, ciphertext malleability, and silent corruption.
- Hashing instead of MAC for tokens → anyone who can read the token can forge new ones.
- MAC instead of signature for cross-org tokens → either party can claim the other forged the message; non-repudiation lost.
- Signing without verifying → no security at all (a surprisingly common bug; the verifier was never wired up).
- Signing the wrong field → "signed" the metadata but not the body; attacker swaps the body.

Severity escalates further when the artifact crosses trust boundaries (multi-tenant, cross-organization, public mirror) or governs authentication, payments, or release artifacts.

## Detection and defense

Ordered by what works:

1.
**Pick the primitive by the guarantee you need, not by the verb in the requirement.**
   "Encrypt the password" is almost always wrong; the requirement is *verify the password*, which needs slow keyed hashing. "Sign the cookie" is almost always actually MAC. "Hash the file for integrity" is fine if you only need integrity against accidents, but for adversarial tampering you need a MAC or signature. Translate verbs into guarantees first.

2.
**Use AEAD for encryption by default.**
   AES-256-GCM, AES-256-GCM-SIV, ChaCha20-Poly1305. AEAD bundles confidentiality and integrity in one primitive and removes the encrypt-then-MAC ordering bug.

3.
**Use HMAC for keyed integrity, not "encryption with a hash" or `==`.**
   HMAC-SHA-256 is the workhorse. Compare with constant-time equality (`crypto.timingSafeEqual`, `hmac.compare_digest`) — *not* `==`, which leaks timing.

4.
**Use signatures for cross-trust authenticity.**
   Ed25519 is the modern default; RSA-PSS for compatibility; ECDSA-P256 for ecosystems that require it. Never use ECDSA without a deterministic nonce (RFC 6979) or a CSPRNG-backed nonce — nonce reuse leaks the private key (Sony PS3, Bitcoin wallet incidents).

5.
**Use slow, memory-hard password hashing (not general-purpose hashing) for passwords.**
   Argon2id, scrypt, bcrypt. SHA-256 of a password is not password hashing — see [[password-hashing]].

### What does not work as a primary defense

- **"We hashed it, so it is secure."** Hashing is not encryption and not signing. A plain hash provides integrity against accidental corruption; it provides nothing against an attacker who can recompute it.
- **"We encrypted it, so it cannot be tampered with."** Encryption alone does not detect tampering. Use AEAD or encrypt-then-MAC.
- **"We use SHA-256, that is FIPS-approved, so password storage is fine."** FIPS approval of the primitive is unrelated to its fitness for password storage. SHA-256 is too fast to be a password verifier.
- **"We MAC it, so it is signed."** A MAC is symmetric. Either party could have produced it. For cross-organization or auditable authorship, you need an actual signature.
- **"We compare with `==`."** Naive equality is timing-side-channel vulnerable on tags, MACs, and HMACs. Always use constant-time equality.

## Practical labs

### Show the difference between hashing, encrypting, and signing the same data

```
# hash
echo -n "hello" | openssl dgst -sha256
# encrypt with AES-GCM (AEAD)
openssl rand -hex 32 > key.hex
KEY=$(cat key.hex)
echo -n "hello" | openssl enc -aes-256-gcm -K "$KEY" -iv $(openssl rand -hex 12) -A -a
# sign with Ed25519 (modern signature)
openssl genpkey -algorithm ed25519 -out sk.pem
openssl pkey -in sk.pem -pubout -out pk.pem
echo -n "hello" > m.txt
openssl pkeyutl -sign -inkey sk.pem -rawin -in m.txt -out sig.bin
openssl pkeyutl -verify -pubin -inkey pk.pem -rawin -in m.txt -sigfile sig.bin
```

Compare what each operation produces and what each one allows the verifier to learn.

### Demonstrate that encryption alone does not detect tampering

```
# encrypt with AES-CBC and no MAC (intentionally bad)
openssl rand -hex 32 > key.hex && openssl rand -hex 16 > iv.hex
echo -n "transfer 100 to alice" | openssl enc -aes-256-cbc -K "$(cat key.hex)" -iv "$(cat iv.hex)" -out ct.bin
# flip a single bit in the ciphertext
python3 -c "b=open('ct.bin','rb').read(); b=bytearray(b); b[16]^=1; open('ct.bin','wb').write(b)"
# decrypt — corruption is silent unless the application checks plaintext shape
openssl enc -d -aes-256-cbc -K "$(cat key.hex)" -iv "$(cat iv.hex)" -in ct.bin
```

Result: the plaintext is corrupted but no error is raised. Now repeat with `-aes-256-gcm` (AEAD) and observe the decryption fail.

### Demonstrate non-constant-time equality leak

```
# DO NOT use this in production
import time
def slow_eq(a, b):
    if len(a) != len(b): return False
    for x, y in zip(a, b):
        if x != y: return False
    return True

import hmac
def safe_eq(a, b):
    return hmac.compare_digest(a, b)

# Compare timings of slow_eq with matching prefixes vs random tags
```

Result: `slow_eq` returns faster on early-mismatch inputs, leaking the position of the first wrong byte to an attacker who can time you.

### Demonstrate MAC ≠ signature for non-repudiation

```
Two services share a 32-byte HMAC key. Service A sends a message and an HMAC tag.
Service B can validate authorship — but B could also have produced the tag itself.
If B accuses A of sending a message and A denies it, the tag does not resolve the dispute.
With Ed25519: only A holds sk_A, so a valid signature pin authorship to A.
```

This is why JWT `HS256` is fine inside one trust boundary but inappropriate when the receiver should not be able to mint tokens.

## Practical examples

- A web app stores user passwords as `SHA-256(password)`. A leaked database is fully cracked on a single 4090 in days. Fix: switch to Argon2id with parameters from [[password-hashing]] and force re-hashing on next login.
- An IoT device uses AES-CBC without an HMAC. An attacker bit-flips firmware update ciphertext to introduce a one-byte parser bug and gain code execution. Fix: AEAD or encrypt-then-MAC.
- A SaaS uses a JWT with `alg=HS256` to authenticate cross-tenant API callbacks. Tenant B can mint tokens that look like Tenant A. Fix: per-tenant keys, or switch to RS256/EdDSA.
- A document signing service "signs" documents by HMAC-ing them with a shared key. Customers cannot prove which signer produced the tag. Fix: real signatures with per-signer keys.
- A microservice "verifies" tokens but the verify call returns `null` on bad signature instead of throwing — and the caller treats `null` as "valid". Fix: explicit verification result, fail-closed by default.

## Related notes

- [[symmetric-encryption-modes]]
- [[mac-and-hmac]]
- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[password-hashing]]
- [[aead-and-nonce-misuse]]
- [[jwt-cryptographic-correctness]]
- [[auth-flaws|Auth Flaws]]
- [[jwt-attacks|JWT Attacks]]

### Suggested future atomic notes

- encrypt-then-mac-vs-mac-then-encrypt
- constant-time-comparisons
- hybrid-encryption-patterns
- fingerprinting-vs-identification

## References

- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- **Standard / RFC:** NIST FIPS 180-4 Secure Hash Standard — https://csrc.nist.gov/publications/detail/fips/180/4/final
- **Foundational:** OWASP ASVS V6 Stored Cryptography — https://github.com/OWASP/ASVS
