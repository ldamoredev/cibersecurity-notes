---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - scanning
  - nmap
sources: []
---

# Escaneo con Nmap

## Definición
Nmap es una herramienta de descubrimiento y escaneo de red usada para identificar hosts alcanzables, puertos abiertos, versiones de servicio, comportamiento de protocolo y exposición básica desde un punto de vista de red elegido.

## Por qué importa
Nmap convierte los supuestos de arquitectura en evidencia. Te dice qué responde desde donde estás parado: internet pública, VPN, bastión, contenedor, subred o workload de nube. Ese punto de vista importa porque un puerto "abierto" siempre es relativo a un camino.

Esta nota es dueña de la estrategia de escaneo con Nmap. [[ports-and-services|Puertos y servicios]] es dueña del concepto de superficie que escucha. [[service-enumeration|Enumeración de servicios]] es dueña de interpretar qué parece ser el servicio después de encontrar un puerto.

## Cómo funciona
El escaneo con Nmap responde **5 preguntas**:

1. **¿El host es alcanzable?** Las sondas de descubrimiento de hosts deciden si Nmap trata a un target como vivo.
2. **¿Qué puertos responden?** Los tipos de escaneo TCP/UDP infieren el estado open, closed o filtered.
3. **¿Qué servicio probablemente escucha?** La detección de versión sondea banners y respuestas de protocolo.
4. **¿Qué comportamiento extra está expuesto?** Los scripts NSE pueden chequear TLS, HTTP, SMB, DNS y muchos otros servicios.
5. **¿Qué ve este punto de vista?** Los resultados difieren desde internet pública, subred interna, VPN o VPC de nube.

Ejemplo:

```bash
nmap -Pn -sS -sV --top-ports 1000 app.example.com
```

Interpretación:

- `-Pn` saltea el descubrimiento de hosts y escanea aunque las sondas tipo ping estén bloqueadas.
- `-sS` realiza escaneo TCP SYN donde los privilegios lo permiten.
- `-sV` les pide a los servicios que se identifiquen.
- `--top-ports 1000` prioriza puertos comunes rápidamente.

El bug no es "un puerto está abierto"; el bug es alcanzabilidad o comportamiento de servicio inesperado desde un punto de vista que no debería tener acceso.

## Técnicas / patrones
Atacantes y defensores usan Nmap para:

- comparar la exposición prevista contra la exposición observada
- escanear desde múltiples puntos de vista: público, VPN, interno, contenedor, workload de nube
- distinguir `open`, `closed` y `filtered`
- identificar versiones de servicio con `-sV`
- inspeccionar la postura de TLS/HTTP con scripts NSE seguros
- enumerar UDP con cuidado porque el silencio puede significar filtrado o pérdida de paquetes
- validar cambios de firewall/security-group antes y después del deploy
- producir evidencia reproducible para hallazgos y remediación

## Variantes y bypasses
Los flujos de trabajo de Nmap caen en **6 modos prácticos**.

### 1. Descubrimiento de hosts
`-sn`, ARP, ICMP, TCP ping y sondas relacionadas identifican hosts vivos. Los firewalls pueden bloquear algunas sondas, así que un host que parece caído puede igual tener servicios abiertos.

### 2. Escaneo de puertos TCP
SYN (`-sS`), connect (`-sT`) y escaneos de rango completo identifican servicios TCP que escuchan. `open`, `closed` y `filtered` son observaciones de red, no etiquetas de vulnerabilidad.

### 3. Escaneo UDP
UDP (`-sU`) es más lento y ruidoso porque muchos servicios no responden salvo que el payload sea protocolo-correcto. Usá puertos dirigidos y esperá ambigüedad.

### 4. Detección de servicio/versión
`-sV` envía sondas para inferir el protocolo y el software. Es más útil que el banner grabbing solo, pero todavía es una inferencia que debería validarse manualmente para hallazgos importantes.

### 5. Chequeos con scripts NSE
El Nmap Scripting Engine puede chequear ciphers de TLS, títulos HTTP, scripts por defecto, info de SMB, comportamiento de DNS y más. NSE es poderoso; elegí scripts deliberadamente y evitá categorías intrusivas salvo que estés autorizado.

### 6. Controles de evasión y timing
El timing (`-T`), los rate limits, los puertos de origen, la fragmentación y los decoys existen, pero la validación defensiva normalmente se beneficia más de escaneos claros y reproducibles que del sigilo.

## Impacto
Ordenado aproximadamente por severidad:

- **Exposición pública inesperada.** Bases de datos, paneles de admin, SSH, Redis, Elasticsearch o servidores de desarrollo alcanzables desde internet.
- **Falla de frontera.** Puertos visibles desde un segmento de red que no debería alcanzarlos.
- **Servicios sombra.** Daemons viejos o puertos de sidecar no rastreados en el inventario.
- **Divulgación de versión.** La detección de servicio revela software desactualizado o defaults riesgosos.
- **Falsa confianza.** Un escaneo desde el punto de vista equivocado se pierde el camino real que atacantes o workloads pueden usar.
- **Ruido operativo.** Los escaneos agresivos pueden disparar alertas o degradar sistemas frágiles si se corren sin cuidado.

## Detección y defensa
Ordenado por efectividad:

1. **Escaneá desde los mismos puntos de vista que usan los llamantes reales.**
   La exposición pública, la exposición por VPN, la exposición de subred interna y la exposición contenedor-a-host son verdades distintas. Un solo escaneo desde tu laptop no alcanza para validar una frontera.

2. **Mantené los escaneos scopeados, autorizados y reproducibles.**
   Guardá las listas de targets, flags, fecha, IP de origen y salida. Los escaneos reproducibles dejan que los defensores comparen antes/después de la remediación sin discutir desde capturas de pantalla.

3. **Usá profundidad por etapas.**
   Empezá con escaneos rápidos de top-port o puertos-conocidos, después profundizá solo donde se necesite con puertos completos, `-sV`, UDP o scripts. Esto reduce el ruido y mantiene los resultados interpretables.

4. **Validá los resultados de alto impacto manualmente.**
   Si Nmap dice que una base de datos o servicio de admin está expuesto, confirmá con tooling específico de protocolo o banner grabs. Los falsos positivos y los mislabels de servicio pasan.

5. **Integrá los resultados de escaneo con el inventario.**
   Cada servicio inesperado debería volverse una pregunta de propiedad: quién es el dueño, por qué es alcanzable y qué frontera debería protegerlo.

6. **Monitoreá el escaneo pero no trates el escaneo como el problema raíz.**
   Las alertas sobre patrones de escaneo son útiles, pero la defensa durable es reducir los servicios expuestos y apretar las fronteras.

### Qué no funciona como defensa primaria

- **"Nmap no lo encontró" como prueba de ausencia.** Firewalls, ambigüedad de UDP, timing, IPv6, hostnames alternativos y diferencias de punto de vista pueden todos esconder exposición.
- **Escanear solo nombres de DNS.** Las IPs directas, los origins viejos y los rangos de nube pueden exponer servicios no linkeados desde el DNS actual.
- **Usar `-A` en todos lados.** La detección agresiva aumenta el ruido y puede correr scripts que no pretendías. Usalo deliberadamente.
- **Tratar filtered como seguro.** Filtered significa que Nmap no pudo obtener una respuesta clara desde ese camino. No prueba que el servicio sea seguro.
- **Ignorar IPv6.** Muchos entornos aseguran IPv4 y accidentalmente exponen IPv6.

## Labs prácticos
Corré solo en sistemas que sean tuyos o para los que tengas autorización explícita de testear.

### Escaneo rápido de postura externa

```bash
nmap -Pn --top-ports 1000 -oA scans/app-top app.example.com
```

Usá esto como una foto rápida de exposición pública.

### Detección de servicio/versión en puertos conocidos

```bash
nmap -Pn -sV -p 22,80,443,8080,8443 -oA scans/app-services app.example.com
```

Seguí cualquier protocolo o versión inesperada manualmente.

### Comparar puntos de vista público e interno

```bash
# Desde internet pública
nmap -Pn -p 22,80,443,5432,6379 app.example.com

# Desde un host VPN/interno
nmap -Pn -p 22,80,443,5432,6379 app.example.com
```

La diferencia entre estas salidas suele ser la historia de la frontera.

### Escaneo TCP completo cuando los top ports no alcanzan

```bash
nmap -Pn -p- --min-rate 1000 -oA scans/app-alltcp app.example.com
```

Usalo cuando sospechás servicios de admin/dev en puertos altos.

### Escaneo UDP dirigido

```bash
nmap -Pn -sU -p 53,123,161,500,4500 --version-light app.example.com
```

UDP es más lento y ambiguo; mantenelo dirigido.

### Uso seguro de NSE

```bash
nmap -Pn -sV --script "default,safe" -p 80,443 app.example.com
nmap -Pn --script ssl-enum-ciphers -p 443 app.example.com
```

Evitá scripts intrusivos salvo que el alcance lo permita explícitamente.

## Ejemplos prácticos
- Un escaneo público encuentra `5432/tcp open postgresql` en un host que debería exponer solo HTTPS.
- Un escaneo interno ve Redis en `6379` mientras el escaneo público no, confirmando que la segmentación funciona en parte.
- Un escaneo IPv6 encuentra SSH alcanzable aunque los security groups de IPv4 estén estrictos.
- `-sV` identifica un servidor de desarrollo en `3000` detrás de un registro DNS viejo.
- Un escaneo antes/después prueba que un cambio de firewall removió el acceso público a un puerto de admin.

## Notas relacionadas
- [[ports-and-services|Puertos y servicios]] — qué significa la superficie que escucha.
- [[service-enumeration|Enumeración de servicios]] — interpretar el comportamiento del servicio tras el descubrimiento.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — validar las reglas de frontera.
- [[cybersecurity/attack-surface-mapping/exposed-service-triage|Triaje de servicios expuestos]]
- [[packet-analysis|Análisis de paquetes]] — inspeccionar el tráfico cuando el comportamiento del escaneo no está claro.
- [[wireshark-workflows|Flujos de trabajo con Wireshark]] — flujo de captura de paquetes para validación de escaneo.
- [[cybersecurity/offensive-security/nmap-timing-and-evasion|Timing y evasión en Nmap]] — análisis profundo de las perillas de timing/evasión introducidas en el modo 6.
- [[cybersecurity/offensive-security/packet-fragmentation-and-decoy-scans|Fragmentación de paquetes y escaneos con decoys]] — análisis profundo compañero de la mecánica de `-f`/`--mtu`/`-D`.
- [[cybersecurity/offensive-security/masscan-internet-scale-scanning|Masscan: escaneo a escala de internet]] — el par de descubrimiento masivo cuando el espacio de direcciones excede la escala cómoda de Nmap.
- [[cybersecurity/offensive-security/rustscan-and-nse-pipeline|RustScan y pipeline NSE]] — acelerador de host único que alimenta a Nmap.
- [[cybersecurity/detection-engineering/scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de escaneo y análisis de fingerprint]] — interpretación del lado del defensor del timing, entropía, fingerprints y transiciones de escaneo.
- [[cybersecurity/detection-engineering/edr-network-observability-and-process-correlation|Observabilidad de red de EDR y correlación de procesos]] — cómo el comportamiento del escáner se une al contexto de proceso y usuario.

### Notas atómicas futuras sugeridas
- [[nmap-scan-types|Tipos de escaneo de Nmap]]
- [[udp-scanning|Escaneo UDP]]
- [[nse-scripts|Scripts NSE]]
- [[ipv6-exposure-scanning|Escaneo de exposición IPv6]]
- [[scan-scope-and-authorization|Alcance y autorización del escaneo]]
- [[external-vs-internal-scanning|Escaneo externo vs interno]]
- [[scan-to-exploit-transition-detection|Detección de transición de escaneo a exploit]]

## Referencias
- **Official Tool Docs:** Nmap Reference Guide — https://nmap.org/book/man.html
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Testing / Lab:** OWASP WSTG Information Gathering — https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/01-Information_Gathering/
