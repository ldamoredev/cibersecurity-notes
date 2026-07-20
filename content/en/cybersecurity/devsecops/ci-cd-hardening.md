---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# CI/CD Hardening

## Definition

CI/CD hardening ice of securing the build, test, and deployment pipeline so that automation becomes a trusted control path rather than an attack amplifier.

## Why it matters

Pipelines often hold code access, secrets, signing material, release privileges, and deployment automation. A weak CI/CD system can become the shortest path from source compromise to production compromise.
This note stays focused on pipeline execution and build environment trust; [[branch-protection-and-release-controls]] covers governance around code and promotion, while [[secrets-management]] focuses on sensitive material itself.

## Attacker perspective

Attackers target CI/CD to:
- steal secrets
- run malicious steps
- tamper with artifacts
- abuse overly broad automation privileges
- pivot from build environment into infrastructure

## Defender perspective

Defenders should:
- lock down pipeline permissions
- isolate build environments
- minimize secret exposure in jobs
- review who can modify workflows and release logic
- treat pipeline definitions as sensitive code

## Practical examples

- any contributor can modify workflow logic on a sensitive branch
- pipeline logs expose tokens or credentials
- build runners have broad network reach and persistent state

## Related notes

- [[secrets-management]]
- [[artifact-integrity]]
- [[branch-protection-and-release-controls]]
- [[nist-ssdf]]
- [[exposed-storage|Exposed Storage]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
