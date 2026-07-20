---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# TLS Handshake and PKI

## Definition

TLS is a transport-layer protocol that establishes a confidential, authenticated channel between two parties by combining (1) an asymmetric handshake that authenticates at least one peer using a certificate signed by a trusted CA, with (2) a symmetric AEAD record protocol that protects the rest of the conversation. PKI (X.509 public key infrastructure) is the trust graph of certificates, intermediates, and root stores that makes the handshake's authenticity claim meaningful.

## Why it matters

Almost every TLS bug in production is one of three things: a misconfigured certificate (wrong SAN, expired, weak key), a misconfigured handshake (deprecated version, weak cipher, missing forward secrecy), or a misconfigured trust decision (no validation, wrong root store, broken pinning). Reading TLS configurations correctly is the foundation for reasoning about HTTPS, mTLS, MQTT-over-TLS, gRPC, and reverse-proxy mediation. It is also a prerequisite for understanding mid-path attacks (mitmproxy, evilginx, fake CAs) and certificate-driven detection (CT logs, ssh-style TOFU).

## How it works

TLS 1.3 (RFC 8446) is the modern handshake. It collapses the older 2-round-trip TLS 1.2 flow into a single round trip and removes weak primitives by construction. The handshake has 5 logical steps:

1. **ClientHello** — the client sends a list of supported versions, cipher suites (AEAD only in TLS 1.3), supported groups (X25519, P-256), signature algorithms (Ed25519, RSA-PSS, ECDSA-P256), and a key share (its ECDH public key).
2. **ServerHello + Certificate + CertificateVerify + Finished** — the server picks a cipher suite and group, sends its certificate chain, signs the handshake transcript with its private key (`CertificateVerify`), and confirms with `Finished`. From here the connection is encrypted with handshake traffic keys.
3. **Client validates the certificate chain.** The client walks the chain from leaf → intermediates → root, checks signatures with each issuer's public key, checks `notBefore`/`notAfter`, checks `keyUsage`/`extKeyUsage`/`basicConstraints`, validates the hostname against `subjectAltName`, and consults revocation (CRL or OCSP, optionally OCSP stapling).
4. **Client `Finished` and key derivation.** Both sides derive symmetric AEAD keys for the application traffic from the ECDH shared secret via HKDF. The handshake transcript is bound into the keys, so any tampering breaks the next message.
5. **Application data** — record-layer AEAD (AES-GCM, AES-CCM, ChaCha20-Poly1305) protects everything else.

```
ClientHello (versions, suites, groups, signature_algs, key_share)
     -->                                                          <-- ServerHello
                                                                       Certificate
                                                                       CertificateVerify
                                                                       Finished
client validates cert chain + hostname
Finished -->
<-- application data over AEAD record protocol
```

The bug is not "TLS is hard"; it is "the authenticity claim depends on a chain of trust the implementation must actively verify." Disabling validation, accepting wrong hostnames, or trusting a custom root store turns TLS into encrypted but unauthenticated transport — which is exactly what mid-path attackers want.

## Techniques / patterns

The reasoning model when reviewing a TLS deployment:

- **Version posture:** TLS 1.3 preferred; TLS 1.2 acceptable; TLS 1.0/1.1 disabled; SSL 3.0 / 2.0 disabled.
- **Cipher posture:** TLS 1.3 AEAD suites only (AES-GCM, ChaCha20-Poly1305); TLS 1.2 forward-secrecy ECDHE-only with AEAD; static-RSA key exchange disabled.
- **Certificate posture:** ECDSA-P256 or RSA-2048+ keys; SHA-256+ signatures; current and well-formed `notBefore`/`notAfter`; SAN includes the hostnames in use; chain serves any required intermediates; CT-logged.
- **Trust posture:** clients use the OS or platform root store; custom roots are explicit and minimal; pinning is used when the trust set is narrower than "the public Internet"; revocation is checked via OCSP or short-lived certs.
- **Probe pattern in code review:** grep for `verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`, `setSSLSocketFactory`, `TrustManager` overrides, custom hostname verifiers, and `sslcontext.set_default_verify_paths` overrides. Each is a place where someone might have disabled validation "just for testing" and forgotten to remove it.

## Variants and bypasses

The 5 TLS-deployment shapes you will encounter in practice.

### Server-auth TLS (the default web shape)

Client validates server certificate; server does not authenticate the client at TLS layer. Authentication of the client happens at higher layers (passwords, tokens, cookies). This is the entire public web. The trust decision is "does the leaf chain to a CA my OS trusts and does its SAN match the hostname I asked for."

### Mutual TLS (mTLS)

Both client and server present certificates. Used for service-to-service authentication, IoT device fleets, and zero-trust networks. The trust decision becomes bidirectional: both sides must validate the other's chain, hostname/identifier, and any organizational policy embedded in the cert (SPIFFE IDs, internal CN/OU conventions). mTLS is *transport authentication*, not authorization — what the cert is allowed to do is a separate decision.

