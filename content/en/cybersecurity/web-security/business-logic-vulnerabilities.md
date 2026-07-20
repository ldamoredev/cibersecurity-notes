---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Business Logic Vulnerabilities

## Definition

Business logic vulnerabilities are flaws in the intended workflow, assumptions, invariants, or rule design of an application, where the system behaves as coded but not as safely intended.

## Why it matters

Business logic bugs are among the most realistic and product-specific security failures. They do not depend on classic parser bugs. They depend on how the product actually works:
- sequence
- pricing
- approvals
- quotas
- coupons
- retries
- trust in client-enforced flow

They are often under-documented, under-scanned, and high impact.

## How it works

The mechanism is usually:
1. the product assumes a certain workflow, state, or invariant
2. the server does not enforce that assumption strongly enough
3. the attacker interacts with the workflow out of order, too often, or under unexpected conditions
4. the system produces a legitimate-but-unsafe result

## Techniques / patterns

Attackers usually test:
- step skipping
- repeated submission of one-time actions
- race conditions
- negative pricing / discount interactions
- state transitions out of order
- partial refund / coupon / credit abuse
- hidden assumptions enforced only by UI

## Variants and bypasses

### Workflow-order abuse

The attacker calls steps in an unintended order.

### One-time-use / replay abuse

A coupon, token, or action can be reused.

### State-transition abuse

The server allows transitions that should be impossible or role-limited.

### Pricing / accounting logic abuse

The issue is incorrect handling of values, combinations, or state.

### Race-condition logic abuse

Two valid operations can be combined concurrently to violate an invariant.

### UI-enforced rule misconception

The frontend prevents a path, but the backend never truly enforces it.

## Impact

Typical impact:
- financial abuse
- privilege or workflow escalation
- unauthorized state changes
- duplicate credits / rewards / usage
- fraud or resource consumption beyond intended limits

## Detection and defense

Ordered by effectiveness:

1.
**Model abuse cases, not only happy paths**
   Threat-model the workflow before coding it: what happens if the user calls step 3 before step 2, calls step 2 twice, or calls step 4 with stale state from step 1? Most business-logic bugs are missing rows in this matrix, not parser failures.

2.
**Enforce invariants server-side**
   Every invariant the product depends on — "a coupon is single-use," "a refund cannot exceed the original payment," "a user cannot be in two roles at once" — must be enforced at the server, in a single authoritative place, ideally inside a transaction. UI rules and client-side checks do not count.

3.
**Use database constraints and transactions for state-critical flows**
   Race conditions are the most exploited business-logic class. Use row-level locks, unique constraints, and conditional updates (`UPDATE ... WHERE status = 'pending'`) to make replay and concurrent-action abuse impossible at the data layer rather than only at the application layer.

4.
**Test workflows and state transitions intentionally**
   Build state-machine tests that drive the workflow from every reachable state through every transition, including invalid ones. Property-based and stateful tests catch the exact "out-of-order step" class that misses unit tests.

5.
**Audit high-value transitions**
   Money movement, role changes, ownership transfers, and irreversible operations need extra scrutiny — separate review, dual control, or a re-authentication step. The cost of a single business-logic bug here is much higher than at lower-value endpoints.

6.
**Instrument unusual workflow patterns**
   Log every state transition with caller, before/after state, and identifiers. Alert on patterns that should not happen: a single user redeeming the same coupon twice within seconds, a refund larger than the order total, a role change that bypasses the approval queue.

7.
**Do not trust UI constraints**
   The frontend disabling a button, hiding a field, or skipping a step is not a security control. Any control that matters must be enforced on the server independently of what the client did.

## Practical examples

- coupon can be reused because invalidation happens too late
- checkout allows manipulated price through step mismatch
- approval workflow can be triggered out of order
- reward action can be replayed concurrently for extra value

## Related notes

- [[broken-access-control]]
- [[broken-function-level-authorization]]
- [[api-rate-limiting]]

### Suggested future atomic notes

- workflow-invariant-design
- race-condition-business-logic
- state-machine-testing-for-security

## References

- **Foundational:** OWASP WSTG business logic testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/
- **Testing / Lab:** PortSwigger business logic vulnerabilities topic — https://portswigger.net/web-security/logic-flaws
- **Research / Deep Dive:** PortSwigger, "Smashing the state machine: the true potential of web race conditions" — https://portswigger.net/research/smashing-the-state-machine
