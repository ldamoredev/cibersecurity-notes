---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Same-Origin Policy

## Definition

The same-origin policy (SOP) is the browser's foundational isolation rule: script running in one **origin** may freely read another resource's content, DOM, and stored state *only if* that resource shares its origin — otherwise the browser blocks the read. An **origin** is the tuple **(scheme, host, port)**; all three must match exactly. SOP is the default-deny boundary that every other web isolation mechanism (CORS, CORP/COEP/COOP, cookies, `postMessage`) either relaxes or reinforces. If you understand one web-security primitive, it should be this one.

## Why it matters

SOP is *the* reason a malicious tab cannot read your webmail or drain your bank session while you browse elsewhere. Almost every web vulnerability class is best understood as "what happens at, or around, the SOP boundary":

- **It defines the trust boundary the rest of web security argues about.** XSS matters because it runs code *inside* an origin (defeating SOP from within); CORS matters because it *relaxes* SOP's read block; CSRF matters because SOP *does not* block cross-origin *sends*. You cannot reason about any of them without SOP as the baseline.
- **Its central asymmetry — send is allowed, read is blocked — is the seed of two whole bug classes.** The browser will *send* a cross-origin request (and attach cookies, for some), run its side effects, then withhold the response from script. "Send allowed" births CSRF; "controlled read" births CORS; "observe-without-reading" births XS-leaks.
- **It is exact-match and unforgiving, which is where mistakes live.** `https://app.example.com` and `https://api.example.com` are *different* origins; so are `http://` vs `https://`, and `:443` vs `:8443`. Most real cross-origin vulnerabilities are a developer accidentally widening this boundary (reflected CORS, sloppy `postMessage`, `document.domain`, subdomain takeover).

## How it works

SOP governs **3 access surfaces**, and on each the default is deny-across-origins:

1. **Network reads.** Script may *send* a cross-origin request but cannot *read* the response unless the target opts in via CORS.
2. **DOM access.** Script in one frame/window cannot read the DOM or JS state of a cross-origin frame/window.
3. **Storage.** `localStorage`, `sessionStorage`, and IndexedDB are partitioned per origin. (**Cookies are the famous exception** — they are keyed by *site/domain*, not origin, which is exactly why CSRF exists.)

Two URLs are same-origin iff scheme, host, and port all match — path and query are irrelevant:

| URL A | URL B | Same origin? | Why |
| --- | --- | --- | --- |
| `https://app.example.com/a` | `https://app.example.com/b` | ✅ | path doesn't count |
| `https://app.example.com` | `http://app.example.com` | ❌ | scheme differs |
| `https://app.example.com` | `https://api.example.com` | ❌ | host differs |
| `https://app.example.com` | `https://app.example.com:8443` | ❌ | port differs |
| `http://example.com` | `http://example.com:80` | ✅ | `:80` is the http default |

The load-bearing asymmetry — the browser **sends** the request but SOP **blocks the read**:

```
// Page running on https://evil.example
fetch('https://bank.example/account', { credentials: 'include' })
  .then(r => r.text())     // SOP blocks reading the body unless bank.example
  .then(console.log);      // returns CORS headers — script gets a TypeError / opaque response
```

