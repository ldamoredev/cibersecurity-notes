# API Authentication Flaws

## Definición

Los fallos de autenticación de APIs son debilidades prácticas en cómo una API verifica la identidad a través de flows de login, recovery, MFA, dispositivo, token, y cliente máquina.

## Por qué importa

La autenticación de APIs raramente es un formulario de login ordenado. Los sistemas reales tienen SPAs, apps mobile, cuentas de servicio, refresh tokens, flows de reset de contraseña, magic links, pairing de dispositivos, callbacks OAuth/OIDC, y clientes legacy. Cada flow puede definir accidentalmente un significado diferente de "autenticado."

Esta nota se enfoca en las inconsistencias de workflow aplicado. [[broken-authentication]] es la categoría más amplia, mientras que [[jwt-attacks]] y [[token-lifecycle]] aíslan los modos de fallo específicos de tokens.

## Cómo funciona

Los fallos de autenticación de APIs frecuentemente aparecen a través de **5 superficies de auth**:

1. **Login.** Puntos de entrada de contraseña, SSO, OAuth, passkey, o API key.
2. **Recovery.** Reset de contraseña, verificación de email, recovery de cuenta, y magic links.
3. **MFA y confianza de dispositivo.** Autenticación step-up, dispositivos recordados, y registro de dispositivos.
4. **Refresco y continuación de sesión.** Renovación de access token, rotación, logout, y revocación.
5. **Credenciales de máquina.** API keys, service tokens, client credentials, e integraciones de partner.

El bug usualmente no es "sin autenticación." Es garantías de autenticación inconsistentes entre estas superficies.

Ejemplo de fallo:

```
Login web: contraseña + MFA -> sesión completa
Refresco mobile: refresh token -> sesión completa, sin verificación de estado MFA
Reset de contraseña: link de un solo uso -> access token, sin revisión de dispositivo o MFA
```

## Técnicas / patrones

Los atacantes testean:

- comportamiento de cliente web vs mobile vs partner
- tokens emitidos antes de que se complete el MFA
- links de reset de contraseña que crean sesiones completamente autenticadas
- flows de registro de dispositivo o dispositivo recordado
- API keys con scope excesivo o sin rotación
- efectos del logout, cambio de contraseña, y lock de cuenta
- diferencias entre versiones de API legacy y actuales

## Variantes y bypasses

Los fallos de auth de APIs aparecen en **6 formas recurrentes**.

### 1. Puente de token pre-MFA

La API emite un token después del paso de contraseña y luego lo trata como completamente autenticado.

### 2. Recovery flow como login más débil

Los flows de reset, magic-link, o verificación se convierten en paths de login más fáciles que la autenticación normal.

### 3. Sobrealcance de confianza de dispositivo

Los dispositivos recordados o el registro de dispositivos producen credenciales duraderas con revocación débil.

### 4. Inconsistencia de cliente

Los clientes mobile, web, partner, o internos hacen cumplir diferentes reglas de credencial, MFA, o sesión.

### 5. Sprawl de credenciales de máquina

Las API keys y service tokens tienen privilegios amplios, tiempos de vida largos, o propiedad poco clara.

### 6. Bypass de step-up

Las operaciones sensibles requieren step-up en una ruta pero no en otra ruta que llega al mismo efecto.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de cuenta.** Los gaps de recovery, reset, o MFA permiten acceso no autorizado.
- **Bypass de MFA.** Los estados de solo contraseña o pre-MFA se vuelven suficientes para llamadas sensibles de API.
- **Acceso persistente.** Los tokens o credenciales de dispositivo sobreviven al logout, reset, o lock de cuenta.
- **Compromiso de cliente máquina.** Las credenciales de servicio de larga duración exponen amplio alcance de API.
- **Confusión de auditoría e incidente.** Las múltiples superficies de auth hacen poco claro qué garantía falló.

## Detección y defensa

Ordenado por efectividad:

1.
**Inventariar cada punto de entrada de autenticación y tipo de token.**
   No podés asegurar solo la ruta de login principal. Los flows de recovery, dispositivo, refresh, servicio, y partner todos emiten confianza.

2.
**Modelar estados de auth explícitamente.**
   Separar estados de anónimo, contraseña verificada, MFA verificado, step-up verificado, dispositivo confiable, y servicio autenticado.

3.
**Centralizar las decisiones de seguridad preservando el contexto del flow.**
   El middleware de auth compartido ayuda a la consistencia, pero debe llevar si se usó MFA, recovery, confianza de dispositivo, o identidad de servicio.

4.
**Tratar los flows de recovery y dispositivo como equivalentes al login.**
   Un path de reset de contraseña o pairing de dispositivo puede convertirse en la forma más fácil de entrar a la cuenta si no se hardenea.

5.
**Scopear y rotar las credenciales de máquina.**
   Las API keys y service tokens necesitan propiedad, menor privilegio, expiración, rotación, y revocación.

6.
**Testear flows de auth como workflows cross-client.**
   Comparar clientes web, mobile, docs de API, versiones legacy, y clientes partner para garantías de seguridad equivalentes.

### Qué no funciona como defensa primaria

- **Asumir que el flow de login principal representa toda la autenticación.** Los flows de recovery, refresh, y máquina frecuentemente lo bypassean.
- **Flags de MFA del lado del cliente.** El servidor debe hacer cumplir el estado de auth desde contexto del lado del servidor confiable o afirmaciones de token validadas.
- **API keys de larga duración sin propiedad.** Los propietarios desconocidos y sin expiración hacen lenta la respuesta a incidentes.
- **Logout que solo limpia el almacenamiento del cliente.** La utilidad del token del lado del servidor debe abordarse.
- **Seguridad por tipo de cliente.** Los clientes mobile o partner siguen siendo callers directos de API.

## Labs prácticos

Usar una app propia o entorno de lab con clientes web y de API.

### Mapear puntos de entrada de auth

```
rg -n "login|reset|recover|mfa|refresh|device|api-key|client_credentials" routes src openapi.yaml
```

Convertir los resultados en una tabla de flow, credencial, token emitido, estado MFA, lifetime, y evento de revocación.

### Testear comportamiento del token pre-MFA

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"email":"user@example.test","password":"correct-password"}' \
  https://api.example.test/auth/login
```

Si la respuesta incluye un token antes del MFA, testear si ese token puede llamar endpoints sensibles.

### Testear fortaleza de sesión del reset-token

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"resetToken":"TOKEN","newPassword":"NewPass123!"}' \
  https://api.example.test/auth/reset/complete
```

Verificar si la compleción del reset crea una sesión completa y si los tokens viejos siguen siendo utilizables.

### Testear scope de credenciales de máquina

```
curl -i -H "Authorization: Bearer $SERVICE_TOKEN" \
  https://api.example.test/admin/users
```

Las credenciales de servicio deben estar limitadas a las rutas, tenants, y acciones previstas.

## Ejemplos prácticos

- Una ruta de API mobile omite el MFA aplicado en el flow web.
- La compleción del reset de contraseña devuelve un access token completo sin invalidar sesiones viejas.
- El registro de dispositivos crea un token de larga duración que no puede revocarse por dispositivo.
- Una API key de partner puede llamar endpoints similares a admin fuera de su scope de integración.
- Una operación sensible requiere step-up en la UI pero no a través de la ruta directa de API.

## Notas relacionadas

- [[broken-authentication]]
- [[jwt-attacks]]
- [[token-lifecycle]]
- [[break-jwt-validation|Break JWT Validation]]
- [[auth-flaws|Auth Flaws]]

## Referencias

- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Testing / Lab:** PortSwigger authentication vulnerabilities — https://portswigger.net/web-security/authentication
