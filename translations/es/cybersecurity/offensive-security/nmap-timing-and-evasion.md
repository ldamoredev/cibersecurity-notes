# Nmap Timing and Evasion

## Definición

El Nmap timing and evasion es el uso de las primitivas de tasa, reintento, paralelismo y forma de paquete de Nmap para (a) reducir resultados `filtered` falsos contra redes con rate limiting o (b) testear qué capturará y qué no un IDS/IPS, WAF o firewall stateful.

## Por qué importa

El comportamiento por defecto de Nmap optimiza para precisión en una LAN tranquila. Los objetivos de internet en producción están detrás de rate limiters, middleboxes que dropean paquetes y thresholds por IP fuente — los valores por defecto producen resultados *incorrectos* ahí, no solo lentos. El uso senior maneja los dials de timing individuales explícitamente para que el output del scan sea repetible, comparable entre corridas y defendible en un reporte.

Las primitivas de evasión importan menos para esconderse (la inspección stateful moderna las neutraliza en su mayoría) y más como toolkit de diagnóstico: cada primitiva aísla una capa de inspección, así que una matriz de probes te dice exactamente qué control te capturó.

## Cómo funciona

El timing de Nmap es **5 dials** vestidos como una plantilla:

1. **Timeout por probe** (`--min-rtt-timeout`, `--max-rtt-timeout`, `--initial-rtt-timeout`) — cuánto esperar antes de declarar un probe perdido.
2. **Conteo de reintentos** (`--max-retries`) — cuántas veces reenviar un probe perdido antes de llamar el puerto `filtered`.
3. **Concurrencia** (`--min-parallelism`, `--max-parallelism`) — cuántos probes en vuelo mantiene Nmap.
4. **Tasa** (`--min-rate`, `--max-rate`) — piso/techo de paquetes-por-segundo, el dial más predecible.
5. **Espaciado** (`--scan-delay`, `--max-scan-delay`) — brecha determinística entre probes para derrotar los detectores de rate limiting.

Las plantillas `-T0` a `-T5` son combinaciones preestablecidas de esos 5 dials:

```
-T0 paranoid    5 min between probes        IDS evasion theatre
-T1 sneaky      15 s between probes         IDS evasion theatre
-T2 polite      0.4 s spacing, low rate     shared-network considerate
-T3 normal      Nmap default                LAN baseline
-T4 aggressive  fast, max-retries 6         what most tutorials use
-T5 insane      very fast, max-retries 2    accuracy starts dropping
```

El error en la mayoría de los engagements no es "el scan fue demasiado lento"; es "el scan fue rate-limited por un control upstream y Nmap silenciosamente reetiquetó puertos `open` como `filtered`."

## Técnicas / patrones

- Anclar **`--min-rate`** en lugar de `-T` para corridas reproducibles (ej. `--min-rate 100 --max-rate 300`).
- Detectar rate limiting con **dos corridas a diferentes tasas**: si el conteo de `filtered` sube bruscamente a tasas más altas, hay un rate limiter en el camino, no un firewall que bloquea el puerto directamente.
- Usar **`--scan-delay`** cuando un IDS se activa en N probes dentro de W segundos — el espaciado determinístico bajo el threshold supera el timing aleatorio.
- Usar **`--max-retries 1`** para descubrimiento rápido en primera pasada, luego reescanear solo puertos `open` y `open|filtered` con `--max-retries 6` y `-Pn`.
- **Source-port spoofing** (`--source-port 53`, `--source-port 88`) — muchas ACLs de firewall viejas confían en tráfico *desde* el puerto 53/88 para permitir retornos DNS/Kerberos. Todavía funciona en ACLs de perímetro mal configuradas en 2026.
- **`--badsum`** — detección de IDS: los OS reales dropean paquetes con checksum inválido, los motores IDS que no validan el checksum responden de todas formas y se delatan.
- **`--data-length N`** — varía el tamaño del payload del probe, derrotando reglas de firma que coinciden en longitud exacta.

## Variantes y bypasses

El uso senior se agrupa en **4 modos**.

### 1. Preciso contra rate limiters

Objetivo: obtener el estado `open` verdadero en un objetivo hardened. `nmap -Pn -sS --min-rate 200 --max-rate 500 --max-retries 3 -p- target`. Dials anclados, no manejados por plantilla.

### 2. Matriz de forma de paquete diagnóstica

Objetivo: descubrir qué capa de inspección capturó el scan. Correr la *misma* lista de puertos con `-f`, `--mtu 16`, `--data-length 200`, `--badsum`, `--source-port 53` y `-D RND:10` por separado. Cualquier variante que devuelve `open` revela qué inspecciona y qué no el middlebox.

### 3. Stealth desde logs (idle scan)

`nmap -sI zombie:port target` — la IP del scanner nunca aparece en los logs del objetivo. Requiere un host "zombie" con IPID globalmente incremental. La mayoría de OS modernos randomiza IPID; esta es ahora una técnica de nicho para entornos legacy.

### 4. Engaños de source-port y TTL

`--source-port 53` y `--ttl N` explotan ACLs stateless que confían en *source-port igual a 53* o *TTL igual al hop-count esperado*. Ambos son patrones legacy, ambos todavía aparecen en appliances viejos.

## Impacto

- **Falsos negativos** al usar `-T4` por defecto contra objetivos con rate limiting, perdiendo exposición real.
- **Detección del engagement** — un scan `-T5` activa la mayoría de IDS/WAFs modernos en segundos.
- **Blowback de scope** — `-D` con decoys aleatorios puede incluir IPs de terceros en scope como fuentes falsas, lo que algunos pipelines IDS escalan a quejas de abuso.
- **Interrupción de servicio** — `-T5 --min-rate 50000` contra un dispositivo embebido o servicio de bajo rendimiento puede colgarlo.

## Detección y defensa

1. **Inspección stateful más rate limiting por IP fuente.**
   La combinación derrota casi todos los trucos de stealth y timing de Nmap a la vez.

2. **Reglas IDS atadas a combinaciones de flags TCP.**
   `-sN`, `-sF`, `-sX`, `-sM` envían combinaciones de flags inválidas. Los rule sets por defecto de Snort/Suricata/Zeek las capturan de manera confiable.

3. **Detección de anomalías basada en distribución de la distribución de probes.**
   La entropía por IP fuente en destino-puerto × tiempo derrota la evasión por `--scan-delay` porque el *fingerprint* (una fuente tocando muchos puertos, aunque sea despacio) todavía es anómalo.

4. **Honeyports / tarpits.**
   Unos pocos puertos monitoreados que nunca deberían ver tráfico convierten cualquier scan externo en una alerta de alta confianza sin falsos positivos.

### Qué no funciona como defensa primaria

- **Esconder el perímetro** ("no estamos listados en DNS") — Masscan/Shodan igual te ven.
- **Supresión de banners** como control primario — reduce ruido en el output NSE, no explotabilidad.
- **Bloquear `-Pn`** dropeando ICMP echo — Nmap usa probes TCP cuando el ICMP está filtrado; no bloqueaste el descubrimiento, solo lo hiciste más lento.

## Labs prácticos

```
# Lab 1 — reveal rate limiting on an authorized target.
nmap -Pn -sS -p 1-1000 --min-rate 50 --max-rate 100 -oN slow.txt LAB
nmap -Pn -sS -p 1-1000 --min-rate 5000 --max-rate 5000 -oN fast.txt LAB
diff <(grep '^[0-9]' slow.txt) <(grep '^[0-9]' fast.txt)
# What ports moved from open -> filtered between runs is the rate-limit signature.
```

```
# Lab 2 — packet-shape diagnostic matrix on one open port.
PORT=443
for FLAG in "" "-f" "--mtu 16" "--data-length 200" "--badsum" "--source-port 53"; do
  echo "===== $FLAG"
  nmap -Pn -sS -p $PORT $FLAG LAB
done
# Whichever invocation still reports open tells you what the inspection device skipped.
```

```
# Lab 3 — confirm an IDS validates checksums.
nmap -Pn --badsum -p 80,443 LAB
# Real targets answer with nothing (OS drops invalid checksum). If you get RST/ACK,
# something on path is replying without validating the TCP checksum — an inline IDS.
```

```
# Lab 4 — idle scan against an authorized lab zombie.
sudo nmap -sn -PR LAB_NET                            # find candidate zombies
sudo nmap -sI ZOMBIE:80 -p 22,80,443,3389 TARGET     # only works if ZOMBIE has incrementing IPID
# Verify with: nmap -O ZOMBIE  -> look for "IP ID Sequence Generation: Incremental".
```

```
# Lab 5 — `--scan-delay` to evade per-source connection-rate IDS.
sudo nmap -Pn -sS -p 22,80,443,3389 --scan-delay 2s --max-retries 1 LAB
# Compare alert count in IDS console with and without --scan-delay 2s.
```

## Ejemplos prácticos

- **Engagement externo contra app con CDN frontal.** `-T4` por defecto devuelve todos los puertos `filtered`; anclar `--min-rate 50 --max-rate 100` revela puertos abiertos reales detrás del rate limit por IP del CDN.
- **Rescan de assets en bug bounty.** `nmap -Pn -sS --min-rate 200 -p- ASN-IP-LIST` trimestral con flags de timing fijos permite diff de exposición entre trimestres sin ruido de timing.
- **Paridad lab vs producción.** Los mismos flags de scan contra staging y producción revelan que el WAF de staging está configurado diferente al de prod — un hallazgo real recurrente.
- **Detección de un IDS transparente.** Un probe `--badsum` a un puerto cerrado conocido que devuelve RST/ACK es un indicador limpio de inspección inline que no valida checksums.

## Notas relacionadas

- [[nmap-scanning|Nmap Scanning]]
- [[ports-and-services|Puertos y Servicios]]
- [[firewalls-and-network-boundaries|Firewalls y Límites de Red]]
- [[host-and-port-discovery|Descubrimiento de Hosts y Puertos]]
- [[active-recon|Active Recon]]
- [[cloaking-and-security-evasion|Cloaking and Security Evasion]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de Anomalías de Scan y Análisis de Fingerprint]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]

## Referencias

- **Docs Oficiales:** Nmap Reference Guide — Timing and Performance — https://nmap.org/book/man-performance.html
- **Docs Oficiales:** Nmap Reference Guide — Firewall/IDS Evasion and Spoofing — https://nmap.org/book/man-bypass-firewalls-ids.html
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
