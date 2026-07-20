---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Evil Twin Access Points

## Definition

An evil twin access point is a rogue wireless network that imitates a legitimate SSID to lure clients into connecting to an attacker-controlled network.

## Why it matters

Evil twin attacks exploit client trust, user habit, and weak network identity signals. The access point name alone is not proof that the network is legitimate.

This topic belongs between wireless and social engineering: the radio layer attracts the device, while the human or application layer may expose credentials or traffic.

## How it works

Evil twin risk has **5 steps**:

1. **Choose a target SSID.** The rogue network imitates a familiar name.
2. **Broadcast a lookalike AP.** The attacker uses signal strength, placement, or timing to attract clients.
3. **Client connects.** Auto-join or user selection sends the device to the rogue network.
4. **Traffic is controlled.** The rogue network may route, block, inspect, or redirect traffic.
5. **Follow-on attack occurs.** Captive portals, DNS manipulation, TLS errors, or local MITM become possible.

The bug is trusting SSID text as identity instead of using strong authentication and application-layer protection.

A worked example, awareness lab without credential capture:

```
Lab:
  duplicate "Guest-Lab" SSID on isolated AP

Client behavior:
  test phone shows two networks with same name

Portal:
  displays training page with no credential fields

Observation:
  user cannot distinguish legitimacy from SSID name alone

Decision:
  disable auto-join for public SSIDs, monitor duplicate BSSIDs, and avoid credential entry into Wi-Fi portals
```

Evil-twin labs should teach trust failure without harvesting secrets.

## Techniques / patterns

Testing looks at:

- whether devices auto-join known SSIDs
- whether the legitimate network uses Enterprise certificates or only PSK
- whether users accept captive portals or certificate warnings
- whether DNS and HTTP traffic can be manipulated after connection
- whether monitoring detects duplicate SSIDs or rogue BSSIDs

## Variants and bypasses

Evil twin attacks have **4 common variants**.

### 1. Open-network lookalike

Imitates a public or guest Wi-Fi name and relies on user familiarity.

### 2. Captive-portal lure

Displays a fake login or registration page after connection.

### 3. Stronger-signal attraction

Places the rogue AP close enough to look more reliable than the real AP.

### 4. Deauth-assisted attraction

Forces clients off the real AP so they reconnect to the rogue one.

## Impact

Ordered roughly by severity:

- **Credential capture.** Fake portals can trick users into entering passwords.
- **Traffic manipulation.** DNS and unencrypted traffic can be changed.
- **Session compromise.** Weak application security may leak tokens or cookies.
- **Malware delivery.** Captive portals or redirects can lead to hostile content.
- **Trust erosion.** Users learn unsafe habits around Wi-Fi prompts and warnings.

## Detection and defense

Ordered by effectiveness:

1.
**Use WPA-Enterprise with certificate validation for trusted networks.**
   Proper certificate validation gives clients a real network identity check beyond SSID text.

2.
**Disable auto-join for risky public networks.**
   Reducing automatic connection limits silent attraction.

3.
**Monitor for rogue BSSIDs and duplicate SSIDs.**
   Wireless controllers and surveys can detect unauthorized APs using familiar names.

4.
**Train users not to submit credentials to Wi-Fi portals for corporate access.**
   User behavior matters because evil twins often cross into phishing.

5.
**Keep application-layer TLS strong.**
   TLS prevents many same-network manipulations even after a client joins a bad network.

### What does not work as a primary defense

- **Recognizing the SSID name.** Names are easy to copy.
- **Assuming a lock icon in Wi-Fi settings proves safety.** It may only show local link encryption.
- **Using VPN as the only control.** VPN helps after connection but does not fix credential phishing or bad client trust.
- **Ignoring certificate warnings.** Warnings are often the first visible signal of interception.

## Practical labs

Use a closed lab with your own client. Do not collect real credentials.

### Inventory duplicate SSIDs

```
sudo airodump-ng wlan0mon
```

Look for the same ESSID with different BSSIDs, channels, and encryption.

### Create a no-credential awareness lab

```
SSID:
Client behavior:
Captive portal text:
No password fields:
User education point:
```

Demonstrate recognition risk without harvesting secrets.

### Validate rogue AP detection

```
Expected BSSID list:
Detected BSSID list:
Unknown duplicates:
Alert source:
Action taken:
```

Turn the lab into a monitoring check.

### Create a client auto-join inventory

```
device | saved SSIDs | auto-join? | public/open? | owner | change needed
```

Auto-join is the client-side half of evil-twin risk.

### Review portal safety

```
portal asks for credentials:
certificate warning shown:
domain displayed:
training text:
no-secret proof:
```

Awareness labs should avoid collecting credentials or normalizing unsafe entry.

## Practical examples

- A fake coffee-shop SSID attracts laptops configured to auto-join.
- A rogue AP near an office broadcasts the corporate guest network name.
- Users enter VPN credentials into a fake captive portal.
- A device accepts a network with the same SSID but weaker security.
- A wireless controller flags an unknown BSSID broadcasting a protected SSID.

## Related notes

- [[wireless-security]]
- [[wifi-deauthentication]]
- [[mitm-on-local-networks]]
- [[osint|OSINT]]
- [[oauth-security|OAuth Security]]

### Suggested future atomic notes

- captive-portal-security
- enterprise-wifi-8021x
- phishing-kill-chain
- [[mfa-phishing-resistance]]

## References

- **Official Tool Docs:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Official Tool Docs:** Aircrack-ng airbase-ng — https://www.aircrack-ng.org/doku.php?id=airbase-ng
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
