---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Wireless Security Index

## Purpose

This index is the root entry point for the wireless-security branch of the cybersecurity atlas.

Use it to:
- understand Wi-Fi as a radio, frame, association, and authentication system
- practice wireless observation in owned labs
- separate packet capture, disruption, credential-risk, and local-network MITM concepts
- connect wireless findings back to networking, OSINT, offensive recon, and defensive controls

Use [[reference-registry-wireless-security|Reference Registry — Wireless Security]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[tcp-ip-basics|TCP/IP basics]] and [[ports-and-services|Ports and services]] — Wi-Fi is just radio + frames on top of L2/L3.

---

## Recommended learning order

### Phase 1 — Wireless model and observation

1. [[wireless-security]]
2. [[wifi-monitor-mode]]

### Phase 2 — Legacy and modern Wi-Fi authentication

1. [[wep-security]]
2. [[wpa-wpa2-handshakes]]
3. [[wifi-wordlist-attacks]]

### Phase 3 — Management frames and rogue access points

1. [[wifi-deauthentication]]
2. [[evil-twin-access-points]]

### Phase 4 — Local-network interception

1. [[arp-poisoning]]
2. [[mitm-on-local-networks]]
3. [[bettercap-workflows]]

---

## Core Wireless Security Cluster

### Branch maturity

This branch is depth-mature as of 2026-04-30.

All 10 atomic notes follow the canonical 11-section template, include practical labs, and now carry worked examples that connect wireless observations to owned-lab evidence, defensive controls, rollback, and safety boundaries.

### Foundations

- [[wireless-security]]
- [[wifi-monitor-mode]]

### Authentication and key risk

- [[wep-security]]
- [[wpa-wpa2-handshakes]]
- [[wifi-wordlist-attacks]]

### Management-plane attacks

- [[wifi-deauthentication]]
- [[evil-twin-access-points]]

### Local-network MITM

- [[arp-poisoning]]
- [[mitm-on-local-networks]]
- [[bettercap-workflows]]

---

## Cross-links to other branches

### Networking

- [[tcp-ip-basics|TCP/IP Basics]]
- [[ports-and-services|Ports and Services]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[nat-and-private-networks|NAT and Private Networks]]

### Offensive / recon

- [[recon|Recon]]
- [[active-recon|Active Recon]]
- [[scope-validation|Scope Validation]]
- [[service-validation|Service Validation]]

### OSINT and attack surface

- [[osint|OSINT]]
- [[internal-attack-surface|Internal Attack Surface]]
- [[exposed-service-triage|Exposed Service Triage]]

---

## Suggested future notes

- wifi-channel-and-band-planning
- wpa3-sae
- enterprise-wifi-8021x
- wps-security
- bluetooth-security
- zigbee-security
- wireless-intrusion-detection
- radio-frequency-basics

### Possible future playbooks

- build-owned-wifi-lab
- audit-home-wifi-security
- capture-wifi-handshake-in-lab
- detect-rogue-access-points
- validate-local-network-mitm-controls

---

## Branch maintenance notes

- Keep this branch focused on wireless medium, Wi-Fi frames, authentication, rogue access points, and local-network interception.
- Keep generic IP routing, DNS, HTTP, TLS, and packet-analysis fundamentals in [[index]].
- All disruptive wireless procedures must be framed as owned-lab or explicitly authorized work.
- Prefer observation-first labs before injection, deauthentication, or spoofing labs.
- Use unresolved wikilinks for future atomic notes so Obsidian can track the branch expansion.
- Maintain the lab-safety pattern: every active wireless note should name scope, owned devices, expected impact, evidence captured, and rollback verification.

## References

- **Foundational:** Wi-Fi Alliance security overview — https://www.wi-fi.org/discover-wi-fi/security
- **Official Tool Docs:** Aircrack-ng documentation — https://www.aircrack-ng.org/documentation.html
- **Official Tool Docs:** Wireshark User's Guide: Wireless — https://www.wireshark.org/docs/wsug_html/#ChWireless
