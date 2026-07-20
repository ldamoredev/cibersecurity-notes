---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Account Correlation

## Definition

Account correlation is the process of linking separate activities or personas through shared accounts, recovery data, identifiers, devices, or repeated usage patterns.

## Why it matters

Many privacy workflows fail because the same account data appears in multiple places. The same email, phone number, password reset channel, payment method, login device, or social graph can bridge an otherwise separate identity.

## How it works

Use the 6 correlation anchors:

1.
**Email address**
   Often the strongest account-level identifier.

2.
**Phone number**
   Durable and commonly reused.

3.
**Recovery path**
   Reset channels can reconnect identities later.

4.
**Payment identity**
   Billing data often ties accounts together.

5.
**Device and browser**
   Login device, cookies, and fingerprints correlate use.

6.
**Behavior and contacts**
   Usage patterns and social graph can bridge personas.

The bug is not having accounts. The bug is reusing enough of them that the accounts become the same identity.

## Techniques / patterns

- Separate email, recovery, and payment where unlinkability matters.
- Avoid logging into identifying accounts on anonymous workflows.
- Keep browser profiles and devices separate.
- Re-evaluate third-party login links such as "Sign in with X."
- Treat contacts and address books as identity data.
- Consider support and recovery as part of the identity model.

## Variants and bypasses

Use the 6 correlation patterns:

### 1. Direct identity reuse

The same email or username appears across personas.

### 2. Recovery linkage

Different accounts are linked through the same recovery email or phone number.

### 3. Social login linkage

OAuth or federated login creates a bridge to a primary identity provider.

### 4. Payment linkage

Cards, invoices, and app-store subscriptions reveal ownership.

### 5. Device linkage

The same device or browser profile is used for both personas.

### 6. Behavioral linkage

Timing, contacts, and posting style connect accounts without a direct identifier.

## Impact

- Separate personas stop being separate.
- Pseudonymity weakens even when transport privacy is strong.
- Recovery and support requests can reveal the bridge.
- The account becomes a durable identity anchor.
- Services can cross-link profiles internally even when the user thinks they are isolated.

## Detection and defense

Ordered by effectiveness:

1.
**Map the bridges before creating the account**
   Email, recovery, payment, and device all need to be treated as identity paths.

2.
**Separate recovery channels**
   A recovery email or phone number can destroy a carefully built separation.

3.
**Avoid social login for separated personas**
   A federated identity provider can unify accounts quickly.

4.
**Use different devices or profiles for different identities**
   Shared state is a bridge.

5.
**Assume the service can correlate internally**
   Even if the user stays separate, the provider may still infer the link.

### What does not work as a primary defense

- **Changing the display name does not change the account identity.**
- **A new username is not a new persona if recovery data is shared.**
- **Logging out is not separation if the browser profile remains the same.**
- **Deleting one account does not erase all internal correlation.**

## Practical labs

### Build an account bridge map

```
Persona A:
Persona B:
Shared email:
Shared phone:
Shared recovery:
Shared payment:
Shared device:
Shared browser:
Shared contacts:
```

If any rows are shared, the personas are not fully separated.

### Review login paths

```
Account:
Password login:
Social login:
Recovery email:
Recovery phone:
2FA device:
Shared with another persona:
```

The login path is often the bridge.

### Compare provider linkage

```
Service A:
Service B:
Same provider?
Shared analytics?
Shared payment?
Shared device?
Possible internal correlation? yes/no
```

This models provider-side linkage risk.

### Decide if an account is safe to reuse

```
Reuse allowed?
Identity-sensitive?
Recovery reused?
Payment reused?
Device reused?
Browser reused?
```

The answer should usually be no for separated personas.

## Practical examples

- A pseudonymous account is linked because the same recovery phone number is attached.
- A social login bridges a private workflow back to a personal Google or Apple identity.
- Two personas share a browser profile and become correlated by cookies and login history.
- The same credit card and email appear on separate services.
- A support request reveals enough context to tie two personas together.

## Related notes

- [[deanonymization-failures|Deanonymization Failures]]
- [[private-email-threat-models|Private Email Threat Models]]
- [[temporary-email-risks|Temporary Email Risks]]
- [[browser-fingerprinting|Browser Fingerprinting]]
- [[social-media-osint|Social Media OSINT]]

### Suggested future atomic notes

- oauth-account-linkage
- recovery-path-isolation
- social-login-risk

## References

- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
