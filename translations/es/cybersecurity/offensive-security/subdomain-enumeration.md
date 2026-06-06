# Subdomain Enumeration

## Definición

La subdomain enumeration es el proceso de descubrir subdominios asociados a un objetivo y determinar cuáles están activos, son propiedad del objetivo, interesantes, riesgosos o están obsoletos.

## Por qué importa

Los subdominios revelan puntos de entrada alternativos, hosts de staging, entornos viejos, superficies admin, mappings de vendors, tenants de clientes y drift de ownership. Son uno de los puentes más ricos entre OSINT y superficie de ataque concreta.

Esta nota es más acotada que [[public-asset-discovery|Descubrimiento de Assets Públicos]] y más temprana que la validación completa: su trabajo es expandir la superficie de hostnames antes de routear hallazgos hacia verificaciones de alcanzabilidad y ownership.

## Cómo funciona

La subdomain enumeration usa **5 fuentes de descubrimiento**:

1. **Certificate transparency.** Nombres emitidos en certificados públicos.
2. **Datos DNS.** Pistas de zona, brute force, permutaciones, CNAMEs, MX/TXT y comportamiento wildcard.
3. **Búsqueda y archivos.** Páginas indexadas, URLs históricas, docs y links viejos.
4. **Artefactos de cliente.** JavaScript, source maps, apps móviles y SDKs.
5. **Pistas de proveedores y vendors.** Mappings SaaS, hostnames cloud, dominios de status/soporte/docs.

El problema no es tener muchos subdominios. El riesgo son subdominios que están activos, obsoletos, reclamables, privilegiados o fuera de gobernanza.

Un ejemplo trabajado, de nombres a clases:

```
Raw names:
  app.example.test
  staging-api.example.test
  help.example.test
  random-123.example.test

Checks:
  app -> 200 product app
  staging-api -> 401 API, target certificate
  help -> CNAME to support SaaS
  random-123 -> wildcard DNS baseline

Classes:
  product host, environment host, vendor-mapped host, noise

Next actions:
  validate staging scope, review vendor mapping, remove wildcard noise from list
```

El paso de calidad es la clasificación, no el volumen bruto de subdominios.

## Técnicas / patrones

Los operadores buscan:

- `dev`, `staging`, `test`, `qa`, `admin`, `api`, `internal`, `vpn`, `support`, `docs`, `status`
- DNS wildcard que crea falsos positivos ruidosos
- CNAMEs a proveedores de terceros
- nombres de certificados y archivos
- convenciones de naming de entornos
- patrones regionales/de cliente/de tenant

## Variantes y bypasses

La subdomain enumeration tiene **6 clases de resultados**.

### 1. Host de producto en vivo

App pública esperada, API o host de docs.

### 2. Host de entorno

Deploy de staging, beta, preview, dev, QA, demo o temporal.

### 3. Host admin/control

Interfaces de administración, soporte, monitoreo, CI/CD o privilegiadas.

### 4. Host mapeado por vendor

CNAME o dominio custom apunta a proveedor SaaS/cloud.

### 5. Host obsoleto o dangling

El DNS resuelve o aliasea a un objetivo que ya no existe o puede reclamarse.

### 6. Ruido o host no relacionado

Registros wildcard, de parking, compartidos o mal atribuidos.

## Impacto

Ordenado aproximadamente por severidad:

- **Subdomain takeover.** Los mappings de proveedores obsoletos pueden volverse reclamables.
- **Exposición de admin o staging.** Las interfaces sensibles aparecen fuera de los paths del producto principal.
- **Descubrimiento de API oculta.** Los hosts de API y móviles revelan rutas alternativas.
- **Expansión de scope.** Las marcas y vendors se vuelven visibles.
- **Mejora de inventario.** Los defensores descubren nombres olvidados.

## Detección y defensa

Ordenado por efectividad:

1. **Enumerá continuamente tus propios subdominios.**
   Tratá los nombres como assets con lifecycle gestionado.

2. **Validá owner y entorno para cada nombre activo.**
   Los nombres desconocidos en vivo merecen triage.

3. **Eliminá DNS obsoleto rápidamente.**
   La limpieza de DNS debería ser parte del decommissioning.

4. **Monitoreá patrones de naming de alto riesgo.**
   Los nombres admin, staging, support y vendor deberían revisarse rápidamente.

5. **Controlá DNS wildcard y naming de tenants.**
   Los wildcards crean inventario ruidoso y pueden enmascarar recursos obsoletos.

### Qué no funciona como defensa primaria

- **Asumir que los subdominios no linkeados están ocultos.** Los certificados, DNS, archivos y wordlists los revelan.
- **Borrar la app pero dejar el DNS.** Los nombres obsoletos siguen siendo anchors de confianza.
- **Ignorar ruido wildcard.** El ruido puede ocultar exposición real.
- **Tratar cada nombre descubierto como en scope sin validación.** El ownership sigue importando.

## Labs prácticos

Usá dominios propios.

### Recolección de certificate transparency

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' | jq -r '.[].name_value' | sort -u
```

Deduplicar y normalizar entradas wildcard.

### Resolver y clasificar

```
while read host; do printf "%s " "$host"; dig +short "$host" | tail -n 1; done < subdomains.txt
```

Clasificar por proveedor, entorno y owner.

### Detectar comportamiento wildcard

```
dig +short "random-$(date +%s).example.test"
```

El DNS wildcard cambia cómo deberían interpretarse los resultados de la enumeración.

### Construir una tabla de clasificación de subdominios

```
host | fuente | resuelve | status HTTP | cname/proveedor | clase | próxima acción
```

Usá las seis clases de resultado de esta nota para manejar el triage.

### Verificar drift en hosts mapeados por proveedores

```
while read host; do
  cname=$(dig CNAME "$host" +short)
  printf "%s -> %s\n" "$host" "$cname"
done < subdomains.txt
```

Los CNAMEs de proveedores frecuentemente alimentan la revisión de exposición de terceros o takeover.

## Ejemplos prácticos

- La enumeración revela hosts `staging`, `legacy-api` y `admin`.
- Un subdominio apunta a un servicio descomisionado.
- Hosts alternativos específicos de clientes exponen más superficie que el dominio principal.
- Un CNAME de vendor apunta a una plataforma de soporte.
- Los logs de certificados revelan un entorno de preview temporal.

## Notas relacionadas

- [[dns-resolution|DNS Resolution]]
- [[dns-security|DNS Security]]
- [[subdomain-takeover|Subdomain Takeover]]
- [[public-asset-discovery|Descubrimiento de Assets Públicos]]
- [[scope-validation|Scope Validation]]

## Referencias

- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 102 — https://projectdiscovery.io/blog/recon-series-2
- **Fundamental:** OSINT Framework — https://osintframework.com/
- **Fundamental:** OWASP WSTG latest — https://owasp.org/www-project-web-security-testing-guide/latest/
