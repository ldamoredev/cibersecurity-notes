---
type: concept
status: active
created: 2026-06-03
updated: 2026-06-03
tags:
  - cybersecurity
  - detection-engineering
  - network-security-monitoring
  - nsm
  - telemetry
  - methodology
sources: []
---

# Disciplina de Network Security Monitoring (NSM)

## Definición
El network security monitoring (NSM) es la disciplina de *recolectar, retener y analizar evidencia de red* para que las intrusiones se detecten e investiguen incluso cuando la prevención ya falló. NSM no es un producto ni un formato de regla — es la postura operativa que dice que **la visibilidad se ingenia antes de escribir la detección**: decidís dónde se sientan los sensores y qué capas de evidencia retenés, y solo entonces componés detecciones sobre esa evidencia. Esta nota es la spine del lado de red del branch de detection-engineering; las notas de sensores, herramientas y telemetría cuelgan de ella.

## Por qué importa
La prevención eventualmente falla — toda credencial se phishea, todo perímetro tiene un agujero, todo EDR tiene un hueco. NSM es la disciplina construida sobre esa premisa (la tesis fundacional de Richard Bejtlich): si no podés frenar la intrusión, al menos tenés que *verla* y reconstruir qué pasó. El payoff a nivel de branch es cuádruple:

- **La calidad de detección está limitada por la visibilidad.** Una regla perfecta sobre datos que nunca recolectaste dispara cero veces. La decisión que sostiene la estructura es la ubicación de sensores y la retención de evidencia, no la sintaxis de la regla — por eso esta nota se sienta por encima de [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]] y [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]].
- **La alta fidelidad viene de la composición, no de una sola señal.** Una sola regla es ruidosa o ciega. La detección moderna de alta fidelidad acumula varias señales de red débiles (forma del flow + anomalía de protocolo + fingerprint + correlación de endpoint) en un único hallazgo fuerte y resistente a la evasión. Este es el núcleo de la disciplina y la respuesta a "quedarse bajo 1% de falsos positivos a escala empresarial".
- **La evidencia sobrevive a la alerta.** NSM guarda registros de sesión y transacción para que una intrusión descubierta un martes pueda recorrerse hacia atrás hasta su origen del sábado. La detección sin evidencia retenida es una alarma sin caja negra.
- **La disciplina es adversaria.** Toda elección de recolección tiene una evasión correspondiente (payloads cifrados, beacons low-and-slow, puntos ciegos east-west), y toda evasión tiene una señal residual. NSM es la mitad del defensor de la [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|dualidad atacante-defensor]] jugada en el wire.

## Cómo funciona
NSM corre como un **ciclo de 4 etapas** — *recolectar → detectar → analizar → escalar* — retroalimentando a la recolección a medida que se encuentran huecos:

1. **Recolectar.** Ubicá sensores en las fronteras de confianza (perímetro, DMZ, inter-VLAN, egress de nube) y en los endpoints, y decidí qué capas de evidencia retener y por cuánto tiempo.
2. **Detectar.** Corré lógica de firmas, anomalía, conductual y correlación contra la evidencia recolectada para aflorar eventos candidatos.
3. **Analizar.** Un humano (o una regla de orden superior) pivotea a través de las capas de evidencia para confirmar o descartar el candidato y dimensionarlo.
4. **Escalar.** La actividad confirmada se vuelve un incidente; los huecos encontrados durante el análisis se vuelven nuevos requisitos de recolección, cerrando el loop.

La evidencia sobre la que corre el ciclo viene en **4 capas**, ordenadas de la más-barata-y-más-retenida a la más-rica-y-menos-retenida — y, críticamente, de *menor-fidelidad a mayor-fidelidad*:

| Capa | Fuente de ejemplo | Responde | Economía de retención |
|---|---|---|---|
| **Flow / sesión** | NetFlow / IPFIX | quién habló con quién, cuánto, cuándo | barato, semanas–meses, sin contenido |
| **Logs de transacción / protocolo** | Zeek `conn`/`dns`/`http`/`ssl`/`x509` | registros estructurados por protocolo, fingerprints | costo medio, alto valor analítico |
| **Alerta / firma** | Suricata / Snort EVE | patrón known-bad coincidido | solo-evento, apunta a la aguja |
| **Contenido completo** | PCAP | cada byte en el wire | caro, horas–días, verdad de base |

