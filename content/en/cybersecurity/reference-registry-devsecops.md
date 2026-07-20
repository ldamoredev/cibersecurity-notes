---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — DevSecOps

## Purpose

This note standardizes references for the DevSecOps branch.

Use it to:
- keep DevSecOps notes tied to strong primary sources
- help Codex choose consistent references
- avoid vague DevSecOps content with no standards backing
- keep the branch practical and engineering-oriented

## Source of truth rule

For DevSecOps notes, this registry is the primary source of truth.

Use it together with:
- `<a href="devsecops/index.html">DevSecOps Index</a>`
- related reference registries when a note overlaps strongly with APIs, web security, or attack surface

---

## Reference selection policy

### Source priority

1. official standards and primary documentation
2. government or foundation guidance
3. OWASP testing/verification resources
4. high-signal operational guides
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

# DevSecOps topic map

## nist-ssdf

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** NIST SP 800-218 overview/news — https://csrc.nist.gov/Projects/ssdf
- **Foundational:** NIST SSDF project page — https://csrc.nist.gov/projects/ssdf

## secure-by-design

Preferred references:
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** CISA Secure by Design principles and approaches PDF — https://www.cisa.gov/sites/default/files/2023-04/principles_approaches_for_security-by-design-default_508_0.pdf

## asvs-as-dev-process-input

Preferred references:
- **Foundational:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
- **Foundational:** OWASP ASVS Cheat Sheet Index — https://cheatsheetseries.owasp.org/IndexASVS.html

## supply-chain-security

Preferred references:
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design

## dependency-risk

Preferred references:
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final

## artifact-integrity

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html

## ci-cd-hardening

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/

## branch-protection-and-release-controls

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design

## secrets-management

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Foundational:** OWASP Secrets Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## container-security

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design

## image-scanning

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html

## sbom-and-provenance

Preferred references:
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html

---

## Registry usage rules

- choose the smallest set of strongest references for the exact note
- prefer standards and primary guidance over generic blog content
- keep DevSecOps notes focused on engineering workflow and control design
