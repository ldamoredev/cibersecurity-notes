---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# KDF and Key Stretching

## Definition

A Key Derivation Function (KDF) turns one secret into one or more purpose-bound cryptographic keys. Key stretching is a related use case where a low-entropy secret, usually a password, is deliberately made expensive to guess before it becomes a verifier or encryption key.

## Why it matters

Most systems do not have one neat key. They have a root secret, session secret, password, Diffie-Hellman output, cloud KMS data key, or recovery secret that must become several separate keys: encryption key, MAC key, client-to-server key, server-to-client key, cookie key, backup key. Using the raw secret everywhere creates key reuse and cross-protocol failure. KDFs are how a design says: "this key is only for this purpose."

## How it works

KDF use splits into **3 jobs**:

1.
**Extract**
   Turn uneven input material into a strong pseudorandom key. Example: HKDF-Extract over a Diffie-Hellman shared secret.

2.
**Expand**
   Derive one or more keys with explicit labels and context. Example: `app:v1:cookie-mac`, `app:v1:record-aead`, `app:v1:webhook-hmac`.

3.
**Stretch**
   Make guesses expensive when the input is human-memorable or low entropy. Example: PBKDF2, bcrypt, scrypt, or Argon2id for passwords.

HKDF shape:

```
prk = HKDF-Extract(salt, input_key_material)
okm = HKDF-Expand(prk, info="app:v1:purpose", length=32)
```

The bug is not "we did not hash the secret." The bug is "we reused one secret across purposes, or we treated a low-entropy password like a high-entropy key."

## Techniques / patterns

- Identify root secrets, master keys, passwords, API secrets, session secrets, and DH shared outputs.
- Check whether each purpose gets a separate derived key with a clear label.
- Check whether password-derived keys use a password KDF, not plain SHA-256.
- Check salt usage. KDF salts are not secret, but they prevent shared outputs and precomputation.
- Check context strings. Include application, version, tenant/environment where appropriate, direction, and purpose.
- Check rotation. KDF labels and versioning should make old/new keys distinguishable during migration.

## Variants and bypasses

KDF mistakes show up in **5 families**.

### 1. Raw secret reuse

The same secret signs cookies, encrypts records, verifies webhooks, and derives CSRF tokens. A leak in one subsystem becomes a universal break.

### 2. Hash-as-KDF

The application uses `sha256(secret)` or `sha256(password)` as a key. For high-entropy input this may accidentally look fine, but it lacks context, extract/expand separation, and password stretching.

### 3. Missing context binding

The KDF derives bytes but does not label purpose. Two different features can accidentally derive the same key or accept each other's outputs.

### 4. Password KDF confusion

PBKDF2, bcrypt, scrypt, and Argon2id are for low-entropy passwords. HKDF is not a password hashing function; it assumes input key material is already high entropy or comes from a key agreement.

### 5. Bad salt or parameter migration

Global salts, missing salts, static low iteration counts, or unversioned parameters make upgrades painful and weaken resistance to precomputation.

## Impact

Ordered roughly by severity:

- **Cross-protocol compromise.** A key leaked from a low-risk feature authenticates high-risk tokens elsewhere.
- **Password cracking acceleration.** Fast hash-derived password keys are cheap to brute force.
- **Token forgery.** Cookie, CSRF, webhook, and reset-token keys collide or reuse material.
- **Data decryption after partial leak.** One exposed derived key reveals unrelated encrypted data if derivation was not separated.
- **Migration failure.** Unversioned KDF outputs make it hard to rotate algorithms or parameters safely.

Impact escalates when the root secret is environment-wide, shared across tenants, or stored in source control.

## Detection and defense

Ordered by effectiveness:

1.
**Use HKDF or a standard KDF for high-entropy key material.**
   HKDF is the common extract-and-expand workhorse. Use explicit `info` labels for purpose, version, and direction.

2.
**Use password KDFs for passwords and passphrases.**
   Argon2id, scrypt, bcrypt, or PBKDF2 where required by FIPS constraints. Passwords need stretching, salts, and upgradeable parameters.

