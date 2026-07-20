---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cookies and Sessions

## Definition

Cookies are HTTP header-carried state that browsers store and automatically attach to later requests. Sessions are the server-side or token-backed continuity model that lets an application recognize "the same user" across otherwise stateless HTTP requests.

## Why it matters

Most web authentication bugs become concrete at the cookie/session layer. A login can be correct while the browser still sends a session cookie to the wrong host, over the wrong transport, in the wrong cross-site context, or after logout should have killed it. Cookies are also where browser policy, TLS, reverse proxies, CSRF, XSS, and authorization meet.

The recurring lesson: **HTTP state is not one thing**. It is carried by browser rules, cookie attributes, server session storage, and trust boundaries between origins and subdomains.

This note stays at the networking/protocol behavior layer. [[session-management|Session Management]] owns application-side lifecycle flaws such as fixation, rotation, logout, and account switching.

## How it works

HTTP session state moves through **4 parts**:

1. **Server emits state.** A response includes one or more `Set-Cookie` headers.
2. **Browser stores state.** The browser decides whether to accept the cookie based on attributes such as `Domain`, `Path`, `Secure`, `SameSite`, expiry, and prefix rules.
3. **Browser attaches state automatically.** Later requests whose URL and context match the cookie rules carry a `Cookie:` header without JavaScript or user action.
4. **Server interprets state.** The application maps the cookie value to a server-side session row, a signed/encrypted blob, or a token such as a JWT.

Example login response:

```
HTTP/1.1 302 Found
Location: /account
Set-Cookie: __Host-session=9f2a...; Path=/; Secure; HttpOnly; SameSite=Lax
Set-Cookie: csrf=7c31...; Path=/; Secure; SameSite=Strict
Cache-Control: no-store
```

Follow-up request:

```
GET /account HTTP/1.1
Host: app.example.com
Cookie: __Host-session=9f2a...; csrf=7c31...
```

The browser did not "log in" the user; it only replayed state under matching rules. The application still has to validate that state and authorize every action.

The bug usually lives in the gap between what the browser is allowed to send and what the application assumes that send means.

## Techniques / patterns

Attackers and defenders inspect:

- every `Set-Cookie` header on login, logout, password reset, OAuth callback, MFA, account switching, and admin elevation
- whether sensitive cookies use `Secure`, `HttpOnly`, `SameSite`, narrow `Domain`/`Path`, and preferably the `__Host-` prefix
- whether session IDs rotate after login, privilege change, and password reset
- whether logout invalidates server-side state or only deletes the browser cookie
- whether subdomains can set or shadow parent-domain cookies
- whether cross-site requests carry cookies in ways that matter for [[csrf|CSRF]]
- whether XSS can read tokens or only act with ambient cookies
- whether responses carrying session data use `Cache-Control: no-store`

## Variants and bypasses

Cookie/session failures fall into **6 practical classes**. Holding these in working memory is enough to triage most session-state findings.

### 1. Attribute omission

The cookie exists but lacks protective attributes. Missing `Secure` allows cleartext leakage on HTTP paths. Missing `HttpOnly` lets JavaScript read the value after XSS. Missing or loose `SameSite` increases CSRF exposure. These flags do not replace server-side authorization, but they lower the blast radius of other bugs.

### 2. Scope mistakes

`Domain=.example.com` lets subdomains participate in the same cookie namespace. If any subdomain is weaker, compromised, or takeover-prone, it may set a cookie that shadows the real one. `Path` is not an authorization boundary; it only controls browser send behavior.

### 3. Prefix rule bypass or absence

`__Secure-` requires `Secure`. `__Host-` requires `Secure`, no `Domain`, and `Path=/`. The `__Host-` prefix is useful because it makes broad-domain cookie shadowing structurally harder. The bypass is simple: applications often do not use the prefixes, or accept fallback cookies with weaker names.

### 4. Session fixation

The application accepts a session ID before authentication and keeps the same ID after login. If an attacker can plant or predict the pre-auth session, the victim's successful login attaches identity to attacker-known state.

### 5. Broken invalidation

Logout, password reset, account disable, or MFA reset deletes the browser cookie but leaves the server-side session valid. This creates "zombie sessions" that keep working from another browser or stolen cookie jar.

### 6. Stateless token confusion

JWTs or signed cookies remove the server session lookup but not the security problem. If revocation, rotation, expiry, audience, and signing-key handling are weak, the system becomes harder to invalidate than a normal session store.

## Impact

Ordered roughly by severity:

- **Account takeover or persistent session reuse.** Stolen or fixed session IDs continue to authenticate the attacker.
- **Admin action abuse.** XSS or CSRF can act through ambient cookies even when the cookie value is not directly exposed.
- **Cross-subdomain compromise.** A weaker sibling subdomain can set, shadow, or influence cookies for the parent domain.
- **Sensitive data leakage.** Cookies sent over HTTP, cached account pages, or logs that capture `Cookie:` headers expose session material.
- **Weak incident response.** Broken invalidation means password changes and logout do not actually remove attacker access.
- **Confusing auth debugging.** Multiple cookies with the same name but different scope make behavior path-dependent and hard to reason about.

## Detection and defense

Ordered by effectiveness:

1.
**Use server-side session identifiers for browser auth and rotate them at trust changes.**
   A random opaque session ID backed by a server-side store is easier to revoke, inspect, and rotate than a long-lived self-contained token. Rotate on login, privilege elevation, password reset, and account recovery so attacker-planted or stale state cannot become authenticated state.

2.
**Set strong cookie attributes by default.**
   Sensitive auth cookies should be `Secure; HttpOnly; SameSite=Lax` or `Strict` where the workflow allows it. `Secure` protects transport, `HttpOnly` reduces token theft after XSS, and `SameSite` reduces ambient-cookie CSRF risk. These flags are cheap, visible, and prevent many compound failures.

3.
**Prefer `__Host-` for primary session cookies.**
   `__Host-session=...; Secure; Path=/; HttpOnly; SameSite=Lax` with no `Domain` makes the cookie host-only and prevents sibling subdomains from setting the same cookie for the parent domain. This directly addresses subdomain shadowing and takeover-adjacent risk.

4.
**Keep session lifetime and invalidation server-controlled.**
   Expire sessions on the server, not only through browser `Max-Age` / `Expires`. Logout, password reset, account disable, and suspicious activity should revoke active server-side sessions. Browser deletion is user-interface cleanup; server invalidation is the security control.

5.
**Treat CSRF separately from cookie flags.**
   `SameSite=Lax` helps, but complex login flows, OAuth callbacks, older browsers, cross-site top-level navigations, and `SameSite=None` integrations still need explicit CSRF tokens or origin checks. Cookie behavior is a layer, not the whole defense.

6.
**Do not cache personalized responses.**
   Account, profile, admin, billing, and API responses that depend on cookies should use `Cache-Control: no-store`. Shared proxies and browser caches do not know your authorization model unless headers tell them.

7.
**Log session events without logging secrets.**
   Record session creation, rotation, revocation, and suspicious reuse. Never log raw `Cookie:` headers or session IDs. Logs should help reconstruct abuse without becoming a session-token leak.

### What does not work as a primary defense

- **Relying on `HttpOnly` as an XSS fix.** `HttpOnly` stops JavaScript from reading the cookie value; it does not stop malicious JavaScript from making authenticated same-origin requests with the cookie automatically attached.
- **Treating `SameSite` as complete CSRF protection.** `SameSite` has browser and workflow edge cases. Keep anti-CSRF tokens or origin validation for state-changing operations.
- **Using `Path` as authorization.** `Path=/admin` controls when the browser sends a cookie; it does not stop a server route from accepting another cookie or another endpoint from performing admin work.
- **Deleting the cookie without revoking the server session.** The attacker may already have a copy. Server-side invalidation is the control.
- **Storing roles, balances, or permissions in unsigned client-readable cookies.** The browser is not a database boundary. If the client can tamper with state, the server must verify integrity and authorization independently.

## Practical labs

Run these only against systems you own or are authorized to test. Stock `curl`, browser DevTools, and optionally `jq` are enough.

### Inspect `Set-Cookie` posture

