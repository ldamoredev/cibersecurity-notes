# Idle Scan and IPID Side Channels

## Definición

Un **idle scan** (`nmap -sI zombie:port target`) infiere el estado de puertos de un objetivo sin enviar un solo paquete desde la IP real del atacante. Funciona explotando un **contador IPID predecible** en un host "zombie" de terceros: el atacante sondea el IPID actual del zombie, envía un SYN spoofed al objetivo *como si viniera del zombie*, y luego vuelve a sondear el IPID del zombie. El delta revela si el objetivo respondió — y a quién. Los **IPID side channels** son la familia más amplia de ataques de inferencia que usan el campo de identificador IP de cualquier host como contador observable para derivar información que el atacante no puede ver directamente.

## Por qué importa

El idle scan es el único scan de Nmap donde la IP del scanner **nunca aparece en los logs del objetivo**. Todos los demás scans — incluso `-sN`, `-sF`, `-D RND:10` — emiten paquetes desde la fuente real. Los decoys aumentan el ruido; la fuente sigue estando. El idle scan es estructuralmente diferente: el objetivo solo ve tráfico del zombie. Para la evasión de atribución de fuente esto es único.

También importa como nota educativa porque enseña **tres ideas transferibles de nivel senior**:

- **Los contadores predecibles filtran información.** Cualquier contador que se incrementa globalmente (IPID, TCP ISN con RNGs débiles, ciertos contadores SNMP) es un oráculo de side channel. La vulnerabilidad es la predecibilidad, no el protocolo.
- **Los supuestos de confianza se apilan.** El idle scan asume (a) que el zombie responde consistentemente, (b) que el objetivo confía en la IP fuente del zombie, (c) que el zombie está suficientemente quieto para que la inferencia por delta sea confiable. Cada supuesto es su propia superficie de ataque.
- **Las defensas son cambios en la especificación del protocolo.** La guía a nivel RFC para randomizar IPID neutralizó el idle scan clásico en todos los sistemas operativos principales. El pensamiento senior trata el *campo del protocolo* como la superficie de ataque, no la herramienta.

El idle scan hoy es principalmente **diagnóstico** en lugar de operacional — la randomización de IPID en OS modernos lo derrota en Linux, OpenBSD, Windows moderno y la mayoría de workloads cloud. Pero los dispositivos IoT, sistemas embebidos legacy y gateways NAT mal configurados todavía incluyen generadores de IPID que se incrementan globalmente, y la técnica sigue siendo una forma limpia de *probar* que un entorno es más viejo de lo que sus operadores afirman.

## Cómo funciona

El idle scan se reduce a **3 round-trips** y **una observación de un bit**:

1. **Sondear el IPID actual del zombie.** El atacante envía un SYN-ACK no solicitado al zombie. El zombie responde con RST, portando IPID = N.
2. **Spoof de un SYN al objetivo desde la IP del zombie.** El objetivo recibe un SYN que parece venir del zombie.
   - Si el puerto objetivo está **abierto**: el objetivo responde SYN-ACK al zombie. El zombie no esperaba esto, así que responde con RST — *e incrementa su IPID*. El IPID del zombie es ahora N+1.
   - Si el puerto objetivo está **cerrado**: el objetivo responde RST al zombie. El zombie descarta el RST no solicitado y *no envía ningún paquete*. El IPID del zombie se queda en N.
3. **Volver a sondear el IPID del zombie.** El atacante envía otro SYN-ACK no solicitado. El zombie responde con RST, portando su IPID actual:
   - **N+2** (empezó en N, se incrementó una vez en el paso 2, se incrementó ahora) → el puerto estaba **abierto**.
   - **N+1** (sin incremento del paso 2, solo este probe) → el puerto estaba **cerrado**.

Una invocación representativa:

```
# 1) Find a candidate zombie — must have INCREMENTAL IPID.
sudo nmap -O ZOMBIE_CANDIDATE | grep -i 'ip id sequence'
# Look for: "IP ID Sequence Generation: Incremental"

# 2) Run the idle scan.
sudo nmap -Pn -sI ZOMBIE:80 -p 22,80,443,3389 TARGET
# Target sees traffic from ZOMBIE only. Your IP appears nowhere in the target's logs.
```

El error no es "Nmap puede hacer spoof de IPs fuente" (eso siempre fue posible); el error es *el contador IPID del host de terceros es un side channel medible que filtra la response del objetivo — y es observable para cualquiera que pueda sondear al tercero*.

## Técnicas / patrones

- **La selección del zombie es todo el engagement.** Un buen zombie tiene: (a) `IP ID Sequence Generation: Incremental` según `nmap -O`, (b) bajo tráfico para que el delta IPID sea exactamente +2 o +1 (los zombies ocupados avanzan múltiples veces entre probes, produciendo ruido), (c) alcanzabilidad de red al objetivo en los puertos relevantes.
- **Verificá el comportamiento IPID del zombie antes de escanear.** `nmap -O` es el primer movimiento; si el resultado es `Random` o `Randomized`, ese zombie es inútil.
- **El IoT moderno y las impresoras son la fuente típica de zombie.** Los stacks de red embebidos frecuentemente todavía usan IPID incremental global. Impresoras de red, switches KVM, timbres inteligentes, controladores industriales e interfaces de gestión fuera de banda son candidatos recurrentes.
- **El idle scan es lento.** Cada puerto requiere múltiples round-trips. Práctico para confirmar exposición en unos pocos puertos de alto valor; impráctico para scans de rango completo `-p-`.
- **`--proxies` no es lo mismo.** `nmap --proxies` encadena proxies HTTP/SOCKS y reescribe la fuente en la capa del proxy — útil para alcanzabilidad, inútil para evasión (el proxy igual te registra). El idle scan elimina la fuente de los *logs del objetivo*.
- **OPSEC: la detección vive en el zombie, no en el objetivo.** Un defensor que controla el zombie puede correlacionar tres cosas: saltos de IPID que no coinciden con el tráfico saliente, SYN-ACKs no solicitados desde tu IP, y responses no solicitadas llegando desde el objetivo.

## Variantes y bypasses

La familia de IPID side channel tiene **4 variantes importantes**.

### 1. Idle scan clásico (Nmap `-sI`)

El flujo descrito arriba. Requiere un zombie con IPID incremental alcanzable tanto desde el atacante como desde el objetivo. La variante del libro de texto, cada vez más difícil de ejecutar contra OS modernos.

### 2. Idle scan por destino IPID

Linux (desde 2014) usa un contador IPID *por par de destinos* en lugar de uno global. El idle scan clásico no funciona directamente, pero una variante refinada usa el IPID del par *zombie-a-objetivo* como oráculo. Frágil pero documentado en literatura académica.

### 3. TCP shared-state side channels

Más allá del IPID, ciertos campos TCP (ISN bajo RNGs débiles, contadores de challenge ACK, estado de rate limit basado en conteo de paquetes) pueden filtrar el estado del objetivo a un observador tercero. **Ensafi et al. (USENIX 2015)** demostró detección de drops intencionales de paquetes en internet usando estas primitivas.

### 4. Inferencia de mapeo NAT vía IPID

Un gateway NAT que traduce muchos hosts internos a una IP externa frecuentemente comparte un único contador IPID entre ellos. Sondear el IPID externo y observar la tasa de avance revela aproximadamente cuántos hosts internos están activos.

## Impacto

Ordenado por severidad real típica:

- **Evasión de atribución de fuente que sobrevive la revisión forense.** Los packet captures y logs del objetivo contienen solo el zombie. Las investigaciones persiguen primero al dueño del zombie; el atacante real es invisible a menos que el zombie mismo sea capturado y sus propios logs analizados.
- **Inferencia de relaciones de confianza.** Si el zombie es *confiable* para el objetivo (ACL de firewall permite ZOMBIE → TARGET:N pero bloquea internet en general), el idle scan revela exposición que ningún scan directo desde internet encontraría.
- **Estimación de población NAT.** Inteligencia tipo censo sobre la escala interna de una organización, filtrada a través de contadores IPID del perímetro.
- **Falsa confianza en la visibilidad del defensor.** Los defensores que dicen "monitoreamos cada conexión" tienen razón sobre el objetivo; se pierden los idle scans completamente si su telemetría es solo del lado del objetivo.
- **Uso operacional limitado hoy.** La mayoría de OS de producción randomiza IPID. La técnica es *educativa* y *específica para objetivos legacy*.

## Detección y defensa

Ordenado por efectividad:

1. **Usá un kernel que randomiza IPID por destino o por paquete.**
   Linux 4.1+, macOS moderno, FreeBSD, OpenBSD, Windows 10/Server 2016+ lo hacen por defecto. El arreglo estructural que termina con el idle scan clásico como ataque útil contra OS modernos.

2. **Egress filtering y verificación de dirección fuente (BCP 38).**
   El idle scan requiere que el atacante haga spoof de la IP fuente del zombie. Las redes que aplican filtrado de ingreso hacen el spoof imposible. RFC 2827 / BCP 38 fue especificado en 2000 y todavía se despliega inconsistentemente.

3. **Detección conductual del lado del zombie.**
   El zombie ve tres anomalías: (a) SYN-ACKs no solicitados desde el atacante, (b) responses RST o SYN-ACK no solicitadas desde el objetivo, (c) su propio IPID avanzando sin coincidir con tráfico saliente de aplicaciones.

4. **IPID por destino para cualquier stack de red custom.**
   Los fabricantes de dispositivos IoT, sistemas embebidos y stacks de red custom frecuentemente heredan el mismo bug de IPID incremental.

5. **Monitoreo de flujo de red a nivel de red en el perímetro.**
   La detección en el perímetro captura una firma diferente: el SYN spoofed llega desde una fuente que normalmente no se comunica con el objetivo en ese puerto.

### Qué no funciona como defensa primaria

- **Solo logging del host objetivo.** El idle scan fue diseñado para derrotar esto.
- **Reglas de firewall que bloquean patrones "tipo scan".** El idle scan es un SYN por puerto, distribuido al ritmo que elija el atacante.
- **TLS / cifrado.** El idle scan opera en L3/L4. TLS es irrelevante.
- **Geo-blocking del país del zombie.** Si el zombie está en red o cerca de ella, el geo-blocking bloquea tráfico legítimo o falla en aplicarse.

