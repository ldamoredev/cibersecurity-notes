---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-27
tags:
  - cybersecurity
  - networking
  - http
  - foundational
sources: []
---

# Panorama de HTTP

## Definición
HTTP (Hypertext Transfer Protocol) es el protocolo de aplicación request/response que transporta la abrumadora mayoría del tráfico web y de APIs. El formato de wire es basado en texto en HTTP/1.x y con framing binario en HTTP/2 y HTTP/3. El protocolo no impone semántica — la transporta. Toda vulnerabilidad web se presenta en última instancia como una transacción HTTP cuyas partes fueron parseadas, confiadas o ruteadas de una forma que el diseñador no pretendía.

## Por qué importa
HTTP es el sustrato sobre el que se apoya todo hallazgo de web-security y api-security. Importa porque:

- **Todo exploit web es una transacción HTTP.** XSS, SQLi, CSRF, SSRF, IDOR, smuggling, deserialización — todas son vulnerabilidades en cómo las partes de una request HTTP se atan al comportamiento del backend.
- **El estado vive en los headers.** Auth, sesiones, cookies, CORS, CSP, directivas de caché, identidad forwarded — cada uno es un header adjunto a una transacción HTTP.
- **Las fronteras de confianza viven en las costuras del parser.** La traducción de reverse-proxy, el request smuggling y el cache poisoning viven todos donde dos parsers HTTP discrepan sobre los mismos bytes.
- **Es la meta-habilidad.** Sin un modelo de HTTP que el lector pueda sostener en memoria de trabajo, toda nota de nivel superior se vuelve pattern matching sin comprensión.

Esta nota se queda a nivel del modelo del protocolo. [[http-messages|Mensajes HTTP]] es dueña de la profundidad sobre el formato de wire y las reglas de framing del parser. [[http-headers|Headers HTTP]] es dueña de la profundidad sobre qué campos de header realmente dirigen el comportamiento de seguridad.

## Cómo funciona
Una transacción HTTP tiene **5 etapas**. Cada etapa es una frontera de confianza; cada una puede ser manipulada o malinterpretada de forma independiente.

1. **Resolver el objetivo** — el cliente busca el host (DNS) y elige un puerto (por defecto 80 para HTTP, 443 para HTTPS). Los hijacks de DNS aterrizan acá. Ver [[dns-resolution|Resolución DNS]].
2. **Establecer el transporte** — handshake de tres vías de TCP; handshake de TLS si es HTTPS; la conexión puede reusarse para muchas requests (keep-alive en HTTP/1.1, streams multiplexados en HTTP/2/3). Los ataques de MITM y downgrade aterrizan acá.
3. **Enviar la request** — método + URI + versión + headers + (opcional) body. Los bytes de wire son exactamente lo que parsea el próximo hop.
4. **El servidor procesa** — parsea, rutea, autoriza, ejecuta, renderiza. *Cada paso es forjable de forma independiente a partir de los bytes de la request.* La mayoría de las vulnerabilidades de aplicación viven en esta etapa.
5. **Devolver la response** — status code + headers + (opcional) body. La conexión puede persistir o cerrarse.

Una request HTTP/1.1 mínima:

```http
GET /users/42 HTTP/1.1
Host: api.example.com
Accept: application/json
Cookie: session=abc123

```

Una response mínima:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 27
Cache-Control: private

