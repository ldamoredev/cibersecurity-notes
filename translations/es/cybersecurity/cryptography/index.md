# Índice de Criptografía

## Propósito

Este índice es el punto de entrada raíz de la rama de criptografía del atlas de ciberseguridad.

Usalo para:
- navegar las notas de criptografía
- entender el orden de estudio
- conectar primitivos simbólicos (hash, MAC, firma, KDF, AEAD) con casos de uso aplicados (TLS, JWT, almacenamiento de contraseñas, secretos, MFA)
- profundizar en web-security, api-security, networking, devsecops e identity-security que dependen de la corrección criptográfica

Usá [[reference-registry-cryptography|Reference Registry — Cryptography]] como fuente de verdad para las referencias de esta rama.
Volvé a [[index|Índice de Ciberseguridad]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[tls-https|TLS/HTTPS]] y [[http-overview|HTTP overview]] — la cripto cobra sentido cuando TLS, sesiones y JWTs son concretos.

---

## Por qué existe esta rama

La mayoría de las fallas de seguridad que parecen "mala configuración de TLS", "JWT roto", "almacenamiento débil de contraseñas" o "filtración de secretos" son en realidad fallas de corrección criptográfica. El atlas no tenía un lugar canónico para razonar sobre:

- qué primitivo usar para qué problema
- qué parámetros y modos todavía son aceptables
- dónde el reuso de nonce/IV, el stripping de MAC, la confusión de firmas y la confusión de claves rompen diseños que de otro modo serían correctos
- por qué "inventar la propia cripto" casi siempre falla aunque la matemática parezca correcta

Esta rama enseña los primitivos y las fallas comunes en aplicaciones reales, luego enlaza hacia las ramas que los ponen bajo carga (auth web, auth API, TLS, almacenamiento de contraseñas, gestión de secretos, MFA, deserialización).

---

## Orden de estudio recomendado

### Fase 1 — Primitivos e intención

1. [[hashing-vs-encryption-vs-signing]]
2. [[symmetric-encryption-modes]]
3. [[mac-and-hmac]]
4. [[asymmetric-encryption-and-key-exchange]]
5. [[digital-signatures]]

### Fase 2 — Almacenamiento e identidad aplicados

1. [[password-hashing]]
2. [[kdf-and-key-stretching]]
3. [[random-and-csprng-pitfalls]]

### Fase 3 — Transporte y certificados

1. [[tls-handshake-and-pki]]
2. [[certificate-validation-and-pinning]]

### Fase 4 — Corrección de tokens

1. [[jwt-cryptographic-correctness]]

### Fase 5 — Literacy de modos de fallo

1. [[aead-and-nonce-misuse]]
2. [[roll-your-own-crypto-failures]]
3. [[post-quantum-awareness]]

---

## Clusters principales

### Primitivos

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[mac-and-hmac]]
- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[aead-and-nonce-misuse]]
- [[random-and-csprng-pitfalls]]

### Almacenamiento e identidad aplicados

- [[password-hashing]]
- [[kdf-and-key-stretching]]

### Transporte y certificados

- [[tls-handshake-and-pki]]
- [[certificate-validation-and-pinning]]

### Corrección de tokens

- [[jwt-cryptographic-correctness]]

### Literacy de modos de fallo

- [[roll-your-own-crypto-failures]]
- [[post-quantum-awareness]]

---

## Conexiones con otras ramas

- [[tls-https|TLS/HTTPS]] depende de [[tls-handshake-and-pki]] y [[certificate-validation-and-pinning]]
- [[auth-flaws|Auth Flaws]] depende de [[password-hashing]], [[mac-and-hmac]] y [[jwt-cryptographic-correctness]]
- [[session-management|Session Management]] depende de [[random-and-csprng-pitfalls]]
- [[jwt-attacks|JWT Attacks]] depende de [[jwt-cryptographic-correctness]] y [[digital-signatures]]
- [[secrets-management|Secrets Management]] depende de [[symmetric-encryption-modes]] y [[kdf-and-key-stretching]]
- [[mfa-phishing-resistance|MFA Phishing Resistance]] depende de [[digital-signatures]] (modelo de firma WebAuthn)
- [[end-to-end-encryption|End-to-End Encryption]] y [[pgp-encryption-and-signatures|PGP]] dependen de [[asymmetric-encryption-and-key-exchange]] y [[digital-signatures]]

---

## Calibración

- Esta rama es de primitivos y corrección, no de matemática. El objetivo es razonar con confianza sobre fallas del mundo real, no derivar aritmética de curvas elípticas.
- La rama incluye deliberadamente una sección "qué no funciona" en cada nota (por ejemplo, MD5 para almacenamiento de contraseñas, modo ECB, cifrado-sin-MAC, JWT `alg=none`) — las defensas falsas son la forma más común de bugs cripto.
- La resistencia cuántica se trata en una sola nota de conciencia, no como una preocupación operacional actual.
