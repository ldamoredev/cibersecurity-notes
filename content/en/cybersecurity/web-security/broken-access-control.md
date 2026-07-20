---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Broken Access Control

## Definition

Broken access control happens when an application fails to enforce what a caller is allowed to access or do.

## Why it matters

This is one of the highest-impact classes in real applications because it often leads directly to:
- unauthorized data access
- unauthorized actions
- privilege escalation
- workflow abuse
- admin/control-plane exposure

It is broader than any one subtype. It is the umbrella risk area that includes:
- object-level failures
- function-level failures
- property-level failures
- hidden-function exposure
- weak tenant or ownership enforcement

## How it works

The mechanism is:
1. the application authenticates a caller
2. the system exposes data or functionality
3. the server fails to verify whether that caller is allowed to access that resource or action in that context

The important distinction is:
- authentication answers who are you
- authorization answers what can you do / access

## Techniques / patterns

Attackers usually test by changing:
- object identifiers
- routes and route families
- methods
- hidden parameters
- roles and scopes
- workflow stage / state
- client-specific surfaces
- field-level values that should not be writable

## Variants and bypasses

### Object-level authorization failure

Related notes: [[idor]], [[broken-object-level-authorization]]

### Function-level authorization failure

Related notes: [[broken-function-level-authorization]]

### Property-level authorization failure

Related notes: [[broken-object-property-level-authorization]], [[mass-assignment]], [[excessive-data-exposure]]

### Hidden UI failure

The frontend hides capability, but the backend accepts it.

### Cross-version or cross-client drift

One client or version enforces access correctly, another does not.

### Tenant / ownership boundary failure

The system trusts references or state without properly enforcing ownership or tenant separation.

## Impact

Typical impact:
- reading another user’s data
- modifying another user’s resources
- invoking admin or staff-only actions
- changing protected workflow state
- multi-tenant boundary collapse
- privilege escalation

## Detection and defense

Ordered by effectiveness:

1. **Treat authorization as a first-class server-side system**
2. **Enforce authorization on every access path**
3. **Separate object, function, and property checks**
4. **Deny by default**
5. **Test multiple identities and roles**
6. **Log denied and suspicious access attempts**
7. **Review drift across versions and clients**

## Practical examples

- normal user reads another user’s invoice
- mobile endpoint allows access control bypass not present in the web UI
- admin action is callable directly
- writable JSON field lets user escalate ownership or role
- legacy route preserves weaker authorization rules

## Related notes

- [[idor]]
- [[authorization]]
- [[broken-function-level-authorization]]
- [[exploit-idor|Exploit IDOR]]

### Suggested future atomic notes

- tenant-boundary-failures
- authorization-drift-across-clients

## References

- **Foundational:** OWASP Top 10 Broken Access Control — https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- **Foundational:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger access control topic — https://portswigger.net/web-security/access-control
