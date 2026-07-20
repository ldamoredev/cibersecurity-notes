---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# TCP/IP Basics

## Definition

TCP/IP is the practical communication foundation of IP networks: IP moves packets between addresses, while TCP creates reliable ordered byte streams between ports on hosts.

## Why it matters

Most application security findings depend on reachability before they depend on code. SSRF, exposed databases, reverse-proxy trust, metadata endpoints, firewalls, port scans, and packet captures all require basic TCP/IP reasoning.

The recurring lesson: **reachability is a path property**. An address, port, or service is only "internal", "public", "filtered", or "reachable" from a particular network viewpoint.

## How it works

TCP/IP reasoning starts with **5 questions**:

1. **What address is targeted?** IPv4, IPv6, loopback, link-local, private, public, or shared address space.
2. **What route is used?** Local interface, gateway, VPN, NAT, proxy, or cloud route table.
3. **What port is contacted?** The destination port selects the listening service.
4. **Can a TCP connection form?** SYN → SYN-ACK → ACK means the path and listener are reachable.
5. **What speaks over the connection?** HTTP, TLS, SSH, database protocol, or something else.

Example:

```
client 198.51.100.10:51544 -> app.example.com 203.0.113.42:443
SYN → SYN/ACK → ACK
TLS ClientHello
HTTP request inside TLS
```

The app-layer request only exists because addressing, routing, port selection, and TCP connection setup succeeded first.

## Techniques / patterns

Security work uses TCP/IP basics to:

- distinguish bind address (`127.0.0.1`, `0.0.0.0`, private IP, public IP)
- test reachability with `nc`, `curl`, `nmap`, and packet captures
- interpret open, closed, filtered, refused, and timeout behavior
- reason about NAT, private networks, and link-local addresses
- understand source IP before and after proxies/load balancers
- compare public, VPN, internal, container, and cloud viewpoints
- debug connection reuse, resets, retransmissions, and timeouts

## Variants and bypasses

TCP/IP security reasoning has **6 recurring contexts**.

### 1. Loopback

`127.0.0.0/8` and `::1` are local to the host. A service bound to loopback is not reachable from the network, but SSRF inside the same host may still reach it.

### 2. Private address space

RFC 1918 ranges (`10/8`, `172.16/12`, `192.168/16`) are not publicly routed, but they are reachable from inside networks, VPNs, containers, or SSRF-capable workloads.

### 3. Link-local

`169.254.0.0/16` and IPv6 `fe80::/10` are local-link ranges. Cloud metadata endpoints use this shape, which is why link-local egress matters.

### 4. Public address space

Public IPs are routable, but firewalls, security groups, and load balancers decide which ports respond.

### 5. IPv6 exposure

IPv6 can bypass IPv4-only assumptions. A host may be locked down on IPv4 while globally reachable over IPv6.

### 6. NAT and proxy translation

NAT changes addresses and ports; proxies terminate and create new connections. Logs and access controls must account for which hop's source IP they are seeing.

## Impact

Ordered roughly by severity:

- **Unexpected service exposure.** A process bound to `0.0.0.0` or IPv6 becomes reachable outside the intended host.
- **Boundary bypass.** Internal paths, VPN routes, containers, or SSRF reach services public users cannot.
- **Metadata/internal service access.** Link-local and private reachability amplify server-side request bugs.
- **Log and trust confusion.** NAT/proxy translation changes source IP evidence.
- **False test conclusions.** Testing from the wrong viewpoint misses or invents exposure.
- **Operational debugging failures.** Connection resets and timeouts get misdiagnosed as application bugs.

## Detection and defense

Ordered by effectiveness:

1.
**Bind services to the narrowest address needed.**
   Development/admin services should bind loopback or private interfaces, not `0.0.0.0`, unless public exposure is intentional.

2.
**Validate reachability from every relevant viewpoint.**
   Public internet, VPN, internal subnet, container, and cloud workload views can all differ. Security claims need the viewpoint attached.

3.
**Use network boundaries before application trust.**
   Databases, caches, metadata endpoints, and admin services should be unreachable from untrusted paths regardless of app-layer checks.

4.
**Account for IPv6 explicitly.**
   Mirror IPv4 firewall/security-group policy in IPv6 or disable IPv6 intentionally where unsupported.

5.
**Log source and translated addresses clearly.**
   Preserve original network-source data and proxy-derived identity separately so investigations do not confuse header claims with packet source.

6.
**Observe packets when behavior is ambiguous.**
   SYN/ACK, RST, retransmission, and timeout patterns explain what scanners and apps summarize poorly.

### What does not work as a primary defense

- **Relying on "internal IP" names.** Names do not enforce routing or authorization.
- **Binding to all interfaces by default.** Many frameworks do this for convenience; production exposure should be explicit.
- **Testing only from localhost.** Local success says little about public or internal network reachability.
- **Ignoring UDP and IPv6.** Attack surface is not TCP/IPv4-only.
- **Treating NAT as a firewall.** NAT hides some paths but does not define authorization.

## Practical labs

Run on systems you own.

### Inspect local listeners

```
lsof -i -P -n
ss -lntup 2>/dev/null || netstat -an | rg 'LISTEN|udp'
```

Look for services bound to `0.0.0.0`, `::`, public IPs, or unexpected ports.

### Inspect routes and interfaces

```
ip addr 2>/dev/null || ifconfig
ip route 2>/dev/null || netstat -rn
```

Record which interface and gateway traffic will use.

### Test TCP reachability

```
nc -vz app.example.com 443
nc -vz 127.0.0.1 3000
```

Compare local, public, VPN, and cloud-host viewpoints.

### Watch the handshake

```
sudo tcpdump -n 'tcp port 443 and host app.example.com'
nc -vz app.example.com 443
```

Observe SYN/SYN-ACK/RST/timeout behavior.

### Check IPv6 exposure

```
dig +short app.example.com AAAA
nmap -6 -Pn -p 80,443 app.example.com
```

Only meaningful when the target has IPv6 records or addresses.

### Compare bind behavior

```
# Example local lab: one service bound to localhost, one to all interfaces.
nc -l 127.0.0.1 9001
nc -l 0.0.0.0 9002
```

From another host, only the all-interface listener should be reachable.

## Practical examples

- A Node dev server binds `0.0.0.0:3000` and becomes reachable from the office network.
- PostgreSQL listens on a private IP; public internet cannot reach it, but a compromised web app in the same VPC can.
- A firewall allows IPv4 only, but the host exposes SSH over IPv6.
- A proxy access log records the load balancer IP, while the app trusts `X-Forwarded-For` for user identity.
- `nc` times out from public internet but succeeds from a VPN, proving segmentation is viewpoint-dependent.

## Related notes

- [[ports-and-services]] — ports as service entry points.
- [[nat-and-private-networks]] — private reachability and NAT behavior.
- [[metadata-endpoints]] — link-local service risk.
- [[packet-analysis]] — packet-level proof of reachability.
- [[nmap-scanning]] — systematic reachability and service scanning.
- [[firewalls-and-network-boundaries]] — policy controls over network paths.

### Suggested future atomic notes

- tcp-handshake
- bind-addresses
- ipv6-exposure
- udp-basics
- connection-states
- source-ip-vs-forwarded-ip

## References

- **Foundational:** RFC 9293 (Transmission Control Protocol) — https://datatracker.ietf.org/doc/html/rfc9293
- **Foundational:** RFC 791 (Internet Protocol) — https://datatracker.ietf.org/doc/html/rfc791
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