3.
**Separate keys by purpose.**
   Derive independent keys for encryption, MAC, sessions, cookies, webhooks, and backups. Do not reuse root secrets directly.

4.
**Version derivation context and parameters.**
   Include version labels and store KDF parameters next to derived artifacts where needed. Rotation is a design requirement, not a cleanup chore.

5.
**Keep root secrets in a real secret manager or KMS.**
   KDFs do not make hardcoded root secrets safe. They only structure how secrets are used after retrieval.

### What does not work as a primary defense

- **`sha256(password)` as an encryption key.** It is too fast and lacks memory hardness.
- **One environment secret for everything.** Convenience turns small leaks into full compromise.
- **Secret context in comments only.** The KDF needs machine-enforced context labels.
- **A global salt.** Salts should be unique enough to prevent shared outputs and precomputation.
- **Deriving keys client-side from weak user passwords without rate limits.** Offline guessing remains the enemy.

## Practical labs

### Derive two purpose-specific keys with HKDF

```
ROOT=$(openssl rand -hex 32)
openssl kdf -keylen 32 -kdfopt digest:SHA256 -kdfopt key:$ROOT -kdfopt info:"app:v1:cookie-mac" HKDF
openssl kdf -keylen 32 -kdfopt digest:SHA256 -kdfopt key:$ROOT -kdfopt info:"app:v1:record-aead" HKDF
```

The two outputs differ because the purpose labels differ.

### Show why labels matter

```
ROOT=$(openssl rand -hex 32)
openssl kdf -keylen 32 -kdfopt digest:SHA256 -kdfopt key:$ROOT -kdfopt info:"same-purpose" HKDF
openssl kdf -keylen 32 -kdfopt digest:SHA256 -kdfopt key:$ROOT -kdfopt info:"same-purpose" HKDF
```

Same root and same context produce the same key; context is part of the design.

### Compare password stretching cost

```
time openssl dgst -sha256 <<< "correct horse battery staple"
time openssl pkcs5 -in /dev/null -pass pass:"correct horse battery staple" -iter 600000 -v2 sha256 -topk8 -nocrypt -out /tmp/pbkdf2-test.pem 2>/dev/null || true
```

The exact command behavior may vary by OpenSSL version; the point is that password KDFs intentionally cost more than plain hashes.

### Sketch key separation for an app

```
root_secret from KMS
  -> HKDF(info="prod:v3:cookie-mac") -> cookie_mac_key
  -> HKDF(info="prod:v3:webhook-hmac:stripe") -> stripe_webhook_key
  -> HKDF(info="prod:v3:record-aead") -> record_encryption_key
  -> HKDF(info="prod:v3:csrf") -> csrf_key
```

This turns one managed root into explicit, separated application keys.

## Practical examples

- TLS derives traffic keys from a handshake secret and transcript context.
- A backup tool derives separate file-encryption and metadata-authentication keys from one archive key.
- A web app derives cookie-signing and CSRF keys from a root secret rather than reusing the same bytes directly.
- Password managers stretch a master password before unlocking high-entropy vault keys.
- Cloud envelope encryption separates root KMS keys from per-object data keys.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[password-hashing]]
- [[asymmetric-encryption-and-key-exchange]]
- [[symmetric-encryption-modes]]
- [[secrets-management|Secrets Management]]

### Suggested future atomic notes

- hkdf-context-design
- envelope-encryption
- secret-rotation
- client-side-encryption

## References

- **Standard / RFC:** NIST SP 800-108r1: Key Derivation Using Pseudorandom Functions — https://csrc.nist.gov/publications/detail/sp/800-108/rev-1/final
- **Standard / RFC:** RFC 5869: HKDF — https://www.rfc-editor.org/rfc/rfc5869
- **Standard / RFC:** RFC 8018: PKCS #5 PBKDF2 — https://www.rfc-editor.org/rfc/rfc8018
