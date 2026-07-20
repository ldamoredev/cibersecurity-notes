---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Attack Surface Mapping

## Purpose

This note standardizes references for the attack-surface-mapping branch.

Use it to:
- keep exposure-oriented notes tied to strong sources
- help Codex choose consistent references
- avoid random recon blogspam
- keep the branch focused on practical discoverability and exposure control

## Source of truth rule

For attack-surface-mapping notes, this registry is the primary source of truth.

Use it together with:
- `<a href="attack-surface-mapping/index.html">Attack Surface Mapping Index</a>`
- the related networking and API-security reference registries when a note overlaps strongly

---

## Reference selection policy

### Source priority

1. official standards and project documentation
2. practical recon / ASM guidance
3. testing guides
4. high-signal research
5. secondary sources only when they add clear value

### Per-note target

- minimum 2 references
- ideal 3 references

### Labeling

Use:
- **Foundational**
- **Testing / Lab**
- **Research / Deep Dive**
- **Official Tool Docs**

---

# Attack-surface topic map

## attack-surface-mapping

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools
- **Foundational:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services

## external-attack-surface

Preferred references:
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services

## internal-attack-surface

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP API7:2023 SSRF — https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/

## exposed-service-triage

Preferred references:
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4

## endpoint-discovery

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4

## admin-interface-discovery

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## subdomain-takeover

Preferred references:
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers / subdomain takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## exposed-storage

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design

## deprecated-api-versions

Preferred references:
- **Foundational:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## third-party-exposure

Preferred references:
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP API10:2023 Unsafe Consumption of APIs — https://owasp.org/API-Security/editions/2023/en/0xaa-unsafe-consumption-of-apis/
- **Research / Deep Dive:** ProjectDiscovery ASM article — https://projectdiscovery.io/blog/asm-platform-using-projectdiscovery-tools

---

## Registry usage rules

- choose the smallest set of strongest references for the exact note
- prefer standards plus one practical discovery source
- keep attack-surface notes focused on exposure, discoverability, and drift
