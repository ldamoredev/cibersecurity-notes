# EDR Network Observability and Process Correlation

## Definición

La observabilidad de red en EDR es la captura desde el endpoint de actividad relacionada con red, especialmente la capacidad de correlacionar sockets, conexiones, destinos, actividad tipo DNS y alertas con linaje de procesos, command lines, usuarios, hashes, sesiones e identidad del host.

## Por qué importa

El gran cambio en la defensa moderna no es solo mejor inspección de paquetes. Es correlación. Una alerta de red antes decía "la IP fuente 10.0.4.20 contactó 10.0.9.14:445". EDR muchas veces puede decir "PowerShell lanzó un scanner renombrado, bajo este usuario, desde este proceso padre, y después abrió estos sockets hacia estos hosts".

Eso cambia los tradeoffs ofensivos y defensivos. Fragmentación, decoys, trucos de source-port y timing lento todavía pueden afectar algunos sensores de red, pero no borran creación de procesos, historial de command line, file hashes, cadenas padre, identidad, metadata de workloads cloud ni eventos de sockets locales al host.

## Cómo funciona

La correlación endpoint-red sigue un **modelo de join de 5 partes**:

1. **Creación de proceso.** EDR registra ruta del ejecutable, command line, hash, signer, usuario, elevación del token, proceso padre y hora de inicio.
2. **Evento de red.** EDR registra actividad de conexión saliente o entrante: IP/puerto remoto, IP/puerto local, protocolo, acción y a veces contexto DNS o URL.
3. **Join de ownership.** El evento de red se vincula al proceso o proceso iniciador que lo causó.
4. **Join de linaje.** Padre, abuelo, sesión de usuario, logon ID e identidad del host ubican el comportamiento en contexto.
5. **Join de entorno.** Contexto de red, cloud, identidad, vulnerabilidad y rol del asset determina si el comportamiento es esperado.

Ejemplo:

```
Network sensor:
  10.0.4.22 scanned 10.0.9.0/24:445.

EDR join:
  powershell.exe -> rundll32.exe -> c:\programdata\svchost.exe
  command line included encoded script
  same process opened 254 SMB connections in 3 minutes
  host role: finance workstation
```

La detección pivotea de "una IP escaneó" a "una cadena de procesos sospechosa hizo discovery interno".

## Técnicas / patrones

- **Joins proceso-a-red.** Vincular destinos de red con ejecutable, command line, proceso padre, usuario y rol del host.
- **Comportamiento de red raro por proceso.** Alertar cuando un proceso que normalmente no hace conexiones contacta muchos hosts, puertos raros o destinos externos nuevos.
- **Detección de ancestry de scanners.** Identificar `nmap`, `masscan`, `rustscan`, `zmap`, `curl`, `python`, `powershell` o binarios renombrados por ruta, hash, forma de command line y patrón de sockets.
- **Comportamiento living-off-the-land en red.** Detectar fan-out inusual desde `powershell`, `wscript`, `mshta`, `rundll32`, `wmic`, `certutil`, shells, package managers y herramientas admin.
- **Correlación de alertas de endpoint y red.** Elevar cuando un host tiene alertas IDS de red y eventos sospechosos de proceso/archivo/logon en la misma ventana.
- **Contexto de proceso en workloads cloud.** En workloads cloud cubiertos por EDR, unir flow logs o alertas de red con telemetría de proceso de contenedor/VM e identidad cloud.

## Variantes y bypasses

La correlación endpoint-red tiene **7 patrones relevantes para detección**.

### 1. Proceso scanner conocido

El caso más fácil: `nmap`, `masscan`, `rustscan` o `zmap` se lanza y crea comportamiento de red coincidente. Esto debería ser benigno solo en assets scanner aprobados.

### 2. Binario scanner renombrado

El filename cambia, pero hash, signer, flags de command line, padre, patrón de sockets y fan-out de puertos todavía pueden revelar el comportamiento.

### 3. Socket scanner scriptado

Python, PowerShell, Go, Bash o Node abren muchos sockets. La telemetría de red ve scans; EDR aporta el intérprete, ruta del script, command line y padre.

### 4. Discovery living-off-the-land

Herramientas built-in enumeran SMB, LDAP, WinRM, HTTP, API de Kubernetes o metadata cloud. El nombre de proceso parece normal; la distribución de objetivos y el mismatch de rol lo vuelven sospechoso.

### 5. Actividad mediada por navegador o proxy

Endpoint ve el navegador o proceso proxy, mientras sensores de red ven el destino. Atribuir a una acción de usuario versus automatización maliciosa puede requerir command line, extensión, URL y contexto temporal.

### 6. Scanning en containers y workloads efímeros

El proceso puede vivir dentro de un contenedor, pod de corta vida, runtime serverless o job de CI. Hay que unir EDR del host, telemetría de runtime de contenedores, cloud flow logs y audit logs del orquestador.

### 7. Comportamiento de red ciego para EDR

Appliances, sistemas no gestionados, dispositivos de red, IoT, BYOD o hosts manipulados pueden ser visibles solo para telemetría de red.

## Impacto

- **Mejora la atribución.** Proceso, usuario, padre, hash y rol del host dan evidencia que la IP fuente no puede.
- **La evasión vieja se debilita.** Los trucos a nivel paquete no borran evidencia de proceso en endpoint.
- **El triage acelera.** Los analistas pueden scopear desde proceso a conexiones, archivos, logons y alertas relacionadas.
- **La detección se expande hacia adentro.** Tráfico host-local, cloud, VPN, contenedores y split-tunnel puede ser visible donde sensores perimetrales están ciegos.
- **La cobertura se vuelve desigual.** La visibilidad EDR depende de despliegue, soporte de plataforma, resistencia a tamper, retención y fidelidad de schema.

## Detección y defensa

Ordenado por efectividad:

1. **Uní comportamiento de red con linaje de proceso siempre que sea posible.**
   Una alerta de red sin contexto de proceso es una pista; una alerta de red con proceso, usuario, padre y command line es una investigación.

2. **Baseliná comportamiento de red por proceso y rol de host.**
   `nginx` contactando upstream services difiere de `excel.exe` contactando cientos de hosts internos. Los baselines conscientes de rol reducen ataques perdidos y ruido.

3. **Priorizá parent-child-process anormal más comportamiento de red.**
   Padres sospechosos lanzando hijos activos en red suelen importar más que el destino solo.

4. **Correlacioná EDR con Zeek, Suricata, NetFlow, DNS, proxy y logs cloud.**
   Cada capa puede contradecir o confirmar a las otras. La visibilidad de endpoint es más fuerte cuando no está sola.

5. **Rastreá cobertura de sensores y señales de tamper.**
   Falta de EDR en un host crítico, sensores de red deshabilitados, agentes stale y gaps de telemetría deberían tratarse como hallazgos de riesgo.

### Qué no funciona como defensa primaria

- **Visibilidad solo de endpoint.** EDR pierde assets no gestionados, appliances, dispositivos de red y a veces verdad a nivel paquete.
- **Visibilidad solo de red.** Los sensores de red muchas veces no pueden identificar proceso, usuario, padre ni fuente del script.
- **Detección de scanners basada en filename.** Renombrar binarios y envolver herramientas en scripts es trivial.
- **Atribución por IP fuente.** NAT, proxies, decoys, VPNs, egress cloud y hosts comprometidos hacen débil la atribución por IP sin contexto de endpoint o identidad.
- **Asumir que EDR ve todos los sockets.** Loopback, kernel drivers, containers, procesos de corta vida, tampering y límites de plataforma pueden crear gaps.

### Malentendidos operacionales

- **"Si EDR está instalado, el host es visible."** Salud del agente, política, soporte de SO, exclusiones, eventos de tamper y delay de ingestión determinan la visibilidad real.
- **"El linaje de proceso siempre dice la verdad."** Process injection, parent spoofing, hollowing y truncamiento de telemetría pueden debilitar el linaje.
- **"Las detecciones de red son obsoletas."** La telemetría de endpoint complementa, no reemplaza, evidencia de paquetes, flow y protocolo.
- **"El proceso padre prueba intención."** Parentage es evidencia, no motivo. Herramientas admin y automatización pueden verse sospechosas sin intención maliciosa.

### Limitaciones modernas

- Containers, workloads efímeros, funciones serverless y PaaS gestionado reducen cobertura EDR tradicional de host.
- Controles de privacidad y sandboxing del SO pueden limitar recolección de command line o detalle de red.
- Atacantes pueden usar binarios firmados, procesos inyectados, herramientas legítimas de administración remota y APIs cloud para mezclarse con operaciones normales.
- Los schemas de vendors evolucionan, y detecciones atadas a nombres de campos requieren mantenimiento.

### Puntos ciegos de telemetría

- Endpoints no gestionados, appliances, IoT, gear de red, impresoras, storage devices y BYOD.
- Exclusiones EDR para directorios o procesos sensibles a performance.
- Procesos de corta vida que crean conexiones antes de que llegue enrichment completo.
- Split-tunnel VPN, proxy local en host, puentes de contenedores, service mesh sidecars y loopback.
- Reuso de PID cuando las detecciones no usan process IDs únicos y timestamps.

## Labs prácticos

Usá un endpoint de lab con tu propio EDR, Sysmon, osquery, Elastic Defend, Defender for Endpoint o telemetría equivalente.

### Correlacionar un proceso scanner con fan-out de red

```
nmap -Pn -p 22,80,443 LAB_SUBNET/28
```

Telemetría esperada: EDR debería registrar creación de proceso para `nmap` y eventos de red hacia múltiples hosts/puertos. Los sensores de red deberían mostrar fan-out de scan. La detección ocurre en el join.

### Renombrar un scanner y testear detección basada en comportamiento

```
cp "$(command -v nmap)" /tmp/update-helper
/tmp/update-helper -Pn -p 80,443 LAB_SUBNET/28
```

Telemetría esperada: las reglas solo por filename pueden fallar; hash, signer, flags de command line, padre y fan-out de red deberían seguir revelando comportamiento de scanner.

### Generar socket scanning scriptado

```
python3 - <<'PY'
import socket
for host in [f"10.10.10.{i}" for i in range(10, 30)]:
    for port in [22, 80, 443]:
        s = socket.socket()
        s.settimeout(0.2)
        try:
            s.connect((host, port))
        except Exception:
            pass
        s.close()
PY
```

Telemetría esperada: EDR ve `python3` como proceso; flow/Zeek ve el fan-out. Supuesto falso: solo importan scanners con nombre.

### Unir comportamiento de red PowerShell al proceso padre

```
1..20 | ForEach-Object {
  Test-NetConnection -ComputerName "10.10.10.$_" -Port 445 -InformationLevel Quiet
}
```

Telemetría esperada: command line de proceso, shell padre, usuario e intentos de conexión saliente deberían alinearse. Los defensores deberían distinguir scripts admin de comportamiento anormal para el rol del host.

### Comparar puntos ciegos de endpoint y red

```
# On a lab host, compare endpoint event count with Zeek conn.log count
nmap -Pn -p 1-100 LAB_HOST
zeek-cut id.orig_h id.resp_h id.resp_p conn_state < conn.log | wc -l
```

Telemetría esperada: los conteos pueden diferir porque EDR registra sockets intentados, Zeek registra paquetes observados, y cada uno tiene límites de timing/visibilidad.

## Ejemplos prácticos

- Una alerta IDS perimetral sobre probing de exploit HTTP gana alta confianza cuando EDR muestra que `python.exe` se lanzó desde un archive sospechoso y contactó el mismo host.
- Un scan interno lento desde una workstation se detecta porque `powershell.exe` hizo conexiones first-ever a muchos puertos SMB.
- Un burst de Masscan desde una VM cloud se triagea rápido porque los tags del asset cloud muestran que es una instancia scanner aprobada.
- Un decoy scan confunde logs del objetivo, pero EDR en el host scanner real registra el proceso y command line reales.
- Un appliance de red escanea inesperadamente; EDR está ausente, así que defensores dependen de NetFlow, Zeek, inventario de assets y registros de cambios.

## Notas relacionadas

- [[index|Ingeniería de Detección]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[behavioral-detection-vs-signature-detection|Detección de comportamiento vs detección por firmas]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths y observabilidad de kill chain]]
- [[detection-evasion-myths-and-modern-limitations|Mitos de evasión de detección y limitaciones modernas]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[active-recon|Active Recon]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[cloud-logging-and-detection|Cloud Logging and Detection]]
- [[client-ip-trust|Client IP Trust]]

### Notas atómicas futuras sugeridas

- process-lineage-for-detection
- edr-schema-field-quality
- container-runtime-network-telemetry
- endpoint-network-correlation-queries
- pid-reuse-and-process-identity

## Referencias

- **Telemetry Schema:** Microsoft Defender XDR DeviceProcessEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table
- **Telemetry Schema:** Microsoft Defender XDR DeviceNetworkEvents - https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table
- **Fundamental:** MITRE ATT&CK Data Sources - https://attack.mitre.org/datasources/
- **Investigación / Deep Dive:** Elastic Endpoint Investigation Across the Environment - https://www.elastic.co/security-labs/investigating-from-the-endpoint-across-your-environment
