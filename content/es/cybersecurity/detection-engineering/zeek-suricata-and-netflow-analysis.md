# Zeek, Suricata, and NetFlow Analysis

## Definición

Zeek, Suricata y NetFlow/IPFIX son capas complementarias de telemetría de red: Zeek reconstruye transacciones de protocolo, Suricata aplica reglas de detección y emite eventos de alerta/protocolo, y NetFlow/IPFIX resume patrones de comunicación a escala.

## Por qué importa

Muchos equipos dicen "tenemos monitoreo de red" sin saber qué capa de evidencia tienen realmente. Esa distinción decide qué pueden detectar. NetFlow puede mostrar un scan pero no los paths HTTP. Suricata puede alertar sobre una firma pero no preservar el historial completo de transacciones. Zeek puede reconstruir protocol logs ricos pero no tomar las mismas decisiones de alerting basado en reglas.

El modelo senior no es rivalidad de herramientas. Es composición de evidencia.

## Cómo funciona

Las tres capas responden **3 preguntas diferentes**:

1. **NetFlow/IPFIX:** ¿Quién habló con quién, cuándo, con qué frecuencia, por cuánto tiempo y cuánto?
2. **Zeek:** ¿Qué transacciones de protocolo ocurrieron, qué metadata fue visible y qué se vio raro?
3. **Suricata:** ¿Qué paquetes/streams/estados de protocolo matchearon lógica de detección y qué alerta o evento produjo el motor?

Ejemplo:

```
Observation: 10.0.5.20 probed 10.0.9.0/24 on 445/tcp.

NetFlow: one source, 254 destinations, low bytes, short duration.
Zeek conn.log: many failed TCP states and no valid SMB sessions.
Suricata eve.json: scan alerts and possible SMB probe signatures.
Conclusion: discovery behavior, not confirmed exploitation.
```

El bug es asumir que una capa puede responder las tres preguntas.

## Técnicas / patrones

- **Usá NetFlow para amplitud.** Detectar fan-out, conexiones largas, asimetría de bytes, periodicidad de beacon, puertos raros y movimiento a escala de entorno.
- **Usá Zeek para verdad transaccional.** Inspeccionar `conn.log`, `dns.log`, `http.log`, `ssl.log`, `ssh.log`, `files.log`, `weird.log` y `notice.log`.
- **Usá Suricata para firmas y contexto de alerta.** Revisar `eve.json` alert, flow, HTTP, DNS, TLS, file y anomaly records.
- **Uní con Community ID cuando sea posible.** Identificadores de flow compartidos ayudan a atar registros Zeek y Suricata del mismo flow.
- **Chequeá primero la calidad de captura.** Zeek `capture_loss.log`, stats de drops de Suricata, counters de interfaz y salud SPAN/TAP moldean toda conclusión.
- **Leé la ausencia con cuidado.** Sin alerta Suricata más logs de protocolo Zeek es distinto de no packets, sin soporte de parser, payload cifrado o pérdida de sensor.

## Variantes y bypasses

La comparación tiene **6 modos operativos**.

### 1. Monitoreo solo NetFlow

Útil para comportamiento high-level y retención a escala. Débil para payload, semántica de protocolo y atribución de proceso.

### 2. NSM solo Zeek

Fuerte para metadata de protocolo, weird behavior, scripting de policy local y pivots de analista. Débil cuando la pregunta es "¿matcheó esta firma de exploit conocida?"

### 3. IDS solo Suricata

Fuerte para lógica de detección conocida, workflows de alertas y firmas protocol-aware. Débil cuando no existe regla o cuando analistas necesitan historial transaccional más allá de la alerta.

### 4. Zeek más Suricata

El pairing clásico de NSM: Zeek explica qué pasó; Suricata marca formas sospechosas conocidas. Pcap y flow IDs compartidos lo vuelven potente.

### 5. Flow más endpoint

Común en cloud o redes de alta velocidad donde sensores de paquetes son limitados. Útil para comportamiento consciente de rol y correlación de procesos, pero más débil para root cause a nivel protocolo.

### 6. Replay offline de pcap

El modo de lab y regresión más seguro. Reproducí el mismo pcap por Zeek y Suricata para comparar evidencia, alertas, comportamiento de parser y cambios de reglas.

## Impacto

- **Profundidad de investigación.** Zeek puede reconstruir qué preguntó un scanner; Suricata puede mostrar qué regla disparó; NetFlow puede probar escala y timing.
- **Resiliencia de detección.** Si una capa pierde un evento, otra todavía puede preservar evidencia suficiente.
- **Control de costos.** Flow records retienen visibilidad amplia más tiempo; logs de paquete/protocolo dan profundidad donde hace falta.
- **Riesgo de mal uso de herramientas.** Tratar alertas Suricata como protocol logs o NetFlow como packet capture produce malas conclusiones.
- **Calidad operacional.** Capture loss y errores de parser pueden ser tan importantes como el comportamiento adversario.

## Detección y defensa

Ordenado por efectividad:

1. **Diseñá por pregunta de evidencia.**
   Decidí si necesitás escala, semántica de protocolo, firmas, payload o contexto de proceso. Después elegí la capa que puede responder.

2. **Corré Zeek y Suricata desde los mismos puntos de observación cuando sea viable.**
   Paquetes compartidos hacen que las contradicciones sean significativas. Ubicaciones distintas de sensores pueden explicar logs discrepantes.

3. **Correlacioná con flow IDs y timestamps.**
   Community ID, timestamps precisos y normalización consistente reducen joins manuales y falsos desacuerdos.

4. **Monitoreá salud de sensores como telemetría de seguridad.**
   Packet loss, drops del rule-engine, parser failures, presión de disco y queue overflow deberían crear alertas operacionales.

