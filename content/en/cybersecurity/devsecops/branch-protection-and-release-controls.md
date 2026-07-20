---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Branch Protection and Release Controls

## Definition

Branch protection and release controls are the rules and governance mechanisms that determine who can change protected code paths, approve releases, and promote artifacts toward production.

## Why it matters

A secure build pipeline can still be undermined if the code and release gates feeding it are weak. This topic connects code review, approval, separation of duties, and release discipline.
Keep it separate from [[ci-cd-hardening]]: this note is about who can change or promote sensitive code paths, not the security posture of the automation environment itself.

## Attacker perspective

Attackers look for:
- direct pushes to protected branches
- bypassable review gates
- weak release approvals
- overbroad maintainer rights
- manual shortcuts around formal release flow

## Defender perspective

Defenders should:
- protect sensitive branches and release tags
- require appropriate review and status checks
- restrict bypass powers
- define who can approve, build, and promote

## Practical examples

- admins can merge without checks and do so routinely
- release tags are mutable or loosely controlled
- production promotion relies on an undocumented manual shortcut

## Related notes

- [[ci-cd-hardening]]
- [[artifact-integrity]]
- [[secure-by-design]]
- [[supply-chain-security]]

## References

- **Foundational:** NIST SP 800-218 SSDF — https://csrc.nist.gov/pubs/sp/800/218/final
- **Foundational:** CISA Secure by Design — https://www.cisa.gov/resources-tools/resources/secure-by-design
