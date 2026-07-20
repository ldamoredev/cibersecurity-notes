---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Break JWT Validation

## Goal

Identify whether JWT handling is weak enough to allow acceptance of invalid, stale, mis-scoped, or attacker-influenced tokens.

## Assumptions

- the app uses JWTs for auth or session-like state
- validation logic may be inconsistent across services
- developers may confuse token presence with valid authorization

## Prerequisites

- sample tokens from authenticated flows
- ability to replay requests
- basic understanding of JWT structure

## Recon steps

1. Determine where tokens are issued and consumed.
2. Map claims that appear to influence authorization.
3. Identify whether multiple services validate the same token differently.

## Exploit / test steps

1. Replay expired or old tokens.
2. Remove or alter non-critical claims to observe validation strictness.
3. Test whether audience, issuer, or scope checks appear enforced.
4. Compare behavior across web, mobile, and API entry points.
5. Check whether logout or privilege changes actually revoke token usefulness.

## Validation clues

- expired tokens still work
- changed or missing claims are accepted
- different services accept different token states
- authorization decisions rely on weak or stale claims

## Mitigation

- validate signature, issuer, audience, expiry, and relevant claims consistently
- separate authentication from authorization checks
- minimize token lifetime and scope
- design explicit revocation strategies where needed

## Logging / detection

- repeated use of expired tokens
- token claim anomalies
- inconsistent auth decisions across services for same subject

## Related notes

- [[auth-flaws]]
- [[jwt-attacks|JWT Attacks]]
- [[token-lifecycle]]
- [[session-management]]

## References

- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Foundational:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
