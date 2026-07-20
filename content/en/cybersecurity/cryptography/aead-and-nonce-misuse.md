---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# AEAD and Nonce Misuse

## Definition

Authenticated Encryption with Associated Data (AEAD) encrypts plaintext and authenticates both ciphertext and optional associated data. Nonce misuse happens when the same nonce is reused with the same key, or when nonce generation rules do not match the AEAD mode's security assumptions.

## Why it matters

AEAD is the modern default for encryption because it binds confidentiality and integrity. But modes like AES-GCM and ChaCha20-Poly1305 have a sharp edge: nonce reuse under the same key can break confidentiality and may break authenticity. This is one of the places where "we used the right algorithm" is not enough; the operational state around nonce generation is part of the cryptosystem.

## How it works

AEAD protects **3 inputs**:

1.
**Plaintext**
   The secret data to encrypt.

2.
**Nonce**
   A value that must be unique for the key. It is usually public but must not repeat.

3.
**Associated data**
   Public metadata that is authenticated but not encrypted, such as key id, protocol version, tenant id, or record type.

```
ciphertext, tag = AEAD_Encrypt(key, nonce, plaintext, aad)
plaintext = AEAD_Decrypt(key, nonce, ciphertext, aad, tag)
```

If decryption succeeds, the receiver learns that ciphertext and AAD were not modified under that key/nonce pair.

The bug is not "the nonce is visible." Nonces are often public. The bug is reusing a nonce with the same key or failing to authenticate the metadata the application trusts.

## Techniques / patterns

- Identify AEAD modes: AES-GCM, ChaCha20-Poly1305, AES-GCM-SIV, XChaCha20-Poly1305.
- Check nonce source. Random 96-bit nonces, counters, persisted sequence numbers, or library-managed nonces all have different failure modes.
- Check restart behavior. Counters reset after deploys, crashes, VM snapshots, or process restarts unless persisted.
- Check key scope. Nonce uniqueness is per key; rotating keys resets the nonce space.
- Check AAD. Authenticate key id, tenant, protocol, content type, and version if the app relies on them.
- Check decryption error handling. Invalid tags should fail closed and avoid oracle-like detail.

## Variants and bypasses

AEAD misuse appears in **5 families**.

### 1. Random nonce collision

Random nonces can collide if too short or used at massive scale. AES-GCM's common 96-bit nonce is large enough for normal use, but high-volume systems still need design limits.

### 2. Counter reset

Counter nonces are safe only if they never repeat under a key. Restarts, snapshots, failover, and multi-writer deployments can reset or fork counter state.

### 3. Deterministic nonce from low-entropy fields

Using timestamp, user id, filename, or record id can collide across tenants or updates. Deterministic nonces need a uniqueness proof.

### 4. Missing AAD

The ciphertext is authenticated, but metadata that controls interpretation is not. Attackers may move ciphertext between tenants, versions, or record types.

### 5. Nonce misuse in GCM specifically

GCM nonce reuse can expose XOR relationships between plaintexts and can enable authentication forgeries. This is why GCM has a reputation for being fast and sharp.

## Impact

Ordered roughly by severity:

- **Plaintext recovery.** Reused stream-derived keystreams reveal relationships and known-plaintext can recover the other plaintext.
- **Authentication forgery.** In some modes, repeated nonces let attackers forge valid tags.
- **Cross-tenant data mixup.** Missing AAD allows ciphertext to be replayed in the wrong context.
- **Silent corruption rejection failure.** Applications that ignore tag failures process unauthenticated data.
- **Fleet-wide failures.** Distributed systems can repeat nonces after snapshot or counter split-brain.

## Detection and defense

Ordered by effectiveness:

1.
**Use high-level AEAD APIs.**
   Prefer libraries that generate nonces, package them with ciphertext, and fail closed on invalid tags.

2.
**Choose nonce strategy deliberately.**
   Random nonces are simple for moderate volume; counters need persistence and single-writer guarantees; misuse-resistant modes help when uniqueness is hard.

3.
**Authenticate context with AAD.**
   Include key id, tenant id, protocol version, record type, and direction when those fields affect security decisions.

4.
**Rotate keys before nonce space gets risky.**
   Set volume limits per key and make rotation observable.

5.
**Consider misuse-resistant AEAD for dangerous environments.**
   AES-GCM-SIV or XChaCha20-Poly1305 can reduce nonce-management risk, though they do not remove the need to understand mode semantics.

### What does not work as a primary defense

- **Keeping the nonce secret.** Secrecy is not the requirement; uniqueness is.
- **Hashing a repeated nonce.** Deterministically transforming repeats still repeats.
- **Ignoring authentication tag failures.** A failed tag means "do not trust this plaintext."
- **Using AES-GCM with a resettable counter.** Counter nonces need persistence and coordination.
- **Encrypting metadata separately instead of authenticating it.** If metadata controls interpretation, bind it as AAD or include it in plaintext.

## Practical labs

### Demonstrate nonce reuse intuition with XOR

```
from os import urandom

m1 = b"attack at dawn!!!!"
m2 = b"defend at dusk!!!!"
keystream = urandom(len(m1))
c1 = bytes(a ^ b for a, b in zip(m1, keystream))
c2 = bytes(a ^ b for a, b in zip(m2, keystream))
print(bytes(a ^ b for a, b in zip(c1, c2)))
print(bytes(a ^ b for a, b in zip(m1, m2)))
```

Reusing stream-like keystream reveals the XOR of plaintexts.

### Authenticate associated data

```
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=128)
aead = AESGCM(key)
nonce = os.urandom(12)
aad = b"tenant=blue;type=session"
ct = aead.encrypt(nonce, b"user=123", aad)
print(aead.decrypt(nonce, ct, aad))
print(aead.decrypt(nonce, ct, b"tenant=red;type=session"))
```

The second decrypt should fail because AAD is authenticated.

### Search for manual nonce construction

```
rg -n "nonce|iv|initialization vector|counter|GCM|ChaCha20Poly1305|AESGCM" .
```

Manual nonce construction in encryption code deserves careful review.

### Design a ciphertext envelope

```
{
  "alg": "AES-256-GCM",
  "kid": "kms-key-v3",
  "nonce": "base64url...",
  "aad": "tenant=blue;record=invoice;version=2",
  "ciphertext": "base64url...",
  "tag": "base64url..."
}
```

The envelope should make key id, nonce, and authenticated context explicit.

## Practical examples

- A service uses `Date.now()` as a GCM nonce and handles concurrent requests in the same millisecond.
- A counter nonce resets when a pod restarts, producing repeats under the same key.
- A database encrypts rows but does not authenticate table name or tenant id, enabling ciphertext swapping.
- A library returns plaintext before verifying the tag and callers process it incorrectly.
- A backup format uses one key for years with random nonces but no volume limits or collision monitoring.

## Related notes

- [[symmetric-encryption-modes]]
- [[random-and-csprng-pitfalls]]
- [[kdf-and-key-stretching]]
- [[mac-and-hmac]]
- [[roll-your-own-crypto-failures]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- aes-gcm-siv-and-misuse-resistance
- xchacha20-poly1305
- ciphertext-envelope-design
- nonce-generation-patterns

## References

- **Standard / RFC:** NIST SP 800-38D: GCM and GMAC — https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **Standard / RFC:** RFC 8439: ChaCha20 and Poly1305 — https://www.rfc-editor.org/rfc/rfc8439
- **Research / Deep Dive:** Antoine Joux, Authentication Failures in GCM — https://csrc.nist.rip/groups/ST/toolkit/BCM/documents/comments/800-38_Series-Drafts/GCM/Joux_comments.pdf
