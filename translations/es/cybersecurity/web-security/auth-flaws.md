---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - authentication
sources: []
---

# Fallas de autenticación

## Definición
Las fallas de autenticación son debilidades en cómo una aplicación verifica la identidad. Incluyen lógica de login débil, enumeración de usuarios, flujos de MFA rotos, debilidades en el reset de contraseña, exposición a credential stuffing y supuestos defectuosos alrededor de la emisión de sesiones/tokens.

## Por qué importa
La autenticación es la puerta de entrada a la app. Cuando falla, los atacantes a menudo obtienen acceso antes de necesitar algo más avanzado. Estas fallas también amplían la superficie de ataque para la escalada de privilegios y el account takeover.

Esta nota es sobre probar la identidad correctamente. [[session-management|Gestión de sesiones]] cubre lo que pasa después de que el login tiene éxito, y [[cybersecurity/api-security/jwt-attacks|Ataques a JWT]] cubre los modos de falla específicos de tokens en vez del flujo de auth más amplio.

## Perspectiva del atacante
Los atacantes testean:
- el comportamiento de error del login
- las protecciones contra fuerza bruta
- los huecos de enforcement de MFA
- los flujos de reset y recuperación de contraseña
- la emisión de tokens tras validación parcial
- la enumeración de usuarios a través de timing o mensajes

## Perspectiva del defensor
Los defensores deberían:
- hacer los flujos de autenticación explícitos y testeables
- limitar el impacto de la fuerza bruta y el credential stuffing
- endurecer el reset y la recuperación de contraseña
- tratar el MFA como un control con casos borde, no como una capa mágica
- evitar filtrar la existencia de cuentas o el estado de auth

## Ejemplos prácticos
- La app revela si un email existe en el login.
- Los tokens de reset de contraseña son débiles o nunca expiran.
- El MFA se impone en la UI pero no en una llamada de API directa.

## Notas relacionadas
- [[session-management|Gestión de sesiones]]
- [[cybersecurity/api-security/jwt-attacks|Ataques a JWT]]
- [[broken-access-control|Control de acceso roto]]
- [[client-ip-trust|Confianza en la IP del cliente]]
- [[cookies-and-sessions|Cookies y sesiones]]

## Referencias
- **Foundational:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Foundational:** OWASP WSTG authentication testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication
