---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - dns
  - resolution
sources: []
---

# Resolución DNS

## Definición
La resolución DNS es el proceso de lookup que convierte un nombre legible por humanos, como `app.example.com`, en los registros que un cliente necesita para elegir un destino: registros de dirección, alias, mail exchangers, registros de servicio, registros de texto y cadenas de delegación específicas del proveedor.

## Por qué importa
Toda request HTTP empieza con una decisión de nombre antes de que un paquete llegue a la app. La resolución DNS decide qué proveedor, CDN, load balancer, bucket, tenant de SaaS u origin va a intentar alcanzar un cliente. El trabajo de seguridad depende de leer esa cadena con precisión porque la exposición a menudo se esconde en la indirección: alias, respuestas split-horizon, CNAMEs viejos, registros wildcard y mapeos de dominio custom de terceros.

Esta nota es dueña de la mecánica del lookup. [[dns-security|Seguridad de DNS]] es dueña de DNS como un problema de propiedad y control. [[dangling-dns-records|Registros DNS colgantes]] es dueña de los mapeos nombre-objetivo obsoletos. [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] es dueña del hallazgo de exposición cuando un mapeo obsoleto es reclamable.

## Cómo funciona
La resolución DNS responde **5 preguntas**:

1. **¿Quién es autoritativo para el nombre?** El resolver camina root → TLD → nameservers autoritativos de la zona.
2. **¿El nombre es un alias?** Las cadenas `CNAME` redirigen el lookup a otro nombre controlado por el dueño o por un tercero.
3. **¿Qué registro de dirección o servicio se devuelve?** `A`, `AAAA`, `MX`, `TXT`, `SRV`, `CAA` y otros registros cargan cada uno un significado de seguridad distinto.
4. **¿Cuánto se puede cachear la respuesta?** El TTL controla cuánto pueden reusar la respuesta los resolvers recursivos y los clientes.
5. **¿La respuesta varía según resolver, origen o vista?** CDNs, geo-DNS, DNS split-horizon y zonas hospedadas privadas pueden devolver respuestas distintas para el mismo nombre.

Cadena de lookup de ejemplo:

```txt
app.example.com.      300 IN CNAME app-prod.edge.examplecdn.net.
app-prod.edge.examplecdn.net. 60 IN A 203.0.113.42
app-prod.edge.examplecdn.net. 60 IN AAAA 2001:db8::42
```

Interpretación de seguridad:

- `example.com` es dueño del hostname público.
- el CDN es dueño del namespace objetivo y de la infraestructura de edge.
- el TTL bajo sugiere que el steering de tráfico puede cambiar rápido.
- el origin real puede estar oculto, pero la certificate transparency o el historial de DNS todavía pueden exponerlo.

El bug rara vez es "DNS existe". El bug es asumir que un nombre significa una cosa estable cuando la resolución es en realidad una cadena de delegaciones, cachés y propiedad de proveedores.

## Técnicas / patrones
Atacantes y defensores inspeccionan:

- registros `A` / `AAAA` para encontrar hosts directos, edges de CDN, load balancers y origins expuestos
- cadenas `CNAME` para identificar proveedores de terceros y mapeos de dominio custom colgantes
- registros `MX`, `TXT`, `SPF`, `DKIM` y `DMARC` para entender la postura de mail e identidad
- registros `CAA` para ver qué autoridades de certificación pueden emitir para el dominio
- registros `NS` para identificar proveedores autoritativos y fronteras de delegación
- comportamiento wildcard como `anything.example.com` resolviendo inesperadamente
- valores de TTL que señalan steering dinámico, registros obsoletos o ventanas lentas de respuesta a incidentes
- comportamiento split-horizon comparando respuestas de resolvers públicos, internos, VPN y contextos de VPC de nube
- historial de DNS / certificate transparency para encontrar origins viejos, proveedores retirados y subdominios no rastreados

## Variantes y bypasses
El comportamiento de la resolución DNS cae en **6 variantes operativas** que importan durante la revisión de seguridad.

### 1. Registros de dirección directos
Los registros `A` y `AAAA` apuntan directamente a direcciones IPv4/IPv6. Son los más fáciles de razonar pero todavía pueden esconder exposición cuando una IP pública saltea un CDN, WAF o reverse proxy.

### 2. Cadenas de alias
Las cadenas `CNAME` apuntan un nombre a otro nombre. Cada hop puede cruzar una frontera de propiedad. Esta es la forma común para dominios custom de SaaS, CDNs, load balancers de nube y registros colgantes propensos a takeover.

### 3. Registros wildcard
`*.example.com` responde para nombres arbitrarios. Los wildcards pueden esconder errores de inventario, hacer ruidosa la enumeración por fuerza bruta y hacer que las herramientas reporten falsos positivos salvo que chequeen nombres aleatorios de baseline.

### 4. DNS split-horizon
El mismo nombre resuelve distinto según el cliente use DNS público, DNS corporativo, DNS de VPN o zonas hospedadas privadas de nube. Esto importa para SSRF, alcanzabilidad interna y respuesta a incidentes porque el servidor vulnerable puede resolver un objetivo distinto a la laptop del tester.

