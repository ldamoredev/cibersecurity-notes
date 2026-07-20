---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Session Management

## Definition

Session management is the set of mechanisms an application uses to maintain authenticated state across requests. This includes session creation, rotation, expiration, invalidation, and how session identifiers are transported and protected.

## Why it matters

Even when authentication is correct, weak session management can undermine the entire security model. Sessions sit at the intersection of browser behavior, cookies, auth logic, and server-side trust.

This note is about maintaining authenticated state safely after identity has been established. [[auth-flaws]] covers login and identity proof failures, while [[jwt-attacks|JWT Attacks]] covers token-specific state and validation failures.

## Attacker perspective

Attackers look for:
- predictable or reusable session identifiers
- missing rotation after login or privilege change
- weak logout behavior
- fixation opportunities
- cookies with unsafe attributes
- session leakage through URLs or logs

## Defender perspective

Defenders should:
- rotate session identifiers at meaningful trust transitions
- expire sessions appropriately
- invalidate server-side state correctly
- keep session identifiers out of URLs
- apply secure cookie attributes and consistent server-side checks

## Practical examples

- A user logs in but keeps the same session identifier from before authentication.
- Logout clears the browser cookie but leaves the server-side session valid.
- Sessions survive password changes or role transitions without revalidation.

## Related notes

- [[cookies-and-sessions]]
- [[auth-flaws]]
- [[jwt-attacks|JWT Attacks]]
- [[csrf]]
- [[xss]]
- [[inspect-session-handling|Inspect Session Handling]]

## References

- **Foundational:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
