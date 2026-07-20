---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# API Security Index

## Purpose

This index is the root entry point for the API-security branch of the cybersecurity atlas.

Use it to:
- navigate the API-security notes
- understand the order of study
- connect web-security concepts to API-specific risk models
- strengthen backend security intuition with object-, function-, and property-level authorization thinking

Use [[reference-registry-api-security|Reference Registry — API Security]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[http-overview|HTTP overview]], [[http-headers|HTTP headers]], [[tls-https|TLS/HTTPS]].
> - [[index|Web Security]] — APIs inherit most of the web threat model, plus their own.

---

## Recommended learning order

### Phase 1 — API security foundations

1. [[api-security-top-10]]
2. [[authorization]]
3. [[broken-object-level-authorization]]
4. [[broken-object-property-level-authorization]]
5. [[broken-function-level-authorization]]

### Phase 2 — Authentication and token trust

1. [[broken-authentication]]
2. [[api-auth-flaws]]
3. [[jwt-attacks]]
4. [[token-lifecycle]]

### Phase 3 — Data and object/property exposure

1. [[mass-assignment]]
2. [[excessive-data-exposure]]

### Phase 4 — Operational API abuse

1. [[api-rate-limiting]]
2. [[api-inventory-management]]

### Phase 5 — Parser and binding risks

1. [[polymorphic-deserialization]]

---

## Core API-security cluster

### Foundations

- [[api-security-top-10]]
- [[authorization]]
- [[broken-object-level-authorization]]
- [[broken-object-property-level-authorization]]
- [[broken-function-level-authorization]]

### Authentication and token handling

- [[broken-authentication]]
- [[api-auth-flaws]]
- [[jwt-attacks]]
- [[token-lifecycle]]

### Data and object/property control

- [[mass-assignment]]
- [[excessive-data-exposure]]

### Operational resilience

- [[api-rate-limiting]]
- [[api-inventory-management]]

### Parser and binding risks

- [[polymorphic-deserialization]]

---

## Branch maintenance notes

- Atomic notes in this branch should follow the internal 11-section atomic-note template.
- Prefer count-based framing hooks in `How it works` or `Variants and bypasses`.
- Use [[reference-registry-api-security]] before adding or changing references.
- Preserve the split between object authorization ([[broken-object-level-authorization]]), property authorization ([[broken-object-property-level-authorization]]), function authorization ([[broken-function-level-authorization]]), and broad policy framing ([[authorization]]).
- Practical labs should use owned APIs, local labs, or intentionally vulnerable training targets.

---

## Cross-links to other branches

### Networking

- [[http-overview]]
- [[http-messages]]
- [[http-headers]]
- [[reverse-proxies]]
- [[client-ip-trust]]
- [[caching-and-security]]

### Web security

- [[broken-access-control]]
- [[auth-flaws]]
- [[session-management]]
- [[idor]]
- [[cors-misconfiguration]]
- [[ssrf]]

### Security playbooks

- [[exploit-idor]]
- [[break-jwt-validation]]
- [[test-client-ip-spoofing]]
- [[inspect-session-handling]]

---

## Suggested future notes

- server-side-parameter-pollution
- graphql-security
- api-versioning-risk
- webhook-security
- pagination-and-enumeration
- schema-exposure
- machine-to-machine-auth

### Possible future playbooks

- test-rate-limit-bypass
- inspect-api-version-drift
- test-mass-assignment
- test-excessive-data-exposure

## References

- **Foundational:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x00-header/
- **Foundational:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
