---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cross-Site Scripting (XSS)

## Definition

XSS happens when attacker-controlled input is rendered in a browser context in a way that causes the browser to interpret it as executable code instead of inert data.

## Why it matters

XSS is not just “JavaScript pops an alert”. It turns a trusted origin into an execution environment under attacker influence.

That can lead to:
- session abuse
- action-on-behalf-of-user
- phishing inside a trusted origin
- theft of data available to the browser
- privilege escalation when admins or staff view attacker-controlled content

XSS also teaches the same deep lesson as SQLi: context determines safety. Escaping that is correct in one parser context can fail completely in another.

## How it works

The core shape is:

1. attacker-controlled input enters the app
2. that input reaches a browser sink
3. the application fails to encode or sanitize correctly for that exact sink/context

Typical contexts:
- HTML body
- quoted attribute
- unquoted attribute
- URL attribute
- script block
- event handler
- client-side DOM sink
- template-generated HTML

### Main flavors

#### Reflected XSS

Input comes in the request and is immediately reflected in the response.

#### Stored XSS

Input is saved and later rendered to other users.

#### DOM-based XSS

The vulnerable flow occurs entirely in browser-side code, often through JavaScript sinks such as `innerHTML`.

## Techniques / patterns

Attackers usually look at:

- search fields
- reflected error messages
- profile fields
- comments / chat / tickets
- markdown or rich text editors
- frontend code reading from `location`, `hash`, `postMessage`, or storage
- unsafe DOM sinks
- URL-based rendering patterns
- user-controlled HTML or SVG upload/display paths

Useful testing mindset:
- identify the source
- identify the sink
- identify the context
- test context-specific breakout patterns

## Variants and bypasses

### HTML body context

Common vectors:
- tag injection
- event handlers on tags like `img`, `svg`, `details`
- parser-tolerant tag variations

### Attribute context

Need to break out of the attribute or influence its semantics.

Examples of risk areas:
- `value=""`
- `title=""`
- `src=""`
- `href=""`

### URL context

Danger often comes from:
- `javascript:` URLs
- `data:` URLs
- scheme validation weaknesses
- trusted-but-unsafe URL construction

### Script-block context

The attacker tries to break out of JS string / JS syntax context rather than HTML context.

### DOM XSS sinks

High-value sinks include:
- `innerHTML`
- `outerHTML`
- `insertAdjacentHTML`
- `document.write`
- unsafe framework escape hatches

### Framework-specific issues

Even frameworks that escape by default often expose dangerous escape hatches:
- React `dangerouslySetInnerHTML`
- Vue `v-html`
- Angular trust-bypass APIs
- server templates with unescaped interpolation
- markdown/render pipelines that allow raw HTML

### Sanitizer bypasses

Sanitizers are important, but not magical.
Real bypasses often involve:
- parser differences
- mutation XSS
- SVG-specific behavior
- URL handling mistakes
- newly discovered bypasses in sanitizer libraries

### CSP interactions

CSP can reduce exploitability, but:
- weak CSP is often decorative
- whitelisted scripts can still create gadget-based bypasses
- nonce leakage or `unsafe-inline` weaken the control significantly

## Impact

Impact depends on what the victim’s browser can do in that origin.

Typical impact:
- steal or use session context
- perform authenticated actions
- access CSRF tokens or app state
- escalate through stored/admin-view XSS
- launch highly credible phishing inside the real site
- pivot into internal interfaces reachable from the victim browser in some environments

Even if cookies are `HttpOnly`, XSS can still perform actions directly through same-origin requests.

## Detection and defense

Ordered by effectiveness:

1.
**Context-aware output encoding**
   Encode for the exact sink, not generically.

2.
**Avoid dangerous rendering APIs**
   Use framework-safe defaults and avoid unsafe escape hatches unless absolutely necessary.

3.
**HTML sanitization where rich content is required**
   Use a maintained sanitizer and keep it updated.

4.
**CSP as defense-in-depth**
   Good CSP reduces exploitability, but does not replace correct handling.

5.
**Cookie hardening**
   `HttpOnly`, `Secure`, and appropriate `SameSite` settings reduce some damage.

6.
**Trusted Types where applicable**
   Especially useful for reducing DOM XSS exposure.

7.
**Review source → sink flows**
   Especially in frontend code and component libraries.

8.
**Monitoring**
   Watch for:
   - suspicious rendering behavior
   - repeated payload-shaped input
   - unusual client-side errors
   - anomalous admin-facing user content

## Practical examples

- reflected search-term XSS in a results page
- stored XSS in a support ticket viewed by staff
- DOM XSS via `location.hash` inserted into `innerHTML`
- unsafe markdown rendering that allows HTML/script-adjacent content
- SVG upload that becomes executable when served inline

## Related notes

- [[http-headers]]
- [[session-management]]
- [[csrf]]
- [[inspect-file-upload-surface|Inspect File Upload Surface]]

### Suggested future atomic notes

- [[content-security-policy]]
- mutation-xss
- dom-xss-sinks

## References

- **Foundational:** OWASP Cross Site Scripting Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Cross-site scripting topic — https://portswigger.net/web-security/cross-site-scripting
- **Research / Deep Dive:** PortSwigger XSS cheat sheet — https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
