---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# SQL Injection

## Definition

SQL injection (SQLi) happens when user-controlled input is incorporated into a SQL query in a way that changes the query structure instead of remaining only as data.

## Why it matters

SQLi is one of the clearest and most important vulnerability classes because it teaches the core parser-boundary lesson that appears across security: once attacker input is interpreted as code or syntax instead of data, trust collapses.

It also remains highly practical. A single vulnerable query can lead to:
- authentication bypass
- unauthorized data access
- large-scale data extraction
- destructive modification
- sometimes file read, file write, or command execution depending on the DB engine and privileges

## How it works

The mechanism is simple:

1. attacker-controlled input reaches a query builder
2. the query is built unsafely through concatenation or interpolation
3. the database parses the final string as SQL syntax

Example:

```
const query = `SELECT * FROM users WHERE email = '${email}'`
```

If `email` is:

```
admin@example.com' OR 1=1 --
```

the effective query becomes:

```
SELECT * FROM users WHERE email = 'admin@example.com' OR 1=1 --'
```

Now the attacker has changed the logic of the query, not just its value.

### Context matters

The payload shape depends on where the injection lands:

- **String context**

`WHERE name = '<input>'`

- **Numeric context**

`WHERE id = <input>`

- **Identifier context**

`ORDER BY <input>`

- **LIKE context**

`WHERE name LIKE '%<input>%'`

- **Limit / offset / sort direction context**

  often poorly handled because teams assume these fields are “safe”

Understanding context is one of the highest-leverage SQLi skills.

## Techniques / patterns

Attackers usually test SQLi through:

- login forms
- search fields
- filters and report builders
- sort/order parameters
- export endpoints
- admin or “internal” features
- hidden parameters
- cookies or headers used by analytics/reporting code
- JSON body fields mapped into dynamic query builders

Common testing patterns:

- quote-breaking probes
- boolean-based probes
- error-based behavior
- time-based behavior
- union-based extraction
- second-order paths where stored attacker input is later used unsafely

## Variants and bypasses

### Error-based SQLi

The application returns DB errors or stack traces that reveal parser behavior.

Typical signs:
- syntax error near quote
- DB-specific error messages
- cast / type errors that leak query fragments

### UNION-based SQLi

Useful when attacker-controlled output is reflected in the response and the DB allows a compatible `UNION SELECT`.

Main tasks:
- determine column count
- determine compatible types
- find which columns are reflected

### Boolean-based blind SQLi

The response changes subtly based on whether a condition is true or false.

Example pattern:
- `AND 1=1`
- `AND 1=2`

This is slower than full reflection but common and practical.

### Time-based blind SQLi

Used when the app does not visibly reflect results but the DB can introduce measurable delays.

Example patterns differ by engine:
- MySQL: `SLEEP()`
- PostgreSQL: `pg_sleep()`
- MSSQL: `WAITFOR DELAY`

### Out-of-band SQLi

In some environments the DB can trigger DNS or network callbacks. This matters when traditional blind extraction is too slow.

### Filter bypasses

Naive defenses often fail because they rely on:
- keyword blocklists
- quote stripping
- superficial WAF patterns

Common bypass styles include:
- alternate comment styles
- case variation
- encoded payloads
- alternate operators
- exploiting DB-specific syntax quirks
- identifier-context injection where parameterization is not used

### DBMS differences

Payloads vary a lot across:
- MySQL
- PostgreSQL
- MSSQL
- Oracle
- SQLite

A good SQLi note should remind you to fingerprint the engine before assuming payload portability.

## Impact

Impact depends on:
- DB privileges
- environment
- network position
- what data the service account can access

Typical impact:
- read sensitive rows
- modify or delete records
- bypass login
- access internal metadata stored in DB
- pivot into file read/write or RCE on badly configured systems

A “blind” SQLi can still be critical if it runs under a highly privileged DB role.

## Detection and defense

Ordered by effectiveness:

1.
**Parameterized queries everywhere**
   This is the real fix. Query structure and values must be sent separately.

2.
**Allowlist for identifiers**
   For fields like `ORDER BY`, table names, or column names, use explicit allowlists because these usually cannot be parameterized like values.

3.
**Least privilege at the database layer**
   The app DB user should not have broad DDL, file, admin, or command-execution capability.

4.
**Constrain dangerous DB features**
   Disable or restrict features that amplify impact.

5.
**Validate shape at the application edge**
   Type, format, and domain validation reduce attack surface, but are not a substitute for parameterization.

6.
**Safe error handling**
   Do not leak DB errors to users.

7.
**Monitoring**
   Watch for:
   - repeated syntax-like probes
   - unusual query latency
   - spikes in error rates
   - anomalous DB behavior on low-risk endpoints

## Practical examples

- login form auth bypass via string-context injection
- reporting filter vulnerable through unsafely concatenated order field
- admin export endpoint vulnerable because “trusted user” assumptions replaced defensive coding
- search endpoint exploitable via blind SQLi in a JSON field processed by a dynamic query builder

## Related notes

- [[http-messages]]
- [[broken-access-control]]
- [[auth-flaws]]
- [[exploit-sqli|Exploit SQLi]]

### Suggested future atomic notes

- second-order-injection
- nosql-injection
- orm-injection-patterns

## References

- **Foundational:** OWASP Top 10 Injection — https://owasp.org/Top10/2021/A03_2021-Injection/
- **Foundational:** OWASP SQL Injection Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SQL injection topic — https://portswigger.net/web-security/sql-injection
- **Research / Deep Dive:** PortSwigger SQLi cheat sheet — https://portswigger.net/web-security/sql-injection/cheat-sheet
