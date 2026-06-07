# Test CORS Behavior

## Objetivo

Determinar si la policy CORS es demasiado permisiva, se refleja de forma insegura o se malentiende como control de autorización.

## Supuestos

- uno o más endpoints API/browser dependen de acceso cross-origin
- el navegador impone CORS, no el servidor en sentido general de auth
- credenciales y manejo de origin pueden estar mal configurados

## Prerrequisitos

- endpoints que devuelven headers CORS
- capacidad de enviar headers `Origin` custom
- comprensión de si hay cookies o credenciales involucradas

## Pasos de recon

1. Identificá endpoints cross-origin.
2. Registrá headers `Access-Control-*` en responses normales y preflights.
3. Observá si los origins son estáticos, wildcard o reflejados.

## Pasos de exploit / testing

1. Enviá requests con valores `Origin` controlados por atacante.
2. Verificá si se permiten credenciales junto con origins reflejados.
3. Compará comportamiento preflight y no-preflight.
4. Probá variaciones de subdominio y esquema de origins confiables.
5. Confirmá si el equipo depende de CORS donde debería existir auth server-side.

## Señales de validación

- origin de atacante reflejado
- `Access-Control-Allow-Credentials: true` con comportamiento inseguro de origin
- confianza amplia en subdominios influenciables por atacante
- confusión entre responses legibles y cambios de estado escribibles

## Mitigación

- enumerar explícitamente origins confiables
- nunca tratar CORS como autorización
- revisar cuidadosamente flujos cross-origin con credenciales
- mantener access control server-side independiente de la policy del navegador

## Logging / detección

- origins inesperados golpeando rutas sensibles
- drift en patrones de origins permitidos
- anomalías de preflight en endpoints sensibles a auth

## Notas relacionadas

- [[cors-misconfiguration|CORS Misconfiguration]]
- [[http-headers|HTTP headers]]
- [[csrf|Cross-Site Request Forgery (CSRF)]]
- [[cookies-and-sessions|Cookies y sesiones]]

## Referencias

- **Testing / Lab:** PortSwigger CORS topic — https://portswigger.net/web-security/cors
- **Fundamental:** MDN CORS guide — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
