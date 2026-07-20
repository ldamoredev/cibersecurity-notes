# Detect External Recon Scan Pipeline

## Objetivo

Detectar a un operador externo corriendo un pipeline de recon de dos fases Masscan → Nmap-NSE (el playbook ofensivo [[run-scan-pipeline|Run External Recon Scan Pipeline]]) contra tu perímetro, con fidelidad suficiente para identificar fuente, scope e intención en minutos — antes de que los hallazgos de la fase de profundidad se conviertan en explotación posterior.

## Supuestos

- tenés **al menos uno** de: recolección NetFlow/IPFIX en el perímetro, Suricata/Zeek/Snort en el span port perimetral o logs de firewall perimetral con conteos de conexión por fuente
- tus reglas perimetrales bloquean al menos IPs known-bad y podés hot-blockear una IP fuente nueva en minutos
- el objetivo es **detectar, identificar, contener** — no exploit-block; prevenir el scan por completo es imposible contra un operador determinado con control de su scan box

## Prerrequisitos

- collector NetFlow/IPFIX (nfdump, FastNetMon, Plixer o procesamiento en SIEM de exports Cisco/Juniper/pfSense)
- motor IDS — Suricata o Zeek en el perímetro, con ruleset comunitario actualizado
- baseline de tráfico perimetral "normal": tasas de conexión por fuente, puertos destino comunes, integraciones de partners que hacen fan-out legítimo
- runbook de incident response con al menos tres caminos de contacto (analista SOC, network engineer, security on-call)
- opcional: honeyports / tarpits en puertos nunca usados — detección asimétrica de alta confianza

## Pasos de detección

> *Este playbook es el espejo defender-side de [[run-scan-pipeline|Run External Recon Scan Pipeline]]. Cada fase abajo se empareja con la fase del mismo número en el playbook ofensivo. Leelos juntos.*

### Fase 0 — Baseline (hacer una vez, refrescar trimestralmente)

1. Capturá un baseline de 7 días de tráfico perimetral. Registrá tasas de flow por fuente, top 100 source IPs, puertos destino distintos por fuente, protocolos comunes.
2. Identificá fuentes legítimas de fan-out: vendors de monitoreo, proyectos de medición de internet (Censys, Shodan, BinaryEdge, internetdb), partners autorizados, tu propio scanning externo si hacés monitoreo continuo de superficie.
3. Allowlisteá fuentes legítimas de fan-out en tus reglas de alerta. Sin esto, el baseline queda envenenado por ruido rutinario de internet y cada alerta es un falso positivo.

### Fase 1 — Detectar fase de amplitud (firma Masscan / Zmap)

Firma del operador: **una IP fuente emite miles de SYNs contra muchos destinos distintos en segundos**, normalmente con fingerprint TCP no-default.

1. **Regla NetFlow (mayor sensibilidad).** Alertar cuando una fuente produce flows a ≥ 100 IPs destino distintas en 60 s. Tuneá el threshold a tu baseline; algunos entornos necesitan 1000+.
   `text
   # nfdump example
   nfdump -R /var/log/flow -t 2026-05-11/14:00:00-2026-05-11/14:01:00 \
     -A srcip -O bytes -o "fmt:%sa %fl %byt" |
     awk '$2 > 100 {print}'`

2. **Firma Suricata para SYN fan-out.**
   `text
   alert tcp $EXTERNAL_NET any -> $HOME_NET any \
     (msg:"Mass SYN fan-out (Masscan-like)"; flow:to_server; flags:S;
      threshold:type both, track by_src, count 100, seconds 60;
      classtype:network-scan; sid:9000001; rev:1;)`

