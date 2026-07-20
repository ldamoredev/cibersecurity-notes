---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Caching and Security

## Definition

Caching is the reuse of previously generated responses by browsers, CDNs, reverse proxies, shared intermediaries, or application layers. Caching becomes a security issue when a response is stored, keyed, varied, or invalidated differently than the application expects.

## Why it matters

Caching sits between HTTP semantics and infrastructure behavior. A response that is safe for one user, language, host, or authorization context may be unsafe for another. Cache bugs are especially dangerous because one request can affect many later users.

The recurring lesson: **the cache key is part of the security boundary**. If the origin reads a signal that the cache does not vary on, the cache may serve one user's interpretation to another user.

## How it works

HTTP caching answers **4 questions**:

1. **Can this response be stored?** `Cache-Control`, status code, method, authentication, and CDN policy decide whether a cache may keep it.
2. **Who may store it?** Browser cache, shared proxy, CDN edge, application cache, and surrogate cache have different risk profiles.
3. **What is the cache key?** URL is usually the baseline, but `Host`, query string, selected headers, cookies, and CDN rules may be included or ignored.
4. **When is it reused or invalidated?** TTL, `max-age`, `s-maxage`, `ETag`, `Last-Modified`, purge APIs, and revalidation decide lifetime.

Example sensitive response:

```
GET /account HTTP/1.1
Host: app.example.com
Cookie: __Host-session=alice
Accept-Language: en
```

```
HTTP/1.1 200 OK
Cache-Control: public, max-age=600
Content-Type: text/html

Alice's billing dashboard
```

If a shared CDN stores that response under only `Host + path`, the next user requesting `/account` may receive Alice's page. The bug is not "a CDN exists"; the bug is letting personalized content enter a shared cache without a safe key or `no-store`.

## Techniques / patterns

Attackers and defenders inspect:

- `Cache-Control`, `Pragma`, `Expires`, `Age`, `ETag`, `Last-Modified`, and `Vary`
- CDN headers such as `X-Cache`, `CF-Cache-Status`, `X-Served-By`, `X-Cache-Hits`, `Fastly-Cachetype`
- authenticated responses that lack `Cache-Control: no-store`
- responses that vary by `Cookie`, `Authorization`, `Origin`, `Accept-Language`, `X-Forwarded-Host`, or device headers
- unkeyed inputs reflected into responses
- redirects and errors cached more broadly than intended
- path/query normalization differences between cache and origin
- purge and invalidation workflows for sensitive content

## Variants and bypasses

Caching failures fall into **6 practical classes**.

### 1. Sensitive response caching

Authenticated pages, account data, API responses, password-reset pages, or admin views are stored by a browser or shared intermediary. The defense is `Cache-Control: no-store` on truly sensitive responses, not hoping the cache understands auth.

### 2. Web cache poisoning

An attacker changes an unkeyed input that the origin reflects, then the cache stores the poisoned output under a key that later victims hit. Common inputs: `X-Forwarded-Host`, `Host`, `X-Original-URL`, `Accept-Language`, query parameters, and path normalization quirks.

### 3. Cache deception

The cache believes a request is for a static resource, while the origin serves dynamic personalized content. Classic shape: `/account/settings/profile.css` gets cached because the path looks static.

### 4. Key mismatch across layers

Browser, CDN, reverse proxy, and application caches key differently. One layer varies on `Accept-Encoding`, another on `Cookie`, another on URL only. The security bug appears at the layer that ignores a signal the origin trusts.

### 5. Stale authorization state

Permissions, membership, feature flags, or object ownership change, but cached responses remain valid. This can expose revoked access or old data after logout, role removal, or tenant migration.

### 6. Error and redirect caching

Errors, redirects, and maintenance pages are cached too broadly. A temporary 302 to a hostile host, a 500 with stack details, or an auth failure page can become persistent for many users.

## Impact

Ordered roughly by severity:

- **Cross-user data disclosure.** Personalized responses served from shared cache to the wrong user.
- **Stored client-side compromise.** Poisoned cached JavaScript, redirects, or HTML affect many victims.
- **Authorization bypass by stale content.** Revoked or tenant-specific content remains available after permissions change.
- **Credential or token exposure.** Reset links, OAuth callbacks, signed URLs, or bearer-bearing responses are cached.
- **Persistent misinformation or defacement.** Poisoned content survives until TTL expiry or purge.
- **Incident-response drag.** Purging distributed caches is slower and harder than fixing origin code.

## Detection and defense

Ordered by effectiveness:

1.
**Mark sensitive responses `Cache-Control: no-store`.**
   Account, billing, admin, session-bearing, token-bearing, and user-specific API responses should not enter shared or browser caches. `no-store` is the clearest directive because it tells caches not to retain the response at all.

2.
**Make cache keys explicit and reviewed.**
   Document what each cache layer keys on: host, path, query string, selected headers, cookies, encoding, device, locale. Any origin-read signal that is absent from the key is a poisoning candidate.

3.
**Disable shared caching for authenticated traffic by default.**
   `Authorization` and `Cookie` should normally push responses out of shared caching unless the route is deliberately public and the key policy is proven safe.

