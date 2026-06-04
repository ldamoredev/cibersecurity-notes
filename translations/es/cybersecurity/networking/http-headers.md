---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - http
  - headers
sources: []
---

# Headers HTTP

## Definición
Los headers HTTP son campos de metadata nombrados en las requests y responses que le dicen a clientes, servidores, proxies, cachés y navegadores cómo interpretar el mensaje. Cargan señales de ruteo, identidad, estado, contenido, caché y política del navegador.

## Por qué importa
Los headers son la capa de dirección de la seguridad HTTP. El body puede cargar el dato de negocio, pero los headers deciden de quién parece venir la request, qué host/path/protocolo cree el backend que se usó, si una response puede cachearse, si un navegador puede exponer una response cross-origin y cómo debe interpretarse el contenido.

La lección recurrente: **los headers no son metadata neutral**. Son inputs de múltiples parsers y motores de política independientes.

Esta nota es dueña de la semántica de headers. [[http-messages|Mensajes HTTP]] es dueña del framing crudo del mensaje; [[client-ip-trust|Confianza en la IP del cliente]] es dueña de la confianza en la IP forwarded; [[cookies-and-sessions|Cookies y sesiones]] es dueña del estado `Set-Cookie` / `Cookie`; [[caching-and-security|Caché y seguridad]] es dueña del comportamiento de clave de caché.

## Cómo funciona
Todo header tiene tres propiedades que importan para la seguridad:

1. **Dirección.** Los headers de request van cliente/proxy → servidor. Los de response van servidor/proxy → cliente. Algunos son válidos en ambas direcciones pero significan cosas distintas.
2. **Alcance.** Los headers end-to-end están pensados para el destinatario final; los headers hop-by-hop aplican solo a una conexión y no deberían forwardearse más allá de ese hop.
3. **Intérprete.** Un navegador, CDN, WAF, reverse proxy, framework, caché o aplicación pueden leer cada uno el mismo header de forma distinta.

Request y response de ejemplo:

```http
GET /account HTTP/1.1
Host: app.example.com
Cookie: __Host-session=9f2a...
Authorization: Bearer eyJ...
X-Forwarded-For: 203.0.113.42
Origin: https://app.example.com
Accept: text/html
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Cache-Control: no-store
Set-Cookie: __Host-session=9f2a...; Path=/; Secure; HttpOnly; SameSite=Lax
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; frame-ancestors 'none'
```

Los mismos bytes cargan al menos cinco significados de seguridad: identidad, estado, ruteo, comportamiento de caché y política del navegador.