3. **Correlación de fingerprint TCP.** Si múltiples alertas disparan desde IPs "distintas" en la misma ventana, capturá paquetes completos y compará fingerprints TCP (window size, MSS, orden de options). Fingerprints idénticos a través de fuentes "distintas" confirman evasión de atribución basada en decoys ([[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]) — clusterizá como un actor.

### Fase 2 — Detectar fase de profundidad (Nmap + NSE)

Firma del operador: **una IP fuente prueba muchos puertos distintos en uno o pocos hosts en ~60 s**, con payloads de probe específicos de NSE que matchean reglas comunitarias Suricata/Snort.

1. **Alerta de port fan-in por host.** Alertar cuando una fuente toca ≥ 100 puertos distintos en un destino dentro de 60 s.
2. **Firmas de probes NSE.** Suscribite a Emerging Threats o ruleset comunitario de Suricata; ambos traen firmas para payloads NSE comunes (`http-shellshock`, `smb-vuln-ms17-010`, `ssl-poodle`, etc.). Actualizá semanalmente.
3. **Firma de banner grab `-sV`.** Version detection de Nmap manda una secuencia específica de payloads. La regla Suricata `2010493` o equivalente detecta la secuencia canónica `-sV`.
4. **Correlación EDR network-to-process.** Si tenés EDR en hosts internet-facing, alertá cuando la misma fuente de Fase 1 también haga probes profundos por puerto y el EDR del host destino vea la conexión sin actividad app-level posterior. La combinación es una firma Nmap de alta confianza.

### Fase 3 — Detectar intentos de evasión

Firma del operador: **probes fragmentados, decoy traffic, source-port spoofing (`--source-port 53`), paquetes `--badsum` o evasión de atribución idle-scan**.

1. **Alertas de reassembly de fragmentos.** Suricata/Zeek con `stream.reassembly` habilitado reensambla probes fragmentados antes del signature matching; el hecho de que un probe llegue fragmentado ya es una anomalía alertable para tráfico externo.
2. **Detección `--badsum`.** Paquetes con checksums TCP/IP inválidos enviados a hosts perimetrales. Los OS reales los dropean; el probe también es visible como paquete malformado en el perímetro.
3. **Source-port spoofing.** Alertar sobre tráfico entrante con puerto fuente 53 (DNS) u 88 (Kerberos) hacia puertos destino no-DNS/no-Kerberos. ACLs stateless legacy a veces confían en esos source ports.
4. **Detección zombie-side de idle scan.** Si tus hosts se usan como zombies para un idle scan, el host muestra SYN-ACKs no solicitados del operador + responses no solicitadas del objetivo + contador IPID avanzando sin tráfico app saliente correspondiente.

## Pasos de investigación / respuesta

Cuando dispara una alerta de Fase 1 o 2:

1. **Capturá paquetes completos de la fuente por 5 minutos.**
   `text
   sudo tcpdump -i $PERIMETER_IFACE -w /tmp/scan-$(date +%s).pcap \
       -s 0 'host SOURCE_IP' &
   sleep 300; sudo pkill -P $! tcpdump`

2. **Identificá la huella del operador.** Corré `p0f` o fingerprint logging de Suricata contra la captura para extraer fingerprint TCP, JA3/JA4 TLS y User-Agent si hay HTTP banner-grab.
3. **WHOIS / atribución ASN.** Identificá ASN de la fuente y atribución conocida de scanner. ¿Allowlisted? Frená ahí. ¿Desconocido? Continuá.
4. **Hot-block en el perímetro** si la fuente es desconocida y no está en allowlist de scanners legítimos. Documentá el bloqueo en ticket IR.
5. **Chequeá actividad correlacionada.** ¿La misma fuente tocó admin panels, login pages o API endpoints en las últimas 24 horas? Pivot a web/API logs.
6. **Abrí ticket IR** con: IP fuente, ASN, firma de scan, estado bloqueado/no bloqueado, path de packet capture completo, hallazgos de pivots.

## Señales de validación

- **Scan de alta confianza:** ≥ 100 destinos o puertos distintos desde una fuente en ≤ 60 s, sin baseline previo de esa fuente.
- **Atribución por decoys confirmada:** fingerprints TCP idénticos en IPs fuente "distintas" en la misma ventana.
- **Banner-grab follow-up confirmado:** la misma fuente que disparó Fase 1 también disparó Fase 2 contra un subset de destinos interesantes.
- **Idle scan contra vos como objetivo:** logs del host objetivo muestran sesión limpia desde una IP tercera conocida; capturá paquetes y chequeá avance IPID.
- **Vos como zombie confirmado:** el IPID de tu host avanzó N unidades durante una ventana donde emitió solo ~N/2 outbound flows.

## Mitigación / remediation

Controles durables del lado defensor:

- **Alerting de tasa SYN por source-IP** en el perímetro — derrota Masscan en segundos.
- **Clustering comportamental** (fan-out + TCP fingerprint) — derrota decoys.
- **Reassembly de fragmentos IP habilitado en IDS** — derrota evasión `-f`/`--mtu`.
- **Generación IPID per-destination en hosts internet-facing** — derrota idle scan clásico.
- **Version-banner shaping** — sube falsos positivos de NSE `vuln` y baja señal atacante.
- **Honeyports / tarpits en puertos nunca usados** — toda conexión externa es alerta de alta confianza.
- **Reducir superficie real de ataque** — alertar sobre scans es monitoreo; defensa durable es reducir servicios expuestos.

### Qué no funciona como defensa primaria

- **Bloquear por IP fuente después del hecho** — Masscan termina su barrido en segundos.
- **Geo-blocking** — los operadores rotan VPS en cualquier país trivialmente.
- **Confiar en "sin alerta" como evidencia de seguridad** — `-T2`, `--scan-delay`, idle scan o queries selectivas pueden volar bajo reglas threshold-only.
- **Contar hits individuales de puertos como alertas** — internet-facing hosts reciben hits constantes. Alertá sobre fan-out y fan-in, no conteos raw.

## Logging / forensics

- **Retener flow logs perimetrales ≥ 90 días.** Los operadores suelen scanear, esperar una semana y volver a explotar.
- **Retener packet captures completos de cualquier fuente alertada ≥ 30 días.** Soportan análisis de fingerprint TCP, JA3/JA4 y clustering de decoys.
- **Taggear cada alerta con:** IP fuente, ASN fuente, hash de fingerprint TCP, JA3 si aplica, estado allowlist, estado bloqueado.
- **Cross-reference con [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan]]** para el framing conceptual.

