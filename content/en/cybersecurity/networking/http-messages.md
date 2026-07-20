---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# HTTP Messages

## Definition

An HTTP message is the unit of data exchanged between client and server — either a *request* (sent client → server) or a *response* (sent server → client). In HTTP/1.x the message is a text stream with strict CRLF framing; in HTTP/2 and HTTP/3 the message is a sequence of binary frames carrying logically equivalent fields. This note focuses on the HTTP/1.1 message format because that is where the security-relevant parsing decisions live, and where every HTTP/1.1-speaking hop in a modern chain is forced to make them.

## Why it matters

Many vulnerabilities are invisible from application code and obvious from the wire. The shape of an HTTP message — *not the framework's interpretation of it* — is what proxies, WAFs, CDNs, and the application server each independently parse. Three things make message-level fluency essential:

- **Every web exploit eventually surfaces as a malformed or ambiguous message.** Smuggling, header-injection, cache poisoning, host-header attacks, and many CRLF-injection bugs are all message-format bugs.
- **Frameworks lie.** `request.headers` is a normalized view; the wire might have duplicates, weird casing, or extra whitespace the framework silently merged or dropped. The bug usually lives in the difference.
- **Two parsers on the same bytes disagree.** Reverse proxy + backend each parse the same message and can reach different conclusions about it. Every disagreement is a candidate vulnerability. See [[reverse-proxies]] for the framing.

This note stays at the *message format* level. [[http-overview]] owns the depth on the protocol lifecycle and version differences. [[request-smuggling]] owns the depth on exploiting parser disagreement. [[http-headers]] owns the depth on individual header fields.

## How it works

Every HTTP/1.1 message has **4 parts**:

1. **Start-line** — for a request, `<method> <request-target> HTTP/<version>`. For a response, `HTTP/<version> <status-code> <reason-phrase>`.
2. **Header section** — zero or more `Name: Value` lines, one per CRLF-terminated line.
3. **Empty line** — a single CRLF separating headers from body. This is the framing signal.
4. **Body** (optional) — bytes whose length is determined by the headers.

A request:

```
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 31
Cookie: session=abc123

{"user":"carlos","password":"x"}
```

The bytes between the start-line and the first CRLFCRLF are headers. The bytes after CRLFCRLF are the body. Everything is text. Everything depends on the parser agreeing with the writer about what counts as a CRLF.

Every HTTP/1.1 parser must answer **3 framing questions** to decode a message. Almost all the security-relevant variation lives in disagreements about the answers:

1. **Where does the start-line end?** First CRLF. Subtleties: bare LF, leading whitespace, weird HTTP version strings, oversized request-line.
2. **Where does the header section end?** First empty line (CRLFCRLF). Subtleties: header-line folding (obsolete but still parsed by some implementations), header lines without a colon, header names with whitespace, repeated headers.
3. **Where does the body end?** Determined by headers, in this priority:
   - `Transfer-Encoding: chunked` → body is a sequence of `<size-hex>\r\n<bytes>\r\n` chunks terminated by `0\r\n\r\n`.
   - else `Content-Length: N` → body is exactly N bytes.
   - else (some methods) → body extends to connection close.
   - else → no body.

The last question is the one that breaks. **Two HTTP/1.1 parsers given the same message can reach different conclusions about where the body ends.** That is the entire substrate of [[request-smuggling]]: when `Content-Length` and `Transfer-Encoding` are both present and one parser prefers one and the other parser prefers the other, the connection is desynchronized.

The bug is rarely in any single parser. The bug is in the **disagreement between two parsers reading the same bytes**.

## Techniques / patterns

What testers look at:

- **Read messages with `curl -v --trace-ascii -` or raw `printf | nc`.** The framework's view of `request.headers` is a sanitized abstraction; the wire is the truth.
- **Look for header duplication.** `Host: a.com\r\nHost: b.com` — which one does the proxy use? Which one does the backend use? Different is exploitable.
- **Look at whitespace in header values.** Trailing OWS, embedded tabs, leading spaces — different parsers normalize differently. `Content-Length: 13` (trailing space) vs `Content-Length:13` (no leading space) vs `Content-Length :13` (space before colon, illegal but accepted by some).
- **Look for both `Content-Length` and `Transfer-Encoding`.** Even if the message is syntactically valid in isolation, this combination *forces* the parser to pick one. Different parsers pick differently. See [[request-smuggling]].
- **Look at line endings.** RFC says CRLF; some parsers accept bare LF; some accept bare CR. A naked LF inside a header value is a smuggling primitive on permissive parsers.
- **Look for case games.** Header names are case-insensitive per spec; some parsers lowercase, some preserve, some hash. `transfer-encoding`, `Transfer-Encoding`, `TRANSFER-ENCODING` may not all be treated the same when normalizing for "is the chunked encoding present?".

## Variants and bypasses

