---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# OWASP Top 10

## Definition

The OWASP Top 10 is a high-level awareness document that summarizes the most important web application security risk categories. It is not a complete methodology, but it is one of the best starting maps for what repeatedly goes wrong in real applications.

## Why it matters

This note matters because it helps organize the web-security branch around root causes instead of random exploits. It gives you a vocabulary for common risk categories and a shared frame for discussing priorities, testing, and mitigation.

## Attacker perspective

Attackers do not care about the Top 10 as a checklist. They care about the underlying classes of weakness it names:
- broken access control
- injection
- insecure design
- identification and authentication failures
- security misconfiguration

The value of this note is not memorization. It is learning where entire families of exploitable mistakes come from.

## Defender perspective

Defenders should use the Top 10 as:
- a prioritization aid
- a communication tool with developers
- a bridge into deeper standards like WSTG and ASVS

It is useful for orientation, but not enough by itself to test or secure an application.

## Practical examples

- A team says “we don’t have SQL injection,” but still has broken access control and insecure design.
- A review names “XSS” as the problem, but the root cause is broader input/output handling and missing security controls.
- A roadmap uses Top 10 categories to decide which labs and playbooks to build first.

## Related notes

- [[broken-access-control]]
- [[auth-flaws]]
- [[sql-injection]]
- [[xss]]
- [[ssrf]]

## References

- **Foundational:** OWASP Top Ten Web Application Security Risks — https://owasp.org/www-project-top-ten/
- **Foundational:** OWASP Top 10 2021 Introduction — https://owasp.org/Top10/2021/A00_2021_Introduction/
- **Foundational:** OWASP Top 10 related cheat sheets — https://cheatsheetseries.owasp.org/IndexTopTen.html
