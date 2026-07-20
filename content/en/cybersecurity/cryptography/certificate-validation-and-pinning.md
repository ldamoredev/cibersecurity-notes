---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Certificate Validation and Pinning

## Definition

Certificate validation is the process of deciding whether a presented certificate chain proves the peer's identity for the name being contacted. Certificate pinning narrows that trust decision by requiring a specific certificate, public key, CA, or trust anchor in addition to normal validation.

## Why it matters

TLS does not protect against a man-in-the-middle unless the client validates the server identity. Many catastrophic "TLS bugs" are actually validation bugs: disabled verification, hostname mismatch ignored, expired cert accepted, private CA accidentally trusted, or pinning deployed without a rotation plan. Pinning can reduce CA and local trust-store risk, but it can also brick clients if treated as magic.

## How it works

Certificate validation answers **5 questions**:

1.
**Is the chain cryptographically valid?**
   Each certificate is signed by the next issuer up to a trusted root or configured anchor.

2.
**Is the certificate valid now?**
   Not before, not after, and not obviously revoked where revocation is checked.

3.
**Does the name match?**
   The DNS name or IP being contacted must match the Subject Alternative Name.

4.
**Is the key allowed for this use?**
   Key usage and extended key usage must permit server authentication or the relevant role.

5.
**Is the trust anchor acceptable for this context?**
   Public WebPKI, private CA, workload identity CA, or pinned SPKI must be the intended trust root.

```
connect to https://api.example.com
  -> receive leaf + intermediates
  -> build chain to trust anchor
  -> check validity, name, usage, policy
  -> optional: check pin / CT / expected issuer
  -> only then send secrets
```

The bug is not "the certificate is self-signed." Self-signed can be correct in a private system if explicitly trusted. The bug is accepting an identity without a deliberate trust path.

## Techniques / patterns

- Search for `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify`, `curl -k`, custom trust-all managers, and disabled hostname verification.
- Inspect SANs, issuer, expiry, key usage, and chain path with `openssl`.
- Check whether private CAs are scoped to internal clients rather than added broadly to user devices.
- Check pinning type: leaf cert pin, SPKI pin, CA pin, or trust-store restriction.
- Check pin rotation. There should be at least current and next pins or a safe update channel.
- Use Certificate Transparency monitoring for public names.

## Variants and bypasses

Validation failures cluster into **5 families**.

### 1. Verification disabled

Development flags escape into production. The connection is encrypted, but identity is not authenticated.

### 2. Hostname verification skipped

The chain is valid for some name, but not the requested name. Attackers with any valid certificate for a controlled domain can impersonate if name checks are disabled.

### 3. Overbroad trust store

The app trusts every OS/user-installed CA when it should trust only a private CA or pinned service key. Enterprise roots, malware-installed roots, and local proxies become part of the trust boundary.

### 4. Brittle pinning

The app pins a single leaf certificate and has no backup. Normal rotation breaks clients, so teams disable pinning during incidents.

### 5. Revocation and CT blind spots

Revocation checking is inconsistent in clients, and CT is usually monitoring rather than blocking. Attackers may exploit the time between issuance, detection, and response.

## Impact

Ordered roughly by severity:

- **Credential/token interception.** MITM can read bearer tokens if the client accepts the wrong peer.
- **API response manipulation.** Signed-in clients process attacker-controlled responses.
- **Update compromise.** Software update channels that skip validation can install malicious artifacts.
- **Private CA blast radius.** Overtrusted internal roots can impersonate unrelated services.
- **Availability failure.** Bad pinning can lock out entire mobile or IoT fleets.

## Detection and defense

Ordered by effectiveness:

1.
**Keep platform certificate validation enabled.**
   Default TLS stacks are usually safer than custom validators. Override only with narrow, reviewed trust anchors.

2.
**Verify hostnames and intended identity.**
   Chain validity is not enough. The certificate must be valid for the exact DNS name or service identity being contacted.

3.
**Use scoped private trust for internal systems.**
   Internal mTLS or workload identity should trust internal roots only where needed, not globally across browsers and user devices.

4.
**Pin only when the threat model justifies it.**
   Pinning helps mobile apps, high-risk APIs, and controlled clients. It requires backup pins, telemetry, and a rotation playbook.

5.
**Monitor CT and expiry.**
   CT catches unexpected public cert issuance; expiry monitoring catches the most common operational failure.

### What does not work as a primary defense

- **"It uses HTTPS."** HTTPS without validation is encryption to an unknown party.
- **`curl -k` in production scripts.** This disables identity verification.
- **Self-signed certificate without distribution of trust.** The client must explicitly trust the correct certificate or CA.
- **Single leaf pin forever.** Certificates rotate; brittle pins become outages.
- **Relying on revocation alone.** Revocation behavior is inconsistent; prevention and monitoring both matter.

## Practical labs

### Inspect a certificate chain

```
HOST=example.com
echo | openssl s_client -connect "$HOST:443" -servername "$HOST" -showcerts 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
```

Check whether the SAN matches the hostname and the certificate is inside its validity window.

### Detect disabled verification in a codebase

```
rg -n "verify\\s*=\\s*False|rejectUnauthorized\\s*:\\s*false|InsecureSkipVerify|TrustAll|curl\\s+-k|--insecure" .
```

Every match needs environment and threat-model review.

### Compare valid and invalid hostnames

```
openssl s_client -connect example.com:443 -servername example.com -verify_hostname example.com </dev/null
openssl s_client -connect example.com:443 -servername example.com -verify_hostname wrong.example </dev/null
```

The second command should fail hostname verification.

### Extract an SPKI pin candidate

```
HOST=example.com
echo | openssl s_client -servername "$HOST" -connect "$HOST:443" 2>/dev/null \
  | openssl x509 -pubkey -noout \
  | openssl pkey -pubin -outform der \
  | openssl dgst -sha256 -binary | openssl base64
```

Pinning SPKI is usually more rotation-friendly than pinning the whole leaf certificate, but still needs backup pins.

## Practical examples

- A mobile app sets `TrustAllCerts` during testing and ships it, allowing Wi-Fi MITM to capture API tokens.
- An internal CLI uses `curl -k` against production because an intermediate CA was missing once.
- A service mesh trusts both public WebPKI and internal CA for workload traffic, expanding who can impersonate internal services.
- A mobile banking app pins one leaf cert and breaks during planned certificate rotation.
- CT monitoring alerts on a certificate for a sensitive subdomain issued by an unexpected CA.

## Related notes

- [[tls-handshake-and-pki]]
- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[tls-https|TLS / HTTPS]]
- [[cloud-dns-and-certbot|Cloud DNS and Certbot]]

### Suggested future atomic notes

- certificate-transparency-monitoring
- mtls-deployment-patterns
- spiffe-and-workload-identity
- acme-and-short-lived-certs

## References

- **Standard / RFC:** RFC 5280: Internet X.509 Public Key Infrastructure Certificate and CRL Profile — https://www.rfc-editor.org/rfc/rfc5280
- **Foundational:** OWASP Pinning Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Pinning_Cheat_Sheet.html
- **Standard / RFC:** RFC 6962: Certificate Transparency — https://www.rfc-editor.org/rfc/rfc6962
