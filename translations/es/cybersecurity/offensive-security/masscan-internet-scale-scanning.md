# Masscan Internet-Scale Scanning

## Definición

Masscan es un scanner de puertos TCP/IP asíncrono y stateless con su propio stack de red en espacio de usuario, diseñado para enumerar puertos abiertos en espacios de direcciones muy grandes (prefijos BGP AS enteros, bloques /8, o el internet IPv4 completo) a tasas de paquetes que el stack TCP del kernel no puede sostener.

## Por qué importa

El modelo mental de Nmap — estado de conexión por objetivo, reintentos, probing de versión — se rompe pasado ~/16 de espacio de direcciones porque el estado por conexión domina la RAM y el CPU. Masscan responde una pregunta diferente: "dado una lista enorme de direcciones y un conjunto fijo de puertos, ¿dónde están las puertas?". Es la herramienta correcta cuando la pregunta es amplitud, y la incorrecta cuando la pregunta es profundidad.

El framing senior es el pipeline de dos fases: **Masscan encuentra las puertas, Nmap (o herramientas específicas de servicio) las atraviesa.** Tratar Masscan como un "Nmap rápido" produce tanto resultados incorrectos como accidentes operacionales — la historia de seguridad (tasa, listas de exclusión, IP fuente) es completamente diferente a la de Nmap.

## Cómo funciona

La arquitectura de Masscan son **4 decisiones de diseño**:

1. **TX/RX asíncrono stateless.** Dos threads. El thread TX emite SYNs tan rápido como `--rate` permite. El thread RX escucha SYN-ACKs y los registra. No hay estado por objetivo; ambos threads solo ven el wire.
2. **Stack TCP/IP en espacio de usuario.** Masscan emite frames Ethernet raw y lee responses raw, saltando el kernel. Esto es lo que le permite escalar; también es por qué `--adapter-ip` debe setearse en hosts multi-homed o de ruta no predeterminada.
3. **Recorrido aleatorio del espacio de direcciones.** La randomización por defecto distribuye los probes por el rango objetivo para que ningún router intermedio o rate limiter vea una ráfaga secuencial.
4. **Tasa como único dial.** `--rate` controla directamente la carga del link. No hay plantilla de timing al estilo Nmap — paquetes-por-segundo es el contrato.

Ejemplo:

```
# A scoped, polite, full-port scan of one /24.
sudo masscan 10.0.0.0/24 -p0-65535 \
    --rate 1000 \
    --excludefile /etc/masscan/exclude.conf \
    -oJ scan.json
```

Interpretación:
- `--rate 1000` = 1000 paquetes por segundo. Seguro en un link simple.
- `--excludefile` se honra *antes* de la lista de inclusión. No anulable. Esta es la propiedad de seguridad que hace a Masscan operacionalmente responsable.
- `-oJ` JSON delimitado por líneas va al disco — sobrevive Ctrl-C con `paused.conf`.

## Técnicas / patrones

- **Disciplina de `--excludefile` antes que cualquier otra cosa.** Construí la lista de exclusión (datos IRR, asignaciones gubernamentales, rangos de documentación RFC 5737, partners sensibles, tu propia infraestructura de monitoreo) y `--echo` la config mergeada para inspeccionar antes de escanear.
- **Empezar en `--rate 1000`** en links compartidos. Medí RTT y tasa de ICMP-type-3 desde tu upstream. Aumentá solo después de que el path esté verificado.
- **`--shard X/Y`** para dividir trabajo entre Y boxes de scan particionando el espacio de direcciones deterministamente.
- **Siempre guardar en binario (`-oB`)** para trabajos sobre ~/16. `--readscan` vuelve a parsear el binario en JSON/XML/grepable después.
- **Pipeline de dos fases.** Masscan produce tuplas `host:port` → alimentarlas en Nmap con `-iL` y `-p` para detección de versión, NSE, detección de OS.
- **Usá `--source-ip` y `--source-port`** para anclar tu huella de scan en logs de auditoría.

## Variantes y bypasses

### 1. Bounded enumeration

`masscan 10.0.0.0/8 -p443 --rate 5000`. Un puerto, espacio grande. Actualización estándar de superficie de ataque externa contra el AS de una organización.

### 2. AS-targeted scan

Pre-resolver un AS a sus prefijos con `whois -h whois.radb.net -- "-i origin AS123"` y alimentar la lista como `-iL`. La forma correcta de mapear la huella de IPs públicas de una organización.

### 3. Port-set discovery

`masscan 192.0.2.0/24 -p21,22,23,80,443,3389,5900,8080,8443 --rate 1000`. Sweep de puertos comunes a través de una subred — precursor rápido de Nmap enfocado.

### 4. Banner snapshot mode

`--banners --rate 100` abre sesiones TCP completas en puertos encontrados y captura el primer paquete del servidor. Útil para distinguir versiones SSH o HTTP vs. HTTPS sin invocar Nmap. *Reduce la tasa efectiva ~10× — no es gratis.*

### 5. UDP scanning

`-pU:53,123,161,1900 --rate 1000`. Biblioteca de probes más pequeña que Nmap, pero adecuada para los servicios UDP bien conocidos.

