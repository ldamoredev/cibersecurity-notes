# Passive Recon

## Definición

El passive recon es la recopilación de información que no interactúa directamente con los sistemas del objetivo de una manera que normalmente generaría tráfico del lado del objetivo.

## Por qué importa

El passive recon es amplio, de bajo esfuerzo y frecuentemente suficiente para revelar grandes partes de la superficie de ataque externa antes de tocar el objetivo. Los temas OSINT de zSecurity pertenecen aquí por ahora: operadores de búsqueda, pistas de brechas/leaks, perfiles sociales, documentos públicos, pistas de email/teléfono, trabajo de imagen/ubicación y company mapping.

Mantené el límite claro: el passive recon recolecta pistas; el [[active-recon|Active Recon]] prueba el comportamiento del objetivo en vivo.

## Cómo funciona

El passive recon usa **6 fuentes de pistas públicas**:

1. **Nombres y dominios.** Dominios, marcas, subsidiarias, adquisiciones y patrones de naming.
2. **Registros de infraestructura pública.** DNS, certificate transparency, WHOIS/RDAP, ASNs y hostnames cloud.
3. **Búsqueda y archivos.** Operadores de búsqueda, páginas en caché, consultas tipo GHDB, Wayback, docs viejos.
4. **Código y artefactos.** Repos públicos, source maps, metadata de paquetes, apps móviles y docs.
5. **Personas y organización.** Ofertas de trabajo, perfiles sociales, emails, teléfonos, roles y vendors.
6. **Contexto de brecha/leak.** Referencias de leaks públicos, indicadores de credenciales expuestas e incidentes históricos.

El error no es que exista información pública. La lección de seguridad es que las pistas públicas se combinan en un modelo preciso de sistemas y límites de confianza.

Un ejemplo trabajado, cadena de pistas pasivas:

```
Search clue:
  site:example.test filetype:pdf "staging"

Document clue:
  PDF mentions "preview-api.example.test"

Certificate clue:
  CT confirms preview-api.example.test had a cert issued last month

Archive clue:
  Wayback has /api/v1/examples for that host

Passive conclusion:
  likely staging/API asset; do not test yet, send to scope + live validation
```

El passive recon es más fuerte cuando fuentes públicas independientes se corroboran mutuamente.

## Técnicas / patrones

Los operadores recolectan:

- subdominios de certificate transparency
- resultados de operadores de búsqueda y URLs archivadas
- strings de repositorios públicos y nombres de paquetes
- docs públicos, PDFs, metadata y páginas de soporte
- ofertas de trabajo que revelan stack y vendors
- pistas de redes sociales y perfiles de empresa
- patrones de email y superficies de contacto

## Variantes y bypasses

El passive recon tiene **5 lentes útiles**.

### 1. Lente de assets

Encontrar nombres, dominios, hosts, proveedores cloud y servicios externos.

### 2. Lente de rutas

Encontrar URLs, paths de API, parámetros, docs y endpoints históricos.

### 3. Lente de tecnología

Inferir frameworks, lenguajes, vendors y patrones de deployment.

### 4. Lente de organización

Mapear marcas, subsidiarias, equipos, roles y vendors.

### 5. Lente humana/contextual

Encontrar canales de soporte, emails, roles públicos y contexto de ingeniería social. Mantener esto ético y consciente del scope.

## Impacto

Ordenado aproximadamente por severidad:

- **Descubrimiento de assets ocultos.** Las fuentes pasivas revelan dominios y subdominios olvidados.
- **Descubrimiento de rutas y endpoints.** Los archivos y artefactos de código exponen paths de backend.
- **Pistas de exposición de credenciales y secretos.** Los repos públicos o leaks pueden revelar problemas de seguridad.
- **Targeting tecnológico.** Las pistas del stack guían el testing más profundo.
- **Clarificación de scope.** El company mapping reduce el testing de objetivos equivocados.

## Detección y defensa

Ordenado por efectividad:

1. **Auditá información pública como parte del attack surface management.**
   Si los de afuera pueden encontrarlo, los defensores deberían saber que existe.

2. **Reducí artefactos públicos obsoletos.**
   Los docs viejos, source maps, ejemplos filtrados y referencias archivadas suelen sobrevivir al sistema.

3. **Revisá repositorios públicos y metadata de paquetes.**
   Los nombres, endpoints, tokens y dominios internos suelen filtrarse a través de artefactos de desarrollo.

4. **Limitá la divulgación tecnológica innecesaria.**
   Esconder nombres del stack no es una defensa primaria, pero evitá banners gratuitos, páginas de error y comentarios.

5. **Usá los hallazgos para mejorar el inventario y el entrenamiento.**
   El passive recon debería alimentar la limpieza de ownership, la higiene de secretos y la concientización.

### Qué no funciona como defensa primaria

- **Ignorar datos en caché o históricos.** La información vieja sigue siendo útil para los atacantes.
- **Tratar OSINT como separado de la ingeniería de seguridad.** Las pistas públicas mapean a sistemas reales.
- **Depender de robots.txt o noindex como secreto.** Son pistas de indexación, no controles de acceso.
- **Solo limpiar el sitio web principal.** Los repos, docs, vendors y archivos también filtran.

## Labs prácticos

Usá objetivos propios o auto-auditoría pública.

### Usar operadores de búsqueda

```
site:example.test filetype:pdf
site:example.test inurl:api
site:example.test intitle:index.of
```

Registrar solo hallazgos relevantes y en scope.

### Obtener nombres de certificados

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u
```

Alimentar candidatos en scope y validación en vivo.

### Buscar en repos locales/públicos

```
rg -n "api\\.|secret|token|password|internal|staging|callback|webhook" .
```

Para repos propios, clasificar secretos reales versus ejemplos inofensivos.

### Construir una tabla de corroboración pasiva

```
claim | source 1 | source 2 | source 3 | confidence | active validation needed
```

No promover una sola pista pública a objetivo sin corroboración o revisión de scope.

### Obtener URLs archivadas de forma segura

```
curl -s "https://web.archive.org/cdx?url=example.test/*&output=text&fl=original&collapse=urlkey" \
  | rg "/api/|admin|staging|debug" \
  | sort -u
```

Las rutas archivadas son pistas; el probing en vivo pertenece al active recon.

## Ejemplos prácticos

- Los logs de certificados revelan subdominios.
- Las URLs archivadas muestran rutas que ya no están linkeadas desde la UI.
- Los docs públicos exponen patrones de naming internos.
- Las ofertas de trabajo revelan opciones de framework y cloud.
- Los repositorios públicos mencionan hostnames de API y paths de webhook.

## Notas relacionadas

- [[recon|Recon]]
- [[active-recon|Active Recon]]
- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[company-mapping|Company Mapping]]
- [[subdomain-enumeration|Subdomain Enumeration]]

## Referencias

- **Investigación / Deep Dive:** ProjectDiscovery recon 101 — https://projectdiscovery.io/blog/reconnaissance-a-deep-dive-in-active-passive-reconnaissance
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
