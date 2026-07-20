---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# OAuth Security

## Definition

OAuth security is the set of controls that keep OAuth/OIDC authorization flows from leaking authorization codes, tokens, identity claims, or redirect trust to the wrong client or attacker-controlled destination.

## Why it matters

OAuth is not just "login with another provider." It is a redirect-based delegation protocol involving browsers, clients, identity providers, redirect URIs, codes, tokens, scopes, and user identity claims. Small validation gaps can become account takeover or token theft.

This note focuses on web app OAuth/OIDC flaws. [[jwt-attacks]] owns JWT validation details, and [[open-redirect]] owns generic redirector behavior.

## How it works

OAuth authorization-code flow has **6 trust checks**:

1. **Client identity.** The client is registered and allowed to use the flow.
2. **Redirect URI.** The callback exactly matches a registered destination.
3. **State.** The response matches the initiating browser session.
4. **Code exchange.** The authorization code is exchanged by the legitimate client.
5. **Token validation.** ID/access tokens have correct issuer, audience, expiry, and signature.
6. **Account binding.** The returned identity maps safely to a local account.

The bug is usually treating one successful OAuth step as proof that every trust check succeeded.

## Techniques / patterns

Attackers test:

- open redirect chains in registered redirect URIs
- weak or missing `state`
- redirect URI matching by prefix, suffix, or wildcard
- code leakage through referrers, logs, or third-party redirects
- account confusion through email claim trust
- scope overreach and token reuse
- ID token validation gaps

## Variants and bypasses

OAuth flaws appear in **7 forms**.

### 1. Redirect URI bypass

Validation accepts attacker-controlled callback destinations.

### 2. Missing or weak state

CSRF or login confusion becomes possible.

### 3. Open redirect chaining

A trusted redirect URI forwards codes or tokens elsewhere.

### 4. Code interception

Codes leak through logs, referrers, browser history, or malicious clients.

### 5. Token validation failure

The app trusts tokens with wrong issuer, audience, expiry, or signature.

### 6. Account linking confusion

Email or provider identity is bound to the wrong local account.

### 7. Scope overreach

The client requests or receives broader permissions than needed.

## Impact

Ordered roughly by severity:

- **Account takeover.** Codes, tokens, or identity claims bind to attacker control.
- **Token theft.** Redirect or validation bugs leak usable tokens.
- **Login CSRF.** Victims are logged into attacker-linked accounts.
- **Privilege or data overreach.** Broad scopes expose more than the feature needs.
- **Identity confusion.** Wrong issuer/provider/account mapping grants access.

## Detection and defense

Ordered by effectiveness:

1.
**Use exact redirect URI matching.**
   Avoid wildcards, prefix checks, and redirect-chain endpoints.

2.
**Use strong, per-request `state` and validate it server-side.**
   `state` binds the browser session to the OAuth response.

3.
**Use authorization code with PKCE for public clients.**
   PKCE reduces code interception risk, especially for SPAs and mobile clients.

4.
**Validate tokens fully.**
   Check signature, issuer, audience, expiry, nonce where relevant, and required claims.

5.
**Bind accounts using stable provider subject IDs.**
   Do not rely only on mutable or unverified email claims.

6.
**Request least-privilege scopes.**
   Scopes should match the feature, not provider defaults.

### What does not work as a primary defense

- **Wildcard redirect URIs.** They make redirect trust too broad.
- **Open redirectors as callbacks.** Exact callback registration is defeated by forwarding.
- **Email-only account binding.** Emails can be unverified, changed, or provider-dependent.
- **Decoding ID tokens without validation.** Token structure is not proof of trust.

## Practical labs

Use a local OAuth lab or owned integration.

### Inventory OAuth configuration

```
client_id | redirect_uri | scopes | public/confidential | PKCE | owner
```

Exact redirect URIs and owner fields matter.

### Test redirect URI strictness

```
curl -i 'https://idp.example.test/auth?client_id=CLIENT&redirect_uri=https://app.example.test.evil.example/callback'
```

The provider should reject non-exact destinations.

### Search for OAuth callbacks and state handling

```
rg -n "redirect_uri|client_id|state|nonce|code_verifier|oauth|oidc" src config
```

Review whether state, nonce, and token validation are enforced.

## Practical examples

- A redirect URI prefix check accepts `https://app.example.test.evil.example`.
- A registered callback is an open redirect that forwards the code.
- OAuth login lacks `state`, enabling login CSRF.
- ID tokens are decoded but not validated.
- Local accounts are linked by email without checking provider subject.

## Related notes

- [[open-redirect]]
- [[auth-flaws]]
- [[session-management]]
- [[jwt-attacks|JWT Attacks]]
- [[token-lifecycle|Token Lifecycle]]

### Suggested future atomic notes

- oauth-redirect-uri-bypass
- oauth-state-parameter
- pkce
- oidc-id-token-validation
- account-linking-flaws

## References

- **Foundational:** RFC 9700 OAuth 2.0 Security Best Current Practice — https://datatracker.ietf.org/doc/html/rfc9700
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
