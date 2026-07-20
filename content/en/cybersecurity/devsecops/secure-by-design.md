---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Secure by Design

## Definition

Secure by Design is the principle that software manufacturers and engineering teams should make security outcomes the default result of product design rather than shifting the burden to operators and end users.

## Why it matters

This note matters because DevSecOps can become too tool-centric. Secure by Design reframes the goal: reduce exploitable conditions before deployment by changing defaults, product architecture, and engineering incentives.
Keep the boundary clear: this is a product and engineering philosophy, not the process framework of [[nist-ssdf]] or the verification catalog role of [[asvs-as-dev-process-input]].

## Attacker perspective

Attackers benefit when products:
- ship insecure defaults
- require customers to harden everything manually
- expose dangerous functionality by default
- make risky configurations easy and safe ones hard

## Defender perspective

Defenders should use Secure by Design to:
- reduce exploitable exposure before runtime
- simplify secure defaults
- eliminate classes of mistakes at the product level
- shift security responsibility left onto the producer, not the customer alone

## Practical examples

- default admin interfaces remain enabled
- public storage or debug features are exposed by default
- product teams rely on docs telling customers to “configure securely later”

## Related notes

- [[nist-ssdf]]
- [[branch-protection-and-release-controls]]
- [[container-security]]
- [[exposed-storage|Exposed Storage]]

## References

- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
- **Foundational:** CISA principles and approaches PDF — https://www.cisa.gov/sites/default/files/2023-04/principles_approaches_for_security-by-design-default_508_0.pdf