HTTP/1.1 messages can be ambiguous on the wire in **5 distinct classes**. Each is a potential parser-disagreement surface; collectively they cover the bulk of the message-format attack surface.

### 1. Body framing ambiguity (CL vs TE)

Both `Content-Length` and `Transfer-Encoding: chunked` present. Spec says `TE` wins, but real implementations vary, especially when `TE` is malformed (`Transfer-Encoding: chunked\r\n` vs `Transfer-Encoding: x-chunked\r\n` vs `Transfer-Encoding: chunked, identity\r\n`). The disagreement is the smuggling surface. Owns the depth: [[request-smuggling]].

### 2. Header-name canonicalization

Case sensitivity, leading/trailing whitespace, embedded NULs, header-line folding (`obs-fold` per RFC 7230 — obsolete but still accepted by some parsers via continuation lines). Two parsers seeing the same bytes can produce different sets of header names, which is enough to bypass any logic that branches on "is header X present?".

### 3. Line-ending strictness

RFC mandates CRLF; permissive parsers accept bare LF or even bare CR. A header value containing `\n` becomes a new header line on a permissive parser and stays a value on a strict one. Classic CRLF-injection / response-splitting primitive.

### 4. Whitespace handling in/around values

Optional whitespace (OWS) per RFC; in practice, parsers strip differently. Embedded tabs, multiple spaces, trailing whitespace all subtly affect comparisons (`Content-Length: 13` vs `13`). Particularly dangerous for `Transfer-Encoding` where value-parsing variations decide whether the parser sees "chunked" or not.

### 5. Encoding stack (chunked, compression, charsets)

Multiple `Transfer-Encoding` codings (`chunked, gzip`), unsupported codings, and `Content-Encoding` plus `Transfer-Encoding` interactions. Some parsers reject unknown codings; some pass them through; the result-of-decoding can differ per hop.

## Impact

Message-format bugs are typically **substrate bugs** — they enable a higher-level attack rather than landing one directly. Ordered roughly by ceiling:

- **Request smuggling** — front-end and back-end disagree on body framing. Highest impact in this class. Yields request hijack, cache poisoning, auth bypass.
- **Cache poisoning** — proxy and cache key the message differently than the backend processes it. Owns its own depth at [[caching-and-security]].
- **CRLF injection / response splitting** — naked LF in attacker-controlled header value injects a fake header (or a fake response) that some intermediary believes.
- **Header-injection authentication / authorization bypass** — duplicate `Host`, duplicate `Authorization`, duplicate `Cookie` parsed differently between proxy and backend.
- **Detection / WAF evasion** — message reaches the backend in a form the WAF didn't normalize the same way.

## Detection and defense

Ordered by effectiveness:

1.
**Reject ambiguous messages at the edge.**
   The strictest hop in the chain should refuse anything that is not a single canonical form: no duplicate `Host`, no `Content-Length` plus `Transfer-Encoding`, no malformed chunked encoding, no bare LF, no leading/trailing whitespace in header values, no header-line folding. If the edge cannot canonicalize, fail closed. This eliminates entire classes of disagreement before any parser-mismatch matters.

2.
**Use HTTP/2 end-to-end where you control both ends.**
   Binary frame headers carry an explicit length per frame. The whole "where does the body end" framing question disappears. The remaining attack surface is the h2 → h1 downgrade hop; eliminate it by speaking h2 to the origin too.

3.
**Align parsers across hops.**
   Same web-server family and version on both sides where feasible. Most disagreement findings are because one side is permissive and the other is strict on the same input. Audit the diff explicitly.

4.
**Log normalized message shape, not framework abstractions.**
   Log the raw header lines (or a faithful canonicalization). Framework log lines hide the trailing whitespace, the duplicate header, the case game — which is exactly the data forensics needs.

5.
**Treat `request.headers` as a *view*, not the truth.**
   In application code, never branch security decisions on "header X exists." Branch on "edge proxy authoritatively asserted X" — i.e., the value the trusted proxy injected, distinguishable by being on a header name the application never reads from clients directly.

6.
**Cap header count and header-line length at the edge.**
   Big-headers DoS, slowloris-by-headers, and pathological canonicalization costs all become non-issues with a sane cap. Most attacks have to be short to be useful.

### What does not work as a primary defense

- **WAF signatures alone.** WAFs catch known smuggling payload shapes; they do not catch novel parser disagreements or whitespace games. The novel ones are the dangerous ones.
- **Trusting the framework's normalization.** The framework normalizes for *its own* parser. The proxy may have already accepted bytes the framework would have rejected, and forwarded them to the backend without re-canonicalizing.
- **One-time pen-test.** Parsers drift between versions. A clean test today is meaningless after the next Nginx point release. Edge canonicalization needs to be verified continuously.
- **Lowercasing or stripping in application code.** By the time application code runs, a smuggled second request has already been queued.

