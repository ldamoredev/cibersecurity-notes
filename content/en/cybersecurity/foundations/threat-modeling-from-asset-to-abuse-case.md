---
kind: mechanism
level: intermediate
status: current
perspective: purple
last_verified: 2026-07-19
---

# Threat modeling from asset to abuse case

## Scope and data flow

Start with a bounded feature, its assets, actors, data stores, and external
dependencies. Draw the data flow before naming attacks. Mark every place where
the feature accepts data or authority and every state transition it can cause.

## From threat to requirement

Use STRIDE as a question set: can an actor spoof identity, alter state, deny an
action, disclose data, exhaust capacity, or gain authority? Convert a plausible
answer into an abuse case with attacker prerequisite, intended state change,
impact, observable behavior, and a security requirement. Rank by contextual
impact and likelihood rather than by technique popularity.

## Local lab

For a local “share report” feature, define a fixture with two tenants and a
test account per tenant. The abuse case is “a signed-in user requests another
tenant's report by replacing an ID.” The requirement is a server-side
object-to-tenant check. Expected output is a generic denial and an audit event
containing the actor, requested object, decision, and correlation ID. Reset by
reloading the fixture; never point this exercise at a public service.

## Verification and limits

Unit-test policy decisions and run an integration test through the HTTP
boundary. Review whether administrators, exports, caches, asynchronous jobs,
and support tools enforce the same policy. A completed threat model is a
snapshot: architecture and dependencies change, so revisit it with the change.

## Sources

- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
- [Microsoft threat modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
