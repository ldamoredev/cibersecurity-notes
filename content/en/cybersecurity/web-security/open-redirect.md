---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Open Redirect

## Definition

Open redirect occurs when an application redirects users to attacker-controlled destinations based on untrusted input without strict destination validation.

## Why it matters

Open redirects often look low impact alone, but they become powerful when chained with phishing, OAuth flows, login redirects, token leakage, CSP bypasses, or trusted-domain allowlists. The trusted domain performs the redirect, so users and systems may treat the destination as legitimate.

## How it works

Open redirect has **3 parts**:

1. **Redirect parameter.** `next`, `url`, `redirect`, `returnTo`, `continue`, or similar.
2. **Server/client redirect behavior.** HTTP `Location`, JavaScript assignment, meta refresh, or framework routing.
3. **Weak validation.** The application accepts arbitrary or bypassable destinations.

Payload-shaped example:

```
GET /login?next=https://evil.example HTTP/1.1
Host: app.example.test
```

The bug is not redirecting after login. The bug is letting untrusted input choose a destination outside the allowed trust boundary.

## Techniques / patterns

Attackers test:

- redirect parameters in login, logout, SSO, password reset, and invite flows
- absolute URLs, protocol-relative URLs, and encoded URLs
- path confusion: `//evil.example`, `/\evil.example`, `%2f%2fevil.example`
- userinfo tricks: `https://app.example.test@evil.example`
- subdomain and suffix confusion
- OAuth redirect and callback chains

## Variants and bypasses

Open redirects appear in **5 contexts**.

### 1. Login return redirect

The app redirects after authentication to an arbitrary destination.

### 2. OAuth redirect chain

A trusted redirect endpoint is used to bypass OAuth redirect URI restrictions.

### 3. Client-side redirect

JavaScript reads a URL parameter and navigates the browser.

### 4. Domain validation bypass

Suffix, substring, userinfo, encoding, or scheme tricks bypass allowlists.

### 5. Token leakage redirect

Tokens or codes in URLs are forwarded to attacker-controlled destinations.

## Impact

Ordered roughly by severity:

- **OAuth or SSO compromise chain.** Redirects bypass strict callback rules.
- **Credential phishing.** Trusted domains lend credibility to phishing links.
- **Token or code leakage.** Sensitive URL fragments or query parameters leak.
- **Access-control bypass chains.** Redirect behavior interacts with allowlists or SSRF filters.
- **Brand abuse.** Trusted links send users to malicious content.

## Detection and defense

Ordered by effectiveness:

1.
**Use server-side destination IDs instead of raw URLs.**
   Map `next=dashboard` to a known internal route rather than accepting arbitrary URLs.

2.
**Allow only relative paths when possible.**
   Most post-login redirects do not need external destinations.

3.
**Validate destinations with URL parsers and exact allowlists.**
   Compare canonical scheme, host, and path; avoid substring checks.

4.
**Keep OAuth redirect URIs exact and avoid redirect-chain endpoints.**
   OAuth clients should not allow trusted open redirectors as callback paths.

5.
**Do not place secrets in URLs.**
   This reduces damage if redirects or referrers misbehave.

### What does not work as a primary defense

- **Substring allowlists.** `trusted.com.evil.example` is not trusted.
- **Checking only URL starts-with.** Encoding and userinfo can bypass naive checks.
- **User confirmation pages alone.** They reduce phishing but do not fix unsafe redirect logic.
- **Assuming same-domain redirectors are harmless.** Chains matter.

## Practical labs

Use owned apps or labs.

### Find redirect parameters

```
rg -n "redirect|returnTo|next|continue|callback|url" src routes public
```

Review where user-controlled destinations are accepted.

### Test absolute destination

```
curl -i 'https://app.example.test/login?next=https://example.org'
```

Check whether `Location` points outside the intended domain.

### Test parser confusion

```
curl -i 'https://app.example.test/login?next=//example.org'
curl -i 'https://app.example.test/login?next=https://app.example.test@example.org'
```

Use a controlled destination in labs.

## Practical examples

- Login accepts `next=https://evil.example`.
- Password reset redirects to a user-controlled URL after completion.
- OAuth callback allowlists a path that is itself an open redirect.
- JavaScript redirects based on `location.hash`.
- A support link uses a redirector that can target arbitrary domains.

## Related notes

- [[oauth-security]]
- [[auth-flaws]]
- [[session-management]]
- [[ssrf]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]

### Suggested future atomic notes

- oauth-redirect-uri-bypass
- client-side-open-redirect
- url-parser-confusion
- phishing-link-hardening
- safe-return-url-design

## References

- **Foundational:** OWASP Unvalidated Redirects and Forwards Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
