---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Artifact Integrity

## Definition

Artifact integrity is the assurance that build outputs, packages, images, and release artifacts have not been tampered with and can be traced back to the intended build process.

## Why it matters

If you cannot trust what was built and shipped, security checks earlier in the pipeline lose much of their value. Integrity is about preserving trust from source to release.
This is distinct from [[dependency-risk]] and [[sbom-and-provenance]]: the question here is whether the shipped artifact stayed trustworthy, not just what components it contains or where they came from.

## Attacker perspective

Attackers target artifact integrity by:
- tampering with build outputs
- swapping artifacts after CI
- abusing weak release controls
- exploiting gaps between build, storage, and deployment

## Defender perspective

Defenders should:
- limit who and what can write release artifacts
- trace artifacts back to specific builds and commits
- review storage and promotion paths
- separate build trust from deployment trust intentionally

## Practical examples

- a release artifact in storage is mutable after build
- deployment pulls “latest” instead of a controlled immutable artifact
- there is no reliable way to prove which source produced a shipped binary

## Related notes

- [[supply-chain-security]]
- [[ci-cd-hardening]]
- [[sbom-and-provenance]]
- [[branch-protection-and-release-controls]]
- [[exposed-storage|Exposed Storage]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
