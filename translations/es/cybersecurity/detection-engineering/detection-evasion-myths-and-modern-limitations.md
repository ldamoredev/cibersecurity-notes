# Detection Evasion Myths and Modern Limitations

## Definición

Los mitos de evasión de detección son afirmaciones sobresimplificadas que confunden evitar un sensor o una firma con volverse invisible para el sistema completo de telemetría.

## Por qué importa

La mayoría del folklore de evasión contiene una pequeña verdad y una falsedad peligrosa. Los scans lentos pueden saltear ventanas cortas, la fragmentación puede confundir inspección de paquetes débil, los decoys pueden ensuciar logs ingenuos, y el cifrado oculta payload. Nada de eso significa que la actividad sea invisible a través de EDR, telemetría de flow, Zeek, Suricata, logs cloud, logs de identidad, DNS, proxy logs y motores de correlación.

La ciberseguridad moderna es guerra de telemetría. La evasión debe evaluarse contra el sistema, no contra un detector.

## Cómo funciona

Cada afirmación de evasión debería testearse con **5 preguntas**:

1. **¿Qué sensor apunta a evadir?** IDS, EDR, AV, SIEM, logs cloud, WAF, DNS, proxy, flow o workflow del analista?
2. **¿Qué sigue observable?** Timing, proceso, usuario, destino, flow, parentage, DNS, TLS, API cloud, identidad o efectos laterales?
3. **¿Qué correlación la derrota?** Joins multisensor, ventanas largas, baselines por rol o detección de secuencia.
4. **¿Dónde sigue siendo útil?** Diagnóstico, controles débiles, sistemas legacy de nicho o reducción de una señal.
5. **¿Qué necesita hacer todavía el atacante?** Ejecutar, autenticarse, descubrir, persistir, moverse, recolectar o exfiltrar.

El mito falla cuando ignora la telemetría residual.

## Técnicas / patrones

- **Evasión específica de sensor.** Una técnica reduce visibilidad en un lugar pero deja evidencia en otro.
- **Desplazamiento de señal.** Desaparece el payload; metadata, proceso o identidad se vuelven más importantes.
- **Manipulación de tempo.** El comportamiento lento o con jitter intercambia visibilidad de tasa por ventanas de correlación más largas.
- **Ruido de atribución.** Decoys, proxies, NAT y egress cloud complican la identidad fuente pero no necesariamente el comportamiento.
- **Mezcla living-off-the-land.** Las herramientas legítimas reducen señal de artefacto, pero aumentan la dependencia en parentage, comando, objetivo y secuencia.

## Perspectiva del atacante

Los atacantes suelen optimizar contra el detector que conocen: una firma, una prueba de AV, una alerta IDS básica o una regla de SIEM de lab. Los entornos reales tienen sensores superpuestos y workflows humanos. Evitar una alerta todavía puede crear evidencia más rica en otro lado, especialmente cuando se unen logs de endpoint, red, identidad y cloud.

## Perspectiva del defensor

Los defensores deberían traducir cada afirmación de evasión en requisitos de telemetría residual. En vez de decir "la fragmentación no funciona", preguntá si los sensores reensamblan, si los fragmentos aparecen en weird logs, si flow todavía muestra fan-out y si la telemetría de procesos de endpoint identifica al scanner.

## Tradeoffs de detección e ingeniería

1. **Evitar un sensor vs evitar el sistema.**
   Muchas técnicas solo bypassean una capa de detección. La invisibilidad a nivel sistema es mucho más difícil.

2. **Reducción de ruido vs costo operacional.**
   El comportamiento lento o distribuido aumenta tiempo y coordinación del atacante mientras sigue dejando señales de ventana larga.

3. **Ofuscación de herramienta vs preservación de comportamiento.**
   Encoding, renombrado y ejecución fileless cambian artefactos, no objetivos.

4. **Cifrado vs metadata.**
   El payload está protegido; endpoints, timing, DNS, handshakes TLS y contexto de proceso pueden permanecer.

5. **Manipulación de logs vs ecología de logs.**
   Deshabilitar un log crea su propia señal y no borra trazas upstream, downstream, endpoint, cloud o identidad.

