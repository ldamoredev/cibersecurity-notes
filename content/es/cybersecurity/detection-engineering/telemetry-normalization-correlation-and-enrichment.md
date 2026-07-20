# Telemetry Normalization, Correlation, and Enrichment

## Definición

La normalización de telemetría mapea eventos heterogéneos a campos consistentes; el enrichment agrega contexto; la correlación cose eventos relacionados en evidencia higher-order.

## Por qué importa

La calidad de detección muchas veces depende menos de la regla y más de si el pipeline de telemetría produce eventos confiables, normalizados y enriquecidos. Una detección perfecta escrita contra `source.ip` falla si un log lo llama `src`, otro lo llama `client_ip` y un proxy lo pisa con una dirección de load balancer.

La ingeniería de sistemas de seguridad vive en esta capa. Normalización, enrichment, timestamps, resolución de entidades y claves de correlación deciden si las detecciones son posibles, explicables y mantenibles.

## Cómo funciona

Un pipeline de telemetría tiene **7 etapas de transformación**:

1. **Ingest.** Recolectar raw logs, alertas, flow records, eventos de endpoint, eventos de auditoría cloud y application logs.
2. **Parse.** Extraer campos desde JSON, syslog, CSV, EVE, Zeek TSV, Windows events, web logs y API records.
3. **Normalize.** Mapear campos locales a un schema como ECS, OTel semantic conventions o un modelo canónico local.
4. **Enrich.** Agregar owner del asset, rol, identidad, cloud metadata, GeoIP, threat intel, vulnerabilidad y contexto de negocio.
5. **Deduplicate.** Colapsar registros duplicados preservando conteo y detalles de fuente.
6. **Correlate.** Unir eventos por host, usuario, IP, proceso, sesión, flow ID, request ID, recurso cloud o ventana temporal.
7. **Quality monitor.** Detectar fallas de parser, field drift, timestamp skew, enrichments faltantes e ingestion delay.

Ejemplo:

```
Apache: 10.0.0.5 GET /admin 403
Zeek: id.orig_h=10.0.0.5 id.resp_h=10.0.0.20 id.resp_p=443 service=ssl
EDR: DeviceName=web-1 InitiatingProcessFileName=curl RemoteIP=10.0.0.20

Normalized:
source.ip=10.0.0.5 destination.ip=10.0.0.20 destination.port=443
process.name=curl host.name=web-1 event.action=http_request
```

La detección depende del join normalizado, no solo de los eventos raw.

## Técnicas / patrones

- **Schema mapping.** Mapear campos source-specific a ECS, OTel semantic conventions o campos locales.
- **Alineación de timestamps.** Preservar timestamp original, timestamp de ingestión, timezone, fuente de reloj y delay de parsing.
- **Claves de correlación.** Usar claves estables: device ID, process unique ID, cloud instance ID, user SID/object ID, Community ID, session ID, request ID.
- **Resolución de entidades.** Vincular IPs, hostnames, device IDs, recursos cloud, containers e identidades que representan la misma entidad.
- **Enrichment de assets.** Agregar owner, entorno, criticidad, rol, exposición, subnet y servicio de negocio.
- **Enrichment de identidad.** Agregar tipo de cuenta, estado MFA, membresía de grupos, privilege tier, IdP fuente y ownership de service account.
- **Enrichment de threat intel.** Agregar reputación y sightings con cuidado; no conviertas intel débil en veredicto.

## Perspectiva del atacante

Los atacantes explotan debilidades de pipeline moviéndose por lugares donde la identidad es ambigua, las IPs fuente son compartidas, los logs llegan tarde, el parsing falla o los joins de entidad están mal. Se benefician cuando un SOC no puede decir si `10.0.0.5` es una laptop de usuario, NAT gateway, nodo de contenedores, scanner o workload cloud.

## Perspectiva del defensor

Los defensores necesitan eventos normalizados que preserven la verdad raw. Buenos pipelines mantienen `event.original` o campos raw equivalentes, mapean campos comunes y guardan suficiente detalle source-specific para investigar. El objetivo no es aplanar todos los logs hasta que sean iguales; es hacer joins confiables sin perder evidencia.

## Tradeoffs de detección e ingeniería

1. **Schema canónico vs fidelidad de fuente.**
   Un schema común habilita correlación. La sobre-normalización puede borrar campos source-specific que explican el evento.

2. **Enrichment en tiempo real vs latencia.**
   Más enrichment mejora triage pero puede demorar alerting o fallar durante outages de dependencias.

3. **Deduplicación vs pérdida de evidencia.**
   Dedup reduce ruido pero puede esconder volumen, retries o confirmación multisensor.

4. **GeoIP y threat intel vs falsa confianza.**
   GeoIP puede estar mal, ser VPN/proxy-heavy o irrelevante. Threat intel puede estar stale o ser demasiado amplio.

5. **Ventanas de correlación vs joins falsos.**
   Ventanas más largas capturan secuencias lentas pero aumentan encadenamiento accidental de eventos.

## Detección y defensa

Ordenado por efectividad:

1. **Definí campos requeridos por detección.**
   Cada detección debería declarar qué campos normalizados necesita y qué ocurre si faltan.

2. **Preservá contenido raw del evento.**
   Los campos raw permiten a analistas debuggear parsers, probar chain-of-custody y recuperarse cuando cambian schemas.

3. **Usá identificadores de entidad estables.**
   Preferí device IDs, cloud resource IDs, user object IDs, process unique IDs y flow IDs por encima de display names o PIDs reciclados.

