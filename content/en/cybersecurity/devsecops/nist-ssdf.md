---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# NIST SSDF

## Definition

The Secure Software Development Framework (SSDF) is NIST’s framework for integrating software security into development practices across the organization, toolchain, and release process.

## Why it matters

SSDF gives DevSecOps a durable structure. It turns “security in the pipeline” from a vague aspiration into concrete practices around preparing the organization, protecting software, producing well-secured software, and responding to vulnerabilities.
This note is the framework anchor for the branch; [[secure-by-design]] is the product philosophy, while [[asvs-as-dev-process-input]] is a concrete verification input teams can feed into delivery work.

## Attacker perspective

Attackers benefit when teams treat security as ad hoc tooling instead of a system. Weak environments, inconsistent checks, unclear roles, and informal release practices create openings long before runtime exploitation.

## Defender perspective

Defenders should use SSDF to:
- define secure development practices
- establish secure environments and responsibilities
- integrate checks into the workflow
- improve response and remediation discipline

## Practical examples

- secure code review exists, but release approval and artifact integrity are informal
- teams scan dependencies but lack a process for fixing or prioritizing findings
- developers harden code but the build environment is weakly controlled

## Related notes

- [[secure-by-design]]
- [[ci-cd-hardening]]
- [[supply-chain-security]]
- [[asvs-as-dev-process-input]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** NIST SSDF project page — https://csrc.nist.gov/Projects/ssdf
