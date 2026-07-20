---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Digital Signatures

## Definition

A digital signature is an asymmetric proof that a specific private key approved a specific message. Anyone with the matching public key can verify the signature, but only the private-key holder should be able to create it.

## Why it matters

Digital signatures sit underneath TLS certificates, WebAuthn/passkeys, signed JWTs, package signing, code signing, software updates, PGP signatures, SSH host keys, and audit trails. They are different from MACs: with a MAC, every verifier can also forge because they share the same secret; with a signature, the verifier only needs the public key. That distinction is why signatures matter across organizational boundaries.

## How it works

Digital signatures answer **4 questions**:

1.
**Which bytes were signed?**
   Signatures bind to bytes, not intentions. If the signed representation differs from the parsed representation, the system can still fail.

2.
**Which private key signed them?**
   The private key creates the signature. If the private key leaks, the authorship guarantee collapses.

3.
**Which public key verifies them?**
   Verification proves only "the matching private key signed this." It does not prove the key belongs to the entity you think unless the public key itself is trusted.

4.
**Is the algorithm safe for this ecosystem?**
   Modern defaults: Ed25519 where available, RSA-PSS for RSA compatibility, ECDSA P-256 where required by platform constraints.

```
signature = Sign(private_key, message)
valid = Verify(public_key, message, signature)
```

Minimal Ed25519 shape:

```
openssl genpkey -algorithm ed25519 -out signing.key
openssl pkey -in signing.key -pubout -out signing.pub
printf "release artifact digest" > message.txt
openssl pkeyutl -sign -rawin -inkey signing.key -in message.txt -out sig.bin
openssl pkeyutl -verify -rawin -pubin -inkey signing.pub -in message.txt -sigfile sig.bin
```

The bug is not "we need encryption." Signatures do not hide data. They prove authorship and integrity for data that may be completely public.

## Techniques / patterns

- Find every place the system accepts signed data: JWTs, SAML, package metadata, webhooks, mobile updates, API callbacks, passkey assertions.
- Check what exact bytes are signed and whether the parser consumes the same bytes.
- Check public-key trust: certificate chain, JWKS origin, pinned key, package registry root, device credential, or manually verified fingerprint.
- Check algorithm allowlists. Verifiers should pin expected algorithms, not accept whatever the message header requests.
- Check key rotation and revocation. Old keys need a defined retirement path; compromised keys need emergency removal.
- Check signature replay. A valid signature on an old message may still need timestamp, challenge, nonce, origin, or audience binding.

## Variants and bypasses

Signature failures show up in **6 families**.

### 1. Verification skipped

The system parses the signed object but never calls verification, or ignores verification failure. This is the "signature as decoration" bug.

### 2. Wrong public key trusted

The signature is valid, but under an attacker-controlled public key. JWKS confusion, certificate validation failure, or accepting embedded public keys can all create this.

### 3. Algorithm confusion

The verifier accepts a weaker or different algorithm than intended. JWT `alg=none`, HS256-vs-RS256 confusion, and accepting RSA-PKCS1 where RSA-PSS is required are common examples.

### 4. Nonce failures in ECDSA-like schemes

ECDSA and DSA require a fresh unpredictable nonce for each signature unless deterministic nonce generation is used. Nonce reuse can reveal the private key.

### 5. Signed metadata but unsigned payload

The system signs a manifest but not the artifact bytes, or signs a header but not the body. Attackers swap the unsigned portion.

### 6. Missing context binding

The same valid signature is accepted in the wrong origin, audience, tenant, protocol, or time window because the signed message omits context.

## Impact

Ordered roughly by severity:

- **Identity or session forgery.** Signed tokens accepted under the wrong key or algorithm become authentication bypass.
- **Supply-chain compromise.** Software updates, packages, or artifacts install malicious content if signature verification is weak.
- **Passkey/WebAuthn bypass pressure.** Origin or challenge verification mistakes undermine phishing resistance.
- **Audit non-repudiation failure.** The system cannot prove who approved an action if keys are shared or verification is weak.
- **Trust-store poisoning.** Adding an attacker public key to a trusted key set makes every future signature valid.

Impact escalates when signatures guard software releases, authentication tokens, cross-organization approvals, or financial workflows.

