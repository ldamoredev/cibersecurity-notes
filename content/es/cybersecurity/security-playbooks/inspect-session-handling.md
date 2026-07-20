# Inspect Session Handling

## Objetivo

Determinar si los identificadores de sesión, lifecycle y comportamiento de cookies se manejan de forma segura a través de login, logout y transiciones de privilegio.

## Supuestos

- la app usa cookies o estado de sesión respaldado por tokens
- el comportamiento del navegador influye en el riesgo
- rotación e invalidación de sesión pueden estar incompletas

## Prerrequisitos

- una o más cuentas de prueba
- browser devtools o tooling de proxy
- capacidad de observar cookies y hacer replay de requests

## Pasos de recon

1. Registrá estado de sesión antes del login.
2. Capturá headers Set-Cookie en login y logout.
3. Observá comportamiento de sesión ante cambios de contraseña, cambios de rol e inactividad.

## Pasos de exploit / testing

1. Verificá si el identificador de sesión cambia después del login.
2. Verificá si logout invalida estado server-side.
3. Reproducí requests con cookies viejas después del logout.
4. Testeá si las cookies usan `HttpOnly`, `Secure` y `SameSite` apropiado.
5. Observá si transiciones privilegiadas reutilizan estado de sesión viejo.

## Señales de validación

- mismo session ID antes y después del login
- cookies viejas siguen funcionando después del logout
- cookies sin atributos seguros
- la sesión persiste inesperadamente a través de transiciones de confianza

## Mitigación

- rotar sesiones después de authentication y cambios de privilegio
- invalidar correctamente sesiones server-side
- setear atributos seguros de cookie
- mantener session IDs fuera de URLs y logs
- alinear política de timeout con riesgo

## Logging / detección

- session IDs reutilizados entre múltiples estados auth
- reutilización post-logout de sesiones supuestamente muertas
- reutilización sospechosa de sesión a través de cambios de IP/dispositivo cuando corresponda

## Notas relacionadas

- [[session-management|Gestión de sesiones]]
- [[cookies-and-sessions|Cookies y sesiones]]
- [[auth-flaws|Fallas de autenticación]]
- [[csrf|Cross-Site Request Forgery (CSRF)]]

## Referencias

- **Fundamental:** OWASP WSTG session management testing — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Fundamental:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- **Fundamental:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
