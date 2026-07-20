---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# MFA Phishing Resistance

## Definition

MFA phishing resistance is the property that an authentication method cannot produce a reusable secret or valid authentication result for an impostor origin, even if the user is tricked into interacting with that impostor.

## Why it matters

MFA is not one thing. SMS codes, TOTP apps, push approvals, hardware OTP tokens, passkeys, WebAuthn, smart cards, and device-bound credentials behave differently under phishing pressure.

The old mirror project's injected 6-digit modal is the perfect teaching hook: a code that a user types into a page can be relayed. A properly configured origin-bound cryptographic authenticator cannot be replayed to a different relying party.

## How it works

Use the **4-question MFA resistance test**:

1.
**Is there a user-readable output?**
   If a code appears and the user can type it, a phishing proxy can ask for it.

2.
**Is the output bound to the legitimate origin?**
   If the result is not tied to the real domain or TLS channel, it can often be relayed.

3.
**Does the authenticator prove intent?**
   The user should knowingly approve the specific login, not just respond to a generic prompt.

4.
**Can the resulting session be reused elsewhere?**
   Even strong MFA can be undermined if session cookies or recovery paths are weak.

Comparison:

```
TOTP:
  user sees 123456 -> types into impostor page -> proxy relays to real service

WebAuthn/passkey:
  browser asks authenticator for example.com -> impostor.test cannot obtain
  a valid assertion for example.com
```

The bug is not “MFA failed.” The bug is choosing an MFA method whose proof can be relayed through the wrong origin.

## Techniques / patterns

- Inventory MFA methods by account class: users, admins, service accounts, contractors, recovery flows.
- Mark each method as phishable, relay-resistant, phishing-resistant, or unknown.
- Check whether high-risk flows use stronger authentication than ordinary sign-in: MFA enrollment, password reset, device registration, OAuth consent, API token creation.
- Distinguish number matching from origin binding. Number matching improves push intent but does not make a method equivalent to WebAuthn.
- Treat recovery and helpdesk workflows as part of authentication. Attackers often bypass strong sign-in through weak reset paths.
- Log MFA method, device, session, and post-authentication action together.

## Variants and bypasses

MFA methods fall into **5 useful classes**.

### 1. Password plus SMS or email OTP

Better than password alone, but codes are typed into a page and can be relayed or socially engineered.

### 2. TOTP app

Avoids telecom risks but remains phishable because the user reads and enters a time-based code.

### 3. Push approval

Reduces typing but can be abused through prompt bombing or misleading context. Number matching helps, but the user can still be tricked.

### 4. Hardware or app OTP token

May be stronger operationally, but if it emits a code the user types into a page, the output is still relayable.

### 5. WebAuthn / passkeys / FIDO

Uses public-key cryptography and relying-party binding. The authenticator does not hand the user a reusable code and does not produce a valid assertion for the wrong origin.

## Impact

- **Reduced phishing blast radius.** Origin-bound MFA can stop proxy phishing where OTP-based MFA cannot.
- **Admin account hardening.** Privileged users benefit most from phishing-resistant methods.
- **Lower credential-stuffing impact.** Password reuse becomes less decisive when authentication requires a non-relayable factor.
- **Recovery-flow pressure.** Attackers shift to helpdesk, device enrollment, token theft, OAuth consent, and session hijacking.
- **Migration complexity.** Legacy apps, shared accounts, contractors, and unsupported devices can slow adoption.

## Detection and defense

Ordered by effectiveness:

1.
**Require phishing-resistant MFA for high-risk accounts**
   Admins, developers, finance users, identity admins, and support staff should use WebAuthn/passkeys, smart cards, or equivalent cryptographic authenticators first.

2.
**Move broad user populations toward passkeys/WebAuthn**
   Phishing resistance scales best when it becomes the default path, not a special admin exception.

3.
**Protect enrollment and recovery**
   Strong sign-in is undermined if attackers can register a new factor, reset MFA, or recover an account through weak helpdesk proofing.

4.
**Use number matching and context where WebAuthn is not yet possible**
   This reduces accidental push approvals and MFA fatigue, but should be treated as an interim improvement.

5.
**Bind sessions and reauthenticate risky actions**
   Device-bound sessions, token protection, and step-up authentication reduce damage when a session is suspicious.

6.
**Monitor by MFA method**
   Track which methods are used, where failures cluster, and whether risky actions follow weaker methods.

### What does not work as a primary defense

- **Saying “we have MFA” without naming the method.** MFA strength depends on method and workflow.
- **SMS/TOTP as phishing-resistant controls.** They are useful but relayable.
- **Push approval without context.** Users can approve prompts they did not initiate.
- **HTTPS indicators.** A phishing domain can have valid TLS.
- **Training alone.** Training helps, but phishing resistance should not rely only on user vigilance.

## Practical labs

### Classify MFA methods

```
method | user-readable output | origin-bound | replay-resistant | phishing-resistant | current population
SMS    | yes                  | no           | partial          | no                 |
TOTP   | yes                  | no           | time-limited     | no                 |
Push   | no/code varies       | weak/no      | partial          | usually no         |
WebAuthn/passkey | no         | yes          | yes              | yes                |
```

This inventory turns vague MFA posture into an actionable migration map.

### Map high-risk flows

```
flow | current auth | step-up required | phishing-resistant? | owner | migration gap
admin login |
MFA reset |
device enrollment |
OAuth consent |
API token creation |
payment change |
```

Attackers target the weakest flow that can change authentication state.

### Review suspicious MFA events

```
user:
method:
prompt time:
login initiated by user?
source ASN:
device:
number matching used:
post-login action:
```

This distinguishes ordinary MFA friction from relay or fatigue patterns.

### Test origin binding conceptually

```
legitimate RP ID: example.com
impostor origin: examp1e-login.test
method: WebAuthn/passkey
expected result: authenticator cannot produce valid assertion for example.com from impostor origin
```

This is the core reason passkeys resist reverse-proxy phishing.

### Plan a migration ring

```
ring 1: identity admins
ring 2: developers and finance
ring 3: helpdesk and executives
ring 4: all employees
ring 5: customers / external users
fallback policy:
recovery policy:
```

Phishing-resistant MFA works best as a staged program, not a one-day switch.

## Practical examples

- A TOTP code entered into a fake modal is relayed before it expires.
- A push prompt is approved because the user expects a login, but the login was initiated by an attacker.
- Number matching blocks blind push approval but still depends on the user understanding the context.
- A passkey fails on a lookalike domain because the relying-party identity does not match.
- An attacker who cannot phish WebAuthn pivots to helpdesk reset or new-device enrollment.

## Related notes

- [[evilginx-and-reverse-proxy-phishing|Evilginx and Reverse Proxy Phishing]]
- [[auth-flaws|Auth Flaws]]
- [[session-management|Session Management]]
- [[token-lifecycle|Token Lifecycle]]
- [[account-correlation|Account Correlation]]

### Suggested future atomic notes

- passkeys-and-webauthn
- mfa-fatigue-attacks
- helpdesk-social-engineering
- session-token-protection
- oauth-consent-phishing

## References

- **Foundational:** NIST SP 800-63B: Authentication and Lifecycle Management — https://pages.nist.gov/800-63-4/sp800-63b.html
- **Mitigation:** CISA: More than a Password / MFA — https://www.cisa.gov/mfa
- **Foundational:** FIDO Alliance: Passkeys — https://fidoalliance.org/passkeys/
