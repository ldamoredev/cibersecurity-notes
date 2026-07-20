---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Private Email Threat Models

## Definition

Private email threat models describe which observers can see the contents, metadata, account identity, and access pattern of an email workflow, and what controls actually reduce each of those exposures.

## Why it matters

Email is often used for accounts, recovery, alerts, outreach, and sensitive communication. Even if message content is encrypted, the account, headers, sender, recipient, subject line, timing, and provider logs can still reveal a great deal.

## How it works

Use the 5 exposure layers:

1.
**Content**
   The body and attachments of the message.

2.
**Headers and metadata**
   Sender, recipient, subject, timestamp, routing, and message IDs.

3.
**Account identity**
   The address, recovery email, phone, login method, and device used.

4.
**Provider records**
   Logs, abuse handling, retention, authentication records, and metadata stored by the email service.

5.
**Behavior**
   Timing, reply cadence, subject patterns, and writing style.

The bug is not using email. The bug is thinking email has the same privacy properties as an anonymous message board.

## Techniques / patterns

- Separate content encryption from metadata privacy.
- Use different email identities for different purposes.
- Avoid using personal email for sensitive signups when the account identity matters.
- Assume the provider can see more than the recipient sees.
- Treat recovery channels as part of the identity model.
- Prefer minimal-account workflows when possible.

## Variants and bypasses

Use the 6 email patterns:

### 1. Personal mailbox

Convenient but highly identifying.

### 2. Separate pseudonymous mailbox

Useful for compartmentalization if recovery data and login habits are also separated.

### 3. Encrypted email

Protects contents, not necessarily headers, subject lines, sender identity, or provider logs.

### 4. Alias or forwarding address

Reduces exposure of the main inbox but may still link back through provider records.

### 5. Temporary mailbox

Useful for one-off signups, but often weak on persistence, recovery, and abuse tolerance.

### 6. Tor-centered email workflow

Can reduce local-network or ISP visibility, but the email provider and login behavior remain relevant.

## Impact

- Email addresses become durable identity anchors.
- Subject lines and headers can reveal sensitive context.
- Providers can retain metadata even when content is protected.
- Recovery workflows can re-link pseudonymous and real identities.
- Reply timing and style can correlate activities.

## Detection and defense

Ordered by effectiveness:

1.
**Use separate identities for separate purposes**
   A private identity should not share recovery channels, contacts, or login routines with a public one.

2.
**Minimize account data**
   The less recovery and profile data stored, the fewer identity hooks exist.

3.
**Encrypt contents when the recipient model supports it**
   Content encryption helps, but only when the corresponding key and operational workflow are handled safely.

4.
**Reduce metadata exposure**
   Avoid revealing unnecessary subject lines, visible attachments, or routing context.

5.
**Treat providers as data holders**
   Choose providers on architecture and retention, not slogans.

### What does not work as a primary defense

- **A new inbox is not a new identity if recovery data is shared.**
- **Encryption does not hide sender and recipient metadata by itself.**
- **Temporary email is not robust privacy.**
- **Deleting messages from the inbox does not erase provider logs or recipients' copies.**

## Practical labs

### Build an email threat model

```
Account:
Recipient:
Content sensitive:
Metadata sensitive:
Recovery email:
Phone attached:
Provider logs:
Behavioral clues:
```

This makes the email identity surface concrete.

### Separate personas

```
Persona A email:
Persona B email:
Shared recovery:
Shared browser:
Shared device:
Shared contacts:
Allowed to overlap:
```

The result should tell you whether the separation is real.

### Review message metadata

```
To:
From:
Subject:
Attachment names:
Timestamp:
Reply chain:
Provider logs:
```

Metadata often reveals more than the message body.

### Decide if email is the right channel

```
Need message confidentiality:
Need sender anonymity:
Need recipient anonymity:
Need persistence:
Need recovery:
Need third-party storage:
Use email? yes/no
Alternative:
```

The right answer is sometimes "not email."

## Practical examples

- A whistleblower uses a separate mailbox but forgets that recovery info links back to their main identity.
- A contact form uses email and subject lines that reveal sensitive context.
- A provider can still correlate message timing even when content is encrypted.
- A password reset email becomes an identity recovery path.
- A pseudonymous newsletter address stays separate until the same device and browser are reused.

## Related notes

- [[temporary-email-risks|Temporary Email Risks]]
- [[end-to-end-encryption|End-to-End Encryption]]
- [[pgp-encryption-and-signatures|PGP Encryption and Signatures]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[email-and-phone-osint|Email and Phone OSINT]]

### Suggested future atomic notes

- email-alias-strategies
- mail-header-leakage
- recovery-channel-risk

## References

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
