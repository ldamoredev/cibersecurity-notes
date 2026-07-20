---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Asymmetric Encryption and Key Exchange

## Definition

Asymmetric encryption and key exchange use different key roles so two parties can establish secrecy without first sharing a symmetric key. In practice, public-key cryptography is rarely used to encrypt large messages directly; it is used to agree on or wrap symmetric keys, then symmetric AEAD protects the actual data.

## Why it matters

TLS, age, Signal-style messaging, PGP, SSH, passkeys, package signing, and cloud KMS all depend on public/private key thinking. The common mental trap is "public-key crypto encrypts data." Sometimes, but not usually. Most real systems use public-key operations to solve the distribution problem: how do two parties that do not already share a secret end up with a shared secret that attackers cannot compute?

## How it works

The applied pattern has **4 moving parts**:

1.
**Long-term identity keys**
   A party may have a stable private key and public key. The public key can be shared; the private key must not leave its boundary.

2.
**Ephemeral key agreement**
   Each side creates a fresh temporary key pair and uses Diffie-Hellman or ECDH to derive a shared secret. X25519 is the modern common case.

3.
**Key derivation**
   The shared secret is not used directly as an encryption key. A KDF such as HKDF turns it into context-bound keys.

4.
**Symmetric protection**
   AEAD such as AES-GCM or ChaCha20-Poly1305 encrypts and authenticates the payload.

```
Alice ephemeral private a, public A = aG
Bob ephemeral private b, public B = bG

Alice computes shared = aB
Bob computes shared = bA

Both derive keys with HKDF(shared, transcript_context)
Then use AEAD for application data
```

The bug is not "we used RSA instead of elliptic curves." The bug is usually "we failed to authenticate the peer, reused the wrong key, skipped validation, or confused key agreement with trust."

## Techniques / patterns

- Identify whether the system needs encryption to a recipient, key agreement between peers, or signatures for authorship.
- Check whether the public key is authenticated. A public key from an attacker is just an attacker-controlled identity.
- Check for forward secrecy. Ephemeral DH means future compromise of a long-term key does not decrypt old sessions.
- Check key separation. Shared secrets should go through a KDF with context, transcript, algorithm, and purpose labels.
- Check curve and parameter choices. Prefer X25519/X448 for key agreement where supported; avoid custom DH groups.
- Check RSA usage. Legacy RSA encryption should use OAEP, not PKCS#1 v1.5. Modern TLS does not use RSA key transport.

## Variants and bypasses

Asymmetric secrecy failures fall into **5 families**.

### 1. Public-key encryption

The sender encrypts to the recipient's public key, and the recipient decrypts with the private key. Direct public-key encryption is size-limited, so production systems use hybrid encryption: generate a random data key, encrypt data with AEAD, then wrap the data key with the recipient public key or KMS key.

### 2. Key exchange without authentication

Plain Diffie-Hellman creates a shared secret but does not prove who is on the other side. A man-in-the-middle can establish separate secrets with each peer unless the exchange is authenticated with certificates, signatures, pre-shared keys, or a verified identity protocol.

### 3. Static keys without forward secrecy

If old session keys can be recomputed after a long-term key leaks, old traffic becomes readable. Ephemeral DH in TLS 1.3 prevents that class.

### 4. Invalid or weak parameters

Unsafe curves, small DH groups, missing public-key validation, or accepting low-order points can collapse key agreement. Modern libraries hide most of this; custom implementations often do not.

### 5. Key confusion

A key intended for signing is used for encryption, or an encryption key is accepted as an identity key. Different algorithms and key uses need explicit metadata and enforcement.

## Impact

Ordered roughly by severity:

- **Man-in-the-middle decryption.** Unauthenticated key exchange lets an attacker sit between peers and read or alter traffic.
- **Historical traffic exposure.** Lack of forward secrecy means one future key compromise decrypts old captures.
- **Recipient confusion.** Data encrypted to the wrong public key is secret from the intended recipient and available to the wrong one.
- **KMS misuse.** Wrapping data keys without context or policy separation can cross tenant or environment boundaries.
- **Downgrade risk.** Legacy key transport or weak groups can be forced if negotiation is not authenticated.

Severity escalates when the exchange protects authentication cookies, tokens, private messages, backups, or deployment secrets.

## Detection and defense

