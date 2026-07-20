---
kind: concept
level: beginner
status: current
perspective: purple
last_verified: 2026-07-19
---

# Security boundaries and trust assumptions

## Mental model

Security is a property of a system operating across boundaries, not a property
of a library or a scanner. An asset is valuable because a person or service can
change, read, spend, or depend on it. A boundary is crossed when the system
accepts a new identity, input, authority, execution context, or data store.

## System boundary

For a small service, draw browser, edge proxy, application, database, queue,
and administrator as separate actors. Mark what crosses each boundary: session
cookie, request body, tenant identifier, job payload, and privileged command.
Each arrow has a security assumption: the identity is authentic, the request
belongs to the claimed tenant, a proxy header is trustworthy, or a worker is
allowed to perform an action.

## Failure condition and controls

A failure occurs when an assumption is accepted without a check at the
boundary that must enforce it. For example, a handler that receives an object
identifier must prove both authentication and object-level authorization; an
ID format check does neither. Controls include explicit policy checks,
least-privilege service identities, schema validation, tamper-evident audit
events, and tested recovery paths.

## Evidence and residual risk

Record actor, action, target, authorization decision, policy version, request
correlation ID, and result. This lets an investigator distinguish a rejected
guess from an accepted cross-tenant action. Logs can be incomplete, identities
can be compromised, and policy can be wrong; those are residual risks to test,
not reasons to omit controls.

## Example

A report URL crosses a browser-to-application boundary. The server derives the
tenant from the verified session, checks that the report belongs to it, emits a
decision event, and returns a generic denial. A regression test must prove that
changing only the report ID cannot reveal a neighboring tenant's report.

## Sources

- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
