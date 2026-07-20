---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Container Security

## Definition

Container security is the practice of reducing risk in how containerized applications are built, configured, shipped, and run.

## Why it matters

Containers make delivery easier, but they also package software, dependencies, configuration, and privilege assumptions into a highly portable unit. Weak base images, broad privileges, and poor defaults can scale insecure patterns quickly.
Container security is broader than [[image-scanning]]: scanning is one useful control, but the full topic includes base image trust, privilege design, build context, runtime posture, and promotion discipline.

## Attacker perspective

Attackers look for:
- overly privileged containers
- weak or bloated base images
- secrets baked into images
- exposed admin/debug tooling
- drift between what the image contains and what teams think it contains

## Defender perspective

Defenders should:
- reduce image complexity
- control privileges and capabilities carefully
- keep build context and image contents intentional
- separate build hygiene from runtime assumptions
- review how images are sourced and promoted

## Practical examples

- a container runs as root unnecessarily
- debug tools and credentials are baked into production images
- teams inherit a base image without understanding its maintenance state

## Related notes

- [[image-scanning]]
- [[supply-chain-security]]
- [[artifact-integrity]]
- [[exposed-storage|Exposed Storage]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
