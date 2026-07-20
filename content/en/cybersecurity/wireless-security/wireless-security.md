---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Wireless Security

## Definition

Wireless security is the protection and testing of networks whose first trust boundary is radio communication rather than a cable, route, or web endpoint.

## Why it matters

Wi-Fi changes the security model because nearby devices can observe management frames, discover networks, impersonate access points, and join the same local segment if authentication is weak.

The core lesson is that wireless security starts before IP traffic exists. Association, authentication, encryption, signal range, client behavior, and management frames all shape what an attacker or defender can observe.

## How it works

Wireless security has **5 moving parts**:

1. **Radio medium.** Devices transmit over channels that nearby adapters may observe.
2. **Discovery.** Access points advertise SSIDs and capabilities through management frames.
3. **Association.** Clients choose and join an access point.
4. **Authentication and keys.** WEP, WPA/WPA2-PSK, WPA/WPA2-Enterprise, or WPA3 decide who can join and how traffic is protected.
5. **Local-network behavior.** Once joined, clients still face ARP, DNS, TLS, segmentation, and service exposure risks.

There is no single wireless payload. The bug is usually a weak protocol choice, weak passphrase, unsafe client trust, missing segmentation, or lack of monitoring.

A worked example, wireless finding to risk decision:

```
Observation:
  lab-office SSID uses WPA2-PSK, guest network enabled

Capture:
  monitor-mode survey shows client traffic and one natural WPA handshake

Router config:
  WPS disabled, PMF optional, guest isolation disabled

Local-network check:
  guest client can ping another guest and reach printer admin page

Decision:
  the main risk is not "WPA2 exists"; it is weak segmentation and local admin reachability
```

Wireless security should connect radio-layer facts to network and application-layer blast radius.

## Techniques / patterns

Wireless testing looks at:

- SSID, BSSID, channel, band, encryption, and client count
- whether an adapter supports monitor mode and packet injection
- handshake capture and passphrase strength in owned labs
- deauthentication and rogue AP resilience
- client isolation, guest segmentation, and local service exposure
- whether TLS and application controls still hold on hostile local networks

## Variants and bypasses

Wireless security has **6 practical domains**.

### 1. Passive observation

Management frames, beacons, probes, and signal data can be observed without joining a network.

### 2. Weak legacy encryption

WEP is structurally broken and should be treated as no meaningful protection.

### 3. WPA/WPA2-PSK strength

WPA/WPA2-PSK commonly fails through weak passphrases, not through breaking AES directly.

### 4. Management-frame disruption

Deauthentication and disassociation attacks abuse unauthenticated or weakly protected management behavior.

### 5. Rogue access points

Clients may connect to lookalike or stronger-signal networks if trust decisions are loose.

### 6. Same-LAN attacks

After joining, ARP spoofing, DNS manipulation, service discovery, and insecure local apps become the next layer.

## Impact

Ordered roughly by severity:

- **Network access.** Weak credentials or legacy protocols let attackers join the LAN.
- **Credential exposure.** Evil twin and captive-portal tricks can capture secrets in unsafe environments.
- **Traffic interception.** Same-LAN attackers can observe or manipulate unprotected traffic.
- **Availability disruption.** Deauthentication can force client disconnects.
- **Reconnaissance.** SSIDs, clients, vendors, and probe behavior reveal environment structure.

## Detection and defense

Ordered by effectiveness:

1.
**Use WPA3 or WPA2 with strong passphrases or Enterprise authentication.**
   Modern authentication and high-entropy secrets remove the most common path from captured material to network access.

2.
**Disable WEP, WPS PIN, and obsolete mixed modes.**
   Legacy compatibility keeps broken security alive. Removing it is stronger than monitoring it.

3.
**Segment wireless networks.**
   Guest, IoT, lab, and admin devices should not share one flat LAN. Segmentation limits what a wireless compromise can reach.

4.
**Enable protected management frames where supported.**
   PMF reduces common management-frame abuse, especially deauthentication-style disruption.

5.
**Monitor for rogue APs and unusual management traffic.**
   Wireless IDS, controller alerts, and periodic surveys help detect spoofed networks and active disruption.

### What does not work as a primary defense

- **Hiding the SSID.** Clients and frames still reveal network behavior.
- **MAC allowlists alone.** MAC addresses are observable and spoofable.
- **Short complex-looking passwords.** Offline guessing rewards length and unpredictability.
- **Trusting Wi-Fi encryption to protect application secrets.** TLS and application-layer controls still matter.

## Practical labs

Use an owned access point or isolated lab router only.

### Inventory nearby wireless signals

```
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon
```

Record SSID, BSSID, channel, encryption, and client count.

### Compare Wi-Fi and IP layers

```
ip addr
ip route
arp -a
```

Map how wireless association becomes local IP reachability.

### Review router security posture

```
Encryption:
WPA mode:
WPS:
Guest network:
Client isolation:
Admin interface exposure:
```

Turn wireless observations into control checks.

### Build a wireless risk card

```
SSID:
Authentication:
Client isolation:
Admin surface:
PMF:
Guest/IoT separation:
Evidence:
Top next action:
```

The output of a wireless review should be a control decision, not only a capture file.

### Compare trusted and guest reachability

```
ip route
arp -a
ping -c 2 192.168.1.1
```

Run from owned lab clients; compare what each SSID can reach.

## Practical examples

- A home router uses WPA2-PSK with a short reused password.
- A guest network lacks client isolation, exposing printers and admin panels.
- A legacy device forces a mixed WPA/WPA2 compatibility mode.
- A fake access point uses a familiar SSID in a public space.
- A deauthentication burst causes devices to reconnect through a stronger rogue AP.

## Related notes

- [[wifi-monitor-mode]]
- [[wpa-wpa2-handshakes]]
- [[wifi-deauthentication]]
- [[evil-twin-access-points]]
- [[packet-analysis|Packet Analysis]]

### Suggested future atomic notes

- wpa3-sae
- enterprise-wifi-8021x
- wps-security
- wireless-intrusion-detection
- radio-frequency-basics

## References

- **Foundational:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
- **Official Tool Docs:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
- **Official Tool Docs:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
