# External Attack Surface

## Definición

La external attack surface es el conjunto de activos, servicios, interfaces, almacenes de datos y rutas de confianza alcanzables desde fuera de las redes internas de la organización — más frecuentemente a través de internet público, pero también a través de redes de partner, portales de vendor e identidades federadas. Es **la vista dominante que los atacantes reales, investigadores de bug bounty y buscadores web realmente ven**.

## Por qué importa

La superficie externa suele ser lo primero que descubre un atacante y lo último que termina de mapear un defensor. Incluye dominios públicos, APIs, puertos, almacenamiento de objetos, páginas de login, servicios de acceso remoto, apps cloud-hosted, contenido hosted por vendors y entornos olvidados. La mayoría de los eventos de acceso inicial en el mundo real vienen de esta superficie — un Jenkins olvidado, un bucket S3 público, un subdominio obsoleto, un panel admin expuesto — no de bugs de aplicación personalizados.

Mantené la distinción con [[internal-attack-surface]]: la superficie externa es sobre **alcanzabilidad pública**, no sobre lo que se vuelve alcanzable solo después de SSRF, foothold o acceso a red privada. Mezclar ambos produce priorización incoherente.

La superficie externa también es el objetivo defensivo de mayor apalancamiento. Cada exposición eliminada aquí reduce el tiempo de permanencia del atacante y el costo de descubrimiento sin ningún cambio en los controles internos. La matemática favorece el mantenimiento: una vista outside-in continua cuesta menos que la respuesta promedio a un incidente.

## Cómo funciona

La external attack surface tiene **4 capas de descubrimiento**. Un mapa útil cubre las cuatro; faltar cualquiera crea un punto ciego conocido.

1. **Capa de nombres.** Dominios, subdominios, certificados (`crt.sh` certificate transparency), registros DNS (actuales + históricos vía DNS pasivo), hostnames cloud, mapeos de vendor (cadenas CNAME). Lo primero que enumera un atacante y lo más fácil de mapear.
2. **Capa de red.** IPs, registros ASN/BGP, puertos, protocolos, CDNs, reverse proxies, servicios de acceso remoto. Resuelve "cuál es la dirección" en "qué es alcanzable en la dirección".
3. **Capa de aplicación.** Apps web, APIs, rutas, paneles admin, almacenamiento, documentos expuestos, rutas JavaScript, endpoints GraphQL. La mayoría de la superficie del producto vive aquí, pero las exposiciones de admin y almacenamiento causan los incidentes más grandes.
4. **Capa de relaciones.** Providers de terceros, callbacks, proveedores de identidad, analytics, herramientas de soporte, integraciones SaaS, scopes OAuth. La confianza se extiende a través de CNAMEs y tokens; aquí es donde las brechas de vendors se convierten en brechas del objetivo.

El bug **no es que existan activos públicos** — la mayoría de ellos deben ser públicos. El bug son los activos públicos que son **desconocidos, sin propietario, sobre-privilegiados, obsoletos o más débiles que la superficie principal del producto**.

Un ejemplo trabajado, las cuatro capas en conjunto:

```
Pregunta:   ¿Qué es alcanzable externamente para example.com que no está en la lista de activos?
Capa 1:    crt.sh devuelve 47 nombres; DNS pasivo agrega 8 nombres históricos.
Capa 2:    52 nombres resuelven; 6 están frente a CDN, 4 origen cloud directo, 1 ASN desconocido.
Capa 3:    sondeo directo encuentra 12 apps web + 4 páginas admin/login + 2 endpoints GraphQL.
Capa 4:    inspección CNAME: 3 zendesk, 2 statuspage, 1 vendor desaprovisionado (RECLAMABLE).
Hallazgos: 2 paneles admin con auth débil; 1 GraphQL con introspección activa; 1 candidato a takeover.
Acción:    [admin → forzar SSO + allowlist de IP], [GraphQL → deshabilitar intro], [CNAME → eliminar DNS].
```

El candidato a takeover es el hallazgo de mayor severidad. La capa 1 sola lo hubiera pasado por alto.

## Técnicas / patrones

La disciplina es "outside-in más inside-out, luego diff".

- **Dominios raíz, subdominios, certificados** vía certificate transparency (`crt.sh`), historial DNS (SecurityTrails, ViewDNS), enumeración basada en wordlists.
- **Hostnames cloud, almacenamiento de objetos, mapeos CDN** vía patrones de hostname del provider cloud (`*.s3.amazonaws.com`, `*.blob.core.windows.net`, `*.storage.googleapis.com`).
- **Puertos comunes, tecnologías web, superficies de login** vía escaneo autorizado (nmap, masscan), fingerprinting web (estilo Wappalyzer), triaje basado en screenshots (`gowitness`, `eyewitness`).
- **Nombres de entornos staging, preview, beta, dev, regional** vía enumeración de subdominios basada en wordlists y wildcards de certificate transparency.
- **Docs de API pública, specs OpenAPI, endpoints GraphQL, rutas JavaScript** vía rutas well-known estándar (`/openapi.json`, `/graphql`, `/.well-known/`), extracción de source-maps y análisis de bundles JS.
- **Backups, logs, source maps, artefactos expuestos** vía [[google-dorking|queries con forma de exposición]] y enumeración de nombres de bucket.