Ordered by effectiveness:

1.
**Use protocol-level implementations instead of raw primitives.**
   TLS 1.3, age, libsodium sealed boxes, Noise-based protocols, and KMS envelope encryption solve parameter and composition details that application code usually gets wrong.

2.
**Authenticate the key exchange.**
   Certificates, pinned/verified public keys, signatures over the transcript, or pre-shared keys prevent man-in-the-middle substitution.

3.
**Prefer ephemeral Diffie-Hellman for sessions.**
   Ephemeral X25519 or equivalent gives forward secrecy. Long-term keys should authenticate the exchange, not become the session key.

4.
**Use a KDF with explicit context.**
   Derive separate keys for encryption, MAC, export, and different protocol directions. Include protocol name and transcript when available.

5.
**Enforce key usage metadata.**
   A signing key should not decrypt; an encryption key should not sign; a test key should not be trusted in production.

### What does not work as a primary defense

- **"The public key is public, so any public key is fine."** Public does not mean trusted. You still need to know whose public key it is.
- **Static DH without authentication.** It can create a secret, but not necessarily with the intended peer.
- **RSA PKCS#1 v1.5 encryption for new designs.** OAEP is the safe RSA encryption padding, and many modern designs avoid RSA encryption entirely.
- **Encrypting large data directly with public-key operations.** Hybrid encryption is the normal design.
- **Trusting key ids without checking the key material and issuer.** A key id is routing metadata, not proof.

## Practical labs

### Derive a shared secret with X25519 using OpenSSL

```
openssl genpkey -algorithm X25519 -out alice.key
openssl genpkey -algorithm X25519 -out bob.key
openssl pkey -in alice.key -pubout -out alice.pub
openssl pkey -in bob.key -pubout -out bob.pub
openssl pkeyutl -derive -inkey alice.key -peerkey bob.pub -out alice.shared
openssl pkeyutl -derive -inkey bob.key -peerkey alice.pub -out bob.shared
cmp alice.shared bob.shared && echo "same shared secret"
```

Both sides derive the same secret without sending the private key.

### Show why a KDF comes after DH

```
openssl kdf -keylen 32 \
  -kdfopt digest:SHA256 \
  -kdfopt key:$(xxd -p -c 256 alice.shared) \
  -kdfopt info:"lab encryption key" \
  HKDF
```

The shared secret becomes a purpose-bound key; different `info` labels should produce different keys.

### Inspect TLS key exchange

```
openssl s_client -connect example.com:443 -tls1_3 -brief </dev/null
```

Look for TLS 1.3 and an ephemeral key exchange group; modern sessions should not use static RSA key transport.

### Model hybrid encryption

```
1. random data_key = 32 bytes
2. ciphertext = AEAD_Encrypt(data_key, plaintext, associated_data)
3. wrapped_key = PublicKey_Encrypt(recipient_public_key, data_key)
4. package = {wrapped_key, nonce, associated_data, ciphertext, tag}
```

This is the normal mental model for public-key encryption at production scale.

## Practical examples

- TLS 1.3 uses authenticated ephemeral key exchange to derive session keys, then AEAD protects application data.
- A backup system encrypts each file with a random data key and wraps that key using a cloud KMS public key or policy-bound key.
- A secure file sharing tool encrypts to each recipient's public key by wrapping a shared file key once per recipient.
- An SSH client trusts a server host key after first verification; a changed key is a potential MITM signal.
- A messaging protocol uses long-term identity keys to authenticate ephemeral session keys, preserving forward secrecy.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[digital-signatures]]
- [[kdf-and-key-stretching]]
- [[tls-handshake-and-pki]]
- [[certificate-validation-and-pinning]]
- [[end-to-end-encryption|End-to-End Encryption]]

### Suggested future atomic notes

- hybrid-encryption
- envelope-encryption
- forward-secrecy
- noise-protocol-framework

## References

- **Standard / RFC:** NIST SP 800-56A Rev. 3: Pair-Wise Key Establishment — https://csrc.nist.gov/publications/detail/sp/800-56a/rev-3/final
- **Standard / RFC:** RFC 7748: Elliptic Curves for Security — https://www.rfc-editor.org/rfc/rfc7748
- **Research / Deep Dive:** Real-World Cryptography, David Wong — Chapter 6
