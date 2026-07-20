---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry - Privacy, Anonymity & OPSEC

## Purpose

This note standardizes references for the Privacy, Anonymity & OPSEC branch.

Use it to:
- keep privacy and anonymity notes tied to official, practical, high-signal sources
- avoid vendor-marketing drift, VPN listicles, and tool-ranking sprawl
- evaluate claims through threat models, trust boundaries, metadata, and operational failure modes
- help future agents choose consistent references

## Source of truth rule

For notes under [[index|Privacy, Anonymity & OPSEC]], this registry is the primary source of truth.

Use it together with:
- [[reference-registry-networking|Reference Registry - Networking]]
- [[reference-registry-osint|Reference Registry - OSINT]]
- [[reference-registry-web-security|Reference Registry - Web Security]]
- [[reference-registry-devsecops|Reference Registry - DevSecOps]]

---

## Reference selection policy

### Source priority

1. official standards, project documentation, and maintainer documentation
2. civil-society privacy guidance from high-trust organizations
3. official tool documentation for verification and metadata inspection
4. high-signal research on anonymity limits, browser fingerprinting, or deanonymization
5. vendor sources only when they explain their own architecture or audit model

### Per-note target

- minimum 2 references
- ideal 3 references
- maximum 5 references unless a topic genuinely spans several independent systems

### Labeling

Use:
- **Foundational**
- **Threat Model**
- **Official Tool Docs**
- **Testing / Lab**
- **Mitigation**
- **Research / Deep Dive**
- **Ethics / Safety**

### Avoid

- "best VPN" rankings
- affiliate-marketing review pages
- generic privacy tips without a clear threat model
- claims that treat "private", "anonymous", and "encrypted" as synonyms

---

# Topic map

## privacy-vs-anonymity-vs-confidentiality

Preferred references:
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Foundational:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## metadata-and-identity-leakage

Preferred references:
- **Foundational:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** ExifTool documentation - https://exiftool.org/
- **Official Tool Docs:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/

## anonymity-threat-models

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Research / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf

## deanonymization-failures

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Research / Deep Dive:** Tor Project: Research safety board and research resources - https://research.torproject.org/

## tor-and-onion-services

Preferred references:
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Official Tool Docs:** Tor Browser: Onion Services - https://support.torproject.org/tor-browser/features/onion-services/
- **Research / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf

## tor-browser-security-settings

Preferred references:
- **Official Tool Docs:** Tor Browser Security Levels - https://support.torproject.org/tor-browser/features/security-levels/
- **Official Tool Docs:** Tor Browser Fingerprinting Protections - https://support.torproject.org/tor-browser/features/fingerprinting-protections/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## tor-bridges-and-pluggable-transports

Preferred references:
- **Official Tool Docs:** Tor Browser Censorship Circumvention - https://support.torproject.org/tor-browser/circumvention/
- **Official Tool Docs:** Tor: Using Bridges - https://support.torproject.org/little-t-tor/circumvention/using-bridges/
- **Research / Deep Dive:** Tor Project Anti-censorship - https://community.torproject.org/anti-censorship/

## vpn-threat-models

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework

## vpn-protocols

Preferred references:
- **Official Tool Docs:** WireGuard - https://www.wireguard.com/
- **Official Tool Docs:** OpenVPN Community Documentation - https://openvpn.net/community-docs/
- **Official Tool Docs:** strongSwan documentation - https://docs.strongswan.org/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you

## vpn-logging-and-trust

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## vpn-leakage-risks

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Official Tool Docs:** ExifTool documentation - https://exiftool.org/

## vpn-kill-switches

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** WireGuard - https://www.wireguard.com/
- **Official Tool Docs:** OpenVPN Community Resources - https://openvpn.net/community-resources/

## vpn-dns-and-ipv6-leaks

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** [[dns-resolution|DNS Resolution]]
- **Foundational:** [[dns-security|DNS Security]]
- **Official Tool Docs:** Tor Browser User Manual: Secure Connections - https://tb-manual.torproject.org/secure-connections/

## vpn-fingerprinting-limitations

Preferred references:
- **Official Tool Docs:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## vpn-vs-tor

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Official Tool Docs:** Tor Project Support: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/

## vpn-with-tor

Preferred references:
- **Official Tool Docs:** Tor Project Support: Tor Browser with VPN - https://support.torproject.org/tor-browser/general/vpn-with-tor/
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/

## corporate-vpns-vs-consumer-vpns

Preferred references:
- **Threat Model:** EFF Choosing the VPN That's Right for You - https://ssd.eff.org/module/choosing-vpn-thats-right-you
- **Foundational:** NIST Zero Trust Architecture SP 800-207 - https://csrc.nist.gov/pubs/sp/800/207/final
- **Foundational:** CISA Zero Trust Maturity Model - https://www.cisa.gov/zero-trust-maturity-model

## tails-operational-model

Preferred references:
- **Official Tool Docs:** Tails documentation - https://tails.net/doc/
- **Official Tool Docs:** Tails: warnings - https://tails.net/doc/about/warnings/
- **Official Tool Docs:** Tor Browser User Manual - https://tb-manual.torproject.org/

## qubes-compartmentalization

Preferred references:
- **Official Tool Docs:** Qubes OS documentation - https://doc.qubes-os.org/en/latest/
- **Official Tool Docs:** Qubes OS architecture - https://doc.qubes-os.org/en/latest/developer/system/architecture.html
- **Threat Model:** Qubes OS security design goals - https://doc.qubes-os.org/en/latest/developer/system/security-design-goals.html

## whonix-gateway

Preferred references:
- **Official Tool Docs:** Whonix documentation - https://www.whonix.org/wiki/Documentation
- **Official Tool Docs:** Whonix Gateway - https://www.whonix.org/wiki/Whonix-Gateway
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/

## private-email-threat-models

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/

## temporary-email-risks

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## xmpp-and-private-messaging

Preferred references:
- **Official Tool Docs:** XMPP Standards Foundation - https://xmpp.org/
- **Official Tool Docs:** OMEMO XEP-0384 - https://xmpp.org/extensions/xep-0384.html
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## end-to-end-encryption

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Research / Deep Dive:** Signal Protocol documentation - https://signal.org/docs/

## pgp-encryption-and-signatures

Preferred references:
- **Official Tool Docs:** GnuPG Manual - https://gnupg.org/documentation/manuals/gnupg/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** OpenPGP RFC 9580 - https://www.rfc-editor.org/rfc/rfc9580

## file-metadata-removal

Preferred references:
- **Official Tool Docs:** ExifTool documentation - https://exiftool.org/
- **Official Tool Docs:** Tails: Removing metadata from files - https://tails.net/doc/sensitive_documents/metadata/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## secure-file-sharing

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html
- **Official Tool Docs:** OnionShare documentation - https://docs.onionshare.org/

## secure-deletion-and-storage-wiping

Preferred references:
- **Official Tool Docs:** Tails: secure deletion - https://tails.net/doc/encryption_and_privacy/secure_deletion/
- **Official Tool Docs:** NIST SP 800-88 Rev. 1 - https://csrc.nist.gov/publications/detail/sp/800-88/rev-1/final
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

## opsec-failure-chains

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Foundational:** NIST Privacy Framework - https://www.nist.gov/privacy-framework
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/

## browser-fingerprinting

Preferred references:
- **Official Tool Docs:** Tor Browser User Manual: Anti-fingerprinting - https://tb-manual.torproject.org/anti-fingerprinting/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## account-correlation

Preferred references:
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/
- **Official Tool Docs:** Tor Browser User Manual: Managing Identities - https://tb-manual.torproject.org/managing-identities/
- **Mitigation:** OWASP User Privacy Protection Cheat Sheet - https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html

## traffic-correlation

Preferred references:
- **Research / Deep Dive:** Tor design paper - https://svn-archive.torproject.org/svn/projects/design-paper/tor-design.pdf
- **Official Tool Docs:** Tor Project Support - https://support.torproject.org/
- **Threat Model:** EFF Surveillance Self-Defense - https://ssd.eff.org/

---

## Registry usage rules

- Choose the smallest reference set that supports the exact note.
- Prefer official project docs for tool behavior and EFF/NIST/OWASP for threat-model framing.
- Do not cite VPN provider marketing as evidence for general VPN claims.
- When vendor claims are discussed, label them as claims and evaluate them through audits, architecture, jurisdiction, incentives, and observed history.
- For notes involving people, accounts, or sensitive personal data, include an ethics/safety reference and keep examples defensive.
