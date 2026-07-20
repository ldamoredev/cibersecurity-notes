---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Symmetric Encryption Modes

## Definition

A symmetric encryption mode is the wrapper around a block cipher (or stream cipher) that decides how plaintext is split, padded, randomized, and authenticated. The block cipher is one piece (e.g., AES); the mode (ECB, CBC, CTR, GCM, GCM-SIV, ChaCha20-Poly1305) is what makes the construction secure or broken in practice.

## Why it matters

"AES is secure" is a true but useless statement. AES-ECB leaks plaintext patterns; AES-CBC without a MAC is malleable; AES-CTR with a reused nonce loses confidentiality completely; AES-GCM with a reused nonce loses authentication. Almost every real-world "we used AES and it broke" incident is a mode bug, not a primitive bug. Picking the right mode is the line between secure-by-default and catastrophic.

## How it works

A block cipher only encrypts a single fixed-size block (AES = 128 bits). To encrypt anything bigger, you need a mode. Modes split into 4 useful families:

1. **ECB (Electronic Codebook)** — encrypt each block independently. Same plaintext block → same ciphertext block. Pattern-leaking. Never use for real data.
2. **CBC (Cipher Block Chaining)** — XOR each plaintext block with the previous ciphertext block, then encrypt. Needs a random IV per message. Confidentiality only — does *not* detect tampering.
3. **CTR (Counter)** — turn the block cipher into a stream cipher by encrypting a counter and XOR-ing the result with plaintext. Confidentiality only. Catastrophic if the (key, nonce) pair ever repeats.
4. **AEAD (Authenticated Encryption with Associated Data)** — bundles confidentiality + integrity + optional unencrypted "associated data" that is also authenticated. Modern AEADs: AES-GCM, AES-GCM-SIV, ChaCha20-Poly1305, AES-OCB. AEAD is the default for new designs.

```
ECB:    block_i -> Enc(k, block_i)                        # never use
CBC:    c_i    = Enc(k, p_i XOR c_{i-1}), c_0 = IV         # needs MAC on top
CTR:    c_i    = p_i XOR Enc(k, nonce || counter_i)        # nonce reuse = catastrophic
AEAD:   (c, tag) = Enc(k, nonce, p, aad)                  # default
```

The bug is not "we used AES"; it is "we used a mode whose failure mode does not match our threat model." ECB ignores patterns. CBC ignores tampering. CTR collapses on nonce reuse. AEAD without nonce discipline still fails.

## Techniques / patterns

The reasoning model when reviewing a mode choice:

- **What primitive is in use?** (AES, ChaCha20, 3DES, RC4) — 3DES and RC4 are deprecated; AES-128/256 and ChaCha20 are current.
- **What mode wraps it?** (ECB, CBC, CTR, GCM, GCM-SIV, OCB, CCM)
- **Where does the IV/nonce come from?** Random? Counter? Predictable? Fixed?
- **Is there a MAC?** If the mode is not AEAD, where does integrity come from?
- **Is associated data authenticated?** Headers, content-type, key-id, version field — all of these can be tampered with if they are not part of the AAD.
- **Probe pattern in code review:** grep for `ECB`, `CBC` without HMAC nearby, manual `XOR` loops, hand-rolled PKCS#7 padding, `IV = key`, and anywhere a nonce is fixed or derived only from the key.

## Variants and bypasses

The 5 modes you actually need to recognize, with their canonical failure modes:

### ECB — pattern leak

Identical 16-byte plaintext blocks produce identical ciphertext blocks. The "ECB penguin" image is the textbook demonstration. ECB is also vulnerable to block reordering, copy-paste, and chosen-prefix attacks. There is no scenario in modern application code where ECB is the right answer.

### CBC — malleability and padding oracles

CBC is confidentiality-only. Bit-flipping the IV deterministically flips bits in the first plaintext block. PKCS#7 padding combined with leaky error responses creates a padding oracle (POODLE for SSL 3.0; Vaudenay 2002 for general CBC). Fix: switch to AEAD, or use encrypt-then-MAC where the MAC covers IV + ciphertext.

### CTR / streaming — nonce-reuse catastrophe

CTR turns AES into a stream cipher: `c = p XOR keystream(k, nonce)`. If the same `(k, nonce)` is ever used twice, XOR-ing the two ciphertexts yields `p1 XOR p2`, which leaks plaintext relationships. Counter overflow, deterministic nonces from request fields, or reusing a nonce across restarts all trigger this. CTR alone has no integrity, so it must be paired with a MAC.

