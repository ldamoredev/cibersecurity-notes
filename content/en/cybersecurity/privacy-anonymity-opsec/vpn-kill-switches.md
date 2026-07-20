---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# VPN Kill Switches

## Definition

A VPN kill switch blocks traffic when the VPN is disconnected or unavailable so the system does not silently fall back to the normal network path.

## Why it matters

Without a kill switch, a brief disconnect can expose the user's real IP, DNS resolver, or application traffic at exactly the moment the user assumes the VPN is still protecting them. This is especially risky during sleep/wake, roaming, captive portals, and mobile network changes.

## How it works

Use the 4-state model:

1.
**VPN connected**
   Traffic should follow the tunnel path.

2.
**VPN disconnected**
   Traffic should be blocked rather than sent over the normal interface.

3.
**Reconnect in progress**
   The system may temporarily have no valid route. The control should fail closed.

4.
**Tunnel restored**
   Traffic resumes only when the VPN path is back.

Example policy:

```
if vpn_up:
  allow outbound only through tunnel
else:
  block outbound traffic
```

The bug is not using a kill switch. The bug is assuming the presence of a VPN app icon means traffic is contained.

## Techniques / patterns

- Prefer system-level firewall containment over app-only toggles.
- Test the kill switch during real disconnect conditions.
- Check browser, terminal, and app traffic separately.
- Verify behavior after sleep/wake and network handoff.
- Document what split-tunnel apps are allowed to bypass the switch.
- Ensure DNS and IPv6 are not silently exempted.

## Variants and bypasses

Use the 5 kill-switch patterns:

### 1. App toggle

The VPN client blocks traffic itself. This is convenient but can fail if the client crashes or does not manage every app path.

### 2. Firewall-based block

The firewall prevents non-tunnel traffic from leaving. This is usually stronger because it is closer to the system routing layer.

### 3. Full-device containment

The whole device is blocked unless the tunnel is up. This is often the safest option for a sensitive workflow.

### 4. Split-tunnel exception

Some apps or subnets are exempted. This should be explicit because exemptions can become leak paths.

### 5. Mobile reconnect containment

The device sleeps, wakes, or changes networks. The kill switch must still fail closed across those transitions.

## Impact

- Lower chance of accidental fallback to the normal network path.
- Better containment during unstable Wi-Fi or mobile transitions.
- Reduced chance of DNS or IPv6 leaks when the tunnel drops.
- More predictable privacy posture during sensitive workflows.
- Potential usability friction if the tunnel is unstable.

## Detection and defense

Ordered by effectiveness:

1.
**Use firewall-level fail-closed control**
   A system policy that blocks traffic when the tunnel is down is harder to bypass than a client UI toggle.

2.
**Test the disconnect path explicitly**
   The relevant failure case is not normal connected state. Pull the tunnel down and observe what happens.

3.
**Cover DNS and IPv6 in the policy**
   A good switch must block all relevant network paths, not just the most obvious IPv4 browser traffic.

4.
**Audit split-tunnel exceptions**
   If certain apps are allowed direct access, those exceptions need to be documented and monitored.

5.
**Retest after client or OS updates**
   Network stack changes can change fail-open/fail-closed behavior.

### What does not work as a primary defense

- **The connected badge is not proof.** It only indicates app state.
- **A kill switch that only watches the VPN app can fail if the app crashes.**
- **Split tunneling is not equivalent to containment.** It creates intentional bypasses.
- **Testing only when the VPN is connected proves nothing about disconnect behavior.**

## Practical labs

### Simulate disconnect state

```
1. Connect VPN.
2. Record visible IP and DNS.
3. Disconnect VPN.
4. Record whether any traffic still leaves.
5. Reconnect VPN.
6. Repeat the checks.
```

This is the core kill-switch test.

### Check route containment

```
netstat -rn | sed -n '1,120p'
```

Compare route tables while connected and disconnected to see whether a default route remains.

### Check DNS after drop

```
dig whoami.cloudflare @1.1.1.1
curl -4 https://ifconfig.me
```

Run after disconnecting. A leak means the policy is not actually fail-closed.

### Write a failure record

```
Device:
VPN:
Connected state:
Disconnect trigger:
Traffic blocked:
Traffic leaked:
DNS leaked:
IPv6 leaked:
Retest after restart:
```

This turns a vague "kill switch on" claim into a testable record.

## Practical examples

- A laptop loses Wi-Fi and the switch blocks traffic until the VPN reconnects.
- A mobile device wakes from sleep and the firewall prevents fallback traffic.
- A split-tunnel exception is documented for a printer subnet but not for browser traffic.
- A VPN app crashes and the system firewall still blocks egress.
- A reconnect race is caught because the test included sleep/wake, not just manual disconnect.

## Related notes

- [[vpn-threat-models|VPN Threat Models]]
- [[vpn-leakage-risks|VPN Leakage Risks]]
- [[vpn-dns-and-ipv6-leaks|VPN DNS and IPv6 Leaks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[tls-https|TLS / HTTPS]]

### Suggested future atomic notes

- split-tunneling
- reconnect-race-conditions
- mobile-vpn-leaks

## References

- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** WireGuard - https://www.wireguard.com/
- **Official Tool Docs:** OpenVPN Community Documentation - https://openvpn.net/community-docs/
