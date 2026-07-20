---
type: concept
status: active
created: 2026-04-23
updated: 2026-04-29
tags:
  - cybersecurity
  - networking
  - tcp-ip
  - foundational
sources: []
---

# Fundamentos de TCP/IP

## Definición
TCP/IP es la base práctica de comunicación de las redes IP: IP mueve paquetes entre direcciones, mientras que TCP crea flujos de bytes confiables y ordenados entre puertos en los hosts.

## Por qué importa
La mayoría de los hallazgos de seguridad de aplicaciones dependen de la alcanzabilidad antes que del código. SSRF, bases de datos expuestas, confianza en reverse-proxy, endpoints de metadata, firewalls, escaneos de puertos y capturas de paquetes requieren todos razonamiento básico de TCP/IP.

La lección recurrente: **la alcanzabilidad es una propiedad del camino**. Una dirección, puerto o servicio es "interno", "público", "filtrado" o "alcanzable" solo desde un punto de vista de red particular.

## Cómo funciona
El razonamiento de TCP/IP arranca con **5 preguntas**:

1. **¿Qué dirección es el objetivo?** IPv4, IPv6, loopback, link-local, privada, pública o espacio de direcciones compartido.
2. **¿Qué ruta se usa?** Interfaz local, gateway, VPN, NAT, proxy o tabla de rutas de la nube.
3. **¿Qué puerto se contacta?** El puerto de destino selecciona el servicio que escucha.
4. **¿Puede formarse una conexión TCP?** SYN → SYN-ACK → ACK significa que el camino y el listener son alcanzables.
5. **¿Qué habla sobre la conexión?** HTTP, TLS, SSH, protocolo de base de datos u otra cosa.

Ejemplo:

```txt
client 198.51.100.10:51544 -> app.example.com 203.0.113.42:443
SYN → SYN/ACK → ACK
TLS ClientHello
HTTP request inside TLS
```

La request de capa de aplicación solo existe porque el direccionamiento, el ruteo, la selección de puerto y el setup de la conexión TCP tuvieron éxito primero.

## Técnicas / patrones
El trabajo de seguridad usa los fundamentos de TCP/IP para:

- distinguir la dirección de bind (`127.0.0.1`, `0.0.0.0`, IP privada, IP pública)
- probar alcanzabilidad con `nc`, `curl`, `nmap` y capturas de paquetes
- interpretar el comportamiento open, closed, filtered, refused y timeout
- razonar sobre NAT, redes privadas y direcciones link-local
- entender la IP de origen antes y después de proxies/load balancers
- comparar puntos de vista público, VPN, interno, de contenedor y de nube
- depurar reuso de conexión, resets, retransmisiones y timeouts

## Variantes y bypasses
El razonamiento de seguridad de TCP/IP tiene **6 contextos recurrentes**.

### 1. Loopback
`127.0.0.0/8` y `::1` son locales al host. Un servicio bindeado a loopback no es alcanzable desde la red, pero un SSRF dentro del mismo host todavía puede llegarle.

### 2. Espacio de direcciones privadas
Los rangos RFC 1918 (`10/8`, `172.16/12`, `192.168/16`) no se rutean públicamente, pero son alcanzables desde dentro de redes, VPNs, contenedores o workloads con capacidad de SSRF.

### 3. Link-local
`169.254.0.0/16` e IPv6 `fe80::/10` son rangos de enlace local. Los endpoints de metadata de la nube usan esta forma, por eso importa el egress link-local.

### 4. Espacio de direcciones públicas
Las IPs públicas son ruteables, pero los firewalls, security groups y load balancers deciden qué puertos responden.

### 5. Exposición por IPv6
IPv6 puede saltearse supuestos solo-IPv4. Un host puede estar cerrado en IPv4 mientras es alcanzable globalmente por IPv6.

### 6. Traducción NAT y proxy
NAT cambia direcciones y puertos; los proxies terminan y crean conexiones nuevas. Los logs y controles de acceso deben tener en cuenta de qué hop están viendo la IP de origen.

## Impacto
Ordenado aproximadamente por severidad:

- **Exposición inesperada de servicio.** Un proceso bindeado a `0.0.0.0` o IPv6 queda alcanzable fuera del host previsto.
- **Bypass de frontera.** Caminos internos, rutas de VPN, contenedores o SSRF llegan a servicios que los usuarios públicos no pueden.
- **Acceso a metadata/servicios internos.** La alcanzabilidad link-local y privada amplifica los bugs de request del lado del servidor.
- **Confusión de logs y de confianza.** La traducción NAT/proxy cambia la evidencia de IP de origen.
- **Conclusiones de prueba falsas.** Probar desde el punto de vista equivocado pierde o inventa exposición.
- **Fallas de debugging operativo.** Resets de conexión y timeouts se mal-diagnostican como bugs de aplicación.

## Detección y defensa
Ordenado por efectividad:

1. **Bindeá los servicios a la dirección más angosta necesaria.**
   Los servicios de desarrollo/admin deberían bindear loopback o interfaces privadas, no `0.0.0.0`, salvo que la exposición pública sea intencional.

