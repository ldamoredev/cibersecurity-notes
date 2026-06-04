---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - sessions
  - http
  - cookies
sources: []
---

# Cookies y sesiones

## Definición
Las cookies son estado cargado por headers HTTP que los navegadores guardan y adjuntan automáticamente a requests posteriores. Las sesiones son el modelo de continuidad del lado del servidor o respaldado por token que le permite a una aplicación reconocer "al mismo usuario" a través de requests HTTP que de otro modo no tienen estado.

## Por qué importa
La mayoría de los bugs de autenticación web se vuelven concretos en la capa de cookie/sesión. Un login puede ser correcto mientras el navegador igual envía una cookie de sesión al host equivocado, sobre el transporte equivocado, en el contexto cross-site equivocado, o después de que el logout debería haberla matado. Las cookies también son donde se encuentran la política del navegador, TLS, los reverse proxies, CSRF, XSS y la autorización.

La lección recurrente: **el estado HTTP no es una sola cosa**. Lo cargan las reglas del navegador, los atributos de cookie, el almacenamiento de sesión del servidor y las fronteras de confianza entre orígenes y subdominios.

Esta nota se queda en la capa de comportamiento de networking/protocolo. [[cybersecurity/web-security/session-management|Gestión de sesiones]] es dueña de las fallas de ciclo de vida del lado de la aplicación como fixation, rotación, logout y cambio de cuenta.

## Cómo funciona
El estado de sesión HTTP se mueve a través de **4 partes**:

1. **El servidor emite estado.** Una response incluye uno o más headers `Set-Cookie`.
2. **El navegador guarda estado.** El navegador decide si acepta la cookie según atributos como `Domain`, `Path`, `Secure`, `SameSite`, expiración y reglas de prefijo.
3. **El navegador adjunta estado automáticamente.** Las requests posteriores cuya URL y contexto coinciden con las reglas de la cookie cargan un header `Cookie:` sin JavaScript ni acción del usuario.
4. **El servidor interpreta estado.** La aplicación mapea el valor de la cookie a una fila de sesión del lado del servidor, un blob firmado/cifrado o un token como un JWT.

Response de login de ejemplo:

```http
HTTP/1.1 302 Found
Location: /account
Set-Cookie: __Host-session=9f2a...; Path=/; Secure; HttpOnly; SameSite=Lax
Set-Cookie: csrf=7c31...; Path=/; Secure; SameSite=Strict
Cache-Control: no-store
```

Request de seguimiento:

```http
GET /account HTTP/1.1
Host: app.example.com
Cookie: __Host-session=9f2a...; csrf=7c31...
```

El navegador no "logueó" al usuario; solo reprodujo estado bajo reglas que coinciden. La aplicación todavía tiene que validar ese estado y autorizar cada acción.

El bug suele vivir en la brecha entre lo que el navegador tiene permitido enviar y lo que la aplicación asume que ese envío significa.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- cada header `Set-Cookie` en login, logout, reset de contraseña, callback de OAuth, MFA, cambio de cuenta y elevación de admin
- si las cookies sensibles usan `Secure`, `HttpOnly`, `SameSite`, `Domain`/`Path` angostos y preferentemente el prefijo `__Host-`
- si los IDs de sesión rotan después del login, cambio de privilegio y reset de contraseña
- si el logout invalida el estado del lado del servidor o solo borra la cookie del navegador
- si los subdominios pueden setear o ensombrecer las cookies del dominio padre
- si las requests cross-site cargan cookies de formas que importan para [[cybersecurity/web-security/csrf|CSRF]]
- si XSS puede leer tokens o solo actuar con cookies ambientales
- si las responses que cargan datos de sesión usan `Cache-Control: no-store`

## Variantes y bypasses
Las fallas de cookie/sesión caen en **6 clases prácticas**. Tener estas en memoria de trabajo basta para triajear la mayoría de los hallazgos de estado de sesión.

### 1. Omisión de atributos
La cookie existe pero le faltan atributos protectores. `Secure` faltante permite fuga en texto plano en caminos HTTP. `HttpOnly` faltante deja que JavaScript lea el valor tras XSS. `SameSite` faltante o laxo aumenta la exposición a CSRF. Estos flags no reemplazan la autorización del lado del servidor, pero bajan el radio de explosión de otros bugs.

