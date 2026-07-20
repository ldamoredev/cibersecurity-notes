# Network Telemetry Sources and Visibility

## Definición

La telemetría de red es la evidencia producida por puntos de observación que ven comunicación a través de una red: paquetes, flows, transacciones de protocolo, logs de dispositivos, cloud flow logs, proxy/WAF logs, DNS logs, metadata TLS y registros de salud de sensores.

## Por qué importa

La ciberseguridad moderna es guerra de telemetría. Un atacante no solo interactúa con un host; crea evidencia a través de routers, switches, firewalls, proxies, DNS resolvers, handshakes TLS, sockets de endpoint, control planes cloud y sistemas de identidad. Un defensor que entiende qué capa vio qué comportamiento puede reconstruir intención incluso cuando los payloads están cifrados o un sensor único perdió el evento.

El error senior es tratar "network logs" como una sola cosa. Un SPAN packet capture, un registro NetFlow, Zeek `conn.log`, una alerta Suricata, un cloud VPC flow log, un evento WAF y un evento de socket EDR describen proyecciones distintas del mismo comportamiento.

## Cómo funciona

La visibilidad de red es un **stack de evidencia de 6 capas**:

1. **Visibilidad de paquetes.** TAPs, SPAN ports, capturas de host y full-packet capture exponen headers y a veces payload. Es la mayor fidelidad y el mayor costo.
2. **Visibilidad de flow.** NetFlow/IPFIX/sFlow/cloud flow logs resumen quién habló con quién, cuándo, por cuánto tiempo y cuánto.
3. **Visibilidad de protocolo.** Zeek, Suricata, proxies, DNS servers y WAFs reconstruyen transacciones de application-layer cuando pueden parsear el protocolo.
4. **Visibilidad de control-plane.** Logs de firewall, load balancer, cloud security group, NAT gateway, route-table y proxy exponen decisiones de policy y cambios de path.
5. **Visibilidad de endpoint.** EDR y host logs conectan actividad de red con proceso, usuario, command line, padre, hash y sesión.
6. **Visibilidad de correlación.** SIEM/XDR/hunting platforms unen eventos por host, usuario, IP, proceso, flow ID, ventana temporal y contexto de asset.

Interpretación de ejemplo:

```
10.0.4.22 -> 10.0.9.14:445 over 2 minutes

Flow log: 900 short TCP attempts, mostly no bytes returned.
Zeek: many failed conn states, no SMB transactions.
Suricata: scan/fan-out alerts.
EDR: powershell.exe launched nmap.exe from a temp directory.
Cloud log: source host is a newly created workload in a dev subnet.
```

La detección no vive en un log. Vive en la relación entre timing, comportamiento de puerto, ancestry de proceso, rol del host y path de red.

## Técnicas / patrones

- **Mapeo de visibilidad.** Para cada pregunta de seguridad, escribí los campos requeridos: fuente, destino, puerto, protocolo, usuario, proceso, hostname, nombre DNS, SNI, JA3/JA4, bytes, paquetes, verdict, action, salud del sensor.
- **Razonamiento de punto de observación.** Preguntá dónde está el sensor respecto de NAT, load balancers, TLS termination, proxies, cambios de routing y overlays cloud.
- **Pivot packet-to-flow-to-process.** Empezá amplio con flow, profundizá con Zeek/Suricata/pcap y después uní con EDR donde exista cobertura de endpoint.
- **Chequeos de salud de sensores.** Tratá packet loss, eventos droppeados, delays de ingestión, clock skew y errores de parser como datos de detección first-class.
- **Comparación de puntos de vista.** Compará telemetría pública, VPN, interna, VPC, container y endpoint-local porque la reachability depende del path.

## Variantes y bypasses

La visibilidad de red tiene **7 familias prácticas de telemetría**.

### 1. Full packet capture

Full packet capture da la evidencia más reproducible, pero es caro, sensible a privacidad, pesado en storage y muchas veces imposible a escala cloud. TLS oculta payload salvo que existan claves de terminación o proxy logs descifrados.

### 2. Feeds SPAN y TAP

Los TAPs son preferibles para monitoreo fijo de alta fidelidad, mientras SPAN es común para monitoreo flexible. SPAN puede estar sobresuscripto, ser direccional, modificado por comportamiento del switch o mal configurado, así que las capturas SPAN son una vista, no ground truth.

### 3. Registros de flow

NetFlow/IPFIX/cloud flow logs escalan bien y detectan fan-out, beaconing, sesiones largas y patrones volumétricos. Normalmente carecen de payload, proceso, hostname, URI y secuencias exactas de TCP flags.

### 4. Protocol transaction logs

Zeek, proxies, DNS logs y WAF logs exponen significado de protocolo parseado: DNS queries, métodos HTTP, metadata TLS, archivos, certificados, user agents y parser weirdness. Dependen de visibilidad, soporte de parser y tráfico suficientemente limpio.

### 5. Streams de alertas IDS/IPS

Motores tipo Suricata/Snort convierten paquetes y streams en matches de reglas. Son de alto valor cuando están tuneados y contextualizados, pero una alerta es un claim del sensor, no una investigación completa.

### 6. Telemetría de red de endpoint

EDR ve comportamiento de red propiedad de procesos desde la perspectiva del host. Puede observar tráfico que sensores perimetrales pierden, pero suele carecer de detalle de paquete y puede estar ausente en appliances, hosts no gestionados, containers y workloads de corta vida.

### 7. Telemetría cloud-native

Cloud flow logs, load-balancer logs, DNS resolver logs, firewall logs, NAT gateway logs y eventos de control-plane exponen paths que sensores físicos no pueden ver. Son agregados, específicos de proveedor y muchas veces demorados.

## Impacto

- **Cobertura de detección.** La selección de telemetría determina qué ataques son detectables antes de escribir cualquier regla.
- **Calidad de triage.** Contexto rico acorta investigaciones; contexto débil crea dead ends por IP-only o alert-only.
- **Falsos negativos.** Sensores faltantes, flow sampleado, pérdida SPAN, routing asimétrico, payloads cifrados y endpoints no gestionados crean puntos ciegos.
- **Falsos positivos.** Telemetría sin rol de asset, ventanas de cambio, contexto de usuario y baselines hace que operaciones normales parezcan maliciosas.
- **Presión de costo y retención.** Los logs de alta fidelidad cuestan. Los programas de detección deben decidir qué mantener hot, warm, resumido o descartado.

## Detección y defensa

Ordenado por efectividad:

1. **Ingenierizá telemetría desde preguntas, no desde herramientas.**
   Empezá con el comportamiento que necesitás probar o refutar, después listá campos y puntos de observación. Esto evita que "compramos un sensor" se vuelva una estrategia falsa de visibilidad.

2. **Ubicá sensores en transiciones de trust boundary.**
   Monitoreá donde el tráfico cambia de significado: borde internet, ingreso VPN, choke points east-west, límites de identidad, TLS termination, NAT cloud, service mesh y subnets admin privilegiadas.

3. **Correlacioná entre paquete, flow, protocolo, endpoint y cloud.**
   Las detecciones single-source fallan bajo condiciones modernas. La correlación permite que flow fan-out se vuelva un incidente respaldado por proceso en vez de una estadística de IP anónima.

4. **Validá continuamente la salud de sensores.**
   Capture loss, queue drops, ingestion lag, parser failures, clock drift y normalización rota deberían alertar. Un sensor silencioso es una interrupción de detección.

5. **Usá tiers de retención deliberadamente.**
   Conservá metadata de alto valor más tiempo que raw payloads. Guardá suficiente detalle para reconstruir incidentes: timestamps, 5-tuples, dirección, acción, asset, proceso, usuario y parse status.

### Qué no funciona como defensa primaria

- **Comprar un SIEM sin diseño de telemetría.** Un SIEM solo correlaciona lo que existe, llega a tiempo y tiene campos usables.
- **Depender solo de packet capture.** Los paquetes carecen de identidad, ancestry de proceso, contexto cloud y larga retención en muchos entornos.
- **Depender solo de NetFlow.** Flow ve patrones pero normalmente no puede explicar contenido de protocolo, causa de proceso ni payload de exploit.
- **Asumir que cifrado significa invisibilidad.** El payload queda oculto, pero timing, endpoints, DNS, metadata de handshake TLS, tamaño de flow y contexto de proceso de endpoint suelen permanecer.
- **Tratar capturas SPAN como verdad perfecta.** SPAN puede dropear, duplicar, modificar u omitir tráfico según dirección y oversubscription.

### Malentendidos operacionales

- **"Los scans lentos son stealthy."** Los scans lentos reducen alertas simples por tasa pero todavía crean contacto raro con servicios, joins proceso-red, fan-out de ventana larga, metadata DNS/TLS y comportamiento first-seen.
- **"Cloud significa sin monitoreo de red."** Cloud cambia los puntos de recolección: flow logs, load balancer logs, DNS resolver logs, NAT logs, service meshes y sensores endpoint reemplazan TAPs físicos.
- **"Más logs significa mejor detección."** Más datos no accionables aumentan costo y carga del analista salvo que los campos soporten triage.

### Limitaciones modernas

- TLS 1.3, QUIC, ECH, DNS-over-HTTPS, mobile apps, cloud NAT, service meshes y workloads efímeros reducen visibilidad clásica de payload.
- La identidad de asset cambia más rápido que la identidad IP en cloud y containers.
- Los schemas de vendors cambian; las detecciones necesitan regression tests y monitoreo de calidad de campos.

