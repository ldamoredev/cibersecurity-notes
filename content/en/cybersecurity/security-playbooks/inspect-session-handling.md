---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Inspect Session Handling

## Goal

Determine whether session identifiers, lifecycle, and cookie behavior are handled safely across login, logout, and privilege transitions.

## Assumptions

- the app uses cookies or token-backed session state
- browser behavior influences risk
- session rotation and invalidation may be incomplete

## Prerequisites

- one or more test accounts
- browser devtools or proxy tooling
- ability to observe cookies and replay requests

## Recon steps

1. Record session state before login.
2. Capture Set-Cookie headers on login and logout.
3. Observe session behavior across password changes, role changes, and inactivity.

## Exploit / test steps

1. Check whether the session identifier changes after login.
2. Check whether logout invalidates server-side state.
3. Replay requests with old cookies after logout.
4. Test whether cookies use `HttpOnly`, `Secure`, and appropriate `SameSite`.
5. Observe whether privileged transitions reuse old session state.

## Validation clues

- same session ID before and after login
- old cookies still work after logout
- cookies lack safe attributes
- session persists unexpectedly across trust transitions

## Mitigation

- rotate sessions after authentication and privilege change
- invalidate server-side sessions properly
- set safe cookie attributes
- keep session IDs out of URLs and logs
- align timeout policy with risk

## Logging / detection

- reused session IDs across multiple auth states
- post-logout reuse of supposedly dead sessions
- suspicious session reuse across IP/device shifts where appropriate

## Related notes

- [[session-management]]
- [[cookies-and-sessions]]
- [[auth-flaws]]
- [[csrf]]

## References

- **Foundational:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
