---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cryptography Index

## Purpose

This index is the root entry point for the cryptography branch of the cybersecurity atlas.

Use it to:
- navigate the cryptography notes
- understand the order of study
- connect symbolic primitives (hash, MAC, signature, KDF, AEAD) to applied use cases (TLS, JWT, password storage, secrets, MFA)
- support web-security, api-security, networking, devsecops, and identity-security depth work that depends on crypto correctness

Use [[reference-registry-cryptography|Reference Registry — Cryptography]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[tls-https|TLS/HTTPS]] and [[http-overview|HTTP overview]] — crypto is most meaningful once TLS, sessions, and JWTs are concrete.

---

## Why this branch exists

Most security failures that look like "TLS misconfiguration", "broken JWT", "weak password storage", or "secret leak" are really cryptographic-correctness failures. The atlas was missing a canonical place to reason about:

- which primitive to use for which problem
- which parameters and modes are still acceptable
- where nonce reuse, IV reuse, MAC stripping, signature confusion, and key confusion break otherwise-correct designs
- why "rolling your own" usually fails even when the math looks right

This branch teaches the primitives and the common applied failures, then links downstream to the branches that put them under load (web auth, API auth, TLS, password storage, secrets management, MFA, deserialization).

---

## Recommended learning order

### Phase 1 — Primitives and intent

1. [[hashing-vs-encryption-vs-signing]]
2. [[symmetric-encryption-modes]]
3. [[mac-and-hmac]]
4. [[asymmetric-encryption-and-key-exchange]]
5. [[digital-signatures]]

### Phase 2 — Applied storage and identity

1. [[password-hashing]]
2. [[kdf-and-key-stretching]]
3. [[random-and-csprng-pitfalls]]

### Phase 3 — Transport and certificates

1. [[tls-handshake-and-pki]]
2. [[certificate-validation-and-pinning]]

### Phase 4 — Token-shape correctness

1. [[jwt-cryptographic-correctness]]

### Phase 5 — Failure-mode literacy

1. [[aead-and-nonce-misuse]]
2. [[roll-your-own-crypto-failures]]
3. [[post-quantum-awareness]]

---

## Core clusters

### Primitives

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[mac-and-hmac]]
- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[aead-and-nonce-misuse]]
- [[random-and-csprng-pitfalls]]

### Applied storage and identity

- [[password-hashing]]
- [[kdf-and-key-stretching]]

### Transport and certificates

- [[tls-handshake-and-pki]]
- [[certificate-validation-and-pinning]]

### Token-shape correctness

- [[jwt-cryptographic-correctness]]

### Failure-mode literacy

- [[roll-your-own-crypto-failures]]
- [[post-quantum-awareness]]

---

## Connections to other branches

- [[tls-https|TLS/HTTPS]] depends on [[tls-handshake-and-pki]] and [[certificate-validation-and-pinning]]
- [[auth-flaws|Auth Flaws]] depends on [[password-hashing]], [[mac-and-hmac]], and [[jwt-cryptographic-correctness]]
- [[session-management|Session Management]] depends on [[random-and-csprng-pitfalls]]
- [[jwt-attacks|JWT Attacks]] depends on [[jwt-cryptographic-correctness]] and [[digital-signatures]]
- [[secrets-management|Secrets Management]] depends on [[symmetric-encryption-modes]] and [[kdf-and-key-stretching]]
- [[mfa-phishing-resistance|MFA Phishing Resistance]] depends on [[digital-signatures]] (WebAuthn signing model)
- [[end-to-end-encryption|End-to-End Encryption]] and [[pgp-encryption-and-signatures|PGP]] depend on [[asymmetric-encryption-and-key-exchange]] and [[digital-signatures]]

---

## Calibration

- This branch is a primitives-and-correctness branch, not a math branch. The goal is to reason confidently about real-world failures, not to derive elliptic-curve arithmetic.
- The branch deliberately includes a "what does not work" section across notes (e.g., MD5 for password storage, ECB mode, encryption-without-MAC, JWT `alg=none`) — false-friend defenses are the common shape of crypto bugs.
- Quantum-resistance is treated as one note for awareness, not a current operational concern.
