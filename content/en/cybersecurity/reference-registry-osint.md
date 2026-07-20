---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — OSINT

## Purpose

This note standardizes references for the OSINT branch.

Use it to:
- keep OSINT notes tied to practical, high-signal sources
- avoid weak tool-list sprawl
- keep the branch focused on public-source investigation, evidence quality, ethics, and reporting
- help future agents choose consistent references

## Source of truth rule

For OSINT notes, this registry is the primary source of truth.

Use it together with:
- [[index|OSINT Index]]
- [[reference-registry-offensive-security|Reference Registry — Offensive Security]]
- [[reference-registry-attack-surface-mapping|Reference Registry — Attack Surface Mapping]]

---

## Reference selection policy

### Source priority

1. official documentation for search engines, tools, and public-data providers
2. established OSINT investigation toolkits and methodology sources
3. testing/security guides when OSINT connects to exposure
4. high-signal research and investigative methodology
5. secondary sources only when they add clear practical value

### Per-note target

- minimum 2 references
- ideal 3 references
- avoid long tool dumps inside atomic notes

### Labeling

Use:
- **Foundational**
- **Official Tool Docs**
- **Testing / Lab**
- **Research / Deep Dive**
- **Ethics / Safety**

---

# OSINT topic map

## osint

Preferred references:
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/

## osint-triage

Preferred references:
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/

## search-engine-operators

Preferred references:
- **Official Tool Docs:** Google Search Help: refine searches — https://support.google.com/websearch/answer/2466433/refine-web-searches
- **Official Tool Docs:** Google Advanced Search Help — https://support.google.com/websearch/answer/35890
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit

## google-dorking

Preferred references:
- **Official Tool Docs:** Exploit-DB Google Hacking Database — https://www.exploit-db.com/google-hacking-database
- **Official Tool Docs:** Google Search Help: refine searches — https://support.google.com/websearch/answer/2466433/refine-web-searches
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/

## breach-and-leak-intelligence

Preferred references:
- **Official Tool Docs:** Have I Been Pwned API documentation — https://haveibeenpwned.com/API/v3
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/

## social-media-osint

Preferred references:
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Ethics / Safety:** EFF Surveillance Self-Defense — https://ssd.eff.org/

## email-and-phone-osint

Preferred references:
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Official Tool Docs:** Have I Been Pwned API documentation — https://haveibeenpwned.com/API/v3
- **Ethics / Safety:** EFF Surveillance Self-Defense — https://ssd.eff.org/

## image-and-location-osint

Preferred references:
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Official Tool Docs:** ExifTool by Phil Harvey — https://exiftool.org/
- **Foundational:** OSINT Framework — https://osintframework.com/

## company-osint

Preferred references:
- **Foundational:** OSINT Framework — https://osintframework.com/
- **Research / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/

## osint-reporting

Preferred references:
- **Foundational:** Bellingcat Online Investigation Toolkit — https://bellingcat.gitbook.io/toolkit
- **Foundational:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OSINT Framework — https://osintframework.com/

---

## Registry usage rules

- choose the smallest set of strongest references for the exact note
- prefer methodology and official tool docs over generic listicles
- avoid turning notes into tool catalogs; list workflows and evidence decisions instead
- include ethics/safety references when people, accounts, or sensitive personal data are involved
