---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Evilginx and Reverse Proxy Phishing

## Definition

Reverse-proxy phishing is an adversary-in-the-middle pattern where a phishing site proxies the real identity provider or application, relays the victim's login flow, and attempts to capture reusable credentials, session cookies, or relayable MFA outputs.

## Why it matters

Classic phishing copied a login page. Reverse-proxy phishing mediates the real page. That makes the experience more convincing and can defeat many MFA methods that rely on user-entered OTPs or approving a prompt without origin binding.

This note uses Evilginx as the recognizable public name for the pattern, but keeps the framing defensive. The learning goal is to understand the mechanism, detection signals, and controls that make this class less effective.

## How it works

Reverse-proxy phishing has **5 moving parts**:

1.
**Lookalike entry point**
   The victim lands on an attacker-controlled domain through email, chat, QR code, ad, or redirect.

2.
**Transparent proxy**
   The phishing server requests the real login page and relays content between victim and legitimate service.

3.
**Credential and MFA relay**
   Passwords, OTPs, push approvals, or other relayable factors are submitted through the proxy to the real service.

4.
**Session capture or continuation**
   If the legitimate service issues session cookies or tokens that can be reused by the proxy operator, the account may be accessed without knowing the password again.

5.
**Cloaking and filtering**
   The infrastructure may hide from scanners, security vendors, cloud networks, and non-target geographies.

Safe conceptual flow:

```
victim browser -> attacker-controlled proxy -> real identity provider
      credentials and relayable MFA pass through the middle
      session artifacts may be observed by the middle
```

The bug is not that the real service is cloned visually. The bug is that the authentication ceremony can be relayed through an impostor origin.

## Techniques / patterns

- Identify whether the suspicious page is a static clone, a redirect chain, or an active reverse proxy.
- Compare URL origin, TLS certificate, DNS, hosting ASN, and page behavior against the legitimate service.
- Look for session anomalies: impossible travel, new device, new ASN, suspicious user-agent consistency, or login followed by unusual token/session use.
- Watch for MFA prompts that originate from a login the user did not intentionally start.
- Preserve original links and redirect chains from user reports; copied browser screenshots are not enough.
- Treat cloaking as part of the infrastructure pattern, not a separate curiosity.

## Variants and bypasses

Reverse-proxy phishing appears in **5 defensive-relevant variants**.

### 1. Password-only relay

The proxy captures and forwards username/password. Basic MFA would usually reduce this, but password reuse and weak recovery flows can still make it harmful.

### 2. OTP relay

The proxy prompts for TOTP/SMS/email codes and submits them immediately. OTP proves possession of a factor but is not bound to the legitimate origin.

### 3. Push fatigue or approval relay

The victim approves a push notification for a session they did not understand. Number matching reduces blind approval but does not fully solve social engineering.

### 4. Session-cookie capture

The proxy observes cookies or session artifacts and attempts to reuse them. Cookie scope, device binding, continuous access evaluation, and risk controls affect whether reuse works.

### 5. Phishing-resistant authentication failure path

When WebAuthn/passkeys are properly deployed, the authentication output is bound to the legitimate relying-party origin. The impostor origin cannot obtain a valid assertion for the real origin, so the relay breaks.

## Impact

- **Account takeover.** Reusable sessions or credentials give direct access.
- **MFA bypass perception.** The user “used MFA,” but the factor was relayable.
- **Identity-provider compromise.** SSO access can fan out to many apps.
- **Mail and collaboration abuse.** Attackers can read mail, set forwarding rules, harvest contacts, or send internal phishing.
- **Fraud and persistence.** New devices, OAuth grants, recovery changes, and helpdesk abuse can extend access.

## Detection and defense

Ordered by effectiveness:

1.
**Adopt phishing-resistant authentication**
   WebAuthn/passkeys and other cryptographic, origin-bound authenticators break the central relay property. A code typed into the wrong origin can be relayed; an origin-bound assertion cannot.

