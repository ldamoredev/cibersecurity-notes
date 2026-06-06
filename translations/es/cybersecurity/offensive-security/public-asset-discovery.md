# Public Asset Discovery

## Definición

El public asset discovery es el proceso de identificar dominios, subdominios, hosts, servicios, APIs, superficies de storage, documentos e infraestructura de soporte que pertenecen o se relacionan materialmente con un objetivo y son accesibles desde internet.

## Por qué importa

Antes de testear en profundidad, necesitás saber qué existe. El public asset discovery revela exposición indocumentada, legacy, hosteada por vendors, hosteada en cloud o con gobernanza débil. Es el flujo de trabajo de recon que alimenta la [[external-attack-surface|Superficie de Ataque Externa]].

Esta nota se mantiene enfocada en encontrar assets. El [[company-mapping|Company Mapping]] prueba las relaciones organizacionales, mientras que el [[tech-stack-fingerprinting|Tech Stack Fingerprinting]] infiere qué corren esos assets.

## Cómo funciona

El public asset discovery tiene **5 clases de assets**:

1. **Nombres.** Dominios, subdominios, hostnames, certificados y registros DNS.
2. **Ubicaciones de red.** IPs, ASNs, rangos cloud, orígenes CDN y puertos.
3. **Aplicaciones.** Sitios web, APIs, paneles admin, apps de staging, docs y portales.
4. **Storage y artefactos.** Buckets, uploads, source maps, backups, logs y outputs de CI.
5. **Superficies de terceros.** Portales SaaS, sistemas de soporte, callbacks de identidad, widgets y contenido hosteado por vendors.

El error no es el descubrimiento en sí. El valor está en convertir los assets públicos descubiertos en decisiones de ownership y exposición.

Un ejemplo trabajado, asset discovery a clasificación:

```
Candidate:
  docs-preview.example.test

Discovery source:
  certificate transparency + search result

Resolution:
  CNAME to vendor-docs.example

HTTP:
  200 with target logo, no login

Classification:
  vendor-hosted documentation surface, likely target-controlled content

Next action:
  scope validation + third-party exposure review, not platform testing
```

El public asset discovery es útil cuando cada asset recibe un rol, hipótesis de owner y siguiente paso de validación.

## Técnicas / patrones

Los operadores usan:

- certificate transparency y enumeración DNS
- operadores de búsqueda y URLs archivadas
- mapeo de rangos ASN/IP donde esté en scope
- mapeo de cloud-hostname y proveedor
- extracción de rutas desde JavaScript y source maps
- patrones de naming de storage/buckets
- identificación de CNAMEs de SaaS y vendors

## Variantes y bypasses

Los assets públicos aparecen en **6 formas**.

### 1. Assets del producto principal

Apps web principales, APIs, docs y dominios orientados al cliente.

### 2. Assets de entorno

Deploys de staging, preview, beta, dev, demo y regionales.

### 3. Assets hosteados por vendors

Portales de soporte, sitios de docs, páginas de status, proveedores de identidad y sistemas de marketing.

### 4. Assets de infraestructura cloud

Hostnames cloud, load balancers, object storage, sitios estáticos y endpoints serverless.

### 5. Assets artefacto

Source maps, bundles, paquetes, logs, backups y reportes exportados.

### 6. Assets huérfanos o legacy

Sistemas viejos, marcas adquiridas, DNS obsoleto y servicios olvidados.

## Impacto

Ordenado aproximadamente por severidad:

- **Puntos de entrada ocultos.** Los assets desconocidos pueden carecer de controles actuales.
- **Exposición de datos sensibles.** Storage, docs, source maps o artefactos filtran información.
- **Riesgo de takeover.** Los dominios custom huérfanos y los mappings de vendors pueden volverse reclamables.
- **Expansión de scope.** Los assets públicos revelan marcas, subsidiarias y vendors.
- **Mejor targeting de testing.** El descubrimiento identifica objetivos manuales probablemente de alto valor.

## Detección y defensa

Ordenado por efectividad:

1. **Descubrí continuamente assets públicos desde fuera del perímetro.**
   El public asset discovery debería ser parte del inventario defensivo, no solo del flujo de trabajo del atacante.

2. **Atá cada asset a owner, entorno y exposición prevista.**
   Los assets públicos sin dueño se convierten en prioridades de remediación.

3. **Retirá DNS, storage y mappings de vendors obsoletos.**
   Los nombres e integraciones viejos son drift común de assets públicos.

4. **Revisá artefactos públicos antes del release.**
   Los source maps, docs, paquetes, logs y reportes no deberían publicar accidentalmente contexto sensible.

5. **Validá ownership antes de testear.**
   Público no siempre significa en scope o en propiedad del objetivo.

### Qué no funciona como defensa primaria

- **Asumir que el dominio principal es todo el objetivo.** Las marcas, subsidiarias, vendors y assets cloud expanden la superficie.
- **Depender de la documentación.** El descubrimiento público encuentra lo que los docs omiten.
- **Dejar hosts temporales públicos.** Los assets temporales frecuentemente se olvidan.
- **Tratar las superficies hosteadas por vendors como problema de otro.** Pueden llevar tu marca, auth, datos y confianza.

## Labs prácticos

Usá objetivos propios.

### Construir una lista de assets públicos

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u > subdomains.txt
```

Clasificar cada host por owner, entorno y rol probable.

### Resolver candidatos

```
while read host; do printf "%s " "$host"; dig +short "$host" | tail -n 1; done < subdomains.txt
```

Agrupar por proveedor, CDN, cloud y destinos desconocidos.

### Identificar assets web

```
while read host; do curl -m 3 -ks -o /dev/null -w "%{http_code} $host\n" "https://$host"; done < subdomains.txt
```

Mover assets en vivo a validación.

### Clasificar assets públicos por rol

```
asset | source | provider | role | owner confidence | exposure concern | next step
```

La clasificación es la diferencia entre descubrimiento y recon utilizable.

### Encontrar candidatos de artefactos estáticos

```
site:example.test filetype:map
site:example.test filetype:zip
site:example.test inurl:backup OR inurl:export
```

Los assets artefacto suelen alimentar el endpoint discovery y la revisión de storage expuesto.

## Ejemplos prácticos

- Un sitio estático olvidado sigue sirviendo contenido.
- Un host de API público es alcanzable pero ausente de la documentación formal.
- Los assets públicos están distribuidos entre múltiples vendors y proveedores.
- Un hostname de cloud load balancer expone un origen directo.
- Un source map revela paths de API ocultos.

## Notas relacionadas

- [[external-attack-surface|Superficie de Ataque Externa]]
- [[recon|Recon]]
- [[subdomain-enumeration|Subdomain Enumeration]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[company-mapping|Company Mapping]]

## Referencias

- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