El bug suele vivir donde un componente trata un header como autoritativo aunque otro componente pueda proveer, transformar, omitir, duplicar o ignorar el mismo header.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- **headers de ruteo:** `Host`, `X-Forwarded-Host`, `Forwarded`, `X-Original-URL`, `X-Rewrite-URL`
- **headers de identidad:** `Authorization`, `Cookie`, `X-Forwarded-For`, `X-Real-IP`, `True-Client-IP`
- **headers de estado:** `Set-Cookie`, `Cookie`, validadores de caché, `Origin` / `Referer` adyacentes a CSRF
- **interpretación de contenido:** `Content-Type`, `Content-Length`, `Transfer-Encoding`, `Content-Encoding`, `Accept`
- **política del navegador:** `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `Referrer-Policy`, headers de CORS
- **comportamiento de caché:** `Cache-Control`, `Vary`, `ETag`, `Age`, `Surrogate-Control`, headers de estado de caché específicos del CDN
- **rarezas de normalización:** headers duplicados, diferencias de casing, espacio en blanco, valores unidos por coma, variantes agregadas-por-proxy vs provistas-por-cliente

## Variantes y bypasses
Las fallas de seguridad de headers HTTP caen en **6 clases semánticas**. Esta taxonomía es más útil que memorizar nombres de header individuales.

### 1. Headers de identidad y autorización
`Cookie` y `Authorization` prueban la identidad de la aplicación solo si el servidor los valida correctamente. Los headers de identidad forwarded como `X-Forwarded-For` no prueban nada salvo que el camino de red sea confiable. Headers de auth duplicados o en conflicto pueden producir desacuerdo proxy/backend.

### 2. Headers de ruteo y origen
`Host`, `Forwarded`, `X-Forwarded-Host`, `X-Forwarded-Proto` y los headers de rewrite influyen en la generación de URLs, el ruteo de virtual-host, los links de reset de contraseña y el comportamiento de redirect interno. Si el backend confía en headers de ruteo provistos por el atacante, siguen la inyección de host-header y los bugs de proxy-bypass.

### 3. Headers de estado y cookies
`Set-Cookie` y `Cookie` son especiales porque los navegadores los guardan y reproducen automáticamente. Su seguridad depende de atributos, alcance, reglas de prefijo y transporte. [[cookies-and-sessions|Cookies y sesiones]] es dueña de la profundidad completa.

### 4. Headers de interpretación de contenido
`Content-Type`, `Content-Encoding`, `Content-Length` y `Transfer-Encoding` le dicen a los parsers cómo leer los bytes. El desacuerdo acá lleva a XSS vía confusión de MIME, request smuggling vía framing del body, huecos de validación de upload y parseo de API roto.

### 5. Headers de control de caché
`Cache-Control`, `Vary`, `ETag` y los headers específicos del CDN deciden si la response de un usuario puede volverse la response de otro. Cualquier header que el origin lea pero que la caché no incluya en la clave es un input candidato a cache-poisoning.

### 6. Headers de política del navegador
CSP, HSTS, CORS, `X-Frame-Options`, `Permissions-Policy` y `Referrer-Policy` modelan lo que los navegadores permiten. Estos headers reducen la explotabilidad cuando son correctos pero a menudo se malentienden como reemplazos de la validación o autorización del lado del servidor.

## Impacto
Ordenado aproximadamente por severidad:

- **Bypass de autenticación o autorización.** `Authorization` en conflicto, headers forwarded confiados o headers de ruteo pueden hacer que el backend crea que una request vino de un camino o identidad privilegiada.
- **Request smuggling y confusión de parser.** `Content-Length`, `Transfer-Encoding`, headers duplicados y rarezas de espacio en blanco pueden hacer que dos componentes parseen requests distintas.
- **Cache poisoning / fugas de caché sensibles.** `Cache-Control` faltante, `Vary` débil o headers sin clave pueden exponer contenido personalizado o controlado por el atacante.
- **Amplificación del impacto de XSS.** CSP faltante, `Content-Type` equivocado o responses sniffables amplían los caminos de ejecución del lado del cliente.
- **CSRF y exposición de datos cross-origin.** `SameSite` débil, CORS permisivo o mal manejo de `Origin` deja que el contexto del navegador haga demasiado.
- **Confusión de frontera de confianza.** Los headers inyectados por el proxy se vuelven indistinguibles de los provistos por el cliente salvo que se sobrescriban y validen en la frontera.

## Detección y defensa
Ordenado por efectividad:

1. **Definí qué componente es dueño de cada header relevante para la seguridad.**
   El edge debería ser dueño de los headers de forwarding, protocolo e IP de cliente. La aplicación debería ser dueña de la validación de auth/sesión y la autorización de negocio. Los headers de política del navegador deberían emitirse deliberadamente por la app o el edge, no accidentalmente por los defaults del framework. La propiedad previene que dos componentes acepten silenciosamente señales en conflicto.

2. **Sobrescribí los headers entrantes no confiables en las fronteras de confianza.**
   Los reverse proxies deben sobrescribir, no agregar ni preservar, `X-Forwarded-*`, `Forwarded` y los headers de identidad/ruteo relacionados. Los backends deberían confiar en esos headers solo desde rangos de origen de proxy conocidos. Esto elimina la falla común de "el atacante proveyó un header que la app creía que solo el proxy podía setear".

3. **Rechazá headers críticos malformados, ambiguos y duplicados.**
   Fallá cerrado ante `Host` duplicado, `Content-Length` / `Transfer-Encoding` en conflicto, terminaciones de línea inválidas, nombres de header con espacio en blanco y headers de auth duplicados. La ambigüedad es donde vive el desacuerdo de parsers.

4. **Emití política de caché explícita para responses sensibles.**
   Usá `Cache-Control: no-store` para páginas autenticadas y responses de API sensibles. Al cachear variantes públicas, hacé que `Vary` coincida con cada header de request que cambia la response. Las cachés no pueden proteger datos que no se les dijo que eran privados.

5. **Seteá los headers de política del navegador como defensa en profundidad.**
   HSTS, CSP, `frame-ancestors` o `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy` reducen la explotabilidad en los navegadores. Van después de la corrección del lado del servidor porque restringen clientes en vez de arreglar autorización rota.

6. **Normalizá y logueá el valor interpretado, no solo el header crudo.**
   Los logs deberían registrar tanto las señales crudas donde sea útil como el valor que la aplicación realmente usó: IP de cliente percibida, host seleccionado, esquema de auth, content type, estado de caché. Esto hace visible el desacuerdo proxy/backend durante el testing y los incidentes.

### Qué no funciona como defensa primaria

- **Agregar headers de seguridad mientras se dejan los bugs del lado del servidor intactos.** CSP no arregla los sinks de XSS, CORS no autoriza usuarios, HSTS no vuelve seguro el HTTP del origin y `X-Frame-Options` no protege los endpoints que cambian estado.
- **Confiar en un header porque "el navegador lo setea".** `Origin`, `Referer`, `User-Agent` y la mayoría de los headers de request pueden estar ausentes, ser forjados por clientes no-navegador o transformados por proxies. Tratalos como señales con restricciones, no verdad de base.
- **Hacer blocklist de nombres de header malos.** Los atacantes usan variantes: casing distinto, headers duplicados, nombres legacy, `Forwarded` vs `X-Forwarded-*`, espacio en blanco, listas unidas por coma y alias específicos del framework.
- **Asumir que el framework ve lo que vio el edge.** CDNs, WAFs, proxies y load balancers normalizan los headers antes de que la aplicación los lea. Testeá la cadena completa.
- **Confiar en los headers de response para secretos.** Los headers son visibles para los clientes y a menudo para logs/proxies. No pongas secretos bearer ni detalles internos sensibles en headers custom.

## Labs prácticos
Corré esto contra sistemas que sean tuyos o que estés autorizado a testear. `curl`, `openssl`, `nc` y `rg` estándar cubren lo básico.

### Inventariar los headers de seguridad de la response

```bash
curl -skI https://app.example.com/ | rg -i \
  '^(strict-transport-security|content-security-policy|x-frame-options|frame-options|referrer-policy|permissions-policy|cache-control|vary|content-type|set-cookie):'
```

Buscá HSTS faltante en sitios HTTPS, CSP faltante o débil, protección de frame ausente, páginas autenticadas cacheables y atributos de cookie.

### Comparar headers de caché públicos y autenticados

```bash
# Página pública
curl -skI https://app.example.com/ | rg -i '^(cache-control|vary|etag|age|x-cache|cf-cache-status):'

# Página autenticada con un cookie jar
curl -sk -b /tmp/app.cookies -I https://app.example.com/account | \
  rg -i '^(cache-control|vary|etag|age|x-cache|cf-cache-status):'
```

Esperado: las responses autenticadas o personalizadas no deberían ser guardadas por cachés compartidas.

### Sondear el manejo de host y forwarded-host

```bash
curl -skI https://app.example.com/reset \
  -H 'Host: evil.example' \
  -H 'X-Forwarded-Host: evil.example' \
  -H 'X-Forwarded-Proto: http'
```

Vigilá redirects, URLs absolutas, links de reset de contraseña en cuentas de prueba y links canónicos generados. Un backend que refleja host/proto controlado por el atacante tiene un bug de confianza de ruteo.

### Sondear la confianza en headers de IP de cliente

```bash
curl -skI https://app.example.com/admin \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'X-Real-IP: 127.0.0.1' \
  -H 'Forwarded: for=127.0.0.1;proto=https;host=app.example.com'
