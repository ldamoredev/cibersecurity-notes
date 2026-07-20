---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Email and Phone OSINT

## Definition

Email and phone OSINT is the collection and validation of public email addresses, phone numbers, contact patterns, and account-exposure clues for a scoped security or investigation purpose. It is the connective tissue between [[breach-and-leak-intelligence|breach intelligence]], [[social-media-osint|social-media OSINT]], and [[company-osint|company OSINT]] — most account-takeover and social-engineering chains pivot on a contact identifier.

## Why it matters

Emails and phone numbers connect people, accounts, domains, breach exposure, support flows, and social-engineering risk. They are the single most reused identifier across services, which is why credential-stuffing and account-recovery abuse depend on them.

They are also **personal data** under most data-protection regimes, even when the data is technically public. Collection should be minimal, scoped, evidence-driven, and tied to a clear purpose. The default is "what is the smallest contact dataset that answers the question," not "what contact data can I find."

The defensive case for email/phone OSINT is strongest in three directions:
- **Security contact discovery** — finding the right person to receive a vulnerability disclosure.
- **Domain-wide breach exposure review** — checking whether owned-domain emails appear in breach indexes.
- **Account-recovery hardening** — confirming that public phone/email exposure is not enough to recover accounts.

## How it works

Email/phone OSINT processes **5 signal classes**. A scoped investigation usually answers one or two.

1. **Contact discovery.** Public emails, phone numbers, support addresses, and forms. Sources: official contact pages, security.txt, support portals, public regulatory filings.
2. **Pattern inference.** Naming formats such as `first.last@example.test` or `flast@example.test`. Sources: public PDFs, conference speaker bios, public commit emails. **Pattern inference, not address harvesting** — the goal is the format, not a list of every employee.
3. **Account exposure.** Breach or reuse indicators tied to identifiers. Handled in [[breach-and-leak-intelligence]] with the rotation-first discipline.
4. **Role mapping.** Security, support, sales, engineering, and executive functional contacts. Sources: official contact pages, security.txt, vendor CRM aliases.
5. **Verification.** Confirming whether a contact is current, official, and relevant — without intrusive probes (no login attempts, no password resets, no SMTP verification dialogs).

The bug is **treating contact data as harmless**. Contact data is the most common bridge between OSINT and account-takeover risk.

A worked example, defensive use:

```
Question:    Does Example Corp publish a clear security disclosure contact?
Sources:     example.com/.well-known/security.txt, example.com/security, security@example.com header.
Findings:    security.txt present at /.well-known/security.txt; lists security@example.com + PGP key.
Action:      none on the target. Output is a yes/no with the discovered channel.
Stored:      URL of security.txt + retrieved channel. No employee personal data collected.
```

The investigation answered the question without touching anyone's personal contact data.

## Techniques / patterns

The discipline is "lightest source that answers the question."

- **Official contact pages and `security.txt`** for organizational contact discovery.
- **Public documents and PDFs** for pattern inference (author metadata, footer signatures).
- **Git commits, package registries, repositories** for technical contact patterns (commit emails, maintainer fields).
- **Breach notification services** for owned/authorized domains only, via domain APIs, not bulk email lists.
- **Social/professional profiles** when the question requires role corroboration (with the [[social-media-osint|minimization rules]]).
- **Phone number formats on official pages** for impersonation detection.
- **Support and vendor contact flows** for role mapping and impersonation review.

## Variants and bypasses

Email/phone OSINT clusters into **5 practical uses**. Each implies a different evidence and minimization standard.

### 1. Security contact discovery

Find official reporting or incident contacts. Lowest sensitivity; the contact exists explicitly to be found. Evidence: `security.txt`, dedicated security page, or canonical `security@` alias. Action: hand to disclosure workflow.

### 2. Domain email pattern mapping

Infer likely format (`first.last@`, `flast@`, `first@`) without validating private accounts intrusively. Evidence: 3+ public examples from independent sources. **No SMTP probing, no password-reset probes, no validation requests** — the format is the deliverable, not a list of valid addresses.

### 3. Breach exposure review

Check whether owned or authorized emails appear in breach indexes. Use [[breach-and-leak-intelligence]] discipline: domain-API, not bulk email harvesting; rotate-first, investigate-second; never store raw passwords.

### 4. Support-flow mapping

Understand public support numbers, escalation paths, and the impersonation surface. Useful for detecting fake support phone numbers in search results that redirect victims to scammers.

### 5. Personal-data boundary review

Decide what **not** to collect or retain. The deliverable is the minimization decision itself, recorded in the action ledger. Sometimes the right output of email/phone OSINT is "we chose not to collect this."

## Impact

Ordered roughly by severity:

- **Credential-stuffing risk.** Emails plus breach signals enable automated account-takeover at scale.
- **Social-engineering risk.** Roles and contact paths sharpen targeted phishing and pretexting.
- **Account recovery risk.** Phone/email exposure may be enough to complete recovery flows on services with weak verification.
- **Security reporting improvement.** Discoverable security contacts reduce time-to-disclosure for good-faith reporters.
- **Impersonation detection.** Fake phone or support contact data can be found and reported to platforms.

