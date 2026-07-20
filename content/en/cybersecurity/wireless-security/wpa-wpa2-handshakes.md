---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# WPA/WPA2 Handshakes

## Definition

WPA/WPA2 handshakes are authentication exchanges that let a client and access point prove shared key material and derive session keys without sending the passphrase itself.

## Why it matters

Handshake capture is the classic bridge between wireless observation and credential-risk assessment. A captured WPA/WPA2-PSK handshake does not reveal the password directly, but it can enable offline guessing if the passphrase is weak.

The defensive lesson is clean: WPA2-PSK security depends heavily on passphrase entropy and configuration hygiene.

## How it works

The WPA/WPA2-PSK risk path has **5 steps**:

1. **Client associates.** A station connects to the AP.
2. **Handshake occurs.** The AP and client exchange EAPOL messages.
3. **Tester captures handshake material.** Monitor mode records the relevant frames.
4. **Candidate passphrases are tested offline.** Tools derive keys and compare against the captured exchange.
5. **Only a matching passphrase succeeds.** Strong passphrases make capture useless for guessing.

The bug is not the presence of a handshake. The bug is a guessable PSK or weak operational controls around it.

A worked example, handshake to defensive conclusion:

```
Capture:
  EAPOL handshake from owned test client on lab-ap

Password policy:
  12-character human phrase based on company name

Bounded check:
  small lab wordlist finds the PSK quickly

Network design:
  same PSK used by staff and guests

Decision:
  rotate to generated PSK, split guest/staff, and plan Enterprise authentication for high-trust devices
```

The finding is not "handshake captured"; it is whether the shared secret and network design survive capture.

## Techniques / patterns

Testing looks at:

- PSK versus Enterprise authentication
- EAPOL and PMKID capture indicators
- SSID, BSSID, channel, and client presence
- whether deauthentication is needed or prohibited by the rules of engagement
- passphrase policy, rotation, guest separation, and device inventory

## Variants and bypasses

WPA/WPA2 handshake testing has **4 practical variants**.

### 1. Natural handshake capture

A client reconnects normally while the tester captures passively.

### 2. Deauth-assisted capture

An authorized lab test briefly disconnects a client to force reauthentication.

### 3. PMKID capture

Some APs expose key material useful for offline guessing without a connected client.

### 4. Enterprise authentication

WPA/WPA2-Enterprise changes the model toward certificate, identity, and EAP configuration.

## Impact

Ordered roughly by severity:

- **PSK recovery.** Weak passphrases can be recovered offline.
- **Network joining.** A recovered PSK allows access until rotated.
- **Lateral exposure.** Joined clients may reach internal services.
- **Incident scope expansion.** Shared PSKs make attribution and revocation harder.

## Detection and defense

Ordered by effectiveness:

1.
**Use high-entropy passphrases or WPA-Enterprise.**
   Offline guessing is only practical when candidate passwords are plausible. Long random PSKs or per-user authentication change the economics.

2.
**Use WPA3-SAE where supported.**
   WPA3-Personal improves resistance to offline dictionary guessing compared with WPA2-PSK.

3.
**Segment wireless clients.**
   Even if a PSK is recovered, segmentation limits what the attacker can reach.

4.
**Monitor deauth and unusual association behavior.**
   Management-frame spikes can indicate active handshake forcing.

### What does not work as a primary defense

- **Hiding the SSID.** Handshake and client behavior still leak useful data.
- **Short symbol-heavy passwords.** Length and unpredictability matter more than decorative complexity.
- **Relying on MAC filtering.** MAC addresses are visible and spoofable.
- **Never rotating shared PSKs.** Shared secrets become harder to trust over time.

## Practical labs

Use an owned lab AP and a test client.

### Capture a natural handshake

```
sudo airodump-ng --bssid LAB_BSSID --channel LAB_CH --write wpa-lab wlan0mon
```

Reconnect your own test client and confirm EAPOL appears in the capture.

### Inspect the pcap

```
wireshark wpa-lab-01.cap
```

Filter for EAPOL frames and confirm the capture is complete enough for analysis.

### Record passphrase quality

```
SSID:
Authentication:
Passphrase length:
Generated or human-chosen:
Rotation process:
Guest isolation:
```

The defensive output is the control assessment, not the crack attempt.

### Build a handshake evidence card

```
BSSID:
channel:
client:
capture method:
EAPOL/PMKID present:
wordlist tested:
result:
what this proves:
what this does not prove:
```

Handshake analysis needs limits as much as results.

### Review PSK blast radius

```
SSID | PSK shared by | devices | guest access | rotation owner | last rotated
```

Shared PSKs become operational risk when many users and devices depend on one secret.

### Decide whether Enterprise auth is justified

```
environment:
number of users:
device ownership:
offboarding frequency:
shared PSK pain:
802.1X readiness:
```

WPA-Enterprise is an operational decision as much as a cryptographic one.

## Practical examples

- A small office uses one memorable PSK for all staff and guests.
- A lab capture records EAPOL when a test phone reconnects.
- A router exposes PMKID material that can be tested offline.
- A long random PSK resists practical guessing even when the handshake is captured.
- A shared PSK must be rotated after a contractor leaves.

## Related notes

- [[wireless-security]]
- [[wifi-monitor-mode]]
- [[wifi-deauthentication]]
- [[wifi-wordlist-attacks]]
- [[wireshark-workflows|Wireshark Workflows]]

### Suggested future atomic notes

- wpa3-sae
- enterprise-wifi-8021x
- pmkid-attacks
- wireless-key-rotation

## References

- **Official Tool Docs:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Official Tool Docs:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Foundational:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
