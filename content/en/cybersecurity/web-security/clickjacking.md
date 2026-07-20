---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Clickjacking

## Definition

Clickjacking is a UI redress attack where an attacker embeds a target page in a frame and tricks the user into clicking or typing into the real target UI while they believe they are interacting with another page.

The vulnerability is not "a page has buttons." The vulnerability is that a sensitive page can be embedded by an untrusted origin and visually manipulated around a user's trusted session.

## Why it matters

Clickjacking turns the browser's normal framing behavior into a confused-user action channel. If a logged-in user can be lured to an attacker page, the attacker may cause account changes, consent grants, payment actions, destructive admin clicks, or privacy-impacting UI actions.

It is tightly connected to [[content-security-policy]] because modern protection is usually `Content-Security-Policy: frame-ancestors ...`. It also touches [[csrf]] because both classes abuse an authenticated user's browser, but they are not the same bug: CSRF sends a request; clickjacking manipulates visible interaction.

## How it works

Clickjacking has **5 moving parts**:

1. **Sensitive target page.** The victim is authenticated to a page with meaningful UI actions.
2. **Attacker-controlled wrapper.** The attacker hosts a page that embeds the target in an `<iframe>`.
3. **Visual deception.** CSS opacity, positioning, overlays, or misleading text hide what the user is really clicking.
4. **User action.** The victim clicks, drags, types, or taps where the attacker wants.
5. **Browser sends trusted interaction.** The action lands on the framed target page under the victim's session.

Minimal wrapper shape:

```
<style>
iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 800px;
  height: 600px;
  opacity: 0.05;
  z-index: 2;
}
.bait {
  position: absolute;
  top: 140px;
  left: 220px;
  z-index: 1;
}
</style>
<button class="bait">Claim reward</button>
<iframe src="https://target.example/account/delete"></iframe>
```

The bug is not the iframe tag. The bug is missing or too-broad embed control on a page whose UI can cause sensitive state changes.

## Techniques / patterns

Attackers and testers look at:

- account settings, password reset, email change, MFA, OAuth consent, billing, admin, and destructive-action pages
- pages that render while authenticated and have no anti-framing header
- state-changing actions that rely only on a click or simple form interaction
- single-click confirmations and weak confirmation dialogs
- mixed protection where some pages set `frame-ancestors` and others do not
- partner or portal flows where legitimate embedding is needed but too broadly allowed

### Worked example: sensitive page frameability

```
Target:
  /account/email

Action:
  change recovery email

Headers:
  no Content-Security-Policy frame-ancestors
  no X-Frame-Options

Test:
  owned wrapper page embeds /account/email while logged in

Decision:
  clickjacking risk is real if the framed UI can complete the change or start a sensitive workflow
```

A good finding states both frameability and the user action that becomes dangerous.

## Variants and bypasses

Clickjacking has **5 practical variants**.

### 1. Classic transparent iframe

The target page is placed over attacker-controlled bait with low opacity or careful positioning. The victim clicks the real target UI.

### 2. Cursor or pointer deception

The attacker uses styling and layout to make the pointer appear aligned with a fake action while the real click lands elsewhere.

### 3. Multi-step UI redress

The attacker guides the user through several harmless-looking clicks that line up with a sensitive multi-step flow inside the frame.

### 4. Drag-and-drop or typing abuse

Some UI actions are not simple clicks. The attack may trick users into dragging data, selecting options, or typing into a framed target.

### 5. Overbroad trusted framing

The site uses `frame-ancestors` but allows broad partner, wildcard, or legacy origins that can host attacker-controlled pages.

## Impact

Ordered roughly by severity:

- **Account or security setting changes.** Email, MFA, password, session, or recovery settings can be altered.
- **Authorization or consent abuse.** OAuth, SSO, app-authorization, or admin-consent pages can be manipulated.
- **Financial or destructive actions.** Payments, purchases, deletions, and administrative changes can be triggered.
- **Privacy exposure.** Framed UI may reveal state or trick users into sharing information.
- **Trust erosion.** Even failed attempts undermine confidence in sensitive workflows.

Impact depends on the framed page, the user's role, whether the action requires fresh authentication, and whether the target UI has independent confirmation.

## Detection and defense

Ordered by effectiveness:

1.
**Set `Content-Security-Policy: frame-ancestors` on sensitive pages.**
   `frame-ancestors 'none'` blocks all framing; `frame-ancestors 'self'` limits framing to same-origin pages. This is the modern, expressive browser control and should be deployed on the responses that need protection.

2.
**Use `X-Frame-Options` for legacy browser coverage where appropriate.**
   `DENY` and `SAMEORIGIN` are simpler than CSP and less flexible, but still useful for older clients. Do not rely on `ALLOW-FROM`; support is inconsistent and obsolete.

3.
**Require strong confirmation for high-risk actions.**
   Re-authentication, typed confirmation, step-up MFA, and transaction signing reduce damage when a UI is exposed. These controls should complement frame blocking, not replace it.

4.
**Keep legitimate embedding narrow and explicit.**
   If partners or internal portals must frame a page, allow only exact trusted origins and review whether those origins can host attacker-controlled content.

5.
**Test every sensitive route, not just the homepage.**
   Header middleware, proxy routes, static error pages, and legacy flows often drift. Clickjacking protection is per response.

### What does not work as a primary defense

- **CSRF tokens alone.** Clickjacking uses the user's real browser and real UI, so valid CSRF tokens may be present.
- **Frame-busting JavaScript.** Scripts can fail, be blocked, race, or be sandboxed; headers are the primary control.
- **Hiding buttons with CSS.** The attacker controls the wrapper page, not the target's secure presentation.
- **Only protecting the login page.** The risk is usually authenticated settings, consent, billing, and admin pages.

## Practical labs

Use owned apps or intentionally vulnerable labs.

### Inspect frame protections

```
curl -I https://app.example.test/account/settings | rg -i "content-security-policy|x-frame-options"
```

Look specifically for `frame-ancestors` in CSP or `DENY` / `SAMEORIGIN` in `X-Frame-Options`.

### Build a local frame test

```
<!doctype html>
<html>
  <body>
    <h1>Frame test</h1>
    <iframe src="https://app.example.test/account/settings" width="900" height="700"></iframe>
  </body>
</html>
```

Open this file locally while authenticated to the target app and confirm whether the browser blocks framing.

### Compare sensitive and nonsensitive routes

```
for path in / /account /account/settings /admin /oauth/authorize; do
  printf "\n== %s ==\n" "$path"
  curl -skI "https://app.example.test$path" | rg -i "content-security-policy|x-frame-options" || true
done
```

Protection should be consistent on sensitive routes, not only on the root page.

### Check allowed ancestors

```
Route:
frame-ancestors value:
Allowed origins:
Do allowed origins host user content:
Sensitive action available:
Decision:
```

An allowlist is only as strong as the least trustworthy allowed origin.

### Record a clickjacking finding

```
Page:
User role:
Sensitive action:
Frame protection observed:
Proof wrapper:
Action completed or partially completed:
Recommended header:
Retest result:
```

Avoid destructive proof. Demonstrate frameability and choose a harmless or reversible action.

## Practical examples

- Account settings can be framed and a logged-in user can be tricked into starting an email-change flow.
- An OAuth consent page is frameable and can be aligned under misleading "continue" UI.
- An admin dashboard blocks framing, but a legacy admin action endpoint does not.
- A payment confirmation page uses CSRF tokens but lacks `frame-ancestors`, allowing UI redress.
- A partner portal requires framing, but `frame-ancestors *` allows any site to embed the page.

## Related notes

- [[content-security-policy]]
- [[csrf]]
- [[http-headers]]
- [[xss]]
- [[open-redirect]]
- [[auth-flaws]]

### Suggested future atomic notes

- frame-ancestors
- x-frame-options
- ui-redress-attacks
- oauth-consent-clickjacking
- browser-security-headers

## References

- **Foundational:** MDN CSP `frame-ancestors` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
- **Foundational:** OWASP Clickjacking Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Clickjacking — https://portswigger.net/web-security/clickjacking
