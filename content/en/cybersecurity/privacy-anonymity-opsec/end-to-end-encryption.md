---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# End-to-End Encryption

## Definition

End-to-end encryption protects content so that only the communicating endpoints can decrypt it. It does not automatically hide metadata, account identity, device state, or behavior.

## Why it matters

E2EE is one of the most important privacy controls available, but it is also one of the most misunderstood. Users often hear "encrypted" and assume "private" or "anonymous," even though the server may still see who talked to whom, when, and from what device or account.

## How it works

Use the 4-layer E2EE model:

1.
**Key agreement**
   The endpoints establish a shared secret or key material.

2.
**Message encryption**
   The content is encrypted before it leaves the sender and decrypted only at the recipient.

3.
**Session update**
   Ratcheting or session refresh limits the effect of key compromise over time.

4.
**Trust boundaries**
   Servers, relays, and transport providers should not be able to read the message body, but they may still see metadata.

Conceptual example:

```
Sender app -> encrypt locally -> server relays ciphertext -> recipient app decrypts locally
```

The bug is not the absence of encryption. The bug is expecting encryption to erase metadata and identity signals.

## Techniques / patterns

- Encrypt before upload or send.
- Keep keys on endpoints, not on shared servers.
- Use protocols with forward secrecy and good session management.
- Minimize metadata in contact and group workflows.
- Separate content encryption from transport encryption.
- Inspect what the server can still observe.

## Variants and bypasses

Use the 6 E2EE cases:

### 1. Messaging E2EE

Protects chat content, but account and timing metadata may remain.

### 2. File E2EE

Protects file contents, but filenames, metadata, and delivery context still matter.

### 3. Backup E2EE

Protects backups if the key is controlled correctly, but recovery design becomes crucial.

### 4. Group E2EE

Protects content for the group, but membership and message fanout can still leak metadata.

### 5. Multi-device E2EE

Convenient, but more devices mean more keys and compromise surface.

### 6. Transport-only encryption

TLS protects in transit but is not E2EE. It is a different control.

## Impact

- Reduced server or relay visibility into message content.
- Better protection against passive network observers.
- Better protection if a provider is breached but endpoints remain safe.
- Continued exposure of metadata, identity, and behavior.
- Risk of false confidence if users confuse TLS with E2EE.

## Detection and defense

Ordered by effectiveness:

1.
**Use a protocol designed for E2EE**
   Signal-style protocols and modern OMEMO-style messaging are better starting points than ad hoc encryption.

2.
**Keep keys on trusted endpoints**
   The content is only private if the private keys are not casually exposed elsewhere.

3.
**Separate metadata from content thinking**
   Ask what remains visible even when the body is encrypted.

4.
**Use secure session management**
   Forward secrecy and ratcheting reduce blast radius over time.

5.
**Minimize device and backup sprawl**
   Every additional copy or device expands the attack surface.

### What does not work as a primary defense

- **TLS is not E2EE.**
- **E2EE does not hide sender/recipient metadata.**
- **E2EE does not fix compromised endpoints.**
- **A provider policy saying "we can't read messages" does not prove metadata privacy.**

## Practical labs

### Split content from metadata

```
Message body:
Attachment:
Sender identity:
Recipient identity:
Timestamp:
Device count:
Server logs:
```

This separates the actual encryption target from the surrounding metadata.

### Classify a protocol

```
Protocol:
Encrypts body before server:
Server sees recipients:
Server sees timing:
Forward secrecy:
Multi-device:
Group support:
```

This tells you whether the system is really E2EE or just transport encrypted.

### Review key storage

```
Keys stored where:
Backed up where:
Shared between devices:
Lost recovery path:
Compromise blast radius:
```

If keys are everywhere, privacy is not.

### Compare E2EE to TLS

```
Property                TLS                E2EE
Content privacy:
Server reads body:
Network observer sees body:
Metadata privacy:
Endpoint compromise resistance:
```

The difference between the two is the whole note.

## Practical examples

- Signal-style messaging protects content while the server still sees account-level metadata.
- A file transfer uses encryption but the filename still reveals context.
- A backup is encrypted but the recovery key is stored in an unsafe place.
- A user assumes HTTPS means only the recipient can read the message.
- A group E2EE chat still leaks membership and message timing.

## Related notes

- [[xmpp-and-private-messaging|XMPP and Private Messaging]]
- [[pgp-encryption-and-signatures|PGP Encryption and Signatures]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[tls-https|TLS / HTTPS]]

### Suggested future atomic notes

- signal-protocol
- e2ee-metadata
- ratcheting-protocols

## References

- **Research / Deep Dive:** Signal Technical Information - https://signal.org/docs
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