## Labs prácticos

Corré **únicamente** contra entornos de lab propios o engagements autorizados.

```
# Lab 1 — Find a candidate zombie in a lab subnet.
sudo nmap -O 10.0.0.0/24 2>/dev/null |
    awk '/Nmap scan report/{ip=$NF} /IP ID Sequence Generation: Incremental/{print ip}'
# Output: every host with incremental IPID is a candidate zombie.
```

```
# Lab 2 — Verify a specific zombie's IPID behavior in detail.
sudo nmap -O ZOMBIE | grep -A1 "IP ID Sequence"
# Expected: "IP ID Sequence Generation: Incremental"
# If you see "Random" or "Randomized", this zombie cannot be used.
```

```
# Lab 3 — Run an idle scan against an authorized lab target.
sudo nmap -Pn -sI ZOMBIE:80 -p 21,22,80,443,3389,8080 TARGET
# The target's packet capture will show ZOMBIE as the source.
# Verify by running tcpdump on TARGET during the scan.
```

```
# Lab 4 — Confirm the source-attribution property from TARGET's perspective.
# On TARGET:
sudo tcpdump -i any -nn "host ATTACKER_REAL_IP or host ZOMBIE" -c 50
# Expected: zero packets to/from ATTACKER_REAL_IP, many packets to/from ZOMBIE.
```

```
# Lab 5 — Defender lab: detect being used as a zombie.
# On the ZOMBIE host:
sudo tcpdump -i any -nn 'tcp and ((tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack != 0) or (tcp[tcpflags] & tcp-rst != 0))' -c 200
# Look for: SYN-ACK or RST packets arriving from the TARGET that do not correspond
# to any outbound connection your host initiated. That is the zombie-side signature.
```

```
# Lab 6 — IPID-based NAT-population inference (educational, against owned NAT).
# Probe the NAT external IP repeatedly and watch IPID advance.
for i in $(seq 1 20); do
  sudo hping3 -c1 -S -p 80 NAT_EXTERNAL_IP 2>/dev/null |
      grep -oP 'id=\K\d+'
  sleep 1
done
# If IPID advances by more than ~1 between samples, the NAT is sharing the counter
# across multiple internal hosts — the rate of advance approximates the active host count.
```

## Ejemplos prácticos

- **Engagement contra red industrial legacy.** El perímetro tiene ACLs estrictas pero confía en una impresora de red del año 2010 en la misma subred. El idle scan con la impresora como zombie revela puertos que el scan directo desde internet reporta como `filtered`.
- **Ejercicio forense posterior a un scan de perímetro.** El equipo defensor ve tráfico de scan aparentemente desde `printer-3F-001`. La investigación revela que el IPID de la impresora avanzó inconsistentemente con su tráfico saliente durante la ventana de scan.
- **Objetivo Linux moderno — el idle scan falla.** Mismo engagement, pero el objetivo es un host Linux 5.x. El generador IPID por destino significa que la técnica clásica no funciona; el operador cae en `-sS` ordinario y acepta el costo de atribución.
- **Censo NAT durante pre-engagement recon.** Sondear la IP de perímetro de una organización revela que el contador IPID avanza aproximadamente 50 unidades por minuto, sugiriendo ~30-50 hosts internos activos en el momento de la medición.

## Notas relacionadas

- [[nmap-timing-and-evasion|Nmap Timing and Evasion]] — primitivas más amplias de timing/evasión; el idle scan es el caso más profundo de la pregunta de evasión de atribución.
- [[packet-fragmentation-and-decoy-scans|Packet Fragmentation and Decoy Scans]] — familia hermana de evasión; los decoys oscurecen la atribución por ruido, el idle scan la elimina por mecanismo.
- [[tcp-ip-basics|Fundamentos de TCP/IP]] — el campo de identificador IP que usa este ataque.
- [[nmap-scanning|Nmap Scanning]] — estrategia de scan más amplia en la que encaja.
- [[packet-analysis|Análisis de Paquetes]] — la herramienta correcta para verificar el flujo de paquetes zombie/objetivo durante un lab.
- [[attacker-defender-duality-as-a-learning-tool|Dualidad Atacante-Defensor como Herramienta de Aprendizaje]] — el idle scan es un ejemplo limpio de un ataque cuyas defensas son cambios en la especificación del protocolo, no reglas perimetrales.

## Referencias

- **Docs Oficiales:** Nmap Reference Guide — Idle Scan — https://nmap.org/book/idlescan.html
- **Investigación / Deep Dive:** Antirez (Salvatore Sanfilippo) — Dumb scan / new TCP scan method (disclosure original de 1998 en Bugtraq) — https://seclists.org/bugtraq/1998/Dec/79
- **Investigación / Deep Dive:** Ensafi et al. — Detecting Intentional Packet Drops on the Internet via TCP/IP Side Channels (USENIX Security 2015) — https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/ensafi