### AEAD with random nonce — the modern default

AES-GCM and ChaCha20-Poly1305 take `(k, nonce, plaintext, aad)` and produce `(ciphertext, tag)`. The tag binds plaintext, ciphertext, and AAD. Any tampering changes the tag and decryption fails. Nonce must not repeat for a given key — for AES-GCM the safe construction is either a 96-bit random nonce (with a strict key-rotation budget) or a deterministic counter inside an envelope.

### AEAD with misuse-resistance — GCM-SIV / SIV / OCB

AES-GCM-SIV (RFC 8452) and AES-SIV (RFC 5297) are nonce-misuse-resistant: a repeated nonce only leaks message equality, not message contents. Useful for stateless services where nonce uniqueness is hard to guarantee. Slower than plain GCM but the safety budget is much larger.

## Impact

- **ECB on confidential data:** plaintext shape leaks, sometimes plaintext itself (if blocks are predictable). Trivially fingerprintable across messages.
- **CBC without MAC:** padding oracle → full plaintext recovery. Bit-flipping → targeted plaintext modification.
- **CTR / GCM with nonce reuse:** confidentiality and authentication both lost; entire keystream is recoverable for the reused nonce.
- **AEAD without AAD coverage of headers:** attacker swaps headers (e.g., key-id, content-type, recipient) without invalidating the tag.
- **3DES / RC4 / DES:** primitive-level breaks; key sizes too small or biases too exploitable to be safe at any mode.

Severity escalates with adversary access: a passive observer of CBC ciphertext is dangerous; an oracle that returns "padding error" vs "MAC error" is catastrophic.

## Detection and defense

Ordered by what works:

1.
**Default to AES-256-GCM or ChaCha20-Poly1305 with random 96-bit nonces (or counter envelopes).**
   Both are AEAD, both are well-supported, both are misuse-resistant when used with proper nonce discipline. ChaCha20-Poly1305 is preferred on platforms without AES-NI hardware acceleration.

2.
**Use AES-GCM-SIV or AES-SIV when nonce uniqueness is not guaranteed.**
   Stateless workers, cross-restart re-encryption, and "encrypt this small blob with the same key forever" patterns benefit from misuse resistance.

3.
**Authenticate associated data, not just plaintext.**
   Key-id, version, content-type, recipient, and routing fields belong in AAD so tampering is detected. The AAD is not encrypted; it is bound to the ciphertext.

4.
**Manage keys, do not memorize them in code.**
   KMS, HSM, envelope encryption (data-encryption-key wrapped by key-encryption-key). Rotate keys with versioning so you can decrypt old data while new data uses a new key.

5.
**Use libraries, not block-cipher primitives directly.**
   `libsodium`, `cryptography.hazmat` AEAD, Tink, AWS Encryption SDK, age. Direct calls to a low-level block-cipher API are a lint flag.

### What does not work as a primary defense

- **"We use AES, so we are secure."** AES-ECB, AES-CBC without MAC, and AES-CTR with reused nonce are all broken in practice.
- **"We use a long IV, so the IV cannot collide."** A long *random* IV from a CSPRNG plus a sufficient rotation policy is fine; a long *predictable* IV (timestamp, counter from zero on every restart) is not.
- **"We hash the ciphertext for integrity."** A plain hash is not keyed and not bound to the key — an attacker can re-hash. Use a MAC over `IV || ciphertext`, or use AEAD.
- **"The IV is secret."** IVs are not secret; they ride with the ciphertext. Confidentiality must not depend on IV secrecy.
- **"We encrypt-then-base64 so it is safe."** Encoding is not encryption. Adding a layer of base64 changes nothing about confidentiality or integrity.

## Practical labs

### Show the ECB penguin (pattern leak)

```
# requires imagemagick: brew install imagemagick
curl -L -o tux.png https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/512px-Tux.svg.png
convert tux.png -depth 8 tux.bmp
# strip header (first 54 bytes) and ECB-encrypt the body
KEY=$(openssl rand -hex 32)
dd if=tux.bmp of=body.bin bs=54 skip=1
openssl enc -aes-256-ecb -K "$KEY" -nopad -in body.bin -out body.enc
dd if=tux.bmp of=header.bin bs=54 count=1
cat header.bin body.enc > tux-ecb.bmp
open tux-ecb.bmp
```

