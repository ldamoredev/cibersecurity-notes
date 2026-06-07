# Encrypted Traffic Analysis and Metadata Leakage

## Definición

El análisis de tráfico cifrado es la detección e investigación del comportamiento de comunicación usando metadata que sigue visible cuando el contenido del payload está protegido por TLS, QUIC, VPNs u otras capas de cifrado.

## Por qué importa

El cifrado oculta contenido, no todo el comportamiento. Los defensores pueden perder cuerpos HTTP, credenciales, comandos y file payloads, pero todavía pueden observar endpoints, timing, conteos de bytes, tamaños de paquetes, DNS, metadata de certificados, SNI cuando es visible, ALPN, fingerprints de cliente TLS, ancestry de procesos, logs cloud y forma de flow.

El framing senior no es "TLS inspection resuelve todo" ni "el cifrado hace imposible monitorear". El tráfico cifrado desplaza la detección desde inspección de payload hacia metadata, correlación de endpoint, proxy logs, identidad y baselines de comportamiento.

## Cómo funciona

El tráfico cifrado todavía expone **7 capas de metadata**:

1. **Tupla de red.** Fuente, destino, puertos, protocolo, dirección, duración, paquetes, bytes.
2. **Resolución de nombres.** DNS queries, resolver logs, selección de endpoint DoH y timing de cache name-to-IP.
3. **Metadata del handshake TLS.** Versión, ciphers, extensiones, ALPN, SNI donde sea visible, campos de certificado, issuer, validez y fingerprints tipo JA3/JA4.
4. **Forma de flow.** Tamaños de paquetes, patrones de burst, ratios de bytes, periodicidad, duración de sesión, comportamiento de retry.
5. **Contexto de endpoint.** Proceso, usuario, proceso padre, command line, identidad de container/workload.
6. **Proxy y termination logs.** Metadata HTTP descifrada donde TLS termina intencionalmente en un punto de control confiable.
7. **Contexto de secuencia.** Recon previo, destino first-seen, comportamiento de red raro por proceso y acciones posteriores.

Ejemplo:

```
Payload: encrypted.
Visible: workstation -> 198.51.100.20:443 every 60 seconds, 900 bytes out / 1400 bytes in,
Python process, rare JA4-like profile, no browser parent, first-seen destination.
```

El payload está oculto; el comportamiento no.

## Técnicas / patrones

- **Análisis de metadata TLS.** Inspeccionar SNI, ALPN, issuer/subject de certificado, validez, versión, ciphers y extensiones.
- **Fingerprinting tipo JA3/JA4.** Usar la forma del handshake como pivot, no como veredicto.
- **Flow analytics.** Detectar periodicidad de beacon, asimetría de bytes, sesiones largas, puertos raros y destinos nuevos.
- **Costura DNS-a-flow.** Unir DNS queries con flows cifrados posteriores por host, tiempo y destino.
- **Correlación endpoint-red.** Unir conexiones cifradas con proceso, command line, usuario, hash y cadena padre.
- **Análisis de proxy logs.** Usar puntos explícitos de terminación TLS cuando sea legal, documentado y revisado por privacidad.

## Perspectiva del atacante

Los atacantes cifran C2, staging, exfiltración y tooling para evitar inspección de payload. Pueden usar puertos comunes, CDNs legítimas, patrones tipo domain fronting donde estén disponibles, librerías comunes, DoH, QUIC o APIs cloud para mezclarse con tráfico normal.

Pero todavía necesitan comunicarse. Su infraestructura, timing, librería cliente, proceso, elección de destino, comportamiento de certificado y secuencia suelen permanecer observables.

## Perspectiva del defensor

Los defensores deberían evitar la nostalgia de payload. Si la inspección de payload no está disponible o no es deseable, el modelo de detección cambia a metadata más contexto de endpoint e identidad. La pregunta pasa a ser: "¿Esta comunicación cifrada es esperada para este proceso, usuario, rol de host, destino y hora?"

## Tradeoffs de detección e ingeniería

