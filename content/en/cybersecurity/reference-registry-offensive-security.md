---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Offensive Security

## Purpose

This note standardizes references for the offensive-security branch.

Use it to:
- keep recon notes tied to strong practical sources
- help Codex choose consistent references
- avoid generic recon content with weak sourcing
- keep the branch centered on discovery, enumeration, validation, and operational handoff while leaving room for broader offensive-security topics

## Source of truth rule

For offensive-security notes, this registry is the primary source of truth.

Use it together with:
- `<a href="offensive-security/index.html">Offensive Security / Recon Index</a>`
- networking and attack-surface registries when notes overlap strongly

---

## Reference selection policy

### Source priority

1. official or primary project documentation
2. practical reconnaissance methodology
3. testing guides and structured frameworks
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

# Offensive / recon topic map

## recon

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OSINT Framework — https://osintframework.com/

## passive-recon

Preferred references:
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OSINT Framework — https://osintframework.com/

## active-recon

Preferred references:
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 105 — https://projectdiscovery.io/blog/reconnaissance-series-5-additional-active-reconnaissance
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## public-asset-discovery

Preferred references:
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## company-mapping

Preferred references:
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance

## tech-stack-fingerprinting

Preferred references:
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger information disclosure — https://portswigger.net/web-security/information-disclosure

## enumeration

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance

## subdomain-enumeration

Preferred references:
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 102 — https://projectdiscovery.io/blog/recon-series-2
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## host-and-port-discovery

Preferred references:
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## scope-validation

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** HackerOne Disclosure Guidelines — https://www.hackerone.com/disclosure-guidelines

## service-validation

Preferred references:
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4

## recon-to-testing-handoff

Preferred references:
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## cloaking-and-security-evasion

Preferred references:
- **Foundational:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Testing / Lab:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance

## nmap-timing-and-evasion

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — Timing and Performance — https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery

## packet-fragmentation-and-decoy-scans

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Research / Deep Dive:** Ptacek & Newsham — Insertion, Evasion, and Denial of Service (1998) — https://insecure.org/stf/secnet_ids/secnet_ids.pdf
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery

## masscan-internet-scale-scanning

Preferred references:
- **Official Tool Docs:** Masscan README and man page — https://github.com/robertdavidgraham/masscan
- **Research / Deep Dive:** Erratasec — Masscan: the entire internet in 3 minutes — https://blog.erratasec.com/2013/09/masscan-entire-internet-in-3-minutes.html
- **Research / Deep Dive:** Durumeric et al. — ZMap (USENIX Security 2013) — https://zmap.io/paper.pdf

## rustscan-and-nse-pipeline

Preferred references:
- **Official Tool Docs:** RustScan repository and docs — https://github.com/RustScan/RustScan
- **Official Tool Docs:** Nmap Scripting Engine — https://nmap.org/book/nse.html
- **Research / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery

> *AD-specific topics (kerberoasting, as-rep-roasting, bloodhound-attack-path-analysis, dcsync-and-ntdsdit-extraction) were promoted to their own branch on 2026-05-10. See [[reference-registry-identity-and-active-directory|Reference Registry — Identity and Active Directory]] for those entries.*

## idle-scan-and-ipid-side-channels

Preferred references:
- **Official Tool Docs:** Nmap Reference Guide — Idle Scan — https://nmap.org/book/idlescan.html
- **Research / Deep Dive:** Antirez — Dumb scan / new TCP scan method (Bugtraq, 1998, original disclosure) — https://seclists.org/bugtraq/1998/Dec/79
- **Research / Deep Dive:** Ensafi et al. — Detecting Intentional Packet Drops on the Internet via TCP/IP Side Channels (USENIX Security 2015) — https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/ensafi

## nse-vuln-category-audit

Preferred references:
- **Official Tool Docs:** Nmap Scripting Engine — Categories — https://nmap.org/book/nse-usage.html#nse-categories
- **Official Tool Docs:** NSE script library — `vuln` category index — https://nmap.org/nsedoc/categories/vuln.html
- **Research / Deep Dive:** David Bianco — The Pyramid of Pain — https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html

---

## Registry usage rules

- choose the smallest set of strongest references for the exact note
- prefer one methodology source plus one practical source where possible
- keep recon notes focused on discovery, validation, and transition into testing
