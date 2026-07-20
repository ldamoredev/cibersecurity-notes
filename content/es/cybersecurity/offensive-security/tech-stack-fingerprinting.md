# Tech Stack Fingerprinting

## Definición

El tech stack fingerprinting es el proceso de inferir qué tecnologías, frameworks, CDNs, proxies, lenguajes, servicios y patrones de deployment usa un objetivo a partir de comportamiento observable y artefactos.

## Por qué importa

Conocer el stack cambia la estrategia de testing. Ayuda a acotar las estructuras de rutas probables, el comportamiento de parsers, los patrones de auth, los endpoints por defecto, las configuraciones de proxies y las clases de vulnerabilidades.

Mantenerlo separado de [[public-asset-discovery|Descubrimiento de Assets Públicos]]: esta nota es sobre qué parece correr en los assets, no simplemente cuáles assets existen.

## Cómo funciona

El fingerprinting usa **6 clases de señales**:

1. **Señales de protocolo.** Headers, TLS, versiones HTTP, redirects, cookies y comportamiento de status.
2. **Señales de contenido.** HTML, JavaScript, source maps, paths estáticos, comentarios y nombres de bundles.
3. **Señales de error.** Stack traces, páginas de error de frameworks, mensajes de validación y output de debug.
4. **Señales de routing.** Formas de URL, convenciones de API, GraphQL, REST, RPC y versionado.
5. **Señales de infraestructura.** CDN, WAF, reverse proxy, load balancer, proveedor cloud y pistas de origen.
6. **Señales de contexto público.** Docs, ofertas de trabajo, repos, nombres de paquetes y menciones de tecnología.

El problema no es que un stack sea detectable. El riesgo es filtrar detalles innecesarios que hacen más fácil el targeting y el chaining.

Un ejemplo trabajado, de fingerprint a elección de test:

```
Observed:
  x-powered-by: Express
  set-cookie: connect.sid
  bundle contains /api/v1/users/:id
  404 page differs behind CDN and direct origin

Inference:
  Node/Express app behind edge proxy with session cookie and object-ID API routes

Testing direction:
  API inventory + BOLA/IDOR route tests + proxy/header trust review
```

Un buen fingerprinting no se detiene en nombrar un framework; explica qué tests se vuelven más relevantes.

## Técnicas / patrones

Los operadores inspeccionan:

- headers y cookies de respuesta
- certificados TLS y comportamiento ALPN
- nombres de bundles JavaScript y source maps
- paths específicos de framework y assets estáticos
- páginas de error y patrones de status codes
- pistas de DNS/CDN/proxy
- docs, ofertas de trabajo y repositorios públicos

## Variantes y bypasses

El fingerprinting tiene **6 resultados comunes**.

### 1. Fingerprint de framework

Patrones de rutas, cookies, errores y assets sugieren Rails, Django, Express, Spring, Laravel, Next.js, etc.

### 2. Fingerprint de edge

Headers, TLS, DNS y comportamiento de caché revelan CDN, WAF, reverse proxy o load balancer.

### 3. Fingerprint de estilo de API

OpenAPI, GraphQL, convenciones REST, paths RPC y content types dan forma al testing.

### 4. Fingerprint de cloud/proveedor

Hostnames, certificados, rangos de IP, object storage y errores revelan servicios cloud.

### 5. Fingerprint de versión

Banners, assets, paths de paquetes y errores revelan versiones específicas.

### 6. Fingerprint engañoso

Los proxies, headers genéricos y páginas de error custom pueden ocultar o distorsionar la realidad del backend.

## Impacto

Ordenado aproximadamente por severidad:

- **Foco del testing.** El tester elige clases de vulnerabilidades probables y formas de payload.
- **Targeting de vulnerabilidades conocidas.** Los leaks de versión pueden mapear a CVEs o defaults de mala configuración.
- **Descubrimiento de rutas.** Las convenciones de framework revelan paths ocultos.
- **Testing consciente del proxy.** Los fingerprints de edge guían la revisión de request smuggling, caché y header-trust.
- **Validación de inventario defensivo.** El stack observado puede compararse con la arquitectura aprobada.