5. **Guardá muestras de paquetes para detecciones de alto valor.**
   La retención completa puede ser imposible, pero pcaps representativos alrededor de alertas mejoran regression testing y confianza del analista.

### Qué no funciona como defensa primaria

- **Elegir una herramienta como toda la estrategia.** Zeek, Suricata y NetFlow responden preguntas distintas.
- **Contar alertas como incidentes.** Los conteos de alertas Suricata miden actividad de reglas, no impacto de negocio.
- **Asumir que flow logs prueban seguridad de payload.** Flow records no pueden validar contenido de exploit.
- **Asumir que Zeek loguea toda aplicación.** Soporte de parser, cifrado, visibilidad y calidad de tráfico limitan la reconstrucción.
- **Ignorar capture loss.** La pérdida de paquetes cambia la confiabilidad de alertas y la reconstrucción de protocolo.

### Malentendidos operacionales

- **"Zeek reemplaza IDS."** Zeek puede detectar y emitir notices, pero su fuerza principal es telemetría NSM rica y policy programable.
- **"Suricata es solo firmas."** Suricata también produce protocol logs, flow records, file events, anomalías y metadata TLS.
- **"NetFlow tiene poco valor porque no tiene payload."** Flow suele ser la única forma escalable de detectar fan-out, beaconing y forma de exfil en ventanas largas.
- **"Offline replay prueba comportamiento de producción."** El replay prueba lógica del engine, no ubicación de sensores, packet loss ni efectos de timing en producción.

### Limitaciones modernas

- QUIC, TLS 1.3, ECH, DoH, service meshes y overlays cloud reducen visibilidad clásica de payload/protocolo.
- Links de alta velocidad pueden superar capacidad de sensores commodity.
- Entornos cloud pueden no permitir acceso tipo TAP a paquetes.
- Parsers de protocolo van detrás de protocolos nuevos y encodings propietarios.

### Puntos ciegos de telemetría

- Routing asimétrico donde el sensor ve solo una dirección.
- Sobresuscripción SPAN o mirror traffic droppeado.
- Protocolos cifrados sin metadata visible o proxy logs.
- Flow records sampleados que pierden conexiones cortas.
- Puntos de load balancer o NAT que ocultan identidad original del cliente.

## Labs prácticos

Usá replay offline de pcap para repetibilidad.

### Reproducir el mismo pcap de scan por Zeek y Suricata

```
mkdir -p zeek-out suricata-out
(cd zeek-out && zeek -r ../scan.pcap)
suricata -r scan.pcap -l suricata-out
ls zeek-out
jq 'select(.event_type=="alert") | .alert.signature' suricata-out/eve.json | sort | uniq -c
```

Telemetría esperada: Zeek produce transaction logs; Suricata produce alertas y eventos EVE. Compará qué explica cada capa.

### Usar Zeek para resumir estados de port scan

```
zeek-cut id.orig_h id.resp_h id.resp_p conn_state history < zeek-out/conn.log |
  awk '{k=$1" "$3" "$4; c[k]++} END {for (k in c) print c[k], k}' |
  sort -nr | head
```

Telemetría esperada: estados de conexión repetidos muestran forma de scan incluso sin alertas de payload.

### Inspeccionar metadata TLS de Suricata

```
jq 'select(.event_type=="tls") | {src:.src_ip,dst:.dest_ip,sni:.tls.sni,ja3:.tls.ja3,ja4:.tls.ja4}' \
  suricata-out/eve.json | head
```

Telemetría esperada: el tráfico cifrado todavía puede exponer metadata de handshake cuando está configurada y visible.

### Chequear capture loss antes de confiar en la ausencia

```
(cd zeek-out && zeek -r ../busy-link.pcap policy/misc/capture-loss)
cat zeek-out/capture_loss.log
```

Telemetría esperada: los registros de pérdida cambian la interpretación de alertas faltantes o sesiones de protocolo incompletas.

### Derivar una tabla tipo NetFlow desde Zeek

```
zeek-cut ts uid id.orig_h id.resp_h id.resp_p proto duration orig_bytes resp_bytes < zeek-out/conn.log |
  head -30
```

Telemetría esperada: los campos tipo flow son útiles para comportamiento amplio, mientras Zeek conserva contexto de protocolo adicional en logs separados.

## Ejemplos prácticos

- NetFlow muestra miles de intentos cortos a `3389/tcp`; Suricata no tiene alertas de exploit; Zeek confirma que no hubo sesiones RDP exitosas.
- Zeek `dns.log` muestra volumen de queries tipo DGA; reglas DNS de Suricata agregan matches known-bad para un subset.
- Suricata alerta sobre un patrón de exploit HTTP; Zeek `http.log` muestra método, host, URI, user agent y response code para triage.
- Zeek `weird.log` muestra comportamiento de protocolo malformado durante una prueba de decoy/fragmentación que un sistema puro de flow perdería.
- Flow logs muestran asimetría de bytes tipo exfil; Zeek `ssl.log` y telemetría de proceso EDR identifican el cliente y perfil TLS.

## Notas relacionadas

- [[index|Ingeniería de Detección]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[encrypted-traffic-analysis-and-metadata-leakage|Análisis de tráfico cifrado y fuga de metadata]]
- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[packet-analysis|Packet Analysis]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]

### Notas atómicas futuras sugeridas

- threat-hunting-with-zeek
- suricata-rule-tuning
- community-id-correlation
- sensor-health-and-capture-loss
- netflow-beaconing-analysis

## Referencias

- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Zeek Capture Loss Logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Fundamental:** RFC 7011 IPFIX - https://www.rfc-editor.org/rfc/rfc7011.html