## Detection and defense

Ordered by effectiveness:

1.
**Treat public-key trust as part of verification.**
   A signature is meaningful only under a trusted public key. Verify certificate chains, JWKS origins, pinned fingerprints, or registry trust roots before trusting the signature result.

2.
**Pin allowed algorithms per use case.**
   The verifier should already know whether it expects EdDSA, RS256, ES256, or RSA-PSS. Do not let attacker-controlled headers choose verification policy.

3.
**Sign the full security decision.**
   Include subject, issuer, audience, expiry, nonce/challenge, origin, tenant, action, artifact digest, and version where relevant.

4.
**Use modern libraries and deterministic nonce schemes where applicable.**
   Prefer Ed25519 for simplicity where ecosystem support exists. For ECDSA, rely on vetted implementations with deterministic nonces or strong CSPRNGs.

5.
**Design key rotation and revocation.**
   Keep key ids as routing metadata, not proof. Track active, retired, and revoked keys separately.

### What does not work as a primary defense

- **Checking that a signature field exists.** Existence is not verification.
- **Trusting a public key included by the attacker.** A valid signature under an attacker key proves attacker authorship, not legitimate authorship.
- **Letting the token choose the algorithm.** Algorithm negotiation inside untrusted data creates confusion bugs.
- **Signing only display text.** The machine-enforced fields must be signed.
- **Using one private key everywhere.** One compromise then breaks every trust boundary.

## Practical labs

### Sign and verify with Ed25519

```
openssl genpkey -algorithm ed25519 -out sk.pem
openssl pkey -in sk.pem -pubout -out pk.pem
printf "amount=100&to=alice" > message.txt
openssl pkeyutl -sign -rawin -inkey sk.pem -in message.txt -out sig.bin
openssl pkeyutl -verify -rawin -pubin -inkey pk.pem -in message.txt -sigfile sig.bin
```

Verification succeeds only for the exact message.

### Show message binding

```
printf "amount=900&to=alice" > message.txt
openssl pkeyutl -verify -rawin -pubin -inkey pk.pem -in message.txt -sigfile sig.bin || echo "verification failed"
```

Changing the message invalidates the signature.

### Inspect a certificate signature chain

```
echo | openssl s_client -connect example.com:443 -servername example.com -showcerts 2>/dev/null \
  | openssl x509 -noout -subject -issuer -text | rg "Subject:|Issuer:|Signature Algorithm"
```

TLS server identity depends on signatures chained to a trusted CA.

### Model signed artifact verification

```
artifact.tar.gz
artifact.sha256
artifact.sha256.sig

1. verify signature over artifact.sha256
2. compute SHA-256 over artifact.tar.gz
3. compare computed digest to signed digest
4. install only if both checks pass
```

The signature must authenticate the digest that actually corresponds to the artifact.

## Practical examples

- A JWT with RS256 is accepted only if the verifier uses the issuer's trusted public key and rejects algorithm confusion.
- A WebAuthn authenticator signs a challenge and origin-bound data; phishing resistance depends on verifying the origin and challenge.
- A package manager verifies repository metadata signatures before installing packages.
- A CI/CD system signs release artifacts so deployment can reject tampered builds.
- An SSH client warns when a server host key changes because the public key binding changed.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[mac-and-hmac]]
- [[asymmetric-encryption-and-key-exchange]]
- [[jwt-cryptographic-correctness]]
- [[tls-handshake-and-pki]]
- [[mfa-phishing-resistance|MFA Phishing Resistance]]
- [[artifact-integrity|Artifact Integrity]]

### Suggested future atomic notes

- code-signing
- package-signature-verification
- webauthn-signature-verification
- jwt-jwks-key-rotation

## References

- **Standard / RFC:** NIST FIPS 186-5: Digital Signature Standard — https://csrc.nist.gov/publications/detail/fips/186/5/final
- **Standard / RFC:** RFC 8032: Edwards-Curve Digital Signature Algorithm — https://www.rfc-editor.org/rfc/rfc8032
- **Standard / RFC:** RFC 8017: PKCS #1 v2.2 RSA Cryptography Specifications — https://www.rfc-editor.org/rfc/rfc8017