4. **Monitoreá salud del pipeline.**
   Tasa de errores de parser, tasa de campos faltantes, fallas de enrichment, clock skew e ingestión demorada deberían alertar.

5. **Versioná schemas y mappings.**
   ECS, OTel, schemas de vendors y campos locales evolucionan. Detection-as-code debería pinear y testear supuestos de mapping.

### Qué no funciona como defensa primaria

- **Regex parsing sin quality checks.** Se rompe silenciosamente cuando cambian formatos.
- **GeoIP como atribución.** La ubicación es evidencia débil y suele reflejar hosting, VPN o routing de proveedor.
- **Threat intel como veredicto.** Intel enriquece; no reemplaza comportamiento local y contexto de asset.
- **Joins solo por hostname.** Los hostnames cambian y colisionan; usá IDs estables cuando sea posible.
- **Descartar eventos originales.** Hace irrecuperables los errores de parser.

### Malentendidos operacionales

- **"La normalización es plomería aburrida."** Es la corteza sensorial del sistema de detección.
- **"Un schema común resuelve correlación."** El schema ayuda, pero timestamps, resolución de entidades y calidad de datos siguen decidiendo la corrección.
- **"El enrichment siempre mejora detección."** Enrichment malo crea falsos positivos confiados.
- **"La deduplicación solo elimina ruido."** Puede eliminar evidencia de repetición y escala.

### Limitaciones modernas

- La convergencia ECS y OTel es direccional, no una fusión perfecta; algunos campos tienen nombres o semánticas distintas.
- Los schemas de vendors cambian con el tiempo.
- Los recursos cloud son efímeros y la identidad IP es inestable.
- Logs SaaS pueden carecer de fidelidad raw o identificadores estables.

### Puntos ciegos de telemetría

- Eventos sin timestamp original o timezone.
- Process unique IDs, request IDs, session IDs, cloud IDs o identity object IDs faltantes.
- Logs de NAT/proxy/load-balancer que ocultan fuente original salvo que los forwarded fields se confíen correctamente.
- Sistemas de enrichment caídos durante incidentes.

## Labs prácticos

Usá logs locales generados.

### Lab 1 - Normalizar logs heterogéneos

Objetivo: Convertir registros tipo Apache, Zeek y endpoint en campos comunes.

```
cat > /tmp/raw-events.jsonl <<'EOF'
{"type":"apache","client_ip":"10.0.0.5","host":"web","method":"GET","uri":"/admin","status":403,"ts":"2026-05-11T10:00:00Z"}
{"type":"zeek","id.orig_h":"10.0.0.5","id.resp_h":"10.0.0.20","id.resp_p":443,"service":"ssl","ts":"2026-05-11T10:00:01Z"}
{"type":"edr","DeviceName":"web","InitiatingProcessFileName":"curl","RemoteIP":"10.0.0.20","RemotePort":443,"Timestamp":"2026-05-11T10:00:02Z"}
EOF
jq 'if .type=="apache" then {"@timestamp":.ts,"source.ip":.client_ip,"host.name":.host,"http.request.method":.method,"url.path":.uri,"http.response.status_code":.status}
elif .type=="zeek" then {"@timestamp":.ts,"source.ip":."id.orig_h","destination.ip":."id.resp_h","destination.port":."id.resp_p","network.protocol":.service}
else {"@timestamp":.Timestamp,"host.name":.DeviceName,"process.name":.InitiatingProcessFileName,"destination.ip":.RemoteIP,"destination.port":.RemotePort} end' /tmp/raw-events.jsonl
```

Telemetría esperada: tres fuentes se vuelven joinables. Los defensores observarían que la correlación requiere campos comunes. Limitación: mapping de juguete sin preservación raw ni validación de tipos. Malentendido corregido: "la regla es independiente de la calidad del pipeline."

### Lab 2 - Demostrar mala resolución de entidades

Objetivo: Mostrar por qué los joins solo por IP son débiles.

```
cat > /tmp/entities.csv <<'EOF'
time,ip,entity
10:00,10.0.0.5,laptop-a
10:05,10.0.0.5,vpn-nat
10:10,10.0.0.5,container-node
EOF
column -t -s, /tmp/entities.csv
```

Telemetría esperada: una IP mapea a múltiples entidades en el tiempo. Los defensores necesitarían timestamps e IDs estables. Malentendido corregido: "source IP equivale a actor."

## Ejemplos prácticos

- Una alerta Suricata y Zeek `conn.log` se unen limpiamente solo cuando timestamps y 5-tuples alinean.
- Un evento de proceso EDR y un evento de red se unen correctamente con process unique ID, no solo PID.
- Un cloud flow log necesita instance ID y tags antes de que analistas sepan owner y criticidad.
- Un proxy log necesita parsing confiable de forwarded-header antes de que `source.ip` sea significativo.

## Notas relacionadas

- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[false-positives-false-negatives-and-detection-tradeoffs|Falsos positivos, falsos negativos y tradeoffs de detección]]
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths y observabilidad de kill chain]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[silver-ticket-and-service-account-persistence|Silver Ticket and Service Account Persistence]]
- [[client-ip-trust|Client IP Trust]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]

### Notas atómicas futuras sugeridas

- ecs-and-otel-for-security-telemetry
- entity-resolution-for-detection
- pipeline-health-monitoring
- community-id-correlation

## Referencias

- **Fundamental:** Elastic Common Schema Reference - https://www.elastic.co/docs/reference/ecs/
- **Fundamental:** ECS and OpenTelemetry - https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry
- **Fundamental:** OpenTelemetry Semantic Conventions - https://opentelemetry.io/docs/concepts/semantic-conventions/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
