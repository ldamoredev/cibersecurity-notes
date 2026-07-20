---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# MITM on Local Networks

## Definition

Man-in-the-middle (MITM) on local networks is interception or manipulation of traffic by a host that positions itself between a victim and the service or gateway the victim meant to reach.

## Why it matters

Wireless access often collapses physical boundaries. If an attacker joins a Wi-Fi network or runs a rogue AP, local MITM becomes the test for whether applications, devices, and segmentation survive hostile neighbors.

The point is not just sniffing. The important question is which traffic remains trustworthy when the local network is untrusted.

## How it works

Local MITM has **5 layers**:

1. **Positioning.** The attacker becomes the path through ARP spoofing, rogue AP, DNS manipulation, or gateway control.
2. **Forwarding.** Traffic must continue flowing to avoid obvious breakage.
3. **Observation.** Metadata, destinations, and plaintext content may be visible.
4. **Manipulation.** DNS, HTTP, redirects, or downloads may be changed if controls are weak.
5. **Control boundary.** TLS, HSTS, certificate validation, VPN, and app design decide impact.

The bug is not being on Wi-Fi. The bug is assuming the local network is honest.

A worked example, local MITM review:

```
Position:
  owned test client joins lab guest Wi-Fi

Path control:
  ARP spoof succeeds only when client isolation is disabled

Traffic:
  HTTPS banking site protected, HTTP camera admin page exposes basic auth

DNS:
  test resolver manipulation changes local hostname resolution

Decision:
  enable client isolation, require HTTPS on local admin tools, and treat guest Wi-Fi as hostile
```

The finding is which controls fail under hostile local networking, not the fact that sniffing is possible.

## Techniques / patterns

Testing looks at:

- ARP, DNS, DHCP, and gateway trust
- plaintext HTTP, FTP, Telnet, POP3, or local admin panels
- TLS downgrade attempts and certificate warnings
- apps that ignore certificate errors
- whether guest/client isolation prevents peer attacks

## Variants and bypasses

Local MITM has **5 common variants**.

### 1. ARP-based MITM

Redirects traffic on an existing LAN by poisoning neighbor mappings.

### 2. Rogue AP MITM

Places the attacker as the access point or gateway from the start.

### 3. DNS manipulation

Changes where victims connect before TLS or app validation begins.

### 4. Captive-portal manipulation

Uses portal flows to drive users toward unsafe actions.

### 5. TLS failure exploitation

Relies on users or apps accepting warnings, weak validation, or plaintext fallback.

## Impact

Ordered roughly by severity:

- **Credential theft.** Plaintext and fake login flows expose secrets.
- **Session compromise.** Weak cookies or tokens leak over unsafe channels.
- **Content injection.** HTTP responses and downloads can be modified.
- **Service discovery.** Local flows reveal internal systems.
- **Availability disruption.** Broken forwarding or DNS manipulation causes outages.

## Detection and defense

Ordered by effectiveness:

1.
**Assume local networks are hostile.**
   Applications should rely on TLS, certificate validation, secure cookies, and authenticated updates even inside trusted buildings.

2.
**Segment and isolate wireless clients.**
   Guest and IoT clients should not be able to directly attack each other or admin devices.

3.
**Enforce HTTPS, HSTS, and certificate validation.**
   Strong transport trust limits what a local MITM can read or change.

4.
**Monitor ARP/DNS anomalies and rogue APs.**
   Network telemetry can catch positioning attempts.

5.
**Train users around certificate warnings and captive portals.**
   Local MITM often succeeds when users normalize warnings.

### What does not work as a primary defense

- **Trusting office Wi-Fi because it has a password.** Shared access does not make peers trustworthy.
- **Depending on users to spot every fake portal.** Technical controls should carry most of the burden.
- **Using HTTPS on only login pages.** Sessions and assets also need protection.
- **Ignoring local admin interfaces.** Printers, routers, cameras, and NAS devices are common weak points.

## Practical labs

Use a lab network with devices you own.

### Identify plaintext local services

```
nmap -sV 192.168.56.0/24
```

Look for HTTP, FTP, Telnet, or old admin panels in a lab subnet.

### Observe TLS resilience

```
Target app:
Certificate warning shown:
HSTS:
Cookies Secure/HttpOnly:
Plaintext fallback:
```

Measure what survives hostile local networking.

### Compare isolated and flat Wi-Fi

```
SSID A client isolation:
Peer ping result:
ARP visibility:
Local service reachability:
```

Segmentation should change what MITM can reach.

### Build a hostile-LAN control table

```
app/service | TLS valid | HSTS | plaintext fallback | local-only assumption | result
```

This shows which services survive a hostile neighbor.

### Test DNS manipulation resilience safely

```
target hostname:
expected resolver:
manipulated answer in lab:
TLS/cert result:
user-visible warning:
```

DNS tricks should fail at TLS or application validation boundaries.

## Practical examples

- A coffee-shop-style rogue AP can see DNS lookups and plaintext HTTP.
- A flat office guest network allows peer scanning and ARP poisoning.
- A mobile app accepts invalid TLS certificates and leaks API tokens.
- A printer admin page uses HTTP basic auth on a shared Wi-Fi segment.
- HSTS prevents a browser from silently downgrading a sensitive site.

## Related notes

- [[arp-poisoning]]
- [[evil-twin-access-points]]
- [[bettercap-workflows]]
- [[tls-https|TLS and HTTPS]]
- [[client-ip-trust|Client IP Trust]]

### Suggested future atomic notes

- dns-spoofing-on-local-networks
- captive-portal-security
- mobile-app-tls-validation
- client-isolation

## References

- **Official Tool Docs:** bettercap documentation — https://www.bettercap.org/
- **Official Tool Docs:** Wireshark User's Guide — https://www.wireshark.org/docs/wsug_html/
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
