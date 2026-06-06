# Packet Fragmentation and Decoy Scans

## Definición

La fragmentación de paquetes (`-f`, `--mtu`) y los decoy scans (`-D`) son dos primitivas de evasión de Nmap que operan en capas diferentes: la fragmentación divide los headers de probe a través del límite de fragmentación IP para derrotar el matching de firmas *a nivel de paquete*, mientras que los decoys inundan los logs del objetivo con IPs fuente falsas adicionales para derrotar la atribución *a nivel de log*.

## Por qué importa

Ambas técnicas son ampliamente enseñadas y ampliamente malentendidas. No son stealth — la inspección stateful moderna rearma fragmentos y los SIEMs modernos agrupan por comportamiento, no por IP fuente. Su valor real es *diagnóstico*: cada primitiva aísla un supuesto en un middlebox o pipeline de detección. Mapear qué primitivas todavía funcionan contra un objetivo dado es cómo un operador de scan senior lee el stack de inspección desde afuera.

Confundir cualquiera de las dos con stealth real es el error clásico de principiante. Confundirlas con inútiles es el error clásico de nivel intermedio. El framing senior es que responden la pregunta "¿qué asume el pipeline de inspección del objetivo sobre los paquetes y las fuentes?".

## Cómo funciona

### Fragmentación

1. `-f` divide el header TCP en fragmentos IP de 8 bytes cada uno.
2. `--mtu N` permite al operador elegir el MTU (debe ser múltiplo de 8). `--mtu 24` es la variante común.
3. El reensamblado IP ocurre en el OS destino — pero los middleboxes pueden o no rearmar antes de aplicar firmas.
4. El error explotado: un motor de firmas que lee solo el primer fragmento no puede ver los flags TCP, el puerto fuente/destino ni el payload L4.
5. Snort/Suricata/Zeek modernos rearman por defecto. Las ACLs stateless legacy y algunos firewalls de dispositivos embebidos no.

### Decoys

1. `-D decoy1,decoy2,ME,decoy4` inyecta paquetes de scan con IPs fuente spoofed junto a la real. `ME` marca la posición de la fuente real.
2. `-D RND:10` genera 10 IPs aleatorias por iteración de scan.
3. El objetivo ve 11 fuentes golpeándolo. Desde el *log del objetivo*, el scanner real es una entrada entre muchas.
4. Los paquetes decoy tienen IPs fuente spoofed pero el mismo fingerprint de scan, mismo timing, mismos tipos de probe que los reales.
5. Los returns van a las IPs spoofed, no al scanner. Los decoys son útiles solo para flujos tipo SYN-scan donde el scanner no necesita la reply SYN-ACK para ese decoy.

## Técnicas / patrones

- **Diagnóstico de dos pasadas.** Correr lista de puertos idéntica con y sin `-f`. Los puertos solo `open` en la corrida fragmentada revelan que un middlebox no rearma.
- **La posición de `-D ME` importa.** Los decoys antes/después de `ME` cambian qué paquete golpea primero al objetivo; algunos IDSes alertan en la *primera* fuente vista.
- **Los decoys deben ser IPs alcanzables.** Las IPs de decoy que no son enrutables se dropean en el primer salto y nunca llegan al objetivo.
- **Combinar con `--data-length`.** Sin payload aleatorio, los probes fragmentados todavía tienen un fingerprint de longitud de probe constante.
- **Nunca usar IPs de terceros reales como decoys** en engagements de producción. Las quejas de abuso contra terceros ajenos ocurren — los rangos de documentación RFC 5737 (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) son operacionalmente más seguros que `RND:N`.

## Variantes y bypasses

### Variantes de fragmentación

#### Fragmentos tiny (`-f`)

Fragmentos de 8 bytes. Derrota solo motores de firmas que leen el primer fragmento únicamente. Casi todos los IDSes modernos rearman.

#### MTU custom (`--mtu N`)

N debe ser múltiplo de 8. `--mtu 16` produce fragmentos suficientemente grandes como para incluir el header TCP en el primer fragmento pero suficientemente pequeños como para dividir el payload.

#### Fragmentos superpuestos

Elaborados a mano (Scapy), no por Nmap. Los distintos OS usan diferentes políticas de reensamblado (first-wins BSD, last-wins Windows, RFC 1122 Linux). El ataque de desync target-vs-IDS.

### Variantes de decoy

#### Decoys aleatorios (`-D RND:N`)

Los más baratos, más ruidosos, más probables de involucrar IPs no enrutables. La receta tutorial por defecto.

#### Decoys curados

IPs de decoy elegidas a mano del AS del objetivo, redes de partners o scanners conocidos (Censys, Shodan, proyectos de medición de internet). Entierra la fuente real en ruido esperado.

#### Idle scan (`-sI`)

No es estrictamente un decoy pero de la misma familia: usa el contador IPID incremental de un host "zombie" de terceros para inferir el estado del puerto. La IP del scanner nunca aparece en los logs del objetivo.

## Impacto

- **Reducción falsa de la tasa de detección por IP fuente** cuando el triage de logs es ingenuo.
- **Divulgación diagnóstica** — las diferencias de fragmentación y la efectividad de los decoys revelan el stack de inspección al operador.
- **Riesgo operacional** — los decoys aleatorios contra infraestructura crítica pueden desencadenar quejas de abuso contra terceros no relacionados.
- **Mala atribución dentro del SOC del objetivo** — los analistas que no se dan cuenta de que hay decoys pueden perseguir una de las IPs de decoy como el "verdadero" atacante.

## Detección y defensa

1. **Rearmar en el IDS.**
   Comportamiento por defecto de Snort/Suricata/Zeek. Derrota la fragmentación completamente. La defensa es *auditoría de configuración*, no comprar un producto nuevo.

2. **Agrupar entradas de log por comportamiento, no por IP fuente.**
   Si 11 IPs envían secuencias de probe idénticas en milisegundos, son un actor con decoys. Las reglas de correlación SIEM modernas expresan esto como "alertar cuando N IPs fuente distintas golpean el mismo dst:port dentro de W segundos con fingerprint TCP idéntico."

3. **Dropear paquetes con source-routed y con opción timestamp en el edge.**
   Los juegos con `--ip-options` dejan de funcionar si el perímetro dropea opciones IP incondicionalmente.

4. **Rate limit por IP fuente combinado con TCP fingerprinting (tipo p0f).**
   Incluso con decoys, el OS del scanner se filtra (TTL, tamaño de ventana, orden de opciones, MSS) aparece idénticamente en todos los paquetes decoy — el fingerprint *es* la clave de cluster.

### Qué no funciona como defensa primaria

- **Bloquear ICMP** creyendo que va a parar los scans.
- **Esperar que el IDS vea a través de `-f`** sin auditar los ajustes de reensamblado.
- **Geo-bloquear las IPs de decoy obvias** — los rangos de IPs aleatorios derrotan el filtrado geo trivialmente.

## Labs prácticos

```
# Lab 1 — fragmentation diagnostic on an authorized lab IDS.
sudo nmap -Pn -sS -p 22,80,443 LAB > normal.out
sudo nmap -Pn -sS -p 22,80,443 -f > frag.out
sudo nmap -Pn -sS -p 22,80,443 --mtu 24 > mtu24.out
diff normal.out frag.out; diff frag.out mtu24.out
# Ports open in frag.out/mtu24.out but missing in normal.out reveal a non-reassembling middlebox.
```

```
# Lab 2 — decoy attribution test on an authorized lab IDS.
sudo nmap -Pn -sS -p 80 -D 192.0.2.10,192.0.2.20,ME,192.0.2.30 LAB
# Then check the IDS console: does it cluster the 4 sources as one actor, or alert 4 times?
```

```
# Lab 3 — TCP fingerprint persists across decoys.
sudo nmap -Pn -sS -p 80 -D RND:10 LAB
# In a Wireshark capture from the IDS sensor, all 11 source IPs carry identical
# TTL, window size, MSS, and TCP options. That is the fingerprint that beats decoys.
sudo tshark -i any -f 'host LAB and tcp port 80' -T fields -e ip.src -e ip.ttl -e tcp.window_size_value
```

```
# Lab 4 — idle scan when a zombie exists.
sudo nmap -O ZOMBIE | grep "IP ID Sequence"        # need "Incremental"
sudo nmap -Pn -sI ZOMBIE:80 -p 22,80,443,3389 LAB
```

```
# Lab 5 — IP options probe.
sudo nmap -Pn --ip-options "L 192.0.2.1" -p 80 LAB
# Replies indicate the path tolerates loose source routing, which is a routing misconfiguration finding.
```

## Ejemplos prácticos

- **Objetivo cloud hardened.** La fragmentación no produce puertos `open` nuevos — el edge del proveedor cloud rearma. Resultado negativo útil: descarta esa clase de evasión para la próxima fase.
- **Red industrial legacy.** `-f` revela puertos invisibles para el scan por defecto porque el appliance inline es un firewall stateless del año 2008.
- **Engagement red team contra equipo SIEM.** Los decoys curados del AS del objetivo mismo prueban si el SIEM agrupa por comportamiento o por IP fuente.
- **Bug bounty scope con rate limiting estricto por IP.** Los decoys son inútiles (el rate limit aplica a tu IP sin importar los falsos); cambiar a `--scan-delay` en su lugar.

## Notas relacionadas

- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[nmap-scanning|Nmap Scanning]]
- [[firewalls-and-network-boundaries|Firewalls y Límites de Red]]
- [[packet-analysis|Análisis de Paquetes]]
- [[wireshark-workflows|Wireshark Workflows]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de Anomalías de Scan y Análisis de Fingerprint]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]

## Referencias

- **Docs Oficiales:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Investigación / Deep Dive:** Ptacek & Newsham — Insertion, Evasion, and Denial of Service (1998) — https://insecure.org/stf/secnet_ids/secnet_ids.pdf
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
