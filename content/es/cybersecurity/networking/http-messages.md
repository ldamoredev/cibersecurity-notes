---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-27
tags:
  - cybersecurity
  - networking
  - http
  - wire-format
  - parser
sources: []
---

# Mensajes HTTP

## Definición
Un mensaje HTTP es la unidad de datos intercambiada entre cliente y servidor — ya sea una *request* (enviada cliente → servidor) o una *response* (enviada servidor → cliente). En HTTP/1.x el mensaje es un flujo de texto con framing CRLF estricto; en HTTP/2 y HTTP/3 el mensaje es una secuencia de frames binarios que cargan campos lógicamente equivalentes. Esta nota se enfoca en el formato de mensaje de HTTP/1.1 porque ahí es donde viven las decisiones de parseo relevantes para la seguridad, y donde cada hop que habla HTTP/1.1 en una cadena moderna se ve forzado a tomarlas.

## Por qué importa
Muchas vulnerabilidades son invisibles desde el código de la aplicación y obvias desde el wire. La forma de un mensaje HTTP — *no la interpretación del framework* — es lo que proxies, WAFs, CDNs y el servidor de aplicación parsean cada uno de forma independiente. Tres cosas hacen esencial la fluidez a nivel de mensaje:

- **Todo exploit web en algún momento aflora como un mensaje malformado o ambiguo.** El smuggling, la inyección de headers, el cache poisoning, los ataques de host-header y muchos bugs de inyección CRLF son todos bugs de formato de mensaje.
- **Los frameworks mienten.** `request.headers` es una vista normalizada; el wire podría tener duplicados, casing raro o espacios extra que el framework silenciosamente unió o descartó. El bug suele vivir en la diferencia.
- **Dos parsers sobre los mismos bytes discrepan.** El reverse proxy + el backend parsean cada uno el mismo mensaje y pueden llegar a conclusiones distintas. Cada desacuerdo es una vulnerabilidad candidata. Ver [[reverse-proxies|Reverse proxies]] para el encuadre.

Esta nota se queda a nivel del *formato de mensaje*. [[http-overview|Panorama de HTTP]] es dueña de la profundidad sobre el ciclo de vida del protocolo y las diferencias de versión. [[request-smuggling|Request smuggling]] es dueña de la profundidad sobre explotar el desacuerdo de parsers. [[http-headers|Headers HTTP]] es dueña de la profundidad sobre los campos de header individuales.

## Cómo funciona
Todo mensaje HTTP/1.1 tiene **4 partes**:

1. **Start-line** — para una request, `<método> <request-target> HTTP/<versión>`. Para una response, `HTTP/<versión> <status-code> <reason-phrase>`.
2. **Sección de headers** — cero o más líneas `Name: Value`, una por línea terminada en CRLF.
3. **Línea vacía** — un único CRLF que separa los headers del body. Esta es la señal de framing.
4. **Body** (opcional) — bytes cuya longitud está determinada por los headers.

Una request:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: 31
Cookie: session=abc123

{"user":"carlos","password":"x"}
```

Los bytes entre la start-line y el primer CRLFCRLF son headers. Los bytes después del CRLFCRLF son el body. Todo es texto. Todo depende de que el parser coincida con el escritor sobre qué cuenta como un CRLF.

Todo parser HTTP/1.1 debe responder **3 preguntas de framing** para decodificar un mensaje. Casi toda la variación relevante para la seguridad vive en los desacuerdos sobre las respuestas:

1. **¿Dónde termina la start-line?** Primer CRLF. Sutilezas: LF solo, espacio en blanco al inicio, strings de versión HTTP raros, request-line sobredimensionada.
2. **¿Dónde termina la sección de headers?** Primera línea vacía (CRLFCRLF). Sutilezas: folding de línea de header (obsoleto pero todavía parseado por algunas implementaciones), líneas de header sin dos puntos, nombres de header con espacios, headers repetidos.
3. **¿Dónde termina el body?** Determinado por los headers, en esta prioridad:
   - `Transfer-Encoding: chunked` → el body es una secuencia de chunks `<size-hex>\r\n<bytes>\r\n` terminada por `0\r\n\r\n`.
   - si no, `Content-Length: N` → el body es exactamente N bytes.
   - si no (algunos métodos) → el body se extiende hasta el cierre de la conexión.
   - si no → no hay body.

La última pregunta es la que se rompe. **Dos parsers HTTP/1.1 dado el mismo mensaje pueden llegar a conclusiones distintas sobre dónde termina el body.** Ese es todo el sustrato del [[request-smuggling|request smuggling]]: cuando `Content-Length` y `Transfer-Encoding` están ambos presentes y un parser prefiere uno y el otro prefiere el otro, la conexión queda desincronizada.

El bug rara vez está en un solo parser. El bug está en el **desacuerdo entre dos parsers leyendo los mismos bytes**.

## Técnicas / patrones
Qué miran los testers:

- **Leé los mensajes con `curl -v --trace-ascii -` o `printf | nc` crudo.** La vista de `request.headers` del framework es una abstracción saneada; el wire es la verdad.
- **Buscá duplicación de headers.** `Host: a.com\r\nHost: b.com` — ¿cuál usa el proxy? ¿Cuál usa el backend? Distinto es explotable.
- **Mirá el espacio en blanco en los valores de header.** OWS al final, tabs embebidos, espacios al inicio — distintos parsers normalizan distinto. `Content-Length: 13 ` (espacio al final) vs `Content-Length:13` (sin espacio al inicio) vs `Content-Length :13` (espacio antes de los dos puntos, ilegal pero aceptado por algunos).
- **Buscá `Content-Length` y `Transfer-Encoding` juntos.** Aunque el mensaje sea sintácticamente válido en aislamiento, esta combinación *fuerza* al parser a elegir uno. Distintos parsers eligen distinto. Ver [[request-smuggling|request smuggling]].
- **Mirá las terminaciones de línea.** El RFC dice CRLF; algunos parsers aceptan LF solo; algunos aceptan CR solo. Un LF desnudo dentro de un valor de header es una primitiva de smuggling en parsers permisivos.
- **Buscá juegos de casing.** Los nombres de header son case-insensitive según el spec; algunos parsers pasan a minúscula, algunos preservan, algunos hashean. `transfer-encoding`, `Transfer-Encoding`, `TRANSFER-ENCODING` pueden no tratarse todos igual al normalizar para "¿está presente el chunked encoding?".

## Variantes y bypasses
Los mensajes HTTP/1.1 pueden ser ambiguos en el wire en **5 clases distintas**. Cada una es una superficie potencial de desacuerdo de parsers; en conjunto cubren el grueso de la superficie de ataque de formato de mensaje.

### 1. Ambigüedad de framing del body (CL vs TE)
`Content-Length` y `Transfer-Encoding: chunked` ambos presentes. El spec dice que gana `TE`, pero las implementaciones reales varían, especialmente cuando `TE` está malformado (`Transfer-Encoding: chunked\r\n` vs `Transfer-Encoding: x-chunked\r\n` vs `Transfer-Encoding: chunked, identity\r\n`). El desacuerdo es la superficie de smuggling. Dueña de la profundidad: [[request-smuggling|request smuggling]].

### 2. Canonicalización del nombre de header
Sensibilidad al casing, espacio en blanco al inicio/final, NULs embebidos, folding de línea de header (`obs-fold` según RFC 7230 — obsoleto pero todavía aceptado por algunos parsers vía líneas de continuación). Dos parsers viendo los mismos bytes pueden producir conjuntos distintos de nombres de header, lo que basta para saltearse cualquier lógica que se ramifique según "¿está presente el header X?".

### 3. Estrictez de terminación de línea
El RFC manda CRLF; los parsers permisivos aceptan LF solo o incluso CR solo. Un valor de header que contiene `\n` se vuelve una línea de header nueva en un parser permisivo y queda como valor en uno estricto. Primitiva clásica de inyección CRLF / response-splitting.

### 4. Manejo del espacio en blanco en/alrededor de los valores
Espacio en blanco opcional (OWS) según el RFC; en la práctica, los parsers lo quitan distinto. Tabs embebidos, espacios múltiples y espacio al final afectan sutilmente las comparaciones (`Content-Length: 13 ` vs `13`). Particularmente peligroso para `Transfer-Encoding` donde las variaciones de parseo de valor deciden si el parser ve "chunked" o no.

### 5. Stack de encoding (chunked, compresión, charsets)
Múltiples codings de `Transfer-Encoding` (`chunked, gzip`), codings no soportados e interacciones de `Content-Encoding` más `Transfer-Encoding`. Algunos parsers rechazan codings desconocidos; algunos los pasan; el resultado-del-decoding puede diferir por hop.

## Impacto
Los bugs de formato de mensaje son típicamente **bugs de sustrato** — habilitan un ataque de nivel superior en vez de aterrizar uno directamente. Ordenado aproximadamente por techo:

- **Request smuggling** — front-end y back-end discrepan sobre el framing del body. El impacto más alto de esta clase. Rinde hijack de request, cache poisoning, bypass de auth.
- **Cache poisoning** — el proxy y la caché derivan la clave del mensaje distinto a como lo procesa el backend. Dueña de su propia profundidad en [[caching-and-security|Caché y seguridad]].
- **Inyección CRLF / response splitting** — un LF desnudo en un valor de header controlado por el atacante inyecta un header falso (o una response falsa) que algún intermediario cree.
- **Bypass de autenticación/autorización por inyección de header** — `Host` duplicado, `Authorization` duplicado, `Cookie` duplicado parseados distinto entre proxy y backend.
- **Evasión de detección / WAF** — el mensaje llega al backend en una forma que el WAF no normalizó igual.

## Detección y defensa
Ordenado por efectividad:

1. **Rechazá los mensajes ambiguos en el edge.**
   El hop más estricto de la cadena debería rechazar cualquier cosa que no sea una única forma canónica: sin `Host` duplicado, sin `Content-Length` más `Transfer-Encoding`, sin chunked encoding malformado, sin LF desnudo, sin espacio al inicio/final en los valores de header, sin folding de línea de header. Si el edge no puede canonicalizar, fallá cerrado. Esto elimina clases enteras de desacuerdo antes de que cualquier desajuste de parsers importe.

2. **Usá HTTP/2 end-to-end donde controlás ambos extremos.**
   Los headers de frame binarios cargan una longitud explícita por frame. Toda la pregunta de framing "¿dónde termina el body?" desaparece. La superficie de ataque restante es el hop de downgrade h2 → h1; eliminala hablando h2 también con el origin.

3. **Alineá los parsers entre hops.**
   La misma familia y versión de servidor web en ambos lados donde sea factible. La mayoría de los hallazgos de desacuerdo son porque un lado es permisivo y el otro estricto sobre el mismo input. Auditá el diff explícitamente.

4. **Logueá la forma normalizada del mensaje, no las abstracciones del framework.**
   Logueá las líneas de header crudas (o una canonicalización fiel). Las líneas de log del framework esconden el espacio al final, el header duplicado, el juego de casing — que es exactamente el dato que la forensia necesita.

5. **Tratá `request.headers` como una *vista*, no la verdad.**
   En el código de la aplicación, nunca ramifiques decisiones de seguridad según "el header X existe". Ramificá según "el proxy de edge afirmó X de forma autoritativa" — es decir, el valor que el proxy confiable inyectó, distinguible por estar en un nombre de header que la aplicación nunca lee de los clientes directamente.

6. **Limitá la cantidad de headers y la longitud de línea de header en el edge.**
   El DoS de big-headers, el slowloris-por-headers y los costos de canonicalización patológicos se vuelven no-problemas con un límite sensato. La mayoría de los ataques tienen que ser cortos para ser útiles.

### Qué no funciona como defensa primaria

- **Solo firmas de WAF.** Los WAFs atrapan formas de payload de smuggling conocidas; no atrapan desacuerdos de parser novedosos ni juegos de espacio en blanco. Los novedosos son los peligrosos.
- **Confiar en la normalización del framework.** El framework normaliza para *su propio* parser. El proxy puede ya haber aceptado bytes que el framework habría rechazado, y haberlos forwardeado al backend sin re-canonicalizar.
- **Un pen-test único.** Los parsers derivan entre versiones. Un test limpio hoy no significa nada después del próximo point release de Nginx. La canonicalización de edge necesita verificarse continuamente.
- **Pasar a minúscula o quitar en el código de la aplicación.** Para cuando corre el código de la aplicación, una segunda request smuggleada ya fue encolada.

## Labs prácticos
`printf`, `nc`, `openssl` y `curl` estándar. Burp Repeater es la herramienta de producción para este trabajo pero lo básico no necesita GUI.

### Enviar una request HTTP/1.1 cruda y limpia

```bash
# HTTP plano — saltea la normalización de curl, te deja ver el framing exacto del servidor
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | nc example.com 80

# HTTPS — la misma idea envuelta en TLS
printf 'GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect example.com:443 -servername example.com 2>/dev/null
```

### Sondear la canonicalización del nombre de header

```bash
# Sonda de juego de casing — ¿el backend trata estos como el mismo?
curl -sI https://example.com/ -H 'X-API-Key: a' -H 'x-api-key: b' -H 'X-Api-Key: c'

# Host duplicado — ¿cuál gana?
printf 'GET / HTTP/1.1\r\nHost: legit.example.com\r\nHost: evil.example\r\nConnection: close\r\n\r\n' \
  | openssl s_client -quiet -connect legit.example.com:443 -servername legit.example.com 2>/dev/null

# Cookie / Authorization duplicado — ¿cuál se lee?
curl -sI https://example.com/me -H 'Authorization: Bearer real' -H 'Authorization: Bearer fake'
```

### Sondear la estrictez de espacio en blanco y terminación de línea

```bash
# LF desnudo en vez de CRLF — ¿el servidor acepta esto como terminador de línea válido?
printf 'GET / HTTP/1.1\nHost: example.com\nConnection: close\n\n' \
  | nc example.com 80

# Juegos de espacio en blanco sobre Content-Length / Transfer-Encoding
printf 'POST / HTTP/1.1\r\nHost: example.com\r\nContent-Length: 13 \r\nTransfer-Encoding:  chunked\r\nConnection: close\r\n\r\n0\r\n\r\nSMUGGLED' \
  | nc example.com 80
```

### Sondear la ambigüedad de framing del body (CL/TE)

```bash
# Ambos headers presentes — distintos parsers prefieren distinto.
# Esta es la primitiva de smuggling; correla solo contra sistemas que sean tuyos o
# para los que tengas autorización escrita de testear. Ver [[request-smuggling]] para la
# metodología completa y HTTP Request Smuggler / smuggler.py para sondeo sistemático.
printf 'POST / HTTP/1.1\r\nHost: lab.example.com\r\nContent-Length: 6\r\nTransfer-Encoding: chunked\r\n\r\n0\r\n\r\nXYZ' \
  | nc lab.example.com 80
```

### Mirar cómo se ve una request real en el wire

```bash
# Capturar una request de curl tal como sale de tu máquina
curl -v --trace-ascii /tmp/curl-trace https://example.com/login -d 'user=a&pass=b' >/dev/null 2>&1
less /tmp/curl-trace
# Las secciones "=> Send header" / "=> Send data" son los bytes literales en el wire.
```

## Ejemplos prácticos
- Un formulario de login postea a un backend que lee `request.body` después de que Express lo parsea. Una segunda request smuggleada se cuela vía desajuste de `Transfer-Encoding`/`Content-Length` y secuestra la cookie de sesión del próximo usuario antes de que el framework siquiera la vea.
- Una app guarda `request.headers['x-api-key']` para logs de auditoría. El proxy normaliza los nombres de header a minúscula; la aplicación usa Express que preserva el casing para headers desconocidos. Dos entradas de log de auditoría distintas registran la misma request de forma distinta.
- Un reverse proxy quita un header `Cookie` y forwardea el resto; la aplicación concatena todos los headers `Cookie` en uno. El estado de autenticación termina dependiendo de qué nodo de CDN sirvió la request.
- Un WAF rechaza requests que contienen `Transfer-Encoding: chunked` pero un backend permisivo acepta `Transfer-Encoding:  chunked` (espacio extra). Los payloads de smuggling pasan el WAF y llegan al backend.
- Un atacante inyecta `\r\n` en un parámetro de redirect `Location` provisto por el usuario. La aplicación emite `Location: https://example.com/...\r\nSet-Cookie: admin=1`, y un cliente permisivo honra el `Set-Cookie` inyectado. Inyección CRLF / response splitting clásica.
- Un pipeline de logging parsea mensajes HTTP crudos de los access logs y usa el valor `User-Agent` del access log como string. Un atacante envía `User-Agent: x\nINJECTED LINE`. El parser de logs ve dos líneas; el resto del pipeline queda envenenado.

## Notas relacionadas
- [[http-overview|Panorama de HTTP]] — modelo del protocolo, ciclo de vida, diferencias de versión. La mitad de "qué es HTTP" del par que esta nota completa.
- [[http-headers|Headers HTTP]] — significado semántico de campos de header específicos que dirigen el comportamiento de seguridad.
- [[reverse-proxies|Reverse proxies]] — traducción de confianza entre dos parsers HTTP; el encuadre "dos parsers, los mismos bytes".
- [[client-ip-trust|Confianza en la IP del cliente]] — la especialización de desacuerdo-de-confianza para los headers de IP forwarded.
- [[caching-and-security|Caché y seguridad]] — la derivación de clave de caché lee el mismo mensaje; las diferencias de framing se vuelven poisoning.
- [[packet-analysis|Análisis de paquetes]] — observá los bytes del mensaje en el wire cuando curl/nc no alcanzan.
- [[wireshark-workflows|Flujos de trabajo con Wireshark]] — capturar e inspeccionar mensajes HTTP en vivo.
- [[cybersecurity/web-security/request-smuggling|Request smuggling]] — dueña de la profundidad sobre la explotación de framing del body.
- [[cybersecurity/web-security/cors-misconfiguration|Mala configuración de CORS]] — semántica de los headers `Origin`/`Access-Control-Allow-Origin`.

### Notas atómicas futuras sugeridas
- [[crlf-injection|Inyección CRLF]]
- [[response-splitting|Response splitting]]
- [[chunked-encoding-quirks|Rarezas del chunked encoding]]
- [[header-folding-obs-fold|Folding de header (obs-fold)]]
- [[duplicate-header-resolution|Resolución de headers duplicados]]
- [[content-length-vs-transfer-encoding-history|Historia de Content-Length vs Transfer-Encoding]]

## Referencias
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Foundational:** RFC 9112 (HTTP/1.1 Message Syntax) — https://datatracker.ietf.org/doc/html/rfc9112
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
