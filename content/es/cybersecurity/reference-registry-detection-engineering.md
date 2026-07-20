# Registro de Referencia - Ingeniería de Detección

## Propósito

Este registro es la fuente de verdad para referencias en `cybersecurity/detection-engineering/`.

Usalo para:
- mantener las notas de detection-engineering ancladas en documentación primaria de telemetría y sensores
- evitar deriva hacia tutoriales de vendors
- conectar comportamiento ofensivo con evidencia visible para defensores
- distinguir telemetría de paquetes, flow, protocolo, endpoint, cloud y correlación

Usalo junto con:
- [[index|Índice de Ingeniería de Detección]]
- [[reference-registry-networking|Reference Registry - Networking]]
- [[reference-registry-offensive-security|Reference Registry - Offensive Security]]
- [[reference-registry-cloud-security|Reference Registry - Cloud Security]]

---

## Política de selección de referencias

### Prioridad de fuentes

1. estándares oficiales y documentación de proyectos
2. documentación oficial de schemas de vendors cuando la nota depende de campos de telemetría
3. investigación de ingeniería de alta señal de equipos de seguridad reputados
4. guía pública alineada a estándares de CISA/NIST/MITRE/SANS
5. fuentes secundarias solo cuando agregan un detalle de ingeniería concreto no cubierto en otro lado

### Objetivo por nota

- mínimo 2 referencias
- objetivo 3-4 referencias
- máximo default 5 referencias

### Etiquetado

Usá:
- **Fundamental**
- **Official Tool Docs**
- **Telemetry Schema**
- **Investigación / Deep Dive**
- **Mitigación / Operaciones**

---

# Mapa de temas de detection-engineering

## Set común de autoridad externa

Usá estas como familias de fuentes a nivel registry. Agregá el subset relevante más pequeño a la sección compacta `## Referencias` de cada nota atómica; no crees nuevas páginas `wiki/sources/` para estas referencias externas ordinarias.

- **Official Tool Docs:** Zeek documentation - https://docs.zeek.org/
- **Official Tool Docs:** Zeek logs reference - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Zeek capture loss logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata documentation - https://docs.suricata.io/
- **Official Tool Docs:** Suricata EVE JSON output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Fundamental:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
- **Fundamental:** RFC 5470 IPFIX Architecture - https://www.rfc-editor.org/rfc/rfc5470.html
- **Telemetry Schema:** Microsoft Defender XDR advanced hunting schema tables - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-schema-tables
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
- **Fundamental:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Fundamental:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Investigación / Deep Dive:** Salesforce Engineering TLS fingerprinting with JA3 and JA3S - https://engineering.salesforce.com/tls-fingerprinting-with-ja3-and-ja3s-247362855967
- **Investigación / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Investigación / Deep Dive:** FoxIO JA4+ overview - https://foxio.io/ja4
- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Mitigación / Operaciones:** CISA Use Logging on Business Systems - https://www.cisa.gov/use-logging-business-systems
- **Investigación / Deep Dive:** Elastic higher-order detection rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Investigación / Deep Dive:** Elastic endpoint-to-environment investigation - https://www.elastic.co/security-labs/investigating-from-the-endpoint-across-your-environment
- **Official Tool Docs:** Cisco Catalyst 9000 SPAN guide - https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mgmt/management-configuration-guide/span.html
- **Official Tool Docs:** Cisco SPAN configuration example - https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6500-series-switches/10570-41.html
- **Fundamental:** Elastic Common Schema reference - https://www.elastic.co/docs/reference/ecs/
- **Fundamental:** ECS and OpenTelemetry - https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry
- **Fundamental:** OpenTelemetry Semantic Conventions - https://opentelemetry.io/docs/concepts/semantic-conventions/
- **Fundamental:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Fundamental:** MITRE ATT&CK Analytics - https://attack.mitre.org/analytics/
- **Fundamental:** MITRE ATT&CK Enterprise Tactics - https://attack.mitre.org/tactics/enterprise/
- **Fundamental:** NIST SP 800-94 Guide to Intrusion Detection and Prevention Systems - https://csrc.nist.gov/pubs/sp/800/94/final
- **Fundamental:** RFC 8446 TLS 1.3 - https://datatracker.ietf.org/doc/html/rfc8446

## behavioral-detection-vs-signature-detection

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Fundamental:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table

Por qué:
- esta nota distingue artifact matching, IOCs, IOAs, behavior analytics y lógica de secuencia sin fingir que un modelo reemplaza a los otros

---

## false-positives-false-negatives-and-detection-tradeoffs

Referencias preferidas:
- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
- **Fundamental:** NIST SP 800-94 Guide to Intrusion Detection and Prevention Systems - https://csrc.nist.gov/pubs/sp/800/94/final
- **Investigación / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Fundamental:** MITRE ATT&CK Analytics - https://attack.mitre.org/analytics/

Por qué:
- esta nota posee precision/recall, fatiga de alertas, problemas de base-rate, thresholds, tuning drift, riesgo de supresión y límites operativos del SOC

---

## telemetry-normalization-correlation-and-enrichment

Referencias preferidas:
- **Fundamental:** Elastic Common Schema Reference - https://www.elastic.co/docs/reference/ecs/
- **Fundamental:** ECS and OpenTelemetry - https://www.elastic.co/docs/reference/ecs/ecs-opentelemetry
- **Fundamental:** OpenTelemetry Semantic Conventions - https://opentelemetry.io/docs/concepts/semantic-conventions/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html

Por qué:
- esta nota posee schema mapping, calidad de campos, enrichment, resolución de entidades, alineación de timestamps y confiabilidad de claves de correlación

---

## encrypted-traffic-analysis-and-metadata-leakage

Referencias preferidas:
- **Fundamental:** RFC 8446 TLS 1.3 - https://datatracker.ietf.org/doc/html/rfc8446
- **Fundamental:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Investigación / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html

Por qué:
- esta nota explica por qué el cifrado oculta contenido pero deja metadata, timing, forma de flow, handshakes TLS, contexto de endpoint y evidencia de correlación

---

## detection-evasion-myths-and-modern-limitations

Referencias preferidas:
- **Official Tool Docs:** Nmap Firewall/IDS Evasion and Spoofing - https://nmap.org/book/man-bypass-firewalls-ids.html
- **Official Tool Docs:** Zeek Capture Loss and Reporter Logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table

Por qué:
- esta nota desarma folklore viejo de evasión separando verdades parciales de telemetría residual y correlación moderna

---

## attack-path-correlation-and-kill-chain-observability

Referencias preferidas:
- **Fundamental:** MITRE ATT&CK Enterprise Tactics - https://attack.mitre.org/tactics/enterprise/
- **Fundamental:** MITRE ATT&CK Detection Strategies - https://attack.mitre.org/detectionstrategies/
- **Investigación / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table

Por qué:
- esta nota posee correlación de secuencias, acumulación de señales débiles, razonamiento de grafos, reconstrucción de timeline y observabilidad de attack paths

## scan-anomaly-detection-and-fingerprint-analysis

Referencias preferidas:
- **Official Tool Docs:** Nmap Reference Guide - Timing and Performance - https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Masscan README and man page - https://github.com/robertdavidgraham/masscan
- **Fundamental:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Investigación / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Suricata EVE JSON TLS fields - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html

Por qué:
- esta nota une mecánicas ofensivas de scan con timing, fan-out, fingerprints TCP/TLS y metadata de protocolo visibles para defensores

---

## network-telemetry-sources-and-visibility

Referencias preferidas:
- **Fundamental:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
- **Official Tool Docs:** Zeek logs reference - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Cisco SPAN configuration guide - https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mgmt/management-configuration-guide/span.html
- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection

Por qué:
- esta nota posee arquitectura de visibilidad: dónde están los sensores, qué pueden inferir y cómo pérdida/agregación/cifrado/abstracción cloud afectan evidencia

---

## ids-ips-and-behavioral-detection-pipelines

Referencias preferidas:
- **Official Tool Docs:** Suricata User Guide and EVE JSON - https://docs.suricata.io/
- **Fundamental:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Investigación / Deep Dive:** Elastic Security Labs higher-order detection rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection

Por qué:
- esta nota explica firmas, anomalías, comportamiento, enrichment, correlación y pipelines de respuesta sin reducir detection engineering a sintaxis de reglas

---

## zeek-suricata-and-netflow-analysis

Referencias preferidas:
- **Official Tool Docs:** Zeek logs reference - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Zeek capture loss logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Fundamental:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html

Por qué:
- esta nota compara reconstrucción de protocolo, telemetría de firmas y agregación de flow como capas de evidencia complementarias

---

## edr-network-observability-and-process-correlation

Referencias preferidas:
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
- **Fundamental:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Investigación / Deep Dive:** Elastic endpoint-to-environment investigation - https://www.elastic.co/security-labs/investigating-from-the-endpoint-across-your-environment

Por qué:
- esta nota posee el lado endpoint de observabilidad de red: linaje de procesos, ownership de sockets, contexto de usuario y dónde EDR difiere de sensores de paquetes

---

## windows-event-logs

Referencias preferidas:
- **Fundamental:** Microsoft Learn — Advanced security audit policy settings — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/advanced-security-audit-policy-settings
- **Fundamental:** Microsoft Learn — Events to Monitor — https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/appendix-l-events-to-monitor
- **Investigación / Deep Dive:** Sean Metcalf (ADSecurity.org) — Securing Domain Controllers / Windows audit guidance — https://adsecurity.org/?p=3299
- **Official Tool Docs:** Microsoft Sysinternals — Sysmon — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon

Por qué:
- esta nota posee la base de telemetría host-side Windows: el subset de ~30 Event IDs que impulsa detección, las precondiciones de audit-policy que hacen aparecer esos eventos y los patrones de secuencia Event-ID de ataques AD

---

## Próximas entradas sugeridas del registry

Agregá estas cuando la rama crezca:
- correlation-windows-and-entity-resolution
- tls-fingerprinting-for-detection
- tap-vs-span-sensor-placement
- cloud-flow-logs-and-network-detection
- detection-as-code-and-rule-lifecycle
- alert-triage-and-evidence-quality
- honeyports-and-tarpit-detection
- threat-hunting-with-zeek
- ioc-lifecycle-management
- living-off-the-land-detection
- ecs-and-otel-for-security-telemetry
- entity-resolution-for-detection
- beaconing-analysis
- attack-graph-detection
