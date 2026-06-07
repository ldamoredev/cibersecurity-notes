# IDS/IPS and Behavioral Detection Pipelines

## Definición

Un pipeline de IDS/IPS y detección de comportamiento es el camino ingenierizado desde la recolección de telemetría hasta lógica analítica, enrichment, correlación, alerting, triage, respuesta, supresión, tuning y retención de evidencia.

## Por qué importa

Detection engineering no es "escribí una regla y esperá". Una firma puede matchear un paquete, pero un incidente requiere contexto: rol del asset, usuario, proceso, ventana temporal, historial de cambios, threat model, alertas relacionadas y qué acción de respuesta es segura.

La detección moderna es comportamental y correlacional. El pensamiento IDS legacy suele detenerse en firmas de payload. Detection engineering senior pregunta qué comportamiento debería ser observable, qué fuente de datos lo prueba, qué campos se necesitan para triage, qué ventana de correlación es válida y cómo va a fallar la regla.

## Cómo funciona

Un pipeline de detección tiene **8 etapas**:

1. **Recolección.** Los sensores recolectan eventos de paquetes, flow, endpoint, identidad, aplicación, cloud y control-plane.
2. **Normalización.** Campos crudos se vuelven un schema común: host, usuario, IP, puerto, proceso, acción, outcome, timestamp, tipo de evento.
3. **Enrichment.** Se agregan rol del asset, owner, criticidad, geolocalización, reputación, vulnerabilidad, identidad y contexto de cambio.
4. **Detección atómica.** Las reglas identifican un comportamiento: scan fan-out, proceso sospechoso, firma malware, impossible travel, nueva acción admin.
5. **Correlación.** Múltiples señales se agrupan por host, usuario, IP, proceso, sesión, flow ID o ventana temporal.
6. **Priorización.** Severidad, novedad, criticidad de asset, confianza y blast radius determinan posición en la cola.
7. **Respuesta.** Las alertas disparan investigación de analista, contención automática, ticketing o supresión.
8. **Feedback.** Falsos positivos, ataques perdidos, notas de analistas y cambios del entorno actualizan la regla y el modelo de telemetría.

Ejemplo:

```
Suricata alert: ET SCAN Nmap Scripting Engine User-Agent
Zeek: HTTP path enumeration and TLS metadata from same source
EDR: nmap.exe launched by powershell.exe under a non-admin user
Asset context: source is a production app server, not a scanner
Higher-order rule: discovery + abnormal process + high-value destination set
```

La detección útil es el comportamiento correlacionado, no el string único de alerta.

## Técnicas / patrones

- **Detección por firmas.** Matchear patrones conocidos de paquete, protocolo, archivo, comando o comportamiento. Fuerte para known-bad y violaciones de policy; débil contra variaciones desconocidas.
- **Detección de anomalías.** Comparar comportamiento contra baselines: destino first-seen, puerto inusual, parent-child process raro, ratio de bytes anormal, país nuevo, secuencia rara de API cloud.
- **Detección de comportamiento.** Detectar comportamiento tipo técnica independiente del IOC exacto: port fan-out, credential spraying, process injection, cifrado masivo de archivos, data staging.
- **Detección higher-order.** Usar alertas y eventos de bajo nivel como inputs para correlacionar a través de tiempo, entidades y fuentes de datos.
- **Resolución de entidades.** Normalizar hostnames, IPs, cloud instance IDs, usuarios, service accounts, process IDs y containers para que los joins signifiquen lo que dicen.
- **Disciplina detection-as-code.** Guardar reglas con propósito, requisitos de datos, eventos de prueba, notas de falsos positivos, mapeo ATT&CK, plan de rollback y owner.

## Variantes y bypasses

Los pipelines fallan de **7 maneras comunes**.

### 1. Falla signature-only

El atacante cambia payload, user agent, path, librería TLS o sintaxis de comando. Una regla de firma pierde el evento mientras el comportamiento sigue siendo obvio en la telemetría.

### 2. Falla threshold-only

Un scan lento, login spray distribuido o beacon de bajo volumen queda debajo de un threshold fijo. Se necesitan analíticas de ventana larga y novedad por entidad.

### 3. Falla de enrichment

Una alerta sobre `10.0.3.22` tiene bajo valor hasta que el sistema sabe si es domain controller, scanner, laptop dev, container efímero o NAT gateway.

### 4. Falla de resolución de entidades

Las IPs se mueven, hosts cambian de nombre, instancias cloud se reciclan, NAT oculta clientes y usernames colisionan. Malos joins crean incidentes falsos o incidentes perdidos.

### 5. Falla de ventana de correlación

Ventanas demasiado cortas pierden comportamiento lento. Ventanas demasiado largas cosen eventos no relacionados.

### 6. Falla de modo de respuesta

Las alertas IDS son más seguras para tunear de forma laxa; los drops IPS requieren change control, pueden romper producción y necesitan cobertura de tests. Detección y prevención no son el mismo riesgo.

### 7. Falla de feedback

Las reglas que nunca reciben labels de falsos positivos, outcomes de incidentes o cambios del entorno se pudren hasta volverse ruido.

## Impacto

- **Detección más temprana de attack chain.** La correlación captura discovery, staging, uso de credenciales, movimiento lateral y explotación como secuencia.
- **Mejor triage.** Los analistas reciben evidence cards en vez de strings de alerta aislados.
- **Menor carga de analista.** Reglas higher-order suprimen o depriorizan ruido atómico de bajo valor mientras elevan comportamiento multi-señal.
- **Riesgo de control.** Modo IPS puede prevenir ataques pero también dropear tráfico de negocio si la lógica de detección es frágil.
- **Realismo de cobertura.** Los mapeos ATT&CK solo son útiles cuando están atados a telemetría real y calidad de campos.

## Detección y defensa

Ordenado por efectividad:

1. **Definí la hipótesis de detección antes de escribir lógica.**
   Declarar comportamiento, fuentes de datos requeridas, campos esperados, falsos positivos conocidos y preguntas de triage. Una regla sin hipótesis se vuelve deuda de mantenimiento.

2. **Separá detecciones atómicas de detecciones de correlación.**
   Las reglas atómicas deberían ser simples y explicables. Las higher-order deberían combinar señales para subir confianza, no esconder mala lógica base.

3. **Ingenierizá evidencia de triage dentro de las alertas.**
   Incluí proceso, padre, usuario, rol de host, destino, protocolo, alertas recientes relacionadas, estado first-seen y confianza del sensor. El analista debería saber por qué importa el evento.

4. **Tuneá por rol de entidad y entorno.**
   Subnets scanner, CI runners, domain controllers, laptops dev, servidores de producción y workloads cloud necesitan baselines y allowlists distintas.

5. **Testeá falsos positivos y falsos negativos.**
   Reproducí pcaps, corré labs locales, simulá comportamiento admin benigno y compará alertas esperadas. Una detección debería tener regression tests cuando sea posible.

### Qué no funciona como defensa primaria

- **Volumen de reglas.** Miles de reglas sin contexto crean deuda de alertas, no cobertura.
- **Heatmaps ATT&CK solos.** Claims de cobertura de técnicas no prueban recolección, calidad de campos, valor de triage ni baja tasa de falsos positivos.
- **AI triage sin calidad de telemetría.** El razonamiento del modelo no puede recuperar campos que nunca se recolectaron o joins equivocados.
- **IPS como sustituto de arquitectura.** Bloquear firmas no arregla servicios sobreexpuestos, identidad débil ni segmentación faltante.
- **Supresiones permanentes.** Las supresiones deberían expirar o estar atadas a owners; si no, se vuelven puntos ciegos.

### Malentendidos operacionales

- **"Las alertas son detecciones."** Las alertas son salidas. Las detecciones incluyen supuestos de telemetría, lógica, triage, respuesta y feedback.
- **"Anomalía equivale a malicioso."** Lo nuevo puede ser deploy, failover, patching, testing o logging roto.
- **"La detección comportamental no tiene firmas."** Las reglas comportamentales también codifican patrones; simplemente están en un nivel más alto que byte strings.
- **"La correlación siempre mejora fidelidad."** La correlación amplifica señal y ruido. Eventos base malos crean incidentes malos con apariencia confiada.

### Limitaciones modernas

- El tráfico cifrado reduce firmas de payload y desplaza valor hacia metadata, endpoint y proxy logs.
- Logs cloud y SaaS llegan con delay, se normalizan distinto y suelen ser caros a full fidelity.
- La telemetría de endpoint puede ser manipulada o estar ausente en assets no gestionados.
- Los atacantes se mezclan cada vez más con herramientas de administración, sistemas CI/CD, APIs cloud y plataformas legítimas de remote-management.

