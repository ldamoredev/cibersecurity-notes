# Reference Registry — Web Security

## Propósito

Esta nota es la semilla específica de web-security para el registro de referencias de ciberseguridad más amplio.

Usala para:
- estandarizar referencias para las notas de web-security
- mantener la calidad de fuentes consistente
- ayudar a asignar referencias sin inventar conjuntos de fuentes débiles
- facilitar la expansión de futuras notas de web-security

## Regla de fuente de verdad

Para las notas de web-security, este registro es la fuente de verdad primaria.

Usalo junto con:
- [[web-security/index|Índice de Seguridad Web]] para el orden de estudio y la estructura de la rama
- [[reference-registry|Registro de Referencias de Ciberseguridad]] como fallback más amplio cuando esta nota aún no cubre un tema de web-security

---

## Política de selección de referencias

### Prioridad de fuente

1. documentación oficial y estándares
2. labs oficiales y entrenamiento práctico
3. guías de testing y cheat sheets
4. investigación de alta señal
5. fuentes secundarias solo cuando agregan valor claro

### Objetivo por nota

- mínimo 2 referencias
- ideal 3 referencias
- evitar inflar las notas con listas largas

### Etiquetado

Usar:
- **Fundamental:**
- **Testing / Lab:**
- **Investigación / Deep Dive:**
- **Docs Oficiales:**

---

# Mapa de temas de web-security

## owasp-top-10

Referencias preferidas:
- **Fundamental:** OWASP Top Ten Web Application Security Risks — https://owasp.org/www-project-top-ten/
- **Fundamental:** OWASP Top 10 2021 Introduction — https://owasp.org/Top10/2021/A00_2021_Introduction/
- **Fundamental:** OWASP Top 10 related cheat sheets — https://cheatsheetseries.owasp.org/IndexTopTen.html
- **Testing / Lab:** OWASP Web Security Testing Guide project — https://owasp.org/www-project-web-security-testing-guide/

## broken-access-control

Referencias preferidas:
- **Fundamental:** OWASP Top 10 Broken Access Control — https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
- **Fundamental:** OWASP WSTG authorization testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger access control topic — https://portswigger.net/web-security/access-control

## auth-flaws

Referencias preferidas:
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP WSTG authentication testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication

## session-management

Referencias preferidas:
- **Fundamental:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Fundamental:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Fundamental:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie

## mfa-phishing-resistance

Referencias preferidas:
- **Fundamental:** NIST SP 800-63B Authentication and Lifecycle Management — https://pages.nist.gov/800-63-4/sp800-63b.html
- **Mitigación:** CISA More than a Password / MFA — https://www.cisa.gov/mfa
- **Fundamental:** FIDO Alliance Passkeys — https://fidoalliance.org/passkeys/

## evilginx-and-reverse-proxy-phishing

Referencias preferidas:
- **Investigación / Deep Dive:** Microsoft, Identifying Adversary-in-the-Middle phishing attacks through third-party network detection — https://techcommunity.microsoft.com/blog/microsoftsentinelblog/identifying-adversary-in-the-middle-aitm-phishing-attacks-through-3rd-party-netw/3991358
- **Mitigación:** CISA More than a Password / MFA — https://www.cisa.gov/mfa
- **Fundamental:** FIDO Alliance Passkeys — https://fidoalliance.org/passkeys/

## bot-detection-signals

Referencias preferidas:
- **Fundamental:** OWASP Automated Threats to Web Applications — https://owasp.org/www-project-automated-threats-to-web-applications/
- **Mitigación:** OWASP Credential Stuffing Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html
- **Fundamental:** Cloudflare Learning Center: What is bot management? — https://www.cloudflare.com/learning/bots/what-is-bot-management/

## sql-injection

Referencias preferidas:
- **Fundamental:** OWASP Top 10 Injection — https://owasp.org/Top10/2021/A03_2021-Injection/
- **Fundamental:** OWASP SQL Injection Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SQL injection topic — https://portswigger.net/web-security/sql-injection
- **Testing / Lab:** PortSwigger SQL injection cheat sheet — https://portswigger.net/web-security/sql-injection/cheat-sheet

## xss

Referencias preferidas:
- **Fundamental:** OWASP WSTG client-side testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Fundamental:** OWASP Cross Site Scripting Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Cross-site scripting topic — https://portswigger.net/web-security/cross-site-scripting
- **Testing / Lab:** PortSwigger XSS cheat sheet — https://portswigger.net/web-security/cross-site-scripting/cheat-sheet

## csrf

Referencias preferidas:
- **Fundamental:** OWASP Cross-Site Request Forgery Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- **Fundamental:** OWASP WSTG authentication/session testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf

## path-traversal

Referencias preferidas:
- **Fundamental:** OWASP WSTG configuration and deployment testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger Path traversal topic — https://portswigger.net/web-security/file-path-traversal
- **Investigación / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability

## ssrf

Referencias preferidas:
- **Fundamental:** OWASP Cheat Sheet Series SSRF prevention — https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger SSRF topic — https://portswigger.net/web-security/ssrf

## request-smuggling

Referencias preferidas:
- **Fundamental:** OWASP WSTG web application testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger request smuggling topic — https://portswigger.net/web-security/request-smuggling
- **Investigación / Deep Dive:** PortSwigger research archive — https://portswigger.net/research
- **Investigación / Deep Dive:** James Kettle, "HTTP/2: The Sequel is Always Worse" — https://portswigger.net/research/http2

## business-logic-vulnerabilities

Referencias preferidas:
- **Fundamental:** OWASP WSTG business logic testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Fundamental:** OWASP WSTG business logic testing chapter — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/10-Business_Logic_Testing/
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Testing / Lab:** PortSwigger business logic vulnerabilities topic — https://portswigger.net/web-security/logic-flaws
- **Investigación / Deep Dive:** PortSwigger, "Smashing the state machine" — https://portswigger.net/research/smashing-the-state-machine

## cors-misconfiguration

Referencias preferidas:
- **Fundamental:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Investigación / Deep Dive:** PortSwigger CORS misconfiguration research — https://portswigger.net/research/exploiting-cors-misconfigurations-for-bitcoins-and-bounties

## file-upload-abuse

Referencias preferidas:
- **Fundamental:** OWASP WSTG configuration and deployment testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger file upload vulnerabilities — https://portswigger.net/web-security/file-upload
- **Fundamental:** OWASP File Upload Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- **Investigación / Deep Dive:** Snyk Zip Slip research — https://security.snyk.io/research/zip-slip-vulnerability

## deserialization

Referencias preferidas:
- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Insecure deserialization topic — https://portswigger.net/web-security/deserialization
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (PHAR deserialization, Black Hat USA 2018) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf

## gadget-chains

Referencias preferidas:
- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Chris Frohoff & Gabriel Lawrence, "Marshalling Pickles" (AppSecCali 2015, original ysoserial talk) — https://frohoff.github.io/appseccali-marshalling-pickles/
- **Docs Oficiales:** ysoserial — https://github.com/frohoff/ysoserial
- **Docs Oficiales:** PHPGGC — https://github.com/ambionics/phpggc

## phar-deserialization

Referencias preferidas:
- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Sam Thomas, "It's a PHP unserialization vulnerability Jim, but not as we know it" (Black Hat USA 2018) — https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
- **Docs Oficiales:** PHPGGC `--phar` mode — https://github.com/ambionics/phpggc#phar-archives

## command-injection

Referencias preferidas:
- **Fundamental:** OWASP OS Command Injection Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OS command injection — https://portswigger.net/web-security/os-command-injection
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## xxe

Referencias preferidas:
- **Fundamental:** OWASP XML External Entity Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger XXE — https://portswigger.net/web-security/xxe
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## open-redirect

Referencias preferidas:
- **Fundamental:** OWASP Unvalidated Redirects and Forwards Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/

## content-security-policy

Referencias preferidas:
- **Fundamental:** MDN Content Security Policy — https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- **Testing / Lab:** PortSwigger CSP — https://portswigger.net/web-security/cross-site-scripting/content-security-policy
- **Fundamental:** OWASP Content Security Policy Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html

## clickjacking

Referencias preferidas:
- **Fundamental:** MDN CSP `frame-ancestors` — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/frame-ancestors
- **Fundamental:** OWASP Clickjacking Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Clickjacking — https://portswigger.net/web-security/clickjacking

## oauth-security

Referencias preferidas:
- **Fundamental:** RFC 9700 OAuth 2.0 Security Best Current Practice — https://datatracker.ietf.org/doc/html/rfc9700
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

---

## Reglas de uso del registro

- elegir el conjunto más pequeño de referencias más fuertes para cada nota exacta
- no asignar links genéricos a ciegas
- preferir documentación oficial y labs sólidos
- si una futura nota de web-security no está en este registro, mapearla al tema padre más cercano primero
