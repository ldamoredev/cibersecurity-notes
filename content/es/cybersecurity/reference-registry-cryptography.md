# Reference Registry — Cryptography

Registro centralizado de referencias para la rama de criptografía. Cada entrada apunta a las fuentes más útiles por tema, categorizadas por tipo.

---

## Hashing vs Encryption vs Signing

- **Fundamental:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- **Fundamental:** "Cryptographic Right Answers" (latacora) — https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html
- **Estándar / RFC:** NIST SP 800-175B Rev. 1 — https://csrc.nist.gov/publications/detail/sp/800-175b/rev-1/final

---

## Symmetric Encryption Modes

- **Estándar / RFC:** NIST SP 800-38A: Block Cipher Modes — https://csrc.nist.gov/publications/detail/sp/800-38a/final
- **Estándar / RFC:** NIST SP 800-38D: AES-GCM — https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **Testing / Lab:** PortSwigger Web Security Academy — Cryptography Labs — https://portswigger.net/web-security/all-labs#cryptography
- **Investigación / Deep Dive:** "Failures of Secret-Key Cryptography" (Dan Boneh) — https://eprint.iacr.org/2012/049.pdf

---

## MAC and HMAC

- **Estándar / RFC:** RFC 2104: HMAC — https://www.rfc-editor.org/rfc/rfc2104
- **Estándar / RFC:** NIST SP 800-107: Recommendations for Applications Using Approved Hash Algorithms — https://csrc.nist.gov/publications/detail/sp/800-107/rev-1/final
- **Fundamental:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

---

## Asymmetric Encryption and Key Exchange

- **Estándar / RFC:** RFC 7748: Elliptic Curves for Diffie-Hellman Key Agreement (X25519, X448) — https://www.rfc-editor.org/rfc/rfc7748
- **Estándar / RFC:** NIST SP 800-56A Rev. 3: Key-Establishment Schemes — https://csrc.nist.gov/publications/detail/sp/800-56a/rev-3/final
- **Docs Oficiales:** libsodium key exchange — https://doc.libsodium.org/key_exchange
- **Investigación / Deep Dive:** A Graduate Course in Applied Cryptography (Boneh & Shoup) — https://toc.cryptobook.us/

---

## Digital Signatures

- **Estándar / RFC:** RFC 8032: Ed25519 — https://www.rfc-editor.org/rfc/rfc8032
- **Estándar / RFC:** FIPS 186-5: Digital Signature Standard (DSS) — https://csrc.nist.gov/publications/detail/fips/186/5/final
- **Investigación / Deep Dive:** "ECDSA Security in Bitcoin and Ethereum" — https://eprint.iacr.org/2019/023.pdf

---

## Password Hashing

- **Fundamental:** OWASP Password Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **Estándar / RFC:** RFC 9106: Argon2 Memory-Hard Function — https://www.rfc-editor.org/rfc/rfc9106
- **Estándar / RFC:** NIST SP 800-63B: Digital Identity Guidelines (Memorized Secret Verifiers) — https://pages.nist.gov/800-63-3/sp800-63b.html
- **Docs Oficiales:** argon2-cffi — https://argon2-cffi.readthedocs.io/

---

## KDF and Key Stretching

- **Estándar / RFC:** NIST SP 800-108r1: Key Derivation Using Pseudorandom Functions — https://csrc.nist.gov/publications/detail/sp/800-108/rev-1/final
- **Estándar / RFC:** RFC 5869: HKDF — https://www.rfc-editor.org/rfc/rfc5869
- **Estándar / RFC:** RFC 8018: PKCS #5 PBKDF2 — https://www.rfc-editor.org/rfc/rfc8018

---

## Random and CSPRNG Pitfalls

- **Estándar / RFC:** NIST SP 800-90A Rev. 1: Random Bit Generation — https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final
- **Estándar / RFC:** NIST SP 800-90B: Entropy Sources — https://csrc.nist.gov/publications/detail/sp/800-90b/final
- **Fundamental:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html

---

## TLS Handshake and PKI

- **Estándar / RFC:** RFC 8446: TLS 1.3 — https://www.rfc-editor.org/rfc/rfc8446
- **Fundamental:** Mozilla Server Side TLS Recommendations — https://wiki.mozilla.org/Security/Server_Side_TLS
- **Testing / Lab:** SSL Labs SSL Server Test — https://www.ssllabs.com/ssltest/
- **Investigación / Deep Dive:** "The Transport Layer Security (TLS) Protocol Version 1.3" Analysis — https://tls13.ulfheim.net/

---

## Certificate Validation and Pinning

- **Estándar / RFC:** RFC 5280: X.509 Certificate and CRL Profile — https://www.rfc-editor.org/rfc/rfc5280
- **Estándar / RFC:** RFC 6962: Certificate Transparency — https://www.rfc-editor.org/rfc/rfc6962
- **Fundamental:** OWASP Pinning Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- **Docs Oficiales:** Cert Spotter (CT monitoring) — https://sslmate.com/certspotter/

---

## JWT Cryptographic Correctness

- **Estándar / RFC:** RFC 7519: JSON Web Token (JWT) — https://www.rfc-editor.org/rfc/rfc7519
- **Estándar / RFC:** RFC 7515: JSON Web Signature (JWS) — https://www.rfc-editor.org/rfc/rfc7515
- **Fundamental:** PortSwigger JWT Attacks — https://portswigger.net/web-security/jwt
- **Testing / Lab:** JWT.io Debugger — https://jwt.io/
- **Investigación / Deep Dive:** "Critical Vulnerabilities in JWT Libraries" — https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/

---

## AEAD and Nonce Misuse

- **Estándar / RFC:** RFC 5116: An Interface for Authenticated Encryption — https://www.rfc-editor.org/rfc/rfc5116
- **Estándar / RFC:** RFC 8452: AES-GCM-SIV — https://www.rfc-editor.org/rfc/rfc8452
- **Investigación / Deep Dive:** "Nonce-Disrespecting Adversaries: Practical Forgery Attacks on GCM in TLS" — https://eprint.iacr.org/2016/475.pdf

---

## Roll-Your-Own Crypto Failures

- **Fundamental:** "Cryptographic Right Answers" — https://latacora.micro.blog/2018/04/03/cryptographic-right-answers.html
- **Docs Oficiales:** libsodium — https://doc.libsodium.org/
- **Docs Oficiales:** Google Tink — https://developers.google.com/tink
- **Investigación / Deep Dive:** A Graduate Course in Applied Cryptography — https://toc.cryptobook.us/

---

## Post-Quantum Awareness

- **Estándar / RFC:** NIST FIPS 203: ML-KEM — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
- **Estándar / RFC:** NIST FIPS 204: ML-DSA — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.204.pdf
- **Estándar / RFC:** NIST FIPS 205: SLH-DSA — https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.205.pdf
- **Fundamental:** NIST PQC Project Overview — https://csrc.nist.gov/projects/post-quantum-cryptography
- **Investigación / Deep Dive:** Global Risk Institute — Quantum Threat Timeline Report — https://globalriskinstitute.org/publications/quantum-threat-timeline-report-2023/