### Public CA vs private CA

Public CAs (Let's Encrypt, Sectigo, DigiCert) are trusted by default browsers/OSes. Private CAs (corporate, K8s service mesh, AWS PCA) are only trusted within their org. Mixing them up — accepting a private CA in a public-facing context, or trusting public CAs in a private mesh — broadens the attack surface unnecessarily.

### Pinning

The client only accepts a specific certificate, public-key hash, or CA. Useful when you control both ends (mobile app to your API, IoT device to your fleet manager). Brittle if the pin set is a single key — rotation requires a software update. Best practice: pin to the SPKI hash of multiple keys, rotate before any single pin's expiry, prefer dynamic pinning (HPKP-style or platform-specific) when available.

### TOFU and anonymous TLS

Trust on first use (SSH-style) or anonymous-DH style. Common in SSH, Tor onion services, and Noise-Protocol systems. Useful where there is no global PKI; vulnerable to the first-encounter MITM.

## Impact

- **No certificate validation:** any mid-path attacker (rogue Wi-Fi, compromised proxy, evilginx) can transparently MITM. All "encrypted" traffic is plaintext to the attacker. Credentials, tokens, and PII leak.
- **Wrong hostname acceptance:** even a real CA-signed cert for a different hostname succeeds, which lets a domain-validating attacker pivot.
- **Weak primitives (TLS 1.0, RC4, 3DES, NULL ciphers, export-grade):** known attacks (BEAST, CRIME, POODLE, SWEET32, FREAK, Logjam) chip away at confidentiality and integrity in specific scenarios.
- **No forward secrecy (static-RSA key exchange):** if the server private key ever leaks, *all past* traffic that was captured is decryptable. ECDHE prevents this.
- **Long-lived certificates without revocation:** a stolen private key remains usable until the cert expires. Modern best practice trends toward 90-day or shorter certs and OCSP must-staple.
- **Trusting a private CA across the org:** any holder of any private CA cert can mint certs for any hostname; one compromised CI runner becomes a wildcard MITM.

Severity escalates when TLS protects high-value identity (admin sessions, code signing, payments), when pinning is absent on mobile apps, and when client validation is disabled "for development".

## Detection and defense

Ordered by what works:

1.
**TLS 1.3-only or TLS 1.3 + TLS 1.2 with FS-only suites.**
   Disable TLS 1.0, 1.1, and SSL 3.0/2.0. In TLS 1.2, allow only ECDHE_ECDSA / ECDHE_RSA with AES-GCM or ChaCha20-Poly1305. Mozilla's "intermediate" or "modern" profile is a good starting set. Re-check with SSL Labs.

2.
**Validate certificates by default; never disable validation in production code.**
   Treat `verify=False`, `InsecureSkipVerify`, `rejectUnauthorized: false`, and overridden `TrustManager`/`HostnameVerifier` as production lint failures. Provide a development-only configuration path that is impossible to hit in production builds.

3.
**Use ACME-managed certificates with short lifetimes.**
   Let's Encrypt and similar ACME issuers automate issuance and renewal. Short-lived certs (≤ 90 days) reduce the window of value of a stolen key. Internal services should use an internal ACME (step-ca, smallstep, K8s cert-manager) rather than long-lived hand-issued certs.

4.
**Watch CT logs for hostnames you own.**
   Certificate Transparency logs (RFC 6962) record every issued cert. Subscribe to alerts for your domains (Cert Spotter, Censys CT alerts, Crt.sh feed) — unexpected issuance is a rogue-CA or supply-chain signal.

5.
**Pin in apps where the trust set is narrower than the Web PKI.**
   Mobile apps and embedded devices that talk to your own services should pin to your SPKI hashes, with multiple pins for rotation. Browsers should not pin via HPKP (deprecated); rely on CT and Expect-CT.

### What does not work as a primary defense

- **"We use HTTPS, so we are secure."** TLS without validation is encryption against passive observers only. Active attackers (rogue Wi-Fi, captive portals, compromised proxies, evilginx-style reverse-proxy phishing) trivially MITM unvalidated TLS.
- **"We use a long key (RSA-4096), so the cipher does not matter."** Key size is unrelated to cipher mode. RSA-4096 + RC4 is still RC4-broken.
- **"We trust the cert because it is in our Java keystore."** Adding a custom root to the keystore broadens trust to *every* cert that root signs, forever. Pinning narrows; trusting widens.
- **"OCSP responder is down so we just skip revocation."** Soft-fail OCSP is essentially no revocation. Prefer OCSP must-staple and short-lived certs over manual fail-open.
- **"We disabled validation for the staging environment and use the same code path in prod."** This is the single most common production-grade TLS failure. Use a platform-level boundary: distinct configs per environment, distinct secret stores, and CI checks that fail the build if validation is disabled in a prod artifact.

## Practical labs

### Inspect a TLS handshake with curl/openssl

```
# OpenSSL connect with verbose handshake details
openssl s_client -connect example.com:443 -servername example.com -tls1_3 -showcerts < /dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName -ext extendedKeyUsage
# curl with verbose handshake
curl -vI --tls-max 1.3 https://example.com 2>&1 | grep -E 'TLS|cipher|ALPN|subject|issuer'
```

Result: you can see the negotiated version, suite, ALPN, leaf SAN, issuer, and validity. If your server falls back below your floor, the suite and version values reveal it.

### Score the deployment with SSL Labs

```
https://www.ssllabs.com/ssltest/analyze.html?d=example.com
```

Result: a letter grade plus the exact reason for each deduction. Aim for A+, with HSTS, full chain, OCSP must-staple, and modern suites only.

### Reproduce a "failed validation" client correctly

```
import ssl, socket
ctx = ssl.create_default_context()  # secure defaults: TLSv1.2+, validates chain + hostname
with socket.create_connection(("example.com", 443)) as raw:
    with ctx.wrap_socket(raw, server_hostname="example.com") as s:
        print(s.version(), s.cipher())
        print(s.getpeercert()["subject"], s.getpeercert()["subjectAltName"])
```

Result: `ssl.create_default_context()` is the safe call. Switch to `ssl._create_unverified_context()` and observe how a wrong-hostname or self-signed cert silently succeeds — that is exactly the mid-path-attack surface.

### Detect mid-path injection via mitmproxy

```
# install mitmproxy, generate its CA, do NOT install it in your real system trust store
mitmproxy
# point a curl at the mitm: by default validation fails because the mitmproxy CA is not trusted
curl -x http://127.0.0.1:8080 https://example.com -v
# only with -k (insecure) or with the mitmproxy CA explicitly added does the curl succeed
```

Result: a correctly configured client *fails* to MITM. The vulnerability is in clients that disable validation. Run the same scenario against a mobile-app emulator with and without pinning to see how pinning narrows trust further.

### Validate cert lifetime, SAN, and issuer in CI

```
# Fail CI if cert expires within 14 days, missing required SAN, or wrong issuer
HOST=example.com
NOTAFTER=$(echo | openssl s_client -servername $HOST -connect $HOST:443 2>/dev/null \
  | openssl x509 -noout -enddate | cut -d= -f2)
EXP_TS=$(date -j -f "%b %e %T %Y %Z" "$NOTAFTER" +%s 2>/dev/null || date -d "$NOTAFTER" +%s)
NOW_TS=$(date +%s)
echo "days_left=$(( (EXP_TS - NOW_TS) / 86400 ))"
```

Result: a one-line CI gate that catches the most common operational TLS bug — silent expiry.

## Practical examples

- An internal microservice mesh accepts both Let's Encrypt and a private CA root because of historical migration. Removing the public CA from the internal trust store reduces the cross-trust attack surface to zero with no functionality cost.
- A mobile app uses `verify=False` for a development build and a forgotten flag flips on for production. Add a CI check that scans the production binary for the symbol or string and fails the build.
- An IoT fleet manager pins a single SPKI hash in firmware. The cert rotates and 100k devices break. Move to multi-pin (current + next) and document the rotation playbook.
- An admin notices unexpected certs for `pay.example.com` in CT logs. Investigation reveals a CI runner with a private CA that an engineer added to test something months ago. Revoke, rotate, and add a CT-watch alert.
- A new gRPC service uses static-RSA TLS 1.2 because of an old library default. Past captured traffic is now retroactively decryptable if the key leaks. Switch to TLS 1.3 (FS by construction) and rotate keys.

## Related notes

- [[asymmetric-encryption-and-key-exchange]]
- [[digital-signatures]]
- [[symmetric-encryption-modes]]
- [[aead-and-nonce-misuse]]
- [[certificate-validation-and-pinning]]
- [[tls-https|TLS / HTTPS]]
- [[reverse-proxies|Reverse Proxies]]
- [[cloud-dns-and-certbot|Cloud DNS and Certbot]]
- [[evilginx-and-reverse-proxy-phishing|Evilginx and Reverse-Proxy Phishing]]

### Suggested future atomic notes

- certificate-transparency-monitoring
- acme-and-short-lived-certs
- mtls-deployment-patterns
- hsts-and-preload
- downgrade-attacks-and-tls-fallback
- spiffe-and-workload-identity

## References

- **Standard / RFC:** RFC 8446 The Transport Layer Security (TLS) Protocol Version 1.3 — https://www.rfc-editor.org/rfc/rfc8446
- **Foundational:** Mozilla Server Side TLS Recommendations — https://wiki.mozilla.org/Security/Server_Side_TLS
- **Testing / Lab:** SSL Labs SSL Server Test — https://www.ssllabs.com/ssltest/
