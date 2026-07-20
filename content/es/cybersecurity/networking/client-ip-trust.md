---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-27
tags:
  - cybersecurity
  - networking
  - trust-boundary
  - forwarded-headers
  - http
sources: []
---

# Confianza en la IP del cliente

## Definición
La confianza en la IP del cliente es la pregunta de **qué IP trata una aplicación como "el cliente"** cuando las requests pasan por cualquier intermediario — reverse proxy, load balancer, CDN, WAF o sidecar de service-mesh. El bug rara vez es "leímos el header equivocado". El bug es que la traducción de confianza entre la identidad de red y la identidad de header HTTP no está auditada: el proxy dice una verdad, el backend cree otra distinta y el atacante elige cuál.

## Por qué importa
Una cantidad sorprendente de seguridad en producción depende de este único string:

- **Rate limiting** — con clave por IP de cliente. IP spoofeada → rotación ilimitada.
- **Allowlists de IP** — paneles de admin, APIs internas, integraciones con vendors. IP spoofeada → acceso privilegiado.
- **Logs de auditoría** — fraude, abuso, respuesta a incidentes. IP spoofeada → atribución equivocada, cadena de evidencia corrompida.
- **Geo-blocking y enforcement de licencias** — IP spoofeada → bypass de política.
- **Señales de detección de fraude** — IP spoofeada → comportamiento lavado.
- **Blocklists de WAF y abuso** — IP spoofeada → evasión de ban por rotación de header.
- **Claves de caché** — cuando `X-Forwarded-For` es parte de la clave de caché, los valores spoofeados se vuelven una superficie de poisoning.

La confianza en headers forwarded es también el ejemplo canónico de la **clase de desacuerdo-de-confianza** introducida en [[reverse-proxies|Reverse proxies]]: el proxy y el backend coinciden en los bytes pero discrepan en qué creer sobre la identidad.

## Cómo funciona
No existe una "IP de cliente real". Solo existe una **traducción de confianza** entre dos hechos:

1. **Identidad de red** — la IP de origen de la conexión TCP que llegó al backend. El kernel la conoce; no se puede forjar en la capa TCP (módulo escenarios de BGP/route-hijack, que quedan fuera de alcance para esta nota). Para un backend detrás de un proxy, esta es *la IP del proxy*, no la del usuario.
2. **Inyección de header** — el proxy inyecta un header (`X-Forwarded-For`, `X-Real-IP`, `X-Forwarded`, `Forwarded`, `True-Client-IP`, `CF-Connecting-IP`, `Fastly-Client-IP`, etc.) que carga su afirmación sobre el cliente original.
3. **Interpretación del backend** — el backend elige creer (o no) ese header. *Si esa creencia es sólida depende enteramente de si la conexión en el paso 1 vino de un proxy confiable.*

La cadena estándar de `X-Forwarded-For` crece de izquierda a derecha a medida que una request atraviesa hops:

```http
# Cliente → CDN → ALB → app server, lo que ve el app server:
GET / HTTP/1.1
Host: example.com
X-Forwarded-For: 203.0.113.42, 198.51.100.10, 198.51.100.20
X-Real-IP: 203.0.113.42
```

`203.0.113.42` es el de más a la izquierda — se afirma que es el cliente original. `198.51.100.10` es el CDN. `198.51.100.20` es el ALB. La IP de origen TCP (lo que ve el kernel) es el ALB.

El reemplazo estandarizado, definido en **RFC 7239**, es el header estructurado `Forwarded:`:

```http
Forwarded: for=203.0.113.42;proto=https;by=198.51.100.20
```

El bug no está en la cadena. El bug es que **la IP de más a la izquierda es controlable por el atacante**. Si el cliente envió `X-Forwarded-For: 1.2.3.4` y el CDN agregó su propio valor en vez de sobrescribir, la cadena es `1.2.3.4, <cliente-real>, <cdn>, <alb>` — y cualquier backend que lee la entrada de más a la izquierda ahora lee input del atacante.

La regla: la confianza viene del **camino de red** (paso 1), no del header (paso 2). El header es dato. El camino de red es la frontera de seguridad.

## Técnicas / patrones
Qué miran los atacantes y cómo sondean:

- **Leé la response y los logs.** Si la app refleja `X-Forwarded-For` en algún lado (páginas de debug, mensajes de error, logs visibles en admin) el comportamiento de atribución está medio revelado gratis.
- **Probá los valores obvios primero.** `X-Forwarded-For: 127.0.0.1`, `X-Forwarded-For: 10.0.0.1`, `X-Forwarded-For: ::1`. Las apps que whitelistean IPs "internas" sin verificar el camino de red se rompen de inmediato.
- **Probá cada variante de header.** Muchos backends leen múltiples headers en orden de prioridad. Spoofealos todos: `X-Forwarded-For`, `X-Real-IP`, `X-Client-IP`, `True-Client-IP`, `X-Cluster-Client-IP`, `Forwarded`, `CF-Connecting-IP`, `Fastly-Client-IP`. El backend puede leer el que el proxy *no* sobrescribe.
- **Sondeá el conteo de trust-hop.** Enviá cadenas de longitud variable (`1.2.3.4`, después `1.2.3.4, 5.6.7.8`, después más) y observá qué IP usa la app. Esto revela si lee primer-confiable-desde-la-derecha (correcto) o el de más a la izquierda (roto).
- **Encontrá alcanzabilidad directa al backend.** Si el backend está expuesto en una IP no-edge, *todo* chequeo de header forwarded es bypasseable porque el camino de red ya no se origina en el proxy. Ver [[reverse-proxies|Reverse proxies]] §"Bloqueá la alcanzabilidad directa al backend".
- **Testeá la inclusión en la clave de caché.** Un valor `X-Forwarded-For` reflejado en una response cacheada es una primitiva de web-cache-poisoning.

## Variantes y bypasses
La confianza en la IP forwarded falla de **5 formas distintas**. Tener la taxonomía en memoria de trabajo basta para navegar cualquier hallazgo específico.

### 1. Confianza-desde-cualquier-lado
El backend lee `X-Forwarded-For` y lo usa sin chequear que la conexión vino de un proxy. Atacante directo → backend → la IP spoofeada gana.

Este es el modo de falla en Express default, Flask default, Django default, Spring Boot default — todos requieren configuración explícita de "trust proxy" para leer headers de forwarding de forma segura, y muchas apps o lo mal-configuran o lo setean demasiado permisivo (`trust proxy: true` sin scoping de IP).

### 2. Agregar-no-sobrescribir
El proxy preserva el `X-Forwarded-For` provisto por el atacante y agrega su propia observación: la cadena se vuelve `<provisto-por-atacante>, <cliente-real>, <cdn>`. Los backends que leen la entrada de más a la izquierda obtienen input del atacante. Este es el comportamiento **por defecto** de muchos proxies (Nginx con `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for` agrega; la config más segura es sobrescribir).

### 3. Confusión de nombre de header
El backend lee `X-Real-IP` mientras el proxy solo sobrescribe `X-Forwarded-For`. O el backend lee `True-Client-IP` (un header de Cloudflare/Akamai) que el Nginx local nunca sanea. O el backend lee `Forwarded:` (RFC 7239) mientras el proxy solo manipula headers legacy. El atacante spoofea la variante no saneada.

### 4. Confianza-por-posición
El backend lee la IP de más a la izquierda en la cadena en vez de la más-a-la-derecha-confiable (o viceversa, en un despliegue invertido). El algoritmo correcto es: **contar hacia atrás N hops desde la derecha**, donde N es la cantidad de proxies confiables delante de la app. La mayoría de los bugs de producción son el resultado de leer la posición 0 (siempre controlada por el atacante) o leer la posición -1 (siempre la IP del propio proxy).

### 5. Magia de loopback / RFC1918
El backend confía en `X-Forwarded-For` *solo* cuando el valor es una IP de rango privado o loopback (`127.0.0.1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`). El atacante simplemente envía `X-Forwarded-For: 127.0.0.1` y hereda la confianza "interna". Este patrón es deprimentemente común en las allowlists de admin.

## Impacto
Ordenado aproximadamente por severidad:

- **Bypass de allowlist de IP** — paneles de admin, APIs internas, integraciones partner expuestas spoofeando una IP de origen "confiable". El techo más alto porque las allowlists frecuentemente sustituyen a la autenticación.
- **Bypass de rate-limit / abuso** — cada IP spoofeada es una cuota fresca. Ruta en texto plano a credential stuffing, scraping de contenido y abuso de SMS-bomb.
- **Forja de log de auditoría / atribución de fraude** — el equipo de fraude persigue la IP equivocada. La respuesta a incidentes descarrila.
- **Cache poisoning** — `X-Forwarded-For` reflejado en una response con clave solo en la URL. Una request mala, muchas responses malas. Ver [[caching-and-security|Caché y seguridad]].
- **Bypass de geo / licencia** — licenciamiento de contenido, restricciones de región de pago, cumplimiento de sanciones colapsan todos por un único header spoofeado.
- **Evasión de blocklist de WAF** — la IP baneada rota `X-Forwarded-For` y reaparece como un cliente fresco.
- **Alcanzabilidad de endpoints solo-internos** — cuando la confianza de "IP interna" otorga acceso a endpoints de debug, métricas o rutas de gestión.

## Detección y defensa
Ordenado por efectividad:

1. **Anclá la confianza en el camino de red, no en el header.**
   El backend debe verificar que la IP de origen TCP sea un proxy conocido (allowlist CIDR) antes de leer cualquier header de forwarding. Si la conexión llega de una dirección no-proxy, cada `X-Forwarded-For`, `X-Real-IP`, `Forwarded:` es dato, no identidad. Esta única regla derrota toda la clase de desacuerdo-de-confianza.

2. **Configurá el conteo de hops confiables explícitamente.**
   Express `trust proxy: 1` (un hop confiable), Django `USE_X_FORWARDED_HOST = True` emparejado con `SECURE_PROXY_SSL_HEADER`, Spring `ForwardedHeaderFilter`, Rails `config.action_dispatch.trusted_proxies`. La respuesta correcta es *el conteo de proxies entre internet pública y este proceso*, no `true`. Seteala a un número, no a un booleano.

3. **Hacé que el proxy sobrescriba, no agregue.**
   El proxy de edge debe reemplazar el `X-Forwarded-For` entrante con la IP de origen observada (Nginx: `proxy_set_header X-Forwarded-For $remote_addr;` — notá `$remote_addr`, no `$proxy_add_x_forwarded_for`). Lo mismo para `X-Real-IP`, `X-Forwarded-Host`, `Forwarded`. Si confiás en un CDN upstream, la política de sobrescritura de *ese* CDN también es parte de tu modelo de confianza — verificala.

4. **Quitá cada variante que no poseas de forma autoritativa.**
   En el edge, descartá o reseteá `True-Client-IP`, `X-Real-IP`, `Forwarded:`, `X-Cluster-Client-IP`, `X-Originating-IP`, `CF-Connecting-IP`, etc. salvo que los generes específicamente. La mayoría de los bugs de confusión-de-nombre-de-header vienen de "saneamos XFF" y el backend lee silenciosamente un hermano.

5. **Preferí RFC 7239 `Forwarded:` end-to-end donde controlás ambos extremos.**
   Estructurado (`for=...;proto=...;by=...`), resistente al desacuerdo-de-parser e inequívoco sobre la dirección de la cadena. El legacy `X-Forwarded-For` vive para siempre, pero los nuevos hops internos pueden empezar con `Forwarded:` y evitar dos décadas de rarezas de compatibilidad.

6. **Logueá la IP de origen de red y la IP del header afirmado por separado, siempre.**
   `client_ip` (lo que el framework decidió) y `tcp_source_ip` (lo que vio el kernel). Cuando la forensia necesita la verdad, el valor del kernel es el único que importa. La mayoría de las apps loguean solo el valor decidido por el framework, que es exactamente el valor que el atacante controla.

7. **Tratá los controles basados en IP como defensa en profundidad, nunca como auth primaria.**
   Las allowlists son útiles como una capa de un camino de admin multi-control. No son autenticación. Emparejalas con mTLS, SSO con clave de hardware o tokens firmados — cualquier cosa donde forjar la IP ya no alcance.

### Qué no funciona como defensa primaria

- **Confiar en `X-Forwarded-For: 127.0.0.1` porque "loopback es interno".** No lo es, cuando el valor está en un header HTTP que un atacante tipea. La confianza en loopback debe venir de la interfaz `lo` del kernel, no de un string.
- **Leer la entrada de más a la izquierda de `X-Forwarded-For`.** Esa siempre es controlada por el atacante en cualquier cadena que incluya input del atacante — que es todo despliegue público.
- **Leer la entrada de más a la derecha sin un conteo de hops confiables.** Esa siempre es la IP del proxy anterior — útil solo si "proxy anterior" es internet pública (es decir, tu app es el edge), lo que contradice la existencia del header.
- **Quitar `X-Forwarded-For` solo en las responses de outbound.** El header se lee en el **inbound**, antes de que corra cualquier handler. Quitarlo en el outbound es demasiado tarde.
- **Reglas de WAF custom que descartan `X-Forwarded-For` que contiene IPs privadas.** Fácil de evadir con `X-Forwarded-For: 1.2.3.4, 127.0.0.1` (dependiendo de qué entrada lee el backend) o cambiando a un header hermano que el WAF no filtra.
- **Asumir que el CDN sanea por vos.** Algunos lo hacen, algunos no, algunos solo sanean los headers que ellos mismos escribieron. Leé los docs del CDN *y* testeá la frontera; tu supuesto es tu CVE.

## Labs prácticos
Comandos concretos para construir intuición de confianza-de-header-forwarded. `curl` estándar alcanza para lo básico.

### Leer qué cree la app que es la IP del cliente

```bash
# Muchas apps reflejan la IP de cliente percibida en páginas de debug o error.
# httpbin (o cualquier herramienta local que ecoa la request) es el objetivo de práctica más fácil:
curl -s https://httpbin.org/get | jq '.origin, .headers'

# En un engagement real, buscá:
#   - avisos "Logged in from <IP>" en páginas de perfil
#   - mensajes de error citando la IP que hace la request
#   - headers de response de rate-limit (X-RateLimit-* suelen exponer con qué se hace la clave)
curl -sI https://example.com/login -o /dev/null -D - | grep -iE 'rate|limit|client'
```

### Testear la confianza-desde-cualquier-lado

```bash
# Test por defecto — ¿la app loguea o confía en una IP de cliente provista por el atacante?
curl -i https://example.com/admin -H "X-Forwarded-For: 127.0.0.1"
curl -i https://example.com/admin -H "X-Forwarded-For: 10.0.0.1"
curl -i https://example.com/admin -H "X-Real-IP: 127.0.0.1"

# Un 200 (o contenido distinto) cuando el mismo path devuelve 403 sin el header
# es evidencia directa de confianza-desde-cualquier-lado o magia-de-loopback.
```

### Testear la confusión de nombre de header

```bash
# Rociá cada nombre común de header de forwarding; mirá cuál prefiere el backend.
for h in 'X-Forwarded-For' 'X-Real-IP' 'X-Client-IP' 'True-Client-IP' \
         'X-Originating-IP' 'X-Cluster-Client-IP' 'CF-Connecting-IP' \
         'Fastly-Client-IP' 'X-ProxyUser-Ip' 'Forwarded'; do
  printf '%-25s -> ' "$h"
  curl -sI "https://example.com/" -H "$h: 1.2.3.4" \
    -o /dev/null -w '%{http_code}\n'
done
```

### Sondear el conteo de trust-hop

```bash
# Enviá cadenas de longitud creciente; el valor que la app *usa* te dice qué
# posición lee. Mirá los logs o reflejos en la response para identificar cuál gana.
curl -sI https://example.com/ -H "X-Forwarded-For: 1.2.3.4"
curl -sI https://example.com/ -H "X-Forwarded-For: 1.2.3.4, 5.6.7.8"
curl -sI https://example.com/ -H "X-Forwarded-For: 1.2.3.4, 5.6.7.8, 9.10.11.12"

# Usá RFC 7239 también — muchas apps lo leen sin sanearlo:
curl -sI https://example.com/ -H 'Forwarded: for=1.2.3.4;proto=https'
```

### Bypassear un rate-limit por IP

```bash
# Si la app limita requests por IP y lee un header forwarded ingenuamente,
# rotar el header rota el bucket:
for i in $(seq 1 200); do
  curl -s -o /dev/null -w '%{http_code}\n' \
    -H "X-Forwarded-For: 192.0.2.$((i % 254 + 1))" \
    https://example.com/api/login
done | sort | uniq -c
# Un stream limpio de 200s más allá del rate limit documentado confirma el bypass.
```

### Confirmar que el backend rechaza headers forwarded de IPs no-proxy

```bash
# El mejor test si tenés acceso directo a la IP del origin. Spoofeá XFF sobre el
# camino directo; un backend correctamente configurado debería ignorar el header por completo.
curl -k --resolve example.com:443:<origin-ip> https://example.com/whoami \
  -H "X-Forwarded-For: 1.2.3.4"
# Si la response muestra 1.2.3.4 como la IP del cliente, el backend está leyendo
# headers forwarded desde internet pública — bug de desacuerdo-de-confianza completo.
```

## Ejemplos prácticos
- Una API de Express corre `app.set('trust proxy', true)` (booleano, no conteo). Cualquier cliente puede spoofear `X-Forwarded-For` y el framework lo trata como el origen. El middleware de rate-limiter usa `req.ip` como clave; el abuso se vuelve trivial.
- Una allowlist de admin de Django permite `127.0.0.1` y `10.0.0.0/8`. El backend lee `request.META['HTTP_X_FORWARDED_FOR']` directamente. El atacante envía `X-Forwarded-For: 10.0.0.5` desde internet pública y alcanza `/admin/`.
- Una app fronteada por Cloudflare lee `CF-Connecting-IP` para rate-limiting pero nunca verifica que la conexión vino de un rango de IP de Cloudflare. La IP del origin se filtra vía historial de DNS; el atacante bypassea el rate limit alcanzando el origin directamente *y* spoofeando `CF-Connecting-IP` para parecer fresco en cada request.
- Un proxy Nginx está configurado con `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for` (el default de agregar). El backend lee la IP de más a la izquierda. El atacante antepone `X-Forwarded-For: 1.2.3.4` y la cadena llega a la app como `1.2.3.4, <cliente-real>` — el backend loguea `1.2.3.4`.
- Un vendor de detección de fraude usa la IP de origen de la request como clave para los scores de riesgo. El vendor lee `X-Forwarded-For` directamente porque "el cliente nos lo dio". El atacante rota el header a un rango limpio; el score de riesgo colapsa.
- Un CDN incluye `X-Forwarded-For` en la clave de caché. El atacante refleja un payload vía el header en una response cacheable y prepara una entrada de caché por-IP que las requests posteriores con el mismo valor forjado recuperan.

## Notas relacionadas
- [[reverse-proxies|Reverse proxies]] — la clase de desacuerdo-de-confianza vive acá; esta nota es su especialización específica para los headers de IP forwarded.
- [[http-headers|Headers HTTP]] — semántica de headers, hop-by-hop vs end-to-end, rarezas de normalización de nombre de header.
- [[http-messages|Mensajes HTTP]] — el formato de wire que el proxy y el backend parsean cada uno.
- [[load-balancers|Load balancers]] — la misma superficie de traducción-de-confianza; los LBs típicamente también inyectan `X-Forwarded-For`.
- [[caching-and-security|Caché y seguridad]] — XFF en claves de caché se vuelve una primitiva de poisoning.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — la mitad de capa-de-red de la defensa de edge.
- [[cybersecurity/api-security/api-rate-limiting|Rate limiting de APIs]] — el consumidor directo más común de la confianza en la IP del cliente.
- [[cybersecurity/web-security/business-logic-vulnerabilities|Vulnerabilidades de lógica de negocio]] — los controles de abuso basados en IP son lógica de negocio; spoofearlos es una falla de lógica enraizada en la traducción de confianza.
- [[cybersecurity/security-playbooks/test-client-ip-spoofing|Testear el spoofing de IP de cliente]]

### Notas atómicas futuras sugeridas
- [[forwarded-header-spec|Spec del header Forwarded]]
- [[trust-proxy-configuration|Configuración de trust proxy]]
- [[origin-ip-discovery|Descubrimiento de IP de origin]]
- [[ip-allowlist-design|Diseño de allowlist de IP]]
- [[ipv6-forwarding-quirks|Rarezas de forwarding en IPv6]]
- [[bgp-route-hijack-and-source-ip|BGP route-hijack y la IP de origen]]

## Referencias
- **Foundational:** MDN X-Forwarded-For — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
- **Foundational:** RFC 7239 (Forwarded HTTP Extension) — https://datatracker.ietf.org/doc/html/rfc7239
- **Testing / Lab:** PortSwigger Web Security Academy — https://portswigger.net/web-security
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning
