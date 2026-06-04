---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - packet-analysis
  - wireshark
sources: []
---

# Flujos de trabajo con Wireshark

## Definición
Wireshark es una herramienta de captura de paquetes y análisis de protocolos usada para inspeccionar el tráfico de red, reconstruir conversaciones, aplicar filtros conscientes del protocolo y convertir la evidencia a nivel de paquete en conclusiones de debugging o seguridad.

## Por qué importa
Las DevTools del navegador y los logs muestran el comportamiento interpretado. Wireshark muestra la conversación debajo de esas abstracciones: lookups de DNS, handshakes TCP, negociación de TLS, mensajes HTTP cuando son visibles, resets, retransmisiones y timing.

Esta nota es dueña del flujo de trabajo de Wireshark. [[packet-analysis|Análisis de paquetes]] es dueña del modelo de razonamiento más amplio para la evidencia de paquetes.

## Cómo funciona
Un flujo de trabajo útil de Wireshark tiene **5 etapas**:

1. **Elegí el punto de captura.** Cliente, proxy, backend, contenedor, VPN o gateway.
2. **Capturá de forma angosta.** Limitá por interfaz, tiempo, host, puerto o protocolo donde sea posible.
3. **Aplicá filtros de visualización.** Usá filtros para aislar DNS, streams TCP, handshakes TLS, mensajes HTTP o un host objetivo.
4. **Seguí las conversaciones.** Reconstruí streams TCP, inspeccioná campos de protocolo y compará la secuencia request/response.
5. **Exportá la evidencia.** Guardá paquetes, capturas de pantalla, valores de campo o PCAPs filtrados con timestamps y contexto.

Filtros de ejemplo:

```text
dns
tls.handshake
http
tcp.stream eq 3
ip.addr == 10.0.0.5
tcp.port == 443
```

La herramienta es solo tan buena como la pregunta y el punto de captura. Un filtro limpio no puede arreglar una captura tomada del lado equivocado del proxy.

## Técnicas / patrones
Usá Wireshark para:

- seguir streams TCP en labs de HTTP en texto plano
- inspeccionar la metadata de SNI, ALPN, intercambio de certificados, versión y cipher de TLS
- observar las preguntas y respuestas de DNS antes de una request HTTP
- distinguir conexiones rechazadas, filtradas, reseteadas y con timeout
- comparar el comportamiento de `curl`, navegador y cliente de aplicación
- verificar si un proxy o load balancer cambió headers o paths
- identificar retransmisiones, ACKs duplicados y gaps de latencia
- exportar capturas filtradas mínimas para un reporte

## Variantes y bypasses
El trabajo con Wireshark se divide en **6 tipos de flujo de trabajo**.

### 1. Captura local del cliente
Captura lo que el cliente envía y recibe. Lo mejor para DNS, metadata de TLS y comparaciones navegador vs curl. No prueba qué vio un backend después de los intermediarios.

### 2. Captura del lado del servidor
Captura lo que llega al servicio. Lo mejor para normalización del proxy, IP de origen y tráfico interno en texto plano. Puede perderse el comportamiento original del cliente.

### 3. Captura de gateway o span-port
Captura el tráfico que cruza una frontera. Potente para revisión de segmentación y egress, pero a menudo ruidoso y sensible.

### 4. Flujo de trabajo de TLS descifrado
Usa key logs o intercepción controlada para inspeccionar payloads HTTPS. Útil en labs; sensible y con mucha autorización en producción.

### 5. Flujo de trabajo de seguir-protocolo
Usa "Follow TCP Stream" o vistas de protocolo para reconstruir una conversación. Lo mejor para HTTP, SMTP, protocolos en texto plano tipo Redis y labs crudos.

### 6. Flujo de trabajo de estadísticas
Usa Conversations, Endpoints, I/O Graphs y Expert Info para entender volumen, errores, retransmisiones y patrones de timing.

## Impacto
Ordenado aproximadamente por severidad:

- **Evidencia de tráfico sensible en texto plano.** Muestra credenciales, cookies o tokens cruzando links sin cifrar.
- **Prueba de falla de frontera.** Revela acceso directo al backend, reescritura faltante del proxy o IP de origen inesperada.
- **Claridad para debugging de exploits.** Confirma si los bytes del payload sobrevivieron el camino.
- **Insight de DNS/SSRF.** Muestra qué resolvió y contactó realmente un runtime.
- **Causa raíz operativa.** Expone resets, retransmisiones, problemas de MTU, fallas de handshake y timeouts.
- **Valor de entrenamiento.** Construye intuición de cómo se comportan los protocolos fuera de las abstracciones del framework.

## Detección y defensa
Ordenado por efectividad:

1. **Capturá solo lo que la pregunta requiere.**
   Las capturas angostas reducen el ruido y bajan la chance de recolectar secretos. Empezá con un host, un puerto y una acción.

2. **Registrá el contexto de la captura.**
   Anotá la interfaz, host, tiempo, comando/acción del navegador, red de origen y comportamiento esperado. Sin contexto, un PCAP es difícil de interpretar después.

3. **Usá filtros de visualización antes de sacar conclusiones.**
   Filtrá por stream, host y protocolo. Muchos patrones aparentes desaparecen una vez que se remueve el tráfico no relacionado.

4. **Correlacioná con los logs de aplicación y proxy.**
   Wireshark muestra paquetes; los logs muestran la interpretación de la aplicación. Las conclusiones de seguridad normalmente necesitan ambos.

5. **Protegé los PCAPs como artefactos sensibles.**
   Las capturas pueden incluir cookies, bearer tokens, hostnames internos, IPs y payloads. Redactá o filtrá antes de compartir.

6. **Usá los dissectors oficiales pero validá los supuestos.**
   Wireshark decodifica muchos protocolos, pero el tráfico malformado o los protocolos custom pueden ser malinterpretados. Cuando lo que está en juego es alto, inspeccioná los bytes.

### Qué no funciona como defensa primaria

- **Mirar solo las filas de resumen.** El detalle importante suele estar en los campos de protocolo expandidos o en la reconstrucción del stream.
- **Usar filtros de visualización como filtros de captura.** Los filtros de visualización esconden paquetes después de la captura; no reducen lo que se recolectó.
- **Capturar en la interfaz equivocada.** Las VPNs, contenedores, loopback y las interfaces Wi-Fi/Ethernet ven tráfico distinto.
- **Asumir que cifrado significa incognoscible.** La metadata de TLS todavía revela SNI, ALPN, timing, IPs y certificados.
- **Compartir PCAPs completos en tickets.** Exportá paquetes filtrados o evidencia redactada siempre que sea posible.

## Labs prácticos
Corré solo en un lab propio o entorno autorizado.

### Capturar DNS más HTTPS para una carga de página

```text
Filtros de visualización:
dns
tls.handshake
ip.addr == <target-ip>
```

Cargá el sitio una vez, después inspeccioná la query DNS, el connect TCP, el TLS ClientHello, ALPN y el certificado.

### Seguir un stream HTTP en texto plano

```bash
printf 'GET / HTTP/1.1\r\nHost: lab.local\r\nConnection: close\r\n\r\n' | nc lab.local 80
```

En Wireshark: clic derecho en el paquete → Follow → TCP Stream.

### Comparar navegador y curl

```bash
curl -skI https://app.example.com/
```

Capturá tanto las requests del navegador como las de curl. Compará DNS, SNI, ALPN, headers donde sean visibles y reuso de conexión.

### Inspeccionar SNI y ALPN de TLS

```text
Filtro:
tls.handshake.extensions_server_name or tls.handshake.extensions_alpn
```

Útil al depurar comportamiento de CDN, load-balancer, HTTP/2 o ruteo de origin.

### Encontrar resets y retransmisiones

```text
Filtros:
tcp.flags.reset == 1
tcp.analysis.retransmission
tcp.analysis.duplicate_ack
```

Estos filtros explican muchos síntomas de "app inestable" que en realidad son comportamiento del camino de red.

### Exportar una captura de evidencia mínima

```text
1. Aplicá un filtro de visualización para el stream o host objetivo.
2. File → Export Specified Packets.
3. Exportá solo los paquetes mostrados.
4. Guardá con timestamp, punto de vista y acción de test.
```

## Ejemplos prácticos
- Una captura muestra que el navegador negoció HTTP/2 en el edge, mientras los logs del backend muestran HTTP/1.1 desde el proxy.
- Las queries DNS revelan que la app contacta `metadata.google.internal` durante un lab de SSRF.
- Un reset TCP de un firewall explica por qué Nmap reporta un puerto como cerrado desde una red y filtrado desde otra.
- "Follow TCP Stream" muestra un header `Host` extra en un lab crudo de request-smuggling.
- El SNI de TLS muestra un cliente conectándose al virtual host equivocado después de un cambio de DNS.

## Notas relacionadas
- [[packet-analysis|Análisis de paquetes]] — modelo de razonamiento para la evidencia de paquetes.
- [[http-messages|Mensajes HTTP]] — los bytes exactos del mensaje HTTP.
- [[dns-resolution|Resolución DNS]] — paquetes DNS antes de las conexiones.
- [[tls-https|TLS/HTTPS]] — interpretación del handshake de TLS.
- [[tcp-ip-basics|Fundamentos de TCP/IP]] — fundamentos de conexión y ruteo.
- [[reverse-proxies|Reverse proxies]] — comparar capturas del lado del cliente y del backend.

### Notas atómicas futuras sugeridas
- [[wireshark-display-filters|Filtros de visualización de Wireshark]]
- [[wireshark-tls-analysis|Análisis de TLS con Wireshark]]
- [[follow-tcp-stream|Follow TCP Stream]]
- [[pcap-redaction|Redacción de PCAPs]]
- [[tcp-retransmission-analysis|Análisis de retransmisión TCP]]
- [[browser-vs-curl-captures|Capturas navegador vs curl]]

## Referencias
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Official Tool Docs:** Wireshark display filter reference — https://www.wireshark.org/docs/dfref/
- **Official Tool Docs:** Wireshark display filters man page — https://www.wireshark.org/docs/man-pages/wireshark-filter.html