{"id":42,"name":"Carlos"}
```

Toda request HTTP carga **4 señales relevantes para la confianza**. Tratá cada una como forjable hasta verificarla:

- **Identidad** — `Cookie`, `Authorization`, certificados de cliente, mTLS. *Lo que el cliente dice ser.*
- **Intención** — método + URI. *Qué quiere que se haga el cliente, sobre qué.*
- **Contexto / estado** — `Host`, `Origin`, `Referer`, `X-Forwarded-*`, `User-Agent`. *Afirmaciones del navegador y el proxy sobre el entorno.*
- **Payload** — los bytes del body, interpretados según `Content-Type`.

El bug rara vez está en HTTP mismo. El bug está en **qué señal confía el backend y cómo viaja esa confianza a través de los hops**.

## Técnicas / patrones
Qué miran los testers y cómo sondean:

- **Leé siempre los headers de la response, no solo el body.** Los flags de `Server`, `Via`, `X-Cache`, `Content-Type`, `Content-Security-Policy`, `Set-Cookie` revelan el stack y su postura de seguridad antes de cualquier test específico de vuln.
- **Los status codes filtran arquitectura.** 401 vs 403 vs 404 filtran sobre el layering de autenticación-vs-autorización y la enumeración de recursos. Un 500 con un stack trace filtra la versión del framework. Los patrones 502/504 revelan fronteras de proxy.
- **Establecé primero la versión del protocolo.** El handshake de ALPN/TLS revela soporte de h2/h3. El comportamiento — y la superficie de ataque — diverge materialmente entre 1.1, 2 y 3.
- **Leé el wire, no el framework.** Los frameworks normalizan, ocultan y mienten. `curl -v --trace-ascii -` y `openssl s_client` son la única verdad de base.
- **Buscá endpoints olvidados.** `OPTIONS *`, `TRACE`, `PROPFIND`, `/.well-known/`, `/debug/`, `/metrics` — la superficie de método/URI de HTTP es más amplia que la API documentada.

## Variantes y bypasses
El protocolo tiene **4 versiones desplegadas**, cada una con diferencias relevantes para la seguridad. Saber qué versión habla cada hop de la cadena es el primer paso en cualquier análisis de producción.

### HTTP/1.0
Conexión-por-request por defecto. No requiere header `Host` (multi-hosting imposible). Mayormente histórico, pero todavía aparece en servicios legacy y algunas herramientas CLI. Vale reconocerlo en el wire porque elimina toda la familia de confusión de virtual-host.

### HTTP/1.1
Formato de wire basado en texto, terminaciones de línea CRLF, conexiones persistentes (keep-alive) por defecto. El pipelining fue especificado pero mayormente deshabilitado en la práctica. **Framing del body vía `Content-Length` *o* `Transfer-Encoding: chunked`** — este either-or es la fuente de toda la clase de vulnerabilidad de request smuggling. Ver [[http-messages|Mensajes HTTP]] y [[request-smuggling|Request smuggling]].

### HTTP/2
Framing binario sobre TCP+TLS. Streams multiplexados sobre una sola conexión. Compresión de headers (HPACK). Los frames con prefijo de longitud eliminan la ambigüedad textual, lo que mata la mayor parte del smuggling en el front-end. **El downgrade HTTP/2 → HTTP/1.1 entre el proxy y el origin reintroduce toda la superficie de smuggling** — el proxy habla h2 con el cliente y h1 con el backend, y la capa de traducción se vuelve un hotspot de desajuste de parsers.

### HTTP/3
Framing binario sobre QUIC, que está sobre UDP. TLS 1.3 nativo. Migración de conexión: la identidad de la conexión ya no es una 4-tupla `(src-IP, src-port, dst-IP, dst-port)`, lo que complica los controles basados en IP de origen (rate limiting, allowlists de IP). Las reglas de firewalling de UDP difieren de las de TCP — un deployment que filtraba HTTP/1.1 limpio puede estar abierto de par en par en h3.

## Impacto
El malentendido de HTTP es **meta-impactante** — amplifica cada otra clase de vulnerabilidad:

- Malinterpretar `Host` habilita la inyección de host-header (envenenamiento de URL de reset de contraseña, confusión de virtual-host).
- Malinterpretar `Content-Type` habilita bugs de type-confusion en deserialización o upload.
- Malinterpretar `Cache-Control` y `Vary` habilita cache poisoning y cache deception.
- Malinterpretar la terminación de TLS habilita la fuga de credenciales a un hop de backend en texto plano.
- Malinterpretar el reuso de conexión habilita el request smuggling.
- Malinterpretar los redirects (semántica del header `Location`) habilita open-redirect y robo de flujos OAuth.
- Malinterpretar `Origin` vs `Referer` habilita malas configuraciones de CORS y CSRF.
- Malinterpretar la idempotencia de los métodos HTTP deja que `GET` cambie estado y se vuelva tanto CSRF-able como accidentalmente cacheable.

## Detección y defensa
Las defensas acá son defensas de *postura operativa* — guía genérica que hace tratables las vulnerabilidades de capa de aplicación. Las defensas específicas de cada clase de vuln viven en sus propias notas.

1. **Leé tu propio protocolo en el wire.**
   `curl -v` a tu tráfico de producción. Asegurate de que las requests y responses que creés enviar son las que realmente están en el wire. Los frameworks abstraen HTTP; esa abstracción es exactamente lo que hace invisibles las vulnerabilidades a nivel de wire desde dentro del código.

2. **Tratá cada header como dato de cliente no confiable salvo que lo verifique el camino de red.**
   Esta es la única regla durable para la traducción de confianza. No "sanitizamos XFF" — *la conexión tiene que venir de una IP de proxy conocida*, y solo entonces el dato del header es informativo. Ver [[client-ip-trust|Confianza en la IP del cliente]] para la versión completa.

3. **Especificá `Content-Type`, `Content-Length`, `Cache-Control` y `Vary` explícitamente.**
   Los defaults varían por framework, por versión y por middleware. La ambigüedad es superficie de ataque — tanto para confusión de parser como para confusión de clave de caché.

4. **Preferí HTTP/2 o HTTP/3 end-to-end donde controlás ambos extremos.**
   El framing con prefijo de longitud elimina la mayor clase individual de vulnerabilidades de HTTP/1.1 (smuggling, juegos de línea de header). El hop de downgrade h2 → h1 es el modo de falla a vigilar; mTLS-al-origin con h2 en todo el camino es la postura más fuerte.

5. **Hacé coincidir el comportamiento del parser entre hops.**
   La misma familia y versión de servidor web en ambos lados donde sea factible. La mayoría de los hallazgos de desync vienen de un lado siendo más permisivo que el otro sobre el mismo input. Ver [[reverse-proxies|Reverse proxies]] para la versión larga.

6. **Logueá el wire — versión, método, URI, status, longitud — en cada hop.**
   Cuando algo sale mal, el wire es la única verdad de base. Las líneas de log a nivel de framework son el valor que el framework eligió mostrarte, no lo que vio el parser.

### Qué no funciona como defensa primaria

- **"Usamos HTTPS".** TLS protege los bytes en tránsito. No protege la semántica de parseo en ninguno de los extremos. El smuggling, el cache poisoning, la forja de confianza de header y los ataques de Host-header ocurren todos *dentro* de una sesión HTTPS.
- **Leer las abstracciones del framework en vez del wire real.** Los objetos `request.headers` del framework son una *vista* del wire, post-normalización. Lo que sea que dijo el wire y el framework ocultó es exactamente la superficie de ataque.
- **Reglas de WAF afinadas para HTTP/1.1 frente a un backend h2.** Framing distinto significa reglas distintas; un WAF que hace pattern-matching de CRLF de línea de texto es ciego a los headers de frame de h2.
- **Confiar en que "los frameworks modernos vienen seguros por defecto".** Cada default está a un flag de config de ser inseguro, y el default de una versión distinta del framework rara vez es idéntico.

## Labs prácticos
`curl`, `openssl`, `dig` y `nc` estándar cubren lo básico.

### Inspeccionar headers, versión y TLS

```bash
# Ver headers de request y response; el modo verbose también muestra el resumen del handshake TLS
curl -v https://example.com 2>&1 | head -40

# Detectar soporte de HTTP/2 / HTTP/3 vía ALPN
openssl s_client -connect example.com:443 -servername example.com -alpn h2,http/1.1 </dev/null 2>/dev/null \
  | grep 'ALPN'

# Forzar HTTP/1.1 vs HTTP/2 vs HTTP/3 para comparar el comportamiento del servidor entre versiones
curl -sI --http1.1 https://example.com
curl -sI --http2   https://example.com
curl -sI --http3   https://example.com   # requiere curl compilado con HTTP/3
```

### Leer el wire directamente

```bash
# HTTP plano — hablale al servidor sin la normalización de curl
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | nc example.com 80

# HTTPS — la misma idea, con openssl s_client envolviendo el socket TCP
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect example.com:443 -servername example.com 2>/dev/null
```

### Sondear la superficie de métodos y endpoints

```bash
# Descubrimiento de métodos — muchos servidores exponen verbos no previstos
for m in GET HEAD OPTIONS PUT DELETE PATCH TRACE PROPFIND CONNECT; do
  printf '%-9s -> %s\n' "$m" "$(curl -sI -X "$m" -o /dev/null -w '%{http_code}' https://example.com/)"
done

# Endpoints de reconocimiento estándar
for path in /.well-known/security.txt /robots.txt /sitemap.xml /server-status \
            /metrics /debug /actuator/health /api/v1/openapi.json; do
  printf '%-32s -> %s\n' "$path" "$(curl -sI -o /dev/null -w '%{http_code}' "https://example.com$path")"
done
```

### Chequeo rápido de la semántica de status codes

```bash
# 401 vs 403 vs 404 — ¿una request no autenticada a un recurso protegido
# filtra su existencia (403 = existe, 404 = no existe)?
curl -sI https://example.com/admin -o /dev/null -w '%{http_code}\n'
curl -sI https://example.com/admin/users/1 -o /dev/null -w '%{http_code}\n'
```

## Ejemplos prácticos
- Una app detrás de un CDN HTTP/2 despliega un origin HTTP/1.1. El CDN serializa aguas arriba como HTTP/1.1 y la superficie de smuggling que h2 se suponía que eliminaba reaparece silenciosamente en el hop de downgrade.
- Una response de debug incluye `Server: gunicorn/19.6 Python/3.6` revelando una versión vulnerable del servidor web de Python. Una búsqueda pública de CVE se enciende de inmediato.
- Una API REST usa `GET /users/42/delete` para borrar usuarios. La acción ahora es CSRF-able desde cualquier tag de imagen y silenciosamente cacheable por cualquier intermediario.
- Un backend lee `request.headers['host']` para construir URLs de reset de contraseña. El proxy de frontend pasa `Host:` sin modificar. Un atacante envía `Host: evil.example` y los emails de reset de contraseña apuntan al atacante.
- Un servicio Go desplegado detrás de Cloudflare habla HTTP/3 al público pero no existía ninguna regla de firewall para UDP/443. La mitad del monitoreo del perímetro queda ciego.
- Un flujo OAuth redirige a `Location: https://evil.example/callback?code=...`. La app valida el redirect contra una allowlist sobre `Host` pero no sobre el header `Location` que genera. El código de autorización se filtra.

## Notas relacionadas
- [[http-messages|Mensajes HTTP]] — formato de wire y reglas de framing del parser; la pregunta "¿dónde termina esta parte?".
- [[http-headers|Headers HTTP]] — semántica de los headers que dirigen el comportamiento de seguridad.
- [[tls-https|TLS/HTTPS]] — confianza de capa de transporte, HSTS, manejo de certificados.
- [[reverse-proxies|Reverse proxies]] — traducción de confianza entre parsers HTTP.
- [[client-ip-trust|Confianza en la IP del cliente]] — la especialización de desacuerdo-de-confianza para los headers de IP forwarded.
- [[cookies-and-sessions|Cookies y sesiones]] — la capa de estado adjunta a HTTP vía `Set-Cookie`/`Cookie`.
- [[caching-and-security|Caché y seguridad]] — semántica de `Cache-Control` y `Vary`.
- [[dns-resolution|Resolución DNS]] — etapa 1 de toda transacción.
- [[cybersecurity/web-security/request-smuggling|Request smuggling]] — la clase canónica de ataque de desacuerdo-de-parser h1/h2.
- [[cybersecurity/web-security/cors-misconfiguration|Mala configuración de CORS]] — semántica del header `Origin`.
- [[cybersecurity/web-security/csrf|CSRF]] — idempotencia de métodos y confianza en `Origin`/`Referer`.

### Notas atómicas futuras sugeridas
- [[http-versions-comparison|Comparación de versiones de HTTP]]
- [[http3-quic-security|Seguridad de HTTP/3 y QUIC]]
- [[alpn-and-version-negotiation|ALPN y negociación de versión]]
- [[http-status-code-semantics|Semántica de los status codes HTTP]]
- [[http-method-semantics|Semántica de los métodos HTTP]]
- [[content-type-handling|Manejo de Content-Type]]
- [[connection-reuse-and-keep-alive|Reuso de conexión y keep-alive]]

## Referencias
- **Foundational:** MDN HTTP overview — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview
- **Foundational:** RFC 9110 (HTTP Semantics) — https://datatracker.ietf.org/doc/html/rfc9110
- **Foundational:** MDN HTTP request methods — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
