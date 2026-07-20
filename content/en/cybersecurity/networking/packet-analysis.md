---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Packet Analysis

## Definition

Packet analysis is the practice of inspecting captured network packets, streams, and protocol conversations to understand what systems actually sent, received, retransmitted, negotiated, or rejected on the wire.

## Why it matters

Application logs show what code thinks happened. Packet captures show what crossed the network boundary. That distinction matters for proxy bugs, TLS negotiation, DNS resolution, retries, redirects, session cookies, firewall behavior, and parser disagreement.

This note owns the reasoning model for packet evidence. [[wireshark-workflows]] owns the Wireshark tool workflow.

## How it works

Packet analysis follows **5 steps**:

1. **Define the question.** Example: "Did the client send this header?" or "Did DNS resolve to the private address?"
2. **Capture at the right point.** Client, proxy, backend, container, or gateway each sees different traffic.
3. **Filter to the relevant flow.** Use host, port, protocol, time window, and stream identifiers.
4. **Reconstruct the conversation.** Follow TCP streams, TLS handshakes, DNS queries, HTTP requests, or retransmissions.
5. **Compare expectation with observation.** Convert packet evidence into a security or architecture conclusion.

Example reasoning:

```
Expected: app sends HTTPS to origin.
Observed: client -> proxy uses TLS, proxy -> origin uses plaintext HTTP.
Conclusion: edge TLS exists, but origin hop is not encrypted.
```

The bug often lives in the difference between the path engineers describe and the packets the path actually carries.

## Techniques / patterns

Analysts inspect:

- DNS query/response pairs before connection attempts
- TCP SYN/SYN-ACK/RST behavior for reachability and filtering
- TLS ClientHello, SNI, ALPN, certificate chain, and version/cipher negotiation
- HTTP request/response headers and redirects when plaintext or decrypted
- retransmissions, resets, timeouts, and handshake failures
- source/destination IPs and ports across NAT, proxy, and container boundaries
- protocol mismatches: HTTP on TLS ports, TLS on unexpected ports, non-HTTP behind HTTP assumptions
- before/after captures around a firewall, proxy, or config change

## Variants and bypasses

Packet analysis has **6 evidence classes**.

### 1. Reachability evidence

SYN, SYN-ACK, RST, ICMP unreachable, and timeout behavior show whether a path is open, closed, filtered, or silently dropped from one viewpoint.

### 2. Naming evidence

DNS packets reveal which name was resolved, by which resolver, to which answer, and whether the runtime context sees a different result than the tester.

### 3. Transport evidence

TCP retransmissions, resets, window behavior, and connection reuse explain failures that app logs flatten into "network error."

### 4. TLS evidence

SNI, ALPN, certificate, TLS version, and cipher negotiation reveal edge identity, downgrade behavior, and protocol support.

### 5. Application-message evidence

When traffic is plaintext or decrypted, HTTP messages show exact headers, body framing, cookies, and proxy transformations.

### 6. Timing and sequence evidence

Packet order, gaps, retries, and concurrent streams help debug race conditions, request smuggling symptoms, and load-balancer behavior.

## Impact

Ordered roughly by severity:

- **Trust-boundary proof.** Captures can prove direct backend access, plaintext internal hops, or unexpected proxy rewriting.
- **Credential or sensitive-data exposure.** Packet evidence can show secrets crossing plaintext paths or logs.
- **Exploit confirmation.** Smuggling, SSRF, header injection, and cache bugs often need wire-level proof.
- **Segmentation validation.** Packet behavior shows whether firewall/security-group rules block or pass traffic.
- **Incident reconstruction.** Captures preserve evidence when app logs are incomplete or misleading.
- **False-assumption removal.** Packet analysis often disproves "the browser/proxy/framework would never send that."

## Detection and defense

Ordered by effectiveness:

1.
**Capture from the boundary that answers the question.**
   Client-side captures cannot prove what the backend received after a proxy. Backend captures cannot prove what the browser sent. Pick the point where the disputed transformation happens.

2.
**Minimize capture scope.**
   Use tight time windows, interfaces, hosts, and ports. Smaller captures are easier to reason about and reduce accidental collection of sensitive data.

