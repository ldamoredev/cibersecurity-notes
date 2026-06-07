# Break JWT Validation

## Objetivo

Identificar si el manejo de JWT es lo suficientemente débil como para aceptar tokens inválidos, viejos, mal scopeados o influenciados por un atacante.

## Supuestos

- la app usa JWTs para auth o estado tipo sesión
- la lógica de validación puede ser inconsistente entre servicios
- los developers pueden confundir presencia del token con autorización válida

## Prerrequisitos

- tokens de muestra de flujos autenticados
- capacidad de replay de requests
- comprensión básica de la estructura JWT

## Pasos de recon

1. Determiná dónde se emiten y consumen los tokens.
2. Mapeá claims que parecen influir en la autorización.
3. Identificá si múltiples servicios validan el mismo token de forma diferente.

## Pasos de exploit / testing

1. Reproducí tokens expirados o viejos.
2. Eliminá o alterá claims no críticos para observar qué tan estricta es la validación.
3. Probá si audience, issuer o scope checks parecen aplicarse.
4. Compará comportamiento entre entradas web, mobile y API.
5. Verificá si logout o cambios de privilegio realmente revocan la utilidad del token.

## Señales de validación

- tokens expirados siguen funcionando
- claims cambiados o faltantes son aceptados
- servicios distintos aceptan estados distintos del token
- las decisiones de autorización dependen de claims débiles o stale

## Mitigación

- validar firma, issuer, audience, expiry y claims relevantes de forma consistente
- separar authentication de authorization checks
- minimizar lifetime y scope del token
- diseñar estrategias explícitas de revocación cuando haga falta

## Logging / detección

- uso repetido de tokens expirados
- anomalías de claims en tokens
- decisiones auth inconsistentes entre servicios para el mismo subject

## Notas relacionadas

- [[auth-flaws|Fallas de autenticación]]
- [[jwt-attacks|JWT Attacks]]
- [[token-lifecycle|Ciclo de vida de tokens]]
- [[session-management|Gestión de sesiones]]

## Referencias

- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Fundamental:** OWASP WSTG — https://owasp.org/www-project-web-security-testing-guide/latest/
