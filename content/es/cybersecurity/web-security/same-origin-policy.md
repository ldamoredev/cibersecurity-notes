---
type: concept
status: active
created: 2026-06-03
updated: 2026-06-03
tags:
  - cybersecurity
  - web-security
  - same-origin-policy
  - browser-security
  - cors
sources: []
---

# Política del mismo origen (SOP)

## Definición
La política del mismo origen (SOP, same-origin policy) es la regla de aislamiento fundamental del navegador: un script corriendo en un **origen** puede leer libremente el contenido, el DOM y el estado guardado de otro recurso *solo si* ese recurso comparte su origen — de lo contrario el navegador bloquea la lectura. Un **origen** es la tupla **(esquema, host, puerto)**; los tres deben coincidir exactamente. La SOP es la frontera default-deny que toda otra mecánica de aislamiento web (CORS, CORP/COEP/COOP, cookies, `postMessage`) relaja o refuerza. Si entendés una sola primitiva de seguridad web, debería ser esta.

## Por qué importa
La SOP es *la* razón por la que una pestaña maliciosa no puede leer tu webmail ni drenar tu sesión bancaria mientras navegás en otro lado. Casi toda clase de vulnerabilidad web se entiende mejor como "qué pasa en, o alrededor de, la frontera de la SOP":

- **Define la frontera de confianza sobre la que discute el resto de la seguridad web.** XSS importa porque corre código *dentro* de un origen (derrotando la SOP desde adentro); CORS importa porque *relaja* el bloqueo de lectura de la SOP; CSRF importa porque la SOP *no* bloquea los *envíos* cross-origin. No podés razonar sobre ninguno sin la SOP como baseline.
- **Su asimetría central — enviar está permitido, leer está bloqueado — es la semilla de dos clases enteras de bug.** El navegador *envía* una request cross-origin (y adjunta cookies, para algunas), ejecuta sus efectos secundarios, y luego le retiene la response al script. "Enviar permitido" pare CSRF; "lectura controlada" pare CORS; "observar-sin-leer" pare los XS-leaks.
- **Es de coincidencia-exacta e implacable, que es donde viven los errores.** `https://app.example.com` y `https://api.example.com` son orígenes *distintos*; también lo son `http://` vs `https://`, y `:443` vs `:8443`. La mayoría de las vulnerabilidades cross-origin reales son un desarrollador ensanchando accidentalmente esta frontera (CORS reflejado, `postMessage` descuidado, `document.domain`, subdomain takeover).

## Cómo funciona
La SOP gobierna **3 superficies de acceso**, y en cada una el default es negar-entre-orígenes:

1. **Lecturas de red.** Un script puede *enviar* una request cross-origin pero no puede *leer* la response salvo que el target opte por entrar vía CORS.
2. **Acceso al DOM.** Un script en un frame/ventana no puede leer el DOM ni el estado JS de un frame/ventana cross-origin.
3. **Almacenamiento.** `localStorage`, `sessionStorage` e IndexedDB están particionados por origen. (**Las cookies son la excepción famosa** — se indexan por *sitio/dominio*, no por origen, que es exactamente por lo que existe CSRF.)

Dos URLs son del mismo origen sí y solo sí esquema, host y puerto coinciden todos — path y query son irrelevantes:

| URL A | URL B | ¿Mismo origen? | Por qué |
|---|---|---|---|
| `https://app.example.com/a` | `https://app.example.com/b` | ✅ | el path no cuenta |
| `https://app.example.com` | `http://app.example.com` | ❌ | difiere el esquema |
| `https://app.example.com` | `https://api.example.com` | ❌ | difiere el host |
| `https://app.example.com` | `https://app.example.com:8443` | ❌ | difiere el puerto |
| `http://example.com` | `http://example.com:80` | ✅ | `:80` es el default de http |

La asimetría que sostiene la estructura — el navegador **envía** la request pero la SOP **bloquea la lectura**:

```js
// Página corriendo en https://evil.example
fetch('https://bank.example/account', { credentials: 'include' })
  .then(r => r.text())     // la SOP bloquea leer el body salvo que bank.example
  .then(console.log);      // devuelva headers CORS — el script obtiene un TypeError / response opaca
```
La request *fue enviada* (y las cookies de `bank.example` pueden haber viajado, ejecutando cualquier efecto secundario); la SOP solo impide que el script de `evil.example` *vea* la response. El bug no es "la request ocurrió" — es si la lectura, el acceso al DOM o el almacenamiento cruzaron la línea del origen.

## Técnicas / patrones
Qué sondea un atacante — cada sonda busca un lugar donde la frontera del origen se ensanchó accidentalmente:

- **Cazá las relajaciones, no la SOP misma.** La SOP es robusta; sus *opt-outs* son donde viven los bugs: CORS reflejado/`null`/wildcard con credenciales, handlers de `postMessage` sin chequeo de `event.origin`, relajación de `document.domain`, endpoints JSONP.
- **Explotá la asimetría enviar/leer.** Los *envíos* cross-origin están permitidos → CSRF. Las *observaciones* cross-origin (eventos load/error, conteos de frames, timing, dimensiones) están permitidas → los XS-leaks infieren estado cross-origin sin leer bodies.
- **Distinguí same-origin de same-site.** Las cookies, `SameSite` y CORP se indexan por *sitio* (eTLD+1), no por origen. `a.example.com` y `b.example.com` son cross-origin pero same-site — una distinción que los atacantes weaponizan.
- **Perseguí el subdomain takeover.** Si `cdn.example.com` está colgante y es reclamable por el atacante, un origen "confiable" same-site se vuelve hostil, derrotando cualquier confianza indexada por sitio.
- **Recordá que XSS es el trabajo desde adentro.** La SOP protege *entre* orígenes; un XSS que ejecuta *dentro* del origen target posee todo lo que la SOP estaba protegiendo.

## Variantes y bypasses
La SOP viene con **5 relajaciones sancionadas**, cada una un agujero deliberado — y cada una una clase de bug cuando se mal-usa.

### 1. CORS (Cross-Origin Resource Sharing)
El servidor opta por entrar a las lecturas cross-origin con `Access-Control-Allow-Origin`. Las malas configuraciones — reflejar el `Origin` de la request mientras se permiten credenciales, aceptar `null`, o confiar en subdominios wildcard — reabren exactamente la lectura que la SOP bloqueó. Ver [[cors-misconfiguration|Mala configuración de CORS]].

### 2. postMessage
El canal sancionado para mensajería entre ventanas cross-origin. Un receptor que no valida `event.origin`, o un emisor que usa `targetOrigin: '*'`, filtra datos entre orígenes o le entrega al atacante un sink de DOM-XSS.

### 3. document.domain (deprecado / deshabilitado por defecto)
Dos páginas bajo un dominio padre compartido podían antes setear `document.domain` para volverse "same-origin". Los navegadores modernos lo deshabilitan por defecto (ahora requiere optar por salir de Origin-Agent-Cluster). Un footgun legacy que colapsa el origen a sitio.

### 4. Embedding cross-origin (la asimetría leer/escribir)
La SOP deja a una página *embeber* recursos cross-origin (`<img>`, `<script>`, `<iframe>`, `<link>`) y *enviar* formularios — sin leerlos. Esta regla sancionada de "escribir/embeber permitido, leer bloqueado" es precisamente lo que hace posibles CSRF y XS-leaks.

### 5. JSONP (legacy)
Un hack pre-CORS: traer datos cross-origin como un `<script>` que invoca un callback, esquivando la SOP por diseño. Un peligro de inyección y exfiltración de datos donde sobreviva.

## Impacto
Ordenado por severidad, para cuando una relajación se mal-usa (o la frontera colapsa de otro modo):

- **Robo de datos cross-origin.** Una mala config de CORS deja a un origen atacante leer responses autenticadas — datos de cuenta, PII, tokens anti-CSRF.
- **XSS basado en DOM.** Un handler de `postMessage` que confía en input del atacante y lo escribe al DOM rinde ejecución de código dentro del origen víctima.
- **Session riding (CSRF).** La SOP permite la request cross-origin que cambia estado; sin `SameSite`/tokens la acción tiene éxito.
- **Inferencia cross-site (XS-leaks).** Estado de login, resultados de búsqueda o atributos de cuenta inferidos vía canales laterales permitidos por la SOP sin leer ningún body.
- **Compromiso total del origen.** Un subdomain takeover o un XSS dentro del origen derrotan la SOP por completo desde una posición confiable.

## Detección y defensa
Para una nota de concepto fundamental, "defensa" es *mantener intacta la frontera del origen*. Ordenado por efectividad:

1. **Tratá el origen como la frontera de seguridad y mantené los servicios sensibles en orígenes distintos.**
   La separación por origen es el aislamiento más fuerte que ofrece la plataforma; co-hostear niveles de confianza no relacionados en un origen lo tira. Poné el panel de admin, la API y el contenido de usuario en orígenes que puedas razonar independientemente.

2. **Asegurá cada relajación sancionada.**
   CORS: nunca reflejes `Origin` con `Access-Control-Allow-Credentials: true`, nunca permitas `null`, hacé allowlist de orígenes exactos. `postMessage`: validá `event.origin` contra una allowlist *y* seteá un `targetOrigin` explícito. No uses `document.domain`. Retirá JSONP. Cada relajación es una puerta que abriste — mantenela tan angosta como el caso de uso.

3. **Defendé la asimetría-de-envío por separado con cookies SameSite + tokens anti-CSRF.**
   Como la SOP *no* bloquea los envíos cross-origin, la frontera de la request necesita su propio control. Cookies `SameSite=Lax/Strict` más tokens CSRF por request la cierran. Ver [[csrf|CSRF]].

4. **Apilá los controles de frontera modernos encima.**
   `Cross-Origin-Resource-Policy`, COOP/COEP para aislamiento cross-origin, Origin-Agent-Cluster y CSP endurecen la frontera contra canales laterales y abuso de embedding — el tema de [[browser-security-boundaries|Fronteras de seguridad del navegador]].

5. **Prevení el subdomain takeover y mantené el XSS afuera.**
   Un subdominio colgante o un script inyectado dentro del origen derrotan todo lo de arriba; la higiene de DNS y el encoding de salida/CSP protegen la frontera del colapso desde adentro.

### Qué no funciona como defensa primaria
- **"La SOP frena CSRF".** El falso amigo canónico. La SOP bloquea la *lectura*, no el *envío* — la request cross-origin pasa con cookies. CSRF necesita `SameSite`/tokens, no la SOP.
- **"HTTPS vuelve las páginas same-origin".** El esquema es *parte* del origen, así que `http`↔`https` son cross-origin — pero TLS no define ni impone la frontera en sí.
- **"Son todos dominios de nuestra empresa, así que son same-origin".** Subdominios y puertos distintos son orígenes distintos. `app.example.com` ≠ `api.example.com`.
- **Oscuridad de orígenes internos.** Los hostnames inadivinables no son una frontera de aislamiento; la tupla del origen sí.

## Labs prácticos
Corré solo contra sistemas que sean tuyos o que estés autorizado a testear. La mayoría corren en la consola de las DevTools del navegador.

### Observar el envío/bloqueo de lectura
```js
// En la consola de cualquier página https, fetcheá un endpoint cross-origin:
fetch('https://example.com/', { mode: 'cors' })
  .then(r => r.text()).then(console.log)
  .catch(e => console.log('SOP/CORS bloqueó la lectura:', e.message));
// La request sale del navegador; la lectura falla salvo que el target envíe headers CORS.
```

### Sondear un reflejo de allow-origin de CORS
```bash
curl -sD - -o /dev/null https://app.example.com/api/me \
  -H 'Origin: https://evil.example'
# Buscá: Access-Control-Allow-Origin: https://evil.example  (reflejado = malo)
#        Access-Control-Allow-Credentials: true             (con reflejo = crítico)
```

