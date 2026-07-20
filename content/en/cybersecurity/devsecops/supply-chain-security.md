---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Supply Chain Security

## Definition

Supply chain security is the practice of reducing risk introduced by third-party code, build systems, dependencies, artifacts, signing paths, and release distribution processes.

## Why it matters

Modern software is assembled from many upstream parts. DevSecOps is incomplete if it secures only first-party code while ignoring dependencies, transitive packages, build integrity, and release provenance.
This note is the umbrella for the supply-chain cluster: [[dependency-risk]] covers upstream package exposure, [[artifact-integrity]] covers tamper resistance in outputs, and [[sbom-and-provenance]] covers component and build traceability.

## Attacker perspective

Attackers target supply chains because one compromise can scale across many downstream consumers. Weaknesses in package trust, build systems, secrets, and artifacts can bypass strong runtime security entirely.

## Defender perspective

Defenders should:
- understand where software components come from
- reduce unnecessary trust in upstreams
- secure the build and release path
- verify what is shipped, not just what is developed

## Practical examples

- a dependency update pulls in a malicious or compromised package
- a build artifact is replaced after CI but before release
- teams track vulnerabilities but not provenance or trust boundaries

## Related notes

- [[dependency-risk]]
- [[artifact-integrity]]
- [[sbom-and-provenance]]
- [[third-party-exposure|Third-Party Exposure]]

## References

- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