2. **Validá la alcanzabilidad desde cada punto de vista relevante.**
   Internet pública, VPN, subred interna, contenedor y workload de nube pueden diferir. Las afirmaciones de seguridad necesitan llevar el punto de vista adjunto.

3. **Usá las fronteras de red antes que la confianza de aplicación.**
   Bases de datos, cachés, endpoints de metadata y servicios de admin deberían ser inalcanzables desde caminos no confiables sin importar los chequeos de capa de aplicación.

4. **Tené en cuenta IPv6 explícitamente.**
   Espejá la política de firewall/security-group de IPv4 en IPv6, o deshabilitá IPv6 intencionalmente donde no se soporte.

5. **Logueá las direcciones de origen y traducidas con claridad.**
   Preservá por separado los datos originales de origen de red y la identidad derivada del proxy para que las investigaciones no confundan afirmaciones de header con el origen del paquete.

6. **Observá los paquetes cuando el comportamiento es ambiguo.**
   Los patrones de SYN/ACK, RST, retransmisión y timeout explican lo que escáneres y apps resumen mal.

### Qué no funciona como defensa primaria

- **Confiar en nombres de "IP interna".** Los nombres no imponen ruteo ni autorización.
- **Bindear a todas las interfaces por defecto.** Muchos frameworks lo hacen por conveniencia; la exposición de producción debería ser explícita.
- **Probar solo desde localhost.** El éxito local dice poco sobre la alcanzabilidad de red pública o interna.
- **Ignorar UDP e IPv6.** La superficie de ataque no es solo TCP/IPv4.
- **Tratar NAT como un firewall.** NAT oculta algunos caminos pero no define autorización.

## Labs prácticos
Corré sobre sistemas que sean tuyos.

### Inspeccionar listeners locales

```bash
lsof -i -P -n
ss -lntup 2>/dev/null || netstat -an | rg 'LISTEN|udp'
```

Buscá servicios bindeados a `0.0.0.0`, `::`, IPs públicas o puertos inesperados.

### Inspeccionar rutas e interfaces

```bash
ip addr 2>/dev/null || ifconfig
ip route 2>/dev/null || netstat -rn
```

Registrá qué interfaz y gateway va a usar el tráfico.

### Probar alcanzabilidad TCP

```bash
nc -vz app.example.com 443
nc -vz 127.0.0.1 3000
```

Compará los puntos de vista local, público, VPN y host de nube.

### Mirar el handshake

```bash
sudo tcpdump -n 'tcp port 443 and host app.example.com'
nc -vz app.example.com 443
```

Observá el comportamiento SYN/SYN-ACK/RST/timeout.

### Chequear exposición IPv6

```bash
dig +short app.example.com AAAA
nmap -6 -Pn -p 80,443 app.example.com
```

Solo tiene sentido cuando el objetivo tiene registros o direcciones IPv6.

### Comparar comportamiento de bind

```bash
# Lab local de ejemplo: un servicio bindeado a localhost, otro a todas las interfaces.
nc -l 127.0.0.1 9001
nc -l 0.0.0.0 9002
```

Desde otro host, solo el listener de todas-las-interfaces debería ser alcanzable.

## Ejemplos prácticos
- Un servidor de desarrollo de Node bindea `0.0.0.0:3000` y queda alcanzable desde la red de la oficina.
- PostgreSQL escucha en una IP privada; internet pública no puede alcanzarlo, pero una app web comprometida en la misma VPC sí.
- Un firewall permite solo IPv4, pero el host expone SSH por IPv6.
- Un access log de proxy registra la IP del load balancer, mientras la app confía en `X-Forwarded-For` para la identidad del usuario.
- `nc` da timeout desde internet pública pero tiene éxito desde una VPN, probando que la segmentación depende del punto de vista.

## Notas relacionadas
- [[ports-and-services|Puertos y servicios]] — los puertos como puntos de entrada de servicios.
- [[nat-and-private-networks|NAT y redes privadas]] — alcanzabilidad privada y comportamiento de NAT.
- [[metadata-endpoints|Endpoints de metadata]] — riesgo de servicio link-local.
- [[packet-analysis|Análisis de paquetes]] — prueba a nivel de paquete de la alcanzabilidad.
- [[nmap-scanning|Escaneo con Nmap]] — escaneo sistemático de alcanzabilidad y servicios.
- [[firewalls-and-network-boundaries|Firewalls y fronteras de red]] — controles de política sobre los caminos de red.

### Notas atómicas futuras sugeridas
- [[tcp-handshake|Handshake de TCP]]
- [[bind-addresses|Direcciones de bind]]
- [[ipv6-exposure|Exposición por IPv6]]
- [[udp-basics|Fundamentos de UDP]]
- [[connection-states|Estados de conexión]]
- [[source-ip-vs-forwarded-ip|IP de origen vs IP forwarded]]

## Referencias
- **Foundational:** RFC 9293 (Transmission Control Protocol) — https://datatracker.ietf.org/doc/html/rfc9293
- **Foundational:** RFC 791 (Internet Protocol) — https://datatracker.ietf.org/doc/html/rfc791
- **Official Tool Docs:** Nmap Network Scanning — https://nmap.org/book/toc.html
- **Official Tool Docs:** Wireshark User’s Guide — https://www.wireshark.org/docs/wsug_html_chunked/