### Puntos ciegos de telemetría

- Command-line arguments no recolectados, campos truncados, datos de proceso padre faltantes o DNS/TLS logging deshabilitado.
- NAT gateways, proxies y load balancers que colapsan muchos usuarios en una identidad de red.
- Sensores con clock drift, ingestion lag, errores de parser o packet loss.
- Plataformas SaaS con APIs de auditoría limitadas o retención corta.

## Labs prácticos

Usá tráfico de lab aislado y stacks SIEM/hunting locales.

### Construir una alerta base de scan y una alerta de correlación

```
# Generate a vertical scan in a lab.
nmap -Pn -p 1-1000 LAB_HOST

# Then add service enumeration.
nmap -Pn -sV --script "default,safe" -p 80,443 LAB_HOST
```

Telemetría esperada: las reglas base deberían capturar comportamiento de scan; una regla de correlación debería elevar "scan más version/script probing" por encima de un scan solo.

### Reproducir un pcap por Suricata

```
suricata -r scan.pcap -l suricata-out
jq 'select(.event_type=="alert") | {ts:.timestamp, sig:.alert.signature, src:.src_ip, dest:.dest_ip}' suricata-out/eve.json
```

Telemetría esperada: las alertas son matches de reglas. Compará con registros Zeek/flow para identificar qué no explicó la regla.

### Crear una query de fan-out en ventana larga

```
Group by source host over 24h:
- count distinct destination IPs
- count distinct destination ports
- count failed connection states
- count first-seen destination-port pairs
Alert when role != scanner and novelty + fan-out exceed baseline.
```

Telemetría esperada: captura scans lentos que ventanas cortas de tasa pierden. Supuestos falsos: "baja tasa significa benigno" y "un threshold sirve para todos los hosts."

### Testear sensibilidad de ventana de correlación

```
for p in 22 80 443 445 3389; do
  nmap -Pn -p "$p" LAB_HOST
  sleep 300
done
```

Telemetría esperada: una ventana de 5 minutos pierde el patrón; una ventana de 24 horas consciente de rol ve expansión inusual de puertos. Las ventanas largas necesitan contexto de asset para evitar ruido.

### Comparar riesgo IDS e IPS

```
# Offline only: inspect what would have alerted before considering blocking.
suricata -r production-like-sample.pcap -k none -l ids-test
jq 'select(.event_type=="alert") | .alert.signature' ids-test/eve.json | sort | uniq -c
```

Telemetría esperada: el testing IDS revela drops candidatos sin afectar tráfico. La lección defensiva: la lógica de prevención necesita testing más estricto que la lógica de alerta.

## Ejemplos prácticos

- Una firma Suricata de scan es baja prioridad desde una subnet scanner conocida pero alta prioridad desde un servidor de base de datos.
- Una alerta de "nuevo fingerprint TLS saliente" es ruidosa globalmente pero de alto valor para un rol de domain controller.
- Tres alertas de baja severidad en un host se vuelven un incidente high-priority porque comparten process ancestry y ocurren dentro de una ventana válida de attack-chain.
- Una regla NSE ruidosa se baja de prioridad salvo que esté seguida por requests de exploit-path o intentos de credenciales.
- El flow fan-out de un workload cloud se suprime durante una ventana de despliegue aprobada, pero no después de cerrar el change ticket.

## Notas relacionadas

- [[index|Ingeniería de Detección]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[false-positives-false-negatives-and-detection-tradeoffs|Falsos positivos, falsos negativos y tradeoffs de detección]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths y observabilidad de kill chain]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[bot-detection-signals|Bot Detection Signals]]

### Notas atómicas futuras sugeridas

- correlation-windows-and-entity-resolution
- detection-as-code-and-rule-lifecycle
- alert-triage-and-evidence-quality
- detection-coverage-vs-attack-coverage
- suppression-debt

## Referencias

- **Official Tool Docs:** Suricata Documentation - https://docs.suricata.io/
- **Fundamental:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Investigación / Deep Dive:** Elastic Higher-Order Detection Rules - https://www.elastic.co/security-labs/higher-order-detection-rules
- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