### Puntos ciegos de telemetría

- Tráfico east-west dentro de redes planas sin choke point.
- Tráfico host-local, loopback, container bridge y comportamiento de service-mesh sidecar.
- Endpoints no gestionados, appliances, dispositivos de red, IoT y SaaS de terceros.
- Flow records sampleados, conexiones de corta vida y beaconing de bajo volumen.
- Gaps SPAN/TAP, routing asimétrico, packet loss y clock skew.

## Labs prácticos

Corré solo en labs locales propios, cuentas cloud privadas, rangos tipo HTB/THM o contenedores aislados.

### Comparar vistas de paquete, flow y protocolo

```
# Terminal 1: capture packets on a lab host
sudo tcpdump -i any -w scan.pcap 'host 10.10.10.10'

# Terminal 2: generate a small authorized scan
nmap -Pn -sS -p 22,80,443,445 10.10.10.10

# Terminal 3: derive Zeek logs from the same pcap
mkdir -p zeek-out && cd zeek-out
zeek -r ../scan.pcap
cat conn.log
```

Telemetría esperada: tcpdump muestra paquetes y flags; Zeek `conn.log` resume conexiones y estados TCP; ninguna vista incluye process ancestry salvo que se agregue telemetría de endpoint.

### Observar pérdida estilo SPAN/TAP como variable de detección

```
# Use a lab pcap or safe capture feed.
zeek -r busy-link.pcap policy/misc/capture-loss
cat capture_loss.log
```

Telemetría esperada: `capture_loss.log` reporta evidencia de pérdida. La lección defensiva es que alertas faltantes durante ventanas de pérdida no pueden interpretarse como tráfico limpio.

### Construir una tabla de scan con forma de flow desde Zeek

```
zeek -r scan.pcap
zeek-cut id.orig_h id.resp_h id.resp_p proto conn_state duration orig_pkts resp_pkts < conn.log |
  sort | head -50
```

Telemetría esperada: el comportamiento de scan aparece como muchas conexiones cortas con fuente repetida, expansión de destinos, estados inusuales y bajo payload de respuesta.

### Comparar punto de vista público e interno

```
# From a public-controlled host
nmap -Pn --top-ports 100 LAB_PUBLIC_IP

# From an internal lab subnet
nmap -Pn --top-ports 100 LAB_PRIVATE_IP
```

Telemetría esperada: la diferencia entre outputs es la historia de límite. Los defensores deberían comparar logs de edge devices, sensores internos y eventos de endpoint para la misma ventana temporal.

### Testear visibilidad de metadata cifrada

```
openssl s_client -connect example.com:443 -servername example.com -alpn h2 </dev/null 2>/dev/null |
  sed -n '1,30p'
```

Telemetría esperada: el payload está cifrado, pero SNI, detalles del certificado, protocolo negociado, destino, timing y conteos de bytes todavía pueden ser útiles según ubicación del sensor.

## Ejemplos prácticos

- Un sensor perimetral ve fan-out SYN tipo Masscan; EDR muestra que se originó en `masscan` lanzado por un script temporal en una workstation dev.
- Cloud VPC flow logs muestran un workload nuevo contactando cientos de destinos internos `445/tcp`; Zeek está ciego porque no existe sensor dentro de esa subnet.
- Un WAF loguea enumeración de URI, pero NetFlow muestra que el mismo cliente también probaba SSH y RDP en hosts adyacentes.
- Zeek `ssl.log` ve un perfil TLS first-seen tipo JA4 desde una subnet de base de datos que solo debería correr servicios Java.
- Una revisión de incidente no encuentra alerta Suricata durante una ventana de exploit, pero `capture_loss.log` muestra pérdida de sensor por encima del threshold.

## Notas relacionadas

- [[index|Ingeniería de Detección]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[encrypted-traffic-analysis-and-metadata-leakage|Análisis de tráfico cifrado y fuga de metadata]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[packet-analysis|Packet Analysis]]
- [[firewalls-and-network-boundaries|Firewalls and Network Boundaries]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[active-recon|Active Recon]]
- [[run-scan-pipeline|Ejecutar pipeline de scan externo de recon]]

### Notas atómicas futuras sugeridas

- tap-vs-span-sensor-placement
- cloud-flow-logs-and-network-detection
- telemetry-retention-tiers
- sensor-health-and-capture-loss
- encrypted-traffic-metadata

## Referencias

- **Fundamental:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Cisco SPAN Configuration Guide - https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/mgmt/management-configuration-guide/span.html
- **Mitigación / Operaciones:** CISA Best Practices for Event Logging and Threat Detection - https://www.cisa.gov/resources-tools/resources/best-practices-event-logging-and-threat-detection
