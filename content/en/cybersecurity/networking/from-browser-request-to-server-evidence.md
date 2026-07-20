---
kind: mechanism
level: intermediate
status: current
perspective: purple
last_verified: 2026-07-19
---

# From browser request to server evidence

## System model

A browser request is a chain: DNS resolution, TCP or QUIC, TLS, HTTP, reverse
proxy, application, database, and logging. Each hop has different identities,
timeouts, transformations, and evidence. Do not assume that a header observed
by the application was supplied by the browser or that an edge log proves a
database change.

## Trust boundaries and attack opportunities

DNS delegates names; TLS authenticates the selected endpoint; the proxy may add
or remove forwarding headers; the application authenticates a session and
authorizes an action; the database enforces its own credentials and policies.
Common failures are trusting client-supplied identity headers, forwarding an
ambiguous request, logging secrets, or authorizing an object only at the UI.

## Telemetry and detection

Preserve a correlation ID across edge, application, and audit logs. Capture
request method, route template, authenticated principal, tenant, policy result,
latency, status, and database error class—never raw credentials or sensitive
payloads by default. A detection may correlate repeated denied cross-tenant
object requests with one principal, then distinguish a legitimate broken client
from probing by volume, sequencing, and support context.

## Limits

Encrypted transport does not make authorization correct. Logs do not prove an
event if clocks drift, IDs are absent, or a component is bypassed. Test the
path with a local fixture and compare expected audit events to what arrives in
storage.

## Sources

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
