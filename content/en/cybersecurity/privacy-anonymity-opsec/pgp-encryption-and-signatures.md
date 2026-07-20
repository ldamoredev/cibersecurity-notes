---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# PGP Encryption and Signatures

## Definition

PGP-style workflows use public-key encryption and signatures to protect content confidentiality and verify origin or integrity. In practice, the workflow depends on key management, trust decisions, and careful handling of metadata and endpoints.

## Why it matters

PGP can be very useful for file encryption, signed releases, and long-lived trust relationships. It is also easy to misuse: bad key verification, weak backup habits, stale keys, overbroad trust, and confusing encryption with anonymity all create real risk.

## How it works

Use the 4-step OpenPGP model:

1.
**Key generation**
   Each user creates a public/private key pair.

2.
**Key distribution**
   Public keys are shared through a channel the user must trust or verify.

3.
**Encryption or signing**
   Encryption protects content to a recipient key. Signing proves control of the signing key.

4.
**Verification and rotation**
   Keys must be verified, renewed, revoked, rotated, and backed up correctly.

Example:

```
sender -> encrypt to recipient public key -> ciphertext
sender -> sign with private key -> signature
recipient -> verify signature and decrypt locally
```

The bug is not PGP itself. The bug is confusing cryptographic correctness with identity, trust, and workflow safety.

## Techniques / patterns

- Verify fingerprints out of band when trust matters.
- Keep signing and encryption keys protected separately where possible.
- Use revocation and expiration intentionally.
- Back up keys safely and test recovery.
- Encrypt files, not just email text, when the use case calls for it.
- Treat key servers and directories as discovery aids, not trust sources.

## Variants and bypasses

Use the 6 PGP cases:

### 1. File encryption

Useful for protecting content at rest or in transfer.

### 2. Signed release artifacts

Useful for software or document authenticity.

### 3. Signed email

Provides authenticity but may still expose metadata and mail routing context.

### 4. Web of trust

Can work, but trust management is operationally demanding and often misunderstood.

### 5. Keyserver-discovered keys

Convenient for discovery, but keyserver presence does not prove trust.

### 6. Revocation and rotation failure

Expired, revoked, or replaced keys must be handled carefully or trust relationships rot.

## Impact

- Strong content confidentiality and authenticity when key management is sound.
- Protection for files and signed releases.
- Operational burden around trust, backups, revocation, and fingerprint verification.
- Metadata and account identity still remain outside PGP's content protection.
- False confidence when users think PGP makes them anonymous.

## Detection and defense

Ordered by effectiveness:

1.
**Verify fingerprints out of band**
   Fingerprint comparison is stronger than trusting a web page or directory listing.

2.
**Use expiration and revocation**
   Keys should be replaceable, and old keys should not live forever.

3.
**Back up keys safely**
   Losing a private key can mean losing access to encrypted data or signing identity.

4.
**Separate trust from convenience**
   A key being easy to find is not the same as it being trustworthy.

5.
**Keep the content/metadata distinction explicit**
   PGP protects content, not necessarily who sent it, when, or through which provider.

### What does not work as a primary defense

- **PGP is not anonymity.**
- **A verified keyserver listing is not identity verification.**
- **Encrypting mail does not hide headers or subject lines.**
- **Signing a file does not prove the device that signed it was uncompromised.**

## Practical labs

### Inspect a key workflow

```
Key fingerprint:
How verified:
Expiration:
Revocation method:
Backup location:
Used for signing:
Used for encryption:
```

This makes the trust model explicit.

### Classify a use case

```
Use case:
File encryption:
Email signing:
Software release:
Long-term archive:
Anonymous use:
Suitable tool:
```

PGP is not the answer to every private communication problem.

### Review key hygiene

```
Private key location:
Passphrase:
Hardware token:
Backup:
Revocation certificate:
Expiration:
```

Key hygiene is the control most people forget.

### Compare PGP to E2EE

```
Property                PGP               Modern E2EE
Content confidentiality:
Identity verification:
Multi-device convenience:
Metadata privacy:
Ease of recovery:
```

The comparison helps place PGP in the right niche.

## Practical examples

- A developer signs a release tarball so users can verify authenticity.
- A journalist encrypts a document for a known recipient.
- A team manages revocation when a key is rotated.
- A user trusts a key without verifying the fingerprint and gets the wrong identity.
- An email is encrypted but the subject line still reveals the topic.

## Related notes

- [[end-to-end-encryption|End-to-End Encryption]]
- [[secure-file-sharing|Secure File Sharing]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[artifact-integrity|Artifact Integrity]]

### Suggested future atomic notes

- key-fingerprint-verification
- revocation-certificates
- web-of-trust

## References

- **Official Tool Docs:** GnuPG Manual - https://gnupg.org/documentation/manuals/gnupg/
- **Official Tool Docs:** OpenPGP RFC 9580 - https://www.rfc-editor.org/rfc/rfc9580
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
