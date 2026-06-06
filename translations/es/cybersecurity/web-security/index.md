# Índice de Seguridad Web

## Propósito

Este índice es el punto de entrada raíz para la rama web-security del vault de ciberseguridad.

Usalo para:
- navegar las notas de web-security
- entender el orden de estudio
- conectar los conceptos de redes con las vulnerabilidades a nivel de aplicación
- expandirte hacia API security, mapeo de superficie de ataque y playbooks

Usá [[reference-registry-web-security|Reference Registry — Web Security]] como fuente de verdad para las referencias de esta rama.
Volvé a [[index|Índice de Ciberseguridad]] para la navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Foundations]] (Fase 0).
> - [[tcp-ip-basics|Bases de TCP/IP]], [[http-overview|Visión general de HTTP]], [[http-headers|HTTP headers]], [[cookies-and-sessions|Cookies y sesiones]], [[tls-https|TLS/HTTPS]].

---

## Orden de estudio recomendado

### Fase 1 — Modelos mentales fundamentales

1. [[owasp-top-10]]
2. [[broken-access-control]]
3. [[idor]]
4. [[auth-flaws]]
5. [[mfa-phishing-resistance]]
6. [[session-management]]

### Fase 2 — Ataques de input y del lado del cliente

1. [[sql-injection]]
2. [[xss]]
3. [[csrf]]
4. [[path-traversal]]
5. [[command-injection]]
6. [[xxe]]

### Fase 3 — Ataques del lado del servidor y con proxies

1. [[ssrf]]
2. [[request-smuggling]]
3. [[evilginx-and-reverse-proxy-phishing]]
4. [[business-logic-vulnerabilities]]
5. [[open-redirect]]
6. [[oauth-security]]

### Fase 4 — Contexto de soporte

1. [[cors-misconfiguration]]
2. [[file-upload-abuse]]
3. [[deserialization]]
4. [[content-security-policy]]
5. [[clickjacking]]
6. [[bot-detection-signals]]

---

## Cluster central de web-security

### Fundamentos

- [[owasp-top-10]]
- [[broken-access-control]]
- [[idor]]
- [[auth-flaws]]
- [[mfa-phishing-resistance]]
- [[session-management]]

### Explotación de input y del lado del cliente

- [[sql-injection]]
- [[xss]]
- [[csrf]]
- [[path-traversal]]
- [[command-injection]]
- [[xxe]]
- [[open-redirect]]

### Explotación del lado del servidor

- [[ssrf]]
- [[request-smuggling]]
- [[evilginx-and-reverse-proxy-phishing]]
- [[business-logic-vulnerabilities]]
- [[file-upload-abuse]]
- [[deserialization]]
- [[gadget-chains]]
- [[phar-deserialization]]
- [[oauth-security]]

### Comportamiento del navegador y políticas

- [[cors-misconfiguration]]
- [[content-security-policy]]
- [[clickjacking]]
- [[bot-detection-signals]]

---

## Cross-links a redes

- [[http-overview]] → modelo request/response para todos los exploits web
- [[http-messages]] → forma raw de requests, headers, cuerpos
- [[http-headers]] → cookies, CSP, CORS, forwarding, caché
- [[cookies-and-sessions]] → estado y comportamiento de sesión
- [[reverse-proxies]] → límites de confianza y parsing de requests
- [[client-ip-trust]] → abuso de confianza basada en headers
- [[tls-https]] → seguridad de transporte y de cookies
- [[metadata-endpoints]] → amplificación de impacto de SSRF

---

## Notas futuras sugeridas

### Próximas notas atómicas

- secure-headers
- html-injection
- http-trace-method
- hidden-parameters
- bug-bounty-reporting

### Playbooks conectados

- [[exploit-idor]]
- [[exploit-sqli]]
- [[investigate-ssrf]]
- [[inspect-session-handling]]
- [[reverse-proxy-misconfig-checklist]]
- [[test-cors-behavior]]

---

## Referencias

- **Fundamental:** OWASP Top 10 — https://owasp.org/www-project-top-ten/
- **Fundamental:** OWASP WSTG Latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