### 5. Geo-DNS y steering de CDN
Los resolvers devuelven respuestas distintas según geografía, latencia, salud o EDNS Client Subnet. Un hallazgo reproducido desde una región puede desaparecer desde otra, y un solo hostname puede frontear muchas IPs de edge.

### 6. Caché negativa y obsoleta
NXDOMAIN, SERVFAIL y respuestas positivas viejas se pueden cachear. Durante limpieza o respuesta a incidentes, un registro borrado todavía puede ser recordado por resolvers, mientras un registro nuevo puede no ser visible en todos lados todavía.

## Impacto
Ordenado aproximadamente por severidad:

- **Tráfico hacia infraestructura controlada por el atacante.** Alias colgantes o cadenas de propiedad envenenadas pueden rutear hostnames confiables hacia un atacante.
- **Bypass de controles de edge.** El historial de DNS, registros `A` directos u origins filtrados pueden dejar que el tráfico saltee un camino CDN/WAF/reverse-proxy.
- **Bypass de allowlist de SSRF.** Un dominio de apariencia benigna puede resolver a direcciones privadas, loopback o link-local tras un redirect, rebinding o resolución split-horizon.
- **Abuso de email e identidad.** Registros MX/TXT débiles o confusos afectan la resistencia al phishing, la verificación de dominio y la propiedad de tenants de SaaS.
- **Deriva del inventario de activos.** Subdominios desconocidos, registros obsoletos y dependencias de proveedores amplían la superficie de ataque más allá de los diagramas.
- **Fragilidad operativa.** TTLs bajos, mala delegación o respuestas autoritativas inconsistentes hacen más difíciles las caídas y la respuesta a incidentes.

## Detección y defensa
Ordenado por efectividad:

1. **Mantené un inventario autoritativo de propiedad para cada dominio y subdominio.**
   Cada hostname debería tener un dueño de negocio, dueño técnico, objetivo esperado, proveedor y camino de retiro. La resolución DNS solo es segura cuando la organización sabe quién está autorizado a apuntar nombres a dónde.

2. **Resolvé cadenas completas y registrá las fronteras de propiedad.**
   No pares en el primer `CNAME`. Seguí la cadena completa y etiquetá cuándo la propiedad cruza a un CDN, proveedor de SaaS, load balancer de nube, bucket de almacenamiento o vendor. La mayoría de la deriva de takeover y exposición vive en estas fronteras.

3. **Compará la resolución pública, interna y de contexto de workload.**
   Probá desde resolvers públicos, DNS interno/VPN y el contexto de runtime que importa (VM de nube, contenedor, runner de CI, servidor de app propenso a SSRF). Las respuestas split-horizon no son bugs por sí solas, pero son peligrosas cuando los defensores prueban desde el punto de vista equivocado.

4. **Incorporá la limpieza de registros obsoletos al deprovisioning.**
   Destruir una app de nube, bucket, tenant de SaaS o load balancer debería disparar la eliminación de DNS en el mismo camino de cambio. DNS no debería ser un agregado manual separado.

5. **Detectá las baselines de wildcard antes de confiar en los resultados de enumeración.**
   Consultá nombres aleatorios bajo la zona para aprender el comportamiento wildcard. Sin una baseline, las herramientas de fuerza bruta de subdominios pueden confundir respuestas wildcard con activos reales.

6. **Usá los datos de DNS como una señal, no como toda la verdad.**
   DNS te dice el naming previsto, no necesariamente todos los servicios alcanzables. Emparejalo con certificate transparency, sondeo HTTP, escaneo de puertos, inventario de nube y registros de superficie de ataque.

7. **Configurá los TTLs deliberadamente.**
   Los TTLs cortos ayudan a la migración y respuesta a incidentes pero aumentan la dependencia de la disponibilidad autoritativa. Los TTLs largos reducen la carga de consultas pero ralentizan la recuperación y la limpieza. El valor correcto depende del propósito operativo.

### Qué no funciona como defensa primaria

- **Asumir que NXDOMAIN significa sin exposición.** El historial de DNS, certificados, registros alternativos y exposición directa por IP todavía pueden revelar o alcanzar el servicio.
- **Chequear solo registros `A`.** El comportamiento de `CNAME`, `AAAA`, `MX`, `TXT`, `CAA` y wildcard suele cargar la historia de seguridad.
- **Probar solo desde tu laptop.** Servidores, contenedores, clientes VPN y workloads de nube pueden resolver respuestas distintas.
- **Tratar DNS como autorización.** Un nombre de apariencia privada, un sufijo interno o un subdominio no listado no autoriza al que llama.
- **Confiar en un TTL bajo como limpieza.** El TTL solo controla la vida de la caché. No borra registros obsoletos ni revoca la propiedad de terceros.

