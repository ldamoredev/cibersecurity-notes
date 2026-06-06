# Índice de Detection Engineering

## Definición

Detection engineering es la disciplina de convertir el comportamiento de atacantes y sistemas en telemetría confiable, explicable y operacionalmente útil: analíticas, alertas y evidencia de respuesta.

> *Antes de esta rama:*
> - [[index|Fundamentos]] (Fase 0).
> - [[index|Networking]] — no podés detectar lo que no podés razonar.
> - [[index|Offensive Security / Recon]] — leé cada nota de detección junto a su contraparte ofensiva.

## Por qué importa

La ciberseguridad moderna es una guerra de telemetría. Los atacantes intentan controlar lo que los defensores pueden observar, correlacionar, retener e interpretar. Los defensores ganan menos apostando a la prevención perfecta y más ingeniando visibilidad a través de endpoints, redes, identidades, control planes cloud y fronteras de aplicación.

Esta rama no está centrada en vendors y no enseña operación superficial de herramientas. Explica las superficies de detección, los límites de los sensores, los patrones de comportamiento y los tradeoffs de correlación que hacen útiles a las herramientas.

## Spine de la rama

1. [[network-telemetry-sources-and-visibility]]
2. [[zeek-suricata-and-netflow-analysis]]
3. [[ids-ips-and-behavioral-detection-pipelines]]
4. [[behavioral-detection-vs-signature-detection]]
5. [[false-positives-false-negatives-and-detection-tradeoffs]]
6. [[telemetry-normalization-correlation-and-enrichment]]
7. [[encrypted-traffic-analysis-and-metadata-leakage]]
8. [[scan-anomaly-detection-and-fingerprint-analysis]]
9. [[detection-evasion-myths-and-modern-limitations]]
10. [[edr-network-observability-and-process-correlation]]
11. [[attack-path-correlation-and-kill-chain-observability]]

## Orden de estudio

### 1. Visibilidad antes que reglas

- [[network-telemetry-sources-and-visibility]] — qué pueden y no pueden ver los paquetes, flows, logs, sensores de endpoint y logs cloud.
- [[zeek-suricata-and-netflow-analysis]] — cómo tres capas comunes de telemetría de red se complementan y se contradicen.

### 2. Diseño del pipeline de detección

- [[ids-ips-and-behavioral-detection-pipelines]] — cómo encajan las etapas de firma, anomalía, comportamiento, enriquecimiento, correlación y respuesta.
- [[behavioral-detection-vs-signature-detection]] — por qué la detección madura mezcla indicadores estáticos, IOAs, analíticas de comportamiento y lógica de secuencia.
- [[false-positives-false-negatives-and-detection-tradeoffs]] — por qué la detección es ingeniería de precision/recall y capacidad operacional, no verdad binaria.
- [[telemetry-normalization-correlation-and-enrichment]] — por qué los schemas, el enriquecimiento, la resolución de entidades, los timestamps y los joins frecuentemente deciden la calidad de la detección.

### 3. Comportamiento de escaneo como caso de estudio de detección

- [[scan-anomaly-detection-and-fingerprint-analysis]] — por qué el escaneo no es un evento único sino un patrón de comportamiento que cruza timing, fan-out, forma TCP/IP, fingerprints TLS y transiciones de descubrimiento a explotación.
- [[detection-evasion-myths-and-modern-limitations]] — cómo testear afirmaciones de evasión antiguas contra telemetría multi-sensor moderna.

### 4. Tráfico cifrado y metadata

- [[encrypted-traffic-analysis-and-metadata-leakage]] — por qué el cifrado oculta el contenido pero no todo el comportamiento, metadata o contexto de endpoint.

### 5. Correlación endpoint-red y de ruta de ataque

- [[edr-network-observability-and-process-correlation]] — por qué la defensa moderna cambió cuando los eventos de red se volvieron unibles a procesos, usuarios, hashes y cadenas de parentesco.
- [[attack-path-correlation-and-kill-chain-observability]] — por qué la detección moderna frecuentemente detecta relaciones entre eventos en lugar de eventos aislados.

### 6. Telemetría del host (Windows)

- [[windows-event-logs]] — los 30 Event IDs que cargan la mayor parte de la telemetría de seguridad Windows, las precondiciones de política de auditoría que los hacen aparecer, y los patrones de secuencia de Event ID que impulsan la detección de ataques dirigidos a Windows.

## Afirmaciones centrales

- El sigilo moderno no es "paquetes lentos" o "trucos de fragmentación"; es gestionar telemetría a través de muchos sensores.
- El tráfico cifrado sigue filtrando metadata: timing, endpoints, tamaños, DNS, SNI donde sea visible, ALPN, fingerprints estilo JA3/JA4, ancestría de procesos, logs cloud y contexto de identidad.
- NetFlow/IPFIX, Zeek, Suricata, EDR, logs de flow cloud, logs WAF y detecciones SIEM son distintas capas de evidencia, no etiquetas intercambiables.
- La calidad de la detección depende del posicionamiento del sensor, pérdida de captura, timestamps, resolución de entidades, baselines, ventanas de correlación y evidencia de triage.
- Los falsos positivos y falsos negativos son retroalimentación de ingeniería, no excepciones vergonzosas.
- La madurez de detección se mueve del matching frágil de artefactos hacia el modelado de comportamiento y secuencia, mientras sigue usando firmas donde son precisas.

## Anclas entre ramas

### Seguridad ofensiva

- [[active-recon|Active Recon]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

### Networking

- [[tcp-ip-basics|TCP/IP Basics]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[nmap-scanning|Nmap Scanning]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[service-enumeration|Service Enumeration]]
- [[tls-https|TLS and HTTPS]]

### Cloud y playbooks

- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[cloud-network-boundaries|Cloud Network Boundaries]]
- [[run-scan-pipeline|Run External Recon Scan Pipeline]]

### Hubs conceptuales internos

- [[behavioral-detection-vs-signature-detection]]
- [[false-positives-false-negatives-and-detection-tradeoffs]]
- [[telemetry-normalization-correlation-and-enrichment]]
- [[encrypted-traffic-analysis-and-metadata-leakage]]
- [[detection-evasion-myths-and-modern-limitations]]
- [[attack-path-correlation-and-kill-chain-observability]]

## Notas futuras sugeridas

- correlation-windows-and-entity-resolution
- tls-fingerprinting-for-detection
- tap-vs-span-sensor-placement
- cloud-flow-logs-and-network-detection
- detection-as-code-and-rule-lifecycle
- alert-triage-and-evidence-quality
- honeyports-and-tarpit-detection
- threat-hunting-with-zeek
- scan-to-exploit-transition-detection
- detection-coverage-vs-attack-coverage
- ecs-and-otel-for-security-telemetry
- precision-and-recall-for-security-detections
- attack-graph-detection
- beaconing-analysis

## Referencias

- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection — https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Fundamental:** MITRE ATT&CK Data Sources — https://attack.mitre.org/datasources/
- **Docs Oficiales:** Zeek Logs — https://docs.zeek.org/en/current/logs/
- **Docs Oficiales:** Suricata EVE JSON Output — https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