```
# Show every cookie the server tries to set during login or a protected redirect.
curl -skI https://app.example.com/login | rg -i '^set-cookie|^location|^cache-control'

# Follow redirects and keep headers visible.
curl -skIL https://app.example.com/login | rg -i '^set-cookie|^location|^cache-control'
```

Look for: missing `Secure`, missing `HttpOnly`, missing/loose `SameSite`, broad `Domain`, broad `Path`, no `Cache-Control: no-store` on authenticated pages.

### Persist and replay a session with curl

```
# Capture cookies from a login-like flow.
curl -sk -c /tmp/app.cookies https://app.example.com/login >/dev/null

# Replay them to a protected page.
curl -sk -b /tmp/app.cookies -i https://app.example.com/account | sed -n '1,25p'

# Inspect what curl stored.
cat /tmp/app.cookies
```

This shows which cookies are host-only, which have a `Domain`, and which paths they apply to.

### Compare pre-login and post-login session rotation

```
# 1. Get a pre-auth cookie.
curl -sk -c /tmp/pre.cookies -I https://app.example.com/login | rg -i '^set-cookie'

# 2. Log in manually in a browser or with an authorized test account.
# 3. Export/copy the post-login session cookie value from DevTools.

# Compare whether the primary session ID changed across the trust boundary.
cat /tmp/pre.cookies
```

If the same primary session identifier survives login, investigate session fixation.

### Test cookie scope across sibling subdomains

```
# Does a sibling host set a parent-domain cookie?
curl -skI https://staging.example.com/ | rg -i '^set-cookie'

# A risky shape looks like:
# Set-Cookie: session=...; Domain=.example.com; Path=/; Secure
```

If a low-trust subdomain can set `.example.com` auth-adjacent cookies, review `Domain` scope and prefer `__Host-` for the real session.

### Verify logout invalidates the server-side session

```
# Save a known-good session cookie jar first.
curl -sk -b /tmp/app.cookies -c /tmp/app.cookies https://app.example.com/logout >/dev/null

# Try replaying the old jar after logout.
curl -sk -b /tmp/app.cookies -i https://app.example.com/account | sed -n '1,30p'
```

Expected: redirect to login or `401/403`. If the old cookie still works from another client, logout is only deleting browser state.

### Check cross-site send behavior in a browser

Use DevTools → Application → Cookies and DevTools → Network:

```
1. Open the cookie table for app.example.com.
2. Record SameSite, Secure, HttpOnly, Domain, Path.
3. Trigger a cross-site navigation or authorized CSRF lab form.
4. Check whether the Cookie header was attached.
```

Browser observation matters because `curl` does not implement browser same-site policy.

## Practical examples

- A login response sets `session=...; Domain=.example.com`; a compromised staging subdomain shadows the cookie for the parent app.
- A password reset flow changes the password but does not revoke existing sessions, so a stolen cookie keeps working.
- An XSS payload cannot read an `HttpOnly` cookie but can still `fetch('/admin/users/delete')` with the browser's ambient session.
- A billing page is served with `Cache-Control: public`; a shared proxy stores another user's account page.
- An OAuth callback requires `SameSite=None; Secure` for a third-party flow, but the rest of the app assumes all cookies are same-site protected.

## Related notes

- [[http-overview]] — request lifecycle and browser/server interaction model.
- [[http-messages]] — raw `Set-Cookie` and `Cookie` message shape.
- [[http-headers]] — broader header semantics that cookies build on.
- [[tls-https]] — `Secure`, HSTS, and transport guarantees for cookies.
- [[session-management|Session Management]] — application-side session lifecycle vulnerabilities.
- [[csrf|CSRF]] — browser-automatic cookies are the reason CSRF exists.
- [[xss|XSS]] — XSS interacts with `HttpOnly`, ambient cookies, and token storage.
- [[caching-and-security]] — personalized cookie-backed responses must not be cached incorrectly.
- [[inspect-session-handling|Inspect Session Handling]]

### Suggested future atomic notes

- cookie-prefixes-host-secure
- samesite-cookie-behavior
- session-fixation
- session-rotation
- logout-invalidation
- csrf-token-design

## References

- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
- **Foundational:** OWASP Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- **Testing / Lab:** OWASP WSTG Session Management Testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf
