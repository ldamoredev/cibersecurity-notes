---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Wireshark Workflows

## Definition

Wireshark is a packet capture and protocol analysis tool used to inspect network traffic, reconstruct conversations, apply protocol-aware filters, and turn packet-level evidence into debugging or security conclusions.

## Why it matters

Browser DevTools and logs show interpreted behavior. Wireshark shows the conversation below those abstractions: DNS lookups, TCP handshakes, TLS negotiation, HTTP messages when visible, resets, retransmissions, and timing.

This note owns the Wireshark workflow. [[packet-analysis]] owns the broader reasoning model for packet evidence.

## How it works

A useful Wireshark workflow has **5 stages**:

1. **Choose capture point.** Client, proxy, backend, container, VPN, or gateway.
2. **Capture narrowly.** Limit by interface, time, host, port, or protocol where possible.
3. **Apply display filters.** Use filters to isolate DNS, TCP streams, TLS handshakes, HTTP messages, or a target host.
4. **Follow conversations.** Reconstruct TCP streams, inspect protocol fields, and compare request/response sequence.
5. **Export evidence.** Save packets, screenshots, field values, or filtered PCAPs with timestamps and context.

Example filters:

```
dns
tls.handshake
http
tcp.stream eq 3
ip.addr == 10.0.0.5
tcp.port == 443
```

The tool is only as good as the question and capture point. A clean filter cannot fix a capture taken from the wrong side of the proxy.

## Techniques / patterns

Use Wireshark to:

- follow TCP streams for plaintext HTTP labs
- inspect TLS SNI, ALPN, certificate exchange, version, and cipher metadata
- observe DNS questions and answers before an HTTP request
- distinguish refused, filtered, reset, and timed-out connections
- compare `curl`, browser, and application client behavior
- verify whether a proxy or load balancer changed headers or paths
- identify retransmissions, duplicate ACKs, and latency gaps
- export minimal filtered captures for a report

## Variants and bypasses

Wireshark work splits into **6 workflow types**.

### 1. Local client capture

Captures what the client sends and receives. Best for DNS, TLS metadata, and browser vs curl comparisons. It does not prove what a backend saw after intermediaries.

### 2. Server-side capture

Captures what arrives at the service. Best for proxy normalization, source IP, and plaintext internal traffic. It may miss original client behavior.

### 3. Gateway or span-port capture

Captures traffic crossing a boundary. Powerful for segmentation and egress review, but often noisy and sensitive.

### 4. Decrypted TLS workflow

Uses key logs or controlled interception to inspect HTTPS payloads. Useful in labs; sensitive and authorization-heavy in production.

### 5. Protocol-follow workflow

Uses "Follow TCP Stream" or protocol views to reconstruct one conversation. Best for HTTP, SMTP, Redis-like plaintext protocols, and raw labs.

### 6. Statistics workflow

Uses Conversations, Endpoints, I/O Graphs, and Expert Info to understand volume, errors, retransmissions, and timing patterns.

## Impact

Ordered roughly by severity:

- **Evidence of plaintext sensitive traffic.** Shows credentials, cookies, or tokens crossing unencrypted links.
- **Proof of boundary failure.** Reveals direct backend access, missing proxy rewrite, or unexpected source IP.
- **Exploit-debugging clarity.** Confirms whether payload bytes survived the path.
- **DNS/SSRF insight.** Shows what a runtime actually resolved and contacted.
- **Operational root cause.** Exposes resets, retransmissions, MTU issues, handshake failures, and timeouts.
- **Training value.** Builds intuition for how protocols behave outside framework abstractions.

## Detection and defense

Ordered by effectiveness:

1.
**Capture only what the question requires.**
   Narrow captures reduce noise and lower the chance of collecting secrets. Start with one host, one port, and one action.

2.
**Record capture context.**
   Note interface, host, time, command/browser action, source network, and expected behavior. Without context, a PCAP is hard to interpret later.