```

Un cambio de status, contenido, bucket de rate-limit o log significa que el backend puede confiar en headers de forwarding provistos por el cliente. Ver [[client-ip-trust|Confianza en la IP del cliente]] para el flujo más profundo.

### Sondear headers críticos duplicados

```bash
# Host duplicado a través de HTTP crudo.
printf 'GET / HTTP/1.1\r\nHost: app.example.com\r\nHost: evil.example\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect app.example.com:443 -servername app.example.com 2>/dev/null

# Authorization duplicado a través de curl.
curl -skI https://app.example.com/api/me \
  -H 'Authorization: Bearer valid-test-token' \
  -H 'Authorization: Bearer invalid-test-token'
```

Esperado: los duplicados críticos deberían ser rechazados o manejados de forma consistente por cada hop.

### Inspeccionar los bytes exactos de header de request/response

```bash
curl -sk --trace-ascii /tmp/headers.trace https://app.example.com/login \
  -H 'X-Debug-Probe: header-lab' >/dev/null

rg -n '=> Send header|<= Recv header|X-Debug-Probe|Set-Cookie|Cache-Control' /tmp/headers.trace
```

Esto muestra lo que curl realmente envió y lo que el servidor realmente devolvió, sin la abstracción de la UI del navegador.

## Ejemplos prácticos
- Un backend construye URLs de reset de contraseña a partir de `X-Forwarded-Host`; un atacante inyecta su dominio y captura los tokens de reset.
- Un CDN solo usa la URL como clave mientras el origin varía la salida según `X-Forwarded-Host`, creando web cache poisoning.
- Un WAF rechaza `Transfer-Encoding: chunked`, pero el backend acepta `Transfer-Encoding:  chunked` con espacio extra.
- Una API acepta dos headers `Authorization`; el proxy valida uno mientras la app lee el otro.
- Un sitio setea CSP en las páginas HTML pero deja los endpoints de JSON o file-preview con `Content-Type` equivocado, habilitando bugs de interpretación del navegador.
- Una response incluye `Access-Control-Allow-Origin: *` con comportamiento credentialed en otro lado, revelando que la política de CORS no tiene dueño central.

## Notas relacionadas
- [[http-overview|Panorama de HTTP]] — ciclo de vida del protocolo y comportamiento a nivel de versión.
- [[http-messages|Mensajes HTTP]] — framing crudo del mensaje, headers duplicados y ambigüedad de parser.
- [[cookies-and-sessions|Cookies y sesiones]] — semántica del estado `Set-Cookie` y `Cookie`.
- [[client-ip-trust|Confianza en la IP del cliente]] — headers de identidad de IP forwarded.
- [[reverse-proxies|Reverse proxies]] — donde se introducen normalmente los headers de forwarding, normalización y confianza.
- [[caching-and-security|Caché y seguridad]] — `Cache-Control`, `Vary` y consecuencias de clave de caché.
- [[tls-https|TLS/HTTPS]] — HSTS y garantías de transporte.
- [[cybersecurity/web-security/cors-misconfiguration|Mala configuración de CORS]] — `Origin` y headers de response de CORS.
- [[cybersecurity/web-security/xss|XSS]] — restricciones de CSP y content-type.
- [[cybersecurity/web-security/csrf|CSRF]] — comportamiento de `Origin`, `Referer` y cookies.
- [[cybersecurity/security-playbooks/test-cors-behavior|Testear el comportamiento de CORS]]
- [[cybersecurity/security-playbooks/test-client-ip-spoofing|Testear el spoofing de IP de cliente]]

### Notas atómicas futuras sugeridas
- [[host-header-injection|Inyección de host-header]]
- [[security-response-headers|Headers de seguridad en la response]]
- [[content-type-sniffing|Content-type sniffing]]
- [[duplicate-header-resolution|Resolución de headers duplicados]]
- [[forwarded-header-spec|Spec del header Forwarded]]
- [[cache-control-semantics|Semántica de Cache-Control]]
- [[permissions-policy|Permissions-Policy]]

## Referencias
- **Foundational:** MDN HTTP headers — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
- **Foundational:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Mitigation:** OWASP HTTP Headers Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
