---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# SBOM and Provenance

## Definition

An SBOM records what software components are in a product, while provenance provides traceability about how, where, and from what those artifacts were built.

## Why it matters

You cannot govern software risk well if you do not know what is inside your artifacts or how they were produced. SBOM and provenance improve incident response, dependency review, release confidence, and downstream trust.
Keep the distinction sharp: SBOM and provenance improve visibility and traceability, while [[artifact-integrity]] focuses on whether artifacts stayed trustworthy and [[dependency-risk]] focuses on upstream package exposure.

## Attacker perspective

Attackers benefit when teams cannot answer:
- what components are in this release?
- which build produced it?
- what upstreams were involved?
- which versions are deployed where?

## Defender perspective

Defenders should:
- understand what is being shipped
- connect components to builds and releases
- improve response speed when new upstream risk appears
- use provenance to reinforce artifact trust

## Practical examples

- a team cannot quickly identify where a vulnerable transitive package is deployed
- an artifact exists in production with unclear build origin
- release records do not capture enough component detail for rapid triage

## Related notes

- [[supply-chain-security]]
- [[artifact-integrity]]
- [[dependency-risk]]
- [[api-inventory-management|API Inventory Management]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
