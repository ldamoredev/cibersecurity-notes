---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - caching
  - http
sources: []
---

# Caché y seguridad

## Definición
El caché es el reuso de responses generadas previamente por navegadores, CDNs, reverse proxies, intermediarios compartidos o capas de aplicación. El caché se vuelve un problema de seguridad cuando una response se almacena, se le hace clave, se varía o se invalida de forma distinta a como la aplicación espera.

## Por qué importa
El caché se sienta entre la semántica de HTTP y el comportamiento de la infraestructura. Una response que es segura para un usuario, idioma, host o contexto de autorización puede ser insegura para otro. Los bugs de caché son especialmente peligrosos porque una request puede afectar a muchos usuarios posteriores.

La lección recurrente: **la clave de caché es parte de la frontera de seguridad**. Si el origin lee una señal por la que el caché no varía, el caché puede servirle la interpretación de un usuario a otro usuario.

## Cómo funciona
El caché HTTP responde **4 preguntas**:

1. **¿Esta response puede almacenarse?** `Cache-Control`, status code, método, autenticación y la política del CDN deciden si un caché puede guardarla.
2. **¿Quién puede almacenarla?** El caché del navegador, el proxy compartido, el edge del CDN, el caché de aplicación y el caché surrogate tienen perfiles de riesgo distintos.
3. **¿Cuál es la clave de caché?** La URL suele ser la baseline, pero `Host`, query string, headers seleccionados, cookies y reglas del CDN pueden incluirse o ignorarse.
4. **¿Cuándo se reusa o invalida?** TTL, `max-age`, `s-maxage`, `ETag`, `Last-Modified`, APIs de purge y la revalidación deciden la vida útil.

Response sensible de ejemplo:

```http
GET /account HTTP/1.1
Host: app.example.com
Cookie: __Host-session=alice
Accept-Language: en
```

```http
HTTP/1.1 200 OK
Cache-Control: public, max-age=600
Content-Type: text/html

Alice's billing dashboard
```

Si un CDN compartido almacena esa response bajo solo `Host + path`, el próximo usuario que pida `/account` puede recibir la página de Alice. El bug no es "existe un CDN"; el bug es dejar que contenido personalizado entre a un caché compartido sin una clave segura o `no-store`.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- `Cache-Control`, `Pragma`, `Expires`, `Age`, `ETag`, `Last-Modified` y `Vary`
- headers de CDN como `X-Cache`, `CF-Cache-Status`, `X-Served-By`, `X-Cache-Hits`, `Fastly-Cachetype`
- responses autenticadas que no tienen `Cache-Control: no-store`
- responses que varían por `Cookie`, `Authorization`, `Origin`, `Accept-Language`, `X-Forwarded-Host` o headers de dispositivo
- inputs sin clave reflejados en las responses
- redirects y errores cacheados más ampliamente de lo previsto
- diferencias de normalización de path/query entre el caché y el origin
- flujos de purge e invalidación para contenido sensible

## Variantes y bypasses
Las fallas de caché caen en **6 clases prácticas**.

### 1. Caché de response sensible
Páginas autenticadas, datos de cuenta, responses de API, páginas de reset de contraseña o vistas de admin son almacenadas por un navegador o intermediario compartido. La defensa es `Cache-Control: no-store` en las responses verdaderamente sensibles, no esperar que el caché entienda la auth.

### 2. Web cache poisoning
Un atacante cambia un input sin clave que el origin refleja, y después el caché almacena la salida envenenada bajo una clave que las víctimas posteriores pegan. Inputs comunes: `X-Forwarded-Host`, `Host`, `X-Original-URL`, `Accept-Language`, parámetros de query y rarezas de normalización de path.

### 3. Cache deception
El caché cree que una request es para un recurso estático, mientras el origin sirve contenido dinámico personalizado. Forma clásica: `/account/settings/profile.css` se cachea porque el path parece estático.

### 4. Desajuste de clave entre capas
El navegador, CDN, reverse proxy y los cachés de aplicación usan claves distintas. Una capa varía por `Accept-Encoding`, otra por `Cookie`, otra solo por URL. El bug de seguridad aparece en la capa que ignora una señal en la que el origin confía.

### 5. Estado de autorización obsoleto
Permisos, membresía, feature flags o propiedad de objetos cambian, pero las responses cacheadas siguen válidas. Esto puede exponer acceso revocado o datos viejos después del logout, la remoción de rol o la migración de tenant.