### 2. Errores de alcance
`Domain=.example.com` deja que los subdominios participen del mismo namespace de cookie. Si algún subdominio es más débil, comprometido o propenso a takeover, puede setear una cookie que ensombrece la real. `Path` no es una frontera de autorización; solo controla el comportamiento de envío del navegador.

### 3. Bypass o ausencia de reglas de prefijo
`__Secure-` requiere `Secure`. `__Host-` requiere `Secure`, sin `Domain` y `Path=/`. El prefijo `__Host-` es útil porque hace estructuralmente más difícil el ensombrecimiento de cookies de dominio amplio. El bypass es simple: las aplicaciones a menudo no usan los prefijos, o aceptan cookies de fallback con nombres más débiles.

### 4. Session fixation
La aplicación acepta un ID de sesión antes de la autenticación y mantiene el mismo ID después del login. Si un atacante puede plantar o predecir la sesión pre-auth, el login exitoso de la víctima ata la identidad a un estado conocido por el atacante.

### 5. Invalidación rota
Logout, reset de contraseña, deshabilitación de cuenta o reset de MFA borra la cookie del navegador pero deja la sesión del lado del servidor válida. Esto crea "sesiones zombie" que siguen funcionando desde otro navegador o un cookie jar robado.

### 6. Confusión de tokens sin estado
Los JWTs o cookies firmadas remueven el lookup de sesión del servidor pero no el problema de seguridad. Si la revocación, rotación, expiración, audiencia y manejo de clave de firma son débiles, el sistema se vuelve más difícil de invalidar que un almacén de sesión normal.

## Impacto
Ordenado aproximadamente por severidad:

- **Account takeover o reuso persistente de sesión.** Los IDs de sesión robados o fijados siguen autenticando al atacante.
- **Abuso de acción de admin.** XSS o CSRF pueden actuar a través de cookies ambientales incluso cuando el valor de la cookie no está directamente expuesto.
- **Compromiso cross-subdominio.** Un subdominio hermano más débil puede setear, ensombrecer o influir en las cookies del dominio padre.
- **Fuga de datos sensibles.** Cookies enviadas por HTTP, páginas de cuenta cacheadas o logs que capturan headers `Cookie:` exponen material de sesión.
- **Respuesta a incidentes débil.** La invalidación rota significa que los cambios de contraseña y el logout no remueven realmente el acceso del atacante.
- **Debugging de auth confuso.** Múltiples cookies con el mismo nombre pero distinto alcance hacen el comportamiento dependiente del camino y difícil de razonar.

## Detección y defensa
Ordenado por efectividad:

1. **Usá identificadores de sesión del lado del servidor para la auth del navegador y rotalos en los cambios de confianza.**
   Un ID de sesión opaco y aleatorio respaldado por un almacén del lado del servidor es más fácil de revocar, inspeccionar y rotar que un token autocontenido de larga vida. Rotá en login, elevación de privilegio, reset de contraseña y recuperación de cuenta para que el estado plantado por el atacante o viejo no pueda volverse estado autenticado.

2. **Seteá atributos de cookie fuertes por defecto.**
   Las cookies de auth sensibles deberían ser `Secure; HttpOnly; SameSite=Lax` o `Strict` donde el flujo lo permita. `Secure` protege el transporte, `HttpOnly` reduce el robo de tokens tras XSS y `SameSite` reduce el riesgo de CSRF por cookie ambiental. Estos flags son baratos, visibles y previenen muchas fallas compuestas.

3. **Preferí `__Host-` para las cookies de sesión primarias.**
   `__Host-session=...; Secure; Path=/; HttpOnly; SameSite=Lax` sin `Domain` hace la cookie host-only y previene que los subdominios hermanos seteen la misma cookie para el dominio padre. Esto aborda directamente el ensombrecimiento de subdominio y el riesgo adyacente a takeover.

