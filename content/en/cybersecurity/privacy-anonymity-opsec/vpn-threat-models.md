---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN Threat Models

## Definition

A VPN is not anonymity. A VPN changes who can observe parts of network traffic by moving the user's apparent network path through a VPN provider.

## Why it matters

VPN marketing often collapses privacy, anonymity, security, and anti-tracking into one product promise. In reality, a VPN usually shifts trust from the local network or ISP to the VPN provider.

That shift can be useful. It can protect traffic metadata from hostile Wi-Fi, reduce ISP visibility, route around network blocks, or reach a corporate private network. But it does not erase account identity, browser fingerprints, cookies, behavioral patterns, file metadata, endpoint compromise, or provider-side logs.

VPNs protect transport path exposure. They do not make identity disappear.

## How it works

Use the 4-observer model:

1.
**Local network**
   The coffee shop, hotel, school, office, or home network sees an encrypted tunnel to the VPN server instead of direct connections to every destination.

2.
**ISP or upstream network**
   The ISP sees that the user connects to a VPN endpoint and can observe timing and volume, but it should not see every destination domain or destination IP if traffic and DNS are routed through the tunnel.

3.
**VPN provider**
   The VPN provider can often see the user's source IP, account, connection time, assigned exit IP, traffic timing, traffic volume, and destination metadata unless the architecture prevents or minimizes collection.

4.
**Destination website or service**
   The website sees the VPN exit IP instead of the user's residential IP, but it can still see account login, cookies, browser fingerprint, app telemetry, request behavior, and content submitted to the service.

Concrete visibility table:

```
Observer             Before VPN                         After VPN
Local Wi-Fi          destination metadata, timing        VPN endpoint, timing, volume
ISP                  destination metadata, timing        VPN endpoint, timing, volume
VPN provider         no privileged path view             source IP, timing, destination metadata
Website             residential IP + browser signals    VPN IP + browser/account signals
```

The bug is not that VPNs are useless. The bug is treating a trust shift as anonymity.

## Techniques / patterns

- Name the observer the VPN is meant to reduce: local Wi-Fi, ISP, school network, employer network, geo/network boundary, or destination service.
- Check whether DNS, IPv6, and app traffic actually follow the tunnel.
- Separate consumer VPN privacy from corporate VPN access control.
- Evaluate provider trust through logs, audits, jurisdiction, ownership, infrastructure, payment/account metadata, and business incentives.
- Identify what websites still receive: account, cookie, fingerprint, language, timezone, behavior, and uploaded files.
- Avoid stacking VPN and Tor unless the changed trust model is understood.

## Variants and bypasses

Use the 6 VPN threat-model cases:

### 1. Hostile local network

A VPN can reduce what a cafe, airport, hotel, or shared LAN sees. This is useful when the local network is untrusted, but modern HTTPS already protects most content. The VPN mainly changes metadata exposure.

### 2. ISP privacy

A VPN can reduce ISP visibility into destination metadata, especially when DNS also goes through the tunnel. It replaces ISP trust with VPN-provider trust.

### 3. Censorship or network blocks

A VPN can route around some local restrictions by making traffic appear to leave from a different network. It may fail where VPN endpoints are blocked, legally risky, or fingerprinted.

### 4. Corporate access

Corporate VPNs usually exist to reach private company resources. They are identity-aware, managed, monitored, and logged by design. Their security goal is access control, not consumer anonymity.

### 5. Destination-facing IP change

Websites see the VPN exit IP instead of the user's source IP. This can reduce coarse location exposure, but it does not prevent login correlation, fingerprinting, fraud scoring, or behavior-based linking.

### 6. False-confidence mode

The VPN tunnel works, but the user leaks through accounts, DNS, IPv6, WebRTC, split tunneling, app bypass, browser fingerprinting, file metadata, or endpoint malware.

## Impact

- Useful reduction of local-network and ISP visibility when configured correctly.
- Trust shift toward a VPN provider that may log, sell, retain, or be compelled to disclose records.
- Persistent website-level tracking despite changed IP address.
- Accidental exposure from DNS, IPv6, WebRTC, split-tunnel, mobile sleep/wake, or app bypass behavior.
- Overconfidence during sensitive research or personal safety workflows.

## Detection and defense

Ordered by effectiveness:

1.
**Define the VPN's job before choosing one**
   A VPN for hostile Wi-Fi, ISP privacy, corporate access, censorship circumvention, and destination-facing IP change has different success criteria. Without a goal, any marketing claim sounds relevant.

2.
**Evaluate provider trust as a system**
   No-log claims are not technical guarantees by themselves. Evaluate architecture, audits, jurisdiction, ownership, infrastructure control, incident history, business model, and incentives.

3.
**Verify routing behavior**
   Test visible IPv4, IPv6, DNS resolver, and app behavior from the actual device and apps. Configuration drift can turn a working VPN into a partial tunnel.

4.
**Keep browser and account controls separate**
   Use separate profiles, avoid identifying logins when unlinkability matters, and understand that cookies and fingerprints survive an IP change.

5.
**Use kill switches and firewall rules for containment**
   A kill switch should prevent accidental fallback to the normal network path when the VPN disconnects. System-level firewall controls are usually stronger than app-only toggles.

6.
**Prefer HTTPS and endpoint security regardless of VPN**
   A VPN does not replace TLS, updates, strong authentication, disk encryption, or malware resistance. Endpoint compromise defeats network-path privacy.

### What does not work as a primary defense

- **"No logs" marketing is not proof.** It is a trust claim that needs architecture, audits, jurisdiction, and history.
- **VPN plus real-name login is not anonymity.** The destination can identify the account regardless of source IP.
- **Private browsing plus VPN is not an OPSEC boundary.** Browser and account signals still cross the boundary.
- **A VPN does not protect against endpoint compromise.** Malware or managed-device monitoring can see activity before encryption or after decryption.
- **A VPN does not automatically fix DNS, IPv6, or WebRTC leaks.** Those are configuration and application behaviors that need testing.

## Practical labs

### Compare visible IP addresses

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Run before and after enabling the VPN. If IPv6 still shows the non-VPN path, the threat model has changed less than expected.

### Compare DNS resolver visibility

```
dig o-o.myaddr.l.google.com TXT @ns1.google.com
dig whoami.cloudflare @1.1.1.1
```

Record the resolver/source view before and after enabling the VPN. DNS leaks are about where lookups leave, not whether the web page loads.

### Map observers for a VPN session

```
Activity:
VPN provider:
Account used:
Payment/account metadata:
Local network observer:
ISP observer:
Destination services:
Browser profile:
DNS path:
IPv6 behavior:
Files uploaded:
```

The completed worksheet should show whether the VPN is solving the intended observer problem.

### Test app-level bypass risk

```
Test plan:
1. Enable the VPN.
2. Check the browser visible IP.
3. Check a second browser profile.
4. Check a desktop app with its own networking.
5. Check a mobile app after sleep/wake.
6. Record any app that exposes the normal network path.
```

Some applications do not behave like the browser. The goal is to test the real workflow.

### Simulate disconnect containment

```
Expected kill-switch behavior:
- VPN connected: traffic allowed
- VPN disconnects: traffic blocked
- VPN reconnects: traffic resumes through tunnel
- split-tunnel apps: behavior documented
- mobile sleep/wake: behavior documented
```

Do this only on a device and network you control. The result tells you whether disconnection creates accidental fallback.

## Practical examples

- A journalist uses a trusted VPN on hotel Wi-Fi to reduce local-network metadata exposure, but avoids personal account login for sensitive research.
- A developer uses a corporate VPN to reach internal systems; the company logs identity, device posture, and session activity by design.
- A user changes apparent country with a VPN but remains trackable through the same browser cookies and account.
- A VPN routes browser traffic but an app uses direct DNS or IPv6 outside the tunnel.
- A user assumes "no logs" means impossible-to-disclose records, but the provider still has account, payment, source-IP, abuse, or infrastructure telemetry.

## Related notes

- [[privacy-vs-anonymity-vs-confidentiality|Privacy vs Anonymity vs Confidentiality]]
- [[metadata-and-identity-leakage|Metadata and Identity Leakage]]
- [[dns-resolution|DNS Resolution]]
- [[tls-https|TLS / HTTPS]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

### Suggested future atomic notes

- [[vpn-protocols]]
- [[vpn-logging-and-trust]]
- [[vpn-leakage-risks]]
- [[vpn-kill-switches]]
- [[vpn-dns-and-ipv6-leaks]]
- [[vpn-vs-tor]]
- [[corporate-vpns-vs-consumer-vpns]]

## References

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