## Practical labs

Stock printf, nc, openssl, and curl. Burp Repeater is the production tool for this work but the basics need no GUI.

### Send a clean raw HTTP/1.1 request

```
# Plain HTTP — bypasses curl normalization, lets you see exact server framing
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | nc example.com 80

# HTTPS — same idea wrapped in TLS
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect example.com:443 -servername example.com 2>/dev/null
```

### Probe header-name canonicalization

```
# Case-game probe — does the backend treat these as the same?
curl -sI https://example.com/ -H 'X-API-Key: a' -H 'x-api-key: b' -H 'X-Api-Key: c'

# Duplicate Host — which one wins?
printf 'GET / HTTP/1.1\r\nHost: legit.example.com\r\nHost: evil.example\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect legit.example.com:443 -servername legit.example.com 2>/dev/null

# Duplicate Cookie / Authorization — which one is read?
curl -sI https://example.com/me -H 'Authorization: Bearer real' -H 'Authorization: Bearer fake'
```

### Probe whitespace and line-ending strictness

```
# Bare LF instead of CRLF — does the server accept this as a valid line terminator?
printf 'GET / HTTP/1.1\nHost: example.com\nConnection: close\n\n' \
  | nc example.com 80

# Whitespace games on Content-Length / Transfer-Encoding
printf 'POST / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 13 \r\nTransfer-Encoding:  chunked\r\nConnection: close\r\n\r\n0\r\n\r\nSMUGGLED' \
  | nc example.com 80
```

### Probe body-framing ambiguity (CL/TE)

```
# Both headers present — different parsers prefer different ones.
# This is the smuggling primitive; only run it against systems you own or
# have written authorization to test. See <a href="../web-security/request-smuggling.html">request-smuggling</a> for the full
# methodology and HTTP Request Smuggler / smuggler.py for systematic probing.
printf 'POST / HTTP/1.1\r\nHost: lab.example.com\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nXYZ' \
  | nc lab.example.com 80
```

### Look at what a real request looks like on the wire

```
# Capture a curl request as it leaves your machine
curl -v --trace-ascii /tmp/curl-trace https://example.com/login -d 'user=a&pass=b' >/dev/null 2>&1
less /tmp/curl-trace
# The "=> Send header" / "=> Send data" sections are the literal bytes on the wire.
```

## Practical examples

- A login form posts to a backend that reads `request.body` after Express parses it. A smuggled second request sneaks in via `Transfer-Encoding`/`Content-Length` mismatch and hijacks the next user's session cookie before the framework even sees it.
- An app stores `request.headers['x-api-key']` for audit logs. The proxy normalizes header names to lowercase; the application uses Express which preserves case for unknown headers. Two different audit-log entries record the same request differently.
- A reverse proxy strips one `Cookie` header and forwards the rest; the application concatenates all `Cookie` headers into one. Authentication state ends up depending on which CDN node served the request.
- A WAF rejects requests containing `Transfer-Encoding: chunked` but a permissive backend accepts `Transfer-Encoding:  chunked` (extra whitespace). Smuggling payloads pass the WAF and reach the backend.
- An attacker injects `\r\n` into a user-supplied `Location` redirect parameter. The application emits `Location: https://example.com/...\r\nSet-Cookie: admin=1`, and a permissive client honors the injected `Set-Cookie`. Classic CRLF injection / response splitting.
- A logging pipeline parses raw HTTP messages from access logs and uses the access log's `User-Agent` value as a string. An attacker sends `User-Agent: x\nINJECTED LINE`. The log parser sees two lines; the rest of the pipeline is poisoned.

## Related notes

- [[http-overview]] — protocol model, lifecycle, version differences. The "what HTTP is" half of the pair this note completes.
- [[http-headers]] — semantic meaning of specific header fields that steer security behavior.
- [[reverse-proxies]] — trust translation between two HTTP parsers; the "two parsers, same bytes" framing.
- [[client-ip-trust]] — the trust-disagreement specialization for forwarded-IP headers.
- [[caching-and-security]] — cache key derivation reads the same message; framing differences become poisoning.
- [[packet-analysis]] — observe message bytes on the wire when curl/nc are not enough.
- [[wireshark-workflows]] — capture and inspect HTTP messages live.
- [[request-smuggling|Request smuggling]] — owns the depth on body-framing exploitation.
- [[cors-misconfiguration|CORS misconfiguration]] — `Origin`/`Access-Control-Allow-Origin` header semantics.

### Suggested future atomic notes

- crlf-injection
- response-splitting
- chunked-encoding-quirks
- header-folding-obs-fold
- duplicate-header-resolution
- content-length-vs-transfer-encoding-history

## References

- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Foundational:** RFC 9112 (HTTP/1.1 Message Syntax) — https://datatracker.ietf.org/doc/html/rfc9112
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