1. **TLS inspection vs privacidad y fragilidad.**
   El descifrado puede revelar contenido pero introduce riesgos de privacidad, legales, performance, certificados, pinning y operación.

2. **Estabilidad de fingerprint vs overfitting.**
   Los fingerprints tipo JA3/JA4 ayudan a clusterizar clientes, pero updates de software y mimicry deliberada pueden cambiarlos.

3. **Visibilidad DNS vs DNS cifrado.**
   Los resolver logs son valiosos, pero DoH/DoT desplaza visibilidad hacia endpoint, proxy o capas de política de red.

4. **Performance de QUIC vs observabilidad.**
   QUIC cambia comportamiento de transporte y cifra más metadata, reduciendo algunas suposiciones de middleboxes.

5. **Detección por metadata vs ambigüedad.**
   La metadata puede indicar comportamiento sospechoso pero suele necesitar contexto de proceso, identidad y asset para confianza.

## Detección y defensa

Ordenado por efectividad:

1. **Uní flows cifrados con contexto de proceso de endpoint.**
   Proceso, padre, usuario y command line suelen decidir si una conexión cifrada es esperada.

2. **Baseliná por rol de host y aplicación.**
   Navegadores, update agents, servidores, CI runners y bases de datos tienen tráfico cifrado normal distinto.

3. **Usá fingerprints TLS como pivots.**
   Valores JA3/JA4, ALPN, SNI y patrones de certificado son útiles para hunting y clustering, no veredictos standalone.

4. **Monitoreá novedad de DNS y destino.**
   Dominios first-seen, ASNs raros, comportamiento inusual de resolver y timing DNS-to-flow pueden exponer C2 cifrado.

5. **Tratá TLS inspection como un control acotado.**
   Usalo donde esté justificado, documentado y sea técnicamente seguro; no asumas que es universalmente desplegable.

### Qué no funciona como defensa primaria

- **"Usa HTTPS, así que es seguro."** El tráfico malicioso usa HTTPS rutinariamente.
- **Intercepción TLS en todos lados.** Puede romper aplicaciones, violar expectativas de privacidad y perder tráfico pinned o no-browser.
- **Blocklists JA3/JA4 solas.** Los fingerprints colisionan, cambian y necesitan contexto.
- **Monitoreo solo DNS.** DNS cifrado, resoluciones cacheadas, IPs directas y APIs cloud pueden bypassar vistas DNS simples.
- **Pensamiento IDS solo-payload.** El tráfico cifrado requiere metadata y correlación.

### Malentendidos operacionales

- **"El cifrado oculta actividad."** Oculta contenido, no timing, endpoints, forma de flow, proceso ni muchos campos del handshake.
- **"SNI siempre existe."** ECH y algunos protocolos reducen visibilidad SNI; TLS viejo y muchos flows enterprise todavía lo exponen.
- **"El issuer del certificado prueba legitimidad."** Los atacantes pueden obtener certificados legítimos.
- **"Beaconing siempre significa intervalos fijos."** Los beacons modernos usan jitter; la detección necesita distribuciones y contexto.

### Limitaciones modernas

- TLS 1.3, QUIC, ECH, DoH/DoT, VPNs y tunneling tipo MASQUE reducen visibilidad de middleboxes.
- CDNs y proveedores cloud agregan muchos servicios benignos y maliciosos detrás de infraestructura compartida.
- Aplicaciones móviles y SaaS generan tráfico cifrado de alto volumen difícil de baselinar globalmente.
- La visibilidad de endpoint puede ser necesaria pero no estar disponible para appliances y dispositivos no gestionados.

### Puntos ciegos de telemetría

- DNS logs faltantes, colapso por NAT, bypass de proxy, split-tunnel VPN y endpoints no gestionados.
- Metadata TLS no logueada por sensores o eliminada durante normalización.
- Sesiones cifradas de corta vida ocultas por sampling de flow.
- Certificate pinning y aplicaciones no-proxyables.

## Labs prácticos

Usá endpoints públicos benignos o servicios TLS locales únicamente.

### Lab 1 - Comparar visibilidad de payload y metadata

Objetivo: Mostrar que el contenido cifrado queda oculto mientras la metadata de conexión permanece.

```
openssl s_client -connect example.com:443 -servername example.com -alpn h2 </dev/null 2>/dev/null |
  sed -n '1,35p'
curl -s -o /dev/null -w 'remote_ip=%{remote_ip} remote_port=%{remote_port} http_version=%{http_version} size_download=%{size_download} time_total=%{time_total}\n' https://example.com/
```

Telemetría esperada: metadata de certificado y protocolo negociado son visibles; el cuerpo HTTP está protegido en tránsito. Los defensores observarían destino, timing, certificado y ALPN. Limitación: la salida local del comando no es un sensor de red. Malentendido corregido: "cifrado significa invisible."

### Lab 2 - Generar evidencia de forma de flow

Objetivo: Observar timing y features de tamaño sin payload.

```
for i in 1 2 3 4 5; do
  date -u +%FT%TZ
  curl -s -o /dev/null -w 'bytes=%{size_download} total=%{time_total}\n' https://example.com/
  sleep 5
done
```

Telemetría esperada: periodicidad y tamaños de bytes son visibles. Los defensores buscarían regularidad, jitter y destinos raros. Limitación: cinco muestras no son un baseline. Malentendido corregido: "solo importa el payload."

### Lab 3 - Comparar contexto de proceso

Objetivo: Mostrar que el mismo destino cifrado significa cosas distintas según el proceso.

```
cat > /tmp/tls-process.jsonl <<'EOF'
{"process":"chrome","parent":"explorer","dest":"example.com:443","role":"user-browser"}
{"process":"python3","parent":"cron","dest":"example.com:443","role":"server"}
EOF
jq '{process,parent,dest,role}' /tmp/tls-process.jsonl
```

Telemetría esperada: metadata de red idéntica tiene interpretación distinta por proceso y rol. Limitación: datos de juguete. Malentendido corregido: "la reputación del destino alcanza."

## Ejemplos prácticos

- Un proceso Python en una workstation de finanzas beaconea a un dominio nuevo por TLS cada minuto.
- Un servidor que normalmente solo habla con servicios internos empieza a usar QUIC hacia una CDN de consumo.
- Un perfil TLS sospechoso tipo JA4 aparece desde múltiples hosts después del mismo phishing email.
- EDR identifica `rundll32.exe` como el proceso detrás de tráfico cifrado que el IDS de red no pudo parsear.

## Notas relacionadas

- [[network-telemetry-sources-and-visibility|Fuentes de telemetría de red y visibilidad]]
- [[zeek-suricata-and-netflow-analysis|Análisis con Zeek, Suricata y NetFlow]]
- [[edr-network-observability-and-process-correlation|Observabilidad de red en EDR y correlación de procesos]]
- [[telemetry-normalization-correlation-and-enrichment|Normalización, correlación y enrichment de telemetría]]
- [[detection-evasion-myths-and-modern-limitations|Mitos de evasión de detección y limitaciones modernas]]
- [[tls-https|TLS y HTTPS]]
- [[metadata-and-identity-leakage|Fuga de metadata e identidad]]

### Notas atómicas futuras sugeridas

- tls-fingerprinting-for-detection
- dns-over-https-detection-tradeoffs
- beaconing-analysis
- quic-security-observability

## Referencias

- **Fundamental:** RFC 8446 TLS 1.3 - https://datatracker.ietf.org/doc/html/rfc8446
- **Fundamental:** JA3 and JA3S TLS fingerprinting - https://github.com/salesforce/ja3
- **Investigación / Deep Dive:** JA4+ Network Fingerprinting - https://github.com/FoxIO-LLC/ja4
- **Official Tool Docs:** Zeek Logs - https://docs.zeek.org/en/current/logs/
- **Official Tool Docs:** Suricata EVE JSON Output - https://docs.suricata.io/en/latest/output/eve/eve-json-output.html