## Detection and defense

Defenses prioritize **minimization, official channels, and account-recovery hardening**.

1.
**Minimize personal contact collection.**
   Collect only what the investigation needs. Avoid bulk personal email lists; the minimization decision is the deliverable, not a constraint on it.

2.
**Publish clear security and support contacts.**
   Official channels (`security.txt`, dedicated security page, support phone listing) reduce ambiguity for good-faith reporters and reduce the impersonation surface.

3.
**Monitor breach exposure for owned domains.**
   Use [[breach-and-leak-intelligence|reputable services]] with the rotation-first discipline. Avoid handling raw credential dumps.

4.
**Protect account recovery flows.**
   Public phone/email data should not be enough to recover accounts. SMS-only 2FA, knowledge-based recovery, and email-only recovery all assume the identifier is private; in OSINT terms, none of them are.

5.
**Train staff on contact-data exposure.**
   Public contact details are useful for sales and support, but should not reveal unnecessary internal structure (org charts, escalation paths, private direct dials for executives).

### What does not work as a primary defense

- **Assuming business emails are not personal data.** They still identify natural persons under most regimes.
- **Verifying emails by intrusive login/reset attempts.** That crosses into active testing and is no longer OSINT.
- **Collecting raw breach dumps.** Use safe indicators and response workflows, not stored credentials.
- **Relying on obscurity for security contacts.** Good-faith reporters need a clear, advertised path; obscurity helps only attackers.
- **Treating SMTP "no such user" responses as confidential.** Many servers leak existence; relying on this is a fragile control.

## Practical labs

Use your own domain, an authorized organization, or your own personal accounts. Never query third-party identifiers without authorization.

### Find official security and support contacts

```
# Canonical security.txt location (RFC 9116)
curl -s https://example.test/.well-known/security.txt

# Common alternates
curl -s https://example.test/security.txt
curl -s https://example.test/security
```

```
site:example.test "security contact"
site:example.test "responsible disclosure"
```

Record the canonical channel only. This is low-sensitivity, high-value defensive work.

### Build a minimal contact evidence table

```
contact                | source                  | role     | sensitivity | action            | retention
security@example.test  | /.well-known/security.txt | sec     | low         | use for disclosure | indefinite (public)
support@example.test   | /support page            | support  | low         | none              | indefinite (public)
hire-eng@example.test  | LinkedIn job post        | hiring   | low         | none              | end of investigation
```

Avoid columns like "personal phone" unless the question explicitly justifies them.

### Infer email format without intrusive probing

```
Source 1: PDF author metadata           → "John Smith <john.smith@example.com>"
Source 2: Public commit email           → "j.smith@example.com" (different format!)
Source 3: Conference speaker bio        → "smith@example.com" (third format!)
Decision: format is uncertain; report multiple patterns rather than one.
```

Never SMTP-probe to "validate" the format — that is active testing, not OSINT.

### Check authorized breach exposure (domain-level)

```
# HIBP domain search requires verified ownership; returns counts, not plaintext.
curl -s -H "hibp-api-key: $HIBP_API_KEY" -H "user-agent: example-sec-eng" \
  "https://haveibeenpwned.com/api/v3/breaches?domain=example.com"
```

Record breach name, date, exposed data classes, and remediation action — not raw credentials.

### Audit account-recovery exposure

```
service   | identifier        | recovery method            | OSINT-discoverable? | mitigation
SaaS A    | john@example.com  | email-only                 | yes                 | enforce TOTP recovery
SaaS B    | +1-555-0142       | SMS                        | yes                 | enforce TOTP, disable SMS
SaaS C    | john@example.com  | email + KBA                | partially           | strengthen KBA questions
```

The audit shows where public identifier exposure converts directly into account-takeover risk.

## Practical examples

- Public PDFs reveal employee email formats via author metadata.
- Security-contact discovery finds `security@example.test` plus a published PGP key, enabling disclosure.
- Breach results indicate old employee emails in third-party leaks, triggering MFA enforcement scoped to those accounts.
- A fake support phone number appears in search results, redirecting users to a scammer; defensive OSINT catches it.
- Public Git commits expose personal email addresses tied to company repositories, suggesting cleanup of `git config user.email` defaults.
- A SaaS account-recovery audit reveals SMS-only recovery on a service holding sensitive data, triggering a 2FA-method change.

## Related notes

- [[breach-and-leak-intelligence]]
- [[social-media-osint]]
- [[company-osint]]
- [[osint-triage]]
- [[auth-flaws|Auth Flaws]]
- [[broken-authentication|Broken Authentication]]

### Suggested future atomic notes

- security-txt
- email-pattern-inference
- phone-number-osint
- account-recovery-osint-risk
- contact-data-minimization
- security-contact-discoverability

## References

- **Foundational:** OSINT Framework — https://osintframework.com/
- **Official Tool Docs:** Have I Been Pwned API documentation — https://haveibeenpwned.com/API/v3
- **Ethics / Safety:** EFF Surveillance Self-Defense — https://ssd.eff.org/
