---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Insecure Direct Object Reference (IDOR)

## Definition

IDOR is a class of authorization failure where an attacker can access or act on an object by manipulating a direct reference such as an ID, filename, key, or path.

## Why it matters

IDOR is one of the highest-value bug classes in real applications because:
- object references are everywhere
- the exploitation path is often simple
- the impact is usually real unauthorized access, not just theoretical weirdness

It is best understood as the classic web/appsec framing of object-level authorization failure.

This note should stay distinct from API-side [[broken-object-level-authorization]], even though they are closely related.

## How it works

The mechanism is:

1. the application exposes a reference to an object
2. the server uses that reference to retrieve or modify the object
3. the server fails to verify that the current user is allowed to access that object

The vulnerability is not “the ID is guessable”.
The vulnerability is “authorization is not enforced correctly”.

Even UUIDs do not solve IDOR if ownership or access checks are missing.

## Techniques / patterns

Attackers usually test IDOR by modifying:

- numeric IDs in paths
- UUIDs in URLs or JSON
- filenames and document references
- download/export references
- hidden form values
- mobile-only or alternate frontend routes
- indirect references that still map predictably to real objects

Typical workflow:
- log in as user A
- capture a request to object A
- change only the object reference
- replay against object B
- observe read, write, or metadata differences

## Variants and bypasses

### Read IDOR

Unauthorized reading of another user’s object.

### Write IDOR

Unauthorized modification of another user’s object.

### Delete / destructive IDOR

Object-level access plus destructive action.

### Hidden-function IDOR overlap

Sometimes the issue is not just object access, but also calling a route the UI hides. That begins to overlap with [[broken-access-control]] or [[broken-function-level-authorization]].

### Multi-step workflow IDOR

The object reference is safe on one step but becomes exploitable later in the flow.

### Indirect reference misconceptions

Apps sometimes use:
- UUIDs
- opaque tokens
- base64-wrapped identifiers

These can still be exploitable if server-side authorization is weak.

## Impact

Impact is usually very direct:
- access another user’s data
- change another user’s settings
- download another user’s files
- escalate through access to privileged object state
- destroy or corrupt records

Impact becomes critical when the objects are:
- financial
- identity-related
- admin-facing
- bulk-accessible
- easy to enumerate

## Detection and defense

Ordered by effectiveness:

1.
**Server-side authorization on every object access**
   Always verify the caller’s right to that specific object.

2.
**Separate object retrieval from object authorization clearly**
   Do not assume “if the route is authenticated, the object is safe”.

3.
**Deny by default**
   Ownership or access must be proven, not assumed.

4.
**Log suspicious object access attempts**
   Especially access patterns across adjacent or unrelated objects.

5.
**Use indirect references only as secondary friction**
   They are not a primary authorization control.

6.
**Test both read and write paths**
   Many teams fix one and miss the other.

## Practical examples

- changing `/invoice/1001` to `/invoice/1002`
- swapping a document ID in a download request
- modifying a support ticket or account object not owned by the current user
- changing a hidden project/member/resource ID in a form or API call

## Related notes

- [[broken-access-control]]
- [[broken-object-level-authorization]]
- [[authorization]]
- [[exploit-idor|Exploit IDOR]]

### Suggested future atomic notes

- object-ownership-check-patterns
- indirect-reference-misconceptions

## References

- **Foundational:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Foundational:** OWASP Top 10 Broken Access Control — https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- **Testing / Lab:** PortSwigger IDOR topic — https://portswigger.net/web-security/access-control/idor
