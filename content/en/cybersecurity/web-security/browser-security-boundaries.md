---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Browser Security Boundaries

## Definition

"Browser security boundaries" is the **layered stack of isolation boundaries** a modern browser enforces between web content — not a single rule but five boundaries operating at different granularities: **origin** (script access), **site** (state), **process** (memory), **agent cluster** (powerful APIs), and **storage partition** (cross-site state). The [[same-origin-policy]] is the innermost of these; the others were added (mostly 2019–2025, accelerated by Spectre and by privacy work) because origin-level isolation alone no longer holds against speculative side channels and cross-site tracking. A "browser security bypass" is almost always *finding the one layer in this stack that didn't hold*.

## Why it matters

By 2026 the post-Spectre, post-Privacy-Sandbox browser is the most-attacked sandbox on earth, and its security is no longer explainable by SOP alone. Three transferable lessons:

- **Different controls key on different boundaries, and the seams are the bugs.** SOP and Origin-Agent-Cluster key on *origin*; cookies, CORP, and storage partitioning key on *site* (eTLD+1). `a.example.com` and `b.example.com` are different origins but the *same site* — so a control you assumed was per-origin may actually trust a sibling subdomain. Most boundary bugs live at a seam where a coarse boundary is trusted as if it were fine-grained.
- **Spectre moved the real boundary from the language to the OS process.** Speculative execution can read across the in-process JS heap, defeating any language-level isolation. The browser's structural answer was **Site Isolation** — put different sites in different OS processes — and **cross-origin isolation** (COOP+COEP) to re-enable powerful timing APIs safely. The memory boundary is now a *process* boundary, which is why renderer sandbox escapes matter as much as web bugs.
- **SOP blocks reads, not observations — so the modern attack class is inference, not theft.** Cross-site leaks (XS-leaks) infer cross-origin state through SOP-permitted side effects (timing, frame counts, error events, cache). The boundary stack exists largely to close these side channels, and the 2025–26 offense is the search for the side channel a given site forgot to close.

This is the modern-boundary companion to [[same-origin-policy]]; SOP is the rule, this note is the system built on it.

## How it works

The boundary stack, innermost to outermost — **5 boundaries**:

| Boundary | Granularity | Enforces | Key mechanism |
| --- | --- | --- | --- |
| **Origin** | scheme+host+port | script read/DOM/storage access | [[same-origin-policy]] |
| **Site** | scheme + eTLD+1 | cookie/state scope, CORP `same-site` | Public Suffix List |
| **Process** | site (or origin) | memory isolation vs Spectre | Site Isolation, Origin-Agent-Cluster |
| **Agent cluster** | cross-origin-isolated | access to SAB + precise timers | COOP + COEP |
| **Storage partition** | (top-site, embedded-site) | cross-site state/tracking | CHIPS, Storage Access API |

The mechanics that bind them:

1. **Origin vs site.** Origin is SOP's tuple; *site* is scheme + the registrable domain (eTLD+1, derived from the Public Suffix List). Cookies, `Cross-Origin-Resource-Policy: same-site`, and storage partitioning operate at site granularity — coarser than origin.
2. **Process isolation (Spectre's answer).** Because a speculative read can cross the in-process boundary, **Site Isolation** places different sites in different renderer processes so one site's speculation cannot reach another's memory. **Origin-Agent-Cluster (`Origin-Agent-Cluster: ?1`)** requests origin-keyed (rather than site-keyed) isolation and disables `document.domain`.
3. **Cross-origin isolation.** `SharedArrayBuffer` and high-resolution timers were disabled after Spectre because they build precise side-channel clocks. A document re-enables them only by becoming *cross-origin isolated*: `Cross-Origin-Opener-Policy: same-origin` **and** `Cross-Origin-Embedder-Policy: require-corp`, which together guarantee no un-opted-in cross-origin resource shares its process.
4. **CORP and COOP as the building blocks.** `Cross-Origin-Resource-Policy` lets a *resource* declare who may embed it (`same-origin`/`same-site`/`cross-origin`), blocking speculative cross-origin inclusion. `Cross-Origin-Opener-Policy` severs the `window.opener` link between cross-origin top-level documents, closing cross-window leaks.
5. **Storage partitioning.** Cookies and storage are increasingly keyed by *(top-level site, embedded site)* so a third-party iframe cannot share state across the sites embedding it; **CHIPS** (`Set-Cookie: ...; Partitioned`) is the opt-in, and the **Storage Access API** grants scoped exceptions.

The headers that turn it on, in one block:

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Resource-Policy: same-origin
Origin-Agent-Cluster: ?1
# COOP + COEP  =>  self.crossOriginIsolated === true  =>  SharedArrayBuffer re-enabled
```

The boundary is a stack — origin for script access, site for state, process for memory, agent-cluster for powerful APIs, partition for cross-site state. Security holds only as long as *every* layer the data relies on holds.

## Techniques / patterns

What an attacker probes:

- **Find the coarsest boundary the target trusts.** If a control keys on *site*, a sibling subdomain (or a subdomain takeover) is inside it. Site-vs-origin confusion is the highest-yield seam.
- **Mine SOP-permitted observations for XS-leaks.** Response timing, frame/`window.length` counts, cache hit/miss, `onload`/`onerror` events, `history.length`, COOP/COEP probing, and `crossOriginIsolated` state all leak cross-origin/cross-site bits without reading any body.
- **Hunt missing isolation headers.** Absent CORP/COOP/COEP means resources can be speculatively included and windows can retain `opener` — the preconditions for side-channel reads and cross-window leaks.
- **Look for SAB without isolation.** Any path that exposes `SharedArrayBuffer` or a precise timer *without* full cross-origin isolation reopens the Spectre clock.
- **Chain to a sandbox escape.** The process boundary is the last line; a renderer memory-corruption bug ([[use-after-free-and-dangling-pointers|UAF]]/type confusion) plus an IPC/broker bug escapes Site Isolation entirely.

## Variants and bypasses

The **5 pressure classes** against the boundary stack — covering Q5's named 2025–26 techniques.

### 1. XS-Leaks (cross-site leaks)

Inferring cross-origin/cross-site state via SOP-allowed side effects (timing, frame counting, cache probing, error events, COOP/COEP behavior). The dominant boundary-pressure class against the post-SOP model — it attacks *observability*, which SOP never restricted.

### 2. Spectre-class speculative side channels

Speculative execution reads memory across the in-process boundary. Neutralized by the *process* boundary (Site Isolation) and cross-origin isolation; where those are absent — some mobile browsers, embedded WebViews, misconfigured isolation — cross-origin in-process reads remain feasible.

### 3. SharedArrayBuffer reintroduction edge cases

SAB + precise timers are the side-channel amplifier, gated behind cross-origin isolation. Edge cases reopen them: enterprise policy re-enabling SAB without isolation, origin-trial gaps, or timer-precision quirks that rebuild a usable clock from `performance.now()`/`postMessage` timing.

### 4. Renderer sandbox escape

The process boundary is enforced by the OS sandbox. A renderer RCE (UAF/type confusion) chained with an IPC, broker, or kernel bug escapes Site Isolation — the prestige Pwn2Own chain where web-boundary security meets [[memory-corruption|memory corruption]].

### 5. Site-vs-origin confusion

Controls keyed on *site* (cookies, CORP `same-site`) trust every same-site origin. A single XSS or subdomain takeover on any sibling subdomain pivots across the *site* boundary — the coarse layer is the weak link in the stack.

## Impact

Ordered by severity:

- **Renderer escape → device compromise.** A sandbox-escape chain breaks the process boundary and runs outside the browser — the highest-impact outcome.
- **Cross-origin memory reads.** A Spectre side channel reads another site's secrets sharing the same process (where isolation is absent).
- **Cross-site state inference (XS-leaks).** Login status, account attributes, search results, or admin status inferred across the boundary without reading bodies.
- **Cross-site tracking / state leakage.** Unpartitioned storage links a user across the sites embedding a third party.
- **Defense-in-depth collapse.** A site-granular control trusted as if origin-granular is silently bypassable via a sibling origin.

## Detection and defense

How to keep the boundary stack intact, ordered by effectiveness:

1.
**Deploy cross-origin isolation where it matters.**
   Set `COOP: same-origin` + `COEP: require-corp` for any app that uses `SharedArrayBuffer`/precise timers or holds cross-origin-sensitive data. It guarantees a clean process and closes the timer side channels SAB would otherwise enable — the strongest single control for high-value apps.

2.
**Set CORP on resources.**
   `Cross-Origin-Resource-Policy: same-origin` (or `same-site`) stops a resource from being speculatively included by a cross-origin page — the resource-side half of closing Spectre inclusion.

3.
**Set COOP to sever opener relationships.**
   `Cross-Origin-Opener-Policy: same-origin` cuts the `window.opener` channel between cross-origin top-level documents, closing a class of cross-window XS-leaks even without full isolation.

4.
**Opt into origin-keyed isolation; don't relax to site.**
   `Origin-Agent-Cluster: ?1` requests per-origin process isolation and disables `document.domain`. Never widen the boundary back to site via `document.domain`.

5.
**Reject cross-site requests server-side with Fetch Metadata.**
   `Sec-Fetch-Site`/`Sec-Fetch-Mode` let the *server* see and refuse cross-site/cross-origin requests it never intended to serve — a Resource Isolation Policy that blunts many XS-leaks and CSRF at the origin.

6.
**Partition state and use the Storage Access API.**
   Adopt CHIPS (`Partitioned` cookies) and request cross-site access explicitly via the Storage Access API rather than relying on legacy unpartitioned third-party cookies.

7.
**Keep the renderer hard.**
   Since the process boundary is the last line, the [[exploit-mitigations|memory-safety mitigations]] (hardened allocators, MTE, CFI) are part of the browser boundary story, not separate from it.

### What does not work as a primary defense

- **Relying on SOP alone.** SOP blocks cross-origin *reads*, not the *observations* XS-leaks exploit. The boundary stack exists precisely because SOP is necessary-but-insufficient.
- **Assuming Site Isolation is everywhere.** Mobile browsers and embedded WebViews may lack full Site Isolation; do not assume the process boundary holds on every platform.
- **Treating site as equal to origin.** Sibling subdomains are same-site, not same-origin; site-keyed controls trust them.
- **Enabling SharedArrayBuffer without cross-origin isolation.** This reopens the precise-timer side channel the isolation requirement was added to close.

## Practical labs

Run only against systems you own or are authorized to test. Most run in DevTools.

### Check cross-origin isolation and SAB availability

```
console.log('crossOriginIsolated =', self.crossOriginIsolated);
try { new SharedArrayBuffer(8); console.log('SAB available'); }
catch (e) { console.log('SAB gated:', e.message); }
// SAB should be available iff crossOriginIsolated === true (COOP+COEP set).
```

### Inspect a site's boundary headers

```
curl -sD - -o /dev/null https://app.example.com/ | rg -i \
  '^(cross-origin-opener-policy|cross-origin-embedder-policy|cross-origin-resource-policy|origin-agent-cluster|content-security-policy):'
# Missing COOP/COEP/CORP = the side-channel boundaries are not being enforced.
```

### Distinguish origin from site

```
// For a set of hosts, origin = scheme+host+port; site = scheme + eTLD+1.
// a.example.com and b.example.com: DIFFERENT origin, SAME site.
// app.example.com:443 and app.example.com:8443: DIFFERENT origin, SAME site.
// Controls that key on site trust all of the same-site rows.
```

### Observe Fetch Metadata on the server side

```
# Make a cross-site vs same-origin request and compare the Sec-Fetch-* headers
# the server receives — the basis of a Resource Isolation Policy.
curl -s https://app.example.com/api -H 'Sec-Fetch-Site: cross-site' -D - -o /dev/null | rg -i 'HTTP/'
```

## Practical examples

- **SAB re-enabled without isolation.** An app turns on `SharedArrayBuffer` for a WebAssembly feature via enterprise policy but never sets COOP/COEP; on a shared-process mobile browser this reintroduces a Spectre-grade timer.
- **Frame-counting XS-leak.** An attacker page embeds `victim.example/search?q=secret` and reads `window.length` (subframe count) to infer whether the query matched — login/admin-status inference with no body read.
- **Missing CORP enables pixel-reading.** A site serves images without CORP; a cross-origin page (pre-Site-Isolation) speculatively includes them to read pixel data via a timing channel.
- **Renderer escape chain.** A V8 type-confusion UAF gives renderer RCE; an IPC/broker bug then escapes Site Isolation — the canonical browser Pwn2Own chain.
- **Sibling-subdomain pivot.** An XSS on `blog.example.com` abuses a `CORP: same-site` resource and a host-only cookie trusted across `*.example.com`, crossing the *site* boundary the app implicitly relied on.

## Related notes

- [[same-origin-policy]] — the innermost boundary and the rule this stack is built on.
- [[cors-misconfiguration]] — the read-relaxation layer; CORS sits alongside CORP/COEP in the cross-origin model.
- [[content-security-policy]] — the in-origin defense layer that complements the cross-origin boundaries.
- [[clickjacking]] — `frame-ancestors`/`X-Frame-Options`, the embedding boundary against UI redress.
- [[csrf]] — SameSite + Fetch Metadata, the request-boundary controls referenced above.
- [[cookies-and-sessions|Cookies and Sessions]] — why cookies are site-keyed and how partitioning (CHIPS) changes that.
- [[use-after-free-and-dangling-pointers|Use-After-Free]] — the renderer-bug half of a sandbox-escape chain.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — the boundary stack is the wall; XS-leaks and escapes are where the operator probes it.

### Suggested future atomic notes

- xs-leaks-and-cross-site-inference
- fetch-metadata-and-resource-isolation-policy
- partitioned-storage-and-chips
- spectre-and-speculative-side-channels
- renderer-sandbox-escapes

> Future atomic notes are listed as `<span class="unresolved-link" title="Unpublished or unresolved: wikilinks">wikilinks</span>` even when the target file does not exist yet, so they register as forward-links in Obsidian.

## References

- **Foundational:** web.dev — Why you need "cross-origin isolated" for powerful features (COOP + COEP) — https://web.dev/articles/coop-coep
- **Foundational:** MDN — Cross-Origin-Resource-Policy (CORP) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy
- **Research / Deep Dive:** XS-Leaks Wiki — https://xsleaks.dev/
- **Foundational:** The Chromium Projects — Site Isolation — https://www.chromium.org/Home/chromium-security/site-isolation/