## Variantes y bypasses

La superficie externa se agrupa en **6 formas**. Cada forma tiene una expectativa diferente de "qué debería ser esto".

### 1. Producto público

Sitios web principales, APIs, documentación y servicios orientados al cliente. Diseñados para ser públicos; la disciplina es mantener los controles (autenticación, rate limiting, validación de esquema, monitoreo) alineados con la sensibilidad de los datos.

### 2. Entornos no productivos expuestos

Sistemas de staging, preview, beta, regionales viejos, de entrenamiento o temporales que permanecieron en línea después de que su propósito terminó. **La exposición temporal se vuelve permanente** cuando no está vinculada a la automatización del ciclo de vida. El objetivo de descubrimiento más rentable en la mayoría de las organizaciones.

### 3. Superficies admin y de acceso remoto

VPN, SSH, RDP, paneles de gestión, consolas de appliance, dashboards de soporte, interfaces de debug. Mayor privilegio que la superficie del producto, a menudo autenticación más débil. La exposición a internet de superficies admin debería requerir justificación explícita por activo.

### 4. Almacenamiento expuesto

Almacenamiento de objetos, logs, backups, source maps, informes, artefactos de build expuestos directamente sin una aplicación que los gate. Las revisiones de política de bucket y los chequeos de eliminación de artefactos CI capturan la mayoría de estos a bajo costo.

### 5. Superficies de terceros y vendors

Portales SaaS, orígenes CDN, callbacks de vendor, proveedores de identidad, widgets hosted. La confianza se extiende a través de CNAMEs; los fallos de descomisionamiento de vendors causan riesgo de [[subdomain-takeover|takeover]].

### 6. Servicios legacy y de compatibilidad

Servicios o puertos viejos mantenidos por compatibilidad pero sin los controles actuales (protocolos en texto claro, SMB/NFS no autenticado, algoritmos SSH deprecated, FTP). A menudo el resultado de decisiones "dejémoslo encendido, por las dudas" que nunca se revisan.

## Impacto

Ordenado aproximadamente por severidad:

- **Acceso inicial.** Admin, acceso remoto o servicios vulnerables expuestos se convierten en puntos de entrada; un Jenkins débil es suficiente.
- **Divulgación de datos sensibles.** Almacenamiento público, source maps y artefactos filtran credenciales, código fuente, datos de clientes o terminología interna.
- **Bypass de controles.** Los sistemas de staging o legacy no tienen controles de producción (sin WAF, sin rate limit, sin proxy de auth, sin logging).
- **Takeover e impersonación.** El DNS obsoleto o los mapeos de vendor permiten a los atacantes servir contenido bajo nombres de confianza; cubierto por [[subdomain-takeover]].
- **Aceleración de reconocimiento.** Los metadatos públicos revelan estructura interna, tecnologías y endpoints, perfeccionando cada acción posterior del atacante.

## Detección y defensa

Las defensas priorizan **el diff continuo outside-in vs inside-out** más la automatización del ciclo de vida.

1.
**Inventariás activos públicos continuamente desde vistas outside-in e inside-out.**
   Combiná reconocimiento externo (certs, DNS, escáneres) con inventarios cloud/provider (registros de activos, zonas del provider DNS). Cada uno captura fallos diferentes; el diff es el artefacto clave.

2.
**Clasificás cada activo público por propietario, entorno y audiencia prevista.**
   Los activos de producción, staging, demo interno, hosted por vendor y de adquisición legacy necesitan políticas diferentes. "Propietario desconocido" es en sí mismo un hallazgo.

3.
**Reducís la exposición pública para superficies admin, debug y de acceso remoto.**
   La autenticación fuerte es necesaria, pero la alcanzabilidad innecesaria desde internet también debería eliminarse. Por defecto, las superficies admin van detrás de VPN/zero-trust, redes privadas o política estricta de gateway cuando sea posible.

4.
**Vinculás DNS, certificados y recursos cloud a la automatización del ciclo de vida.**
   Eliminar un servicio debería quitar nombres, certificados, rutas, políticas de almacenamiento, secretos y dependencias de monitoreo juntos. El descomisionamiento manual es la mayor fuente de deriva.

5.
**Monitoreás nuevos hosts públicos y patrones de nombres riesgosos.**
   Los nombres que coinciden con `dev`, `staging`, `admin`, `vpn`, `backup`, `grafana`, `jenkins`, `kibana`, `phpmyadmin` merecen revisión rápida. Las nuevas entradas de certificate transparency deberían disparar flujos de confirmación de ownership.

6.
**Tratás los CNAMEs de terceros como parte de la superficie.**
   Las superficies hosted por vendors llevan tu confianza. La baja del tenant por parte del vendor debe disparar la limpieza del CNAME; de lo contrario [[subdomain-takeover]] se convierte en un riesgo real.

### Qué no funciona como defensa primaria