3.
**Treat captures as sensitive evidence.**
   PCAPs may contain credentials, cookies, internal IPs, URLs, and payloads. Store, redact, and share them like secrets.

4.
**Correlate with logs and request IDs.**
   Packet evidence is strongest when tied to application logs, proxy logs, timestamps, and request identifiers.

5.
**Prefer reproducible captures.**
   Save the command/filter, target, viewpoint, and expected behavior. Future reviewers should be able to repeat the observation.

6.
**Use decrypted capture only with explicit authorization.**
   TLS key logging, proxy interception, or server-side plaintext capture can be powerful and sensitive. Use it only in owned lab or approved debugging contexts.

### What does not work as a primary defense

- **Assuming logs equal wire truth.** Logs reflect parsed interpretation after transformations.
- **Capturing at the wrong hop.** A client capture cannot show backend-only proxy mutations.
- **Collecting huge PCAPs without a question.** More packets usually means less clarity.
- **Ignoring time synchronization.** Packet/log correlation fails if clocks drift.
- **Sharing raw captures casually.** PCAPs are often credential dumps in disguise.

## Practical labs

Run on systems you own or are authorized to inspect.

### Capture a narrow HTTP/TLS session

```
sudo tcpdump -i any -w /tmp/app.pcap 'host app.example.com and port 443'
curl -skI https://app.example.com/
```

Open `/tmp/app.pcap` in Wireshark and inspect DNS/TCP/TLS stages.

### Observe DNS before HTTP

```
sudo tcpdump -i any -n 'port 53' &
dig app.example.com
curl -skI https://app.example.com/
```

Confirm which resolver and answer the client actually used.

### Compare open vs closed ports

```
sudo tcpdump -i any -n 'host app.example.com and tcp' &
nc -vz app.example.com 443
nc -vz app.example.com 5432
```

Look for SYN-ACK vs RST vs timeout behavior.

### Inspect TLS metadata

```
openssl s_client -connect app.example.com:443 -servername app.example.com -alpn h2,http/1.1 </dev/null
```

Pair this with a packet capture to observe SNI, ALPN, and certificate exchange.

### Follow an HTTP stream in plaintext lab traffic

```
printf 'GET / HTTP/1.1\r\nHost: lab.local\r\nConnection: close\r\n\r\n' | nc lab.local 80
```

Capture and use "Follow TCP Stream" in Wireshark to see exact request bytes.

### Compare client and backend captures

```
1. Capture at the client while sending a request with X-Debug-Probe.
2. Capture at the backend or reverse proxy egress.
3. Compare whether the header/path/body changed.
```

This is the cleanest way to prove proxy normalization.

## Practical examples

- A backend log lacks `X-Forwarded-Host`, but a packet capture at proxy egress shows the proxy stripped it.
- A DNS capture inside a container shows metadata or internal service names resolving differently than on the host.
- A TLS capture shows `h2` negotiated at the edge while the backend receives HTTP/1.1.
- TCP RST packets from a firewall explain why the app reports intermittent upstream errors.
- A plaintext capture on an internal hop shows session cookies crossing an unencrypted segment.

## Related notes

- [[wireshark-workflows]] — tool-specific packet inspection workflow.
- [[http-messages]] — exact HTTP request/response bytes.
- [[tls-https]] — TLS handshake and transport trust.
- [[dns-resolution]] — DNS as the first packet-level stage.
- [[reverse-proxies]] — compare before/after proxy transformations.
- [[nmap-scanning]] — scanning behavior can be validated at packet level.
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]] — where packet capture fits among flow, protocol, endpoint, and cloud telemetry.
- [[zeek-suricata-and-netflow-analysis|Zeek, Suricata, and NetFlow Analysis]] — how packet evidence becomes higher-level security logs.

### Suggested future atomic notes

- tcpdump-basics
- pcap-handling
- tls-key-logging
- follow-tcp-stream
- packet-loss-and-retransmission
- proxy-packet-comparison
- sensor-health-and-capture-loss

## References

- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Official Tool Docs:** Wireshark display filter reference — https://www.wireshark.org/docs/dfref/
- **Official Tool Docs:** tcpdump man page — https://www.tcpdump.org/manpages/tcpdump.1.html
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