The request *was sent* (and `bank.example`'s cookies may have ridden along, running any side effect); SOP only stops `evil.example`'s script from *seeing* the response. The bug is not "the request happened" — it is whether reading, DOM access, or storage crossed the origin line.

## Techniques / patterns

What an attacker probes — every probe looks for a place the origin boundary was accidentally widened:

- **Hunt the relaxations, not SOP itself.** SOP is robust; its *opt-outs* are where bugs live: reflected/`null`/wildcard CORS with credentials, `postMessage` handlers with no `event.origin` check, `document.domain` relaxation, JSONP endpoints.
- **Exploit the send/read asymmetry.** Cross-origin *sends* are allowed → CSRF. Cross-origin *observations* (load/error events, frame counts, timing, dimensions) are allowed → XS-leaks infer cross-origin state without reading bodies.
- **Distinguish same-origin from same-site.** Cookies, `SameSite`, and CORP key on *site* (eTLD+1), not origin. `a.example.com` and `b.example.com` are cross-origin but same-site — a distinction attackers weaponize.
- **Chase subdomain takeover.** If `cdn.example.com` is dangling and attacker-claimable, a "trusted" same-site origin becomes hostile, defeating any site-keyed trust.
- **Remember XSS is the inside job.** SOP protects *between* origins; an XSS that executes *inside* the target origin owns everything SOP was protecting.

## Variants and bypasses

SOP ships with **5 sanctioned relaxations**, each a deliberate hole — and each a bug class when misused.

### 1. CORS (Cross-Origin Resource Sharing)

The server opts into cross-origin reads with `Access-Control-Allow-Origin`. Misconfigurations — reflecting the request `Origin` while allowing credentials, accepting `null`, or trusting wildcard subdomains — re-open exactly the read SOP blocked. See [[cors-misconfiguration]].

### 2. postMessage

The sanctioned channel for cross-origin window messaging. A receiver that fails to validate `event.origin`, or a sender that uses `targetOrigin: '*'`, leaks data across origins or hands an attacker a DOM-XSS sink.

### 3. document.domain (deprecated / disabled by default)

Two pages under a shared parent domain could once set `document.domain` to become "same-origin." Modern browsers disable it by default (it now requires opting out of Origin-Agent-Cluster). A legacy footgun that collapses origin to site.

### 4. Cross-origin embedding (the read/write asymmetry)

SOP lets a page *embed* cross-origin resources (`<img>`, `<script>`, `<iframe>`, `<link>`) and *send* forms — without reading them. This sanctioned "write/embed allowed, read blocked" rule is precisely what makes CSRF and XS-leaks possible.

### 5. JSONP (legacy)

A pre-CORS hack: fetch cross-origin data as a `<script>` invoking a callback, sidestepping SOP by design. An injection and data-exfiltration hazard wherever it survives.

## Impact

Ordered by severity, for when a relaxation is misused (or the boundary otherwise collapses):

- **Cross-origin data theft.** A CORS misconfig lets an attacker origin read authenticated responses — account data, PII, anti-CSRF tokens.
- **DOM-based XSS.** A `postMessage` handler that trusts attacker input and writes it to the DOM yields code execution inside the victim origin.
- **Session riding (CSRF).** SOP permits the cross-origin state-changing request; without `SameSite`/tokens the action succeeds.
- **Cross-site inference (XS-leaks).** Login state, search results, or account attributes inferred via SOP-allowed side channels without reading any body.
- **Full origin compromise.** Subdomain takeover or an XSS inside the origin defeats SOP entirely from a trusted position.

## Detection and defense

For a foundational concept note, "defense" is *keeping the origin boundary intact*. Ordered by effectiveness:

1.
**Treat the origin as the security boundary and keep sensitive services on distinct origins.**
   Separation by origin is the strongest isolation the platform offers; co-hosting unrelated trust levels on one origin throws it away. Put the admin panel, the API, and user content on origins you can reason about independently.

2.
**Lock down each sanctioned relaxation.**
   CORS: never reflect `Origin` with `Access-Control-Allow-Credentials: true`, never allow `null`, allowlist exact origins. `postMessage`: validate `event.origin` against an allowlist *and* set an explicit `targetOrigin`. Do not use `document.domain`. Retire JSONP. Each relaxation is a door you opened — keep it as narrow as the use case.

3.
**Defend the send-asymmetry separately with SameSite cookies + anti-CSRF tokens.**
   Because SOP does *not* block cross-origin sends, the request boundary needs its own control. `SameSite=Lax/Strict` cookies plus per-request CSRF tokens close it. See [[csrf]].

4.
**Layer the modern boundary controls on top.**
   `Cross-Origin-Resource-Policy`, COOP/COEP for cross-origin isolation, Origin-Agent-Cluster, and CSP harden the boundary against side channels and embedding abuse — the subject of [[browser-security-boundaries]].

5.
**Prevent subdomain takeover and keep XSS out.**
   A dangling subdomain or an injected script inside the origin defeats everything above; DNS hygiene and output encoding/CSP protect the boundary from collapse from within.

### What does not work as a primary defense

- **"SOP stops CSRF."** The canonical false friend. SOP blocks the *read*, not the *send* — the cross-origin request goes through with cookies. CSRF needs `SameSite`/tokens, not SOP.
- **"HTTPS makes pages same-origin."** Scheme is *part* of the origin, so `http`↔`https` are cross-origin — but TLS does not define or enforce the boundary itself.
- **"They're all our company's domains, so they're same-origin."** Different subdomains and ports are different origins. `app.example.com` ≠ `api.example.com`.
- **Obscurity of internal origins.** Unguessable hostnames are not an isolation boundary; the origin tuple is.

## Practical labs

Run only against systems you own or are authorized to test. Most of these run in the browser DevTools console.

### Observe the send/read block

```
// In the console of any https page, fetch a cross-origin endpoint:
fetch('https://example.com/', { mode: 'cors' })
  .then(r => r.text()).then(console.log)
  .catch(e => console.log('SOP/CORS blocked the read:', e.message));
// The request leaves the browser; the read fails unless the target sends CORS headers.
```

### Probe a CORS allow-origin reflection

```
curl -sD - -o /dev/null https://app.example.com/api/me \
  -H 'Origin: https://evil.example'
# Look for: Access-Control-Allow-Origin: https://evil.example  (reflected = bad)
#           Access-Control-Allow-Credentials: true             (with reflection = critical)
```

### Confirm cross-frame DOM access is blocked

```
// Embed a cross-origin iframe, then try to read its document:
const f = document.createElement('iframe');
f.src = 'https://example.com/'; document.body.appendChild(f);
f.onload = () => { try { console.log(f.contentDocument.body.innerHTML); }
                   catch (e) { console.log('SOP blocked DOM access:', e.message); } };
```

### Test a postMessage listener's origin check

```
// If a page registers window.addEventListener('message', ...), send it a probe
// from a different origin and see whether it acts on data without checking event.origin.
targetWindow.postMessage({probe: 'x'}, '*');   // a safe handler must reject unknown origins
```

## Practical examples

- **Reflected-origin CORS theft.** `app.example.com` reflects any `Origin` and allows credentials; `evil.example` reads the victim's authenticated `/api/me`, exfiltrating account data and the CSRF token.
- **postMessage DOM XSS.** A widget listens for `message` events and `innerHTML`s `event.data` without checking `event.origin`; an attacker frame posts a payload and gets script execution in the widget's origin.
- **CSRF working *because* of SOP's allowance.** A hidden auto-submitting form POSTs to `bank.example/transfer`; SOP permits the cross-origin send and the cookie rides along — the transfer succeeds with no read needed.
- **Subdomain takeover collapses the boundary.** A dangling `cdn.example.com` CNAME is claimed by an attacker; scripts the main app trusts from that "same-site" origin now run hostile code.
- **XS-leak via embedding.** An attacker frames `victim.example/search?q=secret` and times the load or counts subframes to infer whether the query matched — cross-site inference with zero body reads.

## Related notes

- [[cors-misconfiguration]] — relaxation #1; the most common way SOP's read block is wrongly re-opened.
- [[csrf]] — the bug that exists *because* SOP allows the cross-origin send.
- [[content-security-policy]] — defense-in-depth inside the origin once XSS threatens the boundary from within.
- [[clickjacking]] — a framing/UI-redress attack the boundary controls (`frame-ancestors`) defend against.
- [[xss]] — the "inside job" that defeats SOP from within the origin.
- [[browser-security-boundaries]] — the modern multi-control system (site-vs-origin, COOP/COEP/CORP, isolation) layered on top of SOP.
- [[cookies-and-sessions|Cookies and Sessions]] — why cookies follow a *site* model, not the origin model, and what that costs.
- [[http-headers|HTTP Headers]] — where the CORS/CORP/COOP headers that modify SOP actually live.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — SOP is the defender's wall; the relaxations are where the operator looks.

### Suggested future atomic notes

- [[browser-security-boundaries]]
- xs-leaks-and-cross-site-inference
- postmessage-security
- site-vs-origin-and-samesite-cookies
- cross-origin-isolation-coop-coep-corp

> Future atomic notes are listed as `<span class="unresolved-link" title="Unpublished or unresolved: wikilinks">wikilinks</span>` even when the target file does not exist yet, so they register as forward-links in Obsidian.

## References

- **Foundational:** RFC 6454 — The Web Origin Concept — https://www.rfc-editor.org/rfc/rfc6454
- **Foundational:** MDN — Same-origin policy — https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy
- **Testing / Lab:** PortSwigger Web Security Academy — Cross-origin resource sharing (CORS) — https://portswigger.net/web-security/cors