### 6. Resume after pause

`masscan --resume paused.conf`. Se escribe automáticamente en Ctrl-C o kill. La forma correcta de ejecutar scans de varios días a través de ventanas de mantenimiento programadas.

## Impacto

- **Amplitud.** Scans de un solo host de /8 en minutos; IPv4 completo en aproximadamente una hora en hardware dedicado.
- **Fragilidad operacional.** Un `--rate` mal configurado en un link compartido es un denial-of-service contra todos en ese link. Siempre empezar pequeño.
- **Detección.** Masscan es altamente detectable — floods de puerto fuente aleatorio a muchos destinos desde una IP son firmas de scan de libro de texto.
- **Atribución de fuente.** Trivial. `--adapter-ip` siempre se registra.
- **Saturación del path.** Incluso a `--rate` seguro, los routers intermedios cerca de tu box de scan pueden sufrir CPU-bottleneck en el flood de paquetes pequeños.

## Detección y defensa

1. **Alerta de tasa SYN por fuente en el perímetro.**
   La firma de Masscan es N destinos distintos por IP fuente por minuto.

2. **Allowlisting equivalente a `--excludefile` del lado defensor.**
   Los objetivos que nunca deberían ver tráfico de scan (gestión fuera de banda, ICS/SCADA, integraciones de partners) pertenecen en una lista tarpit/drop.

3. **TCP fingerprinting.**
   El stack en espacio de usuario de Masscan emite un fingerprint TCP reconocible. Las herramientas tipo p0f identifican el tráfico de Masscan sin importar la IP fuente.

4. **Correlación de anomalías NetFlow/IPFIX.**
   Masscan crea un patrón fan-out visible en registros de flujo mucho por debajo de la visibilidad a nivel de paquetes del SIEM.

### Qué no funciona como defensa primaria

- **Bloquear IPs fuente de scan individuales a posteriori** — Masscan termina su trabajo en segundos; el bloqueo es post-mortem.
- **Confiar en el output de `--banners` como inventario de servicios** — el banner es un paquete, frecuentemente engañoso en TLS, HTTP/2 o servicios con load balancing.

## Labs prácticos

```
# Lab 1 — safe scan of an owned /24 with explicit exclusion.
cat > exclude.conf <<EOF
10.0.0.1
10.0.0.254
EOF
sudo masscan 10.0.0.0/24 -p22,80,443 --rate 200 --excludefile exclude.conf -oJ lab.json
jq '.[].ports[] | "\(.port)/\(.proto)"' lab.json | sort -u
# What ports appear is the door list; feed those into Nmap next.
```

```
# Lab 2 — two-phase Masscan -> Nmap pipeline.
sudo masscan 10.0.0.0/24 -p1-65535 --rate 1000 -oG lab.gnmap
awk '/Host:/ {print $2}' lab.gnmap | sort -u > hosts.txt
awk '/Ports:/ {for(i=1;i<=NF;i++) if($i~/\/open\//) print $i}' lab.gnmap |
  cut -d/ -f1 | sort -un | paste -sd, - > ports.txt
nmap -Pn -sV -iL hosts.txt -p "$(cat ports.txt)" -oA lab.nmap
# Masscan finds doors, Nmap walks through them. This is the standard pipeline.
```

```
# Lab 3 — rate calibration on a lab link.
for R in 100 500 1000 5000 10000; do
  echo "===== rate=$R"
  sudo masscan 10.0.0.0/24 -p80 --rate $R -oG /dev/null 2>&1 | tail -3
done
# Watch ICMP destination-unreachable / packet loss as rate rises.
# The right --rate is the highest with no loss on the path, halved.
```

## Ejemplos prácticos

- **Actualización de superficie de ataque externa en bug bounty.** Masscan semanal sobre el AS completo de una organización a `--rate 1000`, output binario, diff contra el binario de la semana anterior. Los puertos nuevos aparecen inmediatamente para seguimiento con Nmap.
- **Recon interno durante red team.** Desde un foothold dentro de un /16, Masscan a `--rate 200` encuentra servicios internos alcanzables en minutos.
- **Port-sweep dirigido a ASes adquiridos.** El mapeo de exposición post-adquisición usa Masscan por AS con `--shard X/Y` a través de boxes de scan cloud para paralelismo.

## Notas relacionadas

- [[nmap-scanning|Nmap Scanning]]
- [[ports-and-services|Puertos y Servicios]]
- [[firewalls-and-network-boundaries|Firewalls y Límites de Red]]
- [[service-enumeration|Service Enumeration]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[active-recon|Active Recon]]
- [[scope-validation|Validación de Scope]]
- [[external-attack-surface|Superficie de Ataque Externa]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]

## Referencias

- **Docs Oficiales:** Masscan README and man page — https://github.com/robertdavidgraham/masscan
- **Investigación / Deep Dive:** Erratasec — Masscan: the entire internet in 3 minutes — https://blog.erratasec.com/2013/09/masscan-entire-internet-in-3-minutes.html
- **Investigación / Deep Dive:** Durumeric et al. — ZMap: Fast Internet-wide Scanning (USENIX Security 2013) — https://zmap.io/paper.pdf