2.
**Bind sessions to device and risk context**
   Continuous access evaluation, token protection, device compliance, and reauthentication for risky changes reduce the value of captured cookies.

3.
**Detect AiTM login patterns**
   Correlate login IP/ASN, user-agent, device ID, impossible travel, new session creation, and immediate post-login actions. Reverse proxies often create network and timing patterns that differ from the user's normal path.

4.
**Harden recovery and enrollment paths**
   Attackers frequently pivot from one relayed login into MFA reset, device registration, OAuth grants, or mailbox rules. Protect these flows more strongly than ordinary sign-in.

5.
**Train on origin and intent, not just page appearance**
   Users should understand that a real-looking page is not enough. The origin, the login they initiated, and unexpected MFA prompts matter.

6.
**Preserve user-report artifacts**
   Original URL, email headers, redirect chain, timestamp, and device/network context are essential because cloaking may hide the page from responders.

### What does not work as a primary defense

- **OTP MFA alone.** OTPs can be relayed through an impostor origin.
- **Telling users to look for HTTPS.** Phishing domains can have valid TLS certificates.
- **Brand-perfect login pages.** Real content can be proxied, so visual familiarity is not proof.
- **One-time blocklists.** Domains, infrastructure, and kits rotate quickly.
- **Only scanning from security-vendor networks.** Cloaking can hide the real page from those paths.

## Practical labs

### Draw the relay boundary

```
legitimate origin:
impostor origin:
credential entered at:
MFA factor type:
session artifact issued by:
session artifact visible to:
origin binding present:
```

This separates visual phishing from relayable authentication.

### Review an identity log safely

```
user:
login time:
source IP / ASN:
device ID:
user-agent:
MFA method:
session ID:
post-login actions:
risk events:
```

Use real logs only in authorized environments; redact user and token details.

### Preserve a suspicious URL report

```
original message:
full URL:
redirect chain:
final host:
TLS issuer:
DNS answers:
visible page:
user action taken:
MFA prompt observed:
```

The original path is often the evidence; screenshots alone are weak.

### Compare MFA methods by relayability

```
method | typed/shared output? | origin-bound? | phishing-resistant? | notes
password | yes | no | no |
SMS OTP  | yes | no | no |
TOTP     | yes | no | no |
push     | approval | weak/no | usually no |
WebAuthn | no | yes | yes |
```

This table makes the control difference visible.

### Hunt for post-login pivots

```
after suspicious login, check:
- new MFA device
- password reset
- mailbox forwarding rule
- OAuth app consent
- API token creation
- unusual file/mail access
```

Reverse-proxy phishing often becomes dangerous after the first session succeeds.

## Practical examples

- A user enters a TOTP into a proxied login page; the proxy submits it before expiration.
- A valid TLS phishing domain relays the real identity provider, so visual page inspection fails.
- A suspicious login is followed by a new inbox forwarding rule and OAuth consent grant.
- A passkey login fails on the impostor domain because the authenticator is scoped to the legitimate relying party.
- A takedown analyst sees a harmless redirect from a cloud IP, while the victim path shows the login proxy.

## Related notes

- [[mfa-phishing-resistance|MFA Phishing Resistance]]
- [[auth-flaws|Auth Flaws]]
- [[session-management|Session Management]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[bot-detection-signals|Bot Detection Signals]]

### Suggested future atomic notes

- phishing-detection-signals
- credential-harvesting-defense
- passkeys-and-webauthn
- session-token-protection
- oauth-consent-phishing

## References

- **Research / Deep Dive:** Microsoft: Identifying AiTM phishing attacks through third-party network detection — https://techcommunity.microsoft.com/blog/microsoftsentinelblog/identifying-adversary-in-the-middle-aitm-phishing-attacks-through-3rd-party-netw/3991358
- **Mitigation:** CISA: More than a Password / MFA — https://www.cisa.gov/mfa
- **Foundational:** FIDO Alliance: Passkeys — https://fidoalliance.org/passkeys/
