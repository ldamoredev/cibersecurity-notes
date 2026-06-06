# Token Lifecycle

## Definición

El ciclo de vida del token es la secuencia completa de crear, emitir, refrescar, rotar, revocar, expirar, e invalidar tokens a través de una sesión de API autenticada o relación máquina-a-máquina.

## Por qué importa

Muchas debilidades de autenticación de APIs son fallos de ciclo de vida más que fallos de login. Un token que sobrevive demasiado tiempo, se refresca sin rotación, o ignora eventos de revocación se convierte en un artefacto de confianza permanente.

Esta nota es sobre lo que pasa después de la emisión. [[jwt-attacks]] cubre la semántica de validación, mientras que [[broken-authentication]] y [[api-auth-flaws]] cubren workflows de autenticación más amplios.

## Cómo funciona

El ciclo de vida del token tiene **6 eventos**:

1. **Emisión.** El sistema crea un token después de un estado de autenticación definido.
2. **Uso.** Las APIs aceptan el token para audiences, scopes, rutas, y acciones específicas.
3. **Refresco.** El cliente obtiene nuevo acceso sin repetir la autenticación completa.
4. **Rotación.** Las credenciales de refresco se reemplazan para reducir el valor de replay.
5. **Revocación.** El sistema invalida tokens después de eventos de seguridad o de cuenta.
6. **Expiración.** El token deja de funcionar después de un lifetime planificado.

La debilidad aparece cuando los equipos definen la emisión pero dejan fuzzy el refresco, rotación, revocación, y expiración.

Tabla de ciclo de vida de ejemplo:

```
access token  | 10 min | bearer | sin rotación | solo expira
refresh token | 30 días | almacenado | rotar en cada uso | revocar en logout/cambio de contraseña
api key       | 90 días | header | rotación manual | revocar en remoción de propietario
```

## Técnicas / patrones

Los atacantes testean:

- access tokens que siguen válidos después del logout
- refresh tokens que pueden reproducirse después del uso
- tokens que sobreviven al cambio de contraseña, reset de MFA, lock de cuenta, o remoción de dispositivo
- claims viejos de rol o tenant después de cambios de privilegio
- service tokens sin expiración o propietario
- invalidación inconsistente entre servicios

## Variantes y bypasses

Los fallos de ciclo de vida de tokens aparecen en **7 formas**.

### 1. Access tokens de duración excesiva

Los access tokens viven el tiempo suficiente como para que el compromiso tenga una gran ventana.

### 2. Refresh tokens sin rotación

Los refresh tokens pueden reproducirse repetidamente si se roban.

### 3. Mismatch de logout

El logout limpia el estado del cliente pero no invalida la utilidad del token.

### 4. Puntos ciegos de eventos de seguridad

El cambio de contraseña, reset de MFA, deshabilitación de cuenta, o remoción de dispositivo no afecta los tokens activos.

### 5. Claims de autorización obsoletos

Los tokens emitidos preservan roles, scopes, o estado de tenant viejos por demasiado tiempo.

### 6. Permanencia de service tokens

Las credenciales de máquina no tienen propietario, expiración, scope, o proceso de rotación.

### 7. Lag de revocación distribuida

Una API rechaza un token revocado mientras otra sigue aceptándolo.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso no autorizado persistente.** Los tokens robados o viejos siguen siendo útiles.
- **Persistencia de privilegio.** Los cambios de rol o scope no toman efecto rápidamente.
- **Fijación o replay de sesión.** Los refresh tokens pueden reutilizarse después de ser robados.
- **Compromiso de credencial de máquina.** Los service tokens de larga duración exponen amplia superficie de API.
- **Retraso en respuesta a incidentes.** Los equipos no pueden invalidar confiadamente las credenciales afectadas.

## Detección y defensa

Ordenado por efectividad:

1.
**Definir reglas de ciclo de vida por tipo de token.**
   Los access tokens, refresh tokens, API keys, device tokens, y service tokens necesitan diferentes lifetimes, scopes, reglas de almacenamiento, y semánticas de revocación.

2.
**Usar access tokens de corta duración con audience y scope estrechos.**
   Esto limita el valor de replay y la exposición de autorización obsoleta.

3.
**Rotar refresh tokens y detectar el reuso.**
   El reuso de refresh token después de la rotación es una señal fuerte de robo y debe revocar la familia de tokens.

4.
**Vincular la revocación a eventos de seguridad significativos.**
   El logout, cambio de contraseña, cambio de MFA, remoción de dispositivo, lock de cuenta, degradación de rol, y compromiso de clave deben tener efectos de token explícitos.

5.
**Rastrear familias de tokens, dispositivos, y propietarios.**
   Los usuarios y operadores necesitan poder revocar un dispositivo, integración, o credencial de servicio sin destruir sesiones no relacionadas.

6.
**Testear la propagación de revocación entre servicios.**
   Los sistemas distribuidos necesitan rechazo consistente de tokens revocados o obsoletos.

### Qué no funciona como defensa primaria

- **Bearer tokens de muy larga duración.** Cualquiera que tenga el token puede usarlo por demasiado tiempo.
- **Refresco sin rotación.** Un refresh token robado sigue siendo valioso indefinidamente dentro de su lifetime.
- **Logout como solo limpieza de UI.** El token debe dejar de ser aceptado donde la política lo requiera.
- **Embeber roles de larga duración en tokens.** La verdad de autorización cambia más rápido que la expiración del token.
- **Planillas manuales para propiedad de API key.** Las credenciales de servicio necesitan propiedad y rotación ejecutables.

## Labs prácticos

Usar una cuenta de lab donde se puedan disparar eventos de auth de forma segura.

### Construir una matriz de ciclo de vida

```
tipo de token | lifetime | audience | scope | rotación | eventos de revocación | propietario/dispositivo
```

Llenar para access tokens, refresh tokens, API keys, service tokens, y device tokens.

### Testear revocación por logout

```
curl -i -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.test/users/me
curl -i -X POST -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.test/auth/logout
curl -i -H "Authorization: Bearer $ACCESS_TOKEN" https://api.example.test/users/me
```

El resultado esperado depende del diseño, pero debe estar documentado y ser consistente.

### Testear rotación de refresh token

```
curl -i -X POST -H 'Content-Type: application/json' \
  -d '{"refreshToken":"'$REFRESH_TOKEN'"}' \
  https://api.example.test/auth/refresh
```

Repetir con el refresh token viejo. El reuso debe fallar si la rotación está habilitada.

### Testear frescura del cambio de privilegio

```
curl -i -H "Authorization: Bearer $OLD_ADMIN_TOKEN" \
  https://api.example.test/admin/users
```

Después de la degradación de rol, los tokens viejos deben dejar de otorgar acceso privilegiado dentro de la ventana prevista.

## Ejemplos prácticos

- Los access tokens siguen válidos después del cambio de contraseña.
- La rotación de refresh token falta, habilitando el replay.
- Una degradación de rol no afecta los tokens ya emitidos.
- Las API keys no tienen propietario o expiración.
- Un microservicio honra la revocación mientras otro acepta tokens obsoletos.

## Notas relacionadas

- [[jwt-attacks]]
- [[broken-authentication]]
- [[api-auth-flaws]]
- [[api-rate-limiting]]
- [[inspect-session-handling|Inspect Session Handling]]
- [[session-management|Session Management]]

## Referencias

- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP API2:2023 Broken Authentication — https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/
- **Fundamental:** OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
