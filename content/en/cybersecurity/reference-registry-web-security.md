---
migration_source: published-html-snapshot
migration_status: needs-editorial-review
---

# Reference Registry — Web Security

## Purpose

This note is the web-security-specific seed for the broader cybersecurity reference registry.

Use it to:
- standardize references for web-security notes
- keep source quality consistent
- help Codex assign references without inventing weak source sets
- make future web-security notes easier to expand

## Source of truth rule

For web-security notes, this registry is the primary source of truth.

Use it together with:
- `<a href="web-security/index.html">Web Security Index</a>` for study order and branch structure
- `<a href="reference-registry.html">Cybersecurity Reference Registry</a>` for broader fallback only when this note does not yet cover a web-security topic

---

## Reference selection policy

### Source priority

1. official documentation and standards
2. official labs and practical training
3. testing guides and cheat sheets
4. high-signal research
5. secondary sources only when they add clear value

### Per-note target

- minimum 2 references
- ideal 3 references
- avoid bloating notes with long lists

### Labeling

Use:
- **Foundational**
- **Testing / Lab**
- **Research / Deep Dive**
- **Official Tool Docs**

---

# Web-security topic map

## owasp-top-10

Preferred references:
- **Foundational:** OWASP Top Ten Web Application Security Risks — https://owasp.org/www-project-top-ten/
- **Foundational:** OWASP Top 10 2021 Introduction — https://owasp.org/Top10/2021/A00_2021_Introduction/
- **Foundational:** OWASP Top 10 related cheat sheets — https://cheatsheetseries.owasp.org/IndexTopTen.html
- **Testing / Lab:** OWASP Web Security Testing Guide project — https://owasp.org/www-project-web-security-testing-guide/

## broken-access-control

Preferred references:
- **Foundational:** OWASP Top 10 Broken Access Control — https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- **Foundational:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger access control topic — https://portswigger.net/web-security/access-control

## auth-flaws

Preferred references:
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP WSTG authentication testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication

## session-management

Preferred references:
- **Foundational:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie

## mfa-phishing-resistance

Preferred references:
- **Foundational:** NIST SP 800-63B Authentication and Lifecycle Management — https://pages.nist.gov/800-63-4/sp800-63b.html
- **Mitigation:** CISA More than a Password / MFA — https://www.cisa.gov/mfa
- **Foundational:** FIDO Alliance Passkeys — https://fidoalliance.org/passkeys/

## evilginx-and-reverse-proxy-phishing

Preferred references:
- **Research / Deep Dive:** Microsoft, Identifying Adversary-in-the-Middle phishing attacks through third-party network detection — https://techcommunity.microsoft.com/blog/microsoftsentinelblog/identifying-adversary-in-the-middle-aitm-phishing-attacks-through-3rd-party-netw/3991358
- **Mitigation:** CISA More than a Password / MFA — https://www.cisa.gov/mfa
- **Foundational:** FIDO Alliance Passkeys — https://fidoalliance.org/passkeys/

## bot-detection-signals

Preferred references:
- **Foundational:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Mitigation:** OWASP Credential Stuffing Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html
- **Foundational:** Cloudflare Learning Center: What is bot management? — https://www.cloudflare.com/learning/bots/what-is-bot-management/

## sql-injection

Preferred references:
- **Foundational:** OWASP Top 10 Injection — https://owasp.org/Top10/2021/A03_2021-Injection/
- **Foundational:** OWASP SQL Injection Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SQL injection topic — https://portswigger.net/web-security/sql-injection
- **Testing / Lab:** PortSwigger SQL injection cheat sheet — https://portswigger.net/web-security/sql-injection/cheat-sheet

## xss

Preferred references:
- **Foundational:** OWASP WSTG client-side testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Foundational:** OWASP Cross Site Scripting Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Cross-site scripting topic — https://portswigger.net/web-security/cross-site-scripting
- **Testing / Lab:** PortSwigger XSS cheat sheet — https://portswigger.net/web-security/cross-site-scripting/cheat-sheet

## csrf

Preferred references:
- **Foundational:** OWASP Cross-Site Request Forgery Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- **Foundational:** OWASP WSTG authentication/session testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf

## path-traversal

Preferred references:
- **Foundational:** OWASP WSTG configuration and deployment testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger Path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Research / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability

## ssrf

Preferred references:
- **Foundational:** OWASP Cheat Sheet Series SSRF prevention — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf

## request-smuggling

Preferred references:
- **Foundational:** OWASP WSTG web application testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** PortSwigger research archive — https://portswigger.net/research
- **Research / Deep Dive:** James Kettle, "HTTP/2: The Sequel is Always Worse" — https://portswigger.net/research/http2

## business-logic-vulnerabilities

Preferred references:
- **Foundational:** OWASP WSTG business logic testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Foundational:** OWASP WSTG business logic testing chapter — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Testing / Lab:** PortSwigger business logic vulnerabilities topic — https://portswigger.net/web-security/logic-flaws
- **Research / Deep Dive:** PortSwigger, "Smashing the state machine" — https://portswigger.net/research/smashing-the-state-machine

## cors-misconfiguration

Preferred references:
- **Foundational:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Research / Deep Dive:** PortSwigger CORS misconfiguration research — https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties

## file-upload-abuse

Preferred references:
- **Foundational:** OWASP WSTG configuration and deployment testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Foundational:** OWASP File Upload Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- **Research / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability

## deserialization

Preferred references:
- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Insecure deserialization topic — https://portswigger.net/web-security/deserialization
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (PHAR deserialization, Black Hat USA 2018) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf

## gadget-chains

Preferred references:
- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Chris Frohoff & Gabriel Lawrence, "Marshalling Pickles" (AppSecCali 2015, original ysoserial talk) — https://frohoff.github.io/appseccali-marshalling-pickles/
- **Official Tool Docs:** ysoserial — https://github.com/frohoff/ysoserial
- **Official Tool Docs:** PHPGGC — https://github.com/ambionics/phpggc

## phar-deserialization

Preferred references:
- **Foundational:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Research / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (Black Hat USA 2018) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
- **Official Tool Docs:** PHPGGC `--phar` mode — https://github.com/ambionics/phpggc#phar-archives

## command-injection

Preferred references:
- **Foundational:** OWASP OS Command Injection Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OS command injection — https://portswigger.net/web-security/os-command-injection
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## xxe

Preferred references:
- **Foundational:** OWASP XML External Entity Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger XXE — https://portswigger.net/web-security/xxe
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## open-redirect

Preferred references:
- **Foundational:** OWASP Unvalidated Redirects and Forwards Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Foundational:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## content-security-policy

Preferred references:
- **Foundational:** MDN Content Security Policy — https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- **Testing / Lab:** PortSwigger CSP — https://portswigger.net/web-security/cross-site-scripting/content-security-policy
- **Foundational:** OWASP Content Security Policy Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html

## clickjacking

Preferred references:
- **Foundational:** MDN CSP `frame-ancestors` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
- **Foundational:** OWASP Clickjacking Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Clickjacking — https://portswigger.net/web-security/clickjacking

## oauth-security

Preferred references:
- **Foundational:** RFC 9700 OAuth 2.0 Security Best Current Practice — https://datatracker.ietf.org/doc/html/rfc9700
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

---

## Registry usage rules

- choose the smallest set of strongest references for each exact note
- do not assign generic links blindly
- prefer official documentation and strong labs
- if a future web-security note is missing from this registry, map it to the closest parent topic first