## Detección y defensa

Ordenado por efectividad:

1. **Mapeá telemetría residual por afirmación de evasión.**
   Para cada técnica, listá qué logs de paquete, flow, endpoint, identidad, cloud y aplicación todavía mostrarían algo.

2. **Correlacioná entre familias de sensores.**
   Fragmentación, decoys, cifrado y ofuscación se debilitan cuando se unen con datos de endpoint, flow, DNS, TLS e identidad.

3. **Medí salud y cobertura de sensores.**
   Muchos mitos se vuelven ciertos solo cuando reassembly, logging, cobertura EDR o enrichment están rotos.

4. **Testeá en lab con evidencia esperada.**
   Reproducí la técnica en un lab privado y registrá qué ve cada sensor.

5. **Enseñá explícitamente las verdades parciales.**
   Analistas y operadores toman mejores decisiones cuando saben qué puede hacer una técnica y qué no.

### Qué no funciona como defensa primaria

- **Desmentir como política.** Decir "eso no funciona" es más débil que medir qué ve tu entorno.
- **Confianza en una sola capa.** Un resultado limpio de IDS, AV o EDR no prueba invisibilidad.
- **Blocklists estáticas.** La evasión suele cambiar artefactos; la defensa durable necesita comportamiento y correlación.
- **Asumir que los defaults del vendor alcanzan.** Reassembly, logging, retención y enrichment deben configurarse y monitorearse.

## Mitos comunes

### Los scans lentos son invisibles

Parcialmente cierto: pueden evadir thresholds de tasa cortos. Falso: fan-out de ventana larga, puertos first-seen, roles de host inusuales y joins proceso-red todavía los revelan. Los defensores deberían medir destinos/puertos distintos en múltiples ventanas.

### La fragmentación bypassea IDS

Parcialmente cierto: la inspección de paquetes débil o mal configurada puede fallar. Falso: pipelines modernos tipo Zeek/Suricata pueden reensamblar o al menos loguear fragmentos anormales. Los defensores deberían testear reassembly y comportamiento de capture-loss.

### Los decoys derrotan la atribución

Parcialmente cierto: los logs ingenuos del objetivo muestran múltiples fuentes. Falso: timing, fingerprints TCP, solapamiento de destinos, distancia TTL y telemetría de endpoint pueden clusterizar comportamiento. Los defensores deberían clusterizar por comportamiento, no solo por IP fuente.

### Los encoders bypassean AV

Parcialmente cierto: las firmas simples pueden fallar. Falso: comportamiento decodificado, script block logs, inspección tipo AMSI, ancestry de procesos y efectos laterales de red/archivo permanecen. Los defensores deberían detectar cadenas de ejecución.

### Fileless significa indetectable

Parcialmente cierto: puede haber menos archivos para hash scanning. Falso: memoria, proceso, script, red, registry, WMI, identidad y telemetría de comandos pueden permanecer. Los defensores deberían monitorear comportamiento y paths de persistencia.

### Living off the land es invisible

Parcialmente cierto: los binarios legítimos reducen señal de artefacto malware. Falso: selección de objetivos, parentage, argumentos, frecuencia y contexto de identidad exponen abuso. Los defensores deberían baselinar comportamiento de herramientas por rol.

### La ofuscación de PowerShell derrota EDR

Parcialmente cierto: el string matching puede fallar. Falso: uso de encoded command, patrones de script block, procesos hijos, conexiones de red y padres inusuales permanecen visibles. Los defensores deberían evitar reglas solo por keywords.

### El cifrado oculta la actividad

Parcialmente cierto: el contenido queda oculto. Falso: metadata, DNS, fingerprints TLS, forma de flow y contexto de proceso de endpoint permanecen. Los defensores deberían unir flows cifrados a proceso e identidad.

### Deshabilitar logs borra trazas

Parcialmente cierto: puede perderse evidencia local. Falso: deshabilitar logs suele loguearse en otro lado y sistemas upstream/downstream todavía pueden registrar actividad. Los defensores deberían alertar sobre cambios de logging.

