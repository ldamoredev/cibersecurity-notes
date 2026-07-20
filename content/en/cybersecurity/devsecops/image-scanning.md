---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Image Scanning

## Definition

Image scanning is the process of inspecting container images for known vulnerabilities, risky packages, and other issues before promotion or deployment.

## Why it matters

Image scanning is useful, but only when placed in the right context. It does not replace dependency management, build integrity, or secure base image strategy. It is one signal inside a larger DevSecOps system.
This note stays intentionally narrow: scanning helps surface known issues, but it cannot by itself prove a container is well designed, minimally privileged, or safely promoted.

## Attacker perspective

Attackers benefit when teams:
- trust scan output blindly
- ignore unscanned images and side paths
- use vulnerable bases because “the build passed”
- rely on scanning without fixing or prioritization

## Defender perspective

Defenders should:
- treat scanning as one control among many
- scan early and before release
- prioritize by exploitability and exposure, not just count
- understand scanner blind spots and false confidence risks

## Practical examples

- images pass a scan gate but still contain risky unused tooling and poor defaults
- a side-loaded image path bypasses scanning entirely
- teams scan but do not triage or remediate meaningfully

## Related notes

- [[container-security]]
- [[dependency-risk]]
- [[ci-cd-hardening]]
- [[sbom-and-provenance]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** OWASP Software Supply Chain Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