3.
**Use display filters before drawing conclusions.**
   Filter by stream, host, and protocol. Many apparent patterns disappear once unrelated traffic is removed.

4.
**Correlate with application and proxy logs.**
   Wireshark shows packets; logs show application interpretation. Security conclusions usually need both.

5.
**Protect PCAPs as sensitive artifacts.**
   Captures may include cookies, bearer tokens, internal hostnames, IPs, and payloads. Redact or filter before sharing.

6.
**Use official dissectors but validate assumptions.**
   Wireshark decodes many protocols, but malformed traffic or custom protocols may be misinterpreted. When stakes are high, inspect bytes.

### What does not work as a primary defense

- **Looking only at summary rows.** The important detail is often in expanded protocol fields or stream reconstruction.
- **Using display filters as capture filters.** Display filters hide packets after capture; they do not reduce what was collected.
- **Capturing on the wrong interface.** VPNs, containers, loopback, and Wi-Fi/Ethernet interfaces see different traffic.
- **Assuming encrypted means unknowable.** TLS metadata still reveals SNI, ALPN, timing, IPs, and certificates.
- **Sharing full PCAPs in tickets.** Export filtered packets or redacted evidence whenever possible.

## Practical labs

Run only in an owned lab or authorized environment.

### Capture DNS plus HTTPS for one page load

```
Display filters:
dns
tls.handshake
ip.addr == <target-ip>
```

Load the site once, then inspect DNS query, TCP connect, TLS ClientHello, ALPN, and certificate.

### Follow a plaintext HTTP stream

```
printf 'GET / HTTP/1.1\r\nHost: lab.local\r\nConnection: close\r\n\r\n' | nc lab.local 80
```

In Wireshark: right-click packet → Follow → TCP Stream.

### Compare browser and curl

```
curl -skI https://app.example.com/
```

Capture both browser and curl requests. Compare DNS, SNI, ALPN, headers where visible, and connection reuse.

### Inspect TLS SNI and ALPN

```
Filter:
tls.handshake.extensions_server_name or tls.handshake.extensions_alpn
```

Useful when debugging CDN, load-balancer, HTTP/2, or origin-routing behavior.

### Find resets and retransmissions

```
Filters:
tcp.flags.reset == 1
tcp.analysis.retransmission
tcp.analysis.duplicate_ack
```

These filters explain many "flaky app" symptoms that are really network-path behavior.

### Export a minimal evidence capture

```
1. Apply a display filter for the target stream or host.
2. File → Export Specified Packets.
3. Export displayed packets only.
4. Store with timestamp, viewpoint, and test action.
```

## Practical examples

- A capture shows the browser negotiated HTTP/2 at the edge, while backend logs show HTTP/1.1 from the proxy.
- DNS queries reveal the app contacts `metadata.google.internal` during an SSRF lab.
- A TCP reset from a firewall explains why Nmap reports a port as closed from one network and filtered from another.
- "Follow TCP Stream" shows an extra `Host` header in a raw request-smuggling lab.
- TLS SNI shows a client connecting to the wrong virtual host after a DNS change.

## Related notes

- [[packet-analysis]] — reasoning model for packet evidence.
- [[http-messages]] — exact HTTP message bytes.
- [[dns-resolution]] — DNS packets before connections.
- [[tls-https]] — TLS handshake interpretation.
- [[tcp-ip-basics]] — connection and routing foundations.
- [[reverse-proxies]] — compare client-side and backend-side captures.

### Suggested future atomic notes

- wireshark-display-filters
- wireshark-tls-analysis
- follow-tcp-stream
- pcap-redaction
- tcp-retransmission-analysis
- browser-vs-curl-captures

## References

- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Official Tool Docs:** Wireshark display filter reference — https://www.wireshark.org/docs/dfref/
- **Official Tool Docs:** Wireshark display filters man page — https://www.wireshark.org/docs/man-pages/wireshark-filter.html
