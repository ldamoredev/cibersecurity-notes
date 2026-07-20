---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Web Security Index

## Purpose

This index is the root entry point for the web-security branch of the cybersecurity atlas.

Use it to:
- navigate the web-security notes
- understand the order of study
- connect networking concepts to application-layer vulnerabilities
- expand into API security, attack surface mapping, and playbooks

Use [[reference-registry-web-security|Reference Registry — Web Security]] as the source of truth for references in this branch.
Return to [[index|Cybersecurity Index]] for root navigation across branches.

> *Before this branch:*
> - [[index|Foundations]] (Phase 0).
> - [[tcp-ip-basics|TCP/IP basics]], [[http-overview|HTTP overview]], [[http-headers|HTTP headers]], [[cookies-and-sessions|Cookies and sessions]], [[tls-https|TLS/HTTPS]].

---

## Recommended learning order

### Phase 1 — Core mental models

1. [[owasp-top-10]]
2. [[broken-access-control]]
3. [[idor]]
4. [[auth-flaws]]
5. [[mfa-phishing-resistance]]
6. [[session-management]]

### Phase 2 — Input and client-side attacks

1. [[sql-injection]]
2. [[xss]]
3. [[csrf]]
4. [[path-traversal]]
5. [[command-injection]]
6. [[xxe]]

### Phase 3 — Server-side and proxy-aware attacks

1. [[ssrf]]
2. [[request-smuggling]]
3. [[evilginx-and-reverse-proxy-phishing]]
4. [[business-logic-vulnerabilities]]
5. [[open-redirect]]
6. [[oauth-security]]

### Phase 4 — Supporting context

1. [[cors-misconfiguration]]
2. [[file-upload-abuse]]
3. [[deserialization]]
4. [[content-security-policy]]
5. [[clickjacking]]
6. [[bot-detection-signals]]

---

## Core web-security cluster

### Foundations

- [[owasp-top-10]]
- [[broken-access-control]]
- [[idor]]
- [[auth-flaws]]
- [[mfa-phishing-resistance]]
- [[session-management]]

### Input and client-side exploitation

- [[sql-injection]]
- [[xss]]
- [[csrf]]
- [[path-traversal]]
- [[command-injection]]
- [[xxe]]
- [[open-redirect]]

### Server-side exploitation

- [[ssrf]]
- [[request-smuggling]]
- [[evilginx-and-reverse-proxy-phishing]]
- [[business-logic-vulnerabilities]]
- [[file-upload-abuse]]
- [[deserialization]]
- [[gadget-chains]]
- [[phar-deserialization]]
- [[oauth-security]]

### Browser and policy behavior

- [[cors-misconfiguration]]
- [[content-security-policy]]
- [[clickjacking]]
- [[bot-detection-signals]]

---

## Cross-links to networking

- [[http-overview]] → request/response model for all web exploits
- [[http-messages]] → raw shape of requests, headers, bodies
- [[http-headers]] → cookies, CSP, CORS, forwarding, caching
- [[cookies-and-sessions]] → state and session behavior
- [[reverse-proxies]] → trust boundaries and request parsing
- [[client-ip-trust]] → header-based trust abuse
- [[tls-https]] → transport and cookie security
- [[metadata-endpoints]] → SSRF impact amplification

---

## Suggested future notes

### Next atomic notes

- secure-headers
- html-injection
- http-trace-method
- hidden-parameters
- bug-bounty-reporting

### Connected playbooks

- [[exploit-idor]]
- [[exploit-sqli]]
- [[investigate-ssrf]]
- [[inspect-session-handling]]
- [[reverse-proxy-misconfig-checklist]]
- [[test-cors-behavior]]

---

## References

- **Foundational:** OWASP Top 10 — https://owasp.org/www-project-top-ten/
- **Foundational:** OWASP WSTG Latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
