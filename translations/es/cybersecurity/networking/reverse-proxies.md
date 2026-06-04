---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-26
tags:
  - cybersecurity
  - networking
  - trust-boundary
  - reverse-proxy
  - http
sources: []
---

# Reverse proxies

## Definición
Un reverse proxy es un intermediario HTTP que acepta requests en nombre de uno o más servicios de backend, aplica un conjunto fijo de transformaciones y forwardea el resultado al backend que elige. La propiedad que lo define no es "balancea carga" — el balanceo de carga es una transformación. La propiedad que lo define es que **el proxy y el backend parsean cada uno la request de forma independiente**, lo que vuelve al proxy una frontera de confianza cada vez que sus interpretaciones difieren.

Ejemplos: Nginx, Envoy, HAProxy, Apache (mod_proxy), AWS ALB / CloudFront, Cloudflare, Akamai, Fastly, ingress controllers de Kubernetes, API gateways.

## Por qué importa
Los reverse proxies son la frontera de confianza más consecuente en los sistemas modernos de cara a HTTP. Importan porque:

- **Suelen ser el punto de terminación de TLS.** Lo que sea que el proxy decida sobre una request, el backend lo ve como texto plano — incluyendo cualquier header que el proxy inyectó.
- **Son un segundo parser sobre el mismo wire.** Cada desacuerdo entre el parser del proxy y el del backend es una vulnerabilidad candidata.
- **Cargan identidad forwarded.** La idea del backend de "quién es el cliente" casi siempre viene de un header que el proxy inyectó. Si el proxy no quita el mismo header en el inbound, los atacantes forjan identidad.
- **Normalizan las requests de formas que el backend olvida.** Colapso de path, folding de casing de header, manejo de espacio en blanco, merge de parámetros de query — cada uno es una chance de que el proxy y el backend vean una request distinta.
- **Cachean.** Las responses cacheadas se comparten entre usuarios. Un proxy que cachea con la clave equivocada convierte la fuga de un usuario en una divulgación pública.

La lección recurrente: **un reverse proxy es una frontera de seguridad por accidente**, porque dos parsers independientes manejan los mismos bytes y el operador rara vez audita el diff.

## Cómo funciona
Un reverse proxy aplica cinco transformaciones en cada request. Conocer las cinco te deja predecir dónde van a discrepar el proxy y el backend.

1. **Terminación de TLS** — acepta HTTPS del cliente, abre HTTP (o HTTPS re-cifrado) al backend. El backend ve texto plano y confía en él.
2. **Reescritura de headers** — inyecta headers de identidad y ruteo (`X-Forwarded-For`, `X-Forwarded-Proto`, `X-Real-IP`, `X-Forwarded-Host`, `Forwarded`, `Via`), quita headers hop-by-hop (`Connection`, `Keep-Alive`, `Transfer-Encoding`), puede reescribir `Host`.
3. **Reescritura de path / host** — `/api/v1/users` en el edge se vuelve `/users` en el backend; `Host: app.example.com` puede ser reemplazado o preservado según la config.
4. **Normalización y buffering de la request** — colapsa `//` a `/`, decodifica paths percent-encoded, puede bufferear el body completo antes de forwardear, puede re-chunkear o de-chunkear los bodies transfer-encoded.
5. **Caché de responses** — con clave por URL + un subconjunto (configurable) de headers, servida a *cualquier* cliente futuro cuya request hashee a la misma clave.

Una request antes y después del proxy, ilustrando la inyección de headers y la terminación de TLS:

```http
# Lo que el cliente envía sobre TLS
GET /admin HTTP/1.1
Host: app.example.com
Cookie: session=abc123
User-Agent: curl/8

# Lo que el backend recibe sobre HTTP en texto plano
GET /admin HTTP/1.1
Host: app.example.com
Cookie: session=abc123
User-Agent: curl/8
X-Forwarded-For: 203.0.113.42
X-Forwarded-Proto: https
X-Real-IP: 203.0.113.42
Via: 1.1 nginx
```

El backend ahora cree que el cliente es `203.0.113.42`. Si el backend **no** verifica que este header llegó del proxy (y no de un atacante directo que lo alcanzó en un puerto no-edge), la traducción de confianza está rota.

El bug no es el proxy. El bug es la diferencia no auditada entre lo que el proxy pretende comunicar y lo que el backend elige creer.

## Técnicas / patrones
Qué miran los atacantes y cómo sondean:

- **Fingerprintear el proxy.** Headers `Server`, `Via`, `X-Cache`, `X-Amz-Cf-Id`, `CF-Ray`, `X-Served-By`, estilos de página de error, rarezas del handshake TLS, bodies de 404 por defecto.
- **Encontrar alcanzabilidad directa al backend.** Si el backend está expuesto en una IP/puerto no-edge (mala config de security-group de nube, origin filtrado en el historial de DNS, segundo hostname apuntando a la misma IP), todo control impuesto por el proxy se bypassea.
- **Sondear la confianza de headers.** Enviá `X-Forwarded-For: 127.0.0.1` desde internet pública — ¿la app lo loguea como la IP de origen, o lo confía para una allowlist? Lo mismo para `X-Original-URL`, `X-Rewrite-URL`, `X-Forwarded-Host`.
- **Sondear el desacuerdo de parsers.** `Content-Length` + `Transfer-Encoding` ambiguos, chunked encoding malformado, juegos de casing en nombres de header, headers duplicados, valores con espacio en blanco. Ver [[request-smuggling|request smuggling]] para la taxonomía completa de desync.
- **Sondear el desacuerdo de normalización.** `//admin`, `/admin/.`, `/admin%2F`, `/admin;jsessionid=x`, `/admin?` — ¿el proxy y el backend coinciden en qué path se pidió? Las diferencias se vuelven bypasses de control de acceso.
- **Sondear la clave de caché.** Agregá headers sin clave (`X-Forwarded-Host`, `User-Agent`, `Accept-Language`) y buscá superficie de poisoning. Ver [[caching-and-security|Caché y seguridad]].

## Variantes y bypasses
Las fallas de seguridad de reverse proxy caen en **3 clases de desacuerdo**. Tener esta taxonomía en memoria de trabajo basta para navegar cualquier hallazgo específico.

### 1. Desacuerdo de parser
El proxy y el backend discrepan en **dónde termina la request o qué bytes le pertenecen**. Ejemplo canónico: el desajuste `Content-Length` vs `Transfer-Encoding: chunked` rinde request smuggling (familias CL.TE, TE.CL, TE.TE). Las rarezas de folding de línea de header, bytes NUL, headers duplicados y el downgrade HTTP/2 → HTTP/1.1 viven todos acá.

Techo de impacto: envenenar la cola de requests, secuestrar las requests de otros usuarios, alcanzar endpoints ocultos, bypassear la auth del edge.

Dueña de la profundidad: [[request-smuggling|request smuggling]].

### 2. Desacuerdo de normalización
El proxy y el backend discrepan en **qué request se hizo**, aunque coincidan en los bytes. Colapso de path, comportamiento de percent-encoding, manejo de parámetros con punto y coma, tratamiento del header host, hostnames con punto al final, sensibilidad al casing. Ejemplo: el edge impone que `/admin` está prohibido; el backend trata `/admin/.` como `/admin/` y lo sirve.

Techo de impacto: bypass de control de acceso, web cache poisoning (normalización distinta → clave de caché distinta → response servida al usuario equivocado), inyección de host-header.

### 3. Desacuerdo de confianza
El proxy y el backend discrepan en **qué creer sobre la identidad o el transporte de la request**. El backend confía en `X-Forwarded-For` desde cualquier origen porque se supone que el proxy lo sobrescribe; el atacante llega al backend directamente (o a través de un proxy mal configurado que agrega en vez de sobrescribir) y forja identidad. La misma forma: `X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Original-URL`, `X-Rewritten-URL`, `True-Client-IP`.

Techo de impacto: bypass de rate-limit, forja de logs, bypass de allowlist, bypass de autenticación basada en IP, alcanzabilidad de endpoints solo-internos.

Dueña de la profundidad: [[client-ip-trust|Confianza en la IP del cliente]].

## Impacto
Ordenado aproximadamente por severidad:

- **RCE / bypass de auth por request smuggling** — familia de desacuerdo-de-parser. El techo más alto; afecta a cada usuario detrás del proxy en la misma conexión.
- **Cache poisoning** — familia de desacuerdo-de-normalización. Una request mala se vuelve muchas responses malas a otros usuarios.
- **Alcanzabilidad directa al backend** — todo control impuesto por el proxy se vuelve opcional. Reglas de WAF, auth de edge, rate limiting, geo-blocking, todos bypasseados.
- **Forja de headers forwarded** — familia de desacuerdo-de-confianza. IP de origen spoofeada para bypass de rate-limit, spoofing de logs, bypass de allowlist.
- **Acceso a paths de admin ocultos** — el desacuerdo de normalización o ruteo alcanza un path que el proxy cree bloqueado.
- **Ataques de host-header** — `Host:` o `X-Forwarded-Host:` llega al backend sin filtrar, redirigiendo emails de reset de contraseña, envenenando URLs generadas o ruteando a un virtual host que el proxy no pretendía.
- **Degradación de TLS** — el backend cree que la request fue HTTPS por `X-Forwarded-Proto: https`, cuando en realidad un proxy mal configurado forwardeó texto plano.

## Detección y defensa
Ordenado por efectividad:

1. **Hacé la frontera de confianza explícita y de una sola vía.**
   El proxy debe siempre sobrescribir los headers de identidad (`X-Forwarded-For`, `X-Real-IP`, `X-Forwarded-Proto`, `X-Forwarded-Host`) en el inbound — nunca agregar, nunca preservar. El backend debe confiar en esos headers solo cuando la conexión llegó del rango de IP del proxy. Sin ambas mitades, la traducción de confianza es forjable. La mayoría de las roturas de producción son porque una mitad es correcta en aislamiento y silenciosamente incorrecta como par.

2. **Rechazá las requests ambiguas en el edge.**
   Descartá requests que contengan tanto `Content-Length` como `Transfer-Encoding`, chunked encoding malformado, espacio en blanco en nombres de header, headers `Host` duplicados o terminaciones de línea no conformes. El edge es el parser canónico; si no puede canonicalizar el mensaje, debe fallar cerrado. Esto corta la familia de desacuerdo-de-parser en la fuente.

3. **Alineá el comportamiento del proxy y el backend.**
   Usá la misma familia y versión de servidor web en ambos lados donde sea factible, o al menos auditá el diff. La mayoría de los hallazgos de desync vienen de un lado siendo más permisivo que el otro sobre el mismo input. Esta es la razón por la que "Nginx delante de Apache" tiene una larga historia de CVEs — los parsers nunca fueron diseñados para coincidir.

4. **Hacé la clave de caché explícita.**
   Auditá qué headers de request participan en la clave de caché. Tratá cualquier header que el backend lea pero la caché no incluya como un candidato a poisoning. Deshabilitá el caché para responses autenticadas por completo salvo que `Vary` refleje correctamente cada header relevante.

5. **Bloqueá la alcanzabilidad directa al backend.**
   Los security groups de nube deberían aceptar inbound solo desde el rango de origen del proxy. Los escáneres de historial de DNS (p. ej., Censys, SecurityTrails) encuentran rutinariamente la IP del origin — asumí que los atacantes también. El mTLS entre proxy y backend es la versión más fuerte de este control.

6. **Mapeá la cadena completa.**
   CDN → WAF → load balancer → ingress controller → app server. Cada hop es un parser. Cada hop es una frontera de confianza. Cada hop tiene sus propias reglas de normalización. Documentalos; ensayá qué quita, inyecta, reescribe y cachea cada uno.

7. **Monitoreá indicadores de desync.**
   Vigilá: requests atribuidas al usuario equivocado, clusters inesperados de `400 Bad Request` del backend, entradas de caché con claves desajustadas, anomalías de reuso de conexión en keep-alive, picos repentinos en valores de `X-Forwarded-For` que coinciden con RFC1918 desde internet pública.

### Qué no funciona como defensa primaria

- **Solo reglas de WAF.** Los WAFs atrapan payloads de smuggling conocidos y XSS conocido; no atrapan desacuerdos de parser novedosos, juegos de normalización novedosos ni forja de header de confianza desde dentro del rango de IP confiable.
- **Confiar en `X-Forwarded-For` porque "solo el proxy puede setearlo".** El proxy *también* puede setearlo, pero también cualquiera que llegue a la IP del backend directamente. La confianza viene del camino de red, no de la existencia del header.
- **Quitar `X-Forwarded-For` solo en el outbound.** El header tiene que sobrescribirse en el **inbound**, antes de llegar a cualquier backend que pudiera leerlo. Quitarlo en el outbound es demasiado tarde.
- **Asumir que HTTPS en el edge significa HTTPS en el backend.** La terminación de TLS por defecto produce un hop en texto plano. Cifrá ese hop también si el backend maneja credenciales, o al menos autenticalo (mTLS) para que un atacante de red no pueda inyectar requests que parezcan originadas en el proxy.
- **Un pen-test único.** Las versiones del proxy y el backend derivan. Un test de smuggling limpio hoy no significa nada después del próximo point release de Nginx.

## Labs prácticos
Comandos concretos que podés correr para construir intuición de parser de proxy. Ninguno requiere software de lab más allá de curl, nc, dig y openssl.

### Fingerprintear qué hay delante de la app

```bash
# Buscar headers de fingerprint de proxy en una response normal
curl -sI https://example.com | grep -iE 'server|via|x-cache|x-amz-cf-id|cf-ray|x-served-by'

# El handshake TLS revela la identidad del edge (ALPN, SANs del cert, JA3)
openssl s_client -connect example.com:443 -servername example.com -alpn h2,http/1.1 </dev/null 2>/dev/null | head -30

# Comparar el conjunto de IPs del hostname público contra el apex — registros A extra suelen revelar el origin
dig +short example.com
dig +short origin.example.com
dig +short www.example.com
```

### Sondear la confianza de headers forwarded

```bash
# ¿La app loguea o confía en una IP de cliente provista por el atacante?
curl -sI https://example.com/ -H "X-Forwarded-For: 127.0.0.1"
curl -sI https://example.com/ -H "X-Real-IP: 127.0.0.1"
curl -sI https://example.com/admin -H "X-Forwarded-For: 10.0.0.1"

# Sonda de cache poisoning — ¿un header sin clave se refleja en la response?
curl -sI https://example.com/ -H "X-Forwarded-Host: evil.example"
```

### Sondear el desacuerdo de normalización

```bash
# Juegos de normalización de path — ¿/admin/. o /admin%2F alcanza una ruta de backend "bloqueada"?
for path in /admin /admin/ /admin/. //admin /admin%2F /admin%252F /./admin /admin?; do
  printf '%-25s -> %s\n' "$path" "$(curl -so /dev/null -w '%{http_code}' "https://example.com$path")"
done

# Inyección de host header — ¿la app genera URLs a partir del header Host?
curl -sI https://example.com/password-reset -H "Host: evil.example"
```

### Sondear el desacuerdo de parser (smuggling)

```bash
# Enviar HTTP crudo — curl es demasiado bien-portado para esto. Usá printf + nc / openssl s_client.
# Primero confirmá la alcanzabilidad y observá la normalización del proxy:
printf 'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n' \
  | openssl s_client -quiet -connect example.com:443 -servername example.com

# Para sondas reales de smuggling, usá el HTTP Request Smuggler de PortSwigger (extensión de Burp)
# o smuggler.py — ver [[request-smuggling]] para la metodología de ataque completa.
```

### Confirmar que la alcanzabilidad directa al backend está bloqueada

```bash
# Si encontrás una IP de origin vía historial de DNS o certificate transparency,
# verificá que el security group bloquea el acceso directo:
curl -k --resolve example.com:443:<origin-ip> https://example.com/ -I
# Un timeout o RST es el resultado deseado. Una response 200 significa que el proxy es bypasseable.
```

## Ejemplos prácticos
- Una app SaaS confía en `X-Forwarded-For` desde cualquier origen. El atacante envía `X-Forwarded-For: 127.0.0.1` para bypassear una ruta de admin "solo-interna".
- Un edge de Nginx delante de un backend Node discrepa en `Content-Length` vs `Transfer-Encoding`. Las requests smuggleadas envenenan la cola de keep-alive y secuestran la cookie de sesión del próximo usuario.
- Un CDN cachea `/profile` con clave solo en la URL. El backend personaliza la response según el header `Cookie`. El atacante dispara un cache fill estando logueado; las requests no autenticadas posteriores obtienen la response personalizada cacheada.
- Un WAF quita `<script>` de los bodies de request pero el backend interpreta el body de nuevo tras un re-parse `multipart/form-data`, recuperando el payload — desacuerdo de normalización.
- Un ingress controller de Kubernetes forwardea `Host: evil.example` sin modificar. El backend usa el header Host para construir una URL de reset de contraseña. Los emails de reset apuntan al dominio del atacante.
- Una IP de origin filtrada en registros históricos de DNS deja que un atacante alcance la instancia EC2 directamente, bypasseando el WAF y el rate limiter de Cloudflare por completo.

## Notas relacionadas
- [[http-messages|Mensajes HTTP]] — el formato de wire que cada proxy parsea.
- [[http-headers|Headers HTTP]] — semántica de headers, hop-by-hop vs end-to-end, headers de forwarding.
- [[client-ip-trust|Confianza en la IP del cliente]] — dueña de la profundidad sobre `X-Forwarded-For` y la clase de desacuerdo-de-confianza.
- [[load-balancers|Load balancers]] — concepto solapado; los reverse proxies se enfocan en la interpretación de HTTP, los load balancers en la distribución de tráfico.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — la mitad de capa-de-red de la defensa de edge.
- [[caching-and-security|Caché y seguridad]] — dueña de la profundidad sobre el razonamiento de clave de caché y el poisoning.
- [[tls-https|TLS/HTTPS]] — detalles de terminación de TLS e interacción con HSTS.
- [[cybersecurity/web-security/request-smuggling|Request smuggling]] — dueña de la profundidad sobre la clase de desacuerdo-de-parser.
- [[cybersecurity/web-security/ssrf|SSRF]] — la alcanzabilidad interna se vuelve más peligrosa cuando el backend es directamente direccionable.
- [[cybersecurity/security-playbooks/reverse-proxy-misconfig-checklist|Checklist de mala configuración de reverse proxy]]

### Notas atómicas futuras sugeridas
- [[host-header-injection|Inyección de host-header]]
- [[web-cache-poisoning|Web cache poisoning]]
- [[origin-ip-discovery|Descubrimiento de IP de origin]]
- [[mtls-between-proxy-and-backend|mTLS entre proxy y backend]]
- [[http2-downgrade-desync|Desync por downgrade de HTTP/2]]
- [[forwarded-header-spec|Spec del header Forwarded]]

## Referencias
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger request smuggling academy — https://portswigger.net/web-security/request-smuggling
- **Research / Deep Dive:** James Kettle, "HTTP Desync Attacks: Request Smuggling Reborn" — https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
