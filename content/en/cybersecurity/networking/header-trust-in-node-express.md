---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Header Trust in Node Express

## Definition

Header trust in Node/Express is the decision of whether framework APIs such as `req.ip`, `req.ips`, `req.hostname`, and `req.protocol` should believe proxy-provided HTTP headers such as `X-Forwarded-For`, `X-Forwarded-Host`, `X-Forwarded-Proto`, or `Forwarded`.

## Why it matters

Express applications often sit behind Nginx, Cloudflare, a load balancer, a CDN, or a platform router. In that shape, the TCP peer is the proxy, while the original client identity is carried in headers. If Express trusts those headers from the wrong network path, an attacker can spoof identity, bypass rate limits, poison logs, influence redirects, or reach IP-allowlisted behavior.

This is the common mistake the Mirror learning exercise exposed: old proxy code read `cf-connecting-ip` and `x-forwarded-for` as if they were facts, without proving the request arrived through the trusted proxy that should have authored them.

## How it works

Express has **3 identity layers**:

1.
**Socket identity**
   `req.socket.remoteAddress` is the network peer connected to the Node process. Behind a proxy, this is usually the proxy IP, not the user.

2.
**Forwarded-header identity**
   Headers such as `X-Forwarded-For`, `X-Real-IP`, `CF-Connecting-IP`, and RFC 7239 `Forwarded` claim the original client or previous hops. These are ordinary HTTP headers until a trusted proxy boundary gives them meaning.

3.
**Framework-decided identity**
   `req.ip`, `req.ips`, `req.hostname`, and `req.protocol` may change depending on Express `trust proxy` configuration. This value is convenient, but it is only as correct as the proxy trust model.

Unsafe pattern:

```
function getClientIp(req) {
  return (
    req.headers["cf-connecting-ip"] ||
    req.headers["x-forwarded-for"] ||
    req.socket.remoteAddress ||
    req.ip
  );
}
```

Safer shape:

```
app.set("trust proxy", "loopback, linklocal, uniquelocal");

app.use((req, res, next) => {
  res.locals.clientIp = req.ip;
  res.locals.tcpPeer = req.socket.remoteAddress;
  res.locals.forwardedFor = req.get("x-forwarded-for") || null;
  next();
});
```

The bug is not “using `X-Forwarded-For`.” The bug is believing a header before proving which network hop produced or normalized it.

## Techniques / patterns

- Find every use of `req.ip`, `req.ips`, `req.hostname`, `req.protocol`, `req.headers["x-forwarded-for"]`, `req.headers["x-real-ip"]`, `CF-Connecting-IP`, `True-Client-IP`, and `Forwarded`.
- Identify the real deployment chain: internet → CDN → load balancer → app proxy → Express.
- Check `app.set("trust proxy", ...)` and whether it matches the actual number or CIDR range of trusted proxy hops.
- Compare raw headers, `req.socket.remoteAddress`, and Express-decided values in a local `/whoami` endpoint.
- Look for security decisions based on client IP: admin allowlists, geo-blocking, fraud scoring, rate limiting, password reset throttling, and audit logs.
- Treat direct-origin reachability as a separate test: if the origin is reachable without the intended proxy, forwarded-header trust usually collapses.

## Variants and bypasses

Header trust in Express fails in **5 common ways**.

### 1. Trust disabled but raw headers read manually

Express may be safely configured with `trust proxy` disabled, but application code bypasses the framework and reads `req.headers["x-forwarded-for"]` directly. This recreates the bug under a different name.

### 2. Boolean `trust proxy: true`

A boolean `true` tells Express to trust proxy headers broadly. If the app is reachable directly, the leftmost `X-Forwarded-For` value can become attacker-controlled identity.

### 3. Wrong hop count

`trust proxy: 1` is correct only when exactly one trusted proxy sits in front of Express. Multi-CDN, service mesh, load balancer, and platform-router chains need explicit modeling. The wrong number chooses the wrong IP.

### 4. Header-name split brain

The edge proxy overwrites `X-Forwarded-For`, but the app reads `CF-Connecting-IP`, `True-Client-IP`, `X-Client-IP`, or `Forwarded`. Attackers look for the unsanitized sibling header.

### 5. Internal state hidden in headers

Middleware sets fake request headers such as `x-is-proxy-header` or `x-country-not-allowed-header`, then a later handler reads those names as internal state. It works until a future route, proxy, or middleware lets a client-controlled header collide with that namespace.

## Impact

Ordered roughly by severity:

- **IP allowlist bypass.** Admin paths or internal-only behavior become reachable by spoofing loopback, private, or trusted addresses.
- **Rate-limit bypass.** Login, token, and API limits keyed only on `req.ip` can be rotated by changing forwarded headers.
- **Audit-log poisoning.** Incident response follows a forged “client IP” rather than the observed TCP peer and proxy path.
- **Geo-policy bypass or false blocking.** Country checks become attacker-controlled or unreliable.
- **Risk-scoring distortion.** Fraud, bot, and abuse models ingest spoofed network identity.
- **Redirect and host confusion.** `X-Forwarded-Proto` and forwarded host values can affect URL generation and callback logic when trusted too broadly.