Dos tipos de evidencia transversales sobreviven al cifrado e importan desproporcionadamente en 2026: los **fingerprints** (fingerprints TLS de cliente/servidor JA3/JA4, fingerprints HTTP/2) y la **metadata** (timing, forma del flow, SNI, campos de certificado) — ver [[encrypted-traffic-analysis-and-metadata-leakage|Análisis de tráfico cifrado y fuga de metadata]].

El insight central de la disciplina: **la clave de caché de la detección es la clave de caché de la evidencia.** Si el comportamiento del origin lee una señal que tus sensores nunca registraron, ninguna regla puede verla jamás. El bug rara vez es "la regla estaba mal"; es "la capa de evidencia que lo habría mostrado nunca se recolectó, o se recolectó donde el tráfico no pasa".

> Adaptación de secciones: esta es una nota de metodología, así que *Cómo funciona* describe un ciclo y un modelo de evidencia en vez de un único mecanismo de exploit, y *Variantes y bypasses* abajo carga la vista de evasión-del-adversario en vez de variantes de payload.

## Técnicas / patrones
Lo que realmente hace un detection engineer dentro de la disciplina:

- **Mapeá la recolección a un modelo de cobertura antes de escribir reglas.** Usá [MITRE ATT&CK Data Sources](https://attack.mitre.org/datasources/) como el checklist: para cada técnica que te importa, nombrá la fuente de datos y el sensor que la presenciaría. Las técnicas sin mapear son puntos ciegos, no "bajo riesgo".
- **Componé detecciones multi-señal (fuente → corroboración → enriquecimiento → veredicto).** Empezá de una primitiva sospechosa (un nuevo hash JA3, un dominio padre DNS raro, un flow a un ASN fresco), corroborá con una segunda capa independiente, enriquecé con contexto de activo/identidad, después decidí. Las reglas de una sola capa son la fábrica de FP.
- **Elegí la frontera enriquecer-vs-filtrar deliberadamente.** Filtrar descarta eventos antes del almacenamiento (barato, irreversible, crea puntos ciegos); enriquecer agrega contexto en tiempo de query (flexible, costoso). Filtrá solo lo que podés probar que nunca es evidencia; enriquecé el resto.
- **Hacé baseline por-entidad, no globalmente.** "Inusual" tiene sentido solo contra una baseline por-host / por-cuenta-de-servicio / por-segmento. Un umbral global se pierde al operador quirúrgico y ahoga al ruidoso.
- **Pivoteá entre capas durante el análisis.** Alerta (Suricata) → transacción (Zeek `ssl.log`, `dns.log`) → flow (¿fue un one-shot o un beacon?) → contenido completo (PCAP, solo si está retenido). La fluidez para moverse arriba y abajo del stack de capas es la habilidad del analista.
- **Tratá las detecciones como código.** Versioná las reglas, escribilas contra capturas de test, y revisá los cambios — ver *Detección y defensa* abajo.

## Variantes y bypasses
Para una nota de disciplina, esta sección es el **mapa de presión-del-adversario**: las 4 formas estructurales en que los operadores derrotan NSM, y la señal residual que deja cada una.

### 1. Ceguera por cifrado
TLS 1.3, ESNI/ECH y DoH ocultan payloads y cada vez más ocultan el SNI. La capa de contenido se oscurece. **Señal residual:** los fingerprints JA3/JA4, la metadata de certificado, el timing y volumen de flow, y la reputación del destino todavía sobreviven — el operador puede cifrar el *qué* pero no el *que-pasó*.

### 2. Evasión volumétrica / low-and-slow
Beacons con jitter a una-vez-por-hora, exfil de datos throttleado bajo los umbrales de alerta, tráfico mezclado en el horario laboral. Las reglas de umbral se lo pierden. **Señal residual:** la regularidad en sí es anómala — el análisis de beaconing sobre el timing de inter-arribo y la consistencia de byte-count atrapa el tráfico a ritmo de máquina que un humano nunca generaría.

### 3. Huecos de ubicación de sensores (east-west y nube)
NSM históricamente miraba el tráfico north-south (perímetro); el movimiento lateral dentro de un segmento, y el tráfico entre workloads de nube, puede no cruzar nunca un sensor. **Señal residual:** la telemetría de endpoint — acá es donde la [[edr-network-observability-and-process-correlation|observabilidad de red de EDR]] y los flow logs de nube recuperan la visibilidad que los sensores de paquetes no tienen. La forma moderna de la disciplina es *red + endpoint + identidad*, no red sola.

### 4. Living-off-the-land / mimetismo de protocolo
C2 sobre HTTPS hacia un CDN, DNS tunneling que parece resolución normal, tráfico moldeado para imitar SaaS legítimo. El matching de firmas falla porque los bytes son "normales". **Señal residual:** anomalías conductuales y relacionales — una workstation que nunca habló con un host ahora beaconeándole, un proceso sin razón de negocio para hacer queries DNS TXT.

El hilo conductor: **ninguna capa por sí sola es a prueba de evasión, pero las capas no son independientes.** Derrotarlas todas a la vez — cifrado, lento, fuera-de-sensor, *y* conductualmente normal a través de endpoint e identidad — es la vara cara que NSM fuerza al operador a superar.

## Impacto
Lo que determina la calidad de la disciplina, ordenado por consecuencia:

- **Dwell time.** Un NSM maduro comprime el dwell del atacante de meses a horas; un NSM ausente o solo-alerta deja las intrusiones sin descubrir hasta que un tercero las reporta.
- **Alcance investigativo.** La evidencia de sesión/transacción retenida deja a los responders reconstruir la kill chain completa; sin ella, el scoping es adivinanza y la remediación es incompleta.
- **Carga de falsos positivos y burnout de analistas.** La detección de una sola señal, sin baseline, inunda el SOC, genera fatiga de alertas y *baja* la tasa de detección real a medida que los analistas se desconectan — el problema de precisión/recall del que es dueña [[false-positives-false-negatives-and-detection-tradeoffs|Falsos positivos, falsos negativos y trade-offs de detección]].
- **Resiliencia a la evasión.** La composición multi-capa sube el costo del operador; la detección de una sola capa es bypasseada por la primera técnica que evita esa capa.
- **Defendibilidad de auditoría y cumplimiento.** "Lo habríamos visto" solo es cierto si la capa de evidencia y la retención existían en el momento — NSM es también el registro que les responde a los reguladores.

## Detección y defensa
Para una nota de disciplina-de-detección, "defensa" es *cómo hacer la disciplina de alta fidelidad*. Ordenado por efectividad:

1. **Ingeniá la visibilidad antes que la detección.**
   Decidí la ubicación de sensores y la retención de capas de evidencia contra un mapa de cobertura de ATT&CK Data Sources primero. Una regla sobre datos no recolectados es teatro. Este es el control de mayor palanca porque limita todo lo que viene después.

2. **Componé detecciones multi-señal (de orden superior).**
   Agregá varias señales débiles independientes en un único hallazgo fuerte en vez de alertar sobre cada una. Las [reglas de detección de orden superior](https://www.elastic.co/security-labs/higher-order-detection-rules) de Elastic formalizan esto: detecciones cuyos inputs son otras detecciones. Esto es lo que sube simultáneamente el recall (atrapa la evasión que esquiva una señal) y la precisión (una coincidencia entre capas independientes rara vez es benigna).

3. **Tratá las detecciones como código con un ciclo de vida.**
   Versioná las reglas en control de código, testealas contra capturas etiquetadas (true-positive y known-benign), y revisá los cambios. Decidí explícitamente si **retirar** (la técnica está muerta / el costo de FP excede el valor) o **evolucionar** (re-baselinear, agregar una señal corroboradora) una regla — las reglas que nunca se revisan se pudren silenciosamente en ruido o ceguera.

4. **Baseline y enriquecé por-entidad.**
   Mantené un normal por-host/por-cuenta/por-segmento, y enriquecé los eventos con criticidad de activo y contexto de identidad en tiempo de análisis para que el veredicto tenga en cuenta el *quién* y el *qué*, no solo *qué paquete*.

5. **Tuneá contra la evasión del operador, no solo el tráfico de lab.**
   Testeá las detecciones contra las evasiones de *Variantes y bypasses* (cifrado, throttleado, fuera-de-sensor, LOTL). Una regla que solo atrapa la herramienta default ruidosa es una regla por la que el operador real pasa de largo — ver [[detection-evasion-myths-and-modern-limitations|Mitos de evasión de detección y limitaciones modernas]].

6. **Instrumentá los huecos que no podés cerrar.**
   Donde una capa es genuinamente ciega (east-west cifrado, nube no gestionada), documentá el punto ciego y compensá con la capa adyacente (endpoint/identidad) en vez de pretender que existe cobertura.

### Qué no funciona como defensa primaria
- **Detección solo-por-firmas.** Las firmas atrapan bytes known-bad; son ciegas al C2 novedoso y cifrado-y-mimetizado. Necesaria como una capa, fatal como la única.
- **Alerta solo-por-umbral.** Los umbrales volumétricos se pierden al operador quirúrgico low-and-slow e inundan con ráfagas ruidosas-pero-benignas. La conducta y las baselines por-entidad son el arreglo, no un número más grande.
- **Feeds de IOC como estrategia.** Los indicadores atómicos (IPs, hashes, dominios) son lo más barato para que un atacante rote — la base de la Pirámide del Dolor de David Bianco. Útiles para enriquecimiento, no como programa de detección.
- **"Tenemos un SIEM".** Un SIEM es un motor de queries sobre lo que sea que le alimentaste. Sin recolección ingeniada y detecciones compuestas, es un balde de logs caro.
- **Más alertas.** El volumen no es fidelidad. La alerta sin componer y sin baseline *reduce* la detección efectiva al quemar la atención del analista.

## Labs prácticos
Corré solo contra entornos de lab propios o engagements autorizados.

### Triajear evidencia de transacción de Zeek
```bash
# Desde un directorio de salida de Zeek: top destinos por conteo de conexión, después
# traé los fingerprints SSL que coinciden. Dos capas (flow + transacción) en un pivot.
cat conn.log | zeek-cut id.resp_h | sort | uniq -c | sort -rn | head
cat ssl.log  | zeek-cut id.resp_h server_name ja3 ja3s validation_status | sort | uniq -c | sort -rn | head
```
Un destino que es de alto volumen *y* presenta un JA3 raro con `validation_status` distinto de "ok" vale más que cualquiera de las señales sola.

### Aflorar beaconing en el timing de flow
```bash
# Regularidad de inter-arribo para un par src→dst. El C2 a ritmo de máquina muestra
# deltas casi-constantes; el tráfico humano es a ráfagas e irregular.
cat conn.log | zeek-cut ts id.orig_h id.resp_h \
  | awk '$2=="10.0.0.50" && $3=="203.0.113.10" {if(p)print $1-p; p=$1}' \
  | sort -n | uniq -c | sort -rn | head
```
Un cluster apretado de deltas idénticos es la señal residual que sobrevive al jitter solo parcialmente — exactamente el punto de la resiliencia-a-la-evasión.

### Leer una alerta EVE de Suricata y pivotear al flow
```bash
# Traé una alerta, después el registro de flow para el mismo flow_id — capa alerta → capa flow.
jq -c 'select(.event_type=="alert")  | {ts:.timestamp, sig:.alert.signature, fid:.flow_id, src:.src_ip, dst:.dest_ip}' eve.json | head
jq -c 'select(.event_type=="flow" and .flow_id==<FLOW_ID>) | {bytes:.flow.bytes_toserver, pkts:.flow.pkts_toserver, age:.flow.age}' eve.json
```
La alerta dice "qué"; el flow dice "cuánto / cuánto tiempo" — el veredicto del analista necesita ambos.

### Construir un mini mapa de cobertura de ATT&CK
```text
# Para tres técnicas que te importan, nombrá la fuente de datos y el sensor.
# Las celdas vacías son puntos ciegos — la salida de la primera etapa de la disciplina.
Técnica                    | Fuente de datos (ATT&CK)    | Sensor / capa         | ¿Recolectado?
T1071 C2 de App-Layer (HTTPS)| Network Traffic Flow        | Zeek ssl/conn + JA4   | s/n
T1048 Exfil sobre proto alt | Network Traffic Content     | Suricata + NetFlow    | s/n
T1021 Lateral (east-west)   | Network Traffic Flow        | tap inter-VLAN?       | s/n  <-- usualmente el hueco
```
Las celdas vacías de "¿Recolectado?" son tu backlog real — superan a cualquier regla nueva.

## Ejemplos prácticos
- **C2 con beaconing sobre HTTPS hacia un CDN.** Las firmas no ven nada; la detección se construye de regularidad de flow + un JA4 raro + un destino que el host nunca contactó, compuestos en un único hallazgo.
- **Exfil lento bajo el umbral de DLP.** Ninguna hora individual dispara la alerta; el byte-count acumulado a un ASN externo durante una semana, baselined por-host, sí.
- **Movimiento lateral east-west.** Nunca cruza el sensor de perímetro; atrapado por telemetría de red de endpoint correlacionada a un proceso sin razón de negocio para abrir SMB a un par ([[edr-network-observability-and-process-correlation|Observabilidad de red de EDR y correlación de procesos]]).
- **DNS tunneling que parece resolución.** La entropía por-dominio y el volumen de registros TXT contra una baseline por-resolver lo marcan donde el matching de firmas falla.
- **Reconstrucción post-incidente.** Una alerta de robo de credenciales un martes se recorre hacia atrás a través de logs `conn`/`ssl` de Zeek retenidos hasta un drive-by del sábado — solo porque la evidencia de sesión se retuvo, no solo las alertas.

## Notas relacionadas
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]] — la capa de ubicación-de-sensores y arquitectura-de-visibilidad sobre la que se sienta esta disciplina.
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]] — las tres herramientas que producen las capas de evidencia transacción/alerta/flow.
- [[ids-ips-and-behavioral-detection-pipelines|IDS/IPS y pipelines de detección conductual]] — la mecánica del pipeline de detección dentro de la etapa *detectar*.
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enriquecimiento de telemetría]] — el mapeo de esquema y el enriquecimiento que hacen posible la correlación entre capas.
- [[behavioral-detection-vs-signature-detection|Detección conductual vs detección por firmas]] — la elección de modelo que decide qué puede atrapar cada capa.
- [[false-positives-false-negatives-and-detection-tradeoffs|Falsos positivos, falsos negativos y trade-offs de detección]] — la disciplina de precisión/recall detrás de "bajo 1% de FP a escala".
- [[attack-path-correlation-and-kill-chain-observability|Correlación de rutas de ataque y observabilidad de la kill chain]] — la correlación multi-etapa, la composición de orden superior a la que apunta esta nota.
- [[encrypted-traffic-analysis-and-metadata-leakage|Análisis de tráfico cifrado y fuga de metadata]] — la historia de señal-residual cuando la capa de contenido se oscurece.
- [[edr-network-observability-and-process-correlation|Observabilidad de red de EDR y correlación de procesos]] — la mitad de endpoint que cierra los puntos ciegos east-west y de nube.
- [[cybersecurity/security-playbooks/detect-external-scan-pipeline|Detectar el pipeline de escaneo externo]] — un playbook concreto de NSM que instancia este ciclo.
- [[cybersecurity/foundations/attacker-defender-duality-as-a-learning-tool|La dualidad atacante-defensor]] — el meta-encuadre: NSM es la silla del defensor frente a la del operador.

### Notas atómicas futuras sugeridas
- [[detection-as-code-and-rule-lifecycle|Detección como código y ciclo de vida de reglas]]
- [[tap-vs-span-sensor-placement|Ubicación de sensores: tap vs SPAN]]
- [[beaconing-analysis|Análisis de beaconing]]
- [[cloud-flow-logs-and-network-detection|Flow logs de nube y detección de red]]

> Las notas atómicas futuras se listan como `[[wikilinks]]` aunque el archivo destino todavía no exista, para que registren como forward-links en Obsidian.

## Referencias
- **Foundational:** MITRE ATT&CK Data Sources — https://attack.mitre.org/datasources/
- **Foundational:** NIST SP 800-94 — Guide to Intrusion Detection and Prevention Systems — https://csrc.nist.gov/pubs/sp/800/94/final
- **Official Tool Docs:** Zeek logs reference — https://docs.zeek.org/en/current/logs/
- **Research / Deep Dive:** Elastic Security Labs — Higher-Order Detection Rules — https://www.elastic.co/security-labs/higher-order-detection-rules
- **Mitigation / Operations:** CISA — Best Practices for Event Logging and Threat Detection — https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
