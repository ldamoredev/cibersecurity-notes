---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cross-Site Request Forgery (CSRF)

## Definition

CSRF happens when a victim’s browser is induced to send an authenticated request that the target application accepts as legitimate, even though the user did not intend the action.

## Why it matters

CSRF is one of the clearest examples of how browser behavior itself can become part of the vulnerability. The user’s browser carries cookies, session state, and other ambient authority automatically, which means the browser can be tricked into acting as an unwilling deputy.

CSRF remains important because teams often misunderstand:
- which credentials the browser sends automatically
- what SameSite actually solves
- the difference between CORS and CSRF
- why state-changing routes need intent validation

## How it works

The mechanism is:

1. the victim is authenticated to the target application
2. the browser automatically includes credentials in a request
3. the attacker causes the victim browser to send a request to the target
4. the application accepts the request without sufficiently validating user intent

The attacker often does not need to read the response.
They just need the state-changing action to succeed.

## Techniques / patterns

Attackers typically look for:
- state-changing POST endpoints
- GET endpoints that incorrectly change state
- cookie-based auth flows
- missing anti-CSRF tokens
- weak or absent origin validation
- endpoints that accept simple form submissions
- places where teams assume CORS prevents CSRF

Common delivery methods:
- hidden forms
- auto-submitting forms
- image or script-triggered requests where relevant
- browser-controlled navigation / link flows
- malicious sites visited by an already logged-in victim

## Variants and bypasses

### Classic form-based CSRF

The target accepts a normal browser form submission and the victim’s cookies are included.

### GET-based CSRF

The application changes state on GET, making exploitation even easier.

### Token bypass / weak validation

Anti-CSRF exists but is:
- missing on some endpoints
- not bound to session/user properly
- accepted across contexts it should not trust
- leaked or predictable in some way

### SameSite misunderstandings

`SameSite` helps, but:
- defaults vary by browser era and app behavior
- some app flows require exceptions
- developers sometimes overestimate what it blocks
- same-site vs same-origin distinctions matter

### JSON/API misconceptions

Teams sometimes assume “API endpoints aren’t CSRFable”.
That depends on:
- credential transport
- content types accepted
- preflight behavior
- whether the browser can send the request in a simple form or equivalent path

### Login / logout / state-transition CSRF

Even if “change email” is protected, flows like:
- login
- logout
- account binding
- state toggles
can still have meaningful CSRF impact.

## Impact

Impact depends on what the authenticated victim can do.

Typical impact:
- change account settings
- initiate sensitive actions
- bind attacker-controlled state to victim account
- delete or modify resources
- abuse privileged victim roles (admin/staff CSRF)

CSRF often becomes far more serious when:
- admins can perform high-impact actions
- there is no re-authentication for sensitive operations
- the action is easy to trigger and hard to detect

## Detection and defense

Ordered by effectiveness:

1.
**Anti-CSRF tokens where needed**
   Tokens should be validated server-side and tied appropriately to user/session/request context.

2.
**Use correct browser-aware defense strategy**
   Understand when cookies are sent automatically and what SameSite does in the actual app flow.

3.
**Origin / Referer validation where appropriate**
   Useful as layered defense when implemented carefully.

4.
**Do not use GET for state-changing operations**
   Safe methods should stay safe.

5.
**Re-auth or stronger confirmation for sensitive actions**
   Especially for high-impact admin or account-changing flows.

6.
**Do not confuse CORS with CSRF protection**
   CORS controls browser read permissions, not user intent.

7.
**Monitoring**
   Watch for:
   - suspicious state-changing requests without expected anti-CSRF artifacts
   - unusual origin patterns
   - admin-sensitive actions from unexpected navigation flows

## Practical examples

- hidden form auto-submits to change an account email
- state-changing GET endpoint triggered by visiting a link
- admin action performed because the victim visits an attacker-controlled page while logged in
- JSON endpoint assumed safe, but browser-deliverable request patterns still succeed

## Related notes

- [[cookies-and-sessions]]
- [[session-management]]
- [[cors-misconfiguration]]
- [[inspect-session-handling|Inspect Session Handling]]

### Suggested future atomic notes

- samesite-in-practice
- origin-vs-referer-validation

## References

- **Foundational:** OWASP Cross-Site Request Forgery Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf
