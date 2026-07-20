---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# TLS and HTTPS

## Definition

HTTPS is HTTP carried over TLS. TLS (Transport Layer Security, formerly SSL) is the protocol that wraps a TCP connection — or a UDP-based QUIC connection in HTTP/3 — to provide three guarantees: **confidentiality** (the bytes on the wire are unreadable to anyone but the endpoints), **integrity** (any tampering is detectable), and **authenticity** (the server's identity is verified via a certificate chain anchored in trusted CAs; mTLS extends this to the client). TLS does not say anything about what the application does with those bytes once they arrive — that is the most common security misunderstanding in this whole topic.

## Why it matters

TLS is one of the few primitives that *actually works* against a network attacker — and exactly one of the most overestimated defenses in production. It matters because:

- **It is the only practical defense against passive interception** of credentials, tokens, and PII on the wire.
- **It anchors cookie and storage security.** `Secure`, `HttpOnly`, `SameSite=None` semantics, and `__Host-` cookie prefixes are only meaningful over TLS.
- **It is a trust boundary at every termination point.** Where TLS ends, the plaintext begins; that hop becomes interesting to anyone on the same network segment.
- **It is *not* an application-layer defense.** Smuggling, deserialization, IDOR, XSS, SSRF, host-header attacks all happen *inside* the TLS tunnel. "We use HTTPS" is the wrong answer to most security questions.

This note covers the deployment-and-trust view of TLS — what to verify, where it fails in production, how to test it. The cryptographic internals (key exchange algorithms, AEAD constructions, certificate ASN.1 structure) are out of scope; see references for the formal treatment.

## How it works

TLS provides **3 guarantees** through **4 handshake phases** (in TLS 1.2; TLS 1.3 collapses several into fewer round-trips for performance, but the conceptual phases remain).

The 3 guarantees:

1. **Confidentiality** — symmetric encryption (AEAD ciphers like AES-GCM, ChaCha20-Poly1305) protects the bytes after the handshake.
2. **Integrity** — every record carries an authentication tag derived from the session keys; tampering is detected and the connection aborts.
3. **Authenticity** — the server presents a certificate chain; the client verifies the chain anchors in a trusted root CA and that the certificate matches the requested hostname. Optionally, the server requires the client to present a certificate too — this is **mTLS**.

The 4 phases:

1. **ClientHello** — client offers TLS versions, cipher suites, ALPN protocols (h2 / http/1.1 / h3), supported extensions, and an SNI (Server Name Indication) telling the server which hostname the client wants to talk to.
2. **ServerHello + Certificate + KeyExchange** — server picks a version + cipher + ALPN, sends its certificate chain, sends its key-exchange parameters. Client validates the certificate chain (signed by trusted CA, not expired, hostname matches, not revoked).
3. **Key derivation + Finished** — both sides derive the session keys and confirm they match. Anyone unable to derive the same keys (because they don't have the server's private key) is locked out.
4. **Application data** — encrypted HTTP traffic flows. From this point forward, the wire bytes are opaque to anyone on the network path.

A practical inspection of a TLS handshake on the wire:

```
openssl s_client -connect example.com:443 -servername example.com -alpn h2,http/1.1 </dev/null
# Output reveals: TLS version, cipher suite, certificate chain, ALPN result
```

The bug is rarely in the TLS protocol itself (the cryptographic primitives are solid for current versions). The bug is overwhelmingly in **deployment**: where TLS terminates, what happens after termination, how clients validate, how long certificates live, and what the application assumes the moment plaintext is restored.

## Techniques / patterns

What attackers and operators look at:

- **Read the certificate.** Issuer, subject (`CN` and `Subject Alternative Name`), validity dates, signature algorithm, public-key parameters. SANs in particular reveal architecture: shared certs across hostnames, wildcard scope, internal hostnames accidentally in production certs.
- **Check the version and cipher.** TLS 1.0 and 1.1 are deprecated and broken in different ways; TLS 1.2 with non-AEAD ciphers (CBC + HMAC) has known weaknesses (BEAST, Lucky13). Anything less than TLS 1.2 + AEAD or TLS 1.3 is a finding.
- **Check the redirect chain.** `http://` should redirect to `https://`, ideally with HSTS already set on a redirect of *the same hostname* (some implementations set HSTS only on the secure response, missing the first request).
- **Check Certificate Transparency logs.** `crt.sh` reveals every cert issued for a domain — including misissued ones, internal-only hostnames that leaked into a public cert, and cert rotation history.
- **Check ALPN and HTTP version.** `h2` only at the edge with `http/1.1` to origin is the smuggling-reintroduction trap. See [[reverse-proxies]] §"HTTP/2 → HTTP/1.1 downgrade".
- **Look for mixed content.** A page served over HTTPS that loads scripts/iframes/forms over plaintext HTTP undermines the whole transport.

## Variants and bypasses

TLS deployments fail in **5 distinct classes**. Each is a deployment misconfiguration; the underlying cryptography is rarely at fault.

### 1. Edge-only TLS

TLS terminates at the load balancer / CDN / reverse proxy; traffic from there to the application server is plaintext. An attacker on the internal network — or anyone who has compromised a sidecar, neighboring container, or the LB/origin link itself — can observe credentials and session cookies. The backend may also trust `X-Forwarded-Proto: https` without verifying the connection actually came encrypted.

### 2. Skipped certificate validation

Clients (or server-side libraries making outbound HTTP calls) configure their HTTP client to not verify the certificate. Common offenders: `requests.get(url, verify=False)`, `curl -k`, `InsecureSkipVerify: true` in Go, custom `TrustManager` accepting all certs in Java. Often introduced "temporarily" against a dev cert and forgotten in prod. Fully neutralizes authenticity; integrity and confidentiality survive only against a non-MITM attacker.

### 3. Obsolete versions and weak ciphers

TLS 1.0/1.1 still enabled, RC4 / 3DES / export-grade ciphers still supported, weak DH parameters (Logjam), CBC-mode ciphers without protection (BEAST/Lucky13), SSLv3 (POODLE). Each is a separate downgrade or known-attack surface; modern policy is "TLS 1.3 preferred, TLS 1.2 with AEAD only, everything else disabled."

### 4. Missing or weak HSTS

No `Strict-Transport-Security` header, or one with too-short `max-age`, or without `includeSubDomains`, or not in the browser preload list. The first request from any new client may be over HTTP and is therefore MITM-able. Subdomain takeover risk (see [[subdomain-takeover|Subdomain Takeover]]) is amplified when the parent domain doesn't constrain subdomains via HSTS preload + includeSubDomains.

### 5. Cookie/storage flag misuse

Cookies set without `Secure` (sent over plain HTTP if any HTTP path exists), `HttpOnly` (readable from JS — combines badly with XSS), or `SameSite` (CSRF-vulnerable). The `__Host-` and `__Secure-` prefixes provide additional structural guarantees but are widely ignored. See [[cookies-and-sessions]].

## Impact

TLS deployment failures map to specific impact ceilings:

- **Credential / session theft** — edge-only TLS plus a network-adjacent attacker, or skipped validation plus an active MITM.
- **Phishing-grade MITM** — full handshake interception when validation is bypassed; the client sees no warning.
- **Downgrade attack** — old version negotiation forced (BEAST/POODLE-shaped) recovers plaintext.
- **Subdomain takeover amplification** — missing HSTS scope means a takeover of `forgotten.example.com` produces a valid cert that browsers trust.
- **Cookie hijacking via mixed content** — `Secure` flag missing means one HTTP request anywhere ships the session cookie.
- **Internal traffic exposure** — backend-only TLS gap leaks credentials to colocated workloads, sidecars, or compromised neighbors.

## Detection and defense

Ordered by effectiveness:

1.
**TLS end-to-end, including proxy → origin.**
   Edge termination is fine for performance but the *next* hop must also be TLS. The strongest version is mTLS between proxy and origin: the origin only accepts connections presenting a proxy-issued client certificate, which both encrypts the hop and authenticates the source. Without this, the backend's trust in `X-Forwarded-Proto: https` is forgeable by anyone who reaches the origin directly.

2.
**Strict certificate validation in every client, every library, every script.**
   `verify=True` is the default in `requests`; do not override it. `InsecureSkipVerify: true` in Go is for dev only; ban it in prod via lint/static analysis. Custom Java `TrustManager` overrides should be code-reviewed adversarially. Trust the OS / language CA bundle and rotate it; don't bypass it.

3.
**Modern TLS configuration: TLS 1.3 preferred, TLS 1.2 minimum, AEAD-only.**
   Disable TLS 1.0/1.1 entirely, disable RC4/3DES/export ciphers, prefer Mozilla's "intermediate" or "modern" config. Run a scanner (`testssl.sh`, SSL Labs) at a known cadence; certificate and cipher policy drift over time as new weaknesses are discovered.

4.
**HSTS with preload + includeSubDomains + max-age ≥ 1 year.**
   Header: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`. Submit to the browser preload list at `hstspreload.org` so even the *first* request over a new client is HTTPS-only. Do not enable `preload` until you are certain every subdomain — including future ones — can serve HTTPS, because removal from the preload list is slow.

5.
**Cert lifecycle automation.**
   Short-lived certs (90 days via Let's Encrypt or equivalent) with automated renewal eliminate "we forgot to rotate" outages and reduce the window of a compromised key. Monitor expiry actively (alert at 30 days) — automation breaks silently sometimes.

6.
**Cookie hygiene: `Secure`, `HttpOnly`, `SameSite=Lax` minimum.**
   For sensitive cookies, prefix with `__Host-` (forces `Secure`, no `Domain`, `Path=/`) for structural protection that flag-by-flag review can miss. See [[cookies-and-sessions]] for the full picture.

7.
**Constrain who can issue certs for your domain via CAA records.**
   `example.com.   CAA 0 issue "letsencrypt.org"` tells every CA except Let's Encrypt to refuse certificates for this domain. Combined with monitoring CT logs (`crt.sh`) for unexpected issuances, this catches misissuance and rogue-CA scenarios.

### What does not work as a primary defense

- **"We use HTTPS."** TLS protects bytes in flight. It does not protect against application-layer bugs. Smuggling, IDOR, XSS, SSRF, deserialization all happen inside the TLS tunnel. HTTPS is necessary; it is not sufficient.
- **Trusting `X-Forwarded-Proto: https`.** That header is a string the client (or anyone reaching the backend directly) can supply. Trust comes from the network path, not the header. See [[client-ip-trust]] for the same lesson on the IP side.
- **Self-signed certs in prod with skip-verify clients.** This pattern is ubiquitous in internal services and ubiquitously exploitable. The "we control both ends so it's fine" assumption breaks the moment one endpoint is compromised — the entire trust model collapses to "anyone on the network can MITM."
- **Long-lived certs without rotation.** A compromised key with a 2-year cert is dangerous for the full 2 years. Short certs reduce blast radius and force the rotation tooling to actually work.
- **Hand-rolled cert pinning in mobile apps.** Pinning is useful but operationally fragile; one botched cert rotation bricks the app. Use Certificate Transparency monitoring instead unless the threat model genuinely needs pinning.
- **Letting the browser HSTS-preload work itself out.** The preload list is opt-in; without explicit submission, the first request from any new client is plain HTTP.

## Practical labs

Stock openssl, curl, dig — plus `crt.sh` for Certificate Transparency.

### Inspect the certificate chain

```
# Full handshake: TLS version, cipher, certificate chain, SANs
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null 2>/dev/null \
  | openssl x509 -text -noout

# Just the SANs and validity dates
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -dates -ext subjectAltName
```

### Probe TLS versions and ciphers

```
# Test which TLS versions the server still accepts
for v in tls1 tls1_1 tls1_2 tls1_3; do
  printf '%-8s -> ' "$v"
  echo | openssl s_client -connect example.com:443 -servername example.com -"$v" 2>&1 \
    | grep -E '^(no peer certificate available|Cipher|wrong version|alert)' | head -1
done

# Probe a specific cipher suite
echo | openssl s_client -connect example.com:443 -servername example.com -cipher 'ECDHE-RSA-AES128-GCM-SHA256' 2>&1 \
  | grep -E '^(Cipher|alert)'

# For a deeper sweep, use testssl.sh: https://github.com/drwetter/testssl.sh
# testssl.sh --severity HIGH https://example.com
```

### Verify HSTS posture

```
# Is HSTS set, and with what scope?
curl -sI https://example.com/ | grep -i 'strict-transport-security'

# Is the bare http:// redirected?
curl -sI http://example.com/ | grep -iE 'http/|location|strict-transport-security'

# Is the domain on the browser preload list?
# Visit https://hstspreload.org/?domain=example.com — query format only,
# browsers ship the list embedded.
```

### Search Certificate Transparency for unexpected issuances

```
# crt.sh JSON API — list every cert ever issued for the domain
curl -s 'https://crt.sh/?q=%25.example.com&output=json' \
  | jq -r '.[] | "\(.not_before)  \(.issuer_name)  \(.name_value)"' \
  | sort -u | head

# Look for: certs you didn't issue, hostnames that should be internal-only,
# wildcard certs from CAs you don't use, and suspicious subdomains.
```

### Find skipped-verification clients in your own code

```
# A repo-wide audit for the most common skip-verify offenders
rg -n --hidden \
  -e 'verify=False' \
  -e '-k\b' \
  -e 'InsecureSkipVerify' \
  -e 'rejectUnauthorized: false' \
  -e 'CURLOPT_SSL_VERIFYPEER' \
  -e 'TrustManager' \
  .
```

### Confirm proxy → origin hop is encrypted

```
# If you have access to the origin IP, confirm it speaks TLS too
# (and rejects plain HTTP, ideally)
echo | openssl s_client -connect <origin-ip>:443 -servername example.com -showcerts </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer

# Plain HTTP to origin should fail or redirect, never serve sensitive data
curl -sI http://<origin-ip>/whoami -H 'Host: example.com'
```

## Practical examples

- A SaaS app terminates TLS at the AWS ALB and sends plaintext HTTP to the EKS pods. A compromised sidecar in another namespace ARP-spoofs the pod network and harvests session cookies for an hour before detection.
- An internal microservice calls a partner API with `requests.post(url, json=payload, verify=False)` left over from a 2022 staging fix. An on-path attacker rewrites the response and the service writes the result to the database without further validation.
- A staging hostname `internal-admin.example.com` accidentally lands in a public Let's Encrypt cert SAN list. CT logs surface it; an attacker discovers the hostname, finds it reachable from the internet, and exploits an admin-panel auth flaw.
- A bank disables TLS 1.0 on its public app but forgets the partner-API endpoint. A penetration test downgrades the connection and replays POODLE-style padding-oracle queries.
- A mobile app pins a single intermediate CA. The CA rotates its key. The pin update ships with the next app release — three weeks later. For three weeks, the app is unusable in the field; an attacker MITMs by impersonating the unrotated intermediate during the window.
- A subdomain `legacy.example.com` is dangling (CNAME to a deleted Heroku app). HSTS is set on `example.com` *without* `includeSubDomains`. An attacker takes over the legacy CNAME, gets a Let's Encrypt cert, and serves a phishing page the browser trusts as same-origin-adjacent.

## Related notes

- [[http-overview]] — TLS is stage 2 of the 5-stage HTTP transaction lifecycle (establish transport).
- [[http-headers]] — `Strict-Transport-Security`, cookie security flags.
- [[reverse-proxies]] — TLS termination is one of the 5 transformations a reverse proxy applies; the plaintext-to-origin hop is a recurring trust failure.
- [[client-ip-trust]] — `X-Forwarded-Proto` is the trust-disagreement specialization on the transport side.
- [[cookies-and-sessions]] — `Secure`, `HttpOnly`, `SameSite`, `__Host-` prefix semantics.
- [[load-balancers]] — common TLS termination point; check the proxy → origin hop here.
- [[dns-security]] — CAA records, DNS-based domain validation, takeover risk.
- [[subdomain-takeover|Subdomain Takeover]] — amplified when HSTS scope is wrong.
- [[csrf|CSRF]] — `SameSite` cookie behavior is a primary defense.
- [[cors-misconfiguration|CORS misconfiguration]] — `Origin` reasoning depends on TLS-confirmed identity.

### Suggested future atomic notes

- tls-1-3-handshake
- mtls-deployment-patterns
- certificate-transparency-monitoring
- acme-and-cert-automation
- hsts-preload-strategy
- cookie-prefixes-host-secure
- ocsp-and-crl-revocation

## References

- **Foundational:** MDN HTTPS — https://developer.mozilla.org/en-US/docs/Glossary/HTTPS
- **Foundational:** RFC 8446 (TLS 1.3) — https://datatracker.ietf.org/doc/html/rfc8446
- **Foundational:** Mozilla SSL Configuration Generator — https://ssl-config.mozilla.org/
- **Official Tool Docs:** OpenSSL s_client — https://docs.openssl.org/master/man1/openssl-s_client/
- **Testing / Lab:** testssl.sh — https://github.com/drwetter/testssl.sh