### El modo stealth de Nmap es stealthy en entornos modernos

Parcialmente cierto: los SYN scans evitan semántica local de TCP connect completo. Falso: firewalls stateful, IDS, flow logs y EDR todavía ven comportamiento de scan. Los defensores deberían detectar fan-out y actividad de proceso.

## Malentendidos operacionales

- **"Bypasseé una alerta" equivale a "bypasseé detección."** Normalmente significa que un detector falló.
- **"Sin archivo malware" equivale a "sin artefacto."** Comandos, memoria, logs, identidad y comportamiento de red son artefactos.
- **"Herramienta legítima" equivale a "comportamiento legítimo."** La legitimidad de la herramienta no valida la intención.
- **"La telemetría moderna es perfecta."** Tiene gaps, delays, puntos ciegos y límites de costo.

### Limitaciones modernas

- Los entornos mal instrumentados pueden hacer que los mitos sean más ciertos de lo que deberían.
- Restricciones de privacidad, costo y performance limitan logging full-fidelity.
- Los atacantes pueden combinar técnicas para reducir múltiples señales a la vez.
- La visibilidad cloud/SaaS depende de logs del proveedor y configuración.

### Puntos ciegos de telemetría

- Sin cobertura de endpoint en appliances o hosts no gestionados.
- Sin sensores east-west ni cloud flow logs.
- Script logging deshabilitado o falta de recolección de command line.
- Retención corta y cambios de logging no monitoreados.
- DNS cifrado y bypass de proxy.

## Labs prácticos

Usá hosts de lab propios o logs generados.

### Lab 1 - Comparar mitos contra telemetría residual

Objetivo: Construir una matriz de telemetría residual.

```
cat > /tmp/evasion-matrix.csv <<'EOF'
myth,targeted_sensor,residual_telemetry
slow scan,short rate rule,long-window fan-out; process-network join; first-seen ports
fragmentation,packet signature,fragment logs; reassembly; flow fan-out; endpoint process
decoys,source-IP log,TCP fingerprint; timing; target overlap; EDR on scanner
encryption,payload IDS,DNS; TLS metadata; flow shape; process context
fileless,file hash,process; command; memory; network; identity
EOF
column -t -s, /tmp/evasion-matrix.csv
```

Telemetría esperada: cada mito deja señales residuales. Limitación: el razonamiento de matriz debe validarse por entorno. Malentendido corregido: "la evasión es binaria."

### Lab 2 - Simular falla de threshold en scan lento

Objetivo: Mostrar por qué importan las ventanas largas.

```
cat > /tmp/slow.csv <<'EOF'
minute,dest
0,10.0.0.1
20,10.0.0.2
40,10.0.0.3
60,10.0.0.4
80,10.0.0.5
EOF
awk -F, 'NR>1 {count++} END {print "distinct_destinations_2h="count}' /tmp/slow.csv
```

Telemetría esperada: no existe un burst corto, pero la expansión de destinos en ventana larga permanece. Malentendido corregido: "baja tasa significa stealth."

## Ejemplos prácticos

- Una prueba de Nmap fragmentada no produce una firma IDS vieja pero igual aparece en Zeek weird logs y telemetría de proceso de endpoint.
- Un payload PowerShell fileless deja evidencia de script, padre, red e identidad.
- Un decoy scan confunde firewall logs pero no el clustering de fingerprint TCP.
- C2 cifrado evita firmas de payload pero produce forma de flow periódica y comportamiento raro proceso-red.

## Notas relacionadas

- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[encrypted-traffic-analysis-and-metadata-leakage|Análisis de tráfico cifrado y fuga de metadata]]
- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]

### Notas atómicas futuras sugeridas

- fileless-detection-models
- powershell-detection-tradeoffs
- decoy-scan-correlation
- log-tamper-detection

## Referencias

- **Official Tool Docs:** Nmap Firewall/IDS Evasion and Spoofing - https://nmap.org/book/man-bypass-firewalls-ids.html
- **Official Tool Docs:** Zeek Capture Loss and Reporter Logs - https://docs.zeek.org/en/current/logs/capture-loss-and-reporter.html
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