## Seguridad operacional

- **nunca** auto-bloquees una fuente cuyo ASN pertenece a organizaciones conocidas de medición/research sin revisión manual
- **nunca** dependas de una sola capa de detección
- **siempre** mantené actualizado semanalmente el ruleset IDS
- **siempre** testeá las reglas contra un lab interno autorizado corriendo [[run-scan-pipeline|Run External Recon Scan Pipeline]]
- **siempre** baseliná primero

## Notas relacionadas

- [[run-scan-pipeline|Run External Recon Scan Pipeline]]
- [[nmap-timing-and-evasion|Nmap Timing and Evasion]]
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]]
- [[masscan-internet-scale-scanning|Masscan Internet-Scale Scanning]]
- [[rustscan-and-nse-pipeline|RustScan and NSE Pipeline]]
- [[idle-scan-and-ipid-side-channels|Idle Scan and IPID Side Channels]]
- [[nse-vuln-category-audit|NSE vuln Category Audit]]
- [[scan-anomaly-detection-and-fingerprint-analysis|Detección de anomalías de scan y análisis de fingerprint]]
- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[ids-ips-and-behavioral-detection-pipelines|Pipelines de IDS/IPS y detección de comportamiento]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[attacker-defender-duality-as-a-learning-tool|Dualidad atacante-defensor]]

## Referencias

- **Fundamental:** MITRE ATT&CK T1595 — Active Scanning — https://attack.mitre.org/techniques/T1595/
- **Fundamental:** MITRE D3FEND — Network Traffic Analysis — https://d3fend.mitre.org/technique/d3f:NetworkTrafficAnalysis/
- **Official Tool Docs:** Suricata rules documentation — https://docs.suricata.io/en/latest/rules/
- **Official Tool Docs:** Zeek scan.log and notice framework — https://docs.zeek.io/en/master/scripts/policy/protocols/conn/known-services.zeek.html
- **Investigación / Deep Dive:** David Bianco — The Pyramid of Pain — https://detect-respond.blogspot.com/2013/03/the-pyramid-of-pain.html
