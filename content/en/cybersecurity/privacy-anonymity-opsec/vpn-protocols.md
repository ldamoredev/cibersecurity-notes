---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN Protocols

## Definition

VPN protocols define how a VPN tunnel is negotiated, encrypted, authenticated, routed, and maintained. They determine the shape of the tunnel, not whether the user is anonymous.

## Why it matters

Choosing a VPN protocol is a security engineering decision, but it is often treated as a branding decision. WireGuard, OpenVPN, IKEv2/IPsec, L2TP/IPsec, and PPTP do not have the same design assumptions, audit surface, roaming behavior, deployment complexity, or legacy risk.

The practical question is not "which protocol is best?" It is "which protocol fits this device, network, trust model, and operational constraint without creating false confidence?"

## How it works

Use the 5-part tunnel model:

1.
**Peer authentication**
   The client and server prove who they are through keys, certificates, credentials, or pre-shared material.

2.
**Key agreement**
   The protocol establishes encryption keys for the session. Modern protocols should support forward secrecy and avoid obsolete primitives.

3.
**Encapsulation**
   The original traffic is wrapped inside tunnel packets so it can cross the outer network.

4.
**Routing policy**
   The operating system decides which traffic goes through the tunnel: all traffic, selected subnets, selected apps, or split routes.

5.
**Session maintenance**
   The tunnel handles reconnects, roaming, keepalives, packet loss, network changes, and failure behavior.

Conceptual comparison:

```
WireGuard:
  modern, compact, fast, key-based, opinionated

OpenVPN:
  mature, flexible, widely deployed, more complex

IKEv2/IPsec:
  common on mobile, good roaming behavior, integrated into many OSes

L2TP/IPsec:
  legacy wrapper around IPsec, common historically, usually not first choice

PPTP:
  obsolete, broken for serious security, historical only
```

The bug is not using an older protocol in a lab. The bug is treating legacy compatibility as a serious privacy or security posture.

## Techniques / patterns

- Identify the deployed protocol before judging a VPN product.
- Check whether the client uses full tunnel or split tunnel routing.
- Look for obsolete protocol support, especially PPTP.
- Confirm whether DNS and IPv6 follow the same routing policy as application traffic.
- Treat mobile roaming, sleep/wake, and captive portals as real failure cases.
- Separate cryptographic protocol choice from provider trust. A strong tunnel to an untrustworthy provider is still an untrustworthy workflow.

## Variants and bypasses

Use the 5 protocol families:

### 1. WireGuard

WireGuard is a modern VPN protocol with a small, opinionated design and static public-key identities. It is fast and comparatively easy to reason about, but deployments must handle key rotation, endpoint privacy, and routing policy carefully.

### 2. OpenVPN

OpenVPN is mature and flexible, with broad platform support and many deployment modes. Its flexibility is useful in enterprise and compatibility-heavy environments, but it also creates more configuration surface.

### 3. IKEv2/IPsec

IKEv2/IPsec is common on mobile and operating-system-native deployments. It handles network changes well, but IPsec deployments can be complex and depend heavily on correct cipher, certificate, and identity configuration.

### 4. L2TP/IPsec

L2TP/IPsec is mostly legacy. It can be found in older environments and built-in clients, but modern deployments usually prefer WireGuard, OpenVPN, or IKEv2/IPsec.

### 5. PPTP

PPTP is deprecated and should not be used for serious security. If PPTP appears in a modern environment, treat it as a migration finding, not a normal option.

## Impact

- Stronger cryptographic tunnel design when modern protocols are used correctly.
- Reduced operational risk when the protocol matches the device and network environment.
- Increased exposure from legacy protocols, weak ciphers, or brittle reconnect behavior.
- False assurance when protocol strength is confused with provider trust or anonymity.
- Hard-to-debug leaks when routing policy, DNS, IPv6, or split tunneling are misconfigured.

## Detection and defense

