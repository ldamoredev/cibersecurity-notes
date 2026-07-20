---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Authentication Flaws

## Definition

Authentication flaws are weaknesses in how an application verifies identity. They include weak login logic, user enumeration, broken MFA flows, password reset weaknesses, credential stuffing exposure, and flawed assumptions around session/token issuance.

## Why it matters

Authentication is the front door to the app. When it fails, attackers often gain access before needing anything more advanced. These flaws also expand the attack surface for privilege escalation and account takeover.

This note is about proving identity correctly. [[session-management]] covers what happens after login succeeds, and [[jwt-attacks|JWT Attacks]] covers token-specific failure modes rather than the broader auth flow.

## Attacker perspective

Attackers test:
- login error behavior
- brute-force protections
- MFA enforcement gaps
- password reset and recovery flows
- token issuance after partial validation
- user enumeration through timing or messages

## Defender perspective

Defenders should:
- make authentication flows explicit and testable
- limit brute-force and credential stuffing impact
- harden password reset and recovery
- treat MFA as a control with edge cases, not a magic layer
- avoid leaking account existence or auth state

## Practical examples

- The app reveals whether an email exists at login.
- Password reset tokens are weak or never expire.
- MFA is enforced in the UI but not on a direct API call.

## Related notes

- [[session-management]]
- [[jwt-attacks|JWT Attacks]]
- [[broken-access-control]]
- [[client-ip-trust]]
- [[cookies-and-sessions]]

## References

- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP WSTG authentication testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication
