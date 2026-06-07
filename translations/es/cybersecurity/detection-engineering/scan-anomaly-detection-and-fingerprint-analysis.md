# Scan Anomaly Detection and Fingerprint Analysis

## Definición

La detección de anomalías de scan es la identificación de comportamiento de reconnaissance a partir de timing, fan-out, distribución de puertos, features TCP/IP, probes de protocolo, fingerprints TLS, contexto de endpoint y transiciones desde discovery hacia service enumeration o explotación.

## Por qué importa

El scanning es uno de los ejemplos más claros de guerra de telemetría. El atacante piensa en objetivos, puertos, timing templates, motores de scan y categorías NSE. El defensor ve tasas de paquetes, estados de conexión fallida, entropía de puertos, fan-out de destino, joins proceso-red, handshakes TLS, DNS, flow records y ventanas de correlación.

La cultura ofensiva legacy suele romantizar los "stealth scans". La defensa moderna cambió la ecuación. Scans lentos o fragmentados pueden bypassear un threshold ingenuo, pero igual crean evidencia comportamental en NetFlow, Zeek, Suricata, EDR, logs cloud, fingerprints de protocolo y analíticas first-seen.

## Cómo funciona

La detección de scans responde **6 preguntas comportamentales**:

1. **Fan-out:** ¿Una fuente contacta muchos destinos, muchos puertos o ambos?
2. **Entropía de puertos:** ¿La secuencia de puertos es estrecha y repetida, aparentemente aleatoria, full-range o enfocada por clase de servicio?
3. **Timing:** ¿Los probes son bursty, randomizados, periódicos o distribuidos en una ventana larga?
4. **Forma TCP/IP:** ¿Flags, options, window size, TTL, fragmentación, retransmisiones y reset behavior se parecen a un stack scanner?
5. **Profundidad de protocolo:** ¿El actor frenó en SYNs, hizo version detection, corrió probes tipo NSE, fetcheó paths HTTP o intentó autenticación?
6. **Correlación:** ¿Qué proceso, usuario, rol de asset, workload cloud, identidad e historial previo de alertas explican el comportamiento de red?

Ejemplo:

```
Masscan-like: one source -> thousands of destinations on 443/tcp in seconds.
RustScan-like: one source -> one host, many ports, high concurrency, then Nmap probes.
Nmap NSE-like: few ports, many protocol-specific requests, distinctive HTTP/TLS/SMB script behavior.
Slow scan: low rate, long window, but first-seen contact to unusual ports across many assets.
```

La detección no es "se usó Nmap". La detección es "esta entidad realizó comunicación inconsistente con su rol, con una forma y secuencia consistente con discovery."

## Técnicas / patrones

- **Scanning horizontal.** Uno o pocos puertos en muchos hosts. Ejemplo: `443/tcp` en un /16. La telemetría de flow ve fan-out claramente.
- **Scanning vertical.** Muchos puertos en uno o pocos hosts. Ejemplo: full-range `-p-` contra un servidor. Importan patrones de endpoint y estados Zeek.
- **Block scanning.** Muchos hosts y muchos puertos, muchas veces randomizados. Herramientas tipo Masscan y ZMap viven acá.
- **Análisis de entropía de scan.** Medir conteo de destinos, conteo de puertos, diversidad de clases de servicio, distribución inter-arrival y novedad contra el rol del host fuente.
- **Fingerprints de timing.** Tamaño de burst, gaps entre paquetes, retries, patrones scan-delay y rate ceilings revelan comportamiento de herramienta incluso cuando cambia la IP fuente.
- **Fingerprinting TCP/IP.** Window size, orden de options, MSS, distancia TTL, comportamiento de secuencia inicial, fragmentación y checksum pueden clusterizar decoys o stacks custom.
- **Fingerprinting TLS.** Metadata tipo JA3/JA4 puede distinguir librerías de scanner, runtimes de scripting y clientes no-browser incluso cuando el payload HTTP está cifrado.
- **Transición scan-a-exploit.** Una fuente que scanea `80/443`, corre enumeración HTTP y después postea payloads con forma de exploit cruzó de discovery a testing.

## Variantes y bypasses

El comportamiento de scan tiene **8 familias relevantes para detección**.

### 1. Fast SYN fan-out

Comportamiento tipo Masscan envía SYNs de alta tasa con estado mínimo. Es visible en flow records, edge devices, Zeek `conn.log`, reglas Suricata y counters de router mucho antes de que importe el análisis de payload.

### 2. Full-range single-host scans

Scans full-range de RustScan/Nmap crean alta entropía de puertos contra un host. La vista de red es vertical; la vista de endpoint puede mostrar un proceso scanner abriendo muchos sockets rápido.

### 3. Enumeración Nmap service-aware

`-sV`, `-sC` y NSE scripts producen menos conexiones pero transacciones de protocolo más distintivas. Acá las firmas HTTP/SMB/TLS de Suricata y logs de protocolo Zeek son más útiles que conteos puros de flow.

### 4. Scans lentos

Los scans lentos bajan thresholds por minuto pero ensanchan la ventana del defensor. Motores de correlación pueden agregar puertos first-seen y expansión de hosts durante horas o días, especialmente unidos a proceso y rol de asset.

### 5. Scans fragmentados y con decoys

Fragmentación y decoys apuntan a supuestos viejos de paquetes o source-IP. Defensas modernas reensamblan fragmentos y clusterizan por comportamiento, fingerprint TCP, solapamiento de destinos y timing.

### 6. Scans distribuidos

Botnets, cuentas cloud, proxies y hosts comprometidos distribuyen IPs fuente. La detección se desplaza hacia agregación centrada en destino, fingerprints compartidos, timing común, secuencia URI/probe y enrichment de threat intel.

### 7. Scans con fingerprints TLS/aplicación

Scanners que prueban HTTPS exponen forma de ClientHello, ALPN, comportamiento SNI, patrones de validación de certificados, user agents y secuencias método/path HTTP incluso sin payload descifrado.

### 8. Discovery interno autenticado

EDR y logs de identidad importan más cuando el scanning ocurre después de foothold. `net.exe`, PowerShell, `nmap`, `ldapsearch`, enumeración SMB y llamadas de inventario de API cloud crean evidencia de proceso e identidad.

## Impacto

- **Alerta temprana.** Scanning puede exponer preparación de ataque antes de que empiece la explotación.
- **Validación de assets.** La telemetría de scan revela servicios inesperados y fallas de límites aunque el scanner sea benigno.
- **Presión de ruido.** El scanning de fondo de internet es constante; las detecciones necesitan criticidad de asset, novedad y lógica de transición.
- **Costo adversario.** La correlación obliga a los atacantes a gestionar identidad de proceso, timing, forma TLS, reputación de fuente y secuencia de objetivos, no solo paquetes.
- **Riesgo de falsa confianza.** La falta de alertas de scan no prueba ausencia de scanning; puntos ciegos y thresholds pueden ocultarlo.

## Detección y defensa

Ordenado por efectividad:

1. **Modelá rol de fuente y destino.**
   Un vulnerability scanner, domain controller, CI runner, laptop dev y host de base de datos deberían tener distinto comportamiento de discovery permitido. Baselines por rol superan thresholds globales.

2. **Detectá fan-out y entropía en múltiples ventanas.**
   Usá ventanas cortas para bursts tipo Masscan y ventanas largas para scans lentos. Rastreá hosts destino distintos, puertos distintos, clases de puertos, estados fallidos y combinaciones first-seen.

3. **Correlacioná scan con proceso, usuario y contexto de cambio.**
   Los scans autorizados deberían mapear a assets scanner conocidos, jobs programados, tickets y herramientas esperadas. Comportamiento de scan desconocido desde `powershell`, `python`, `curl` o binarios renombrados merece prioridad.

4. **Usá pivots de protocolo y fingerprint.**
   JA3/JA4, HTTP user-agent, TLS ALPN, inferencia de servicio de Zeek, alertas app-layer de Suricata y fingerprints TCP agregan identidad más allá de IP fuente.

5. **Detectá transición, no solo discovery.**
   Priorizá fuentes que scanean, enumeran versiones, fetchean risky paths, intentan credenciales, explotan un path CVE o tocan servicios de alto valor después del discovery.

### Qué no funciona como defensa primaria

- **Bloquear una IP scanner después de detectarla.** Los scanners rápidos terminan antes de que el bloqueo reactivo importe; la defensa durable necesita reducción de exposición y detección comportamental.
- **Asumir que los scans lentos son invisibles.** Cambian visibilidad de tasa por novedad de ventana larga, mismatch de rol y evidencia de correlación.
- **Asumir que fragmentación y decoys derrotan sensores modernos.** Reassembly, clustering de comportamiento, fingerprints TCP y joins EDR debilitan estos trucos legacy.
- **Depender solo de supresión de banners.** Reduce una señal de enumeración pero no elimina puerto, timing, TLS, DNS ni evidencia de proceso.
- **Tratar alertas de scan como el problema raíz.** El problema raíz suele ser servicios alcanzables inesperados, límites débiles o assets no gestionados.

### Malentendidos operacionales

- **"Stealth significa sin logs."** Stealth real significa gestionar toda la telemetría relevante, incluyendo endpoint, cloud, DNS, flow, TLS e identidad.
- **"Los timing templates de Nmap definen detectabilidad."** `-T` cambia timing de paquetes; no borra probes de protocolo, creación de procesos, selección de objetivos ni comportamiento first-seen.
- **"Los scans cifrados ocultan todo."** TLS oculta payload después del handshake; todavía expone metadata de conexión y muchas veces fingerprints del handshake.
- **"Los decoys confunden la atribución para siempre."** Los decoys confunden logs ingenuos por IP, no clustering de comportamiento sobre secuencias idénticas de probes.

### Limitaciones modernas

- El ruido de fondo de internet crea alto volumen base de scans en el edge.
- NAT, proxies, egress cloud, concentradores VPN y flotas scanner pueden colapsar muchos actores en una IP fuente.
- Protocolos de privacidad y encrypted client hello reducen alguna metadata TLS.
- Los scans distribuidos de bajo volumen pueden ser difíciles de distinguir del uso normal de servicios sin contexto de asset e identidad.

### Puntos ciegos de telemetría

- El sampling de flow puede perder scans de baja tasa o corta vida.
- Sensores de paquetes pueden perder paths asimétricos, tráfico east-west cloud o feeds SPAN sobrecargados.
- EDR puede no cubrir appliances, containers, hosts no gestionados o scanner jump boxes.
- Firmas IDS pueden perder orden de probe custom o comportamiento de aplicación cifrada.

## Labs prácticos

Usá solo rangos de lab propios o entornos de training explícitos.

### Comparar telemetría de Masscan y Nmap

```
# Owned lab /24 only.
sudo masscan 10.10.10.0/24 -p80,443 --rate 200 -oL masscan.lst
sudo nmap -Pn -sS -p80,443 10.10.10.0/24 -oA nmap-http
```

Telemetría esperada: Masscan produce fan-out SYN horizontal más rápido con estado escaso; Nmap crea retries más lentos y stateful. Los defensores deberían comparar conteos de flow, Zeek `conn.log` y alertas de scan de Suricata.

### Generar logs Zeek de scan

```
sudo tcpdump -i any -w nmap-scan.pcap 'net 10.10.10.0/24'
nmap -Pn -p 22,80,443,445 10.10.10.20-40
zeek -r nmap-scan.pcap
zeek-cut id.orig_h id.resp_h id.resp_p conn_state history < conn.log | sort | uniq -c
```

Telemetría esperada: fuente repetida, puertos repetidos, estados fallidos e historias TCP similares. Supuesto falso a testear: "sin alerta Suricata significa sin scan."

### Observar profundidad NSE después del discovery

```
nmap -Pn -sV --script "default,safe" -p 80,443 LAB_HOST -oA nse-depth
```

Telemetría esperada: menos puertos pero transacciones HTTP/TLS más profundas. Zeek `http.log`/`ssl.log` y reglas HTTP/TLS de Suricata deberían mostrar comportamiento específico de scripts.

### Testear correlación de scan lento

```
for p in 22 80 443 445 3389; do
  nmap -Pn -p "$p" --scan-delay 20s LAB_HOST
done
```

Telemetría esperada: thresholds simples por minuto pueden no disparar. Analíticas de ventana larga deberían observar contactos first-seen a puertos y comportamiento proceso-red inusual.

### Testear fragmentación como claim moderno de evasión

```
sudo nmap -Pn -sS -p 80 LAB_HOST
sudo nmap -Pn -sS -f -p 80 LAB_HOST
sudo nmap -Pn -sS --mtu 24 -p 80 LAB_HOST
```

Telemetría esperada: un lab moderno Suricata/Zeek debería reconstruir o al menos exponer comportamiento de fragmentos. Si los resultados difieren, el lab encontró una propiedad del path de inspección, no "stealth mágico."

### Comparar pivots de fingerprint TLS

```
curl -vk https://LAB_HOST/ >/dev/null
python3 - <<'PY'
import urllib.request
urllib.request.urlopen("https://LAB_HOST/", timeout=3)
PY
```

Telemetría esperada: la misma URL puede producir distintos fingerprints TLS/client y user agents. Los defensores deberían tratar fingerprints como pivots que necesitan contexto de proceso y asset.

## Ejemplos prácticos

- Una cuenta de vulnerability scanner corre un job Nmap programado; es ruidoso pero esperado, ticketed y source-pinned.
- Una workstation lanza `rustscan` y luego `nmap -sV`; EDR y Zeek juntos muestran discovery seguido de enumeración.
- Un workload cloud contacta cientos de endpoints internos `22/tcp` y `445/tcp` después de un deploy nuevo, indicando service discovery mal configurado o compromiso.
- Un decoy scan produce 20 IPs fuente con orden idéntico de TCP options y secuencia de objetivos, haciendo más fuerte el clustering de comportamiento que la atribución por IP.
- Un scan lento de 48 horas se detecta porque un host de base de datos hizo contacto first-ever a muchos puertos admin.

## Notas relacionadas

- [[index|Ingeniería de Detección]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[false-positives-false-negatives-and-detection-tradeoffs|Falsos positivos, falsos negativos y tradeoffs de detección]]
- [[encrypted-traffic-analysis-and-metadata-leakage|Análisis de tráfico cifrado y fuga de metadata]]
- [[detection-evasion-myths-and-modern-limitations|Mitos de evasión de detección y limitaciones modernas]]
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths y observabilidad de kill chain]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[nmap-scanning|Nmap Scanning]]
- [[external-attack-surface|External Attack Surface]]
- [[run-scan-pipeline|Ejecutar pipeline de scan externo de recon]]

### Notas atómicas futuras sugeridas

- scan-to-exploit-transition-detection
- tls-fingerprinting-for-detection
- honeyports-and-tarpit-detection
- scan-entropy-analysis
- distributed-scan-correlation

## Referencias

- **Official Tool Docs:** Nmap Timing and Performance - https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Masscan README and man page - https://github.com/robertdavidgraham/masscan
- **Fundamental:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Investigación / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
