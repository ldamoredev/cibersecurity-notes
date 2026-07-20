# OAuth Security

## Definición

OAuth security es el conjunto de controles que evitan que los flujos de autorización OAuth/OIDC filtren códigos de autorización, tokens, claims de identidad, o confianza en la redirección hacia el cliente equivocado o hacia un destino controlado por el atacante.

## Por qué importa

OAuth no es solo "login con otro proveedor." Es un protocolo de delegación basado en redirecciones que involucra navegadores, clientes, proveedores de identidad, redirect URIs, códigos, tokens, scopes y claims de identidad del usuario. Pequeños vacíos de validación pueden convertirse en toma de control de cuentas o robo de tokens.

Esta nota se enfoca en las fallas de OAuth/OIDC en apps web. [[jwt-attacks]] cubre los detalles de validación de JWT, y [[open-redirect]] cubre el comportamiento genérico de redirectores.

## Cómo funciona

El flujo de authorization code de OAuth tiene **6 verificaciones de confianza**:

1. **Identidad del cliente.** El cliente está registrado y tiene permitido usar el flujo.
2. **Redirect URI.** El callback coincide exactamente con un destino registrado.
3. **State.** La respuesta coincide con la sesión del navegador que inició el flujo.
4. **Intercambio de código.** El código de autorización es intercambiado por el cliente legítimo.
5. **Validación de token.** Los tokens ID/access tienen el issuer, audience, expiración y firma correctos.
6. **Binding de cuenta.** La identidad devuelta se mapea de forma segura a una cuenta local.

El bug generalmente es tratar un paso exitoso de OAuth como prueba de que todas las verificaciones de confianza tuvieron éxito.

## Técnicas / patrones

Los atacantes testean:

- cadenas de open redirect en redirect URIs registradas
- `state` débil o ausente
- coincidencia de redirect URI por prefijo, sufijo o wildcard
- filtración de código a través de referrers, logs o redirecciones a terceros
- confusión de cuentas por confianza en el claim de email
- scope excesivo y reutilización de tokens
- vacíos de validación del ID token

## Variantes y bypasses

Las fallas de OAuth aparecen en **7 formas**.

### 1. Bypass de redirect URI

La validación acepta destinos de callback controlados por el atacante.

### 2. State ausente o débil

El CSRF o la confusión de login se vuelven posibles.

### 3. Encadenamiento con open redirect

Una redirect URI de confianza reenvía códigos o tokens a otro lugar.

### 4. Interceptación de código

Los códigos se filtran a través de logs, referrers, historial del navegador o clientes maliciosos.

### 5. Falla en la validación de token

La app confía en tokens con issuer, audience, expiración o firma incorrectos.

### 6. Confusión en el linking de cuentas

El email o la identidad del proveedor se vincula a la cuenta local equivocada.

### 7. Scope excesivo

El cliente solicita o recibe permisos más amplios de los necesarios.

## Impacto

Ordenado aproximadamente por severidad:

- **Toma de control de cuenta.** Códigos, tokens o claims de identidad se vinculan al control del atacante.
- **Robo de tokens.** Los bugs de redirección o validación filtran tokens utilizables.
- **Login CSRF.** Las víctimas inician sesión en cuentas vinculadas al atacante.
- **Scope excesivo o datos excesivos.** Los scopes amplios exponen más de lo que la funcionalidad necesita.
- **Confusión de identidad.** El mapeo incorrecto de issuer/proveedor/cuenta otorga acceso.

## Detección y defensa

Ordenado por efectividad:

1.
**Usar coincidencia exacta de redirect URI.**
   Evitar wildcards, verificaciones de prefijo y endpoints de cadenas de redirección.

2.
**Usar `state` fuerte por request y validarlo del lado del servidor.**
   `state` vincula la sesión del navegador a la respuesta de OAuth.

3.
**Usar authorization code con PKCE para clientes públicos.**
   PKCE reduce el riesgo de interceptación de código, especialmente para SPAs y clientes móviles.

4.
**Validar los tokens completamente.**
   Verificar firma, issuer, audience, expiración, nonce donde sea relevante, y claims requeridos.

5.
**Vincular cuentas usando IDs de sujeto estables del proveedor.**
   No depender solo de claims de email mutables o no verificados.

6.
**Solicitar scopes de mínimo privilegio.**
   Los scopes deberían coincidir con la funcionalidad, no con los defaults del proveedor.

### Qué no funciona como defensa primaria

- **Redirect URIs con wildcard.** Hacen que la confianza en la redirección sea demasiado amplia.
- **Open redirectors como callbacks.** El registro exacto de callback se derrota por el reenvío.
- **Binding de cuentas solo por email.** Los emails pueden ser no verificados, cambiados, o depender del proveedor.
- **Decodificar ID tokens sin validación.** La estructura del token no es prueba de confianza.

## Labs prácticos

Usar un lab OAuth local o una integración propia.

### Inventario de configuración OAuth

```
client_id | redirect_uri | scopes | public/confidential | PKCE | owner
```

Las redirect URIs exactas y los campos de propietario importan.

### Testear la estrictez del redirect URI

```
curl -i 'https://idp.example.test/auth?client_id=CLIENT&redirect_uri=https://app.example.test.evil.example/callback'
```

El proveedor debería rechazar los destinos no exactos.

### Buscar callbacks OAuth y manejo de state

```
rg -n "redirect_uri|client_id|state|nonce|code_verifier|oauth|oidc" src config
```

Revisar si se aplican el state, el nonce y la validación de tokens.

## Ejemplos prácticos

- Una verificación de prefijo de redirect URI acepta `https://app.example.test.evil.example`.
- Un callback registrado es un open redirect que reenvía el código.
- El login OAuth carece de `state`, habilitando login CSRF.
- Los ID tokens se decodifican pero no se validan.
- Las cuentas locales se vinculan por email sin verificar el sujeto del proveedor.

## Notas relacionadas

- [[open-redirect]]
- [[auth-flaws]]
- [[session-management]]
- [[jwt-attacks|JWT Attacks]]
- [[token-lifecycle|Token Lifecycle]]

## Referencias

- **Fundamental:** RFC 9700 OAuth 2.0 Security Best Current Practice — https://datatracker.ietf.org/doc/html/rfc9700
- **Testing / Lab:** PortSwigger OAuth authentication — https://portswigger.net/web-security/oauth
- **Fundamental:** OWASP Authentication Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