### Confirmar que el acceso al DOM cross-frame está bloqueado
```js
// Embebé un iframe cross-origin, luego intentá leer su documento:
const f = document.createElement('iframe');
f.src = 'https://example.com/'; document.body.appendChild(f);
f.onload = () => { try { console.log(f.contentDocument.body.innerHTML); }
                   catch (e) { console.log('SOP bloqueó el acceso al DOM:', e.message); } };
```

### Testear el chequeo de origen de un listener de postMessage
```js
// Si una página registra window.addEventListener('message', ...), enviale una sonda
// desde un origen distinto y mirá si actúa sobre los datos sin chequear event.origin.
targetWindow.postMessage({probe: 'x'}, '*');   // un handler seguro debe rechazar orígenes desconocidos
```

## Ejemplos prácticos
- **Robo por CORS de origen-reflejado.** `app.example.com` refleja cualquier `Origin` y permite credenciales; `evil.example` lee el `/api/me` autenticado de la víctima, exfiltrando datos de cuenta y el token CSRF.
- **DOM XSS por postMessage.** Un widget escucha eventos `message` y hace `innerHTML` de `event.data` sin chequear `event.origin`; un frame atacante postea un payload y obtiene ejecución de script en el origen del widget.
- **CSRF funcionando *por* el permiso de la SOP.** Un formulario oculto auto-submit hace POST a `bank.example/transfer`; la SOP permite el envío cross-origin y la cookie viaja — la transferencia tiene éxito sin necesidad de lectura.
- **Subdomain takeover colapsa la frontera.** Un CNAME `cdn.example.com` colgante es reclamado por un atacante; los scripts que la app principal confía desde ese origen "same-site" ahora corren código hostil.
- **XS-leak vía embedding.** Un atacante framea `victim.example/search?q=secret` y mide el load o cuenta subframes para inferir si la query coincidió — inferencia cross-site con cero lecturas de body.

## Notas relacionadas
- [[cors-misconfiguration|Mala configuración de CORS]] — la relajación #1; la forma más común en que se reabre mal el bloqueo de lectura de la SOP.
- [[csrf|CSRF]] — el bug que existe *porque* la SOP permite el envío cross-origin.
- [[content-security-policy|Content Security Policy]] — defensa en profundidad dentro del origen una vez que el XSS amenaza la frontera desde adentro.
- [[clickjacking|Clickjacking]] — un ataque de framing/UI-redress contra el que defienden los controles de frontera (`frame-ancestors`).
- [[xss|XSS]] — el "trabajo desde adentro" que derrota la SOP desde dentro del origen.
- [[browser-security-boundaries|Fronteras de seguridad del navegador]] — el sistema multi-control moderno (site-vs-origin, COOP/COEP/CORP, aislamiento) apilado encima de la SOP.
- [[cybersecurity/networking/cookies-and-sessions|Cookies y sesiones]] — por qué las cookies siguen un modelo de *sitio*, no el modelo de origen, y qué cuesta eso.
- [[cybersecurity/networking/http-headers|Headers HTTP]] — donde viven realmente los headers CORS/CORP/COOP que modifican la SOP.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — la SOP es el muro del defensor; las relajaciones son donde mira el operador.

### Notas atómicas futuras sugeridas
- [[browser-security-boundaries|Fronteras de seguridad del navegador]]
- [[xs-leaks-and-cross-site-inference|XS-leaks e inferencia cross-site]]
- [[postmessage-security|Seguridad de postMessage]]
- [[site-vs-origin-and-samesite-cookies|Site vs origin y cookies SameSite]]
- [[cross-origin-isolation-coop-coep-corp|Aislamiento cross-origin: COOP/COEP/CORP]]

> Las notas atómicas futuras se listan como `[[wikilinks]]` aunque el archivo destino todavía no exista, para que registren como forward-links en Obsidian.

## Referencias
- **Foundational:** RFC 6454 — The Web Origin Concept — https://www.rfc-editor.org/rfc/rfc6454
- **Foundational:** MDN — Same-origin policy — https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy
- **Testing / Lab:** PortSwigger Web Security Academy — Cross-origin resource sharing (CORS) — https://portswigger.net/web-security/cors
