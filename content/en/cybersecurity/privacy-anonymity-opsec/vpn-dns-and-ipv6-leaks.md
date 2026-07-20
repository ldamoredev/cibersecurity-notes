---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN DNS and IPv6 Leaks

## Definition

VPN DNS and IPv6 leaks happen when domain lookups or IPv6 traffic leave through a path different from the intended VPN path, exposing metadata to an ISP, local network, employer, or destination service.

## Why it matters

DNS and IPv6 are common places where "VPN connected" and "privacy path contained" diverge. A user may see the VPN exit IP in a browser test while DNS queries still go to the local resolver or IPv6 traffic still uses the normal interface.

The purpose of DNS leak testing is to verify whether domain lookups are leaving through the intended resolver path.

## How it works

Use the 4-path model:

1.
**Application asks for a name**
   The browser, app, or OS needs to resolve a domain.

2.
**Resolver choice is made**
   The request may go to the VPN provider resolver, a local network resolver, an ISP resolver, browser DNS-over-HTTPS, a corporate resolver, or a manually configured resolver.

3.
**Address family is selected**
   The destination may have IPv4 records, IPv6 records, or both. The OS and app decide which address family to use.

4.
**Route sends traffic**
   IPv4 and IPv6 can have different route tables. One may use the VPN while the other uses the normal network.

Example mismatch:

```
VPN app: connected
IPv4 route: VPN tunnel
DNS resolver: ISP resolver
IPv6 route: normal Wi-Fi interface

Result:
  The website may see VPN IPv4 for some traffic, while DNS or IPv6 metadata exposes the original network.
```

The bug is not "DNS exists." The bug is unresolved mismatch between name resolution, address family, and routing policy.

## Techniques / patterns

- Test DNS separately from visible IP.
- Test IPv4 and IPv6 separately.
- Check whether the VPN provider supports IPv6 or disables it safely.
- Review browser DNS-over-HTTPS behavior.
- Compare OS resolver settings before and after VPN connection.
- Test from each app that matters, not only a browser.
- Re-test after OS updates, browser updates, VPN client updates, and network changes.

## Variants and bypasses

Use the 6 leak shapes:

### 1. ISP DNS leak

The VPN routes web traffic, but DNS requests still go to the ISP resolver. The ISP may learn domain lookups even if it does not see page contents.

### 2. Local-network DNS leak

A hotel, office, school, or cafe resolver handles lookups. This can expose domains to the network operator and may also allow local filtering or manipulation.

### 3. Browser DNS-over-HTTPS mismatch

The browser uses its own encrypted DNS provider. This may improve confidentiality from the local network but can bypass the VPN provider's intended resolver path and create a new trust point.

### 4. IPv6 support mismatch

The VPN handles IPv4 only. If IPv6 remains enabled and routed outside the tunnel, dual-stack destinations can expose the user's normal network.

### 5. Split DNS and corporate resolver leakage

Corporate VPNs may intentionally send internal names to corporate DNS and public names elsewhere. Misconfiguration can leak internal hostnames or send public browsing metadata to corporate infrastructure.

### 6. Captive portal and reconnect leakage

Before the VPN connects, after sleep/wake, or during captive portal login, DNS and IPv6 behavior may briefly use the local network.

## Impact

- ISP or local-network visibility into domain lookups.
- Real network exposure through IPv6 while IPv4 appears protected.
- Corporate or local resolvers seeing more browsing metadata than intended.
- Incorrect leak-test conclusions when only visible IPv4 is checked.
- Deanonymization or location inference through resolver and address-family metadata.

## Detection and defense

Ordered by effectiveness:

1.
**Use a VPN client that handles DNS and IPv6 explicitly**
   The client should set resolver behavior, route address families intentionally, and fail closed where unsupported.

2.
**Force DNS through the intended path**
   Decide whether DNS should use the VPN provider, a trusted encrypted resolver, or a corporate resolver. Then test that the actual resolver matches the decision.

3.
**Route or disable IPv6 intentionally**
   If the VPN supports IPv6, verify it. If it does not, disable IPv6 for the workflow or use firewall rules to block IPv6 fallback.

4.
**Check browser DNS behavior**
   Browser DNS-over-HTTPS can bypass OS expectations. Align browser settings with the threat model.

5.
**Retest after network transitions**
   Sleep/wake, Wi-Fi changes, captive portals, and reconnects are where clean-looking setups often leak.

6.
**Document split DNS rules**
   In corporate environments, split DNS should be expected and auditable, not mysterious behavior.

### What does not work as a primary defense

- **Checking only IPv4 is incomplete.** IPv6 may follow a different path.
- **Checking only browser IP is incomplete.** DNS can leak even when the browser appears to use the VPN exit.
- **Encrypted DNS is not automatically the right resolver path.** It changes who sees queries; it does not remove trust.
- **Disabling IPv6 everywhere without documenting it is brittle.** It can break apps and hide the need for proper IPv6 support.

## Practical labs

### Capture visible IPv4 and IPv6

```
curl -4 https://ifconfig.me
curl -6 https://ifconfig.me
```

Record both before and after VPN connection. Treat failure to connect over IPv6 as a result to interpret, not as automatic success.

### Query resolver identity

```
dig o-o.myaddr.l.google.com TXT @ns1.google.com
dig whoami.cloudflare @1.1.1.1
```

Compare output across normal network, VPN connected, and browser DNS-over-HTTPS states.

### Inspect OS resolver configuration

```
scutil --dns | sed -n '1,160p'
```

On macOS, compare resolver entries before and after connecting the VPN.

### Inspect route tables

```
netstat -rn -f inet
netstat -rn -f inet6
```

The IPv4 and IPv6 route tables can tell different stories.

### Test after sleep/wake or network change

```
1. Connect VPN.
2. Record IPv4, IPv6, and DNS.
3. Sleep device or switch Wi-Fi.
4. Wait for reconnect.
5. Repeat IPv4, IPv6, and DNS checks.
6. Record any fallback path.
```

The reconnect case is where kill-switch and resolver behavior become visible.

## Practical examples

- A VPN client sets IPv4 routes but leaves IPv6 traffic on the Wi-Fi interface.
- A browser uses DNS-over-HTTPS to a third party while the VPN expects provider DNS.
- A corporate VPN sends internal hostnames to company DNS and public domains to local DNS.
- A mobile device leaks DNS during sleep/wake before the VPN reconnects.
- A user validates only `curl -4` and misses dual-stack exposure.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[vpn-protocols|VPN Protocols]]
- [[dns-resolution|DNS Resolution]]
- [[dns-security|DNS Security]]

### Suggested future atomic notes

- dns-over-https-threat-models
- ipv6-privacy-addresses
- split-dns
- [[vpn-kill-switches]]

## References

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** [[dns-resolution|DNS Resolution]]
- **Foundational:** [[dns-security|DNS Security]]
- **Official Tool Docs:** Tor Browser User Manual: Secure Connections - https://tb-manual.torproject.org/secure-connections/
