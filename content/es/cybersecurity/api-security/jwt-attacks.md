# JWT Attacks

## Definición

Los ataques JWT explotan debilidades en cómo los JSON Web Tokens son emitidos, validados, confiados, scopeados, o expirados. El riesgo no es que una API use JWTs; el riesgo es aceptar el contenido del token sin las verificaciones criptográficas y contextuales correctas.

## Por qué importa

Los JWTs son contenedores de confianza portables. Esa portabilidad es útil para APIs y microservicios, pero también significa que una mala decisión de validación puede propagarse entre servicios, clientes, y capas de autorización.

Esta nota se enfoca en la validación de tokens y la confianza contenida en tokens. [[broken-authentication]] se mantiene más amplia, y [[token-lifecycle]] tiene la emisión, refresco, rotación, revocación, y comportamiento de expiración a lo largo del tiempo.

## Cómo funciona

Un consumidor JWT debe pasar **6 gates de validación**:

1. **Estructura.** El token está bien formado y se decodifica de forma segura.
2. **Firma.** La firma es válida para el algoritmo y clave esperados.
3. **Issuer.** `iss` coincide con el identity provider confiable.
4. **Audience.** `aud` coincide con esta API o servicio.
5. **Tiempo.** `exp`, `nbf`, y `iat` son aceptables para esta decisión de confianza.
6. **Claims y contexto.** Los claims de `sub`, `scope`, `role`, tenant, sesión, y aseguramiento están autorizados para la acción.

Los ataques JWT usualmente explotan un gate faltante o gates inconsistentes entre servicios.

Inspección de ejemplo:

```
jq -R 'split(".") | .[0], .[1] | @base64d | fromjson' <<< "$JWT"
```

Decodificar no es validar. Solo revela qué afirma el token.

## Técnicas / patrones

Los atacantes testean:

- reutilización de token vencido
- aceptación de `aud` o `iss` incorrecto
- confusión de algoritmo o selección de clave débil
- aceptación de tokens no firmados o mal firmados
- afirmaciones obsoletas de roles, scopes, o tenant después de cambios
- validación inconsistente entre servicios
- expectativas de logout, reset de contraseña, y revocación

## Variantes y bypasses

Los ataques JWT aparecen en **7 formas comunes**.

### 1. Fallo de validación de firma

El servicio decodifica el token pero no verifica correctamente la firma.

### 2. Confusión de algoritmo y clave

El servicio acepta algoritmos inesperados, usa la fuente de clave incorrecta, o confía en metadata de clave influenciada por el atacante.

### 3. Mismatch de issuer o audience

Un token emitido para otro servicio, tenant, o entorno es aceptado.

### 4. Fallo de expiración y frescura

Los tokens vencidos, aún-no-válidos, o muy viejos siguen siendo utilizables.

### 5. Claims de autorización obsoletos

Los roles o scopes en tokens viejos siguen otorgando acceso después de cambios de privilegio.

### 6. Inconsistencia cross-service

Una API valida claims estrictamente mientras otro servicio acepta tokens más débiles.

### 7. Confusión de presencia de token

La aplicación trata "tiene un JWT" como equivalente a "puede ejecutar esta acción."

## Impacto

Ordenado aproximadamente por severidad:

- **Bypass de autenticación.** Se aceptan tokens inválidos o fabricados por el atacante.
- **Escalada de privilegios.** Los claims obsoletos o manipulados otorgan acceso más fuerte.
- **Acceso cross-service.** Los tokens para un audience funcionan contra otra API.
- **Acceso persistente.** Los tokens sobreviven al logout, cambio de contraseña, o degradación de rol.
- **Ruptura de límite de tenant.** Los claims de tenant se confían sin autorización del lado del servidor.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar librerías JWT vetadas con configuraciones de verificación estrictas.**
   No hacer la validación JWT a mano. Configurar algoritmos permitidos, issuer esperado, audience esperado, clock skew, y claims requeridos explícitamente.

2.
**Pinar la confianza al issuer, audience, algoritmo, y material de clave esperados.**
   Una firma válida no es suficiente si el token vino del issuer incorrecto o fue pensado para otro servicio.

3.
**Mantener los tokens de corta duración y con scope estrecho.**
   Los tiempos de vida cortos reducen el riesgo de claims obsoletos. Los audiences y scopes estrechos reducen el blast radius.

4.
**Tratar los claims JWT como inputs a la autorización, no como autoridad final.**
   Los roles, IDs de tenant, y scopes todavía necesitan verificaciones de política del lado del servidor contra el objeto y acción solicitados.

5.
**Diseñar la revocación y la rotación de claves deliberadamente.**
   Los tokens stateless todavía necesitan respuestas prácticas para logout, compromiso, cambio de rol, y rollover de clave de firma.

6.
**Testear cada consumidor de tokens.**
   En microservicios, el consumidor más débil define el límite de confianza efectivo.

### Qué no funciona como defensa primaria

- **Verificaciones de decodificación Base64.** Leer el payload no es validación de firma.
- **Confiar en `alg`, `kid`, o URLs de clave de input no confiable.** La metadata del header no debe seleccionar trust roots arbitrarios.
- **Claims de rol de larga duración.** Los roles embebidos por horas o días se convierten en autoridad obsoleta.
- **JWTs como autorización por sí mismos.** Los tokens identifican y llevan claims; la política todavía decide el acceso.
- **Logout que solo elimina el token del browser.** Otras copias del token pueden seguir siendo utilizables.

## Labs prácticos

Usar solo tokens de sistemas propios o labs intencionalmente vulnerables.

### Decodificar y documentar supuestos de validación

```
jq -R 'split(".") | .[0], .[1] | @base64d | fromjson' <<< "$JWT"
```

Registrar `alg`, `kid`, `iss`, `aud`, `sub`, `exp`, `iat`, scopes, roles, y claims de tenant.

### Testear límites de audience e issuer

```
curl -i -H "Authorization: Bearer $TOKEN_FOR_OTHER_API" \
  https://api.example.test/users/me
```

La API debe rechazar tokens emitidos para un audience o issuer diferente.

### Testear comportamiento de expiración

```
curl -i -H "Authorization: Bearer $EXPIRED_TOKEN" \
  https://api.example.test/users/me
```

Los tokens vencidos deben fallar consistentemente en todos los servicios.

### Testear claims de privilegio obsoletos

```
curl -i -H "Authorization: Bearer $OLD_ADMIN_TOKEN" \
  https://api.example.test/admin/users
```

Después de la degradación de rol, los tokens privilegiados viejos no deben seguir otorgando acceso sensible más allá de la ventana prevista.

## Ejemplos prácticos

- Un token con el audience incorrecto es aceptado por una API interna.
- Un servicio acepta tokens vencidos mientras otro los rechaza.
- Una degradación de rol no afecta los tokens de admin emitidos previamente.
- La metadata del header JWT lleva al verificador a la clave incorrecta.
- Un servicio verifica la firma pero ignora la autorización de tenant.

## Notas relacionadas

- [[broken-authentication]]
- [[api-auth-flaws]]
- [[token-lifecycle]]
- [[authorization]]
- [[break-jwt-validation|Break JWT Validation]]
- [[session-management|Session Management]]

## Referencias

- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- **Fundamental:** OWASP JSON Web Token for Java Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger JWT attacks topic — https://portswigger.net/web-security/jwt
