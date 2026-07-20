---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Dependency Risk

## Definition

Dependency risk is the security risk introduced by direct and transitive third-party libraries, frameworks, packages, and their update and trust patterns.

## Why it matters

Dependencies expand the codebase, privilege surface, and maintenance burden beyond what the product team directly writes. Risk comes not only from known CVEs, but from maintenance quality, version drift, trust decisions, and package ecosystem abuse.
Keep the boundary tight: this note is about upstream package trust and maintenance exposure, not artifact tampering or release traceability after the build.

## Attacker perspective

Attackers look for:
- outdated packages with known issues
- poorly maintained libraries
- dependency confusion and typosquatting opportunities
- transitive packages nobody is watching

## Defender perspective

Defenders should:
- minimize dependency count where sensible
- track direct and transitive dependencies
- prioritize based on reachability and impact, not raw count alone
- establish update and retirement discipline

## Practical examples

- a vulnerable package lingers because nobody owns update cadence
- a transitive dependency introduces risk the team did not know existed
- package trust is assumed because “it is popular”

## Related notes

- [[supply-chain-security]]
- [[sbom-and-provenance]]
- [[ci-cd-hardening]]
- [[image-scanning]]

## References

- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
