# Índice de API Security

## Propósito

Este índice es el punto de entrada a la rama de seguridad de APIs del vault de ciberseguridad.

Usalo para:
- navegar las notas de API security
- entender el orden de estudio
- conectar conceptos de web security con modelos de riesgo específicos de APIs
- fortalecer la intuición de seguridad backend con el pensamiento de autorización a nivel de objeto, función y propiedad

Usá [[reference-registry-api-security|Reference Registry — API Security]] como fuente de verdad para referencias en esta rama.
Volvé a [[index|Índice de Ciberseguridad]] para navegación raíz entre ramas.

> *Antes de esta rama:*
> - [[index|Foundations]] (Fase 0).
> - [[http-overview|HTTP overview]], [[http-headers|HTTP headers]], [[tls-https|TLS/HTTPS]].
> - [[index|Web Security]] — las APIs heredan la mayor parte del threat model web, más el propio.

---

## Orden de estudio recomendado

### Fase 1 — Fundamentos de API security

1. [[api-security-top-10]]
2. [[authorization]]
3. [[broken-object-level-authorization]]
4. [[broken-object-property-level-authorization]]
5. [[broken-function-level-authorization]]

### Fase 2 — Autenticación y confianza en tokens

1. [[broken-authentication]]
2. [[api-auth-flaws]]
3. [[jwt-attacks]]
4. [[token-lifecycle]]

### Fase 3 — Exposición de datos y objetos/propiedades

1. [[mass-assignment]]
2. [[excessive-data-exposure]]

### Fase 4 — Abuso operacional de APIs

1. [[api-rate-limiting]]
2. [[api-inventory-management]]

### Fase 5 — Riesgos de parser y binding

1. [[polymorphic-deserialization]]

---

## Cluster central de API security

### Fundamentos

- [[api-security-top-10]]
- [[authorization]]
- [[broken-object-level-authorization]]
- [[broken-object-property-level-authorization]]
- [[broken-function-level-authorization]]

### Autenticación y manejo de tokens

- [[broken-authentication]]
- [[api-auth-flaws]]
- [[jwt-attacks]]
- [[token-lifecycle]]

### Control de datos y objetos/propiedades

- [[mass-assignment]]
- [[excessive-data-exposure]]

### Resiliencia operacional

- [[api-rate-limiting]]
- [[api-inventory-management]]

### Riesgos de parser y binding

- [[polymorphic-deserialization]]

---

## Notas de mantenimiento de la rama

- Las notas atómicas de esta rama deben seguir la plantilla interna de 11 secciones.
- Preferir hooks de encuadre basados en conteo en `Cómo funciona` o `Variantes y bypasses`.
- Usar [[reference-registry-api-security]] antes de agregar o cambiar referencias.
- Preservar la separación entre autorización de objeto ([[broken-object-level-authorization]]), autorización de propiedad ([[broken-object-property-level-authorization]]), autorización de función ([[broken-function-level-authorization]]), y encuadre de política amplia ([[authorization]]).
- Los labs prácticos deben usar APIs propias, labs locales, o targets de entrenamiento intencionalmente vulnerables.

---

## Cross-links a otras ramas

### Networking

- [[http-overview]]
- [[http-messages]]
- [[http-headers]]
- [[reverse-proxies]]
- [[client-ip-trust]]
- [[caching-and-security]]

### Web security

- [[broken-access-control]]
- [[auth-flaws]]
- [[session-management]]
- [[idor]]
- [[cors-misconfiguration]]
- [[ssrf]]

### Security playbooks

- [[exploit-idor]]
- [[break-jwt-validation]]
- [[test-client-ip-spoofing]]
- [[inspect-session-handling]]

---

## Notas futuras sugeridas

- server-side-parameter-pollution
- graphql-security
- api-versioning-risk
- webhook-security
- pagination-and-enumeration
- schema-exposure
- machine-to-machine-auth

## Referencias

- **Fundamental:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x00-header/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