## Detección y defensa

Ordenado por efectividad:

1. **Reducí la divulgación gratuita del stack.**
   Evitá banners verbosos, errores de debug, source maps y páginas por defecto específicas de framework en producción.

2. **Parcheá y hardeá basándote en el stack real, no en el deseado.**
   El fingerprinting es más peligroso cuando las tecnologías observadas son no gestionadas u obsoletas.

3. **Normalizá el comportamiento de edge deliberadamente.**
   Los reverse proxies y CDNs no deberían filtrar accidentalmente diferencias del backend.

4. **Tratá los source maps y bundles públicos como artefactos de recon.**
   Pueden revelar rutas, frameworks y nombres internos incluso sin secretos.

5. **Monitoreá el drift tecnológico.**
   Los fingerprints de stack inesperados pueden revelar shadow apps o deploys viejos.

### Qué no funciona como defensa primaria

- **Ocultar headers solo.** El contenido, errores, rutas y comportamiento todavía revelan pistas del stack.
- **Security through obscurity.** Esconder versiones solo ayuda cuando el parcheo y los controles son reales.
- **Páginas de WAF genéricas.** Las diferencias del backend frecuentemente siguen siendo visibles a través de timing, rutas y errores.
- **Ignorar artefactos del lado cliente.** Los bundles y maps frecuentemente filtran más que los headers.

## Labs prácticos

Usá objetivos propios.

### Inspeccionar headers y cookies

```
curl -i https://app.example.test/ | rg -i "server|x-powered|set-cookie|via|cf-|x-cache"
```

Separar pistas de edge de pistas de backend.

### Buscar en bundles pistas de rutas y framework

```
rg -n "api/|graphql|next|webpack|vite|django|rails|laravel|spring" public dist
```

Los artefactos de cliente frecuentemente revelan más que la landing page.

### Comparar comportamiento de errores

```
curl -i https://app.example.test/does-not-exist-$(date +%s)
```

Las páginas de error pueden revelar el framework, el proxy y las capas de routing.

### Construir una tabla de evidencia de fingerprint

```
señal | valor observado | capa | confianza | implicación de test
```

Separar señales de edge, app, API y contexto público antes de sacar conclusiones.

### Comparar headers de edge y origen

```
curl -i https://app.example.test/ | rg -i "server|via|cache|powered|set-cookie"
curl -i --resolve app.example.test:443:203.0.113.10 https://app.example.test/ | rg -i "server|via|cache|powered|set-cookie"
```

Las diferencias pueden revelar comportamiento de origen directo o gaps de normalización de proxy.

### Vincular fingerprints a clases de vulnerabilidades

```
fingerprint | confianza | test relevante | test irrelevante a evitar
GraphQL errors | alta | revisión de schema/control de acceso | SQLi por defecto
CDN cache headers | media | revisión de cache poisoning/key | auth bypass por suposición
```

Los fingerprints deberían acotar el testing, no crear payloads cargo-cult.

## Ejemplos prácticos

- Los headers de respuesta revelan un CDN y un framework de backend.
- Los bundles JavaScript exponen patrones de rutas y convenciones de API.
- El comportamiento de TLS y errores sugiere un proveedor de edge particular.
- Los source maps exponen componentes del framework y nombres internos de API.
- Los errores de GraphQL revelan detalles de resolvers y schema.

## Notas relacionadas

- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[service-validation|Service Validation]]
- [[http-headers|HTTP Headers]]
- [[reverse-proxies|Reverse Proxies]]
- [[endpoint-discovery|Endpoint Discovery]]

## Referencias

- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Testing / Lab:** PortSwigger information disclosure — https://portswigger.net/web-security/information-disclosure