4. **Mantené la vida y la invalidación de la sesión controladas por el servidor.**
   Expirá las sesiones en el servidor, no solo a través de `Max-Age` / `Expires` del navegador. Logout, reset de contraseña, deshabilitación de cuenta y actividad sospechosa deberían revocar las sesiones activas del lado del servidor. El borrado en el navegador es limpieza de interfaz de usuario; la invalidación del servidor es el control de seguridad.

5. **Tratá CSRF por separado de los flags de cookie.**
   `SameSite=Lax` ayuda, pero los flujos de login complejos, los callbacks de OAuth, los navegadores viejos, las navegaciones top-level cross-site y las integraciones `SameSite=None` todavía necesitan tokens CSRF explícitos o chequeos de origen. El comportamiento de cookie es una capa, no toda la defensa.

6. **No caches las responses personalizadas.**
   Las responses de cuenta, perfil, admin, facturación y API que dependen de cookies deberían usar `Cache-Control: no-store`. Los proxies compartidos y las cachés del navegador no conocen tu modelo de autorización salvo que los headers se lo digan.

7. **Logueá eventos de sesión sin loguear secretos.**
   Registrá la creación, rotación, revocación y reuso sospechoso de sesión. Nunca loguees headers `Cookie:` crudos ni IDs de sesión. Los logs deberían ayudar a reconstruir el abuso sin volverse una fuga de token de sesión.

### Qué no funciona como defensa primaria

- **Confiar en `HttpOnly` como arreglo de XSS.** `HttpOnly` frena que JavaScript lea el valor de la cookie; no frena que JavaScript malicioso haga requests autenticadas same-origin con la cookie adjuntada automáticamente.
- **Tratar `SameSite` como protección CSRF completa.** `SameSite` tiene casos borde de navegador y de flujo. Mantené tokens anti-CSRF o validación de origen para operaciones que cambian estado.
- **Usar `Path` como autorización.** `Path=/admin` controla cuándo el navegador envía una cookie; no frena que una ruta del servidor acepte otra cookie ni que otro endpoint haga trabajo de admin.
- **Borrar la cookie sin revocar la sesión del servidor.** El atacante puede ya tener una copia. La invalidación del lado del servidor es el control.
- **Guardar roles, balances o permisos en cookies sin firmar legibles por el cliente.** El navegador no es una frontera de base de datos. Si el cliente puede manipular el estado, el servidor debe verificar la integridad y la autorización de forma independiente.

## Labs prácticos
Corré esto solo contra sistemas que sean tuyos o que estés autorizado a testear. `curl`, las DevTools del navegador y opcionalmente `jq` alcanzan.

### Inspeccionar la postura de `Set-Cookie`

```bash
# Mostrar cada cookie que el servidor intenta setear durante el login o un redirect protegido.
curl -skI https://app.example.com/login | rg -i '^set-cookie|^location|^cache-control'

# Seguir redirects y mantener los headers visibles.
curl -skIL https://app.example.com/login | rg -i '^set-cookie|^location|^cache-control'
```

Buscá: `Secure` faltante, `HttpOnly` faltante, `SameSite` faltante/laxo, `Domain` amplio, `Path` amplio, sin `Cache-Control: no-store` en páginas autenticadas.

### Persistir y reproducir una sesión con curl

```bash
# Capturar cookies de un flujo tipo login.
curl -sk -c /tmp/app.cookies https://app.example.com/login >/dev/null

# Reproducirlas a una página protegida.
curl -sk -b /tmp/app.cookies -i https://app.example.com/account | sed -n '1,25p'

# Inspeccionar lo que curl guardó.
cat /tmp/app.cookies
```

Esto muestra qué cookies son host-only, cuáles tienen un `Domain` y a qué paths aplican.

### Comparar la rotación de sesión pre-login y post-login

```bash
# 1. Obtener una cookie pre-auth.
curl -sk -c /tmp/pre.cookies -I https://app.example.com/login | rg -i '^set-cookie'

# 2. Logueate manualmente en un navegador o con una cuenta de prueba autorizada.
# 3. Exportá/copiá el valor de la cookie de sesión post-login desde las DevTools.

# Comparar si el ID de sesión primario cambió a través de la frontera de confianza.
cat /tmp/pre.cookies
```

Si el mismo identificador de sesión primario sobrevive al login, investigá session fixation.

