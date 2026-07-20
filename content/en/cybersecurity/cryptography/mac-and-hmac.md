---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# MAC and HMAC

## Definition

A Message Authentication Code (MAC) is a keyed tag over a message that proves the message was produced or approved by someone who knows the shared secret key. HMAC is the most common MAC construction: it wraps a cryptographic hash function with a secret key so verifiers can detect tampering and forgery.

## Why it matters

MACs are the invisible workhorse behind signed cookies, webhook verification, API request signing, CSRF token protection, encrypted-record authentication, and many JWT deployments. The common mistake is to confuse a plain hash with a MAC. A hash says "this data has this fingerprint"; an HMAC says "someone with this secret key authenticated this exact data." That one word, secret, is the boundary between a checksum and a security control.

## How it works

HMAC answers **3 questions**:

1.
**What message was authenticated?**
   The exact bytes matter. `user=1&admin=false` and `admin=false&user=1` may parse the same in one framework but are different byte strings to HMAC.

2.
**Which secret key authenticated it?**
   The verifier and signer both know the same secret key. Anyone without the key should be unable to compute a valid tag for a changed message.

3.
**Was the tag checked safely?**
   The verifier recomputes the HMAC over the received message and compares it to the received tag with constant-time equality.

```
tag = HMAC(secret_key, canonical_message)
valid = constant_time_equal(tag, received_tag)
```

Safe webhook shape:

```
import crypto from "node:crypto";

function sign(secret, rawBody) {
  return crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
}

function verify(secret, rawBody, receivedHex) {
  const expected = Buffer.from(sign(secret, rawBody), "hex");
  const received = Buffer.from(receivedHex, "hex");
  return expected.length === received.length &&
    crypto.timingSafeEqual(expected, received);
}
```

The bug is not "we did not encrypt the message." A MAC does not need secrecy. The bug is "we let an attacker change or invent a message without proving knowledge of the key."

## Techniques / patterns

- Look for plain hashes used as signatures: `sha256(secret + message)`, `md5(message)`, `hash(payload)` in cookies or webhooks.
- Check whether the MAC covers the exact security-critical fields: user id, role, expiry, nonce, method, path, body hash, and key id where applicable.
- Verify canonicalization before signing. JSON, URLs, query strings, Unicode normalization, and header ordering can create "signed one thing, parsed another" bugs.
- Check tag comparison. HMAC tags, API signatures, and reset tokens should use constant-time comparison.
- Check key separation. The same key should not authenticate cookies, webhooks, CSRF tokens, and encrypted records unless a KDF derives separate context-bound keys.
- Check replay protection. A MAC proves authenticity, not freshness. Webhooks and signed requests usually need timestamps, nonces, or idempotency tracking.

## Variants and bypasses

MAC failures show up in **5 common families**.

### 1. Plain hash instead of keyed MAC

The application stores `sha256(payload)` beside `payload` and treats a matching hash as proof. Anyone who can edit the payload can recompute the hash. Without a secret key, there is no authenticity.

### 2. Length-extension-prone constructions

Constructions such as `sha256(secret || message)` with Merkle-Damgard hashes can be vulnerable to length extension. HMAC was designed to avoid this. Do not hand-roll keyed hashes.

### 3. Partial-message authentication

The tag covers the body but not the method, path, tenant, or expiry; or it signs a JSON string before the server adds trusted metadata. Attackers look for unsigned fields that still influence authorization.

### 4. Canonicalization mismatch

The signer signs one representation while the verifier or application parses another. Examples include duplicated query parameters, JSON key order, URL decoding differences, trailing slash normalization, and mixed Unicode forms.

### 5. Replayable valid tags

The tag is valid forever because the message has no timestamp, nonce, sequence number, or replay cache. A MAC can prove the old request was authentic; it cannot prove it is still appropriate.

## Impact

Ordered roughly by severity:

- **Authentication bypass.** Forged signed cookies or session-state tags can turn into user or admin impersonation.
- **Webhook forgery.** Fake payment, delivery, CI, or identity-provider events can drive business logic.
- **Request tampering.** Attackers can change amount, destination, tenant, role, or expiry if those fields are not authenticated.
- **Replay attacks.** Old valid messages trigger actions again.
- **Forensic confusion.** Logs show a "signed" message, but the signature covered a weaker representation than the application used.

Impact escalates when the MAC guards money movement, account recovery, release automation, webhook-driven provisioning, or cross-tenant state.

## Detection and defense

Ordered by effectiveness:

1.
**Use standard HMAC or AEAD, never homegrown keyed hashes.**
   HMAC-SHA-256 remains the boring safe default for keyed message authentication. For encrypted data, prefer AEAD so confidentiality and integrity are bound together.

2.
**Authenticate a canonical, security-complete message.**
   Decide exactly which bytes are signed and include every field that affects authorization, routing, expiry, tenant scope, and replay handling.

3.
**Compare tags in constant time.**
   Use platform helpers such as `crypto.timingSafeEqual` or `hmac.compare_digest`. First normalize length safely, then compare.

4.
**Add freshness for requests.**
   Include timestamp, nonce, sequence number, or event id. Store recently seen identifiers where replay has real impact.

5.
**Separate keys by purpose.**
   Derive separate keys for cookies, webhooks, CSRF, and encrypted records. Key separation prevents one exposed integration key from authenticating unrelated data.

### What does not work as a primary defense

- **Plain SHA-256 over the message.** A plain hash has no secret and no authorship property.
- **`sha256(secret + message)`.** This is a homegrown MAC shape and can be vulnerable to construction mistakes such as length extension.
- **Base64 encoding.** Encoding changes representation; it does not authenticate anything.
- **Encrypting without authentication.** Confidential ciphertext can still be malleable unless it is authenticated.
- **Checking only that a signature header exists.** Presence is not verification.

## Practical labs

### Verify a webhook HMAC

```
SECRET="lab-secret"
BODY='{"event":"payment.succeeded","amount":1000,"currency":"USD"}'
TAG=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -binary | xxd -p -c 256)
echo "$TAG"
printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$SECRET" -binary | xxd -p -c 256
```

The two tags match only when the exact same bytes and secret are used.

### Show that changing one byte breaks the tag

```
SECRET="lab-secret"
BODY1='{"admin":false}'
BODY2='{"admin":true}'
printf '%s' "$BODY1" | openssl dgst -sha256 -hmac "$SECRET"
printf '%s' "$BODY2" | openssl dgst -sha256 -hmac "$SECRET"
```

This demonstrates integrity: small message changes produce unrelated tags.

### Compare plain hash and HMAC

```
MSG='user=123&role=user'
printf '%s' "$MSG" | openssl dgst -sha256
printf '%s' "$MSG" | openssl dgst -sha256 -hmac "secret-a"
printf '%s' "$MSG" | openssl dgst -sha256 -hmac "secret-b"
```

The plain hash is public and reproducible; the HMAC depends on the secret.

### Test replay thinking

```
POST /webhook
X-Timestamp: 2026-05-02T12:00:00Z
X-Event-Id: evt_123
X-Signature: hmac(...)

{"action":"grant_credit","account":"123","amount":500}
```

The signature proves authenticity; the timestamp and event id are what let the receiver reject stale or repeated messages.

## Practical examples

- A payment processor signs webhook bodies with HMAC; the receiver must validate the raw body bytes before processing the event.
- A signed cookie stores user id and expiry; the HMAC must cover both or the expiry can be tampered with.
- An API signs method, path, timestamp, and body hash; omitting the path lets a valid signature on one endpoint be replayed to another.
- A CSRF token is an HMAC over session id and nonce; plain random tokens work too, but HMAC lets the server verify statelessly.
- A mobile app signs requests with a shared secret embedded in the app; once extracted, the MAC no longer proves a trusted client.

## Related notes

- [[hashing-vs-encryption-vs-signing]]
- [[symmetric-encryption-modes]]
- [[jwt-cryptographic-correctness]]
- [[kdf-and-key-stretching]]
- [[session-management|Session Management]]
- [[api-auth-flaws|API Auth Flaws]]

### Suggested future atomic notes

- webhook-signature-verification
- canonicalization-before-signing
- signed-cookie-design
- replay-protection

## References

- **Standard / RFC:** NIST FIPS 198-1: The Keyed-Hash Message Authentication Code — https://csrc.nist.gov/publications/detail/fips/198/1/final
- **Standard / RFC:** RFC 2104: HMAC — https://www.rfc-editor.org/rfc/rfc2104
- **Foundational:** OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