Result: the silhouette of Tux remains visible because identical plaintext blocks produced identical ciphertext blocks. ECB does not hide structure.

### Reproduce CBC bit-flipping

```
from Crypto.Cipher import AES
import os
key = os.urandom(32); iv = os.urandom(16)
pt  = b"transfer 0001 to alice____________"  # padded to 32 bytes
ct  = AES.new(key, AES.MODE_CBC, iv).encrypt(pt)
# attacker has only iv and ct. Flip a bit in iv to change pt block 1.
iv2 = bytearray(iv); iv2[10] ^= 0x01
pt2 = AES.new(key, AES.MODE_CBC, bytes(iv2)).decrypt(ct)
print(pt2)
```

Result: a single bit flipped in the IV deterministically modifies the first plaintext block. CBC does not detect tampering on its own.

### Reproduce GCM nonce reuse

```
from Crypto.Cipher import AES
key = b"\x00"*32; nonce = b"\x00"*12  # intentionally fixed
m1 = b"transfer 100 to alice"
m2 = b"transfer 999 to mallory"
c1, _ = AES.new(key, AES.MODE_GCM, nonce=nonce).encrypt_and_digest(m1)
c2, _ = AES.new(key, AES.MODE_GCM, nonce=nonce).encrypt_and_digest(m2)
xored = bytes(a^b for a,b in zip(c1, c2))
# xored == m1 XOR m2 — known plaintext reveals the other message
```

Result: two ciphertexts under the same `(key, nonce)` XOR to the XOR of the plaintexts. Confidentiality is gone.

### Detect ECB by repeated-block frequency

```
def looks_like_ecb(ct, block=16):
    blocks = [ct[i:i+block] for i in range(0, len(ct), block)]
    return len(blocks) - len(set(blocks)) > 0
```

A non-zero result is a strong signal of ECB. Use this as a code-review or wire-capture heuristic.

### Round-trip a ChaCha20-Poly1305 AEAD with AAD

```
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import os
key = ChaCha20Poly1305.generate_key()
aead = ChaCha20Poly1305(key)
nonce = os.urandom(12)
aad = b"key-id=2026-05-01;version=1"
ct = aead.encrypt(nonce, b"sensitive payload", aad)
# tampering with aad will fail decryption
print(aead.decrypt(nonce, ct, aad))
```

Result: tampering with `aad` raises `InvalidTag`. AAD is authenticated even though it is not encrypted.

## Practical examples

- A backup service stores customer files with AES-CBC and HMAC-SHA-256 over the ciphertext. Migration to AES-GCM removes one layer of complexity (encrypt-then-MAC ordering) and removes a class of padding-oracle bugs.
- A microservice memoizes a single AES-GCM key with a deterministic 96-bit nonce derived from `(timestamp, counter)`. After a restart the counter resets and nonces collide. Switch to GCM-SIV or persist nonce state.
- A cookie value is "encrypted" with AES-CBC. The application uses the decrypted role field for authorization. Bit-flipping the cookie changes the role. Fix: AEAD over the entire cookie payload, or sign the cookie.
- A messaging app uses AES-CTR with a random 64-bit nonce and no MAC. Birthday risk on nonces is real for high-volume keys, and there is no integrity. Fix: ChaCha20-Poly1305.
- A legacy device firmware update uses AES-ECB on a 1 KB binary. Adjacent blocks of zero in the binary produce identical ciphertext that fingerprints the binary version. ECB never the answer.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[aead-and-nonce-misuse]]
- [[random-and-csprng-pitfalls]]
- [[kdf-and-key-stretching]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- encrypt-then-mac-vs-mac-then-encrypt
- padding-oracle-attacks
- envelope-encryption
- aes-gcm-siv-and-misuse-resistance
- fpe-and-format-preserving-encryption

## References

- **Standard / RFC:** NIST SP 800-38A Recommendation for Block Cipher Modes — https://csrc.nist.gov/publications/detail/sp/800-38a/final
- **Standard / RFC:** NIST SP 800-38D GCM and GMAC — https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **Standard / RFC:** RFC 8439 ChaCha20 and Poly1305 — https://www.rfc-editor.org/rfc/rfc8439
