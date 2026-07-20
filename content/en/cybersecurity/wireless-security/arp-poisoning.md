---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# ARP Poisoning

## Definition

ARP poisoning is a local-network attack where a host sends false ARP mappings so victims associate an IP address, often the gateway, with the attacker's MAC address.

## Why it matters

Wireless compromise often becomes local-network compromise. Once an attacker joins the same LAN, ARP poisoning can redirect traffic even though the original weakness was Wi-Fi access or rogue AP connection.

This note lives in wireless security because it is a common post-association lab, but the mechanism is Ethernet/IP neighbor resolution.

## How it works

ARP poisoning has **5 steps**:

1. **Share a broadcast domain.** Attacker and victim must be on the same local segment.
2. **Identify victim and gateway.** The attacker learns IP/MAC relationships.
3. **Send false ARP replies.** Victims update their ARP cache.
4. **Traffic flows through attacker.** The attacker forwards, drops, or observes packets.
5. **Application controls decide impact.** TLS and secure protocols limit what can be read or modified.

The bug is not Wi-Fi encryption itself. It is trusting unauthenticated local ARP updates on a shared LAN.

A worked example, ARP poisoning to segmentation decision:

```
Lab setup:
  two owned laptops on guest SSID

Baseline:
  both can ping gateway and each other

ARP observation:
  gateway MAC changes on victim during controlled spoof

Application impact:
  HTTPS sites remain protected, HTTP printer page exposes credentials

Decision:
  enable client isolation and remove plaintext admin pages from guest-reachable network
```

ARP poisoning value is measuring what same-LAN access can actually affect.

## Techniques / patterns

Testing looks at:

- whether client isolation blocks peer-to-peer traffic
- whether gateway ARP entries change unexpectedly
- whether HTTPS, HSTS, and certificate validation hold under MITM
- whether local services leak plaintext credentials
- whether switches/APs enforce ARP inspection or isolation

## Variants and bypasses

ARP poisoning has **4 practical variants**.

### 1. Gateway impersonation

The attacker claims to be the gateway for the victim.

### 2. Victim impersonation

The attacker claims to be the victim for the gateway.

### 3. Bidirectional MITM

The attacker poisons both directions and forwards traffic.

### 4. Denial of service

The attacker poisons but does not forward, breaking connectivity.

## Impact

Ordered roughly by severity:

- **Traffic interception.** Plaintext protocols can be read.
- **Traffic manipulation.** DNS, HTTP, and update flows can be altered if not protected.
- **Credential exposure.** Legacy protocols and bad TLS behavior leak secrets.
- **Availability loss.** Bad forwarding or deliberate drops break network access.
- **Reconnaissance.** Observed flows reveal services and users.

## Detection and defense

Ordered by effectiveness:

1.
**Enable client isolation on guest or untrusted Wi-Fi.**
   If clients cannot talk directly, ARP poisoning between guests becomes much harder.

2.
**Segment trusted and untrusted wireless networks.**
   Keeping guests, IoT, and admin devices apart reduces shared-broadcast-domain risk.

3.
**Use secure application protocols.**
   TLS with valid certificate checking prevents most credential and content exposure even under local MITM.

4.
**Monitor ARP changes and duplicate MAC/IP mappings.**
   ARP instability is a useful signal for local MITM.

### What does not work as a primary defense

- **WPA2 alone.** Once joined, clients may still share a vulnerable LAN.
- **VPN alone for every risk.** VPN helps routed traffic but may not protect local discovery, captive portals, or all apps.
- **Static trust in local networks.** "Same Wi-Fi" should not imply safe peers.
- **Ignoring plaintext internal protocols.** Local attackers benefit from legacy traffic.

## Practical labs

Use an isolated lab network with your own victim VM/device.

### Observe normal ARP state

```
ip neigh
arp -a
```

Record gateway IP and MAC before any test.

### Detect ARP changes in Wireshark

```
Filter: arp
Expected gateway MAC:
Observed changes:
Duplicate claims:
```

Focus first on recognition and evidence.

### Run a controlled spoof check

```
sudo bettercap -iface wlan0
```

Use bettercap only inside an owned lab and document whether client isolation blocks peer traffic.

### Compare client isolation states

```
SSID:
client isolation on/off:
peer ping:
ARP visibility:
local service reach:
decision:
```

Client isolation should change peer attack feasibility.

### Record protected versus exposed traffic

```
service | protocol | certificate valid? | credentials visible? | fix
```

Local MITM risk depends heavily on application-layer protection.

### Restore ARP state after lab test

```
sudo ip neigh flush all
ip neigh
```

Rollback matters; verify the victim sees the real gateway again.

## Practical examples

- A guest Wi-Fi network lets two laptops ARP-spoof each other.
- An IoT VLAN shares a segment with admin laptops.
- A plaintext printer admin page leaks credentials under local MITM.
- HSTS and certificate validation prevent a captured browser session from being read.
- Client isolation blocks peer ARP traffic on a guest SSID.

## Related notes

- [[mitm-on-local-networks]]
- [[bettercap-workflows]]
- [[wireless-security]]
- [[nat-and-private-networks|NAT and Private Networks]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]

### Suggested future atomic notes

- dhcp-spoofing
- dns-spoofing-on-local-networks
- client-isolation
- dynamic-arp-inspection

## References

- **Official Tool Docs:** bettercap ARP spoofing module — https://www.bettercap.org/modules/ethernet/spoofers/arpspoof/
- **Official Tool Docs:** Wireshark User's Guide — https://www.wireshark.org/docs/wsug_html/
- **Foundational:** RFC 826 (Address Resolution Protocol) — https://datatracker.ietf.org/doc/html/rfc826