## Detection and defense

Ordered by effectiveness:

1.
**Model the proxy chain explicitly**
   Write down every trusted hop and whether it overwrites or appends forwarding headers. Express configuration should encode that exact model, not a vague “behind proxy” assumption.

2.
**Use Express `trust proxy` narrowly**
   Prefer exact hop counts or CIDR ranges for known proxies. Boolean `true` is only safe when direct access is impossible and the last proxy reliably strips/overwrites inbound forwarding headers.

3.
**Stop reading raw forwarding headers for identity**
   Centralize client-IP derivation once, after Express proxy trust is configured. Raw headers can still be logged as claims, but they should not become identity by themselves.

4.
**Block direct origin reachability**
   If the app should only receive traffic from a proxy or load balancer, enforce that with firewall/security-group rules and application-level rejection of unexpected TCP peers.

5.
**Log observed and claimed identity separately**
   Store `tcp_peer`, `express_client_ip`, and `forwarded_for_claim` as different fields. This preserves forensic truth without pretending all values have the same trust level.

6.
**Keep internal state out of request headers**
   Use `res.locals`, request-local symbols, typed metadata, or explicit error subclasses. Internal control signals should not reuse HTTP header names.

### What does not work as a primary defense

- **Checking only that `X-Forwarded-For` exists.** Existence proves nothing about who set it.
- **Trusting Cloudflare-style headers without checking Cloudflare source ranges.** Header names do not authenticate the network path.
- **Using `req.ip` blindly.** `req.ip` is a framework decision affected by `trust proxy`; it is not automatically the network truth.
- **Relying on a WAF rule that strips one header.** Attackers can try sibling headers unless the whole forwarding namespace is normalized.
- **Treating IP allowlists as authentication.** IP checks are a layer, not a substitute for user, device, or service identity.

## Practical labs

### Compare raw and framework identity

```
app.get("/whoami", (req, res) => {
  res.json({
    socketRemoteAddress: req.socket.remoteAddress,
    expressIp: req.ip,
    expressIps: req.ips,
    xForwardedFor: req.get("x-forwarded-for") || null,
    forwarded: req.get("forwarded") || null,
    cfConnectingIp: req.get("cf-connecting-ip") || null
  });
});
```

The result shows which values are observed network facts and which are client-supplied claims.

### Test direct header spoofing

```
curl -s http://localhost:3000/whoami \
  -H "X-Forwarded-For: 127.0.0.1" \
  -H "CF-Connecting-IP: 10.0.0.5" | jq
```

If a security decision changes from this alone, the app is trusting headers from the wrong path.

### Compare `trust proxy` modes

```
// Run the same /whoami route with each setting.
app.set("trust proxy", false);
app.set("trust proxy", 1);
app.set("trust proxy", "loopback, linklocal, uniquelocal");
```

The difference teaches why Express proxy trust is deployment-specific.

### Search a codebase for raw header trust

```
rg -n "x-forwarded-for|x-real-ip|cf-connecting-ip|true-client-ip|forwarded|req\\.ip|trust proxy" src
```

Every match is either identity derivation, telemetry, or a bug candidate; classify it before changing behavior.

### Store claims separately

```
request_id:
tcp_peer:
express_client_ip:
forwarded_for_claim:
trusted_proxy_config:
security_decision:
```

This evidence card prevents logs from flattening claims and facts into one misleading field.

## Practical examples

- An Express login limiter keys attempts by `req.headers["x-forwarded-for"]`; attackers rotate that header and bypass the per-IP limit.
- A dashboard checks `req.ip === "127.0.0.1"` after `trust proxy: true`; a direct request with `X-Forwarded-For: 127.0.0.1` reaches admin-only behavior.
- A Cloudflare-fronted origin leaks its direct IP; attackers connect directly and send `CF-Connecting-IP` manually.
- A geolocation middleware blocks or redirects users based on an attacker-supplied forwarded IP.
- A middleware sets `req.headers["x-blocked-user-agent-header"]` internally; later refactors make it unclear whether that flag is client-supplied or server-owned.

## Related notes

- [[client-ip-trust|Client IP Trust]]
- [[reverse-proxies|Reverse Proxies]]
- [[http-headers|HTTP Headers]]
- [[api-rate-limiting|API Rate Limiting]]
- [[test-client-ip-spoofing|Test Client IP Spoofing]]

### Suggested future atomic notes

- trust-proxy-configuration
- forwarded-header-spec
- origin-ip-discovery
- express-security-middleware

## References

- **Official Tool Docs:** Express behind proxies — https://expressjs.com/en/guide/behind-proxies.html
- **Foundational:** MDN `X-Forwarded-For` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Foundational:** RFC 7239: Forwarded HTTP Extension — https://www.rfc-editor.org/rfc/rfc7239