Ordered by effectiveness:

1.
**Use modern protocols by default**
   Prefer WireGuard, OpenVPN, or IKEv2/IPsec depending on environment needs. They have active ecosystems and safer design assumptions than legacy VPN protocols.

2.
**Disable PPTP and retire legacy fallback**
   Legacy fallback can silently convert a strong posture into a weak one. Removing unsupported protocols is stronger than merely documenting that they should not be used.

3.
**Verify routing policy independently of protocol choice**
   A secure protocol can still leak traffic if the OS routes DNS, IPv6, or selected apps outside the tunnel.

4.
**Harden authentication material**
   Protect private keys, certificates, profiles, and pre-shared keys. Tunnel security fails if client credentials are copied, reused, or left on unmanaged devices.

5.
**Test reconnect and roaming behavior**
   Mobile network changes, sleep/wake transitions, captive portals, and Wi-Fi handoff can expose race conditions that normal "connected" checks miss.

6.
**Document protocol choice and migration path**
   A VPN deployment should state why the protocol was chosen, which clients require it, and when legacy compatibility will end.

### What does not work as a primary defense

- **Protocol name alone is not a guarantee.** A WireGuard, OpenVPN, or IPsec deployment can still be misrouted, overlogged, or poorly authenticated.
- **PPTP compatibility is not worth serious security risk.** Keep it only for isolated historical labs or migration discovery.
- **Encryption does not solve provider trust.** The VPN provider terminates the tunnel and may still observe metadata.
- **Split tunneling is not harmless convenience.** It is a routing policy that can create accidental leakage.

## Practical labs

### Inventory local VPN profiles

```
scutil --nc list 2>/dev/null || true
nmcli connection show 2>/dev/null | rg -i 'vpn|wireguard|openvpn|ipsec|l2tp|pptp' || true
```

Use the output to identify protocol family and whether legacy profiles exist.

### Check WireGuard state

```
wg show 2>/dev/null || echo "WireGuard tools or interface not available"
```

For owned systems, confirm peer public keys, endpoint, latest handshake, and allowed IPs.

### Search configuration for legacy protocols

```
rg -i 'pptp|l2tp|ms-chap|mppe|ikev1|ikev2|openvpn|wireguard' .
```

Run this in an infrastructure or device-profile repository to find legacy VPN configuration.

### Compare full-tunnel and split-tunnel route shape

```
netstat -rn | sed -n '1,80p'
```

Capture route tables before and after VPN connection. Look for default routes, VPN interface routes, and private-subnet-only routes.

### Record protocol decision evidence

```
VPN use case:
Chosen protocol:
Client platforms:
Authentication model:
Full tunnel or split tunnel:
DNS handling:
IPv6 handling:
Reconnect behavior tested:
Legacy protocol disabled:
```

The filled record turns "we use a VPN" into an auditable engineering choice.

## Practical examples

- A consumer VPN defaults to WireGuard for speed, but DNS still leaks through the OS resolver.
- A company keeps IKEv2/IPsec for mobile clients because roaming reliability matters more than protocol fashion.
- A legacy appliance supports only L2TP/IPsec, creating a migration requirement.
- A forgotten PPTP profile remains on a laptop after the official VPN has moved to a modern protocol.
- An OpenVPN deployment is cryptographically fine but uses split tunneling that leaves browser traffic outside the tunnel.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-dns-and-ipv6-leaks|VPN DNS and IPv6 Leaks]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[tcp-ip-basics|TCP/IP Basics]]

### Suggested future atomic notes

- wireguard-key-management
- openvpn-configuration-hardening
- ikev2-ipsec-authentication
- split-tunneling

## References

- **Official Tool Docs:** WireGuard - https://www.wireguard.com/
- **Official Tool Docs:** OpenVPN Community Documentation - https://openvpn.net/community-docs/
- **Official Tool Docs:** strongSwan documentation - https://docs.strongswan.org/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
