# Run External Recon Scan Pipeline

## Objetivo

Mapear puertos abiertos, servicios y exposición de versiones de un objetivo autorizado (host único, subnet o BGP AS) usando un pipeline de dos fases Masscan → RustScan/Nmap-NSE, con timing reproducible, exclude-list obligatorio y output estructurado que diffee limpio entre corridas.

## Supuestos

- existe autorización escrita (scope de engagement, policy de bug bounty o lista de assets propios) y cubre cada IP/CIDR que aparecerá en include list
- la scan box tiene IP fuente estable y link upstream limpio
- el objetivo es recon de amplitud-luego-profundidad, no explotación
- Nmap, Masscan, RustScan, `jq` y `whois` están instalados y actualizados

## Prerrequisitos

- `INCLUDE.txt` — objetivos autorizados (un CIDR/IP/host por línea)
- `EXCLUDE.txt` — IPs fuera de scope, integraciones de partners, infra de monitoreo, rangos RFC 5737 si aplica
- valor `--adapter-ip` que coincide con la IP fuente enrutable real de la scan box
- `nmap --script-updatedb` corrido en los últimos 30 días
- shell `ulimit -n 65535` disponible (o usar la imagen Docker de RustScan)

## Pasos de recon

> *Script runnable de referencia:* `cybersecurity/security-playbooks/run-scan-pipeline.sh` empaqueta las Fases 1–2 de abajo en un script shell. Usalo con env vars `INCLUDE_FILE`, `EXCLUDE_FILE` y `ADAPTER_IP`; el script se niega a correr si `EXCLUDE_FILE` está vacío y pide un `YES` explícito antes de escanear salvo que pases `--yes`. Fase 0 (gate de autorización) y Fase 3 (matriz diagnóstica de packet-shape) quedan como pasos human-in-the-loop y no se automatizan.

> *Par defensor:* [[detect-external-scan-pipeline|Detectar pipeline de scan externo]] es el espejo defender-side de este playbook — leé ambos juntos según [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]].

### Fase 0 — Gate de autorización

1. Imprimí scope y exclude list textualmente y confirmá contra el documento del engagement.
2. `cat INCLUDE.txt EXCLUDE.txt` — verificá visualmente antes de que salga cualquier paquete.
3. Si los objetivos son a nivel AS, expandí el AS a prefixes primero:
   `bash
   whois -h whois.radb.net -- "-i origin AS<NUMBER>" |
     awk '/^route:/ {print $2}' | sort -u > INCLUDE.txt`

### Fase 1 — Amplitud (Masscan)

1. Echo-validá la config de Masscan antes de escanear:
   `bash
   sudo masscan --excludefile EXCLUDE.txt -iL INCLUDE.txt \
        -p1-65535 --rate 1000 --adapter-ip <YOUR_IP> --echo > masscan.conf
   less masscan.conf   # eyeball the merged include/exclude`

2. Calibrá `--rate` en una porción mínima primero (`-p80` en un /24) y observá ICMP-unreachable / spikes de pérdida. Seteá la tasa real a ~½ de la tasa limpia más alta.
3. Corré el scan con output binario para re-parsing sin pérdida:
   `bash
   sudo masscan -c masscan.conf -oB scan.bin`

4. Convertí a JSON para tooling downstream:
   `bash
   sudo masscan --readscan scan.bin -oJ scan.json
   jq -r '.[] | "\(.ip):\(.ports[0].port)"' scan.json | sort -u > openports.txt`

5. Si se interrumpe, retomá con `sudo masscan --resume paused.conf` — nunca reinicies desde cero.

### Fase 2 — Profundidad (RustScan → Nmap NSE)

1. Agrupá output de Masscan por host para que Nmap corra una vez por host con la lista de puertos de ese host:
   `bash
   awk -F: '{ports[$1]=ports[$1]","$2} END {for (h in ports) print h, substr(ports[h],2)}' openports.txt > hostports.txt`

2. Corré Nmap con version detection y una categoría NSE conservadora:
   `bash
   while read host ports; do
     sudo nmap -Pn -sS -sV -sC \
          --script "(default or vuln) and not (intrusive or dos or brute)" \
          --min-rate 100 --max-rate 300 --max-retries 3 \
          -p "$ports" -oA "nmap/$host" "$host"
   done < hostports.txt`

3. Para deep scans de host único donde no hace falta escala Masscan, sustituí RustScan como capa de discovery:
   `bash
   rustscan -a <HOST> --ulimit 5000 -- -sV -sC \
       --script "(default or safe or vuln) and not (intrusive or dos or brute)" \
       --min-rate 100`

4. Si un objetivo parece rate-limited, fijá `--min-rate 50 --max-rate 100` y repetí solo ese host.

### Fase 3 — Matriz diagnóstica de packet-shape (opcional)

Corré solo cuando Fase 2 reporta todo como `filtered` pese a exposición esperada. Elegí un puerto supuestamente abierto y probá cada primitiva de evasión por separado para fingerprinting de la capa de inspección:

```
PORT=443; HOST=<TARGET>
for FLAG in "" "-f" "--mtu 24" "--data-length 200" "--badsum" "--source-port 53"; do
  echo "===== $FLAG"
  sudo nmap -Pn -sS -p $PORT $FLAG "$HOST"
done
```

La invocación que devuelva `open` revela qué inspecciona y qué no el middlebox; esa intel guía la fase siguiente.

## Pasos de exploit / testing

Este playbook se detiene intencionalmente en enumeración. Los hallazgos validados van a:
- playbooks de explotación por clase de servicio (`exploit-sqli`, `break-jwt-validation`, `inspect-file-upload-surface`, etc.)
- `cybersecurity/offensive-security/service-validation` para inspección manual de servicios
- `cybersecurity/offensive-security/recon-to-testing-handoff` para handoff de engagement

## Señales de validación

- puertos `open` aparecen igual entre corridas Masscan y Nmap
- banners de versión son consistentes entre NSE scripts (`-sV`, `http-server-header`, `ssl-cert`)
- conteos `filtered` bajan cuando baja `--min-rate`
- un probe `--badsum` que devuelve `RST/ACK` confirma IDS inline que no valida checksums
- diff contra la corrida previa muestra puertos/servicios nuevos

## Mitigación

Del lado defensor, controles correctos contra este pipeline:
- alerting per-source-IP de tasa SYN en el perímetro
- reglas IDS atadas a fan-out y TCP fingerprint
- reassembly de fragmentos IP habilitado en IDS
- honeyports/tarpits en puertos nunca usados
- version-banner shaping

## Logging / detección

- una IP fuente golpeando > N IPs destino distintas en un puerto dentro de 60 s
- una IP fuente probando > 100 puertos distintos en un host dentro de 60 s
- patrones de probe específicos de NSE en rulesets IDS
- estabilidad de TCP fingerprint por fuente a través de IPs "distintas"
- joins proceso-red EDR que atan scanner behavior a `nmap`, `masscan`, `rustscan`, `python`, `powershell` o binarios renombrados

## Seguridad operacional

- **nunca** uses IPs reales de terceros como decoys `-D`; preferí rangos RFC 5737 (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`)
- **nunca** escanees por encima de `--rate 1000` en un link upstream compartido sin medir pérdida primero
- **nunca** corras categorías NSE `intrusive`, `exploit`, `dos` o `brute` sin autorización escrita explícita
- **siempre** mantené `EXCLUDE.txt` no-overridable
- **siempre** escribí output binario para cualquier scan de más de cinco minutos

## Notas relacionadas

- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[nmap-scanning|Nmap Scanning]]
- [[host-and-port-discovery|Host and Port Discovery]]
- [[service-validation|Service Validation]]
- [[scope-validation|Scope Validation]]
- [[recon-to-testing-handoff|Recon to Testing Handoff]]
- [[external-attack-surface|External Attack Surface]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[detection-evasion-myths-and-modern-limitations|Mitos de evasión de detección y limitaciones modernas]]
- [[attack-path-correlation-and-kill-chain-observability|Correlación de attack paths y observabilidad de kill chain]]

## Referencias

- **Official Tool Docs:** Nmap Reference Guide — Timing and Performance — https://nmap.org/book/man-performance.html
- **Official Tool Docs:** Masscan README — https://github.com/robertdavidgraham/masscan
- **Official Tool Docs:** RustScan repository and docs — https://github.com/RustScan/RustScan
- **Investigación / Deep Dive:** ProjectDiscovery Reconnaissance 103 — Host and Port Discovery — https://projectdiscovery.io/blog/reconnaissance-series-3-host-and-port-discovery