### Testear el alcance de la cookie entre subdominios hermanos

```bash
# ¿Un host hermano setea una cookie de dominio padre?
curl -skI https://staging.example.com/ | rg -i '^set-cookie'

# Una forma riesgosa se ve así:
# Set-Cookie: session=...; Domain=.example.com; Path=/; Secure
```

Si un subdominio de baja confianza puede setear cookies `.example.com` adyacentes a auth, revisá el alcance de `Domain` y preferí `__Host-` para la sesión real.

### Verificar que el logout invalida la sesión del lado del servidor

```bash
# Guardar primero un cookie jar de sesión conocido-bueno.
curl -sk -b /tmp/app.cookies -c /tmp/app.cookies https://app.example.com/logout >/dev/null

# Intentar reproducir el jar viejo después del logout.
curl -sk -b /tmp/app.cookies -i https://app.example.com/account | sed -n '1,30p'
```

Esperado: redirect al login o `401/403`. Si la cookie vieja todavía funciona desde otro cliente, el logout solo está borrando el estado del navegador.

### Chequear el comportamiento de envío cross-site en un navegador

Usá DevTools → Application → Cookies y DevTools → Network:

```txt
1. Abrí la tabla de cookies para app.example.com.
2. Registrá SameSite, Secure, HttpOnly, Domain, Path.
3. Dispará una navegación cross-site o un formulario de lab CSRF autorizado.
4. Chequeá si el header Cookie fue adjuntado.
```

La observación en el navegador importa porque `curl` no implementa la política same-site del navegador.

## Ejemplos prácticos
- Una response de login setea `session=...; Domain=.example.com`; un subdominio de staging comprometido ensombrece la cookie para la app padre.
- Un flujo de reset de contraseña cambia la contraseña pero no revoca las sesiones existentes, así que una cookie robada sigue funcionando.
- Un payload de XSS no puede leer una cookie `HttpOnly` pero igual puede `fetch('/admin/users/delete')` con la sesión ambiental del navegador.
- Una página de facturación se sirve con `Cache-Control: public`; un proxy compartido guarda la página de cuenta de otro usuario.
- Un callback de OAuth requiere `SameSite=None; Secure` para un flujo de terceros, pero el resto de la app asume que todas las cookies están protegidas same-site.

## Notas relacionadas
- [[http-overview|Panorama de HTTP]] — ciclo de vida de la request y modelo de interacción navegador/servidor.
- [[http-messages|Mensajes HTTP]] — forma cruda del mensaje `Set-Cookie` y `Cookie`.
- [[http-headers|Headers HTTP]] — semántica más amplia de headers sobre la que se construyen las cookies.
- [[tls-https|TLS/HTTPS]] — `Secure`, HSTS y garantías de transporte para las cookies.
- [[cybersecurity/web-security/session-management|Gestión de sesiones]] — vulnerabilidades de ciclo de vida de sesión del lado de la aplicación.
- [[cybersecurity/web-security/csrf|CSRF]] — las cookies automáticas del navegador son la razón por la que existe CSRF.
- [[cybersecurity/web-security/xss|XSS]] — XSS interactúa con `HttpOnly`, las cookies ambientales y el almacenamiento de tokens.
- [[caching-and-security|Caché y seguridad]] — las responses personalizadas respaldadas por cookies no deben cachearse incorrectamente.
- [[cybersecurity/security-playbooks/inspect-session-handling|Inspeccionar el manejo de sesiones]]

### Notas atómicas futuras sugeridas
- [[cookie-prefixes-host-secure|Prefijos de cookie __Host- / __Secure-]]
- [[samesite-cookie-behavior|Comportamiento de la cookie SameSite]]
- [[session-fixation|Session fixation]]
- [[session-rotation|Rotación de sesión]]
- [[logout-invalidation|Invalidación en el logout]]
- [[csrf-token-design|Diseño de tokens CSRF]]

## Referencias
- **Foundational:** MDN Set-Cookie header — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie
- **Foundational:** OWASP Session Management Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
- **Testing / Lab:** OWASP WSTG Session Management Testing — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/
- **Testing / Lab:** PortSwigger CSRF topic — https://portswigger.net/web-security/csrf
