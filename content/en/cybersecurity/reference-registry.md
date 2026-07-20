---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Cybersecurity Reference Registry

## Purpose

This note is the root reference policy for the cybersecurity atlas.

It exists to:
- define global reference quality rules
- define preferred source families
- provide fallback guidance when a branch-specific reference registry does not yet cover a topic

This note is **not** the main registry for every topic.

## Source of truth rule

For any mature branch, use the branch-specific registry first.

Examples:
- [[reference-registry-cryptography|Reference Registry — Cryptography]]
- [[reference-registry-networking|Reference Registry — Networking]]
- [[reference-registry-web-security|Reference Registry — Web Security]]
- [[reference-registry-api-security|Reference Registry — API Security]]
- [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]]
- [[reference-registry-devsecops|Reference Registry — DevSecOps]]
- [[reference-registry-detection-engineering|Reference Registry — Detection Engineering]]
- [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]]
- [[reference-registry-offensive-security|Reference Registry — Offensive Security]]
- [[reference-registry-privacy-anonymity-opsec|Reference Registry — Privacy, Anonymity & OPSEC]]
- [[reference-registry-playbooks|Reference Registry — Playbooks]]

Use this root registry only when:
- a branch registry does not yet exist
- a note is cross-branch and no branch registry clearly owns it
- a new topic needs temporary fallback guidance

---

## Global reference policy

### Source priority

1. official standards and project documentation
2. official labs and primary learning platforms
3. official tool documentation
4. high-signal research
5. secondary sources only when they add clear value

### Per-note target

- minimum 2 references
- ideal 3 references
- default maximum 5 references

### Labeling

Use:
- **Foundational**
- **Testing / Lab**
- **Research / Deep Dive**
- **Official Tool Docs**

### Reference quality rule

Prefer:
- fewer, stronger references
- primary sources over summaries
- sources that match the exact topic of the note
- references that support understanding, testing, and mitigation

Avoid:
- random blogspam
- generic “top 10 tools” posts
- references that are only loosely related
- long reference lists without a clear purpose

---

## Preferred source families

### Core application security

- OWASP Top 10
- OWASP WSTG
- OWASP API Security Project
- OWASP Cheat Sheet Series
- OWASP ASVS
- OWASP MASVS / MASTG

### Practical exploitation and labs

- PortSwigger Web Security Academy
- PortSwigger Research

### Networking and protocol understanding

- MDN HTTP docs
- Nmap docs
- Wireshark docs

### Secure engineering and software delivery

- NIST SSDF
- CISA Secure by Design

### Detection engineering and monitoring

- Zeek documentation
- Suricata documentation
- IETF IPFIX / NetFlow references
- Microsoft Defender XDR advanced hunting schema
- MITRE ATT&CK data sources
- MITRE ATT&CK detection strategies and analytics
- CISA event logging and threat detection guidance
- Elastic Security Labs detection engineering research
- Elastic Common Schema and OpenTelemetry semantic conventions
- JA3 / JA4 TLS fingerprinting references

### Identity and Active Directory

- Microsoft Learn Active Directory and Windows Server identity documentation
- MITRE ATT&CK Kerberos ticket, credential access, and detection strategy entries
- SpecterOps / BloodHound research and documentation
- ADSecurity / Sean Metcalf canonical Kerberos and AD compromise research
- RFC 4120 and Kerberos protocol references when protocol mechanics are central

### Recon and exposure discovery

- ProjectDiscovery research and recon series
- OSINT Framework

### Privacy, anonymity, and OPSEC

- EFF Surveillance Self-Defense
- NIST Privacy Framework
- OWASP User Privacy Protection Cheat Sheet
- Tor Project documentation
- Tails, Qubes, and Whonix official documentation

### Cryptography

- NIST Cryptographic Standards and Guidelines
- RFCs for TLS, JOSE/JWT, PKIX, and password-based cryptography
- OWASP Cryptographic Storage Cheat Sheet
- OWASP Password Storage Cheat Sheet
- libsodium documentation

---

## Atlas rule

Branch registries override this note.

This note should remain short, stable, and policy-oriented.
It should not grow into a giant duplicate of all branch registries.
