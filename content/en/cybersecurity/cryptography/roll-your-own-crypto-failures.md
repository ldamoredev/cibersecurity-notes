---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Roll Your Own Crypto Failures

## Definition

Roll-your-own crypto is the practice of designing custom cryptographic algorithms, protocols, formats, key schedules, padding, random generation, or verification logic instead of using vetted primitives and protocols. The failure is usually not bad math alone; it is unsafe composition, missing authentication, weak randomness, broken parsing, or unreviewed edge cases.

## Why it matters

Many teams know not to invent AES. Fewer realize they are still rolling their own crypto when they glue AES-CBC, JSON, timestamps, compression, Base64, and a homegrown signature together. Cryptography fails at the boundaries: what bytes are signed, how nonces are generated, whether errors leak information, how keys rotate, and whether the verifier checks the same thing the signer meant.

## How it works

Roll-your-own failures usually follow **4 steps**:

1.
**A real requirement appears**
   "Protect this cookie", "encrypt this backup", "sign this webhook", "hide this id", "make this reset token."

2.
**A familiar primitive is selected**
   SHA-256, AES, RSA, UUIDs, Base64, or JWT-like JSON.

3.
**Composition details are invented**
   Custom delimiters, handmade padding, `hash(secret + message)`, static IVs, compressed-then-encrypted data, or ad hoc key rotation.

4.
**Attackers target the composition**
   They do not break AES; they exploit nonce reuse, missing MAC, parser mismatch, timing, replay, or unsigned metadata.

```
bad_token = base64(json) + "." + sha256(secret + json)
```

The bug is not "SHA-256 is weak." The bug is inventing a token format and MAC construction when standard signed-token or HMAC patterns already exist.

## Techniques / patterns

- Search for custom crypto wrappers, helpers, or "simple encrypt/decrypt/sign" utilities.
- Look for low-level primitives used directly: AES-CBC, AES-CTR, RSA encrypt/decrypt, raw ECDSA, raw hashes.
- Check whether the design authenticates ciphertext and metadata.
- Check whether the protocol has versioning, key ids, rotation, and replay controls.
- Check parsing boundaries: delimiters, JSON canonicalization, URL encoding, Unicode, compression.
- Check whether errors differ for padding, MAC, parse, and authorization failures.

## Variants and bypasses

Roll-your-own crypto breaks in **7 predictable families**.

### 1. Custom MAC

`sha256(secret + message)`, `md5(message + secret)`, or encrypted hashes replace HMAC. These shapes are easy to get wrong and can be length-extension-prone.

### 2. Encryption without authentication

The app encrypts with CBC, CTR, or custom stream XOR and assumes confidentiality implies integrity. Attackers flip bits, build padding oracles, or replay ciphertext.

### 3. Static IV or nonce

A fixed IV in CBC leaks equal-prefix structure; a repeated nonce in GCM/CTR/ChaCha20 can break confidentiality and authenticity.

### 4. RSA misuse

Raw RSA or legacy padding is used directly. Modern systems use OAEP for encryption, PSS for signatures, or avoid RSA encryption in favor of hybrid/KEM patterns.

### 5. Parser and canonicalization mismatch

The signed bytes are not the parsed bytes. Attackers exploit duplicate fields, alternate encodings, or delimiter injection.

### 6. Compression side channels

Compress-then-encrypt with attacker-controlled reflection can leak secrets through compressed length differences.

### 7. Error oracle

Different error messages or timing reveal whether padding, MAC, key id, or parse checks passed.

## Impact

Ordered roughly by severity:

- **Token forgery.** Custom signed cookies or reset links become forgeable.
- **Plaintext recovery.** Padding oracles, nonce reuse, or compression side channels reveal secrets.
- **Authentication bypass.** Parser mismatch lets signed authorization data be interpreted differently.
- **Key compromise.** ECDSA nonce mistakes or RSA misuse can reveal private keys.
- **Long-lived technical debt.** Custom formats become hard to rotate because every client implements quirks.

## Detection and defense

Ordered by effectiveness:

1.
**Use high-level protocols and libraries.**
   Prefer TLS, libsodium, age, JOSE libraries with strict algorithms, platform KMS envelope encryption, and framework session signing over low-level composition.

2.
**Choose boring constructions.**
   AEAD for encryption, HMAC for keyed integrity, Ed25519/RSA-PSS/ECDSA through vetted libraries for signatures, Argon2id/scrypt/bcrypt/PBKDF2 for passwords.

3.
**Make formats explicit and versioned.**
   Include algorithm, key id, version, nonce, AAD, and tag fields where needed. Avoid ambiguous delimiters and unsigned metadata.

4.
**Fail closed with uniform errors.**
   Verify before decrypting where the mode requires it, do not process unauthenticated plaintext, and avoid revealing oracle details.

5.
**Threat-model the composition, not just the primitive.**
   Ask what is secret, what is authenticated, what is fresh, what is replayable, what is parsed, and what rotates.

### What does not work as a primary defense

- **"We use AES."** AES says almost nothing about mode, nonce, authentication, or key management.
- **"The algorithm is secret."** Obscurity is not a cryptographic security property.
- **"We Base64 it."** Encoding is not encryption or authentication.
- **"Nobody will know the format."** Attackers infer formats from clients, errors, traffic, and code leaks.
- **"It passed unit tests."** Unit tests prove round trips, not adversarial security.

## Practical labs

### Spot custom crypto helpers

```
rg -n "encrypt|decrypt|sign|verify|hash|cipher|iv|nonce|secret" src lib app
```

Review helpers that wrap low-level primitives or invent token formats.

### Break a plain-hash "signature" mentally

```
token = base64(payload) + "." + sha256(payload)

Attacker changes:
{"role":"user"} -> {"role":"admin"}

Then recomputes sha256(payload) because no secret exists.
```

Plain hashes do not authenticate adversarial data.

### Build a safer envelope checklist

```
{
  "v": 2,
  "alg": "XChaCha20-Poly1305",
  "kid": "2026-05-main",
  "nonce": "...",
  "aad": "purpose=session-cookie",
  "ciphertext": "...",
  "tag": "..."
}
```

The envelope documents how the verifier chooses keys and authenticates context.

### Practice with Cryptopals

```
Do Cryptopals Set 1 and Set 2 as an attack exercise, not as production guidance.
Goal: learn why ECB, padding, oracles, and hand-rolled MACs fail.
```

Cryptopals is useful because it teaches failure modes by breaking toy systems.

## Practical examples

- A product uses AES-CBC with a static IV to encrypt cookies; attackers observe repeated prefixes and exploit padding behavior.
- A webhook signs `sha256(secret + body)` instead of HMAC, creating avoidable construction risk.
- A reset token encodes user id and expiry in Base64 with no MAC.
- A mobile app implements custom certificate pinning and accepts any cert on parse errors.
- A backup format compresses attacker-controlled filenames and secrets together before encryption, leaking length information.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[symmetric-encryption-modes]]
- [[aead-and-nonce-misuse]]
- [[random-and-csprng-pitfalls]]
- [[certificate-validation-and-pinning]]

### Suggested future atomic notes

- padding-oracle-attacks
- compression-side-channel-attacks
- cryptographic-envelope-design
- crypto-agility

## References

- **Foundational:** Cryptopals Crypto Challenges — https://cryptopals.com/
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- **Research / Deep Dive:** Real-World Cryptography, David Wong — Chapter 1 and Chapter 16