## Labs prácticos
Corré esto contra dominios que sean tuyos o que estés autorizado a evaluar. `dig`, `host`, `curl` estándar y `jq` opcional alcanzan.

### Trazar la resolución autoritativa

```bash
# Mostrar el camino de delegación desde root hasta la respuesta final.
dig +trace app.example.com

# Preguntarle directamente al nameserver autoritativo después de identificarlo.
dig NS example.com +short
dig @ns1.example-dns.net app.example.com A
```

Usá esto para distinguir el comportamiento de caché recursiva de la verdad autoritativa.

### Seguir cadenas CNAME y registros de dirección

```bash
name=app.example.com
dig +short "$name" CNAME
dig +short "$name" A
dig +short "$name" AAAA

# Respuesta completa con TTLs.
dig "$name" A "$name" AAAA "$name" CNAME
```

Registrá cada frontera de propiedad: tu zona → CDN → proveedor de nube → objetivo de SaaS.

### Detectar comportamiento DNS wildcard

```bash
domain=example.com
for sub in does-not-exist-$RANDOM definitely-missing-$RANDOM random-$RANDOM; do
  printf '%s -> ' "$sub.$domain"
  dig +short "$sub.$domain" A
done
```

Si nombres aleatorios resuelven, la salida de fuerza bruta de subdominios debe filtrarse contra la baseline del wildcard.

### Comparar resolvers y puntos de vista

```bash
name=app.example.com
for resolver in 1.1.1.1 8.8.8.8 9.9.9.9; do
  printf '\nResolver %s\n' "$resolver"
  dig @"$resolver" +short "$name" A
done

# Comparar desde dentro de VPN/nube/contenedor cuando sea posible:
dig +short "$name" A
```

Respuestas distintas pueden ser steering de CDN, DNS split-horizon o cachés recursivas obsoletas.

### Inspeccionar registros de mail y verificación de dominio

```bash
domain=example.com
dig +short "$domain" MX
dig +short "$domain" TXT
dig +short "_dmarc.$domain" TXT
dig +short "$domain" CAA
```

Buscá tokens viejos de verificación de SaaS, política DMARC débil y registros CAA ausentes o demasiado amplios.

### Chequear si el DNS apunta esquivando el edge

```bash
name=app.example.com
dig +short "$name" A
curl -skI "https://$name" | rg -i 'server|via|x-cache|cf-ray|x-amz-cf-id|x-served-by'
```

Compará las respuestas de DNS con los headers de respuesta. Una IP de origin directa sin headers de CDN/proxy puede indicar bypass del edge.

## Ejemplos prácticos
- `app.example.com` apunta a un CDN, pero un viejo registro `A` de `origin.example.com` todavía expone el backend directamente.
- `docs.example.com` es un `CNAME` hacia un proveedor de SaaS; el tenant de SaaS se borró pero el DNS quedó.
- `*.dev.example.com` resuelve a un ingress de staging catch-all, haciendo que los escáneres reporten muchos hosts falsos positivos.
- Un tester público no ve dirección privada, pero un fetcher SSRF vulnerable dentro de la VPC resuelve el mismo nombre a `10.0.4.15`.
- Un registro TXT de verificación olvidado prueba el control de un tenant de SaaS mucho después de que la integración fue retirada.

## Notas relacionadas
- [[dns-security|Seguridad de DNS]] — propiedad, control e higiene de exposición.
- [[dangling-dns-records|Registros DNS colgantes]] — mapeos nombre-objetivo obsoletos.
- [[cybersecurity/attack-surface-mapping/subdomain-takeover|Subdomain Takeover]] — hallazgo de exposición cuando un objetivo colgante es reclamable.
- [[http-overview|Panorama de HTTP]] — DNS es la etapa 1 de toda transacción HTTP.
- [[load-balancers|Load balancers]] — muchos registros DNS terminan en load balancers o CDNs.
- [[cybersecurity/networking/service-enumeration|Enumeración de servicios]] — después de que la resolución identifica objetivos alcanzables, enumerá qué corren realmente.
- [[cybersecurity/web-security/ssrf|SSRF]] — el punto de vista del resolver y el rebinding importan para los bugs de fetch de URL.
- [[cybersecurity/attack-surface-mapping/external-attack-surface|Superficie de ataque externa]]

### Notas atómicas futuras sugeridas
- [[dns-record-types|Tipos de registros DNS]]
- [[split-horizon-dns|DNS split-horizon]]
- [[wildcard-dns|DNS wildcard]]
- [[dns-rebinding|DNS rebinding]]
- [[certificate-transparency-monitoring|Monitoreo de certificate transparency]]
- [[caa-records|Registros CAA]]

## Referencias
- **Foundational:** Cloudflare Learning Center on DNS records — https://www.cloudflare.com/learning/dns/dns-records/
- **Foundational:** ICANN DNS Concepts — https://www.icann.org/resources/pages/dns-2012-02-25-en
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
- **Research / Deep Dive:** ProjectDiscovery guide to DNS takeovers — https://projectdiscovery.io/blog/guide-to-dns-takeovers
