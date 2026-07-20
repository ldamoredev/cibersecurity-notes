---
type: concept
status: active
created: 2026-06-03
updated: 2026-06-03
tags:
  - cybersecurity
  - web-security
  - browser-security
  - cross-origin-isolation
  - xs-leaks
  - same-origin-policy
sources: []
---

# Fronteras de seguridad del navegador

## Definición
Las "fronteras de seguridad del navegador" son el **stack en capas de fronteras de aislamiento** que un navegador moderno impone entre contenido web — no una sola regla sino cinco fronteras que operan a distintas granularidades: **origen** (acceso de script), **sitio** (estado), **proceso** (memoria), **agent cluster** (APIs poderosas) y **partición de almacenamiento** (estado cross-site). La [[same-origin-policy|política del mismo origen]] es la más interna de estas; las otras se agregaron (mayormente 2019–2025, aceleradas por Spectre y por el trabajo de privacidad) porque el aislamiento a nivel de origen por sí solo ya no aguanta contra los canales laterales especulativos y el tracking cross-site. Un "bypass de seguridad del navegador" es casi siempre *encontrar la única capa de este stack que no aguantó*.

## Por qué importa
Para 2026 el navegador post-Spectre, post-Privacy-Sandbox es el sandbox más atacado del planeta, y su seguridad ya no se explica solo con la SOP. Tres lecciones transferibles:

- **Distintos controles se indexan en distintas fronteras, y las costuras son los bugs.** La SOP y Origin-Agent-Cluster se indexan en *origen*; las cookies, CORP y la partición de almacenamiento se indexan en *sitio* (eTLD+1). `a.example.com` y `b.example.com` son orígenes distintos pero el *mismo sitio* — así que un control que asumiste era por-origen en realidad puede confiar en un subdominio hermano. La mayoría de los bugs de frontera viven en una costura donde una frontera gruesa se confía como si fuera de grano fino.
- **Spectre movió la frontera real del lenguaje al proceso del SO.** La ejecución especulativa puede leer a través del heap JS in-process, derrotando cualquier aislamiento a nivel de lenguaje. La respuesta estructural del navegador fue **Site Isolation** — poner distintos sitios en distintos procesos del SO — y el **aislamiento cross-origin** (COOP+COEP) para re-habilitar de forma segura las APIs de timing poderosas. La frontera de memoria ahora es una frontera de *proceso*, que es por qué los sandbox escapes de renderer importan tanto como los bugs web.
- **La SOP bloquea lecturas, no observaciones — así que la clase de ataque moderna es la inferencia, no el robo.** Los cross-site leaks (XS-leaks) infieren estado cross-origin a través de efectos secundarios permitidos por la SOP (timing, conteos de frames, eventos de error, caché). El stack de fronteras existe en gran parte para cerrar estos canales laterales, y la ofensa de 2025–26 es la búsqueda del canal lateral que un sitio dado se olvidó de cerrar.

Esta es la compañera de frontera-moderna de [[same-origin-policy|la política del mismo origen]]; la SOP es la regla, esta nota es el sistema construido sobre ella.

## Cómo funciona
El stack de fronteras, de la más interna a la más externa — **5 fronteras**:

| Frontera | Granularidad | Impone | Mecanismo clave |
|---|---|---|---|
| **Origen** | esquema+host+puerto | acceso de script lectura/DOM/almacenamiento | [[same-origin-policy\|política del mismo origen]] |
| **Sitio** | esquema + eTLD+1 | scope de cookie/estado, CORP `same-site` | Public Suffix List |
| **Proceso** | sitio (u origen) | aislamiento de memoria vs Spectre | Site Isolation, Origin-Agent-Cluster |
| **Agent cluster** | cross-origin-isolated | acceso a SAB + timers precisos | COOP + COEP |
| **Partición de almacenamiento** | (top-site, embedded-site) | estado/tracking cross-site | CHIPS, Storage Access API |

La mecánica que las une:

1. **Origen vs sitio.** El origen es la tupla de la SOP; el *sitio* es el esquema + el dominio registrable (eTLD+1, derivado de la Public Suffix List). Las cookies, `Cross-Origin-Resource-Policy: same-site` y la partición de almacenamiento operan a granularidad de sitio — más gruesa que el origen.
2. **Aislamiento de proceso (la respuesta de Spectre).** Como una lectura especulativa puede cruzar la frontera in-process, **Site Isolation** ubica distintos sitios en distintos procesos de renderer para que la especulación de un sitio no pueda alcanzar la memoria de otro. **Origin-Agent-Cluster (`Origin-Agent-Cluster: ?1`)** pide aislamiento indexado-por-origen (en vez de por-sitio) y deshabilita `document.domain`.
3. **Aislamiento cross-origin.** `SharedArrayBuffer` y los timers de alta resolución se deshabilitaron tras Spectre porque construyen relojes precisos de canal lateral. Un documento los re-habilita solo volviéndose *cross-origin isolated*: `Cross-Origin-Opener-Policy: same-origin` **y** `Cross-Origin-Embedder-Policy: require-corp`, que juntos garantizan que ningún recurso cross-origin no-opt-in comparta su proceso.
4. **CORP y COOP como los bloques de construcción.** `Cross-Origin-Resource-Policy` deja a un *recurso* declarar quién puede embeberlo (`same-origin`/`same-site`/`cross-origin`), bloqueando la inclusión cross-origin especulativa. `Cross-Origin-Opener-Policy` corta el enlace `window.opener` entre documentos top-level cross-origin, cerrando las fugas cross-window.
5. **Partición de almacenamiento.** Las cookies y el almacenamiento se indexan cada vez más por *(sitio top-level, sitio embebido)* para que un iframe de terceros no pueda compartir estado entre los sitios que lo embeben; **CHIPS** (`Set-Cookie: ...; Partitioned`) es el opt-in, y la **Storage Access API** otorga excepciones acotadas.

Los headers que lo activan, en un bloque:

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Resource-Policy: same-origin
Origin-Agent-Cluster: ?1
# COOP + COEP  =>  self.crossOriginIsolated === true  =>  SharedArrayBuffer re-habilitado
```

La frontera es un stack — origen para acceso de script, sitio para estado, proceso para memoria, agent-cluster para APIs poderosas, partición para estado cross-site. La seguridad aguanta solo mientras *cada* capa de la que dependen los datos aguante.

## Técnicas / patrones
Qué sondea un atacante:

- **Encontrá la frontera más gruesa que confía el target.** Si un control se indexa en *sitio*, un subdominio hermano (o un subdomain takeover) está adentro. La confusión site-vs-origin es la costura de mayor rendimiento.
- **Minar las observaciones permitidas por la SOP para XS-leaks.** El timing de response, los conteos de frames/`window.length`, el hit/miss de caché, los eventos `onload`/`onerror`, `history.length`, el sondeo de COOP/COEP y el estado `crossOriginIsolated` filtran todos bits cross-origin/cross-site sin leer ningún body.
- **Cazar headers de aislamiento faltantes.** La ausencia de CORP/COOP/COEP significa que los recursos pueden incluirse especulativamente y las ventanas pueden retener `opener` — las precondiciones para lecturas de canal lateral y fugas cross-window.
- **Buscar SAB sin aislamiento.** Cualquier camino que exponga `SharedArrayBuffer` o un timer preciso *sin* aislamiento cross-origin completo reabre el reloj de Spectre.
- **Encadenar a un sandbox escape.** La frontera de proceso es la última línea; un bug de corrupción de memoria de renderer ([[cybersecurity/binary-exploitation/use-after-free-and-dangling-pointers|UAF]]/type confusion) más un bug de IPC/broker escapa Site Isolation por completo.

## Variantes y bypasses
Las **5 clases de presión** contra el stack de fronteras — cubriendo las técnicas nombradas de 2025–26 de la Q5.

### 1. XS-Leaks (cross-site leaks)
Inferir estado cross-origin/cross-site vía efectos secundarios permitidos por la SOP (timing, conteo de frames, sondeo de caché, eventos de error, comportamiento de COOP/COEP). La clase dominante de presión-de-frontera contra el modelo post-SOP — ataca la *observabilidad*, que la SOP nunca restringió.

### 2. Canales laterales especulativos clase-Spectre
La ejecución especulativa lee memoria a través de la frontera in-process. Neutralizada por la frontera de *proceso* (Site Isolation) y el aislamiento cross-origin; donde esos están ausentes — algunos navegadores móviles, WebViews embebidos, aislamiento mal configurado — las lecturas cross-origin in-process siguen siendo factibles.

### 3. Casos borde de reintroducción de SharedArrayBuffer
SAB + timers precisos son el amplificador de canal lateral, gateado detrás del aislamiento cross-origin. Casos borde los reabren: política empresarial re-habilitando SAB sin aislamiento, huecos de origin-trial, o rarezas de precisión de timer que reconstruyen un reloj usable a partir del timing de `performance.now()`/`postMessage`.

### 4. Renderer sandbox escape
La frontera de proceso la impone el sandbox del SO. Un RCE de renderer (UAF/type confusion) encadenado con un bug de IPC, broker o kernel escapa Site Isolation — la cadena de prestigio de Pwn2Own donde la seguridad de frontera-web se encuentra con la [[cybersecurity/binary-exploitation/memory-corruption|corrupción de memoria]].

### 5. Confusión site-vs-origin
Los controles indexados en *sitio* (cookies, CORP `same-site`) confían en todo origen same-site. Un solo XSS o subdomain takeover en cualquier subdominio hermano pivotea a través de la frontera de *sitio* — la capa gruesa es el eslabón débil del stack.

## Impacto
Ordenado por severidad:

- **Renderer escape → compromiso del dispositivo.** Una cadena de sandbox-escape rompe la frontera de proceso y corre fuera del navegador — el resultado de mayor impacto.
- **Lecturas de memoria cross-origin.** Un canal lateral de Spectre lee los secretos de otro sitio que comparte el mismo proceso (donde el aislamiento está ausente).
- **Inferencia de estado cross-site (XS-leaks).** Estado de login, atributos de cuenta, resultados de búsqueda o estado de admin inferidos a través de la frontera sin leer bodies.
- **Tracking / fuga de estado cross-site.** El almacenamiento sin particionar enlaza a un usuario a través de los sitios que embeben a un tercero.
- **Colapso de la defensa en profundidad.** Un control de granularidad-de-sitio confiado como si fuera de granularidad-de-origen es silenciosamente bypasseable vía un origen hermano.

## Detección y defensa
Cómo mantener intacto el stack de fronteras, ordenado por efectividad:

1. **Desplegá aislamiento cross-origin donde importa.**
   Seteá `COOP: same-origin` + `COEP: require-corp` para cualquier app que use `SharedArrayBuffer`/timers precisos o tenga datos sensibles cross-origin. Garantiza un proceso limpio y cierra los canales laterales de timer que SAB de otro modo habilitaría — el control individual más fuerte para apps de alto valor.

2. **Seteá CORP en los recursos.**
   `Cross-Origin-Resource-Policy: same-origin` (o `same-site`) impide que un recurso sea incluido especulativamente por una página cross-origin — la mitad del-lado-del-recurso de cerrar la inclusión de Spectre.

3. **Seteá COOP para cortar las relaciones de opener.**
   `Cross-Origin-Opener-Policy: same-origin` corta el canal `window.opener` entre documentos top-level cross-origin, cerrando una clase de XS-leaks cross-window incluso sin aislamiento completo.

4. **Optá por aislamiento indexado-por-origen; no relajes a sitio.**
   `Origin-Agent-Cluster: ?1` pide aislamiento de proceso por-origen y deshabilita `document.domain`. Nunca ensanches la frontera de vuelta a sitio vía `document.domain`.

5. **Rechazá las requests cross-site del lado del servidor con Fetch Metadata.**
   `Sec-Fetch-Site`/`Sec-Fetch-Mode` dejan al *servidor* ver y rechazar requests cross-site/cross-origin que nunca pretendió servir — una Resource Isolation Policy que mella muchos XS-leaks y CSRF en el origen.

6. **Particioná el estado y usá la Storage Access API.**
   Adoptá CHIPS (cookies `Partitioned`) y pedí acceso cross-site explícitamente vía la Storage Access API en vez de confiar en las cookies de terceros sin particionar legacy.

7. **Mantené el renderer duro.**
   Como la frontera de proceso es la última línea, las [[cybersecurity/binary-exploitation/exploit-mitigations|mitigaciones de seguridad de memoria]] (allocators endurecidos, MTE, CFI) son parte de la historia de fronteras del navegador, no algo separado.

### Qué no funciona como defensa primaria
- **Confiar solo en la SOP.** La SOP bloquea las *lecturas* cross-origin, no las *observaciones* que los XS-leaks explotan. El stack de fronteras existe precisamente porque la SOP es necesaria-pero-insuficiente.
- **Asumir que Site Isolation está en todos lados.** Los navegadores móviles y los WebViews embebidos pueden carecer de Site Isolation completo; no asumas que la frontera de proceso aguanta en toda plataforma.
- **Tratar sitio como igual a origen.** Los subdominios hermanos son same-site, no same-origin; los controles indexados-por-sitio confían en ellos.
- **Habilitar SharedArrayBuffer sin aislamiento cross-origin.** Esto reabre el canal lateral de timer-preciso que el requisito de aislamiento se agregó para cerrar.

## Labs prácticos
Corré solo contra sistemas que sean tuyos o que estés autorizado a testear. La mayoría corren en las DevTools.

### Chequear el aislamiento cross-origin y la disponibilidad de SAB
```js
console.log('crossOriginIsolated =', self.crossOriginIsolated);
try { new SharedArrayBuffer(8); console.log('SAB disponible'); }
catch (e) { console.log('SAB gateado:', e.message); }
// SAB debería estar disponible sí y solo sí crossOriginIsolated === true (COOP+COEP seteados).
```

### Inspeccionar los headers de frontera de un sitio
```bash
curl -sD - -o /dev/null https://app.example.com/ | rg -i \
  '^(cross-origin-opener-policy|cross-origin-embedder-policy|cross-origin-resource-policy|origin-agent-cluster|content-security-policy):'
# COOP/COEP/CORP faltantes = las fronteras de canal lateral no se están imponiendo.
```

### Distinguir origen de sitio
```js
// Para un conjunto de hosts, origen = esquema+host+puerto; sitio = esquema + eTLD+1.
// a.example.com y b.example.com: origen DISTINTO, MISMO sitio.
// app.example.com:443 y app.example.com:8443: origen DISTINTO, MISMO sitio.
// Los controles que se indexan en sitio confían en todas las filas same-site.
```

### Observar Fetch Metadata del lado del servidor
```bash
# Hacé una request cross-site vs same-origin y compará los headers Sec-Fetch-*
# que recibe el servidor — la base de una Resource Isolation Policy.
curl -s https://app.example.com/api -H 'Sec-Fetch-Site: cross-site' -D - -o /dev/null | rg -i 'HTTP/'
```

## Ejemplos prácticos
- **SAB re-habilitado sin aislamiento.** Una app activa `SharedArrayBuffer` para una feature de WebAssembly vía política empresarial pero nunca setea COOP/COEP; en un navegador móvil de proceso-compartido esto reintroduce un timer de grado-Spectre.
- **XS-leak por conteo de frames.** Una página atacante embebe `victim.example/search?q=secret` y lee `window.length` (conteo de subframes) para inferir si la query coincidió — inferencia de estado de login/admin sin lectura de body.
- **CORP faltante habilita pixel-reading.** Un sitio sirve imágenes sin CORP; una página cross-origin (pre-Site-Isolation) las incluye especulativamente para leer datos de píxeles vía un canal de timing.
- **Cadena de renderer escape.** Un UAF de type-confusion de V8 da RCE de renderer; un bug de IPC/broker luego escapa Site Isolation — la cadena canónica de Pwn2Own del navegador.
- **Pivot de subdominio-hermano.** Un XSS en `blog.example.com` abusa de un recurso `CORP: same-site` y una cookie host-only confiada a través de `*.example.com`, cruzando la frontera de *sitio* en la que la app se apoyaba implícitamente.

## Notas relacionadas
- [[same-origin-policy|Política del mismo origen]] — la frontera más interna y la regla sobre la que se construye este stack.
- [[cors-misconfiguration|Mala configuración de CORS]] — la capa de relajación-de-lectura; CORS se sienta al lado de CORP/COEP en el modelo cross-origin.
- [[content-security-policy|Content Security Policy]] — la capa de defensa in-origin que complementa las fronteras cross-origin.
- [[clickjacking|Clickjacking]] — `frame-ancestors`/`X-Frame-Options`, la frontera de embedding contra el UI redress.
- [[csrf|CSRF]] — SameSite + Fetch Metadata, los controles de frontera-de-request referenciados arriba.
- [[cybersecurity/networking/cookies-and-sessions|Cookies y sesiones]] — por qué las cookies son indexadas-por-sitio y cómo la partición (CHIPS) cambia eso.
- [[cybersecurity/binary-exploitation/use-after-free-and-dangling-pointers|Use-After-Free]] — la mitad de-bug-de-renderer de una cadena de sandbox-escape.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — el stack de fronteras es el muro; los XS-leaks y escapes son donde el operador lo sondea.

### Notas atómicas futuras sugeridas
- [[xs-leaks-and-cross-site-inference|XS-leaks e inferencia cross-site]]
- [[fetch-metadata-and-resource-isolation-policy|Fetch Metadata y Resource Isolation Policy]]
- [[partitioned-storage-and-chips|Almacenamiento particionado y CHIPS]]
- [[spectre-and-speculative-side-channels|Spectre y canales laterales especulativos]]
- [[renderer-sandbox-escapes|Renderer sandbox escapes]]

> Las notas atómicas futuras se listan como `[[wikilinks]]` aunque el archivo destino todavía no exista, para que registren como forward-links en Obsidian.

## Referencias
- **Foundational:** web.dev — Why you need "cross-origin isolated" for powerful features (COOP + COEP) — https://web.dev/articles/coop-coep
- **Foundational:** MDN — Cross-Origin-Resource-Policy (CORP) — https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy
- **Research / Deep Dive:** XS-Leaks Wiki — https://xsleaks.dev/
- **Foundational:** The Chromium Projects — Site Isolation — https://www.chromium.org/Home/chromium-security/site-isolation/