- **Asumir que la oscuridad protege hosts no enlazados.** Certificate transparency, DNS pasivo, buscadores y wordlists revelan nombres; "nunca lo publicitamos" no es un control.
- **Confiar solo en listas de activos internas.** Los atacantes ven lo que es alcanzable, no lo que está documentado; el diff es lo que importa.
- **Dejar staging público porque es temporal.** La exposición temporal se vuelve permanente; el activo "temporal" público promedio sobrevive años.
- **Confiar solo en allowlists de IP.** Los errores de cloud, proxy, VPN y confianza de header las debilitan; las allowlists son defensas por capas, no primarias.
- **Escaneos externos únicos.** La superficie externa cambia diariamente; los escaneos trimestrales pierden la mayoría de la deriva.

## Labs prácticos

Usá un dominio propio, un scope autorizado o un entorno de lab.

### Enumerá nombres vía certificate transparency

```
curl -s 'https://crt.sh/?q=%25.example.test&output=json' \
  | jq -r '.[].name_value' | tr ',' '\n' | sed 's/^\*\.//' | sort -u > names-ct.txt

```

Etiquetá cada nombre como producción / staging / hosted por vendor / desconocido / candidato a retiro.

### Resolvé y mapeá CNAMEs

```
while read host; do
  ip=$(dig +short "$host" | tail -1)
  cname=$(dig CNAME +short "$host" | head -1)
  echo "$host | $ip | ${cname:--}"
done < names-ct.txt > resolved.txt

awk -F'|' '{print $3}' resolved.txt | sort | uniq -c | sort -rn
```

La columna CNAME revela relaciones con vendors. La columna IP revela orígenes cloud, CDN o directos.

### Escaneá y capturá screenshots

```
nmap -sV -Pn -p 80,443,8080,8443,8000,3000,5000,9000,8888 --open names-ct.txt

gowitness scan file -f names-ct.txt -t 10
```

Los screenshots hacen evidentes las superficies admin/login de un vistazo; clasificá cada una como esperado / inesperado / desconocido / candidato a retiro.

### Filtrá nombres de riesgo

```
rg -i 'admin|staging|dev|test|vpn|backup|grafana|jenkins|kibana|phpmyadmin|debug|preview|beta|legacy|old|temp' names-ct.txt
```

Los nombres de riesgo no prueban exposición; enfocan el triaje. Verificá cada hit con [[exposed-service-triage]].

### Verificá candidatos a takeover

```
while read host; do
  cname=$(dig CNAME +short "$host" | head -1)
  if [ -n "$cname" ]; then
    # Sondeá el destino buscando "no such tenant" o fingerprints similares.
    response=$(curl -s -o /dev/null -w "%{http_code}" "https://$host" --max-time 5)
    echo "$host | $cname | $response"
  fi
done < names-ct.txt
```

Pasá candidatos a [[subdomain-takeover]] para validación completa.

### Mapeá relaciones con vendors vía CNAMEs

```
subdominio               | destino CNAME              | vendor             | ¿relación activa?
support.example.com     | example.zendesk.com        | Zendesk            | sí
status.example.com      | example.statuspage.io      | StatusPage         | sí
old-help.example.com    | example.helpscoutdocs.com  | HelpScout          | NO — retirado 2024 — RIESGO TAKEOVER
```

Las filas "no — retirado" son las peligrosas; eliminá el DNS antes de que el vendor libere el tenant.

## Ejemplos prácticos

- Un host de staging tiene acceso a internet y usa credenciales de prueba, proporcionando una ruta de acceso inicial de baja fricción.
- Un servicio VPN legacy permanece alcanzable después de la migración, exponiendo autenticación más débil y TLS desactualizado.
- El almacenamiento de objetos público expone artefactos de build que contienen secretos de aplicación y código fuente.
- Un dashboard de soporte es alcanzable en un subdominio olvidado que nadie en el equipo actual recuerda.
- Un origen CDN es directamente alcanzable, saltando los controles de edge (rate limiting, WAF, restricciones geográficas).
- Una relación de vendor retirada deja un CNAME apuntando a un tenant que el vendor reasigna, permitiendo takeover.

## Notas relacionadas

- [[attack-surface-mapping]]
- [[internal-attack-surface]]
- [[exposed-service-triage]]
- [[exposed-storage]]
- [[admin-interface-discovery]]
- [[subdomain-takeover]]
- [[third-party-exposure]]
- [[public-asset-discovery|Public Asset Discovery]]
- [[company-osint|Company OSINT]]
- [[network-telemetry-sources-and-visibility|Network Telemetry Sources and Visibility]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Scan Anomaly Detection and Fingerprint Analysis]]

### Notas atómicas futuras sugeridas

- staging-environments
- remote-access-exposure
- certificate-transparency-monitoring
- cloud-origin-exposure
- public-object-storage-review
- outside-in-vs-inside-out-diff

## Referencias

- **Fundamental:** OWASP WSTG information gathering — https://owasp.org/www-project-web-security-testing-guide/latest/
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 104 — https://projectdiscovery.io/blog/reconnaissance-series-4
- **Fundamental:** CISA Cyber Hygiene Services — https://www.cisa.gov/cyber-hygiene-services
