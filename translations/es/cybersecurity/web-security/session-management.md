---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - web-security
  - sessions
sources: []
---

# Gestión de sesiones

## Definición
La gestión de sesiones es el conjunto de mecanismos que una aplicación usa para mantener el estado autenticado a través de las requests. Esto incluye la creación, rotación, expiración e invalidación de sesiones, y cómo se transportan y protegen los identificadores de sesión.

## Por qué importa
Incluso cuando la autenticación es correcta, una gestión de sesiones débil puede socavar todo el modelo de seguridad. Las sesiones se sientan en la intersección del comportamiento del navegador, las cookies, la lógica de auth y la confianza del lado del servidor.

Esta nota es sobre mantener el estado autenticado de forma segura después de que la identidad fue establecida. [[auth-flaws|Fallas de autenticación]] cubre las fallas de login y prueba de identidad, mientras que [[cybersecurity/api-security/jwt-attacks|Ataques a JWT]] cubre las fallas de estado y validación específicas de tokens.

## Perspectiva del atacante
Los atacantes buscan:
- identificadores de sesión predecibles o reusables
- falta de rotación tras el login o cambio de privilegio
- comportamiento de logout débil
- oportunidades de fixation
- cookies con atributos inseguros
- fuga de sesión a través de URLs o logs

## Perspectiva del defensor
Los defensores deberían:
- rotar los identificadores de sesión en las transiciones de confianza significativas
- expirar las sesiones apropiadamente
- invalidar el estado del lado del servidor correctamente
- mantener los identificadores de sesión fuera de las URLs
- aplicar atributos de cookie seguros y chequeos consistentes del lado del servidor

## Ejemplos prácticos
- Un usuario se loguea pero mantiene el mismo identificador de sesión de antes de la autenticación.
- El logout borra la cookie del navegador pero deja la sesión del lado del servidor válida.
- Las sesiones sobreviven a cambios de contraseña o transiciones de rol sin revalidación.

## Notas relacionadas
- [[cookies-and-sessions|Cookies y sesiones]]
- [[auth-flaws|Fallas de autenticación]]
- [[cybersecurity/api-security/jwt-attacks|Ataques a JWT]]
- [[csrf|CSRF]]
- [[xss|XSS]]
- [[cybersecurity/security-playbooks/inspect-session-handling|Inspeccionar el manejo de sesiones]]

## Referencias
- **Foundational:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/
- **Foundational:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
