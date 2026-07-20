---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Wireless Security

## Purpose

This note standardizes references for the wireless-security branch.

Use it to:
- keep wireless notes tied to official, practical, high-signal sources
- avoid turning the branch into a random tool list
- preserve the boundary between authorized lab work and unsafe activity
- help future agents choose consistent references

## Source of truth rule

For wireless-security notes, this registry is the primary source of truth.

Use it together with:
- [[index|Wireless Security Index]]
- [[index|Networking Index]]
- [[index|Offensive Security / Recon Index]]

---

## Reference selection policy

### Source priority

1. official standards, vendor, and project documentation
2. official tool documentation
3. practical packet-analysis documentation
4. high-signal security research
5. secondary sources only when they add clear value

### Per-note target

- minimum 2 references
- ideal 3 references
- avoid long reference lists in atomic notes

### Labeling

Use:
- **Foundational**
- **Official Tool Docs**
- **Testing / Lab**
- **Research / Deep Dive**
- **Mitigation**

---

# Wireless topic map

## wireless-security

Preferred references:
- **Foundational:** Wi-Fi Alliance WPA3 — https://www.wi-fi.org/discover-wi-fi/security
- **Official Tool Docs:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
- **Official Tool Docs:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html

## wifi-monitor-mode

Preferred references:
- **Official Tool Docs:** Aircrack-ng airmon-ng — https://www.aircrack-ng.org/doku.php?id=airmon-ng
- **Official Tool Docs:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
- **Official Tool Docs:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng

## wifi-deauthentication

Preferred references:
- **Official Tool Docs:** Aircrack-ng aireplay-ng — https://www.aircrack-ng.org/doku.php?id=aireplay-ng
- **Official Tool Docs:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Mitigation:** Wi-Fi Alliance WPA3 / Protected Management Frames context — https://www.wi-fi.org/discover-wi-fi/security

## wep-security

Preferred references:
- **Official Tool Docs:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
- **Official Tool Docs:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## wpa-wpa2-handshakes

Preferred references:
- **Official Tool Docs:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Official Tool Docs:** Aircrack-ng airodump-ng — https://www.aircrack-ng.org/doku.php?id=airodump-ng
- **Foundational:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## wifi-wordlist-attacks

Preferred references:
- **Official Tool Docs:** Aircrack-ng WPA/WPA2 tutorial — https://www.aircrack-ng.org/doku.php?id=cracking_wpa
- **Official Tool Docs:** Hashcat example hashes — https://hashcat.net/wiki/doku.php?id=example_hashes
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## evil-twin-access-points

Preferred references:
- **Official Tool Docs:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Official Tool Docs:** Aircrack-ng airbase-ng — https://www.aircrack-ng.org/doku.php?id=airbase-ng
- **Mitigation:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security

## arp-poisoning

Preferred references:
- **Official Tool Docs:** bettercap ARP spoofing module — https://www.bettercap.org/modules/ethernet/spoofers/arpspoof/
- **Official Tool Docs:** Wireshark User's Guide — https://www.wireshark.org/docs/wsug_html/
- **Foundational:** RFC 826 (Address Resolution Protocol) — https://datatracker.ietf.org/doc/html/rfc826

## mitm-on-local-networks

Preferred references:
- **Official Tool Docs:** bettercap documentation — https://www.bettercap.org/
- **Official Tool Docs:** Wireshark User's Guide — https://www.wireshark.org/docs/wsug_html/
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## bettercap-workflows

Preferred references:
- **Official Tool Docs:** bettercap documentation — https://www.bettercap.org/
- **Official Tool Docs:** bettercap WiFi module — https://www.bettercap.org/modules/wifi/
- **Official Tool Docs:** bettercap ARP spoofing module — https://www.bettercap.org/modules/ethernet/spoofers/arpspoof/

---

## Registry usage rules

- Use active attack tooling only in notes that explicitly name an owned lab or written authorization boundary.
- Prefer capture, observation, and defensive validation labs before disruptive labs.
- Keep Wi-Fi radio mechanics in this branch and generic TCP/IP mechanics in [[index]].
- Keep credential theft and phishing mechanics out of wireless notes unless the note is explicitly defensive and points to social-engineering controls.
