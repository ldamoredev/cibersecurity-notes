# Reference Registry — API Security

## Propósito

Esta nota es la semilla específica de API security para el registro de referencias de ciberseguridad más amplio.

Usala para:
- estandarizar referencias para notas de API security
- mantener la calidad de las fuentes consistente
- ayudar a asignar referencias sin inventar sets de fuentes débiles
- hacer más fácil expandir notas futuras de API security

## Regla de fuente de verdad

Para notas de API security, este registro es la fuente de verdad primaria.

Usalo junto con:
- `<a href="api-security/index.html">API Security Index</a>` para orden de estudio y estructura de rama
- `<a href="reference-registry.html">Cybersecurity Reference Registry</a>` como fallback más amplio solo cuando esta nota no cubre todavía un tema de API security

---

## Política de selección de referencias

### Prioridad de fuentes

1. estándares oficiales y documentación de proyectos
2. labs oficiales y entrenamiento práctico
3. guías de testing y cheat sheets
4. investigación de alta señal
5. fuentes secundarias solo cuando agregan valor claro

### Objetivo por nota

- mínimo 2 referencias
- ideal 3 referencias
- evitar inflar notas con listas largas

### Etiquetado

Usar:
- **Fundamental**
- **Testing / Lab**
- **Investigación / Deep Dive**
- **Docs Oficiales**

---

# Mapa de temas de API security

## api-security-top-10

Referencias preferidas:
- **Fundamental:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x00-header/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Fundamental:** OWASP REST Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## authorization

Referencias preferidas:
- **Fundamental:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## broken-object-level-authorization

Referencias preferidas:
- **Fundamental:** OWASP API1:2023 Broken Object Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa1-bola/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger access control / IDOR — https://portswigger.net/web-security/access-control/idor

## broken-function-level-authorization

Referencias preferidas:
- **Fundamental:** OWASP API5:2023 Broken Function Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa5-bfla/
- **Fundamental:** OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger access control — https://portswigger.net/web-security/access-control

## broken-authentication

Referencias preferidas:
- **Fundamental:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## api-auth-flaws

Referencias preferidas:
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication

## jwt-attacks

Referencias preferidas:
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP JSON Web Token for Java Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger JWT attacks topic — https://portswigger.net/web-security/jwt

## token-lifecycle

Referencias preferidas:
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Fundamental:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/

## broken-object-property-level-authorization

Referencias preferidas:
- **Fundamental:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure

## excessive-data-exposure

Referencias preferidas:
- **Fundamental:** OWASP WSTG API testing: excessive data exposure — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/03-Testing_for_Excessive_Data_Exposure
- **Fundamental:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## mass-assignment

Referencias preferidas:
- **Fundamental:** OWASP API Security Top 10 2023 — https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- **Fundamental:** OWASP API3:2023 Broken Object Property Level Authorization — https://owasp.org/API-Security/editions/2023/en/0xa3-bopla/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## api-rate-limiting

Referencias preferidas:
- **Fundamental:** OWASP API4:2023 Unrestricted Resource Consumption — https://owasp.org/API-Security/editions/2023/en/0xa4-unrestricted-resource-consumption/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing

## api-inventory-management

Referencias preferidas:
- **Fundamental:** OWASP API9:2023 Improper Inventory Management — https://owasp.org/API-Security/editions/2023/en/0xa9-improper-inventory-management/
- **Fundamental:** OWASP API Security Project — https://owasp.org/www-project-api-security/
- **Testing / Lab:** PortSwigger API testing and OWASP alignment — https://portswigger.net/web-security/api-testing/top-10-api-vulnerabilities

## polymorphic-deserialization

Referencias preferidas:
- **Fundamental:** OWASP Deserialization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html
- **Fundamental:** OWASP API8:2023 Security Misconfiguration — https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/
- **Testing / Lab:** PortSwigger Exploiting insecure deserialization — https://portswigger.net/web-security/deserialization/exploiting
- **Investigación / Deep Dive:** Moritz Bechler, "Java Unmarshaller Security" (`marshalsec`) — https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf
- **Docs Oficiales:** ysoserial.net — https://github.com/pwntester/ysoserial.net

---

## Reglas de uso del registro

- elegir el conjunto más pequeño de referencias más fuertes para cada nota exacta
- no asignar links genéricos ciegamente
- preferir documentación oficial y labs sólidos
- si una futura nota de API security está ausente de este registro, mapearla al tema padre más cercano primero