### 6. Caché de errores y redirects
Los errores, redirects y páginas de mantenimiento se cachean demasiado ampliamente. Un 302 temporal hacia un host hostil, un 500 con detalles de stack o una página de falla de auth pueden volverse persistentes para muchos usuarios.

## Impacto
Ordenado aproximadamente por severidad:

- **Divulgación de datos cross-usuario.** Responses personalizadas servidas desde caché compartido al usuario equivocado.
- **Compromiso del lado del cliente almacenado.** JavaScript, redirects o HTML cacheados envenenados afectan a muchas víctimas.
- **Bypass de autorización por contenido obsoleto.** Contenido revocado o específico de un tenant queda disponible después de un cambio de permisos.
- **Exposición de credenciales o tokens.** Links de reset, callbacks de OAuth, URLs firmadas o responses que cargan bearer se cachean.
- **Desinformación o defacement persistente.** El contenido envenenado sobrevive hasta la expiración del TTL o el purge.
- **Arrastre en la respuesta a incidentes.** Purgar cachés distribuidos es más lento y difícil que arreglar el código del origin.

## Detección y defensa
Ordenado por efectividad:

1. **Marcá las responses sensibles con `Cache-Control: no-store`.**
   Las responses de cuenta, facturación, admin, que cargan sesión, que cargan tokens y las de API específicas del usuario no deberían entrar a cachés compartidos ni del navegador. `no-store` es la directiva más clara porque les dice a los cachés que no retengan la response en absoluto.

2. **Hacé las claves de caché explícitas y revisadas.**
   Documentá por qué hace clave cada capa de caché: host, path, query string, headers seleccionados, cookies, encoding, dispositivo, locale. Cualquier señal que el origin lea y que esté ausente de la clave es un candidato a poisoning.

3. **Deshabilitá el caché compartido para el tráfico autenticado por defecto.**
   `Authorization` y `Cookie` normalmente deberían empujar las responses fuera del caché compartido salvo que la ruta sea deliberadamente pública y la política de clave esté probadamente segura.

4. **Usá `Vary` solo cuando el caché realmente lo honra.**
   `Vary: Origin`, `Vary: Accept-Language` o `Vary: Cookie` pueden ser correctos, pero solo si cada intermediario relevante lo respeta. Las reglas del CDN a menudo sobrescriben o comprimen el comportamiento de `Vary`.

5. **Normalizá en el edge y el origin de forma consistente.**
   La decodificación de path, las barras finales, los puntos y comas, el casing, la normalización de query y el manejo de extensiones de archivo deberían coincidir. La cache deception y el poisoning a menudo vienen de normalización desajustada.

6. **Purgá por surrogate keys o identificadores precisos.**
   La invalidación sensible no debería depender de purges amplios con wildcard ni de esperar a que expiren los TTLs. Usá surrogate keys de ruta/objeto donde el CDN los soporte.

7. **Logueá el estado de caché con contexto de seguridad.**
   Registrá HIT/MISS/BYPASS, los inputs de la clave de caché, el estado autenticado vs anónimo y los headers seleccionados. Sin visibilidad del caché, las fugas parecen bugs de autorización aleatorios.

### Qué no funciona como defensa primaria

- **Asumir que `private` significa sin caché del navegador.** `private` previene que los cachés compartidos almacenen; los cachés del navegador todavía pueden almacenar. Usá `no-store` para contenido verdaderamente sensible.
- **Confiar en `Vary: *`.** Muchos intermediarios no lo manejan como una frontera de seguridad útil. Usá una política de caché explícita en su lugar.
- **Poner secretos en query strings y esperar que HTTPS los oculte.** Las URLs aparecen en cachés, logs, historial del navegador, referers y tooling de CDN.
- **Confiar en los defaults del CDN.** Los productos de CDN están optimizados para rendimiento. El comportamiento de caché sensible a la seguridad debe configurarse intencionalmente.
- **Testear solo una request.** Los bugs de caché necesitan al menos dos perspectivas: envenenar/almacenar como una request, después recuperar como otro usuario o conjunto de headers.

## Labs prácticos
Corré solo contra sistemas que sean tuyos o que estés autorizado a testear.

### Inventariar los headers relacionados con caché

```bash
curl -skI https://app.example.com/ | rg -i \
  '^(cache-control|pragma|expires|age|etag|last-modified|vary|x-cache|cf-cache-status|x-served-by):'
```

Registrá si la response es public, private, no-store, revalidada o servida por CDN.

### Comparar responses anónimas y autenticadas

```bash
curl -skI https://app.example.com/account | rg -i '^(cache-control|vary|x-cache|cf-cache-status):'
curl -skI -b /tmp/app.cookies https://app.example.com/account | rg -i '^(cache-control|vary|x-cache|cf-cache-status):'
```

Las responses autenticadas no deberían ser almacenadas por cachés compartidos salvo que estén explícitamente diseñadas y con clave segura.

### Sondear el reflejo de headers sin clave

```bash
curl -sk https://app.example.com/ \
  -H 'X-Forwarded-Host: poison.example' \
  -H 'X-Original-URL: /poison-probe' \
  | rg -i 'poison.example|poison-probe'
```

Si la response refleja el header, chequeá si la clave de caché incluye ese header antes de considerar el impacto.

### Testear una forma de poisoning de dos requests

```bash
url='https://app.example.com/?cache_probe=1'

curl -skI "$url" -H 'X-Forwarded-Host: poison.example' | rg -i 'x-cache|cf-cache-status|age'
curl -sk  "$url" | rg -i 'poison.example|x-cache|cf-cache-status|age'
```

La primera request intenta almacenar; la segunda chequea si una request con forma de víctima sin modificar recibe contenido influido por el atacante.

### Chequear candidatos a cache deception

```bash
for suffix in profile.css account.js settings.png; do
  curl -skI "https://app.example.com/account/$suffix" | rg -i 'http/|content-type|cache-control|x-cache|cf-cache-status'
done
```

Vigilá contenido dinámico servido bajo paths de apariencia estática con headers cacheables.

### Inspeccionar el comportamiento de invalidación

```bash
# Fetch, cambiar el objeto subyacente a través de la app, después fetch de nuevo.
curl -skI https://app.example.com/resource/123 | rg -i 'etag|last-modified|cache-control|x-cache|age'
```

El punto es comparar la frescura esperada con el reuso real del caché, no solo los headers en aislamiento.

## Ejemplos prácticos
- `/account` devuelve `Cache-Control: public, max-age=600`, y un CDN le sirve el dashboard de un usuario a otro.
- El origin refleja `X-Forwarded-Host` en los links canónicos, pero el CDN solo usa la URL como clave, creando web cache poisoning.
- `/profile/avatar/../../settings.css` es normalizado distinto por el caché y el origin, causando que datos dinámicos de la cuenta se cacheen como CSS.
- Un logout revoca la sesión pero el botón "atrás" del navegador muestra datos de facturación cacheados.
- Un redirect de `/login` a un dominio específico de tenant se cachea y se reusa entre tenants.

## Notas relacionadas
- [[http-headers|Headers HTTP]] — semántica de `Cache-Control`, `Vary` y los headers de cache-status.
- [[http-messages|Mensajes HTTP]] — los headers crudos y la forma de la request que el caché parsea.
- [[reverse-proxies|Reverse proxies]] — los cachés a menudo viven en la frontera proxy/CDN.
- [[client-ip-trust|Confianza en la IP del cliente]] — los headers forwarded se vuelven inputs de poisoning cuando no tienen clave.
- [[cookies-and-sessions|Cookies y sesiones]] — las responses personalizadas respaldadas por cookies no deben cachearse incorrectamente.
- [[load-balancers|Load balancers]] — los puntos de entrada pueden rutear a distintas capas de caché.
- [[cybersecurity/web-security/request-smuggling|Request smuggling]] — el desacuerdo de parsers puede envenenar colas y cachés.

### Notas atómicas futuras sugeridas
- [[web-cache-poisoning|Web cache poisoning]]
- [[cache-deception|Cache deception]]
- [[cache-control-semantics|Semántica de Cache-Control]]
- [[vary-header|El header Vary]]
- [[surrogate-keys|Surrogate keys]]
- [[cdn-cache-key-design|Diseño de clave de caché de CDN]]

## Referencias
- **Foundational:** MDN HTTP caching — https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- **Foundational:** MDN Cache-Control — https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
- **Testing / Lab:** PortSwigger Web Cache Poisoning — https://portswigger.net/web-security/web-cache-poisoning
- **Research / Deep Dive:** James Kettle, "Practical Web Cache Poisoning" — https://portswigger.net/research/practical-web-cache-poisoning
