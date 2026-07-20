---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Privacy, Anonymity & OPSEC Index

## Purpose

This index is the root entry point for the Privacy, Anonymity & OPSEC branch of the cybersecurity atlas.

Use it to understand how privacy tools actually change a threat model:
- what they hide
- what they expose
- who they shift trust toward
- what metadata remains
- where operational mistakes defeat the tool

The branch avoids cryptocurrency and darknet-market framing. Its focus is privacy engineering, anonymity limits, VPN threat models, Tor, metadata leakage, encrypted communication, compartmentalized systems, secure deletion, and common deanonymization failures.

Use [[reference-registry-privacy-anonymity-opsec|Reference Registry - Privacy, Anonymity & OPSEC]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).

> *Always-on:* this branch is a parallel personal discipline, not a phase. Read alongside everything else.

---

## Branch mental model

Privacy tools do not create anonymity by default.
They change visibility, trust, metadata exposure, and failure modes.

The recurring question is not "is this tool private?" It is:

```
Against which observer, for which activity, with which identity signals still present?
```

---

## Recommended learning order

### Core vocabulary and leakage

1. [[privacy-vs-anonymity-vs-confidentiality]]
2. [[metadata-and-identity-leakage]]
3. [[vpn-threat-models]]

### VPNs and routing trust

1. [[vpn-protocols]]
2. [[vpn-logging-and-trust]]
3. [[vpn-leakage-risks]]
4. [[vpn-dns-and-ipv6-leaks]]
5. [[vpn-kill-switches]]
6. [[vpn-fingerprinting-limitations]]
7. [[vpn-vs-tor]]

### Tor, composition, and file OPSEC

1. [[tor-and-onion-services]]
2. [[tor-browser-security-settings]]
3. [[tor-bridges-and-pluggable-transports]]
4. [[vpn-with-tor]]
5. [[corporate-vpns-vs-consumer-vpns]]
6. [[file-metadata-removal]]

### Anonymity environments and sharing

1. [[tails-operational-model]]
2. [[qubes-compartmentalization]]
3. [[whonix-gateway]]
4. [[secure-file-sharing]]
5. [[anonymity-threat-models]]
6. [[deanonymization-failures]]

### Messaging and email privacy

1. [[private-email-threat-models]]
2. [[temporary-email-risks]]
3. [[xmpp-and-private-messaging]]
4. [[end-to-end-encryption]]
5. [[pgp-encryption-and-signatures]]

### Storage and deletion

1. [[secure-deletion-and-storage-wiping]]

### OPSEC and correlation

1. [[opsec-failure-chains]]
2. [[browser-fingerprinting]]
3. [[account-correlation]]
4. [[traffic-correlation]]

---

## Current mature starter notes

### Core model

- [[privacy-vs-anonymity-vs-confidentiality]]
- [[metadata-and-identity-leakage]]

### VPN model

- [[vpn-threat-models]]
- [[vpn-protocols]]
- [[vpn-logging-and-trust]]
- [[vpn-leakage-risks]]
- [[vpn-dns-and-ipv6-leaks]]
- [[vpn-kill-switches]]
- [[vpn-fingerprinting-limitations]]
- [[vpn-vs-tor]]
- [[vpn-with-tor]]
- [[corporate-vpns-vs-consumer-vpns]]

### Tor, environment, and file OPSEC

- [[tor-and-onion-services]]
- [[tor-browser-security-settings]]
- [[tor-bridges-and-pluggable-transports]]
- [[tails-operational-model]]
- [[qubes-compartmentalization]]
- [[whonix-gateway]]
- [[file-metadata-removal]]
- [[secure-file-sharing]]
- [[anonymity-threat-models]]
- [[deanonymization-failures]]

### Messaging and email privacy

- [[private-email-threat-models]]
- [[temporary-email-risks]]
- [[xmpp-and-private-messaging]]
- [[end-to-end-encryption]]
- [[pgp-encryption-and-signatures]]

### Storage and deletion

- [[secure-deletion-and-storage-wiping]]

### OPSEC and correlation

- [[opsec-failure-chains]]
- [[browser-fingerprinting]]
- [[account-correlation]]
- [[traffic-correlation]]

---

## Cross-links to other branches

### Networking

- [[dns-resolution|DNS Resolution]]
- [[dns-security|DNS Security]]
- [[tls-https|TLS / HTTPS]]
- [[cookies-and-sessions|Cookies and Sessions]]
- [[http-headers|HTTP Headers]]

### Web and API security

- [[session-management|Session Management]]
- [[content-security-policy|Content Security Policy]]
- [[oauth-security|OAuth Security]]
- [[token-lifecycle|Token Lifecycle]]

### OSINT

- [[osint|OSINT]]
- [[social-media-osint|Social Media OSINT]]
- [[image-and-location-osint|Image and Location OSINT]]
- [[email-and-phone-osint|Email and Phone OSINT]]

### Cloud and DevSecOps

- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[secrets-management|Secrets Management]]
- [[secure-by-design|Secure by Design]]

---

## Practical lab queue

Future private lab candidate: privacy and OPSEC lab.

Possible exercises:
- compare visible IP address before and after a VPN
- test DNS leak paths
- test IPv6 leak paths
- inspect browser fingerprint surfaces
- inspect file metadata before sharing
- remove image metadata and verify removal
- compare VPN vs Tor routing visibility
- simulate VPN disconnect behavior with a kill switch
- document an OPSEC failure chain from harmless-looking clues

---

## Branch maintenance notes

- Keep the branch defensive, educational, and threat-model oriented.
- Avoid cryptocurrency, marketplace, and evasion-for-crime framing.
- Treat anonymity as an adversary-specific property, not a product label.
- Keep VPN notes precise: VPNs shift network-path trust; they do not erase identity.
- Keep Tor notes careful: Tor changes the observer model but still requires disciplined browser and account behavior.
- Keep OPSEC notes practical: identities leak through accounts, behavior, files, time, language, device state, and social context.
- Note-local suggested future links remain useful for adjacent subtopics, but the branch-level backlog for this pass is closed.

## References

- **Foundational:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Foundational:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Official Tool Docs:** Tor Browser User Manual - https://tb-manual.torproject.org/
