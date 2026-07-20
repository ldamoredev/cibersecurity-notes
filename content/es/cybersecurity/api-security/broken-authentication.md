# Broken Authentication

## Definición

La autenticación rota en APIs se refiere a debilidades en la verificación de identidad, manejo de credenciales, emisión de tokens, continuación de sesión, o enforcement de workflow de autenticación que permiten que los callers ganen o mantengan acceso que no deberían tener.

## Por qué importa

La autenticación es la decisión de confianza raíz para la mayoría de las llamadas a APIs. Cuando es inconsistente, cada decisión de autorización, auditoría, rate limit, y control de abuso downstream puede heredar la identidad incorrecta o el nivel de aseguramiento incorrecto.

Esta nota es el mapa de categoría. [[api-auth-flaws]] cubre las inconsistencias de workflow aplicado; [[jwt-attacks]] cubre la validación de tokens y la confianza en claims; [[token-lifecycle]] cubre la emisión, refresco, rotación, y revocación a lo largo del tiempo.

## Cómo funciona

La autenticación de APIs debe distinguir **4 estados**:

1. **Anónimo.** Sin identidad verificada.
2. **Pre-autenticado.** Se presentó una credencial, token, o link pero no se verificó completamente.
3. **Parcialmente autenticado.** Un factor o paso de workflow tuvo éxito, pero se requiere más aseguramiento.
4. **Completamente autenticado.** La API puede tratar al caller como la identidad afirmada para las acciones permitidas.

La autenticación rota ocurre cuando la API salta estados demasiado pronto, olvida transiciones de estado, o trata todas las credenciales como equivalentes.

Ejemplo de fallo:

```
POST /auth/login -> contraseña correcta -> access_token emitido
POST /auth/mfa/verify -> segundo paso opcional
GET /api/billing -> acepta access_token pre-MFA
```

El paso de contraseña tuvo éxito, pero la API no debe tratar al caller como completamente autenticado hasta que se complete el MFA.

## Técnicas / patrones

Los atacantes testean:

- flows de login, recovery, reset, registro, y verificación de email
- emisión de token antes de MFA, verificación de dispositivo, o verificación de cuenta
- reutilización de token obsoleto después de logout, cambio de contraseña, deshabilitación, o cambio de rol
- resistencia a credential stuffing y brute-force
- diferencias entre clientes web, mobile, partner, y legacy
- comportamiento de cuentas de servicio y API keys

## Variantes y bypasses

La autenticación rota aparece en **7 formas**.

### 1. Verificación débil de credenciales

Las contraseñas, API keys, o client secrets se aceptan con política débil, almacenamiento débil, sin throttling, o lógica de comparación deficiente.

### 2. Bypass de MFA

El MFA es opcional, se aplica de forma inconsistente, o está representado por estado controlado por el cliente.

### 3. Toma de control del recovery flow

Los workflows de reset o recovery son más fáciles de explotar que el login normal.

### 4. Emisión de token prematura

La API emite tokens utilizables antes de que el workflow de autenticación esté completo.

### 5. Fallo del ciclo de vida del token

Los tokens sobreviven al logout, cambio de contraseña, deshabilitación de cuenta, remoción de dispositivo, o eventos de riesgo.

### 6. Inconsistencia de cliente

Diferentes clientes o versiones de API hacen cumplir diferentes garantías de autenticación.

### 7. Debilidad de credenciales de máquina

Las credenciales de servicio son demasiado amplias, de larga duración, mal almacenadas, o imposibles de atribuir.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de cuenta.** Los atacantes se autentican como otro usuario.
- **Bypass de MFA o step-up.** Las operaciones sensibles se vuelven alcanzables con menor aseguramiento.
- **Acceso no autorizado persistente.** Las credenciales revocadas, obsoletas, o filtradas siguen funcionando.
- **Credential stuffing y enumeración.** El throttling débil y el feedback habilitado permiten ataques automatizados.
- **Compromiso de servicio.** Las credenciales de máquina exponen acceso de API backend-a-backend.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir estados de autenticación y hacer cumplir transiciones del lado del servidor.**
   Cada endpoint debe saber si requiere autenticación anónima, parcial, completa, step-up, o de servicio.

2.
**Hardening de flows de credencial y recovery juntos.**
   El recovery es autenticación. El reset de contraseña, magic links, y el enrollment de dispositivo necesitan el mismo rigor que el login.

3.
**Emitir tokens solo después de que se satisfaga el aseguramiento requerido.**
   Los tokens pre-MFA o intermedios de recovery deben estar limitados al siguiente paso de auth, no al acceso general de API.

4.
**Diseñar la revocación e invalidación de sesión intencionalmente.**
   El logout, cambio de contraseña, reset de MFA, lock de cuenta, remoción de dispositivo, y cambio de rol deben tener efectos definidos sobre los tokens.

5.
**Aplicar controles de abuso a las rutas de auth.**
   Los rate limits, lockouts, verificaciones de riesgo, y monitoreo pertenecen al login, recovery, MFA, y refresco de token.

6.
**Testear cada cliente y tipo de credencial.**
   Los flows web, mobile, partner, de servicio, y legacy deben proporcionar garantías equivalentes donde alcanzan la misma superficie de API.

### Qué no funciona como defensa primaria

- **Autenticación sin autorización.** Una identidad válida todavía necesita verificaciones por objeto, por función, y por campo.
- **MFA aplicado solo en el frontend.** Los callers directos de API bypassean la lógica de UI.
- **Solo estructura JWT.** Un string en forma de token no es válido a menos que la firma, claims, frescura, y contexto sean correctos.
- **Logout como eliminación de local storage.** Limpiar un token de browser o app no revoca la aceptación del lado del servidor.
- **Solo rate limits genéricos por IP.** El abuso de auth frecuentemente rota IPs y necesita controles conscientes de cuenta, credencial, y ruta.

## Labs prácticos

Usar un lab propio con al menos una cuenta normal y una cuenta de test admin.

### Trazar la máquina de estado de auth

```
anónimo -> contraseña aceptada -> MFA pendiente -> sesión completa -> step-up verificado
```

Mapear qué token o cookie existe en cada paso y qué endpoints lo aceptan.

### Testear acceso pre-MFA

```
curl -i -H "Authorization: Bearer $PRE_MFA_TOKEN" \
  https://api.example.test/billing/payment-methods
```

Los endpoints sensibles deben rechazar los tokens de auth parcial.

### Testear eventos de revocación

```
curl -i -H "Authorization: Bearer $OLD_TOKEN" https://api.example.test/users/me
```

Repetir después de logout, cambio de contraseña, deshabilitación de cuenta, reset de MFA, y degradación de rol.

### Testear el recovery como login

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"email":"user@example.test"}' \
  https://api.example.test/auth/password-reset
```

Verificar lifetime del token, comportamiento de replay, sesiones post-reset, e invalidación de sesiones viejas.

## Ejemplos prácticos

- Una API emite un bearer token antes de completarse el MFA.
- El logout no detiene la reutilización del access token.
- Un endpoint mobile acepta credenciales más débiles que la app web.
- El reset de contraseña crea una sesión completa pero deja activos los refresh tokens viejos.
- Una API key sin propietario puede acceder a datos sensibles de tenant.

## Notas relacionadas

- [[api-auth-flaws]]
- [[jwt-attacks]]
- [[token-lifecycle]]
- [[api-rate-limiting]]
- [[auth-flaws|Auth Flaws]]

## Referencias

- **Fundamental:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger API testing — https://portswigger.net/web-security/api-testing
