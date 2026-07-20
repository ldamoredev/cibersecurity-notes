---
kind: mechanism
level: intermediate
status: current
perspective: purple
last_verified: 2026-07-19
---

# Authentication, authorization and object access

## System model

Authentication establishes a principal. Session management maintains that
association across requests. Authorization decides whether that principal may
perform an action on a resource in the current tenant and state. These are
separate controls: a valid session is not authority to access every object.

## Failure condition

Broken object-level authorization occurs when a server uses an object identifier
from the request without binding it to a policy decision. Predictable IDs are
not the root cause; opaque IDs can reduce discovery but cannot replace an
authorization check.

## Evidence, detection, and fix

Emit an authorization decision event with principal, tenant, object class,
decision, policy version, and correlation ID. A local detection can flag a
single principal making repeated denied requests for unrelated object IDs, but
it must tolerate retries and stale links. Fix the query or policy so object and
tenant constraints are enforced server-side. Add a regression test: a signed-in
fixture user from tenant A receives no data when requesting tenant B's object.

## Residual risk

Administrators, background jobs, caches, exports, and support tools may follow
different paths. Test them separately and retain a reviewable policy boundary.

## Sources

- [OWASP API Security: Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)
- [OWASP ASVS access control requirements](https://owasp.org/www-project-application-security-verification-standard/)
