---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Content Security Policy

## Definition

Content Security Policy (CSP) is a browser security control that tells the browser which sources and execution patterns are allowed for scripts, styles, images, frames, connections, and other resource types.

## Why it matters

CSP is defense-in-depth for XSS and content injection, not a replacement for output encoding or safe templating. A strong policy can reduce exploitability when an injection bug exists, while a weak policy can create false confidence.

## How it works

CSP controls **5 browser decisions**:

1. **Script execution.** Which scripts may load or execute.
2. **Resource loading.** Which origins may provide images, styles, fonts, media, and frames.
3. **Network connections.** Which endpoints JavaScript may connect to.
4. **Embedding.** Who can frame the page and what the page can frame.
5. **Reporting.** Where violations are reported.

Example header:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-random'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'
```

The bug is not absence of CSP alone. The bug is relying on CSP while allowing unsafe sources or inline execution that defeats the policy.

## Techniques / patterns

Attackers test:

- `script-src` weaknesses: `unsafe-inline`, wildcards, broad CDNs, JSONP, upload origins
- missing nonces or reusable nonces
- `object-src`, `base-uri`, and `frame-ancestors` omissions
- bypassable trusted domains
- DOM XSS sinks under policy constraints
- report-only policies mistaken for enforcement

## Variants and bypasses

CSP failure appears in **6 forms**.

### 1. No policy

The browser receives no meaningful execution restrictions.

### 2. Report-only policy

Violations are reported but not blocked.

### 3. Unsafe inline execution

`unsafe-inline`, unsafe hashes, or nonce misuse allows injected scripts.

### 4. Overbroad trusted sources

Wildcards or broad CDNs allow attacker-controlled content from trusted origins.

### 5. Missing structural directives

Missing `base-uri`, `object-src`, or `frame-ancestors` leaves bypass paths open.

### 6. Policy drift

The policy grows permissive over time to support new features.

## Impact

Ordered roughly by severity:

- **XSS exploitability reduction or failure.** Strong CSP can block injected script execution.
- **Clickjacking and framing control.** `frame-ancestors` protects sensitive pages.
- **Data exfiltration reduction.** `connect-src` limits where scripts can send data.
- **Content injection containment.** Resource restrictions reduce malicious loading.
- **Telemetry.** Reports reveal attempted violations and policy gaps.

## Detection and defense

Ordered by effectiveness:

1.
**Fix injection at the source first.**
   Output encoding, safe templating, sanitization, and DOM safety are primary XSS defenses.

2.
**Use nonce-based or hash-based `script-src` without unsafe inline execution.**
   This is the most meaningful CSP control for modern XSS reduction.

3.
**Set restrictive defaults and structural directives.**
   `default-src 'self'`, `object-src 'none'`, `base-uri 'none'`, and `frame-ancestors` reduce bypass space.

4.
**Keep trusted origins narrow.**
   Every allowed origin should be owned, necessary, and unable to host attacker-controlled scripts.

5.
**Deploy with reporting and review violations.**
   Report-only is useful during rollout, but final protection requires enforcement.

### What does not work as a primary defense

- **CSP instead of output encoding.** CSP is defense-in-depth, not the primary XSS fix.
- **`unsafe-inline`.** It usually defeats the point of script restrictions.
- **Broad wildcards.** `*.cdn.example` can include attacker-controlled paths.
- **Report-only mode.** It observes but does not block.

## Practical labs

Use owned apps.

### Inspect policy

```
curl -I https://app.example.test/ | rg -i "content-security-policy"
```

Check whether the policy is enforced or report-only.

### Review risky directives

```
curl -I https://app.example.test/ | rg -i "unsafe-inline|unsafe-eval|\\*|data:"
```

Each risky source should have a justification.

### Test frame protection

```
curl -I https://app.example.test/account | rg -i "frame-ancestors|x-frame-options"
```

Sensitive pages should not be broadly frameable.

## Practical examples

- A site has XSS but a strong nonce-based CSP blocks script execution.
- A policy uses `unsafe-inline`, making it ineffective against many XSS bugs.
- A trusted CDN path allows user-uploaded JavaScript.
- `frame-ancestors` is missing on account settings.
- CSP report-only logs violations but does not block attacks.

## Related notes

- [[xss]]
- [[http-headers]]
- [[cors-misconfiguration]]
- [[open-redirect]]
- [[clickjacking]]

### Suggested future atomic notes

- nonce-based-csp
- csp-bypasses
- trusted-types
- frame-ancestors
- csp-reporting

## References

- **Foundational:** MDN Content Security Policy — https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- **Testing / Lab:** PortSwigger CSP — https://portswigger.net/web-security/cross-site-scripting/content-security-policy
- **Foundational:** OWASP Content Security Policy Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
