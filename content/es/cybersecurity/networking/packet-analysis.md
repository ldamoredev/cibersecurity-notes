---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - packet-analysis
sources: []
---

# Análisis de paquetes

## Definición
El análisis de paquetes es la práctica de inspeccionar paquetes de red capturados, streams y conversaciones de protocolo para entender qué enviaron, recibieron, retransmitieron, negociaron o rechazaron realmente los sistemas en el wire.

## Por qué importa
Los logs de aplicación muestran lo que el código cree que pasó. Las capturas de paquetes muestran lo que cruzó la frontera de red. Esa distinción importa para bugs de proxy, negociación de TLS, resolución de DNS, reintentos, redirects, cookies de sesión, comportamiento de firewall y desacuerdo de parsers.

Esta nota es dueña del modelo de razonamiento para la evidencia de paquetes. [[wireshark-workflows|Flujos de trabajo con Wireshark]] es dueña del flujo de trabajo de la herramienta Wireshark.

## Cómo funciona
El análisis de paquetes sigue **5 pasos**:

1. **Definí la pregunta.** Ejemplo: "¿El cliente envió este header?" o "¿El DNS resolvió a la dirección privada?"
2. **Capturá en el punto correcto.** El cliente, proxy, backend, contenedor o gateway ven cada uno tráfico distinto.
3. **Filtrá al flujo relevante.** Usá host, puerto, protocolo, ventana de tiempo e identificadores de stream.
4. **Reconstruí la conversación.** Seguí streams TCP, handshakes TLS, queries DNS, requests HTTP o retransmisiones.
5. **Compará la expectativa con la observación.** Convertí la evidencia de paquetes en una conclusión de seguridad o arquitectura.

Razonamiento de ejemplo:

```txt
Esperado: la app envía HTTPS al origin.
Observado: cliente -> proxy usa TLS, proxy -> origin usa HTTP en texto plano.
Conclusión: el TLS de edge existe, pero el hop al origin no está cifrado.
```

El bug a menudo vive en la diferencia entre el camino que los ingenieros describen y los paquetes que el camino realmente carga.

## Técnicas / patrones
Los analistas inspeccionan:

- pares query/response de DNS antes de los intentos de conexión
- comportamiento TCP SYN/SYN-ACK/RST para alcanzabilidad y filtrado
- TLS ClientHello, SNI, ALPN, cadena de certificados y negociación de versión/cipher
- headers de request/response HTTP y redirects cuando es texto plano o descifrado
- retransmisiones, resets, timeouts y fallas de handshake
- IPs y puertos de origen/destino a través de fronteras de NAT, proxy y contenedor
- desajustes de protocolo: HTTP en puertos TLS, TLS en puertos inesperados, no-HTTP detrás de supuestos de HTTP
- capturas antes/después alrededor de un cambio de firewall, proxy o config

## Variantes y bypasses
El análisis de paquetes tiene **6 clases de evidencia**.

### 1. Evidencia de alcanzabilidad
SYN, SYN-ACK, RST, ICMP unreachable y el comportamiento de timeout muestran si un camino está abierto, cerrado, filtrado o silenciosamente descartado desde un punto de vista.

### 2. Evidencia de naming
Los paquetes DNS revelan qué nombre se resolvió, por qué resolver, a qué respuesta, y si el contexto de runtime ve un resultado distinto que el tester.

### 3. Evidencia de transporte
Las retransmisiones TCP, resets, comportamiento de ventana y reuso de conexión explican fallas que los logs de app aplanan en "error de red".

### 4. Evidencia de TLS
SNI, ALPN, certificado, versión de TLS y negociación de cipher revelan la identidad del edge, el comportamiento de downgrade y el soporte de protocolo.

### 5. Evidencia de mensaje de aplicación
Cuando el tráfico es texto plano o descifrado, los mensajes HTTP muestran los headers exactos, el framing del body, las cookies y las transformaciones del proxy.

### 6. Evidencia de timing y secuencia
El orden de los paquetes, los gaps, los reintentos y los streams concurrentes ayudan a depurar race conditions, síntomas de request smuggling y comportamiento de load-balancer.

## Impacto
Ordenado aproximadamente por severidad:

- **Prueba de frontera de confianza.** Las capturas pueden probar acceso directo al backend, hops internos en texto plano o reescritura inesperada del proxy.
- **Exposición de credenciales o datos sensibles.** La evidencia de paquetes puede mostrar secretos cruzando caminos en texto plano o logs.
- **Confirmación de exploit.** El smuggling, SSRF, inyección de headers y bugs de caché a menudo necesitan prueba a nivel de wire.
- **Validación de segmentación.** El comportamiento de los paquetes muestra si las reglas de firewall/security-group bloquean o dejan pasar el tráfico.
- **Reconstrucción de incidentes.** Las capturas preservan evidencia cuando los logs de app están incompletos o engañan.
- **Eliminación de falsos supuestos.** El análisis de paquetes a menudo refuta "el navegador/proxy/framework nunca enviaría eso".

## Detección y defensa
Ordenado por efectividad:

1. **Capturá desde la frontera que responde la pregunta.**
   Las capturas del lado del cliente no pueden probar qué recibió el backend después de un proxy. Las capturas del backend no pueden probar qué envió el navegador. Elegí el punto donde ocurre la transformación en disputa.

2. **Minimizá el alcance de la captura.**
   Usá ventanas de tiempo, interfaces, hosts y puertos ajustados. Las capturas más chicas son más fáciles de razonar y reducen la recolección accidental de datos sensibles.

3. **Tratá las capturas como evidencia sensible.**
   Los PCAPs pueden contener credenciales, cookies, IPs internas, URLs y payloads. Guardalos, redactalos y compartilos como secretos.

4. **Correlacioná con logs y request IDs.**
   La evidencia de paquetes es más fuerte cuando se ata a logs de aplicación, logs de proxy, timestamps e identificadores de request.

5. **Preferí capturas reproducibles.**
   Guardá el comando/filtro, target, punto de vista y comportamiento esperado. Los revisores futuros deberían poder repetir la observación.

6. **Usá captura descifrada solo con autorización explícita.**
   El key logging de TLS, la intercepción de proxy o la captura en texto plano del lado del servidor pueden ser poderosos y sensibles. Usalo solo en lab propio o contextos de debugging aprobados.

### Qué no funciona como defensa primaria

- **Asumir que los logs son la verdad del wire.** Los logs reflejan la interpretación parseada después de las transformaciones.
- **Capturar en el hop equivocado.** Una captura del cliente no puede mostrar las mutaciones del proxy que son solo del backend.
- **Recolectar PCAPs enormes sin una pregunta.** Más paquetes normalmente significa menos claridad.
- **Ignorar la sincronización de tiempo.** La correlación paquete/log falla si los relojes derivan.
- **Compartir capturas crudas a la ligera.** Los PCAPs a menudo son volcados de credenciales disfrazados.

## Labs prácticos
Corré en sistemas que sean tuyos o que estés autorizado a inspeccionar.

### Capturar una sesión HTTP/TLS angosta

```bash
sudo tcpdump -i any -w /tmp/app.pcap 'host app.example.com and port 443'
curl -skI https://app.example.com/
```

Abrí `/tmp/app.pcap` en Wireshark e inspeccioná las etapas de DNS/TCP/TLS.

### Observar DNS antes de HTTP

```bash
sudo tcpdump -i any -n 'port 53' &
dig app.example.com
curl -skI https://app.example.com/
```

Confirmá qué resolver y qué respuesta usó realmente el cliente.

### Comparar puertos abiertos vs cerrados

```bash
sudo tcpdump -i any -n 'host app.example.com and tcp' &
nc -vz app.example.com 443
nc -vz app.example.com 5432
```

Buscá el comportamiento SYN-ACK vs RST vs timeout.

### Inspeccionar la metadata de TLS

```bash
openssl s_client -connect app.example.com:443 -servername app.example.com -alpn h2,http/1.1 </dev/null
```

Emparejá esto con una captura de paquetes para observar SNI, ALPN y el intercambio de certificados.

### Seguir un stream HTTP en tráfico de lab en texto plano

```bash
printf 'GET / HTTP/1.1\r\nHost: lab.local\r\nConnection: close\r\n\r\n' | nc lab.local 80
```

Capturá y usá "Follow TCP Stream" en Wireshark para ver los bytes exactos de la request.

### Comparar capturas del cliente y del backend

```text
1. Capturá en el cliente mientras enviás una request con X-Debug-Probe.
2. Capturá en el egress del backend o reverse proxy.
3. Compará si el header/path/body cambió.
```

Esta es la forma más limpia de probar la normalización del proxy.

## Ejemplos prácticos
- Un log de backend no tiene `X-Forwarded-Host`, pero una captura en el egress del proxy muestra que el proxy lo quitó.
- Una captura de DNS dentro de un contenedor muestra que la metadata o los nombres de servicios internos resuelven distinto que en el host.
- Una captura de TLS muestra `h2` negociado en el edge mientras el backend recibe HTTP/1.1.
- Paquetes TCP RST de un firewall explican por qué la app reporta errores intermitentes de upstream.
- Una captura en texto plano en un hop interno muestra cookies de sesión cruzando un segmento sin cifrar.

## Notas relacionadas
- [[wireshark-workflows|Flujos de trabajo con Wireshark]] — flujo de inspección de paquetes específico de la herramienta.
- [[http-messages|Mensajes HTTP]] — los bytes exactos de request/response HTTP.
- [[tls-https|TLS/HTTPS]] — handshake de TLS y confianza de transporte.
- [[dns-resolution|Resolución DNS]] — DNS como la primera etapa a nivel de paquete.
- [[reverse-proxies|Reverse proxies]] — comparar las transformaciones antes/después del proxy.
- [[nmap-scanning|Escaneo con Nmap]] — el comportamiento del escaneo se puede validar a nivel de paquete.
- [[cybersecurity/detection-engineering/network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]] — dónde encaja la captura de paquetes entre la telemetría de flow, protocolo, endpoint y nube.
- [[cybersecurity/detection-engineering/zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]] — cómo la evidencia de paquetes se vuelve logs de seguridad de nivel superior.

### Notas atómicas futuras sugeridas
- [[tcpdump-basics|Fundamentos de tcpdump]]
- [[pcap-handling|Manejo de PCAPs]]
- [[tls-key-logging|Key logging de TLS]]
- [[follow-tcp-stream|Follow TCP Stream]]
- [[packet-loss-and-retransmission|Pérdida de paquetes y retransmisión]]
- [[proxy-packet-comparison|Comparación de paquetes del proxy]]
- [[sensor-health-and-capture-loss|Salud del sensor y pérdida de captura]]

## Referencias
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
- **Official Tool Docs:** Wireshark display filter reference — https://www.wireshark.org/docs/dfref/
- **Official Tool Docs:** tcpdump man page — https://www.tcpdump.org/manpages/tcpdump.1.html
- **Foundational:** MDN HTTP messages — https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