4.
**Use `Vary` only when the cache actually honors it.**
   `Vary: Origin`, `Vary: Accept-Language`, or `Vary: Cookie` can be correct, but only if every relevant intermediary respects it. CDN rules often override or compress `Vary` behavior.

5.
**Normalize at the edge and origin consistently.**
   Path decoding, trailing slashes, semicolons, case, query normalization, and file-extension handling should agree. Cache deception and poisoning often come from mismatched normalization.

6.
**Purge by surrogate keys or precise identifiers.**
   Sensitive invalidation should not depend on broad wildcard purges or waiting out TTLs. Use route/object surrogate keys where the CDN supports them.

7.
**Log cache status with security context.**
   Record HIT/MISS/BYPASS, cache key inputs, authenticated vs anonymous state, and selected headers. Without cache visibility, leaks look like random authorization bugs.

### What does not work as a primary defense

- **Assuming `private` means no browser cache.** `private` prevents shared caches from storing; browser caches may still store. Use `no-store` for truly sensitive content.
- **Relying on `Vary: *`.** Many intermediaries do not handle it as a useful security boundary. Use explicit caching policy instead.
- **Putting secrets in query strings and hoping HTTPS hides them.** URLs appear in caches, logs, browser history, referers, and CDN tooling.
- **Trusting CDN defaults.** CDN products are optimized for performance. Security-sensitive cache behavior must be configured intentionally.
- **Testing only one request.** Cache bugs need at least two perspectives: poison/store as one request, then retrieve as another user or header set.

## Practical labs

Run only against systems you own or are authorized to test.

### Inventory cache-related headers

```
curl -skI https://app.example.com/ | rg -i \
  '^(cache-control|pragma|expires|age|etag|last-modified|vary|x-cache|cf-cache-status|x-served-by):'
```

Record whether the response is public, private, no-store, revalidated, or CDN-served.

### Compare anonymous and authenticated responses

```
curl -skI https://app.example.com/account | rg -i '^(cache-control|vary|x-cache|cf-cache-status):'
curl -skI -b /tmp/app.cookies https://app.example.com/account | rg -i '^(cache-control|vary|x-cache|cf-cache-status):'
```

Authenticated responses should not be stored by shared caches unless explicitly designed and keyed safely.

### Probe unkeyed header reflection

```
curl -sk https://app.example.com/ \
  -H 'X-Forwarded-Host: poison.example' \
  -H 'X-Original-URL: /poison-probe' \
  | rg -i 'poison.example|poison-probe'
```

If the response reflects the header, check whether the cache key includes that header before considering impact.

### Test a two-request poisoning shape

```
url='https://app.example.com/?cache_probe=1'

curl -skI "$url" -H 'X-Forwarded-Host: poison.example' | rg -i 'x-cache|cf-cache-status|age'
curl -sk  "$url" | rg -i 'poison.example|x-cache|cf-cache-status|age'
```

The first request attempts to store; the second checks whether an unmodified victim-shaped request receives attacker-influenced content.

### Check cache deception candidates

```
for suffix in profile.css account.js settings.png; do
  curl -skI "https://app.example.com/account/$suffix" | rg -i 'http/|content-type|cache-control|x-cache|cf-cache-status'
done
```

Watch for dynamic content served under static-looking paths with cacheable headers.

### Inspect invalidation behavior

```
# Fetch, change the underlying object through the app, then fetch again.
curl -skI https://app.example.com/resource/123 | rg -i 'etag|last-modified|cache-control|x-cache|age'
```

The point is to compare expected freshness with actual cache reuse, not just headers in isolation.

## Practical examples

- `/account` returns `Cache-Control: public, max-age=600`, and a CDN serves one user's dashboard to another.
- The origin reflects `X-Forwarded-Host` into canonical links, but the CDN keys only on URL, creating web cache poisoning.
- `/profile/avatar/../../settings.css` is normalized differently by cache and origin, causing dynamic account data to be cached as CSS.
- A logout revokes the session but the browser back button shows cached billing data.
- A redirect from `/login` to a tenant-specific domain is cached and reused across tenants.

## Related notes

- [[http-headers]] — `Cache-Control`, `Vary`, and cache-status header semantics.
- [[http-messages]] — the raw headers and request shape the cache parses.
- [[reverse-proxies]] — caches often live at the proxy/CDN boundary.
- [[client-ip-trust]] — forwarded headers become poisoning inputs when unkeyed.
- [[cookies-and-sessions]] — personalized cookie-backed responses must not be cached incorrectly.
- [[load-balancers]] — entrypoints may route to different cache layers.
- [[request-smuggling|Request Smuggling]] — parser disagreement can poison queues and caches.

### Suggested future atomic notes

- [[web-cache-poisoning]]
- cache-deception
- cache-control-semantics
- vary-header
- surrogate-keys
- cdn-cache-key-design

## References

- **Foundational:** MDN HTTP caching — https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- **Foundational:** MDN Cache-Control — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
- **Testing / Lab:** PortSwigger Web Cache Poisoning — https://portswigger.net/web-security/web-cache-poisoning
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning
