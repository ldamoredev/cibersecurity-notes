---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Post-Quantum Awareness

## Definition

Post-quantum cryptography (PQC) is cryptography designed to remain secure against adversaries with large-scale quantum computers. For most practitioners today, post-quantum awareness means knowing which current public-key systems are at risk, where long-lived encrypted data is exposed to "harvest now, decrypt later," and how to build crypto-agility for migration.

## Why it matters

Quantum risk is not evenly distributed. Symmetric encryption and hashes mostly need larger security margins, while RSA, classic finite-field Diffie-Hellman, ECDH, ECDSA, and EdDSA are the public-key families threatened by sufficiently capable quantum computers. The practical work today is inventory and migration planning, not panic. Systems with long confidentiality lifetimes need attention earlier because encrypted traffic can be captured now and decrypted later if the public-key exchange becomes breakable.

## How it works

PQC awareness has **4 concepts**:

1.
**Threatened primitives**
   Shor's algorithm threatens RSA, finite-field DH, elliptic-curve DH, ECDSA, and EdDSA. Grover's algorithm affects symmetric search less dramatically and is handled with larger key sizes.

2.
**New standards**
   NIST has standardized ML-KEM for key encapsulation in FIPS 203, ML-DSA for signatures in FIPS 204, and SLH-DSA for stateless hash-based signatures in FIPS 205.

3.
**Hybrid migration**
   Many deployments combine classical and post-quantum key exchange during transition so security does not depend on only one new assumption.

4.
**Crypto-agility**
   Systems need algorithm identifiers, key rotation, protocol negotiation, dependency inventory, and tested migration paths.

```
today:
  TLS with ECDHE -> symmetric session keys

transition:
  hybrid key exchange: ECDHE + ML-KEM -> session keys

long-term:
  standardized PQC KEM/signature where ecosystem support is ready
```

The bug is not "we have not switched everything today." The bug is not knowing where cryptography lives, what data lifetime it protects, and whether the system can change algorithms without a rewrite.

## Techniques / patterns

- Inventory public-key cryptography: TLS, SSH, VPN, S/MIME, PGP, code signing, package signing, device certificates, KMS, mTLS, JWT signing, firmware updates.
- Classify confidentiality lifetime: minutes, days, years, decades.
- Prioritize "harvest now, decrypt later" surfaces: internet TLS, VPN traffic, backups, medical, legal, financial, government, and intellectual-property data.
- Check vendor roadmaps for PQC/hybrid TLS, HSM/KMS support, certificate authority support, and library support.
- Track signatures separately from key exchange. Migration pressure is different for confidentiality and authenticity.
- Build crypto-agility into formats: algorithm id, version, key id, migration tests, deprecation windows.

## Variants and bypasses

PQC planning failures fall into **5 families**.

### 1. No cryptographic inventory

Teams cannot migrate what they cannot find. Crypto hides in libraries, appliances, mobile apps, SDKs, certificates, backups, and vendor protocols.

### 2. Long-lived confidentiality ignored

Short-lived web sessions and decade-long archives have different urgency. Captured encrypted archives may matter long after today's TLS session expires.

### 3. Signature and KEM confusion

ML-KEM solves key establishment; ML-DSA and SLH-DSA solve signatures. Replacing one does not automatically replace the other.

### 4. Algorithm agility without operational agility

The format has an `alg` field, but clients, HSMs, CAs, monitoring, and incident response cannot handle rotation.

### 5. Premature custom adoption

Teams wire experimental algorithms or obscure libraries into production without ecosystem support, side-channel review, or update paths.

## Impact

Ordered roughly by severity:

- **Future decryption of captured traffic.** Long-lived confidential data protected by quantum-vulnerable key exchange may be exposed later.
- **Signature trust disruption.** Code-signing, firmware, package, and document signatures may need new trust roots and validation stacks.
- **Migration outages.** Hardcoded algorithms and brittle clients break during transition.
- **Vendor lock-in risk.** Systems that depend on appliances or proprietary crypto may wait on vendor timelines.
- **False sense of safety.** "PQC-ready" marketing may cover one protocol but not backups, SSH, signing, or embedded devices.

## Detection and defense

Ordered by effectiveness:

1.
**Create a cryptographic inventory.**
   Track where public-key cryptography is used, which algorithms and libraries are involved, which data lifetimes they protect, and who owns migration.

2.
**Prioritize long-lived confidentiality.**
   Systems vulnerable to harvest-now-decrypt-later deserve earlier planning than short-lived low-sensitivity sessions.

3.
**Prefer standardized, ecosystem-supported algorithms.**
   Use NIST-standardized algorithms and vendor-supported implementations rather than experimental production rollouts.

4.
**Design for hybrid transition.**
   Hybrid key exchange can reduce dependency on either the old classical assumption or the new PQC assumption during migration.

5.
**Test crypto-agility before crisis.**
   Practice rotating algorithms, keys, certificates, libraries, and protocol versions in staging.

### What does not work as a primary defense

- **Waiting until quantum computers are public.** Migration takes years, and captured data can be stored now.
- **Replacing only TLS.** SSH, VPNs, backups, signing, firmware, and KMS may still depend on vulnerable public-key crypto.
- **Inventing your own PQC.** Implementation and side-channel risk are high; use standardized libraries.
- **Assuming AES-256 fixes everything.** Public-key establishment and signatures are the main migration concern.
- **Buying "PQC-ready" without inventory.** Claims need mapping to actual protocols and data flows.

## Practical labs

### Make a crypto inventory starter table

```
system | protocol | algorithm | library/vendor | data lifetime | owner | migration status
api    | TLS      | ECDHE P-256 + RSA cert | nginx/OpenSSL | minutes-years | platform | unknown
vpn    | IKEv2    | ECDH + RSA cert        | vendor        | years         | infra    | vendor roadmap needed
updates| signing  | ECDSA P-256            | CI signer     | 10+ years     | release  | needs PQC plan
```

The first task is visibility, not replacement.

### Find public-key crypto mentions

```
rg -n "RSA|ECDSA|Ed25519|ECDH|X25519|Diffie|certificate|JWKS|signing|KMS|OpenSSL|BoringSSL|wolfSSL" .
```

This gives a rough inventory seed for application repositories.

### Classify harvest-now-decrypt-later risk

```
Question: If someone captures this encrypted data today, will it still be sensitive in 10 years?

No  -> monitor ecosystem migration.
Yes -> prioritize PQC/hybrid roadmap and vendor support.
```

Long confidentiality lifetime changes urgency.

### Check TLS library support

```
openssl version -a
```

Library version and provider support determine when hybrid/PQC experiments are realistic.

## Practical examples

- A healthcare archive encrypted today must remain confidential for decades, so PQC planning matters before a practical quantum computer exists.
- A firmware signing system uses ECDSA keys burned into devices. Migration requires device trust-store and update-format planning.
- A VPN appliance vendor supports hybrid key exchange in a new version, but old branch-office devices cannot upgrade.
- A company rotates web TLS but forgets SSH host keys, S/MIME, package signing, and KMS envelope workflows.
- A protocol includes algorithm ids but every client rejects unknown values, so agility exists only on paper.

## Related notes

- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[tls-handshake-and-pki]]
- [[certificate-validation-and-pinning]]
- [[kdf-and-key-stretching]]
- [[artifact-integrity|Artifact Integrity]]

### Suggested future atomic notes

- crypto-agility
- hybrid-key-exchange
- cryptographic-inventory
- pqc-for-code-signing

## References

- **Foundational:** NIST Post-Quantum Cryptography Project — https://csrc.nist.gov/projects/post-quantum-cryptography
- **Standard / RFC:** NIST FIPS 203: ML-KEM — https://csrc.nist.gov/pubs/fips/203/final
- **Standard / RFC:** NIST FIPS 204: ML-DSA — https://csrc.nist.gov/pubs/fips/204/final
- **Standard / RFC:** NIST FIPS 205: SLH-DSA — https://csrc.nist.gov/pubs/fips/205/final
- **Foundational:** NIST selected HQC as a backup KEM for future standardization — https://www.nist.gov/news-events/news/2025/03/nist-selects-hqc-fifth-algorithm-post-quantum-encryption
