---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Cryptography

## Purpose

This note is the cryptography-specific seed for the broader cybersecurity reference registry.

Use it to:
- standardize references for cryptography notes
- keep source quality consistent across primitives, transport, and applied notes
- prefer official standards (NIST, IETF/IRTF) and authoritative project documentation over secondary blogs
- help future cryptography notes pick references without inventing weak source sets

## Source of truth rule

For cryptography notes, this registry is the primary source of truth.

Use it together with:
- [[index|Cryptography Index]] for study order and branch structure
- [[reference-registry|Cybersecurity Reference Registry]] for broader fallback only when this note does not yet cover a cryptography topic

---

## Reference selection policy

### Source priority

1. NIST FIPS / SP 800-series and IETF / IRTF RFCs
2. authoritative project documentation (OpenSSL, libsodium, BoringSSL, age, GnuPG)
3. high-signal academic sources (Cryptography Engineering, A Graduate Course in Applied Cryptography)
4. testing and applied-security guides (OWASP Cryptographic Storage Cheat Sheet, OWASP ASVS V6, Mozilla Server Side TLS)
5. high-quality educational materials (Cryptopals, Real-World Cryptography by David Wong)

### Per-note target

- minimum 2 references
- ideal 3 references
- default maximum 5 references

### Labeling

Use:
- **Foundational**
- **Standard / RFC**
- **Testing / Lab**
- **Research / Deep Dive**
- **Official Tool Docs**

---

# Cryptography topic map

## hashing-vs-encryption-vs-signing

Preferred references:
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- **Standard / RFC:** NIST FIPS 180-4 Secure Hash Standard — https://csrc.nist.gov/publications/detail/fips/180/4/final
- **Foundational:** OWASP ASVS V6 Stored Cryptography — https://github.com/OWASP/ASVS

## symmetric-encryption-modes

Preferred references:
- **Standard / RFC:** NIST SP 800-38A Recommendation for Block Cipher Modes — https://csrc.nist.gov/publications/detail/sp/800-38a/final
- **Standard / RFC:** NIST SP 800-38D GCM and GMAC — https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **Standard / RFC:** RFC 8439 ChaCha20 and Poly1305 — https://www.rfc-editor.org/rfc/rfc8439

## mac-and-hmac

Preferred references:
- **Standard / RFC:** NIST FIPS 198-1 The Keyed-Hash Message Authentication Code (HMAC) — https://csrc.nist.gov/publications/detail/fips/198/1/final
- **Standard / RFC:** RFC 2104 HMAC: Keyed-Hashing for Message Authentication — https://www.rfc-editor.org/rfc/rfc2104
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

## asymmetric-encryption-and-key-exchange

Preferred references:
- **Standard / RFC:** NIST SP 800-56A Recommendation for Pair-Wise Key-Establishment — https://csrc.nist.gov/publications/detail/sp/800-56a/rev-3/final
- **Standard / RFC:** RFC 7748 Elliptic Curves for Security (X25519, X448) — https://www.rfc-editor.org/rfc/rfc7748
- **Foundational:** Real-World Cryptography (David Wong) — Chapter 6

## digital-signatures

Preferred references:
- **Standard / RFC:** NIST FIPS 186-5 Digital Signature Standard — https://csrc.nist.gov/publications/detail/fips/186/5/final
- **Standard / RFC:** RFC 8032 Edwards-Curve Digital Signature Algorithm (Ed25519) — https://www.rfc-editor.org/rfc/rfc8032
- **Standard / RFC:** RFC 8017 PKCS #1 v2.2 RSA Cryptography Specifications — https://www.rfc-editor.org/rfc/rfc8017

## password-hashing

Preferred references:
- **Foundational:** OWASP Password Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **Standard / RFC:** RFC 9106 Argon2 Memory-Hard Function — https://www.rfc-editor.org/rfc/rfc9106
- **Standard / RFC:** NIST SP 800-63B Digital Identity Guidelines (Memorized Secret Verifiers) — https://pages.nist.gov/800-63-3/sp800-63b.html

## kdf-and-key-stretching

Preferred references:
- **Standard / RFC:** NIST SP 800-108r1 Key Derivation Using Pseudorandom Functions — https://csrc.nist.gov/publications/detail/sp/800-108/rev-1/final
- **Standard / RFC:** RFC 5869 HKDF: HMAC-based Extract-and-Expand KDF — https://www.rfc-editor.org/rfc/rfc5869
- **Standard / RFC:** RFC 8018 PKCS #5 PBKDF2 — https://www.rfc-editor.org/rfc/rfc8018

## random-and-csprng-pitfalls

Preferred references:
- **Standard / RFC:** NIST SP 800-90A Rev 1 Recommendation for Random Number Generation — https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final
- **Standard / RFC:** NIST SP 800-90B Entropy Sources — https://csrc.nist.gov/publications/detail/sp/800-90b/final
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet (RNG section) — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

## tls-handshake-and-pki

Preferred references:
- **Standard / RFC:** RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3 — https://www.rfc-editor.org/rfc/rfc8446
- **Foundational:** Mozilla Server Side TLS Recommendations — https://wiki.mozilla.org/Security/Server_Side_TLS
- **Testing / Lab:** SSL Labs SSL Server Test — https://www.ssllabs.com/ssltest/

## certificate-validation-and-pinning

Preferred references:
- **Standard / RFC:** RFC 5280 X.509 Certificate Path Validation — https://www.rfc-editor.org/rfc/rfc5280
- **Foundational:** OWASP Pinning Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- **Standard / RFC:** RFC 6962 Certificate Transparency — https://www.rfc-editor.org/rfc/rfc6962

## jwt-cryptographic-correctness

Preferred references:
- **Foundational:** OWASP JSON Web Token for Java Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **Standard / RFC:** RFC 7519 JSON Web Token (JWT) — https://www.rfc-editor.org/rfc/rfc7519
- **Testing / Lab:** PortSwigger JWT attacks — https://portswigger.net/web-security/jwt
- **Research / Deep Dive:** Auth0 JWT handbook — https://auth0.com/resources/ebooks/jwt-handbook

## aead-and-nonce-misuse

Preferred references:
- **Standard / RFC:** NIST SP 800-38D GCM and GMAC — https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **Standard / RFC:** RFC 8439 ChaCha20 and Poly1305 — https://www.rfc-editor.org/rfc/rfc8439
- **Research / Deep Dive:** Joux "Authentication Failures in NIST version of GCM" — https://csrc.nist.rip/groups/ST/toolkit/BCM/documents/comments/800-38_Series-Drafts/GCM/Joux_comments.pdf

## roll-your-own-crypto-failures

Preferred references:
- **Foundational:** Cryptopals Crypto Challenges — https://cryptopals.com/
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- **Research / Deep Dive:** Real-World Cryptography (David Wong) — Chapter 1 (overview) and Chapter 16 (when crypto fails)

## post-quantum-awareness

Preferred references:
- **Foundational:** NIST PQC Project — https://csrc.nist.gov/projects/post-quantum-cryptography
- **Standard / RFC:** NIST FIPS 203 ML-KEM (Kyber) — https://csrc.nist.gov/pubs/fips/203/final
- **Standard / RFC:** NIST FIPS 204 ML-DSA (Dilithium) — https://csrc.nist.gov/pubs/fips/204/final
- **Standard / RFC:** NIST FIPS 205 SLH-DSA (SPHINCS+) — https://csrc.nist.gov/pubs/fips/205/final
- **Foundational:** NIST selected HQC as a backup KEM for future standardization — https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption
