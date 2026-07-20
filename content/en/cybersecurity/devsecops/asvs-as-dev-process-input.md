---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# ASVS as Dev Process Input

## Definition

This note treats OWASP ASVS not as a post-hoc checklist, but as a development-process input for designing, reviewing, and verifying technical security controls during implementation.

## Why it matters

DevSecOps needs requirements, not just scanners. ASVS gives a structured set of verification requirements that teams can use to shape architecture, backlog items, review criteria, and release readiness.
This note is about turning verification requirements into engineering inputs. It is narrower than [[nist-ssdf]] and less philosophical than [[secure-by-design]].

## Attacker perspective

Attackers exploit the gap between “we run tools” and “we built the right controls”. If teams lack explicit verification requirements, vulnerabilities survive because nobody was concretely accountable for the control.

## Defender perspective

Defenders can use ASVS to:
- define security expectations by control area
- connect requirements to implementation tasks
- improve review rigor
- avoid relying only on ad hoc tests or tooling

## Practical examples

- a team has SAST and dependency scans but no explicit verification requirement for access control or session handling
- security review becomes more consistent once ASVS sections are mapped into stories and release gates

## Related notes

- [[nist-ssdf]]
- [[secure-by-design]]
- [[ci-cd-hardening]]
- [[broken-access-control|Broken Access Control]]

## References

- **Foundational:** OWASP ASVS — https://owasp.org/www-project-application-security-verification-standard/
- **Foundational:** OWASP ASVS Cheat Sheet Index — https://cheatsheetseries.owasp.org/IndexASVS.html
